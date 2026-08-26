---
id: JM-BIBLE-005
title: Current Product Status
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-000
related_documents:
  - JM-BIBLE-001
  - JM-BIBLE-006
  - JM-BIBLE-A01
  - JM-BIBLE-A02
  - JM-BIBLE-DOMAIN-README
implementation_status: current
---

# Current Product Status

This is the factual implementation matrix for JewelMind. Nothing here is
marked `current` or `partial` without a file path and/or a test backing
it, per [`000-bible-governance.md`](000-bible-governance.md). Full detail
per capability lives in
[`appendices/implementation-inventory.md`](../appendices/implementation-inventory.md)
and [`appendices/test-inventory.md`](../appendices/test-inventory.md);
this table is the summary.

| Capability | Status | Relevant files | Relevant tests | Known limitations | Next improvement |
|---|---|---|---|---|---|
| `JewelryDefinition` schema | current | `backend/jewelmind/domain/schema.py`, `shared/types/jewelry-definition.ts` | `test_schema.py` (3), `test_schema_safety.py` (70) | Kept in sync by hand; no codegen between Python and TypeScript. | Codegen or a shared IDL if the schema grows. |
| Validation engine (16 rules) | current | `backend/jewelmind/validation/engine.py`, `shared/validation/engine.ts` | `test_validation.py` (20) | Frontend mirror must be updated by hand alongside the backend rule. | Generate the frontend mirror from the backend rule set. |
| Flat band geometry | current | `backend/jewelmind/geometry/shank/` (via `geometry/components/band.py` re-export) | `test_geometry.py::test_flat_band_is_valid_solid_with_positive_volume`, `test_shank.py` | Optional outer-rim fillet has a documented fallback path (`docs/known-limitations.md`); not applied when taper is requested. | None planned. |
| Comfort-fit band geometry | current | `backend/jewelmind/geometry/shank/` (via `geometry/components/band.py` re-export) | `test_geometry.py::test_comfort_fit_band_is_valid_solid_with_positive_volume`, `test_flat_and_comfort_fit_bands_differ_in_volume`, `test_shank.py` | Fixed flare constant, not user-adjustable. | Expose flare amount as a parameter if requested. |
| Band width/thickness taper (Sprint 17) | current | `backend/jewelmind/geometry/shank/taper.py`, `builder.py` | `test_shank.py` (77 tests) | Tapered shank does not apply the outer-rim fillet (v1 limitation). Only `TOWARD_BOTTOM`, linear. | `TOWARD_HEAD` or non-linear taper if requested — see [`19-shank/559-open-shank-questions.md`](../19-shank/559-open-shank-questions.md). |
| Stone reference geometry | current (explicitly not gemological) | `backend/jewelmind/geometry/components/stone.py` | `test_geometry.py::test_stone_reference_is_valid_and_separate_from_metal` | Simplified proportions, round shape only. See [LAW-006](004-jewelmind-constitution.md). | None planned within current scope. |
| Four prongs | current | `backend/jewelmind/geometry/components/prongs.py` | `test_geometry.py::test_prongs_four_count`, `test_four_and_six_prong_models_visibly_differ` | Prongs are plain cylinders, not tapered/shaped. | None planned within current scope. |
| Six prongs | current | `backend/jewelmind/geometry/components/prongs.py` | `test_geometry.py::test_prongs_default_count_is_six` | Same as above. | None planned within current scope. |
| Basket support | current (deliberately simple) | `backend/jewelmind/geometry/components/basket.py` | `test_geometry.py::test_basket_exists_and_has_positive_volume` | Plain cylindrical shell, not decorative. | None planned within current scope. |
| Complete solitaire assembly | current | `backend/jewelmind/geometry/assemblies/solitaire.py` | `test_geometry.py::test_solitaire_assembly_has_all_required_components`, `test_solitaire_assembly_metal_is_single_fused_solid_by_default`, `test_definition_hash_is_deterministic` | Falls back to a multi-solid compound if boolean fuse fails (see [LAW-005](004-jewelmind-constitution.md)). | None planned within current scope. |
| Browser 3D preview | current | `frontend/src/components/ModelViewport.tsx`, `frontend/src/hooks/useComponentGeometries.ts` | `useComponentGeometries.test.ts` (7) | Single fixed set of materials/colors per metal; no lighting customization. | None planned within current scope. |
| STEP export | current | `backend/jewelmind/exporters/step_exporter.py` | `test_api.py::test_export_step_returns_nonempty_file`, `test_api_hardening.py` (unique-temp-file tests) | Excludes stone by default (by design, [LAW-006](004-jewelmind-constitution.md)). | None planned within current scope. |
| STL export | current | `backend/jewelmind/exporters/stl_exporter.py` | `test_api.py::test_export_stl_returns_nonempty_file`, `test_api_hardening.py` (tolerance validation tests) | Same exclusion as STEP. | None planned within current scope. |
| JSON export | current | `backend/jewelmind/exporters/json_exporter.py` | `test_api.py::test_export_json_matches_original_definition` | None known. | None planned. |
| Technical specification export | current | `backend/jewelmind/exporters/specification.py` | `test_api.py::test_specification_export_contains_disclaimer`, `test_api_hardening.py::test_specification_uses_original_generation_timestamp_not_download_time` | Markdown only, no PDF. | PDF rendering if requested. |
| `localStorage` persistence | current | `frontend/src/store/persistence.ts`, `shared/types/jewelry-definition.ts::isValidJewelryDefinition` | `persistence.test.ts` (14) | Single-slot (one saved project at a time), no project history. | Multiple saved projects, if requested. |
| Docker Compose setup | current (configuration reviewed, not live-tested in this pass) | `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile` | Exercised by the `docker-smoke-test` job in `.github/workflows/ci.yml` | Frontend image runs the Vite dev server, not a production nginx build (`docs/known-limitations.md`). | Multi-stage production frontend image. |
| GitHub Actions CI | current | `.github/workflows/ci.yml` | Runs `pytest`, `ruff`, frontend lint/test/build, and the Docker smoke test on every push/PR to `main` | None known. | None planned. |
| API surface | current | `backend/jewelmind/api/routes.py`, `schemas.py` | `test_api.py` (15), `test_api_hardening.py` (17) | See [`appendices/api-inventory.md`](../appendices/api-inventory.md) for the full endpoint list. | None planned within current scope. |
| Error handling | current | `backend/jewelmind/api/errors.py`, `app.py` | `test_api_hardening.py::test_generation_failure_maps_to_model_generation_failed`, `test_step_export_failure_maps_to_step_export_failed`, `test_stl_export_failure_maps_to_stl_export_failed`, `test_cad_engine_unavailable_returns_503` | None known. | None planned. |
| Temporary file management | current | `backend/jewelmind/services/model_service.py` | `test_api_hardening.py::test_export_temp_file_is_deleted_after_http_response`, `test_export_temp_file_is_cleaned_up_on_failure`, `test_step_and_stl_exports_use_distinct_unique_temp_files` | In-memory model cache capped at 20 entries, cleared on backend restart. | Persistent model cache, if requested. |
| Conversation Engine v1 (multi-turn natural-language design refinement) | current | `backend/jewelmind/conversation/` (`__init__.py`, `errors.py`, `schemas.py`, `state.py`, `references.py`, `clarifications.py`, `context.py`, `service.py`), `backend/jewelmind/api/routes.py::conversation_turn_route`, `frontend/src/components/ConversationPanel.tsx`, `frontend/src/store/useConversationStore.ts` | `test_conversation.py` (26), `test_conversation_engine.py` (15, incl. the 6 required CASE A-F scenarios), `test_conversation_api.py` (6), `test_conversation_corpus.py` (82, incl. 80 real multi-turn cases across 17 categories), `test_conversation_schemas.py` (8); frontend `ConversationPanel.test.tsx` (7), `useConversationStore.test.ts` (3) | Backend is stateless per request — no server-persisted `ConversationSession`; `ADD_INTENT`/`REMOVE_INTENT` action types and `WAITING_FOR_ACCEPTANCE`/`CLOSED`/`FAILED` session statuses are schema-complete but currently unreachable (see `appendices/conversation-action-catalog.md`, `appendices/conversation-state-catalog.md`). | None planned within current scope. |
| Professional Validation Framework v1 (structured evidence capture for real professional review) | current (infrastructure only — zero real validations exist) | `backend/jewelmind/professional_validation/` (`__init__.py`, `errors.py`, `schemas.py`, `registry.py`, `scope.py`, `versioning.py`, `review_package.py`, `cli.py`), `backend/jewelmind/api/routes.py::review_package_route`, `frontend/src/components/ProfessionalReviewPanel.tsx` | `test_professional_validation_schemas.py` (37), `test_professional_validation_registry.py` (7), `test_professional_validation_cli.py` (12), `test_professional_validation_scope.py` (5), `test_professional_validation_specs.py` (8), `test_professional_validation_versioning.py` (6), `test_review_package.py` (14), `test_review_package_api.py` (5); frontend `ProfessionalReviewPanel.test.tsx` (6) | The active registry (`specs/professional-validation/v1/current-validation-registry.json`) contains zero records by design — no real jewelry professional has reviewed anything yet; this framework only builds the capture mechanism. See [`15-professional-validation/451-validation-gap-analysis.md`](../15-professional-validation/451-validation-gap-analysis.md). | Real pilot reviews once qualified reviewers are engaged — see [`15-professional-validation/README.md`](../15-professional-validation/README.md)'s pilot plan. |

## Test totals (as of this document's `last_updated`)

- **Backend:** 139 tests across `test_api.py` (15), `test_api_hardening.py`
  (17), `test_geometry.py` (14), `test_schema.py` (3),
  `test_schema_safety.py` (70), `test_validation.py` (20). Command:
  `cd backend && .venv/Scripts/python -m pytest -q`.
- **Frontend:** 41 tests across `BackendStatus.test.tsx` (3),
  `ConfigurationPanel.test.tsx` (3), `JsonViewer.test.tsx` (2),
  `ProjectActions.test.tsx` (5), `ValidationPanel.test.tsx` (3),
  `useComponentGeometries.test.ts` (7), `persistence.test.ts` (14),
  `useProjectStore.test.ts` (4). Command: `cd frontend && npm run test`.

See [`appendices/test-inventory.md`](../appendices/test-inventory.md) for
what each suite actually covers and where coverage is known to be thin.

## Jewelry-domain detail

The table above is a capability-level summary. For the underlying
jewelry-domain concepts — what a "ring," "band," "stone reference,"
"setting," "prong," and "basket support" actually mean in this codebase,
which are IMPLEMENTED FACTs versus PRELIMINARY SOFTWARE RULEs, and which
jewelry-domain questions remain open — see
[`04-jewelry-domain/README.md`](../04-jewelry-domain/README.md) (Sprint 2
of this Bible). In particular,
[`04-jewelry-domain/054-domain-validation-classification.md`](../04-jewelry-domain/054-domain-validation-classification.md)
classifies every one of the sixteen validation rules referenced above,
and confirms that **zero** of them have been professionally validated as
of this Sprint.
