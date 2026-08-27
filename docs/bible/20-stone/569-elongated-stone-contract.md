---
id: JM-BIBLE-569
title: Elongated Stone Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-STONE-README
  - JM-BIBLE-560
related_documents:
  - JM-BIBLE-566
  - JM-BIBLE-567
  - JM-BIBLE-563
implementation_status: current
professional_validation: not_required
normative: true
---

# Elongated Stone Contract

Covers the two `ELONGATED_SMOOTH` shapes: **oval** and **marquise**. Both are bilaterally symmetric on both horizontal axes, both have a smooth (arc- or ellipse-based) perimeter, and both have genuinely distinct major and minor axes.

They share a class but **not** an implementation — see [`563-stone-shape-model.md`](563-stone-shape-model.md) on why classification never implies identical construction.

## OVAL

| Property | Value |
|---|---|
| Symmetry class | `ELONGATED_SMOOTH` |
| Required dimensions | `length`, `width`, `depth` |
| Generation | CURRENT |
| Current setting compatibility | `EXPERIMENTAL` |

### Construction

```python
def oval_outline(half_length, half_width, scale):
    return cq.Workplane("XY").ellipse(half_width * scale, half_length * scale).val()
```

A true ellipse, not a scaled circle and not a polygonal approximation. The X radius comes first because that is CadQuery's `ellipse()` signature; `half_width` maps to X and `half_length` to Y per [`565-stone-coordinate-and-orientation.md`](565-stone-coordinate-and-orientation.md).

Lofted through the three standard levels (culet 0.05, girdle 1.0, table 0.56) with the shared 0.35/0.65 crown/pavilion split.

### Real generated result

`oval`, 8.0 × 6.0 mm, depth 4.0 → **67.350 mm³**, one valid solid.

Bounding box (from `specs/stone/v1/examples/oval.json`): X extent 6.0, Y extent 8.0 — matching the requested width and length. Recorded live-verified data in that file.

### Why oval is the reference non-round case

Oval is the simplest genuinely non-round shape: a single primitive, no corners, no asymmetry, no pointed features. It is therefore the shape used as the required minimum non-round assembly proof (brief section 28) and is the first new Golden case, `SOL-013-oval-solitaire`. If the shared loft pipeline works at all, it works here; if it fails here, nothing else is worth debugging.

## MARQUISE

| Property | Value |
|---|---|
| Symmetry class | `ELONGATED_SMOOTH` |
| Required dimensions | `length`, `width`, `depth` |
| Generation | CURRENT |
| Current setting compatibility | `EXPERIMENTAL` |

### Construction

```python
def marquise_outline(half_length, half_width, scale):
    hl, hw = half_length * scale, half_width * scale
    return (
        cq.Workplane("XY")
        .moveTo(0, hl)
        .threePointArc((hw, 0), (0, -hl))     # right flank, tip to tip
        .threePointArc((-hw, 0), (0, hl))     # left flank, back to start
        .close()
        .val()
    )
```

Two arcs forming a symmetric lens. Each arc is defined by its start point (a tip), a midpoint at the widest part of that flank, and its end point (the other tip). Both tips lie on the Y axis at `(0, ±half_length)`.

Because the two arcs meet at the tips at a non-zero angle, the tips are genuine corners in the wire — the outline is a true pointed lens, not a rounded-off approximation.

### Real generated result

`marquise`, 10.0 × 5.0 mm, depth 4.0 → **62.430 mm³**, one valid solid.

A useful cross-check: at a *greater* length than oval (10 vs 8) and a *smaller* width (5 vs 6), marquise encloses less volume (62.430 vs 67.350) — exactly what a lens outline should do against an ellipse.

### No tip stabilization was needed — and none exists

The brief pre-authorized a microscopic computational stabilization for pointed shapes, on the condition it be explicit, deterministic, and documented as a geometry-engine accommodation rather than a jewelry standard:

> *"Avoid numerically fragile infinitely sharp constructs if OpenCascade becomes unstable. A microscopic purely computational stabilization is allowed only if: explicit; deterministic; documented as geometry-engine accommodation; not as jewelry standard."*

**It turned out to be unnecessary, and therefore none was implemented.** This was the single riskiest going-in assumption of the Sprint, and it was tested before writing production code rather than assumed. The pointed shapes were prototyped against the real installed CadQuery 2.8.0 / OpenCascade and verified for:

- a valid closed wire at every loft level (including the 5%-scale culet, where the tips are closest together),
- a single valid solid from the three-level ruled loft,
- a clean STEP export and re-import roundtrip,
- correct behaviour under a 90° rotation.

All passed with the sharp construction as written. `outline.py` contains **no** tip blunting, no minimum-radius clamp, and no epsilon offset at the tips.

This matters to state plainly, because a future reader might reasonably expect stabilization to be there and "restore" it. If a future proportion or shape *does* prove unstable, that stabilization must be added deliberately, documented as a geometry-engine accommodation, and covered by its own test — not retro-fitted quietly.

The one real accommodation that *does* exist for all non-round shapes is the proportional culet (`_CULET_SCALE_RATIO = 0.05` rather than a degenerate point), documented in [`567-stone-reference-geometry-contract.md`](567-stone-reference-geometry-contract.md).

## Shared verified behaviour

Both shapes are covered by real tests:

| Test | What it proves |
|---|---|
| `TestNonRoundShapeGeneration::test_shape_generates_single_valid_positive_volume_solid` | One valid solid, finite positive non-NaN volume. |
| `TestNonRoundShapeGeneration::test_shape_bounding_box_matches_requested_length_and_width_at_default_orientation` | Real measured extents match requested `length`/`width`. |
| `TestNonRoundShapeGeneration::test_shape_reference_stays_separate_from_metal` | StoneReference sits above the band, never fused. |
| `TestStoneOrientation::test_90_degree_rotation_swaps_bounding_box_extents` | Applied to **both** oval and marquise: rotation swaps Y/X extents and preserves volume. |
| `TestStoneStlExport::test_stl_structure_has_no_regressions` | Includes marquise (and oval) — real STL structure check. |
| `TestStoneStepExport::test_step_roundtrip_has_no_regressions` | Includes oval — real STEP roundtrip. |

Golden coverage: `SOL-013-oval-solitaire` (8 × 6) and `SOL-018-marquise-solitaire` (10 × 5).

## Setting compatibility

Both are `EXPERIMENTAL`. For marquise the capability registry records the specific reason:

> *"Two-arc pointed lens outline. Current prong placement does not cluster prongs at the tips."*

A real marquise setting places prongs (often V-shaped) at the two tips, because that is where the stone is most vulnerable. The current prong layout distributes prongs evenly around a circle derived from `resolved_width_mm`, which for a 10 × 5 marquise is a circle far narrower than the stone's length — the tips are left entirely unsupported. This is honestly reported rather than papered over; shape-aware placement is Sprint 19's Setting System. See [`573-stone-setting-interface.md`](573-stone-setting-interface.md).

## Not a gemological claim

Neither outline reproduces a commercial cut. A real marquise has a defined length-to-width ratio range and a specific facet arrangement; a real oval brilliant has a defined facet count. These are **reference outlines** with a shared three-level loft, and `isGemologicalReproduction` is `false` for both (STONE-GOV-011).
