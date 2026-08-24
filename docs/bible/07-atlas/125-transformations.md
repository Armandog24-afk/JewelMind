---
id: JM-BIBLE-125
title: Transformations
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

# Transformations

## Definitions and current usage

| Transformation | Definition | Current usage |
|---|---|---|
| Translation | Moving a shape by an offset | `.workplane(offset=z)` (Z-axis offset only) and `.center(x, y)` (in-plane offset) — used by every component builder to place itself along the assembly anchor axis |
| Rotation | Turning a shape around an axis | `.revolve(360, axis_start, axis_end)` for the band (a continuous 360° sweep, not a discrete rotation of an existing solid); prong positions are computed via `math.cos`/`math.sin` at construction time, not by rotating one prong solid N times |
| Scaling | Uniformly or non-uniformly resizing a shape | **Never used anywhere in the current codebase** |
| Mirror | Reflecting a shape across a plane | **Never used anywhere in the current codebase** |
| Placement | Positioning a shape in world space | Implicit — every builder computes its absolute position directly (via `geometry/constants.py` functions) rather than applying a placement transform to a shape built at a local origin |
| Local-to-world transform | A single matrix mapping a component's local frame to world space | **Not materialized as an object anywhere** — see `transform: null` in `specs/atlas/v1/geometry-component.schema.json`'s examples |
| Component transform | A per-component placement record | **PLANNED, not implemented** — see [`130-component-contract.md`](130-component-contract.md)'s `transform` field |

## Why uniform scaling is not implemented, and must not be treated as equivalent to regeneration

**No component is ever built by scaling an existing solid.** Every dimension change (a different `band.width`, a different `stone.diameter`) is handled by re-deriving geometry from the new JDL parameter values — a fresh construction call, never a `scale()` operation applied to a previously-built shape.

This is a deliberate distinction, not an oversight: several of this codebase's geometric features are **fixed millimeter constants**, not proportions of the overall size —

- `_COMFORT_FLARE_MM = 0.3` (the comfort-fit inner-edge flare amount, `band.py`)
- `_FILLET_MAX_MM = 0.25` (the outer-rim fillet radius cap, `band.py`)
- `EMBED_MM = 0.4` (the cross-component embedding depth, `geometry/constants.py`)
- `_MIN_INNER_RADIUS_MM = 0.2` (the basket's minimum inner-radius floor, `basket.py`)
- `_CULET_RADIUS_MM = 0.05` (the stone reference's culet point radius, `stone.py`)

If a ring were uniformly scaled by, say, 150% instead of regenerated from a 150%-larger `band.width`/`stone.diameter`/etc., every one of these fixed constants would scale too — producing a comfort-fit flare, fillet, embed depth, and culet radius that no longer match this codebase's intended fixed millimeter values. **Scaling and parameter-driven regeneration are not interchangeable operations for JewelMind geometry**, and the current implementation correctly never conflates them by never implementing scaling at all.

## Current usage summary

Only translation (via workplane Z-offsets and in-plane `.center()` calls) and one specific rotation form (a 360° revolve for the band; positional trigonometry, not a rotation operator, for prongs) are used. Scaling, mirroring, and a generalized local-to-world transform object are all absent from the current implementation.
