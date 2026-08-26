---
id: JM-BIBLE-550
title: Head Connection Interface
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
  - JM-BIBLE-541
related_documents:
  - JM-BIBLE-526
  - JM-BIBLE-120
implementation_status: current
professional_validation: not_required
normative: true
---

# Head Connection Interface

## The contract

`geometry/connection.py::ShankConnectionInterface` is the one real, named contract between the Shank subsystem and the `RingHead` component builders (`prongs.py`, `basket.py`):

```python
class ShankConnectionInterface(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topZMm: float
    embedMm: float
    headCenterRadiusMm: float
```

```python
def shank_connection_interface(definition: JewelryDefinition) -> ShankConnectionInterface:
    return ShankConnectionInterface(
        topZMm=band_top_z(definition),
        embedMm=EMBED_MM,
        headCenterRadiusMm=prong_center_radius(definition),
    )
```

- `topZMm` — the Z coordinate of the top of the shank at the head, from `geometry/constants.py::band_top_z()`.
- `embedMm` — the fixed embedding depth constant `EMBED_MM`, unchanged from before this Sprint.
- `headCenterRadiusMm` — the radial distance at which prong/basket geometry is centered, from `geometry/constants.py::prong_center_radius()`.

Both `_build_uniform_shank()` and `_build_tapered_shank()` call `shank_connection_interface(definition)` and embed its three fields, unmodified, as `metadata["connectionInterface"]` on the returned `GeneratedComponent` — the shape is identical in both the `UNIFORM` and `TAPERED` metadata forms (see [`542-shank-domain-model.md`](542-shank-domain-model.md)).

## Why it lives in the Atlas layer, not Ring

`geometry/connection.py` is not a Ring-domain concept even though it names a Ring-specific handoff. It lives at `backend/jewelmind/geometry/connection.py` — inside Atlas — because its two consumers, `prongs.py` and `basket.py`, are themselves Atlas-layer component builders (Sprint 5), and Atlas's own layering rule is that `jewelmind.ring` depends on Atlas, never the reverse (see [`18-ring-architecture/520-jewelry-category-architecture.md`](../18-ring-architecture/520-jewelry-category-architecture.md)). If `ShankConnectionInterface` lived under `jewelmind.ring`, `prongs.py`/`basket.py` would have to import from `jewelmind.ring` to consume it, which is exactly the dependency direction Atlas forbids.

This is not a hypothetical concern: an earlier version of this exact module was placed inside `jewelmind/ring/` during this Sprint's own implementation and produced a real, reproducible circular import (`jewelmind.ring.adapter` → `jewelmind.jewelry_category` → `dispatch.py` → `jewelmind.ring.families` → `jewelmind.geometry.assemblies.solitaire` → `geometry/components/basket.py` → back to the Ring-layer connection module). The fix was to relocate the module to `jewelmind/geometry/connection.py` with no change to `ShankConnectionInterface`'s fields or `shank_connection_interface()`'s computation — see [`541-shank-architecture-overview.md`](541-shank-architecture-overview.md) for the full account and how the fix was verified (SHANK-GOV-006).

## Before this Sprint

Before Sprint 17, `prongs.py` and `basket.py` each independently imported `band_top_z()`, `prong_center_radius()`, and `EMBED_MM` directly from `geometry/constants.py` — two separate, unrelated import sites reaching for the same real values, with no single name identifying them as one logical handoff. `geometry/connection.py` is a thin, behavior-preserving re-export: the underlying computation (`band_top_z()`, `prong_center_radius()`, `EMBED_MM`) is unchanged; what changed is that there is now one explicit interface name, `ShankConnectionInterface`, that both component builders and any future caller read (SHANK-GOV-010).

## The guarantee: it never moves for a tapered shank

`_build_tapered_shank()` anchors the taper's full base width and thickness exactly at `u=0` — the head — by construction: `taper_ratio(0.0, taper)` always returns `1.0` regardless of `taper.mode` or `bottomRatio` (see `taper.py::taper_ratio()` and [`548-taper-model.md`](548-taper-model.md)). `angle_deg_for_u(0.0)` maps to `-90` degrees, the same reference point `band_top_z()` already computes against (`x=0, z=+outer_radius`). Because of this, `topZMm`, `embedMm`, and `headCenterRadiusMm` are identical for every taper configuration — uniform, width-tapered, thickness-tapered, or combined (SHANK-GOV-011).

The practical consequence, verified by the code itself rather than assumed: `prongs.py`/`basket.py` required zero changes for this Sprint. Neither module's placement logic references `widthTaper`/`thicknessTaper` at all — it consumes only `ShankConnectionInterface`, and that interface's values are computed the same way regardless of taper. This is also why no new Golden case (SOL-010/011/012) shows any prong/basket displacement relative to their untapered counterparts — see [`555-shank-golden-strategy.md`](555-shank-golden-strategy.md).

## What this interface does not do

`ShankConnectionInterface` is a placement contract, not a geometric-fact report — it says where the head sits relative to the shank, not what shape the shank is at that point. It carries no width/thickness sample and is not the same thing as the `widthSamplesMm`/`thicknessSamplesMm` construction parameters on tapered metadata (see [`553-shank-inspection-contract.md`](553-shank-inspection-contract.md)). Widening it to carry additional per-`u` geometric information, or moving its anchor away from `u=0` (the `taper_toward_head` planned capability), would be a real change to `SHANK_CAPABILITIES` and requires the ADR process in [`540-shank-governance.md`](540-shank-governance.md#when-an-adr-is-required).
