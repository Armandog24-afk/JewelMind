---
id: JM-BIBLE-132
title: Construction Pipeline (ATLAS-0..ATLAS-11)
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-121
related_documents:
  - JM-BIBLE-096
  - JM-BIBLE-168
implementation_status: partial
professional_validation: not_required
normative: true
---

# Construction Pipeline (ATLAS-0..ATLAS-11)

**Relationship to Alchemist (Sprint 6):** [`08-alchemist/168-atlas-execution-contract.md`](../08-alchemist/168-atlas-execution-contract.md)
defines the conceptual `execute_geometry_plan(plan) -> AtlasExecutionResult`
interface Alchemist would call to trigger this pipeline, and confirms
the current real call (`build_solitaire_ring(definition)`) takes the
definition directly rather than a `GeometryPlan`, since none exists.

| Stage | Inputs | Outputs | Possible failures | Current status | Related code |
|---|---|---|---|---|---|
| **ATLAS-0** Receive validated geometry plan | A `JewelryDefinition` that already passed FORGE-0..FORGE-5 | The same definition, ready for geometry | n/a — this stage cannot fail; the gate already happened upstream | CURRENT (as "receive the definition", not a materialized plan object) | `services/model_service.py::generate()` calling `build_solitaire_ring(definition)` |
| **ATLAS-1** Resolve coordinate frame | The definition | The fixed global convention (Y = finger axis, assembly anchor axis) | n/a — the convention is fixed, not computed per-request | CURRENT (implicit — no per-request frame resolution occurs; the frame is a compile-time constant of the code) | `geometry/constants.py` |
| **ATLAS-2** Calculate derived geometric parameters | The definition | `inner_radius`, `outer_radius`, `band_top_z`, `prong_center_radius`, `EMBED_MM` | n/a — pure arithmetic, cannot fail for any finite input | CURRENT | `geometry/constants.py` |
| **ATLAS-3** Build primitives and profiles | Derived parameters | 2D wires (band profiles), circles (stone cross-sections, prong/basket circles) | A profile could in principle be degenerate for an extreme parameter combination (not currently guarded against — see [`128-brep-and-topology-model.md`](128-brep-and-topology-model.md)) | CURRENT | `band.py::_build_flat_wire`/`_build_comfort_fit_wire`, `stone.py`, `prongs.py`, `basket.py` |
| **ATLAS-4** Construct components | Primitives/profiles | Four `GeneratedComponent` solids/compounds | `.revolve()`/`.loft()`/`.extrude()`/`.cut()` could raise for a degenerate input (not currently caught for these operations — only the fillet and fuse are wrapped) | CURRENT | `geometry/components/*.py` |
| **ATLAS-5** Apply transformations | Component solids | Positioned component solids | n/a — placement is baked into construction via workplane offsets, not a separate transform-application step | CURRENT (folded into ATLAS-4; no separate stage exists) | Same files |
| **ATLAS-6** Perform required booleans | `band`, `prongs`, `basket_support` solids | `combined_metal` (fused solid or compound) | Fuse can fail or yield zero solids — **caught, with a documented fallback** | CURRENT | `solitaire.py::_fuse_metal` |
| **ATLAS-7** Assemble components | `combined_metal` + `stone_reference` | `GeneratedModel` | n/a — pure aggregation | CURRENT | `solitaire.py::build_solitaire_ring` |
| **ATLAS-8** Inspect component geometry | Each `GeneratedComponent` | Per-component facts (volume, bounding box) | n/a — these are computed, not separately validated, at this stage | PARTIAL — computed as a byproduct of construction (`.Volume()`, `BoundingBox.from_shape()`), not as a distinct inspection pass; no pass/fail verdict is produced here | `geometry/model.py` |
| **ATLAS-9** Inspect assembly | `GeneratedModel` | Aggregate bounding box, total volume, the one runtime solid-count check | The fuse-solid-count check (`FORGE-GEOM-001`) is the only genuine inspection-with-fallback at this stage | CURRENT for the one check; PARTIAL overall | `solitaire.py::_fuse_metal`, `geometry/model.py::BoundingBox.union` |
| **ATLAS-10** Generate metadata | `GeneratedModel` | `definitionHash`, `generatorVersion`, `generationDurationS`, warnings | n/a | CURRENT | `solitaire.py::build_solitaire_ring` (timing via `time.perf_counter()`, hash via `utils/hashing.py`) |
| **ATLAS-11** Return structured geometry result | Metadata + `GeneratedModel` | The value returned to `ModelService.generate()` | n/a | CURRENT | `services/model_service.py::generate()` |

## Reading this table correctly

ATLAS-4 and ATLAS-5 are listed as separate conceptual stages (construction, then transformation) because a fully general geometry core would need to distinguish "build this shape" from "place this shape" — but the **current implementation does both in one step**: every builder computes its absolute position (via `geometry/constants.py`) before or during construction (workplane offsets), never as a separate post-construction transform application. This mirrors the same honest "conceptual stages, one code path" pattern already used in [`05-jdl/063-jdl-processing-model.md`](../05-jdl/063-jdl-processing-model.md) and [`06-forge/096-rule-evaluation-pipeline.md`](../06-forge/096-rule-evaluation-pipeline.md).

Similarly, ATLAS-8 (component inspection) is not a separate pass with its own pass/fail verdicts today — volumes and bounding boxes are computed as a natural byproduct of construction, not checked against any expectation at construction time. Real checking of these values happens only in `backend/tests/test_geometry.py`, not at ATLAS-8 itself — see [`140-geometry-inspection-framework.md`](140-geometry-inspection-framework.md).
