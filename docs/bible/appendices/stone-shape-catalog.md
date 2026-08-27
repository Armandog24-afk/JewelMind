---
id: JM-BIBLE-A114
title: "Appendix: Stone Shape Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-STONE-README
  - JM-BIBLE-560
related_documents:
  - JM-BIBLE-563
  - JM-BIBLE-566
  - JM-BIBLE-A115
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Stone Shape Catalog

Per-shape geometric detail for all 7 CURRENT stone shapes, sourced from `backend/jewelmind/geometry/stone/outline.py`, `builder.py`, `capability.py`, and the real generated records in `specs/stone/v1/examples/`.

**No entry below is a gemological or commercial-cut claim.** Every construction constant is `provenance: software_reference_profile` — a deterministic software choice verified only to produce robust CAD geometry (STONE-GOV-011). Every shape's `isGemologicalReproduction` is `false`.

## Summary

| Shape | Symmetry class | Required dimensions | Outline primitive | Setting compat. |
|---|---|---|---|---|
| `round` | `RADIAL` | `diameter`, `depth` | `.circle()` | **`SUPPORTED`** |
| `oval` | `ELONGATED_SMOOTH` | `length`, `width`, `depth` | `.ellipse()` | `EXPERIMENTAL` |
| `marquise` | `ELONGATED_SMOOTH` | `length`, `width`, `depth` | 2 × `threePointArc` | `EXPERIMENTAL` |
| `pear` | `ASYMMETRIC` | `length`, `width`, `depth` | 2 lines + 1 arc | `EXPERIMENTAL` |
| `emerald` | `RECTILINEAR_ANGULAR` | `length`, `width`, `depth` | 8-point `.polyline()` | `EXPERIMENTAL` |
| `princess` | `RECTILINEAR_ANGULAR` | `length`, `width`, `depth` | `.rect()` | `EXPERIMENTAL` |
| `cushion` | `ROUNDED_RECTILINEAR` | `length`, `width`, `depth` | 4 lines + 4 arcs | `EXPERIMENTAL` |

## Shared construction (all 7 shapes)

Every shape is a 3-level ruled loft (culet → girdle → table) through self-similar outlines of itself:

| Constant | Value | Meaning |
|---|---|---|
| `_CROWN_FRACTION` | `0.35` | Fraction of `depth` above the girdle. |
| `_PAVILION_FRACTION` | `0.65` | Fraction of `depth` below the girdle. |
| `_TABLE_TO_GIRDLE_RATIO` | `0.56` | Outline scale at the table level. |
| girdle plane Z | `band_top_z + setting.basketHeight` | The assembly's stone anchor. |

## Per-shape detail

### `round`

- **Construction:** `.circle(radius * scale)`. Built by `_build_round_stone()` via the fluent `Workplane.loft()` chain — the byte-identical pre-Sprint-18 path (STONE-GOV-016).
- **Culet:** `_CULET_RADIUS_MM = 0.05` — an **absolute** 0.05 mm circle, unlike every other shape.
- **Extra metadata:** `girdleRadiusMm`, `tableRadiusMm` — meaningful only for a radially symmetric outline.
- **Real generated result:** d = 6.5, depth 4.0 → **58.221419 mm³**, 1 solid.
- **Orientation:** geometrically inert (`RADIAL`).

### `oval`

- **Construction:** `.ellipse(half_width * scale, half_length * scale)` — a true ellipse. Note the X radius comes first, per CadQuery's signature.
- **Real generated result:** 8.0 × 6.0, depth 4.0 → **67.350 mm³**, 1 solid.
- **Setting reason recorded:** *"Prong placement is generic/circular, not shape-optimized."*

### `marquise`

- **Construction:** two `threePointArc` calls forming a symmetric pointed lens; both tips on the Y axis at `(0, ±half_length)`.
- **Real generated result:** 10.0 × 5.0, depth 4.0 → **62.430 mm³**, 1 solid.
- **No tip stabilization exists.** The pre-authorized microscopic blunting proved unnecessary and was not implemented — see [`../20-stone/569-elongated-stone-contract.md`](../20-stone/569-elongated-stone-contract.md).
- **Setting reason recorded:** *"Placement does not cluster prongs at the tips."*

### `pear`

- **Construction:** `.moveTo(0, hl)` → `.lineTo(hw, -hl + hw)` → `.threePointArc((0, -hl), (-hw, -hl + hw))` → `.close()`.
- **Convention:** **TIP at `+Y`, rounded end at `−Y`** at `orientation = 0`.
- **Real generated result:** 9.0 × 6.0, depth 4.0 → **57.413477 mm³**, 1 solid.
- **Measured asymmetry:** centroid Y offset **−0.737306 mm** from the bounding-box centre (vs ~0 for oval/marquise at identical dimensions). Flips to **+0.737306** at 180°.
- **Known limitation:** a simplified **non-tangent** silhouette — the straight sides meet the end arc at a non-zero angle.
- **Setting reason recorded:** *"Placement is not tip-aware."*

### `emerald`

- **Construction:** 8-point `.polyline()` — a rectangle with all four corners clipped diagonally.
- **Corner constant:** `_EMERALD_CORNER_CLIP_RATIO = 0.18`, applied as `0.18 * min(half_width, half_length)`. **Not** an industry corner ratio.
- **Real generated result:** 8.0 × 6.0, depth 4.0 → **84.711 mm³**, 1 solid.
- **Scope:** reproduces the clipped-corner *outline* only; the stepped crown/pavilion faceting that defines a real emerald cut is not modelled.
- **Setting reason recorded:** *"Placement is not corner-aware."*

### `princess`

- **Construction:** plain `.rect(2 * half_width * scale, 2 * half_length * scale)`.
- **Rectangular princess IS supported** — no squareness constraint exists. Square only when `length == width`.
- **Real generated result:** 6.5 × 6.5, depth 4.0 → **75.480 mm³**, 1 solid.
- **Setting reason recorded:** *"Placement is not corner-aware."*

### `cushion`

- **Construction:** 4 straight edges + 4 quarter-circle `threePointArc` corners.
- **Corner constants:** `_CUSHION_CORNER_RATIO = 0.25` (as `0.25 * min(half_width, half_length)`); arc midpoints offset by `k = cr * cos(45°)`.
- **Real generated result:** 7.0 × 7.0, depth 4.0 → **86.365 mm³**, 1 solid.
- **Two real OCC failures preceded this formulation** — a fillet-on-thin-extrusion attempt (`BRep_API: command not done`) and a non-co-circular arc (`StdFail_NotDone`). See [`../20-stone/572-stone-generation-pipeline.md`](../20-stone/572-stone-generation-pipeline.md).
- **Scope:** no commercial cushion subtype semantics are modelled or implied.
- **Setting reason recorded:** *"Placement is not corner-aware."*

## Non-round culet accommodation

Every non-round shape uses `_CULET_SCALE_RATIO = 0.05` — the shape's own girdle outline scaled to 5% — rather than an absolute radius. A genuinely degenerate culet (a point, or a zero-area wire) is exactly the input that makes OpenCascade lofts fail or produce invalid solids. This is a documented **geometry-engine accommodation**, not a jewelry standard.

## Volume cross-check

At `depth = 4.0`, the ordering is a useful sanity signal in itself:

| Shape | Dimensions | Volume (mm³) |
|---|---|---|
| `cushion` | 7 × 7 | 86.365 |
| `emerald` | 8 × 6 | 84.711 |
| `princess` | 6.5 × 6.5 | 75.480 |
| `oval` | 8 × 6 | 67.350 |
| `marquise` | 10 × 5 | 62.430 |
| `round` | d 6.5 | 58.221 |
| `pear` | 9 × 6 | 57.413 |

The angular shapes enclose more volume than the smooth ones at comparable extents, and pear encloses less than oval at a *greater* length — both follow directly from the outline areas, as they should.

## Cross-references

- [`stone-capability-catalog.md`](stone-capability-catalog.md) (A115) — the full machine-readable capability registry.
- [`stone-test-matrix.md`](stone-test-matrix.md) (A116) — which test verifies what.
- [`../20-stone/566-stone-outline-contract.md`](../20-stone/566-stone-outline-contract.md) — the outline contract these implement.
- `specs/stone/v1/examples/` — the real generated records this table restates.
