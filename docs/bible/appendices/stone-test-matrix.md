---
id: JM-BIBLE-A116
title: "Appendix: Stone Test Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-STONE-README
  - JM-BIBLE-560
related_documents:
  - JM-BIBLE-578
  - JM-BIBLE-A114
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Stone Test Matrix

Every real test in the three Sprint 18 Stone System test files, mapped to what it verifies. Sourced by reading the files, not from intent.

**Totals: 92 + 18 + 8 = 118 tests, all passing.** Several are parametrized over 6 non-round shapes or 2 symmetric shapes, so the collected count exceeds the function count.

## `backend/tests/test_stone.py` — 92 tests

### `TestRoundStoneBackwardCompatibility` (3)

| Test | Verifies |
|---|---|
| `test_default_definition_produces_the_pre_sprint18_recorded_volume` | Exact volume `58.22141924499569 mm³` at `rel=1e-9` — the byte-identical guarantee (STONE-GOV-016). |
| `test_round_stone_is_valid_solid_separate_from_metal` | One valid solid, positive volume, `metadata["shape"] == "round"`. |
| `test_round_stone_reports_length_equals_width_equals_diameter` | The internal normalization is reported in metadata (STONE-GOV-005). |

### `TestNonRoundShapeGeneration` (3 × 6 shapes = 18)

Parametrized over `oval`, `pear`, `emerald`, `cushion`, `princess`, `marquise`.

| Test | Verifies |
|---|---|
| `test_shape_generates_single_valid_positive_volume_solid` | Exactly 1 solid, `isValid()`, finite positive non-NaN/non-Inf volume, correct reported shape, `isGemologicalReproduction is False`. Covers OVAL/PEAR/EMERALD/CUSHION/PRINCESS/MARQUISE_GENERATION_TEST. |
| `test_shape_bounding_box_matches_requested_length_and_width_at_default_orientation` | Real measured Y extent = requested `length` (9.0), X extent = requested `width` (5.0), at `abs=0.01` — proves the LENGTH→Y / WIDTH→X mapping. |
| `test_shape_reference_stays_separate_from_metal` | StoneReference sits at or above the band's top (STONE-GOV-003). |

### `TestStoneCapabilityRegistry` (5, one parametrized × 6 = 10 collected)

| Test | Verifies |
|---|---|
| `test_every_current_shape_has_capability_metadata` | All 7 shapes have `status: current`, `generationSupported: True` (STONE-GOV-014). |
| `test_round_setting_compatibility_is_supported` | Round is `SUPPORTED`. |
| `test_non_round_setting_compatibility_is_experimental` (×6) | Every non-round shape is `EXPERIMENTAL` (STONE-GOV-009). |
| `test_no_shape_is_marked_planned` | The strong target was met — no shape is `planned`. |
| `test_unknown_shape_returns_none` | `get_stone_shape_capability("asscher")` is `None`. |

### `TestStoneDimensionValidation` (6, two parametrized × 6 = 26 collected)

Covers STONE_DIMENSION_VALIDATION_TEST.

| Test | Verifies |
|---|---|
| `test_round_without_diameter_is_rejected` | `ValidationError` when round has `diameter: None` (STONE-GOV-006). |
| `test_non_round_without_length_or_width_is_rejected` (×6) | `ValidationError` when neither is supplied. |
| `test_non_round_with_only_length_is_rejected` (×6) | `ValidationError` — **both** are required, not either. |
| `test_unknown_shape_is_rejected` | Closed enum rejects `"asscher"` (STONE-GOV-007). |
| `test_resolved_dimensions_match_public_fields_for_round` | `resolved_length == resolved_width == diameter`. |
| `test_resolved_dimensions_match_public_fields_for_non_round` (×6) | Resolution returns the real `length`/`width`/`depth`. |

### `TestStoneOrientation` (2, one parametrized × 2 = 3 collected)

Covers STONE_ORIENTATION_TEST and ROUND_ROTATION_EQUIVALENCE_TEST.

| Test | Verifies |
|---|---|
| `test_round_orientation_does_not_change_volume_or_bounding_box` | Round at 45° is volume- and extent-equivalent (`RADIAL`). |
| `test_90_degree_rotation_swaps_bounding_box_extents` (oval, marquise) | 90° swaps measured Y/X extents at `abs=0.05` and preserves volume. |

### `TestPearAsymmetry` (5, one parametrized × 2 = 6 collected)

Covers PEAR_ASYMMETRY_TEST. Uses a shared `_centroid_offset_y()` helper — the signed distance from the bounding-box centre to the real centre of mass along Y.

| Test | Verifies |
|---|---|
| `test_pear_mass_is_offset_toward_the_rounded_end` | Pear's centroid offset `< −0.5 mm` (real value −0.737306) — mass genuinely toward `−Y`, matching the tip-at-`+Y` convention. |
| `test_symmetric_elongated_shapes_have_no_centroid_offset` (oval, marquise) | The **control**: same class and dimensions, offset `< 1e-3`. Without this, the pear assertion could pass for a reason that would also hold for a symmetric shape. |
| `test_rotating_pear_180_degrees_flips_the_tip_direction` | `offset0 < 0 < offset180` **and** `offset180 ≈ −offset0` — a true directional flip — **and** volume/extents preserved (a rigid motion). |
| `test_rotating_pear_180_degrees_is_not_a_no_op` | Guards the regression where `_apply_orientation()` might early-return for any angle. |
| `test_pear_generator_never_silently_produces_a_symmetric_fallback` | Structural: pear's outline builder is not the same object as oval's or marquise's (STONE-GOV-013). |

### `TestStoneMeasuredDimensions` (3, one parametrized × 6 = 8 collected)

Covers STONE_MEASURED_DIMENSION_TEST, STONE_REFERENCE_ROLE_TEST, STONE_INSPECTION_TEST.

| Test | Verifies |
|---|---|
| `test_round_requested_and_measured_dimensions_match` | All 3 requested/measured fact pairs agree at `abs=1e-3`. |
| `test_non_round_requested_and_measured_dimensions_match` (×6) | Length and width pairs agree at `abs=0.05` for every non-round shape. |
| `test_stone_reference_never_reported_as_production_metal` | `stoneMetalSeparation.fusedIntoProductionMetal is False` (STONE-GOV-003/004, LAW-006). |

### `TestStoneProductionExportExclusion` (1 × 6 = 6)

Covers STONE_PRODUCTION_EXPORT_EXCLUSION_TEST and STONE_STEP_TEST.

| Test | Verifies |
|---|---|
| `test_step_export_excludes_stone_by_default` (×6) | A real non-empty `.step` file is written with `include_stone=False`, for every non-round shape. |

### `TestStoneStepExport` (1 × 4 = 4)

| Test | Verifies |
|---|---|
| `test_step_roundtrip_has_no_regressions` (oval, emerald, cushion, princess) | `step_roundtrip_check()` returns zero findings. |

### `TestStoneStlExport` (2, one parametrized × 3 = 4 collected)

Covers STONE_STL_TEST.

| Test | Verifies |
|---|---|
| `test_stl_structure_has_no_regressions` (oval, pear, marquise) | `stl_structure_check()` returns zero findings. |
| `test_stl_export_is_non_empty_for_a_non_round_shape` | A real non-empty `.stl` file is written. |

### `TestNonRoundAssembly` (1 × 4 = 4)

Covers NON_ROUND_ASSEMBLY_TEST — exceeds the required minimum of round + oval + one angular shape.

| Test | Verifies |
|---|---|
| `test_shape_generates_a_fully_connected_solitaire_assembly` (oval, emerald, cushion, princess) | A complete solitaire builds; `fullAssemblyConnectivity.isFullyConnected is True`; generated prong count matches. |

### `TestForgeRoundRuleScope` (4)

Covers FORGE_ROUND_RULE_SCOPE_TEST — the no-fake-equivalent-diameter guarantee.

| Test | Verifies |
|---|---|
| `test_stone_diameter_range_never_fires_for_non_round` | An oval at 100 × 100 produces no `JM-STONE-001` — the rule is genuinely ROUND_ONLY. |
| `test_prong_count_vs_stone_size_never_fires_for_non_round` | An oval at 20 × 20 with 4 prongs produces no `JM-PRONG-003`. |
| `test_stone_depth_range_fires_for_non_round_using_real_minimum_extent` | An oval 8 × 6 with depth 6.5 correctly errors — `JM-STONE-002` is genuinely SHARED. |
| `test_valid_non_round_stone_produces_no_stone_errors` | A valid cushion 7 × 7 × 4 produces no `stone.*` errors. |

### `TestStoneConstructionErrorIsRaisedNotSwallowed` (1)

| Test | Verifies |
|---|---|
| `test_stone_generation_error_is_a_real_exception_type` | `StoneGenerationError` is a real `Exception` subclass (STONE-GOV-013). |

## `backend/tests/test_stone_schemas.py` — 18 tests

Covers STONE_REGISTRY_TEST and the machine-readable validation requirement.

| Test | Verifies |
|---|---|
| `test_all_schema_files_exist_and_are_valid_json_schema` | All 5 schemas are valid Draft 2020-12. |
| `test_all_examples_validate_against_stone_definition_schema` | All 7 examples validate. |
| `test_all_vector_files_exist_and_are_non_empty` | All 5 test-vector files exist with non-empty `vectors`. |
| `test_shape_registry_matches_the_real_capability_registry_live` | The JSON mirror equals the live registry, field for field. |
| `test_shape_registry_entries_validate_against_capability_schema` | Every entry validates against the capability schema. |
| `test_registry_never_marks_a_non_generatable_shape_as_current` | No `current` entry has `generationSupported: false`. |
| `test_only_round_is_setting_compatibility_supported` | Exactly `["round"]` is `SUPPORTED`. |
| `test_all_seven_target_shapes_are_present_and_current` | The `current` set is exactly the 7 target shapes. |
| `test_example_reproduces_live` (×7) | Each example's shape, volume (6 dp), and reported length/width re-derive from live code. |
| `test_dimension_vectors_match_live_resolution` | Recorded resolved dimensions match live `resolved_*_mm()` output. |
| `test_invalid_stone_vectors_are_actually_rejected` | Every recorded invalid input really raises `ValidationError`. |
| `test_backward_compatibility_vector_reproduces_the_pre_sprint18_volume` | A pre-Sprint-18-shaped round document still produces the recorded volume. |

## `backend/tests/test_stone_system_no_ring_dependency.py` — 8 tests

Covers STONE_SYSTEM_NO_RING_DEPENDENCY_TEST (STONE-GOV-001). Uses **AST parsing**, not `import` — an import-based check could pass by accident on an already-cached module.

| Test | Verifies |
|---|---|
| `test_stone_system_file_never_imports_ring` (×6 files) | No file under `geometry/stone/` nor `domain/stone_dimensions.py` imports `jewelmind.ring`. |
| `test_at_least_one_stone_system_file_was_actually_checked` | Guards against the glob silently matching zero files. |
| `test_ring_is_allowed_to_depend_on_stone` | The reverse direction is real — documents the arrow in both directions. |

## Related coverage outside these files

| File | Relevance |
|---|---|
| `test_geometry_inspection_schemas.py` | The 6 new `STONE_*` fact types; `test_fact_registry_covers_exactly_the_live_fact_type_values` derives the expected set from the live `FactType` rather than a hardcoded count. |
| `test_geometry_quality_*.py` (49 tests) | STONE_GOLDEN_TEST — the 18-case Golden Suite including the 6 new per-shape cases. |
| `test_validation.py` | Pre-existing Forge rule coverage, unchanged and still passing. |
| `test_jdl_schema_examples.py` | JDL_HASH_STONE_CHANGE_TEST — regenerated hash/canonicalization vectors. |
| `test_designer_corpus.py`, `test_conversation_*.py` | DESIGNER_SHAPE_NORMALIZATION_TEST / CONVERSATION_SHAPE_CHANGE_TEST — the existing corpora, passing with the widened synonym table. |
| `frontend/src/store/useProjectStore.test.ts` | STALE_ON_STONE_CHANGE_TEST — the existing `updateStone()` → stale mechanism, unchanged. |
