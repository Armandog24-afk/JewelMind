---
id: JM-BIBLE-608
title: "Custom Outline Validation"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-607
related_documents:
  - JM-BIBLE-600
implementation_status: current
professional_validation: not_required
normative: true
---

# Custom Outline Validation

`backend/jewelmind/stone/outline_validation.py`.

## Two responsibilities, kept apart

**Validate** — reject a materially malformed outline. Nothing here repairs
geometry (brief section 24).

**Normalize** — apply the small set of well-defined, RECORDED transformations
that put a valid outline into the canonical frame.

The distinction is precise: **normalization changes coordinates, never shape.**
Anything that would change the shape is a validation failure instead. That is
what makes normalization safe to apply silently-but-recorded, and repair
unacceptable at any volume.

## What is rejected

In order, with the real error code:

| Check | Error code |
|---|---|
| More than `MAX_OUTLINE_POINTS` (10,000) | `CUSTOM_OUTLINE_INVALID` |
| A non-finite coordinate (NaN, ±inf) | `CUSTOM_OUTLINE_INVALID` |
| A coordinate beyond ±10,000mm after unit conversion | `CUSTOM_OUTLINE_INVALID` |
| The first point repeated at the end | `CUSTOM_OUTLINE_INVALID` |
| A degenerate segment (endpoints within 1e-9mm) | `CUSTOM_OUTLINE_INVALID` |
| Fewer than 3 distinct points | `CUSTOM_OUTLINE_INVALID` |
| Zero enclosed area (below 1e-9 mm²) | `CUSTOM_OUTLINE_INVALID` |
| Segments that properly cross | `CUSTOM_OUTLINE_SELF_INTERSECTION` |
| A vertex lying ON a non-adjacent edge | `CUSTOM_OUTLINE_SELF_INTERSECTION` |

## The self-intersection test, and why there are two of them

### Proper crossing

`_segments_properly_intersect` uses exact **orientation signs** rather than
computing an intersection point, which avoids the division-by-near-zero
instability a point-based test has on nearly-parallel segments. Adjacent
segments (which legally share an endpoint) are excluded by the caller.

### Boundary touching — the check that was missing

A proper-crossing test alone does **not** prove an outline is a simple closed
curve.

Found during Sprint 20 validation with a Z-shaped outline
`[(-3,3), (3,3), (-3,-1), (3,-3), (-3,-3)]`. It has a real enclosed area
(−18 mm²), no degenerate segments, no duplicated point — and no *proper*
crossing, because a vertex merely **touches** a distant edge, producing no
strict orientation-sign change. It passed every check while not being a simple
polygon, and offsetting it (which is exactly what a bezel does) is ambiguous.

`_find_vertex_touching_edge` closes that. It measures the distance from each
vertex to each non-incident segment (to the segment, not the infinite line, so
a vertex beyond an endpoint does not count) and rejects a touch within 1e-9mm.

### The test that would have passed for the wrong reason

The obvious self-intersection fixture is a symmetric bow-tie. It has **zero
signed area**, so it is caught by the area check and the crossing detector never
fires.

The regression test therefore uses a crossed pentagon with a real area
(−19.5 mm²), so `CUSTOM_OUTLINE_SELF_INTERSECTION` is genuinely what raises.
Four valid controls — convex, concave, square, and a 64-point sampled ellipse —
must all pass, so the detector cannot succeed by rejecting everything.

This is the Sprint 18 lesson applied: when testing "X is detected", find the
input where **only** that check can fire.

## Complexity

`_find_self_intersection` and `_find_vertex_touching_edge` are both O(n²),
deliberately. `MAX_OUTLINE_POINTS` bounds the work, and a sweep-line
implementation would add real complexity for input sizes that never occur in
practice. If a future sprint raises that bound materially, these are the two
functions to revisit.

## What normalization does

| Operation | Recorded as |
|---|---|
| Unit conversion | `UNIT_CONVERSION:cm->mm` |
| Winding reversal | `WINDING_REVERSED:CW->CCW` |
| Origin recentring | `ORIGIN_RECENTERED:bbox_center(x,y)` |

Every operation actually applied is appended to
`StoneSourceProvenance.normalizationOperations`. An operation not applied is not
recorded — and an operation recorded but not applied is a defect, which is
exactly the bug Sprint 20 shipped briefly for mesh unit conversion
(STONEV2-GOV-015).

**Canonical winding is counter-clockwise** (positive signed area), matching what
CadQuery's own `polyline().close()` produces for the native primitives. A
consistent winding is what lets a bezel offset outward rather than inward
without inspecting each outline.

## Tolerances

| Constant | Value | What it is |
|---|---|---|
| `DEGENERATE_SEGMENT_MM` | 1e-9 | Kernel numerical robustness |
| `MIN_OUTLINE_AREA_MM2` | 1e-9 | Kernel numerical robustness |
| `MAX_COORDINATE_MM` | 10,000 | Untrusted-input safeguard |
| `MAX_OUTLINE_POINTS` | 10,000 | Untrusted-input safeguard |

**None is a manufacturing or jewelry tolerance.** The first two are the
threshold below which the CAD kernel cannot distinguish two points; the last two
are resource safeguards. A legitimate hand-authored or vector-imported stone
outline is orders of magnitude below both limits.

## Cross-references

- [`custom-outline-contract.md`](custom-outline-contract.md)
- [`../16-geometry-inspection/460-inspection-governance.md`](../16-geometry-inspection/460-inspection-governance.md)
  — INSPECT-GOV-012, on never inventing a tolerance.
