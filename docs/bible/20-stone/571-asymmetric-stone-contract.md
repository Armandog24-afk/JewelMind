---
id: JM-BIBLE-571
title: Asymmetric Stone Contract
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
  - JM-BIBLE-565
  - JM-BIBLE-566
  - JM-BIBLE-563
implementation_status: current
professional_validation: not_required
normative: true
---

# Asymmetric Stone Contract

Covers **pear** — the only `ASYMMETRIC` shape, and the shape whose whole purpose in this Sprint was to prove the Stone System does not quietly assume bilateral symmetry on both horizontal axes.

## Status

| Property | Value |
|---|---|
| Symmetry class | `ASYMMETRIC` |
| Symmetric about | local X midplane only (one axis, not two) |
| Required dimensions | `length`, `width`, `depth` |
| Generation | CURRENT |
| Current setting compatibility | `EXPERIMENTAL` |

## Construction

```python
def pear_outline(half_length, half_width, scale):
    hl, hw = half_length * scale, half_width * scale
    return (
        cq.Workplane("XY")
        .moveTo(0, hl)                                # the TIP, at +Y
        .lineTo(hw, -hl + hw)                         # straight right side
        .threePointArc((0, -hl), (-hw, -hl + hw))     # rounded end, through -Y
        .close()                                      # straight left side
        .val()
    )
```

**The tip is at `(0, +half_length)`; the rounded end is at `(0, −half_length)`.** This convention is fixed by the construction starting at the tip, and it is what `orientation = 0` means for a pear (see [`565-stone-coordinate-and-orientation.md`](565-stone-coordinate-and-orientation.md)).

The outline is a **simplified, non-tangent silhouette**: the two straight sides meet the end arc at a non-zero angle rather than tangentially. A real commercial pear has a smooth continuous curve from tip to shoulder to belly. This is deliberate — the construction is robust and fully deterministic, and a tangent-continuous variant would need spline fitting with no gain in reference usefulness. Stated plainly rather than implied, per STONE-GOV-011.

## Why pear is the important case

Six of the seven shapes are bilaterally symmetric about **both** horizontal midplanes. Any code that assumes that — a measurement helper, a placement calculation, an inspection fact, a Golden comparison — is correct for those six and **silently wrong** for pear. Pear is therefore the shape that turns an unstated assumption into an observable failure.

Concretely, the assumption could hide in:

- a bounding-box-centre-based measurement that reports a "centre" the stone's mass is nowhere near;
- an orientation implementation that rotates about the wrong point, translating the stone;
- a prong layout derived only from a radius, with no notion of which end is pointed;
- a Golden snapshot that captures only volume and extents, both of which a symmetrized pear would still match.

## The genuinely discriminating signal

Volume and bounding-box extents are **not** sufficient to prove asymmetry: two different shapes can differ in volume while both being symmetric. The real signal is the **centroid offset along Y** — the signed distance from the solid's bounding-box centre to its actual centre of mass:

```python
offset_y = component.shape.Center().y - (bb.ymin + bb.ymax) / 2
```

A shape symmetric about its own Y midplane has a centroid exactly at the bounding-box centre. Real measured values at `length = 9.0, width = 6.0, depth = 4.0`:

| Shape | bbox centre Y | centroid Y | offset |
|---|---|---|---|
| `pear` | +0.000000 | **−0.737306** | **−0.737306** |
| `oval` | +0.000000 | +0.000002 | +0.000002 |
| `marquise` | +0.000000 | +0.000000 | +0.000000 |

Pear's mass sits 0.737 mm toward the rounded end (−Y), exactly as the outline predicts. The two symmetric `ELONGATED_SMOOTH` shapes at identical dimensions sit at zero to within floating-point noise — they are the control case that makes the pear assertion meaningful rather than trivially true.

Under a 180° rotation the offset flips sign with the same magnitude:

| Orientation | centroid Y offset |
|---|---|
| `0°` | −0.737306 |
| `180°` | **+0.737306** |

That is a real semantic flip of the tip direction, not merely a rigid motion that happens to preserve volume.

## What the tests actually prove

`test_stone.py::TestPearAsymmetry`, 6 tests:

| Test | What it proves |
|---|---|
| `test_pear_mass_is_offset_toward_the_rounded_end` | Pear's centroid offset is `< −0.5` mm — mass genuinely on the −Y side, matching the tip-at-+Y convention. |
| `test_symmetric_elongated_shapes_have_no_centroid_offset` (×2: oval, marquise) | The control: same class and dimensions, offset `< 1e-3`. Without this, the pear assertion could pass for a reason that would also hold for a symmetric shape. |
| `test_rotating_pear_180_degrees_flips_the_tip_direction` | `offset0 < 0 < offset180` **and** `offset180 ≈ −offset0` — a true directional flip — **and** volume/extents preserved, so it is a rigid motion rather than a reshape. |
| `test_rotating_pear_180_degrees_is_not_a_no_op` | Guards the specific regression where `_apply_orientation()` might early-return for any angle, silently making orientation inert. |
| `test_pear_generator_never_silently_produces_a_symmetric_fallback` | Structural: `_NON_ROUND_OUTLINE_BUILDERS["pear"]` is not the same object as oval's or marquise's builder — no silent fallback to another shape's generator (STONE-GOV-013). |

An earlier draft of the first test compared pear against oval with an `or` between a centre check and a volume check. It passed — but via the volume clause, since pear (57.413 mm³) and oval differ anyway. That would have proven only "pear is not oval", not "pear is asymmetric". It was replaced with the centroid-offset assertions above precisely because the weaker form could pass for the wrong reason. Recorded here because it is the kind of near-miss worth not repeating: **an assertion joined by `or` is only as strong as its weakest branch.**

## Real generated result

`pear`, 9.0 × 6.0 mm, depth 4.0 → **57.413477 mm³**, one valid solid.

Worth noting against oval: at the *same* 9 × 6 extents, pear encloses less volume than oval (57.413 vs 75.769) because one end tapers to a point. Full record in `specs/stone/v1/examples/pear.json`; orientation data at 0°/90°/180° in `specs/stone/v1/test-vectors/orientation-vectors.json`. Golden case: `SOL-014-pear-solitaire` (9 × 6).

## Anchors

Pear is the one shape with meaningful shape-specific geometric anchors — a `TIP` at `(0, +length/2)` and a `ROUNDED_END` at `(0, −length/2)`. These are **geometric anchors, not mandatory prong positions**, and they are documented conceptual positions derivable from the outline and bounding box rather than a separate implemented API this Sprint. See [`573-stone-setting-interface.md`](573-stone-setting-interface.md).

## Setting compatibility

`EXPERIMENTAL`. The capability registry records the reason: *"One pointed tip, one rounded end. Current prong placement is generic/circular, not tip-aware."*

A real pear setting protects the tip, usually with a dedicated V-prong, because the tip is the most vulnerable point on the stone. The current layout distributes prongs evenly around a circle derived from `resolved_width_mm` and has no concept of a tip at all — so the pear's most fragile feature is precisely what it fails to support. Reported honestly rather than approximated; shape-aware placement is Sprint 19's Setting System.

## Not a gemological claim

The outline is a simplified non-tangent pear silhouette with a three-level ruled loft. It reproduces no commercial pear-cut faceting or proportion standard, and `isGemologicalReproduction` is `false` (STONE-GOV-011).
