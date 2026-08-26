---
id: JM-BIBLE-A104
title: "Appendix: Geometry Quality Test Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-500
related_documents:
  - JM-BIBLE-A98
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Geometry Quality Test Matrix

Every test in the 4 new files under `backend/tests/`, by real class/method name — 49 tests total, mirroring [`inspection-test-matrix.md`](inspection-test-matrix.md) (A98)'s pattern.

## `test_geometry_quality_snapshot.py` (16 tests)

| Class | Test(s) | What it proves |
|---|---|---|
| `TestComponentPresence` | `test_all_four_real_components_are_present` | `GOLDEN_COMPONENT_PRESENCE_TEST`. |
| `TestSolidCount` | `test_band_is_a_single_solid`, `test_default_prongs_solid_count_matches_generated_count` | `GOLDEN_SOLID_COUNT_TEST`. |
| `TestConnectivity` | `test_production_metal_is_fully_connected_by_default` | `GOLDEN_CONNECTIVITY_TEST`. |
| `TestIntersectionRelations` | `test_band_and_stone_reference_do_not_intersect`, `test_prongs_and_basket_support_intersect` | `GOLDEN_INTERSECTION_RELATION_TEST`. |
| `TestProngCount` | `test_default_six_prong_matches`, `test_four_prong_matches` | `GOLDEN_PRONG_COUNT_TEST`. |
| `TestStoneRole` | `test_stone_reference_is_never_production_metal` | `GOLDEN_STONE_ROLE_TEST`. |
| `TestVolatileFieldNormalization` | `test_snapshot_has_no_volatile_fields`, `test_two_snapshots_of_identical_geometry_are_equal` | `GOLDEN_VOLATILE_FIELD_NORMALIZATION_TEST`. |
| `TestMetadataOnlyEquivalence` | `test_metal_choice_does_not_change_geometry_snapshot` (parametrized x4), `test_manufacturing_method_does_not_change_geometry_snapshot` | `GOLDEN_METADATA_EQUIVALENCE_TEST` — metal/manufacturing method change `definitionHash` but never a single geometric fact. |

## `test_geometry_quality_harness.py` (17 tests)

| Class | Test(s) | What it proves |
|---|---|---|
| `TestRealGeneration` | `test_every_golden_in_the_manifest_passes`, `test_verify_golden_uses_the_real_pipeline_not_a_mock` | `GOLDEN_REAL_GENERATION_TEST`. |
| `TestHumanReadableDiff` | `test_a_clean_diff_reads_as_no_regression`, `test_a_real_verification_never_reports_a_false_regression`, `test_failing_diff_names_the_metric_and_both_values` | `GOLDEN_HUMAN_READABLE_DIFF_TEST` — split into a synthetic-zero-diff exact-string check and a live cross-platform-safe check after a real CI run showed the original single test assumed bit-identical cross-platform reproduction (see the Sprint 15 validation report). |
| `TestArtifactSeverityEscalation` | `test_artifact_regression_escalates_even_when_geometric_diff_is_info` | A real bug fix: an artifact regression must never be masked by a prior `INFO`-level geometric diff. |
| `TestIntentionalFailureDetection` | `test_altered_component_count_is_flagged_as_a_regression`, `test_volume_altered_beyond_tolerance_is_flagged`, `test_the_real_accepted_baseline_file_is_unchanged_by_this_test` | The mandated intentional-failure test (brief section 36) — mutates an in-memory copy only. |
| `TestRepeatability` | `test_three_repeated_generations_are_bit_identical_locally` | The mandated repeatability test (brief section 37). |
| `TestNoAutoUpdate` | `test_verify_golden_never_writes_to_the_registry`, `test_verify_all_goldens_never_writes_to_the_registry`, `test_generate_candidate_baseline_never_writes_to_the_registry`, `test_only_accept_candidate_baseline_calls_save_golden`, `test_a_regression_detected_by_verify_golden_does_not_change_the_file_on_disk` | `GOLDEN_NO_AUTO_UPDATE_TEST` — both a source-inspection proof and a real end-to-end proof. |
| `TestVersionFingerprint` | `test_fingerprint_uses_the_real_installed_kernel_version`, `test_every_accepted_golden_has_a_complete_fingerprint` | `GOLDEN_VERSION_FINGERPRINT_TEST`. |

## `test_geometry_quality_artifacts.py` (6 tests)

| Class | Test(s) | What it proves |
|---|---|---|
| `TestStepRoundtrip` | `test_default_solitaire_step_roundtrip_has_no_regressions`, `test_four_prong_variant_step_roundtrip_has_no_regressions` | `GOLDEN_STEP_ROUNDTRIP_TEST`. |
| `TestStlStructure` | `test_default_solitaire_stl_structure_has_no_regressions`, `test_four_prong_variant_stl_structure_has_no_regressions` | `GOLDEN_STL_STRUCTURE_TEST`. |
| `TestNoBinaryStepDeterminismClaim` | `test_two_step_exports_of_identical_geometry_are_not_byte_identical`, `test_step_roundtrip_check_never_compares_raw_bytes` | The mandated no-binary-STEP-determinism-claim test (brief section 38). |

## `test_geometry_quality_schemas.py` (10 tests)

| Test | What it proves |
|---|---|
| `test_all_schema_files_exist_and_are_valid_json_schema` | `GOLDEN_SCHEMA_TEST`. |
| `test_manifest_exists_and_validates_against_golden_suite_schema` | `GOLDEN_MANIFEST_TEST`. |
| `test_manifest_has_no_duplicate_golden_ids` | `GOLDEN_MANIFEST_TEST`. |
| `test_at_least_eight_golden_cases_exist` | Acceptance criterion #3 (brief section 45). |
| `test_every_golden_snapshot_json_validates_against_golden_model_schema` | `GOLDEN_SCHEMA_TEST` applied to all 9 real fixtures. |
| `test_every_golden_design_json_is_a_valid_jewelry_definition` | Confirms every fixture's source JDL is real and schema-valid. |
| `test_every_test_vector_file_exists_and_is_non_empty` | Spec/test-vector completeness. |
| `test_exact_invariant_vectors_are_reproducible_live` | Re-derives a real vector live to catch drift, mirroring `test_geometry_inspection_schemas.py`'s discipline. |
| `TestNoProfessionalClaim::test_no_golden_snapshot_contains_a_prohibited_claim` | The mandated no-professional-claim test (brief section 39). |
| `TestNoProfessionalClaim::test_manifest_contains_no_prohibited_claim` | Same, applied to the suite manifest. |

**Total: 49 tests**, all passing at the time of Sprint 15's completion, on top of the 715 tests that existed after Sprint 14.

## Cross-references

- [`inspection-test-matrix.md`](inspection-test-matrix.md) (A98) — the Sprint 14 equivalent this appendix mirrors.
- [`506-golden-regression-harness.md`](../17-geometry-quality/506-golden-regression-harness.md) — the harness these tests exercise.
