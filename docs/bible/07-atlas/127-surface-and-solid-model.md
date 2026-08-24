---
id: JM-BIBLE-127
title: Surface and Solid Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-124
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Surface and Solid Model

## When a closed solid is required vs. when a compound is acceptable

| Component | Required form | Current form |
|---|---|---|
| `band` | Single closed solid | Single solid, always (revolve always produces one closed solid; the fillet fallback still produces one solid, just unfilleted) |
| `stone_reference` | Single closed solid | Single solid (loft always produces one closed solid for this codebase's valid parameter ranges) |
| `prongs` | Compound acceptable — individual prongs are conceptually separate solids | Always a `cq.Compound` of N solids, even for N=1 or N=0 (empty compound) |
| `basket_support` | Single closed solid | Single solid (cylinder-minus-cylinder cut) |
| `combined_metal` (assembly-level, not a component) | Single fused solid preferred; multi-solid compound acceptable as a documented fallback | Single solid when `.fuse()` succeeds; `cq.Compound` of 3 unfused solids when it does not — see [`134-boolean-operation-strategy.md`](134-boolean-operation-strategy.md) |

## Volume calculation

Every `GeneratedComponent.volume_mm3` comes from CadQuery's `.Volume()` (OCCT's `BRepGProp` volume properties), called once on the final shape after any fallback has already been applied. For `prongs`, the reported volume is the **sum of each individual prong's OCCT-computed volume**, not a single volume computation on the compound (see `prongs.py`: `total_volume = sum(s.Volume() for s in solids)`) — the two are numerically identical for non-overlapping solids, and no current prong configuration produces overlapping prongs.

## Null or empty shapes

The only current path that can produce an empty/zero-volume component is `prongs` with `setting.prongCount <= 0` (which cannot occur through the API, since `JM-PRONG-001` requires `{4, 6}` and blocks generation otherwise — see [`06-forge/105-geometry-precondition-rules.md`](../06-forge/105-geometry-precondition-rules.md)). In that case: `positions = []`, `solids = []`, `compound = cq.Compound.makeCompound([])` (a valid, empty CadQuery compound object, not `None`), `total_volume = 0`, and `bbox = BoundingBox(0, 0, 0, 0, 0, 0)` (an explicit zero box, not a crash). This path is exercised only if `build_prongs()` is called directly (e.g. in a future test or a bypass of validation), never through the normal API flow.

## The four current components, summarized

| Component | Solid strategy | Source |
|---|---|---|
| `band` | Revolve a 2D wire (flat rectangle or comfort-fit arc profile) 360° around Y | `geometry/components/band.py` |
| `stone_reference` | Loft three circular cross-sections (culet → girdle → table) | `geometry/components/stone.py` |
| `prong` (× N, compound) | Extrude a circle along Z for each prong position | `geometry/components/prongs.py` |
| `basket_support` | Cut an inner cylinder from an outer cylinder | `geometry/components/basket.py` |
