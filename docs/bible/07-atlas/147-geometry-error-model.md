---
id: JM-BIBLE-147
title: Geometry Error Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-132
related_documents:
  - JM-BIBLE-080
implementation_status: partial
professional_validation: not_required
normative: true
---

# Geometry Error Model

The normative shape is `specs/atlas/v1/geometry-error.schema.json`. **None of the nine conceptual `ATLAS_*` codes exist as literal strings in current code** — they are a classification lens over the real `AppError` codes, introduced here without renaming or breaking any of them (per the same discipline established in [`05-jdl/080-errors-warnings-and-diagnostics.md`](../05-jdl/080-errors-warnings-and-diagnostics.md)).

## Conceptual codes, mapped to real current codes

| Conceptual code | Meaning | Real current mapping |
|---|---|---|
| `ATLAS_INPUT_ERROR` | The input definition cannot be turned into a geometry plan | `REQUEST_VALIDATION_ERROR` (structural) or `VALIDATION_BLOCKED` (semantic) — both occur upstream of Atlas ever running |
| `ATLAS_CONSTRUCTION_ERROR` | A primitive/profile/component construction call raised | `MODEL_GENERATION_FAILED` (500) — the generic catch-all for an unexpected exception during `build_solitaire_ring()` |
| `ATLAS_BOOLEAN_ERROR` | A boolean operation failed | **Not surfaced as a distinct error today** — `_fuse_metal()` catches this internally and falls back; it never becomes an `AppError` at all unless the fallback itself somehow also fails (unobserved) |
| `ATLAS_TOPOLOGY_ERROR` | A topology validity check failed | **No such check exists**, so no error can currently originate here — see [`128-brep-and-topology-model.md`](128-brep-and-topology-model.md) |
| `ATLAS_INSPECTION_ERROR` | An inspection pass itself failed to run | **No inspection pass exists to fail** beyond the one inline fuse check |
| `ATLAS_TESSELLATION_ERROR` | Tessellation/export meshing failed | Would surface as `STEP_EXPORT_FAILED` or `STL_EXPORT_FAILED` (500) |
| `ATLAS_COMPONENT_MISSING` | A required component could not be produced at all | **Never observed** — every builder always returns a `GeneratedComponent`, even an empty one (see [`127-surface-and-solid-model.md`](127-surface-and-solid-model.md)); this code has no current trigger |
| `ATLAS_FALLBACK_USED` | A documented fallback was taken | Not a distinct error code today — surfaced only as a `warning`-severity entry in `GeneratedModel.warnings`/`GeneratedComponent.warnings`, never as an `AppError` (fallback is success, not failure) |
| `ATLAS_KERNEL_ERROR` | The CAD kernel itself is unavailable | `CAD_ENGINE_UNAVAILABLE` (503) — `services/cad_engine.py::probe_cad_engine()` |

## Conceptual error fields, mapped

`errorCode` → see table above; `stage` → `ATLAS-0`..`ATLAS-11` per [`132-construction-pipeline.md`](132-construction-pipeline.md); `component`/`operation` → not currently captured on the real `AppError` (the exception message text may mention them, but no structured field does); `message`/`technicalCause` → `AppError.message`; `fallbackAvailable` → not a field on the real error (fallback either already happened, transparently, or didn't apply); `blocking` → derivable from `AppError.status_code`; `requestId` → `ErrorDetail.requestId`; `definitionHash` → not currently included in the error envelope (a real, minor current gap — an error response cannot currently be correlated to a specific `definitionHash` without cross-referencing server logs).

## No breaking change

This document introduces no new literal error code and does not rename `MODEL_GENERATION_FAILED`, `STEP_EXPORT_FAILED`, `STL_EXPORT_FAILED`, or `CAD_ENGINE_UNAVAILABLE` — see [`jdl-error-code-catalog.md`](../appendices/jdl-error-code-catalog.md) (Sprint 3's catalog, still authoritative for these codes) for the complete, unmodified current list.
