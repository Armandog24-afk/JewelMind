---
id: JM-BIBLE-142
title: Volume and Bounding Box Inspection
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-140
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Volume and Bounding Box Inspection

## What is measured

| Measurement | Source | Real value (default definition) |
|---|---|---|
| Component volume | `.Volume()` per `GeneratedComponent` | `band: 250.99...`, `stone_reference: 58.22...`, `prongs: 29.65...`, `basket_support: 83.16...` mm³ |
| Assembly (production-metal) volume | `combined_metal.Volume()` | `341.44334316909976` mm³ |
| Component bounding box | `BoundingBox.from_shape()` per component | See `specs/atlas/v1/test-vectors/metadata-vectors.json` |
| Assembly bounding box | Union of `combined_metal`'s bbox and `stone_reference`'s bbox | `x:[-10.7,10.7] y:[-3.635,3.635] z:[-10.7,15.6]` |

## Production-metal volume is not a component-volume sum

See [`139-geometry-metadata-model.md`](139-geometry-metadata-model.md) for the full worked example: `341.44334316909976` mm³ (fused) vs. `363.7977930667917` mm³ (sum of the three pre-fuse components) — a `22.35444989769195` mm³ difference from the `EMBED_MM`-deep overlap regions consumed by the union.

## What plausible-dimension tests actually check

`test_geometry.py::test_band_bounding_box_is_plausible` checks `abs(bb.xmax - outer_r) < 0.05` and `abs(bb.zmax - outer_r) < 0.05` — a **tolerance-based geometric comparison**, not an exact floating-point equality, appropriately per this Sprint's guidance to prefer tolerances over fragile exact comparisons. `test_solitaire_assembly_bounding_box_plausible` only checks that each axis span is positive (`bb.zmax > bb.zmin`, etc.) — a much weaker "not degenerate" check, not a check against any expected dimension.

## Explicit limitations

**Positive volume does not prove manufacturability.** A component can have a perfectly positive, plausible volume and still be geometrically nonsensical in ways volume alone cannot detect (self-intersecting, disconnected internally in a way that still integrates to a positive net volume via OCCT's volume formula, etc. — see [`128-brep-and-topology-model.md`](128-brep-and-topology-model.md)).

**A plausible bounding box does not prove correct construction.** A bounding box only bounds the shape's extent — it says nothing about the shape's interior topology, connectivity, or correctness. Two very different (one correct, one badly malformed) solids could share an identical bounding box.

## Current test coverage, summarized

Every one of the four components and the assembly has at least one volume and/or bounding-box test in `test_geometry.py` — see [`atlas-inspection-catalog.md`](../appendices/atlas-inspection-catalog.md) for the complete component-by-component mapping. No component currently lacks basic volume/bbox test coverage.

## Sprint 14: volume and bounding-box checks are now also runtime

`jewelmind.geometry.inspection.inspect_component()` (Sprint 14) now performs the SAME finiteness/non-negativity volume check and the same real `BoundingBox.from_shape()` computation as the test suite above, but on every real `ModelService.generate()` call, not only in `test_geometry.py` — see [`16-geometry-inspection/468-volume-inspection.md`](../16-geometry-inspection/468-volume-inspection.md) and [`469-bounding-box-inspection.md`](../16-geometry-inspection/469-bounding-box-inspection.md). This does not change either explicit limitation stated above: a runtime-checked positive volume and a runtime-checked bounding box still do not prove manufacturability or correct construction — Sprint 14 makes the same weak, honest checks real-time, it does not make them stronger checks.
