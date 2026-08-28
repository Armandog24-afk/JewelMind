---
id: JM-BIBLE-581
title: Setting Architecture
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-27
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SETTING-README
  - JM-BIBLE-580
related_documents:
  - JM-BIBLE-582
  - JM-BIBLE-561
implementation_status: current
professional_validation: not_required
normative: true
---

# Setting Architecture

## The layers

```
domain/                                   shared contracts
  schema.py::SettingSpec                    public JDL input (flat, backward compatible)

setting/                                  THE SETTING SYSTEM — category-neutral
  __init__.py                               deliberately NON-EAGER
  models.py                                 SettingDefinition, StoneSettingReference,
                                            SettingAttachmentInterface, per-family definitions,
                                            SettingGeometryResult
  capability.py                             SETTING_CAPABILITIES + Stone x Setting matrix
  stone_interface.py                        the ONLY place stone facts enter
  placement.py                              RADIAL / OUTLINE_CARDINAL strategies
  prong.py                                  prong generator
  bezel.py                                  bezel generator
  dispatch.py                               SETTING_GENERATORS registry (lazy, cached)
  errors.py                                 structured errors

geometry/                                 Atlas / Ring side
  setting_adapter.py                        JewelryDefinition -> Setting inputs (the translation point)
  components/prongs.py                      thin adapter, import-path stability only
  assemblies/solitaire.py                   the RingHead integration
  roles.py                                  component role registry (gained `bezel`)
```

## Why the adapter lives outside `setting/`

`geometry/setting_adapter.py` is the single translation point from `JewelryDefinition` to the
Setting System's contracts. It is deliberately **not** inside `jewelmind/setting/`, because putting
it there would require importing `JewelryDefinition` into the Setting core — and that object carries
`ring`, `band`, and `setting` blocks. One import would hand the entire ring domain to a subsystem
that must not know rings exist.

`test_setting_system_no_ring_dependency.py` asserts this explicitly: no file under `setting/` may
import `JewelryDefinition` from `jewelmind.domain.schema`, and no file may import the adapter
either (which would reach Ring transitively).

## The two boundaries Setting defends

Stone System (Sprint 18) had one boundary to defend: it must not depend on Ring. Setting sits
*between* two subsystems and therefore has two:

| Direction | Rule | Mechanism |
|---|---|---|
| **Downward, to Stone** | Setting may consume stone facts; it may never redefine stone geometry | `stone_interface.py` calls Stone's public contracts only; produces a kernel-neutral `StoneSettingReference` |
| **Upward, to the category** | Setting must not know which category incorporates it | The category supplies a `SettingAttachmentInterface`; Setting never computes an attachment plane from category fields |

The upward boundary is the newer idea and the one that makes a future earring possible: the ring
side computes `attachmentPlaneZMm` from its own band geometry, and the Setting simply builds
downward from whatever plane it was handed.

## The non-eager `__init__.py`

`setting/__init__.py` imports nothing, with the reason recorded in its own docstring. This follows
the discipline `geometry/stone/__init__.py` adopted in Sprint 18 after a real circular import: when
a package's submodules depend on modules that may in turn be imported early, an eager convenience
re-export in `__init__.py` is exactly where an import cycle appears. Callers import
`jewelmind.setting.dispatch` (or the specific submodule) directly.

`dispatch.py` applies the same lesson one level down: `SETTING_GENERATORS` is built lazily inside an
`lru_cache`d function rather than as a module-level constant, matching
`jewelry_category/dispatch.py`'s fix from Sprint 16.

## Generator dispatch, not branching

```python
@lru_cache(maxsize=1)
def setting_generators() -> dict[str, SettingGenerator]:
    from jewelmind.setting.bezel import generate_bezel_setting
    from jewelmind.setting.prong import generate_prong_setting
    return {"prong": generate_prong_setting, "bezel": generate_bezel_setting}
```

Only implemented families are registered — there are no placeholder entries for reserved families,
so an unregistered type raises `SettingTypeUnsupportedError` rather than silently producing nothing
(SETTING-GOV-005/012/018). Adding a family is: write a generator, register it, add a capability
entry, add Golden coverage.

## The RingHead integration

`assemblies/solitaire.py` is the RingHead. It owns the band, the basket support, and the decision to
fuse them with whatever the Setting produced:

```python
setting_definition = setting_definition_from_jdl(definition, stone)
setting_components, setting_result = generate_setting(setting_definition)
setting_metal = [setting_components[n] for n in setting_result.productionComponents]
combined_metal, warnings = _fuse_metal([band, basket, *setting_metal])
```

Two details matter. The fuse **order** is preserved from pre-Sprint-19 (band, basket, then the
setting component) so a prong model's fused solid is byte-identical. And the assembly reads
`setting_result.productionComponents` rather than hardcoding a name, so a family producing a
different or additional component needs no change here.

`_fuse_metal()` was generalized from a fixed `(band, prongs, basket)` signature to a list, which is
what allows `bezel` to participate at all.

## What is Setting-owned vs RingHead-owned

See [`current-prong-migration.md`](current-prong-migration.md) for the full audit. In short:

| Behaviour | Owner | Why |
|---|---|---|
| Prong solids, positions, count | **SETTING** | Purely a stone/metal interaction |
| Bezel wall | **SETTING** | Derived from the stone outline |
| Attachment plane Z, embed depth | **RING_HEAD** | Computed from band geometry |
| `basket_support` | **PARTIAL — RING_HEAD today** | Genuinely both a setting support structure and a ring attachment structure; not force-split |
| Stone placement (girdle Z) | **STONE + RING_HEAD** | The stone builder computes it from `band_top_z + basketHeight` |
| Component roles, connectivity, inspection | **SHARED_ATLAS** | Pre-existing infrastructure |

## Cross-references

- [`setting-domain-model.md`](setting-domain-model.md) — the models in detail.
- [`setting-attachment-interface.md`](setting-attachment-interface.md) — the upward boundary.
- [`stone-setting-interface.md`](stone-setting-interface.md) — the downward boundary.
- [`code-mapping-and-gaps.md`](code-mapping-and-gaps.md) — file-by-file map and the real leaks found.
