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
| JM-FR-027 | The system shall generate a real, deterministic non-uniform band solid (width and/or thickness linearly tapered toward the bottom) via a 48-section loft, while leaving every uniform (non-tapered) band request byte-identical to the pre-Sprint-17 revolve construction. | current | `backend/jewelmind/geometry/shank/builder.py`, `test_shank.py` (77 tests), `goldens/solitaire-v1/SOL-010`/`SOL-011`/`SOL-012` |
| JM-FR-028 | The system shall generate a real, deterministic StoneReference solid for each of 7 shapes (round, oval, pear, emerald, cushion, princess, marquise) from explicit LENGTH/WIDTH/DEPTH dimensions plus an explicit orientation, while leaving every round request byte-identical to the pre-Sprint-18 construction. | current | `backend/jewelmind/geometry/stone/`, `test_stone.py` (92 tests), `goldens/solitaire-v1/SOL-013`–`SOL-018` |
| JM-FR-029 | The Stone System shall be category-neutral: no Stone System module may import any jewelry-category package. | current | `backend/jewelmind/geometry/stone/`, `backend/jewelmind/domain/stone_dimensions.py`, `test_stone_system_no_ring_dependency.py` (8 tests, AST-based) |
| JM-FR-030 | The system shall report both the requested and the independently measured LENGTH/WIDTH/DEPTH of a generated StoneReference, so an accidental scaling or shape regression is observable as a divergence between them. | current | `backend/jewelmind/geometry/inspection/inspector.py::_stone_dimension_facts`, `test_stone.py::TestStoneMeasuredDimensions` |
| JM-FR-031 | The system shall not evaluate a round-specific stone rule against a non-round stone by substituting a derived dimension. | current | `backend/jewelmind/validation/engine.py` (`JM-STONE-001`/`JM-PRONG-003` ROUND_ONLY), `test_stone.py::TestForgeRoundRuleScope` |
| JM-FR-032 | A stone shall carry an explicit gem identity (material, declared origin, declared treatments) that is independent of its geometry, and a design that names no gem shall remain valid and normalize to `unknown` rather than to diamond. | current | `backend/jewelmind/gem/`, `domain/schema.py::StoneSpec.gem`, `test_gem_identity.py` (119 tests) |
| JM-FR-033 | The Gem System shall be category-neutral: no Gem System module may import a jewelry category, a geometry module, the CAD kernel, or `JewelryDefinition`. | current | `backend/jewelmind/gem/`, `test_gem_no_category_dependency.py` (9 tests, AST-based) |
| JM-FR-034 | The system shall never infer a gem from geometry, and never substitute a different real gem for an unresolvable reference. | current | `backend/jewelmind/gem/resolution.py`, `test_gem_identity.py::TestResolution`, `test_gem_no_category_dependency.py::test_no_gem_module_reads_a_geometry_field` |
| JM-FR-035 | A semantic-only change (gem, origin, treatment, material, manufacturing) shall not change the geometry hash, and the system shall reuse already-built geometry instead of re-running the CAD kernel. | current | `backend/jewelmind/utils/hashing.py::geometry_hash`, `services/model_service.py`, `test_gem_identity.py::TestGeometryIdentitySeparation`, `test_gem_api.py::TestGemDoesNotForceRegeneration` |
| JM-FR-036 | The system shall distinguish "no treatment recorded" from "declared untreated" from "treated, kind unstated", and shall never resolve an unspecified treatment to a named one. | current | `backend/jewelmind/gem/resolution.py::treatment_summary`, `test_gem_identity.py::TestTreatments`, `frontend/src/components/ConfigurationPanel.tsx` |
| JM-FR-037 | The system shall make no gemological claim — no hardness, durability, heat-sensitivity, treatment-safety or gem-derived setting recommendation — in any rule, registry entry or user-facing message. | current | `test_gem_identity.py::test_no_gem_rule_makes_a_gemological_claim`, `test_gem_api.py::test_validation_never_returns_a_gemological_claim`, `test_capability_coverage.py::test_no_gem_property_rule_is_claimed_as_current` |
| JM-FR-038 | Designer shall recognize gem, origin and treatment terms in English and Italian, report a term naming both a stone cut and a gem species as ambiguous, and offer `custom`/`unknown` for an unrecognized gem rather than reporting a capability gap. | current | `backend/jewelmind/designer/gem_language.py`, `test_gem_designer_language.py` (45 tests) |
| JM-FR-039 | A design shall be able to declare multiple stone occurrences, each with a stable identifier, a reference to the stone specification and gem identity, a semantic role and an explicit placement, without duplicating what the underlying stone or gem defines. | current | `backend/jewelmind/arrangement/models.py`, `test_arrangement.py` (104 tests) |
| JM-FR-040 | The Stone Arrangement Engine shall be category-neutral and shall never construct geometry: no arrangement module may import a jewelry category, a geometry module or the CAD kernel. | current | `backend/jewelmind/arrangement/`, `test_arrangement_no_category_dependency.py` (11 tests, AST-based) |
| JM-FR-041 | An arrangement shall resolve deterministically to explicit placements, so equivalent input produces byte-identical output and an equivalent arrangement produces an identical fingerprint regardless of array order. | current | `backend/jewelmind/arrangement/resolve.py`, `normalize.py`, `test_arrangement.py::TestDeterminism` |
| JM-FR-042 | Arrangement identity shall be separate from design identity and from geometry identity, while the arrangement itself shall participate in the geometry hash. | current | `backend/jewelmind/arrangement/normalize.py::arrangement_fingerprint`, `test_arrangement.py::TestJdlIntegration` |
| JM-FR-043 | An arrangement shall be validated structurally — unique identifiers, resolvable references, resolvable structure — without any spacing, proportion or manufacturing threshold. | current | `backend/jewelmind/validation/engine.py::_arrangement_rules`, `test_arrangement.py::TestForgeArrangementRules` |
| JM-FR-044 | Every resolved stone instance shall report whether geometry was built for it, and an instance with no geometry shall always carry the reason; no placeholder geometry may stand in for it. | current | `backend/jewelmind/arrangement/compile.py`, `test_arrangement.py::TestCompilationBoundary` |
| JM-FR-045 | A design that declares no arrangement shall generate exactly as it did before arrangements existed. | current | `test_arrangement.py::TestBackwardCompatibility`, the 39-case Golden suite (zero baseline updates) |
