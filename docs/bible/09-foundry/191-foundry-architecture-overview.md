---
id: JM-BIBLE-191
title: Foundry Architecture Overview
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-190
  - JM-BIBLE-020
related_documents:
  - JM-BIBLE-162
implementation_status: partial
professional_validation: not_required
normative: true
---

# Foundry Architecture Overview

## The five-layer stack, with Foundry named

| Layer | Owns | Sprint |
|---|---|---|
| JDL | Declarative design definition | 3 |
| Forge | Rule evaluation and eligibility | 4 |
| Alchemist | Orchestration and compilation planning | 6 |
| Atlas | Geometry construction and geometric facts | 5 |
| **Foundry** | **Artifact generation and file-level integrity validation** | **7 (this document)** |
| Vision | Preview/presentation rendering | not yet formalized (Sprint 8) |

Foundry sits after Atlas and reads its output (`GeneratedModel`) and after Forge (via Alchemist) to know whether generation was eligible at all. It does not sit "inside" Alchemist as a stage name only — today it is a real, separately callable set of functions (`export_step`, `export_stl`, `export_json`, `build_specification`) invoked directly by `api/routes.py` and `services/model_service.py`, not through an intermediate `GeometryPlan`/`CompilationResult` object (those remain PLANNED per Sprint 6).

## Conceptual flow

```mermaid
flowchart LR
    A[CompilationResult] --> B[ArtifactRequest]
    B --> C[Export Eligibility]
    C --> D[Component Selection]
    D --> E[Artifact Builder]
    E --> F[File Generation]
    F --> G[Integrity Validation]
    G --> H[Artifact Record]
    H --> I[Artifact Manifest]
```

Every box in this diagram names a concept this Sprint formalizes. Only some are backed by a distinct real function today:

| Conceptual stage | Real code today |
|---|---|
| `CompilationResult` | Not materialized (Sprint 6 finding) — `ModelService` holds the cached `GeneratedModel` directly. |
| `ArtifactRequest` | Not a distinct object — an HTTP request to one of 4 separate export/spec endpoints. |
| Export Eligibility | Implicit: `get_record(model_id)` raising `MODEL_NOT_FOUND` is the only current eligibility check. |
| Component Selection | Real — `exporters/selection.py::select_export_shapes()` (extracted this Sprint from duplicated code). |
| Artifact Builder | Real — `export_step()`, `export_stl()`, `export_json()`, `build_specification()`. |
| File Generation | Real — CadQuery/OpenCascade for STEP/STL; `json.dumps()` for JSON; string building for the specification. |
| Integrity Validation | Partial — `validate_non_empty()` and `sha256_checksum()` (new this Sprint) run for every real STEP/STL export; deeper checks (re-import, format-signature parse) exist only in the test suite. |
| Artifact Record | Not materialized — the HTTP response (`FileResponse` + headers) carries only filename, media type, and (new this Sprint) an `X-Content-SHA256` header, not a structured record object. |
| Artifact Manifest | Not materialized — each artifact type is requested and evaluated independently by the caller; see [`205-export-failure-and-partial-success.md`](205-export-failure-and-partial-success.md). |

## Where Foundry code actually lives

`backend/jewelmind/exporters/` (`step_exporter.py`, `stl_exporter.py`, `json_exporter.py`, `specification.py`, `filenames.py`, `selection.py`, `integrity.py`) plus the export-specific methods on `services/model_service.py` (`export_step_file`, `export_stl_file`) and the export routes in `api/routes.py`. See [`217-current-exporter-code-mapping.md`](217-current-exporter-code-mapping.md) for a line-by-line classification of which parts of this code are genuinely Foundry-owned versus mixed with Alchemist/Atlas/API responsibilities.

## What Foundry explicitly does not own

- Jewelry-domain thresholds (Forge).
- Geometry construction, fillets, fuses, tessellation parameters as design choices (Atlas — Foundry only *selects* already-built shapes and *passes through* already-defined tolerances).
- Compilation orchestration, caching, `definitionHash`/`compilationHash` (Alchemist).
- Visual rendering, cameras, materials, image output (Vision, Sprint 8).
