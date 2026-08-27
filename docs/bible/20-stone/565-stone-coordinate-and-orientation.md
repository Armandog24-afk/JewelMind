---
id: JM-BIBLE-565
title: Stone Coordinate and Orientation
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
  - JM-BIBLE-564
  - JM-BIBLE-571
  - JM-BIBLE-123
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Coordinate and Orientation

## Inheriting the Atlas convention

Stone System introduces no new coordinate system. It sits inside the existing convention documented in [`../07-atlas/123-coordinate-system-and-orientation.md`](../07-atlas/123-coordinate-system-and-orientation.md) and `docs/geometry-conventions.md`, which this document does not restate. The two facts it depends on:

- All lengths are millimetres; the world origin is the ring's centre.
- The stone, prongs, and basket are built concentric around the vertical line `x=0, y=0` (parallel to global Z), rising in `+Z` from the top of the band.

## Axis assignment

| Dimension | Local axis | Rationale |
|---|---|---|
| **LENGTH** (major horizontal) | **Y** | Y is the finger/hole axis — the axis the band revolves around. A stone's long axis running along Y therefore points along the finger, which is the conventional orientation for an elongated centre stone. |
| **WIDTH** (minor horizontal) | **X** | The remaining horizontal axis, across the finger. |
| **DEPTH** (vertical) | **Z** | Unchanged from pre-Sprint-18 behaviour: the crown rises in `+Z`, the pavilion descends in `−Z`. |

This is explicit and load-bearing, not implied by mesh orientation (ATLAS-GOV-012). Every outline function in `outline.py` takes `half_length` and `half_width` and uses them as the Y and X half-extents respectively — for example `oval_outline` calls `.ellipse(half_width * scale, half_length * scale)`, because CadQuery's `ellipse()` takes the X radius first.

Verified rather than assumed: `test_stone.py::TestNonRoundShapeGeneration::test_shape_bounding_box_matches_requested_length_and_width_at_default_orientation` builds every non-round shape at `length=9.0, width=5.0` and asserts the real bounding box measures 9.0 along Y and 5.0 along X.

## The girdle plane

Every shape's girdle sits at:

```python
girdle_z = band_top_z(definition) + definition.setting.basketHeight
```

This is unchanged from the pre-Sprint-18 round builder and is why a shape change never moves the stone's vertical anchor. The crown extends `depth * 0.35` above this plane and the pavilion `depth * 0.65` below it (see [`567-stone-reference-geometry-contract.md`](567-stone-reference-geometry-contract.md)).

`girdleZMm` is reported in every generated component's metadata, so the Setting layer reads the anchor rather than recomputing it.

## Orientation

`stone.orientation` is a real JDL field: a rotation in **degrees** around the stone's own local vertical axis. Default `0.0`.

```python
def _apply_orientation(shape, orientation_deg):
    if orientation_deg == 0.0:
        return shape
    bb = shape.BoundingBox()
    center = ((bb.xmin + bb.xmax) / 2, (bb.ymin + bb.ymax) / 2, (bb.zmin + bb.zmax) / 2)
    return shape.rotate(center, (center[0], center[1], center[2] + 1), orientation_deg)
```

Four properties are deliberate:

1. **Applied to the finished solid**, after the loft — not baked into the outline sampling. This keeps `outline.py` purely a 2D concern.
2. **Rotated about the stone's own bounding-box centre**, not the world origin. A rotation about the origin would translate the stone as well as turn it, detaching it from the setting.
3. **Around the local vertical axis only.** The rotation axis is constructed as the centre point plus `(0, 0, +1)`. No arbitrary 3D transform is exposed — an unconstrained transform could tilt or displace the stone out of any meaningful relationship with the setting (STONE-GOV-008).
4. **Early-returns unchanged at `0.0`**, so the default path is bit-identical to no orientation code at all. This is what preserves round's byte-identical construction and every pre-Sprint-18 Golden baseline.

It is applied **uniformly for every shape**, including `round`, rather than special-cased away. For a `RADIAL` shape the result is geometrically equivalent (a circle rotated about its own centre is the same circle), so the uniform treatment costs nothing and removes a branch.

### Orientation is not placement

`stone.orientation` describes the stone's orientation **within its own placement frame**. Where the stone sits in the assembly is decided by the category integration (the girdle-plane formula above), and *which* stone sits where in a multi-stone design would be StoneArrangement's concern. Orientation never encodes position.

## Per-shape default (orientation = 0) placement

| Shape | At `orientation = 0` |
|---|---|
| `round` | Rotationally symmetric; orientation has no observable effect. |
| `oval` | Major axis along Y, minor along X. |
| `marquise` | Points at `(0, +length/2)` and `(0, −length/2)` — both tips on the Y axis. |
| `emerald` | Long edges parallel to Y; clipped corners at all four corners. |
| `princess` | Long edges parallel to Y; square when `length == width`. |
| `cushion` | Long edges parallel to Y; four rounded corners. |
| `pear` | **Tip at `(0, +length/2)`; rounded end at `(0, −length/2)`.** |

Pear's row is the one that carries real semantic weight, since it is the only shape where 0° and 180° are visually distinguishable. That convention is fixed by `pear_outline()`'s construction (it starts at `(0, hl)` — the tip) and is documented in [`571-asymmetric-stone-contract.md`](571-asymmetric-stone-contract.md).

## Verified orientation behaviour

Real tests, not assumptions:

| Test | What it proves |
|---|---|
| `TestStoneOrientation::test_round_orientation_does_not_change_volume_or_bounding_box` | A `RADIAL` shape at 45° is volume- and extent-equivalent. |
| `TestStoneOrientation::test_90_degree_rotation_swaps_bounding_box_extents` | For `oval` and `marquise` at `length=9.0, width=5.0`, a 90° rotation swaps the measured Y and X extents and preserves volume. |
| `TestPearAsymmetry::test_rotating_pear_180_degrees_changes_tip_direction` | A 180° pear rotation is a rigid motion: same volume, same extents. |

Real bounding boxes and volumes at 0°/90°/180° for `oval`, `pear`, and `marquise` are recorded in `specs/stone/v1/test-vectors/orientation-vectors.json`, generated by running the real builder.

## Known limitation: measurement under rotation

Geometry Inspection's `STONE_MEASURED_LENGTH`/`STONE_MEASURED_WIDTH` facts read the **axis-aligned** bounding box (`sizeY`/`sizeX`). Those isolate LENGTH from WIDTH exactly only at `orientation == 0`; at an arbitrary angle the axis-aligned box no longer separates the two. This is a real, documented limitation of the current measurement rather than an assumed exactness — see [`574-stone-inspection-contract.md`](574-stone-inspection-contract.md) and the open question in [`579-open-stone-questions.md`](579-open-stone-questions.md).
