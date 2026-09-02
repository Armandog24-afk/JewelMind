---
id: JM-BIBLE-604
title: "Extended Native Shapes"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-602
  - JM-BIBLE-603
related_documents:
  - JM-BIBLE-605
implementation_status: current
professional_validation: not_required
normative: true
---

# Extended Native Shapes

How each Sprint 20 cut is actually built, in
`backend/jewelmind/geometry/stone/outline.py`.

## The dimension contract

**Every outline is built so its real bounding box equals the request**
(STONEV2-GOV-012). That is what lets Geometry Inspection compare REQUESTED
against MEASURED dimensions and expect equality.

This was not free. Four shapes violated it during development, and each was
fixed at the source rather than by adjusting what was reported:

| Shape | Measured overshoot | Cause | Fix |
|---|---|---|---|
| `shield` | 6.05mm for a 6.00mm request | Arc-based lower boundary bulged past the width | Made fully polygonal |
| `trillion` | 7.63mm for 7.00mm | Bowed bottom edge extended below the base | Pre-inset the base vertices by the bulge |
| `half_moon` | 7.50mm for 6.00mm | A circular arc through the chord endpoints has radius > half-length, always | Rebuilt as half an ELLIPSE |
| `heart` | 3.3e-4mm too wide at 8×6 | A fixed-point normalization had not converged | Rebuilt exact by construction |

## The centring invariant

Every outline's bounding-box centre is the local origin (STONEV2-GOV-013).

`half_moon` genuinely violated this and it is worth recording why the bug was
easy to miss: `ellipseArc(..., startAtCurrent=False)` centres the ellipse on the
CURRENT point, so moving to the chord endpoint first — the obvious reading —
produced an outline centred at `(-hw, -hl)`. Its bounding-box **size** was
correct, so a size-only check passed. Only asserting the centre caught it.

## Shape by shape

### `radiant` and `asscher` — clipped rectangles

Both use `_clipped_rectangle` with their own ratio: radiant 0.14, asscher 0.22,
against emerald's 0.18. Three deliberately different values so the three shapes
stay visually distinguishable — a software choice, not a cut specification.

Both are **silhouettes only**. Neither models the radiant brilliant nor the
Asscher step-cut facet pattern (STONEV2-GOV-003).

### `baguette` — a plain rectangle

Geometrically identical to `princess`, kept as its own primitive because the two
are distinct canonical identities. See
[`extended-shape-taxonomy.md`](extended-shape-taxonomy.md).

### `tapered_baguette` and `trapezoid` — explicit taper

Both use `_tapered_quadrilateral(half_length, half_wide, half_narrow, scale)`.

**The taper is a real required dimension**, `stone.narrowWidth`, never a hidden
default ratio (brief section 13). `StoneSpec` rejects a tapered shape without
it, and rejects a `narrowWidth` greater than `width`.

**Convention:** the WIDE end is at −Y, the NARROW end at +Y. Fixed so the
`WIDE_END`/`NARROW_END` anchors mean the same thing for both shapes.

### `triangle` — straight sides

An isosceles triangle, apex at +Y. Deliberately NOT `trillion`.

### `trillion` — bowed sides

A triangle whose three sides bow outward by `_TRILLION_BULGE_RATIO` (0.18) of
half-length, measured perpendicular to each side from the centroid.

The base vertices are pre-inset by exactly the bulge amount, so the bowed bottom
edge lands on −half_length rather than beyond it. The tip remains the Y maximum
because the two upper edges' bulged midpoints stay below it.

### `lozenge` — a rhombus

Four vertices on the two axes. **Named LOZENGE, never "diamond"**: in JewelMind
"diamond" is a gem species, and a shape ID must never collide with gem identity
(STONEV2-GOV-008).

### `hexagon` — elongated

Two points on the Y axis and four shoulder vertices at
`_HEXAGON_SHOULDER_RATIO` (0.5) of half-length. Regular only when the caller
supplies the matching length/width ratio; regularity is deliberately not forced,
so an elongated hexagon is a first-class configuration.

### `kite` — longitudinally asymmetric

Points at +Y and −Y with the widest span ABOVE the vertical centre, at
`_KITE_SHOULDER_RATIO` (0.25) of half-length. A real `BILATERAL_ONE_AXIS` shape.

Its asymmetry is verified against its **own mirror**, not against another
shape: the centroid is offset from the bounding-box centre along the length
axis, and two symmetric controls (`lozenge`, `hexagon`) must measure zero. That
test shape was chosen after Sprint 18 learned that "X differs from Y" can pass
for the wrong reason.

### `shield` — flat top, pointed base

Fully polygonal: flat top edge, straight flanks to
`_SHIELD_SHOULDER_RATIO` (0.2), a waist at `_SHIELD_WAIST_RATIO` (0.75), and a
point at −Y. No shield subtypes are modelled.

### `half_moon` — half an ellipse

A straight chord at −X closed by an ELLIPTICAL arc bulging to +X, with the
ellipse centred at `(-hw, 0)` and semi-axes `(2·hw, hl)`.

Half of an ellipse rather than half of a circle, because a circular arc through
the two chord endpoints necessarily has a radius larger than the half-length —
so its bounding box always overshoots. The half-ellipse is exact for every
aspect ratio.

### `heart` — exact by construction

Each lobe is a real circular arc whose own extreme points ARE the requested
bounds. With `r = 0.55 · hw` and the lobe circle centred at
`(-(hw - r), hl - r)`, the circle touches `y = hl` at its top and `x = -hw` at
its left. The cleft is where the two lobe circles meet the centre line, at
`y = hl - r + sqrt(r² - a²)` — a consequence of the lobe geometry rather than an
independent tunable, which is what keeps the outline closed and smooth at the
cleft for every aspect ratio.

**This replaced an iterative correction**, and the replacement matters. The
earlier construction placed control points and then corrected the resulting
box with a fixed-point iteration. That iteration converged linearly at roughly
0.34 per step and did **not** reach tolerance for elongated hearts: a 10×6 heart
was still 8e-6mm too wide after forty steps. Solving the geometry exactly
removed both the residual error and the iteration.

### `pearl` — a sphere

The only shape with no outline. Handled by `SPHERICAL_REFERENCE`; see
[`cabochon-and-pearl.md`](cabochon-and-pearl.md).

## What was pre-authorized and turned out unnecessary

Brief section 69 pre-authorized microscopic stabilization for pointed shapes
(heart tip, kite tips, triangle corners, shield, tapered baguette corners).

**None was needed and none was implemented.** Every pointed shape builds a
valid solid, rotates 90° cleanly, and survives a STEP roundtrip with matching
volume. This is pinned by
`test_stone_v2.py::test_pointed_shapes_need_no_stabilization`, so that a future
change making a pointed shape fragile fails loudly rather than being quietly
patched with a hidden distortion.

Sprint 18 recorded the same outcome for marquise and pear. Documented so nobody
"restores" a stabilization that never existed.

## Cross-references

- [`stone-profile-v2.md`](stone-profile-v2.md) — the second axis.
- [`stone-v2-golden-strategy.md`](stone-v2-golden-strategy.md) — regression
  coverage for each shape.
