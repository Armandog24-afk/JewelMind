---
id: JM-BIBLE-469
title: Bounding Box Inspection
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-464
  - JM-BIBLE-123
  - JM-BIBLE-142
implementation_status: current
professional_validation: not_required
normative: true
---

# Bounding Box Inspection

## `BoundingBoxFact` fields

`models.py::BoundingBoxFact`: `xmin`, `ymin`, `zmin`, `xmax`, `ymax`, `zmax` (the raw axis-aligned extent, in mm), plus three derived pairs computed once at construction — `sizeX`/`sizeY`/`sizeZ` (`max - min` per axis) and `centerX`/`centerY`/`centerZ` (`(min + max) / 2` per axis).

## The two constructors

`shape.py::bounding_box_fact(shape: cq.Shape) -> BoundingBoxFact` calls `BoundingBox.from_shape(shape)` (`geometry/model.py`, itself a thin wrapper around `shape.BoundingBox()`) and passes the result to `bounding_box_fact_from_box()`. `shape.py::bounding_box_fact_from_box(bbox: BoundingBox) -> BoundingBoxFact` builds the `BoundingBoxFact` from an already-computed `BoundingBox` — used for the assembly-level bounding box (`model.bounding_box`, a union of `combined_metal`'s box and `stone_reference`'s box computed once at generation time in `solitaire.py`), so `assembly.py::inspect_assembly()` never needs to re-query the kernel for a fresh shape-level box when a correct one already exists on the `GeneratedModel`.

## Coordinate convention it inherits

Bounding-box inspection does not define its own coordinate convention — it reports whatever `BoundingBox.from_shape()` returns, which is governed entirely by [`07-atlas/123-coordinate-system-and-orientation.md`](../07-atlas/123-coordinate-system-and-orientation.md) (the Bible-level formalization of `docs/geometry-conventions.md` and `geometry/constants.py`): the world origin is the ring's center/finger-hole center, the band revolves around the global Y axis, the band lies in the X/Z plane, and the ring's "top" is `(x=0, z=+outer_radius)`. For the default definition, that document records the real values `inner_radius = 8.9`, `outer_radius = 10.700000000000001`, `band_top_z = 10.700000000000001`. This document does not re-derive those numbers — it defers to 123 as authoritative and only states that `BoundingBoxFact`'s six min/max fields are expressed in exactly that coordinate frame.

## What bounding-box inspection is used for

Diagnostics and debugging (a component whose bounding box collapsed to zero extent, or whose center moved unexpectedly between two generations of nominally similar geometry, is a useful signal something changed); regression detection (`backend/tests/test_geometry_inspection.py::TestComponentBoundingBox` asserts every real component's box has non-negative size on every axis); a shared geometric-origin check between Vision's preview mesh and Foundry's export geometry (both derive from the same underlying `cq.Shape`, so their bounding boxes should agree — see [`10-vision/223-atlas-to-vision-contract.md`](../10-vision/223-atlas-to-vision-contract.md) for that contract, unrelated to but consistent with this fact).

## What it is explicitly never used for

A bounding box is never treated as evidence of "correct proportions." `07-atlas/142-volume-and-bounding-box-inspection.md` already states this limitation plainly and it applies without modification to this Sprint's runtime version of the same check: "a plausible bounding box does not prove correct construction... two very different (one correct, one badly malformed) solids could share an identical bounding box." No code path in `backend/jewelmind/geometry/inspection/` compares a `BoundingBoxFact`'s dimensions against any expected range, ratio, or professional proportion guideline — that would be exactly the kind of jewelry-domain judgment INSPECT-GOV-001/002 reserves for Forge, and no Forge rule currently reads a `BOUNDING_BOX` fact at all (see [`487-forge-fact-contract.md`](487-forge-fact-contract.md)).

## Cross-references

[`464-component-inspection-contract.md`](464-component-inspection-contract.md) for how `boundingBox` fits into the full per-component result, including its failure path (`INSPECTION_BOUNDING_BOX_FAILED` on a kernel exception); [`07-atlas/142-volume-and-bounding-box-inspection.md`](../07-atlas/142-volume-and-bounding-box-inspection.md) for the Sprint 5 test-time-only version of this same measurement and its explicit limitations, now made real and runtime by this Sprint. `backend/tests/test_geometry_inspection.py::TestComponentBoundingBox` exercises this directly.
