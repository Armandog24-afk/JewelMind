---
id: JM-BIBLE-194
title: Artifact Generation Pipeline (FOUNDRY-0..FOUNDRY-9)
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-190
related_documents:
  - JM-BIBLE-096
  - JM-BIBLE-173
implementation_status: partial
professional_validation: not_required
normative: true
---

# Artifact Generation Pipeline (FOUNDRY-0..FOUNDRY-9)

This is Foundry's own view of what happens once a caller asks for one artifact of an already-generated, already-cached model. It picks up exactly where Forge's FORGE-8 (export preconditions) and FORGE-9 (professional-review boundary) leave off — see [`06-forge/096-rule-evaluation-pipeline.md`](../06-forge/096-rule-evaluation-pipeline.md).

| Stage | Inputs | Outputs | Real code today |
|---|---|---|---|
| **FOUNDRY-0** Artifact eligibility | `model_id` | The cached `ModelRecord`, or `MODEL_NOT_FOUND` | CURRENT — `ModelService.get_record()` |
| **FOUNDRY-1** Artifact type dispatch | Which of 4 endpoints was called | The specific builder function to invoke | CURRENT, but implicit — there is no shared dispatcher; each route calls its own function directly |
| **FOUNDRY-2** Component selection | `GeneratedModel`, `include_stone` flag | The shape(s) to serialize (STEP/STL only) | CURRENT — `exporters/selection.py::select_export_shapes()` (extracted this Sprint) |
| **FOUNDRY-3** Temp destination allocation | `model_id`, extension | A unique temp file path | CURRENT — `ModelService._unique_temp_path()` |
| **FOUNDRY-4** Artifact building | Selected shape / definition / model | Real bytes written to the temp path | CURRENT — `Shape.exportStep()`, `Shape.exportStl()`, `json.dumps()`, `build_specification()` |
| **FOUNDRY-5** Non-empty validation | The written file path | Byte size, or `FOUNDRY_INTEGRITY_FAILED` | CURRENT as of Sprint 7 — `exporters/integrity.py::validate_non_empty()`; runs for STEP/STL only today |
| **FOUNDRY-6** Checksum computation | The written file path | A SHA-256 hex digest | CURRENT as of Sprint 7 — `exporters/integrity.py::sha256_checksum()`; runs for STEP/STL only today |
| **FOUNDRY-7** Response assembly | File path, checksum, sanitized filename | An HTTP `FileResponse` with `Content-Disposition` and `X-Content-SHA256` headers | CURRENT — `api/routes.py` |
| **FOUNDRY-8** Streaming and cleanup | The `FileResponse` | Bytes sent to the caller; temp file deleted | CURRENT — `BackgroundTask(_delete_file, path)` runs after the response finishes streaming; see [`207-temp-file-lifecycle.md`](207-temp-file-lifecycle.md) for the one known crash-window gap |
| **FOUNDRY-9** Deep integrity validation | The written file | Confirmed re-importability / format-signature validity | TEST-TIME ONLY — `backend/tests/test_export_integrity.py`; never runs for a real user request |

## Why FOUNDRY-5/6 are new and FOUNDRY-9 is not runtime

Before this Sprint, FOUNDRY-4 (build) was followed directly by FOUNDRY-7 (respond) with no independent check that the file CadQuery just wrote was actually non-empty or what its checksum was. FOUNDRY-5 and FOUNDRY-6 are this Sprint's targeted hardening, added because they are cheap, dependency-free, and directly testable — see [`202-artifact-integrity-model.md`](202-artifact-integrity-model.md). FOUNDRY-9 (re-import/roundtrip validation) was investigated as a *runtime* addition and found impractical for every request (re-importing every STEP file on every export would roughly double export latency for a check that only needs to prove the exporter code itself works, not that any individual output is valid) — it remains a test-suite-only guarantee, honestly documented as such rather than silently applied only sometimes.

## No short-circuit ambiguity

Unlike Forge's rule groups, FOUNDRY-0 through FOUNDRY-8 are a strict sequential chain today, each implemented as ordinary Python function calls inside a `try`/`except`: any stage raising an exception aborts every later stage, and `ModelService.export_step_file()`/`export_stl_file()` catch that exception specifically to delete the (possibly partial) temp file before re-raising — see [`207-temp-file-lifecycle.md`](207-temp-file-lifecycle.md).
