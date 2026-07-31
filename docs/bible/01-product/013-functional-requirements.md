---
id: JM-BIBLE-013
title: Functional Requirements
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-012
related_documents:
  - JM-BIBLE-005
  - JM-BIBLE-A02
implementation_status: current
---

# Functional Requirements

Each requirement below carries its own status per
[`000-bible-governance.md`](../00-foundation/000-bible-governance.md).
All requirements listed here are `current` unless marked otherwise —
this document does not include hypothetical future requirements; see
[`006-scope-and-boundaries.md`](../00-foundation/006-scope-and-boundaries.md)
for what is deliberately excluded.

| ID | Requirement | Status | Evidence |
|---|---|---|---|
| JM-FR-001 | The system shall accept a `JewelryDefinition` describing a solitaire ring's project, ring, band, stone, setting, material, and manufacturing parameters. | current | `backend/jewelmind/domain/schema.py` |
| JM-FR-002 | The system shall reject a `JewelryDefinition` with an unsupported `schemaVersion`. | current | `test_schema_safety.py::test_unsupported_schema_version_is_rejected` |
| JM-FR-003 | The system shall reject numeric fields supplied as strings, `NaN`, or `Infinity`. | current | `test_schema_safety.py` (70 tests) |
| JM-FR-004 | The system shall evaluate sixteen deterministic validation rules against a definition and return each result's rule ID, severity, message, and parameter. | current | `backend/jewelmind/validation/engine.py`, `docs/validation-rules.md` |
| JM-FR-005 | The system shall block model generation when any validation result has `severity: "error"`. | current | `test_api.py::test_generate_invalid_definition_returns_422` |
| JM-FR-006 | The system shall never block generation or export for `warning`/`information` results. | current | `test_validation.py::test_warnings_alone_do_not_block` |
| JM-FR-007 | The system shall deterministically generate the same geometry, volumes, and definition hash for the same input. | current | `test_geometry.py::test_definition_hash_is_deterministic` |
| JM-FR-008 | The system shall generate a flat-profile band and a comfort-fit-profile band that are geometrically distinct. | current | `test_geometry.py::test_flat_and_comfort_fit_bands_differ_in_volume` |
| JM-FR-009 | The system shall generate exactly four or exactly six prong solids as requested. | current | `test_geometry.py::test_prongs_four_count`, `test_prongs_default_count_is_six` |
| JM-FR-010 | The system shall keep the stone reference solid separate from the combined metal body. | current | `test_geometry.py::test_stone_reference_is_valid_and_separate_from_metal` |
| JM-FR-011 | The system shall generate one preview mesh per named component (band, stone reference, prongs, basket support). | current | `backend/jewelmind/preview/mesh.py`, `test_api.py::test_preview_component_endpoint_returns_nonempty_stl` |
| JM-FR-012 | The frontend shall render the 3D preview exclusively from backend-provided meshes. | current | `frontend/src/hooks/useComponentGeometries.ts` |
| JM-FR-013 | The system shall export a real, non-empty STEP file for a generated model, excluding the stone reference by default. | current | `test_api.py::test_export_step_returns_nonempty_file` |
| JM-FR-014 | The system shall export a real, non-empty STL file for a generated model, excluding the stone reference by default. | current | `test_api.py::test_export_stl_returns_nonempty_file` |
| JM-FR-015 | The system shall export the canonical `JewelryDefinition` as downloadable JSON. | current | `test_api.py::test_export_json_matches_original_definition` |
| JM-FR-016 | The system shall export a Markdown technical specification including dimensions, volumes, bounding box, validation results, warnings, and the professional-review disclaimer. | current | `test_api.py::test_specification_export_contains_disclaimer` |
| JM-FR-017 | The technical specification shall report the model's original generation timestamp, not the time it was downloaded. | current | `test_api_hardening.py::test_specification_uses_original_generation_timestamp_not_download_time` |
| JM-FR-018 | The system shall sanitize user-supplied project names before using them in export filenames. | current | `test_api.py::test_sanitized_filenames_in_content_disposition` |
| JM-FR-019 | Concurrent export requests for the same model shall not overwrite each other's output file. | current | `test_api_hardening.py::test_step_and_stl_exports_use_distinct_unique_temp_files` |
| JM-FR-020 | The system shall clean up temporary export files after both successful and failed export operations. | current | `test_api_hardening.py::test_export_temp_file_is_deleted_after_http_response`, `test_export_temp_file_is_cleaned_up_on_failure` |
| JM-FR-021 | The health endpoint shall report whether the CAD engine (CadQuery/OpenCascade) is actually ready, not merely importable. | current | `backend/jewelmind/services/cad_engine.py`, `test_api_hardening.py::test_probe_cad_engine_*` |
| JM-FR-022 | The system shall continue serving health checks and validation when the CAD engine is unavailable. | current | `test_api_hardening.py::test_cad_engine_unavailable_returns_503` (generation/export fail cleanly; validation is unaffected by design — see `api/routes.py::validate_model`) |
| JM-FR-023 | The frontend shall persist the current project to `localStorage` and reject corrupted or structurally invalid saved data, falling back to defaults. | current | `frontend/src/store/persistence.ts`, `persistence.test.ts` (14 tests) |
| JM-FR-024 | The frontend shall mark a generated model as stale when any parameter changes after generation, and disable export until regeneration. | current | `frontend/src/store/useProjectStore.ts`, `useProjectStore.test.ts` |
| JM-FR-025 | A failed model regeneration shall leave the last successful preview visible rather than clearing it. | current | `frontend/src/hooks/useComponentGeometries.ts`, `useComponentGeometries.test.ts` |
| JM-FR-026 | Every API error response shall include a documented error code and a request ID, and shall never include a raw stack trace. | current | `backend/jewelmind/api/app.py`, `test_api_hardening.py` (error-code mapping tests) |
