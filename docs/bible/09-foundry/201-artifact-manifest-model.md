---
id: JM-BIBLE-201
title: Artifact Manifest Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-192
related_documents:
  - JM-BIBLE-178
implementation_status: planned
professional_validation: not_required
normative: true
---

# Artifact Manifest Model

## Reconciliation with Sprint 6

Sprint 6's `specs/alchemist/v1/artifact-manifest.schema.json` already defines a single, minimal per-compilation-result field aggregating artifact outcomes. Foundry's `specs/foundry/v1/artifact-record.schema.json` (one entry) and `artifact-manifest.schema.json` (the aggregate) are declared a genuine, richer extension — never a duplicate — carrying integrity/checksum/versioning detail Alchemist's schema does not define. Alchemist's schema remains authoritative for the minimal shape any compilation result carries; Foundry's schema is authoritative for the artifact-integrity detail specific to production/technical exports.

## `ArtifactRecord` fields and their real status

| Field | Status | Notes |
|---|---|---|
| `artifactId` | PLANNED | No artifact identifier exists; a caller identifies an artifact only by `(model_id, artifactType)`. |
| `artifactVersion` | PLANNED | No versioning scheme exists for individual artifacts. |
| `status` | PARTIAL | Exists implicitly as "the HTTP call succeeded or raised" — never returned as an explicit enum value. |
| `filename` | CURRENT | `Content-Disposition` header, built via `sanitize_filename()`. |
| `mimeType` | CURRENT | Fixed literal per artifact type (`application/step`, `model/stl`, `application/json`, `text/markdown`) — never derived from file content; see [`A35-foundry-mime-type-catalog`](../appendices/foundry-mime-type-catalog.md). |
| `byteSize` | CURRENT as of Sprint 7 | `validate_non_empty()` return value, for STEP/STL only. |
| `checksum` | CURRENT as of Sprint 7 | `sha256_checksum()`, returned via the `X-Content-SHA256` response header, for STEP/STL only. |
| `sourceDefinitionHash` | CURRENT, implicit | Available via the `GeneratedModel` the export was built from, never attached to the HTTP response as a header or body field today. |
| `compilationHash` | PLANNED | Depends on a field that does not exist yet ([`08-alchemist/175-definition-hash-vs-compilation-hash.md`](../08-alchemist/175-definition-hash-vs-compilation-hash.md)). |
| `sourceComponentIds` / `includedComponents` / `excludedComponents` | PARTIAL | Real, but only derivable by inspecting `select_export_shapes()`'s inputs — never returned to the caller as data. |
| `unitContract` | CURRENT, informal | See [`212-unit-and-scale-contract.md`](212-unit-and-scale-contract.md) — true today, never surfaced as a field. |
| `generationDuration` | PLANNED | Not measured for export calls (it is measured for geometry generation itself, via `GeneratedModel.generation_duration_s`, but not for the export step). |
| `generatedAt` | PARTIAL | Threaded through for the specification artifact only (see [`200-technical-specification-contract.md`](200-technical-specification-contract.md)); not recorded for STEP/STL/JSON. |
| `exporterVersion` | PLANNED | See [`208-export-version-fingerprint.md`](208-export-version-fingerprint.md). |
| `warnings` | PARTIAL | `GeneratedModel.warnings` exists and is real, but is not re-surfaced per-artifact at export time. |
| `errorCode` | CURRENT, implicit | The real `AppError.code` raised on failure — never attached to a *successful* record, since no record object exists. |
| `required` | PLANNED | No request carries a required/optional flag; see [`193-artifact-request-contract.md`](193-artifact-request-contract.md). |
| `integrityStatus` | PARTIAL | See [`202-artifact-integrity-model.md`](202-artifact-integrity-model.md). |

## The manifest itself

No code anywhere aggregates multiple `ArtifactRecord`s into a single `ArtifactManifest` response. Each of the 4 artifact endpoints is called and evaluated completely independently by the caller (typically the frontend, calling STEP export and STL export as two separate HTTP requests). `specs/foundry/v1/examples/successful-artifact-manifest.json` and `partial-artifact-manifest.json` describe the *target* aggregate shape, built from real per-artifact data (real checksums and byte sizes from this Sprint's export runs) but assembled by hand for this specification, not returned by any endpoint today.
