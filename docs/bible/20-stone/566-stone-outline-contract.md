---
id: JM-BIBLE-566
title: Stone Outline Contract
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
  - JM-BIBLE-563
  - JM-BIBLE-567
  - JM-BIBLE-572
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Outline Contract

## The 2D / 3D separation

`backend/jewelmind/geometry/stone/outline.py` contains only 2D outline generation. It has no knowledge of depth, crown, pavilion, girdle Z, orientation, or the assembly. `builder.py` owns all of that.

The contract of every function in the module:

```
outline_fn(half_length, half_width, scale) -> closed cq.Wire in the local XY plane at Z = 0
```

(`round_outline` takes `(radius, scale)` instead, since a circle has one half-extent.)

Three properties hold for all of them:

- **Closed.** Every function ends in `.close()` where the construction needs it, and returns `.val()` — a real `cq.Wire`, never an `Edge`. This is not cosmetic: see the recorded API finding in [`572-stone-generation-pipeline.md`](572-stone-generation-pipeline.md).
- **Scaled, not re-parameterised.** `scale` multiplies the half-extents uniformly, so the same function produces the culet, girdle, and table outlines of one stone. Every level is self-similar by construction, which is what makes the loft well-behaved.
- **Pure.** No shape reads global state, wall-clock time, or randomness (STONE-GOV-002).

`half_length` is the Y half-extent, `half_width` the X half-extent — see [`565-stone-coordinate-and-orientation.md`](565-stone-coordinate-and-orientation.md).

## The 7 outlines

### `round_outline(radius, scale)`

```python
cq.Workplane("XY").circle(radius * scale).val()
```

### `oval_outline(half_length, half_width, scale)`

```python
cq.Workplane("XY").ellipse(half_width * scale, half_length * scale).val()
```

Note the argument order: CadQuery's `ellipse()` takes the X radius first, so `half_width` comes first.

### `marquise_outline(half_length, half_width, scale)`

Two arcs forming a symmetric pointed lens, meeting at a point on each end of the major axis:

```python
.moveTo(0, hl)
.threePointArc((hw, 0), (0, -hl))     # right side, tip to tip
.threePointArc((-hw, 0), (0, hl))     # left side, back to start
.close()
```

Both tips lie on the Y axis at `(0, ±hl)`.

### `pear_outline(half_length, half_width, scale)`

```python
.moveTo(0, hl)                                    # the TIP, at +Y
.lineTo(hw, -hl + hw)                             # straight right side
.threePointArc((0, -hl), (-hw, -hl + hw))         # rounded end at -Y
.close()                                          # straight left side
```

A **simplified, non-tangent silhouette**: two straight sides meeting a rounded end. It is deterministic and robust, and it is deliberately *not* a smooth commercial pear outline — the straight sides do not meet the end arc tangentially. See [`571-asymmetric-stone-contract.md`](571-asymmetric-stone-contract.md).

### `emerald_outline(half_length, half_width, scale)`

An 8-point `.polyline()`: a rectangle with all four corners clipped diagonally.

```python
clip = _EMERALD_CORNER_CLIP_RATIO * min(hw, hl)   # 0.18
points = [
    (hw - clip, hl), (hw, hl - clip), (hw, -hl + clip), (hw - clip, -hl),
    (-hw + clip, -hl), (-hw, -hl + clip), (-hw, hl - clip), (-hw + clip, hl),
]
```

`_EMERALD_CORNER_CLIP_RATIO = 0.18` is a fixed **software reference construction** parameter, not a gemological or industry corner ratio (STONE-GOV-011). The clip is proportional to `min(hw, hl)` so it scales sensibly for both near-square and strongly elongated emeralds, and so the clip can never exceed the shape's own smaller half-extent.

### `princess_outline(half_length, half_width, scale)`

```python
cq.Workplane("XY").rect(2 * half_width * scale, 2 * half_length * scale).val()
```

A plain rectangle. **Non-square rectangles are supported**, not an error: the shape is square only when `length == width`. See [`570-angular-stone-contract.md`](570-angular-stone-contract.md).

### `cushion_outline(half_length, half_width, scale)`

Four straight edges joined by four quarter-circle arcs:

```python
cr = _CUSHION_CORNER_RATIO * min(hw, hl)   # 0.25
k  = cr * cos(45°)
```

Each corner is a `threePointArc` whose midpoint is offset by `k` from the corner centre along both axes — the point on a quarter circle at 45°. Getting this formula right required two real corrections against OpenCascade; both are recorded in [`572-stone-generation-pipeline.md`](572-stone-generation-pipeline.md). `_CUSHION_CORNER_RATIO = 0.25` is likewise a software reference constant.

## Why the separation matters

The outline is the reusable half of stone geometry. Keeping it independent of the 3D loft is what makes these future capabilities additive rather than rewrites:

- **Bezels** — a bezel wall is an offset of the stone's girdle outline.
- **Halos** — a halo path is an outward offset of the same outline.
- **Pavé boundaries** — a pavé region is bounded by an offset outline.
- **Stone seats / bearing cuts** — a seat is cut from the girdle outline swept downward.
- **Clearance envelopes** — a clearance check needs the outline, not the faceted solid.

Every one of those consumes a 2D profile. If outline generation had been fused into the loft builder, each would have had to re-derive the profile from a finished solid's faces — fragile, and different per shape.

## What is explicitly not built here

**No setting geometry.** `outline.py` produces stone profiles only. It contains no prong position, no bezel wall, no seat, no basket, and no offset operation. Offsetting an outline for a setting is the Setting layer's job (STONE-GOV-009), and none of it exists yet — see [`573-stone-setting-interface.md`](573-stone-setting-interface.md) and Sprint 19.

**No depth or vertical structure.** Every function returns a planar wire at `Z = 0`. Translation to the culet/girdle/table planes happens in `builder.py`.

**No orientation.** Rotation is applied to the finished solid, not the outline.

## Recorded outline data

`specs/stone/v1/test-vectors/dimension-vectors.json` and the 7 files in `specs/stone/v1/examples/` record real generated results per shape. Outline correctness is exercised indirectly but genuinely: every shape's bounding box is asserted against its requested length/width, and every shape must produce a single valid solid when lofted — a malformed or self-intersecting outline would fail both.

## Cross-references

- [`567-stone-reference-geometry-contract.md`](567-stone-reference-geometry-contract.md) — how these outlines become a 3D solid.
- [`563-stone-shape-model.md`](563-stone-shape-model.md) — the registry that maps shape to outline function.
