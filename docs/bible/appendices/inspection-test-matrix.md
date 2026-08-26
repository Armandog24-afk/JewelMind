---
id: JM-BIBLE-A98
title: "Appendix: Inspection Test Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-A97
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Inspection Test Matrix

Every test in `backend/tests/test_geometry_inspection.py` (34 tests, 19 classes) and `backend/tests/test_geometry_inspection_schemas.py` (6 tests), by real class/function name and line number.

## `backend/tests/test_geometry_inspection.py`

| Class | Test(s) | Line | What it proves |
|---|---|---|---|
| `TestComponentExistsInspection` | `test_every_real_component_exists` | 67 | All 4 real solitaire components produce `PASS` existence facts. |
| | `test_a_zero_solid_component_is_reported_missing` | 74 | A component with zero solids is reported `FAIL`, never silently skipped. |
| `TestComponentVolumeInspection` | `test_real_component_volumes_are_finite_and_positive` | 88 | Every real component's volume is a finite, positive `float` — the NaN guard actually fires on real geometry. |
| `TestComponentBoundingBox` | `test_real_component_bounding_boxes_have_positive_extent` | 98 | Real bounding boxes have positive width/height/depth. |
| `TestSolidCount` | `test_prongs_solid_count_matches_generated_count` | 110 | `prongs`' solid count equals the real generated prong count (not the requested count). |
| | `test_band_is_a_single_solid` | 115 | `band` is exactly 1 solid. |
| `TestAssemblyComponentCount` | `test_real_solitaire_has_4_components` | 122 | The real default solitaire inspects to exactly 4 components. |
| | `test_required_components_present` | 129 | All 4 of `REQUIRED_COMPONENT_NAMES` are present. |
| `TestProngCountInspection` | `test_requested_matches_generated_for_supported_counts` (parametrized) | 138 | Supported prong counts (4, 6) produce `requestedCount == generatedCount`. |
| | `test_negative_requested_count_is_reported_as_a_mismatch` | 148 | The real builder's `max(requested_count, 0)` clamp is caught as a mismatch (see [`495-open-inspection-questions.md`](../16-geometry-inspection/495-open-inspection-questions.md) for related open questions on prong-count edge cases). |
| `TestStoneReferenceRole` | `test_stone_reference_is_counted_as_the_only_reference_component` | 168 | Exactly one `REFERENCE`-role component exists. |
| | `test_stone_metal_separation_reports_stone_exists_and_is_not_fused` | 175 | The structural (not geometric) separation check passes on real geometry. |
| | `test_stone_intersecting_prongs_is_expected_not_a_fusion_signal` | 184 | A positive stone↔prongs intersection volume does **not** flip the structural separation result to failed — the key correction of this Sprint. |
| `TestStoneExportSeparation` | `test_stone_reference_is_excluded_from_combined_metal` | 198 | `model.combined_metal` never includes the stone shape. |
| `TestComponentIntersection` | `test_band_and_stone_do_not_intersect` | 209 | The one genuinely separated pair reports `NO_INTERSECTION`. |
| | `test_prongs_and_basket_intersect_with_positive_volume` | 217 | A real, measured positive intersection volume. |
| | `test_known_separated_skips_the_boolean_call_and_reports_no_intersection` | 225 | `should_skip_intersection()` broad-phase path is exercised and produces the same classification as the full boolean call. |
| `TestComponentDistance` | `test_band_and_stone_distance_is_positive` | 239 | Real `Shape.distance()` result is positive for a separated pair. |
| | `test_touching_components_report_zero_distance` | 248 | A touching/overlapping pair reports `0.0` distance. |
| `TestProductionConnectivity` | `test_real_solitaire_production_metal_is_fully_connected` | 257 | `PRODUCTION` graph is one connected group for the real solitaire. |
| | `test_full_assembly_graph_includes_the_stone_reference` | 265 | `FULL_ASSEMBLY` graph includes `stone_reference` as a node. |
| `TestDisconnectedFixture` | `test_two_far_apart_boxes_are_reported_as_two_disconnected_groups` | 272 | A synthetic disconnected fixture is correctly detected as disconnected. |
| | `test_disconnection_is_never_hidden_or_silently_repaired` | 284 | `isFullyConnected: false` and `disconnectedGroupCount` are both accurate, never smoothed over. |
| `TestIntersectingFixture` | `test_two_overlapping_boxes_report_a_real_intersection_volume` | 295 | A synthetic overlapping fixture reports a real positive volume. |
| `TestInspectionErrorRecovery` | `test_intersection_with_a_kernel_failure_returns_unknown_not_a_crash` (monkeypatch) | 304 | A forced kernel exception in `Shape.intersect()` degrades to `UNKNOWN`, never raises out of `inspect_model()`. |
| | `test_distance_with_a_kernel_failure_returns_error_not_a_crash` | 318 | Same guarantee for `Shape.distance()`, degrading to `ERROR`. |
| `TestInspectionDeterminism` | `test_inspecting_the_same_geometry_twice_produces_equivalent_facts` | 335 | Two independent `inspect_model()` runs on identical geometry produce equivalent facts (excluding timestamps/IDs/timing). |
| `TestInspectionMetadata` | `test_generated_model_record_carries_a_real_inspection_report` | 358 | `ModelService.generate()` attaches a real `inspection_report`, not a placeholder. |
| | `test_inspection_report_accessor_returns_the_same_report` | 366 | `ModelService.inspection_report(model_id)` returns the exact same object generated at model-creation time. |
| `TestInspectionRegression` | `test_default_solitaire_matches_the_recorded_baseline_within_tolerance` | 379 | Real solitaire inspection facts match the recorded baseline (see [`solitaire-inspection-baseline.md`](solitaire-inspection-baseline.md)) within tolerance. |
| `TestFallbackInspection` | `test_band_fillet_fallback_state_is_visible_via_metadata` | 396 | A fillet-fallback warning on `band` is visible through the inspection result's carried-forward `warnings`. |
| | `test_combined_metal_multi_solid_is_detectable_as_a_fallback_signal` | 403 | A multi-solid `combined_metal` (fuse-fallback signal) is detectable via solid count. |
| `TestReviewPackageInspectionFile` | `test_review_package_contains_real_geometry_inspection_json` | 415 | `professional_validation/review_package.py`'s `geometry-inspection.json` entry is the real report, not a stub. |

## `backend/tests/test_geometry_inspection_schemas.py`

| Test | Line | What it proves |
|---|---|---|
| `test_all_schema_files_exist_and_are_valid_json_schema` | 49 | All 9 `specs/geometry-inspection/v2/*.schema.json` files are structurally valid JSON Schema. |
| `test_report_examples_validate_against_inspection_report_schema` | 55 | All example reports under `examples/` validate against `inspection-report.schema.json`. |
| `test_fact_registry_exists_and_has_no_professional_thresholds` | 62 | `fact-registry.json` never uses professional-validation/threshold wording — restates the Atlas/Forge boundary at the spec layer. |
| `test_all_test_vector_files_exist_and_are_non_empty` | 71 | All 8 `test-vectors/*.json` files exist and are non-empty. |
| `test_determinism_vectors_show_equivalent_facts_across_two_runs` | 88 | The determinism test-vector pair is genuinely equivalent. |
| `test_default_solitaire_example_is_reproducible_live` | 96 | The bundled default-solitaire example is reproduced live by `inspect_model()`, stripping `inspectionId`/`startedAt`/`completedAt`/`performance`/`generatedAt` before comparison — never a frozen, unverifiable fixture. |

**Total: 40 tests** (34 + 6), all passing at the time of Sprint 14's completion.
