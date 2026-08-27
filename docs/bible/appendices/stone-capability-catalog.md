---
id: JM-BIBLE-A115
title: "Appendix: Stone Capability Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-STONE-README
  - JM-BIBLE-560
related_documents:
  - JM-BIBLE-575
  - JM-BIBLE-A114
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Stone Capability Catalog

The complete, current catalog of all 7 stone shapes — the human-readable companion to `specs/stone/v1/shape-registry.json`, which is generated from and re-derived live against `backend/jewelmind/geometry/stone/capability.py::STONE_SHAPE_CAPABILITIES`, the real source of truth (STONE-GOV-014).

No documentation, Designer capability list, or Studio option may claim a capability this registry marks otherwise.

## Capability axes

| Axis | Meaning |
|---|---|
| `status` | `current` or `planned`. |
| `generationSupported` | `build_stone()` constructs real CAD geometry. |
| `jdlSupported` | A real, accepted `StoneShape` enum member. |
| `inspectionSupported` | Covered by real runtime inspection facts (generic component facts + the 6 `STONE_*` dimension facts). |
| `visionSupported` | Vision renders the shape's real generated geometry. |
| `currentSettingCompatibility` | Whether the **current** setting geometry places metal meaningfully. **Independent of generation** (STONE-GOV-009). |
| `requiredDimensions` | Which `stone.*` fields must be set. |
| `symmetryClass` | Shared geometric strategy grouping. |
| `referenceGeometryVersion` | Bumped on any MAJOR change to outline/loft construction. |

## The registry

| Shape | status | gen | jdl | inspect | vision | setting compat. | required dims | symmetry class | ref geom ver |
|---|---|---|---|---|---|---|---|---|---|
| `round` | current | ✔ | ✔ | ✔ | ✔ | **`SUPPORTED`** | `diameter`, `depth` | `RADIAL` | `1.0.0` |
| `oval` | current | ✔ | ✔ | ✔ | ✔ | `EXPERIMENTAL` | `length`, `width`, `depth` | `ELONGATED_SMOOTH` | `1.0.0` |
| `marquise` | current | ✔ | ✔ | ✔ | ✔ | `EXPERIMENTAL` | `length`, `width`, `depth` | `ELONGATED_SMOOTH` | `1.0.0` |
| `pear` | current | ✔ | ✔ | ✔ | ✔ | `EXPERIMENTAL` | `length`, `width`, `depth` | `ASYMMETRIC` | `1.0.0` |
| `emerald` | current | ✔ | ✔ | ✔ | ✔ | `EXPERIMENTAL` | `length`, `width`, `depth` | `RECTILINEAR_ANGULAR` | `1.0.0` |
| `princess` | current | ✔ | ✔ | ✔ | ✔ | `EXPERIMENTAL` | `length`, `width`, `depth` | `RECTILINEAR_ANGULAR` | `1.0.0` |
| `cushion` | current | ✔ | ✔ | ✔ | ✔ | `EXPERIMENTAL` | `length`, `width`, `depth` | `ROUNDED_RECTILINEAR` | `1.0.0` |

**Total: 7 shapes. Current: 7. Planned: 0.**

## Recorded descriptions

| Shape | `description` |
|---|---|
| `round` | Byte-identical pre-Sprint-18 lofted round-brilliant-style reference. |
| `oval` | Elliptical outline, real CAD loft. Current prong placement is generic/circular, not shape-optimized. |
| `marquise` | Two-arc pointed lens outline. Current prong placement does not cluster prongs at the tips. |
| `pear` | One pointed tip, one rounded end. Current prong placement is generic/circular, not tip-aware. |
| `emerald` | Clipped-corner rectangular outline. Current prong placement is generic/circular, not corner-aware. |
| `princess` | Plain rectangular outline. Current prong placement is generic/circular, not corner-aware. |
| `cushion` | Rounded-rectangle outline. Current prong placement is generic/circular, not corner-aware. |

## Generation is not setting compatibility

The two right-hand columns above are the point of this catalog. All 7 shapes generate real, valid CAD geometry; **only `round` has a setting designed for it.**

Each `EXPERIMENTAL` entry names a real deficiency a jeweller would recognise — unsupported tips on a marquise, an unprotected tip on a pear, exposed corners on an angular stone. The current layout distributes prongs evenly around a circle derived from `resolved_width_mm`, with no notion of tips or corners at all.

`UNSUPPORTED` is a defined third state but no current shape uses it.

## Why no `planned` entries

Future candidate shapes (asscher, radiant, heart, trillion, baguette, cabochon, custom outlines, calibrated stones) are deliberately **not** pre-registered as `planned` — listing them would imply a commitment and a design that does not exist. Each requires an RFC before becoming a registry entry. They are recorded as open questions in [`../20-stone/579-open-stone-questions.md`](../20-stone/579-open-stone-questions.md) instead.

This differs deliberately from the Shank capability registry (A111), which *does* carry `planned` entries — there, named future capabilities had already been architecturally reserved by earlier sprint documentation, so recording them as `planned` was more accurate than omitting them. No equivalent prior commitment exists for stone shapes.

## Invariants enforced by test

| Test | Invariant |
|---|---|
| `test_stone_schemas.py::test_shape_registry_matches_the_real_capability_registry_live` | The JSON mirror equals the live registry, field for field. |
| `test_stone_schemas.py::test_shape_registry_entries_validate_against_capability_schema` | Every entry validates against `stone-shape-capability.schema.json`. |
| `test_stone_schemas.py::test_registry_never_marks_a_non_generatable_shape_as_current` | No `current` entry has `generationSupported: false`. |
| `test_stone_schemas.py::test_only_round_is_setting_compatibility_supported` | Exactly `["round"]` is `SUPPORTED` — asserted, not merely described. |
| `test_stone_schemas.py::test_all_seven_target_shapes_are_present_and_current` | The `current` set is exactly the 7 target shapes. |
| `test_stone.py::TestStoneCapabilityRegistry` (5 tests) | Per-shape metadata exists; round is `SUPPORTED`; every non-round shape is `EXPERIMENTAL`; no shape is `planned`; an unknown shape returns `None`. |

The `test_only_round_is_setting_compatibility_supported` assertion is deliberately exact rather than a bound: if a future sprint makes a shape genuinely settable, that test must be updated consciously.

## Hand-mirrored consumers

Two places mirror this registry by hand and must be updated in the same change as any registry change:

- `frontend/src/components/ConfigurationPanel.tsx::STONE_SHAPE_OPTIONS` — the Studio shape selector.
- `backend/jewelmind/designer/normalizer.py::STONE_SHAPE_SYNONYMS` — the IT/EN natural-language table.

Designer's `current_capabilities()` reads `StoneShape` directly via `get_args()`, so it cannot drift.

## Cross-references

- `backend/jewelmind/geometry/stone/capability.py` — the real source of truth.
- `specs/stone/v1/shape-registry.json` — the machine-readable generated mirror.
- [`../20-stone/575-stone-capability-model.md`](../20-stone/575-stone-capability-model.md) — the full narrative contract.
- [`stone-shape-catalog.md`](stone-shape-catalog.md) (A114) — per-shape geometric detail.
