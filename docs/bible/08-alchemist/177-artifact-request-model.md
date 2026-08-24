---
id: JM-BIBLE-177
title: Artifact Request Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-176
related_documents:
  - JM-BIBLE-A29
implementation_status: partial
professional_validation: not_required
normative: true
---

# Artifact Request Model

The normative shape is `specs/alchemist/v1/artifact-request.schema.json`; two real examples (`partial-preview-request.json`, `step-export-request.json`) are in `specs/alchemist/v1/examples/`.

## Supported current artifact types

`PREVIEW_MESH`, `STEP`, `STL`, `JSON`, `TECHNICAL_SPECIFICATION` — matching exactly the five real endpoints in `api/routes.py` (`/api/models/{id}/preview/{component}`, `/api/models/export/step`, `/export/stl`, `/export/json`, `/models/specification`).

## Options, per artifact type, exactly as currently supported

| Artifact type | Real current options | Source |
|---|---|---|
| `PREVIEW_MESH` | **None** — no per-request override exists; always uses the definition's own `preview.meshTolerance`/`angularTolerance`, always includes every component visibly | `preview/mesh.py` |
| `STEP` | `includeStoneReference: bool = False` | `api/schemas.py::ExportStepRequest` |
| `STL` | `includeStoneReference: bool = False`, `meshTolerance: float | None`, `angularTolerance: float | None` | `api/schemas.py::ExportStlRequest` |
| `JSON` | **None** | `api/schemas.py::ExportJsonRequest` |
| `TECHNICAL_SPECIFICATION` | **None** | `api/schemas.py::SpecificationRequest` |

## No invented exporter features

Per this Sprint's explicit instruction, no option is listed above that the current API doesn't genuinely accept — `partial-preview-request.json`'s `options: {}` (empty) honestly reflects that preview has no current per-request overrides, rather than inventing a plausible-sounding one.

## `required`, conceptually

Whether an artifact's failure should block overall compilation success (see [`173-partial-compilation-policy.md`](173-partial-compilation-policy.md)). **Not a real field in any current request** — every export request today is independently issued and independently succeeds or fails, with the caller (not the compiler) deciding what "required" means by choosing which calls to make and how to react to their results.

## Not part of `CompilationInput` today

Each `ArtifactRequest` is a separate, later HTTP call today — see [`163-compilation-input-contract.md`](163-compilation-input-contract.md)'s `requestedArtifacts` field, marked PLANNED for exactly this reason. Open question `ALCHEMIST-OQ-004` in [`188-open-alchemist-questions.md`](188-open-alchemist-questions.md) records whether this should ever change.

## Relationship to Foundry (Sprint 7)

`specs/foundry/v1/artifact-request.schema.json` is a deliberate, documented superset of this schema, scoped to production/technical artifacts only (`STEP | STL | JSON | TECHNICAL_SPECIFICATION` — no `PREVIEW_MESH`, which stays this schema's and Vision's concern). This schema remains authoritative for the minimal cross-cutting request shape; Foundry's schema is authoritative for the richer fields production exports specifically need. See [`09-foundry/193-artifact-request-contract.md`](../09-foundry/193-artifact-request-contract.md) for the exact reconciliation, field by field.
