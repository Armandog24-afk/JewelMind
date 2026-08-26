---
id: JM-BIBLE-A97
title: "Appendix: Inspection Code Mapping"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-461
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Inspection Code Mapping

A file-by-file map, mirroring `docs/bible/13-design-intent/361-current-code-mapping.md`'s structure. All line counts are real (`wc -l`).

## Backend: `backend/jewelmind/geometry/inspection/`

| File | Lines | Responsibility |
|---|---|---|
| `__init__.py` | 16 | Exports `inspect_model` only. |
| `models.py` | 227 | Every Pydantic model and enum. |
| `version.py` | 23 | `INSPECTION_VERSION`, `CONTACT_TOLERANCE_MM`. |
| `diagnostics.py` | 35 | The 11 diagnostic code constants. |
| `shape.py` | 63 | `solid_count()`, `shape_is_valid()`, `topology_counts()`, bounding-box helpers. |
| `distance.py` | 37 | `inspect_distance()`. |
| `intersection.py` | 82 | `inspect_intersection()`, `should_skip_intersection()`. |
| `topology.py` | 36 | `inspect_topology()`. |
| `components.py` | 94 | `inspect_component()`. |
| `connectivity.py` | 98 | `pairwise_distances()`, `build_connectivity_graph()`. |
| `assembly.py` | 205 | `inspect_assembly()`. |
| `inspector.py` | 252 | `inspect_model()` — the top-level entry point. |

**Total: 1,168 lines** across 12 files — deliberately not one giant inspector function.

## Backend: shared/modified files

| File | Change this Sprint |
|---|---|
| `geometry/roles.py` | New (42 lines) — `GEOMETRY_ROLE`/`PRODUCTION_ROLE` extracted from a private mapping that used to live only in `preview/mesh.py`, fixing a "geometry facts calculated separately in multiple places" duplication. |
| `preview/mesh.py` | Now imports `GEOMETRY_ROLE`/`PRODUCTION_ROLE` from `geometry/roles.py` instead of defining its own copy. |
| `services/model_service.py` | `ModelRecord.inspection_report` (new required field); `generate()` calls `inspect_model()` unconditionally; new `inspection_report(model_id)` accessor. |
| `api/schemas.py` | `ModelMetadataResponse.inspection: dict[str, Any]` (new required field). |
| `api/routes.py` | New `_inspection_summary()` helper; `GenerateResponse.metadata["inspection"]`; new `GET /api/models/{model_id}/inspection` route. |
| `exporters/specification.py` | `build_specification()` gained an optional `inspection_report` parameter, appending a "Geometry inspection summary" Markdown section. |
| `professional_validation/review_package.py` | Review packages now include `geometry-inspection.json` (the full real report). |

## Backend tests

| File | Tests | Layer |
|---|---|---|
| `backend/tests/test_geometry_inspection.py` | 34 | Unit/integration — component/assembly/connectivity/intersection/distance/determinism/regression/fallback/review-package-file. |
| `backend/tests/test_geometry_inspection_schemas.py` | 6 | Schema — validates `specs/geometry-inspection/v2/` against the real engine's output. |

## Frontend

| File | Change |
|---|---|
| `frontend/src/api/types.ts` | New `InspectionSummary`, `BoundingBoxFact`, `ComponentInspectionResult`, `DistanceResult`, `IntersectionResult`, `ConnectivityGraph`, `AssemblyInspectionResult`, `GeometryInspectionReport` types; `ModelMetadataResponse`/`GenerateResponse.metadata` gained a required `inspection` field. |
| `frontend/src/api/client.ts` | New `fetchInspectionReport(modelId)`. |

**No frontend component currently calls `fetchInspectionReport()`** — the API contract is real and complete; UI consumption is a documented, deliberate gap (see [`490-vision-inspection-integration.md`](../16-geometry-inspection/490-vision-inspection-integration.md)).

## Machine-readable specification: `specs/geometry-inspection/v2/`

| Path | Contents |
|---|---|
| `README.md` | Explains the schema set and the generation/validation discipline. |
| 9 `*.schema.json` files | `geometric-fact`, `component-inspection`, `assembly-inspection`, `connectivity-result`, `intersection-result`, `distance-result`, `inspection-report`, `inspection-diagnostic`, `inspection-version`. |
| `fact-registry.json` | 16 hand-authored fact-type definitions. |
| `examples/` (5 files) | Real generated inspection reports/excerpts. |
| `test-vectors/` (8 files) | Real generated vectors for presence, solid count, connectivity, intersection, distance, stone separation, determinism, and regression. |
