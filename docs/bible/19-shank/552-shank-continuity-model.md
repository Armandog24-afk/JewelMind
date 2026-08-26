---
id: JM-BIBLE-552
title: Shank Continuity Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
  - JM-BIBLE-551
related_documents:
  - JM-BIBLE-548
implementation_status: current
professional_validation: not_required
normative: true
---

# Shank Continuity Model

## What is actually guaranteed: closure, not smoothness

The tapered loft's continuity guarantee is a real, verifiable geometric fact — closure of the 360-degree loop — and this document deliberately does not claim anything stronger than that. `_build_tapered_shank()` samples wires at `i / SECTION_COUNT` for `i in range(SECTION_COUNT + 1)`, i.e. 49 wires for `SECTION_COUNT = 48`: `u = 0/48, 1/48, ..., 48/48`. Since `u = 48/48 = 1.0` and `taper_ratio(u, taper)` treats `u=1.0` identically to `u=0.0` (both map to `distance_from_head = 0.0`, and `angle_deg_for_u(1.0) = -90 + 360 = 270`, the same physical angle as `angle_deg_for_u(0.0) = -90`), the 49th wire is geometrically identical to the 1st wire — the code comment on this line states it directly: `# +1 closes the loop: wire[N] == wire[0]`.

This is what makes `cq.Solid.makeLoft(wires, ruled=True)` produce one continuous, closed 360-degree solid rather than a solid with a seam or a gap between the last and first sampled sections.

## `ruled=True`

The loft is constructed with `ruled=True`. This document records that fact as it appears in `builder.py` and does not go further to assert what specific interpolation behavior CadQuery's `ruled` loft mode implies internally beyond what was verified by inspecting the actual generated solids (via the Golden Suite comparisons in [`555-shank-golden-strategy.md`](555-shank-golden-strategy.md) and the geometric facts in [`553-shank-inspection-contract.md`](553-shank-inspection-contract.md)) — no CadQuery/OpenCascade internal loft algorithm detail is asserted here that was not directly observed.

## What "continuity" does not mean here

This is a **closure guarantee** (the loop connects back on itself with no gap and no duplicated seam geometry), not a **curvature-continuity claim**. Specifically, this document makes no claim that the tapered shank's surface is G1-continuous (matching tangent direction across each section boundary) or G2-continuous (matching curvature) at the 48 internal section boundaries between consecutive sampled `u` values. Whether the loft produces a visually or mathematically smooth surface between sections, versus a faceted one with subtle direction changes at each of the 48 section boundaries, was not measured or verified during this Sprint, and no claim about it should be inferred from the fact that `SECTION_COUNT = 48` was tuned for volume convergence (see [`551-shank-generation-pipeline.md`](551-shank-generation-pipeline.md)) — that tuning measured volume only, not surface smoothness.

## Why closure, not smoothness, is the guarantee that matters here

Closure is the property that determines whether `build_shank()` produces a single valid, manufacturable-shaped solid at all: `_build_tapered_shank()`'s own failure check (`not solid.Solids() or not solid.isValid()`) would catch a loft that failed to close the loop, since an unclosed loft does not produce a valid solid body. Curvature continuity, by contrast, is not something the current failure check or the Golden Suite's regression comparison evaluates — [`17-geometry-quality/README.md`](../17-geometry-quality/README.md) describes Golden comparison as comparing geometric facts (volume, bounding box, component relationships) against a versioned baseline, not a curvature analysis. A future geometric-fact type for local surface smoothness, if ever added, would be a real extension to Geometry Inspection's `FactType` enum (see [`553-shank-inspection-contract.md`](553-shank-inspection-contract.md)) and its own RFC, not an implicit property of the current loft.

## What Inspection can and cannot confirm about closure

`geometry/inspection/`'s generic component checks give an indirect, partial confirmation of closure: `SHAPE_VALID` (`Shape.isValid()`) on the `band` component would fail for a genuinely unclosed or self-intersecting loft, and `SOLID_COUNT` confirms exactly one solid resulted rather than a degenerate multi-shell result. Neither check, nor any other current `FactType`, specifically measures "does wire 49 coincide with wire 1" as its own fact — closure is confirmed only as a side effect of the resulting solid passing kernel validity, not through a dedicated geometric-closure measurement. See [`553-shank-inspection-contract.md`](553-shank-inspection-contract.md) for the fuller account of what Inspection does and does not check for Shank specifically.

## Relationship to the uniform path

`_build_uniform_shank()`'s `revolve()` construction has a different, and in one sense stronger, continuity property: a true surface of revolution around a fixed axis is smooth by construction at every angular position, not merely at 48 sampled boundaries. This is an inherent property of `revolve()`, not something this Sprint added or verified independently — it is unchanged from before Sprint 17. The tapered path's weaker, sampled-and-lofted construction is the direct consequence of needing the cross-section itself to vary by angular position, which a single `revolve()` call cannot express; see [`551-shank-generation-pipeline.md`](551-shank-generation-pipeline.md) for why loft was chosen over other approaches for this reason.

## Why this document exists separately from the generation pipeline

[`551-shank-generation-pipeline.md`](551-shank-generation-pipeline.md) documents *how* the loft is built — dispatch, sampling, `SECTION_COUNT`, and the failure path. This document exists separately to answer a narrower, easily over-claimed question on its own: what does the resulting solid actually guarantee about continuity, and what does it not. Keeping the two questions in separate documents is deliberate, so a future reader asking "is this shank surface smooth" is pointed at an answer that states the closure guarantee precisely rather than inheriting an implicit, unstated assumption from a document primarily about construction mechanics.

## Summary statement

Closure at the seam: verified by construction (`wire[48] == wire[0]`) and consistent with the loft producing a valid solid. Smoothness across the 48 internal section boundaries: not measured, not claimed. Any future document, code comment, or user-facing description that states or implies curvature continuity for the tapered shank should be corrected against this document rather than treated as an independent, newer finding.

## Where a stronger continuity claim could come from

If a future Sprint wanted to make a real G1/G2 continuity claim, the honest path would be a dedicated measurement — sampling surface tangents/curvature across a representative set of section boundaries and comparing them within a stated numeric tolerance, published the same way `SECTION_COUNT`'s volume-convergence table was — not an assumption based on `ruled=True` loft mode or on the fact that `SECTION_COUNT` was tuned for volume. No such measurement exists today.
