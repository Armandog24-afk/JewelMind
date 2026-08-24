---
id: JM-BIBLE-172
title: Diagnostics and Failure Propagation
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-171
related_documents:
  - JM-BIBLE-A31
implementation_status: current
professional_validation: not_required
normative: true
---

# Diagnostics and Failure Propagation

Every scenario below is confirmed by inspecting `backend/jewelmind/services/model_service.py` and `api/routes.py` directly during this Sprint — checked into `specs/alchemist/v1/test-vectors/failure-propagation-vectors.json`.

| Scenario | Propagation | Conceptual status |
|---|---|---|
| Invalid JDL (structural) | Rejected at FastAPI/Pydantic parsing, before any compilation stage — `REQUEST_VALIDATION_ERROR`, HTTP 422 | Never reaches a meaningful `RECEIVED` state |
| Forge generation blocker | `ValidationBlockedError` before `build_solitaire_ring()` runs — HTTP 422, `VALIDATION_BLOCKED` | `BLOCKED` |
| Required component construction failure (hypothetical) | Propagates out of `build_solitaire_ring()` uncaught, out of `ModelService.generate()`, caught generically in `api/routes.py::generate_model()` → `ModelGenerationFailedError`, HTTP 500. No partial `ModelRecord` is ever cached | `FAILED` |
| Combined-metal fuse failure | Caught internally by `_fuse_metal()`; falls back to a compound with a warning. Generation still succeeds overall | `COMPLETED` (with a warning) — **not** a failure path |
| Preview mesh failure after valid B-Rep (hypothetical) | Would propagate uncaught out of `write_component_previews()`, failing the **entire** `generate()` call even though the B-Rep was valid — a real current coupling | `FAILED` (current) vs. `COMPLETED_WITH_WARNINGS` (target — see [`173-partial-compilation-policy.md`](173-partial-compilation-policy.md)) |
| STEP export failure | Caught in `export_step_route()` → `StepExportFailedError`, HTTP 500. The generated model remains valid and cached | Geometry stays `COMPLETED`; only the STEP artifact request fails |
| Export against an unknown/evicted `modelId` | `ModelNotFoundError`, HTTP 404 | `FAILED` for that specific artifact request only |

## Do not hide upstream causes

Every current error path preserves the underlying exception text: `ModelGenerationFailedError(f"Model generation failed: {exc}")`, `StepExportFailedError(f"STEP export failed: {exc}")`, etc. — the original cause is always included in the message (subject to the existing `_json_safe()` sanitization for non-finite-float leakage, see Sprint 1's hardening work), never swallowed into a generic "something went wrong."

## The key finding this document exists to surface

**Preview generation is coupled to core geometry generation; export generation is correctly decoupled.** This asymmetry is real, previously undocumented, and recorded as a gap in [`187-alchemist-gap-analysis.md`](187-alchemist-gap-analysis.md) — not fixed in this Sprint, since fixing it would mean restructuring `ModelService.generate()`, a real (if small) runtime change beyond this Sprint's documentation-and-specification scope.
