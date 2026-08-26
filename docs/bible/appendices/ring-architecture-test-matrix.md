---
id: JM-BIBLE-A109
title: "Appendix: Ring Architecture Test Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-RING-README
  - JM-BIBLE-520
related_documents:
  - JM-BIBLE-535
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Ring Architecture Test Matrix

Every test in `test_jewelry_category_extension.py`,
`test_ring_architecture.py`, and `test_ring_architecture_schemas.py`, by
real class/method name — **44 tests total**, verified by running
`pytest --collect-only -q` against all three files (mirrors
[`geometry-quality-test-matrix.md`](geometry-quality-test-matrix.md)
(A104)'s pattern).

## `test_ring_architecture.py` (20 tests)

| Class | Test(s) | What it proves |
|---|---|---|
| `TestRingDefinitionAdapter` | `test_default_solitaire_maps_cleanly_into_ring_definition`, `test_ring_sizing_mapping`, `test_shank_mapping`, `test_head_mapping`, `test_stone_arrangement_mapping`, `test_setting_attachment_mapping`, `test_adapter_is_pure_and_deterministic` (7) | `ring_definition_from_jdl()` maps every field correctly and deterministically. |
| `TestSolitaireFamilyDispatch` | `test_solitaire_is_the_only_registered_family`, `test_generate_ring_dispatches_to_the_real_solitaire_builder`, `test_unsupported_ring_family_raises_a_clean_error`, `test_reserved_planned_families_have_no_generator_yet` (4) | Only `solitaire` has a real generator; an unsupported/reserved family fails cleanly, never silently. |
| `TestBackwardCompatibleJdl` | `test_default_definition_still_generates_through_the_new_dispatch`, `test_generate_jewelry_and_generate_ring_produce_identical_geometry` (2) | The new dispatch path produces output identical to the old direct call for a real definition. |
| `TestStoneReferenceRegression` | `test_stone_reference_remains_separate_from_production_metal` (1) | LAW-006 stone/metal separation survives the new dispatch path. |
| `TestForgeScope` | `test_ring_sizing_rules_are_ring_specific`, `test_shank_rules_are_ring_specific`, `test_head_rules_are_ring_specific`, `test_stone_and_prong_rules_are_shared_scope`, `test_manufacturing_and_geometry_rules_are_shared_scope`, `test_an_unrecognized_rule_id_prefix_is_unknown_not_a_crash` (6) | `forge_scope.py`'s rule-prefix classification is correct and never crashes on an unknown prefix. |

## `test_jewelry_category_extension.py` (16 tests)

| Class | Test(s) | What it proves |
|---|---|---|
| `TestJewelryCategoryRegistry` | `test_ring_is_current_and_generation_supported`, `test_reserved_future_categories_are_planned_and_not_generatable` (parametrized: `earring`, `pendant`, `bracelet`, `necklace`, `charm` — 5), `test_unknown_category_returns_none`, `test_is_generation_supported_matches_capability_flag` (8 total) | The registry correctly reports `ring` as current/generatable and every other category as planned/not-generatable; an unknown category returns `None`. |
| `TestPlannedCategoryNotGeneratable` | `test_planned_category_cannot_be_dispatched_through_production_registry`, `test_unknown_category_is_unsupported_not_not_generatable` (2) | Planned vs. unknown categories raise distinct, correct error types. |
| `TestCategoryDispatch` | `test_generate_for_category_calls_the_registered_generator`, `test_missing_generator_for_a_supported_category_raises_not_generatable` (2) | The generic dispatch function calls the registered generator, and fails cleanly when a supported category has no generator. |
| `TestNonRingCategoryExtension` | `test_a_wholly_unrelated_category_dispatches_through_the_same_generic_function`, `test_dummy_category_definition_never_carries_a_ring_field`, `test_dummy_category_is_absent_from_the_real_production_registry`, `test_dummy_category_cannot_be_reached_through_generate_jewelry` (4) | The mandatory non-ring extensibility proof: a wholly unrelated `DummyPendantDefinition` category dispatches through the same generic function as `ring`, never touching the real production registry (JEWELRY-ARCH-GOV-011). |

## `test_ring_architecture_schemas.py` (8 tests)

Module-level functions, no classes:

| Test | What it proves |
|---|---|
| `test_all_jewelry_architecture_schemas_are_valid_json_schema` | The 3 `specs/jewelry-architecture/v1/` schemas are valid JSON Schema. |
| `test_all_ring_v2_schemas_are_valid_json_schema` | The 8 `specs/ring/v2/` schemas are valid JSON Schema. |
| `test_category_registry_matches_the_real_capability_registry_live` | `category-registry.json` matches the live `CATEGORY_CAPABILITIES` dict exactly (JEWELRY-ARCH-GOV-015 — no drift). |
| `test_category_registry_entries_validate_against_schema` | Every registry entry validates against `category-capability.schema.json`. |
| `test_only_ring_is_generation_supported_in_the_registry` | Only `ring` has `generationSupported: true` in the real registry file. |
| `test_ring_examples_validate_against_ring_definition_schema` | All 3 `specs/ring/v2/examples/*.json` files validate against `ring-definition.schema.json`. |
| `test_default_solitaire_ring_definition_example_is_reproducible_live` | `current-default-solitaire.json` is byte-for-byte reproducible by running the real `ring_definition_from_jdl()` today. |
| `test_all_ring_test_vector_files_exist_and_are_non_empty` | All 4 `specs/ring/v2/test-vectors/*.json` files exist and contain at least one vector. |

## Total: 44 tests (20 + 16 + 8)

Confirmed by running:

```
.venv/Scripts/python.exe -m pytest --collect-only -q \
  tests/test_ring_architecture.py \
  tests/test_jewelry_category_extension.py \
  tests/test_ring_architecture_schemas.py
```

which reports `44 tests collected`.
