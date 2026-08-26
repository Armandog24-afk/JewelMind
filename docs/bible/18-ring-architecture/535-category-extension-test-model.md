---
id: JM-BIBLE-535
title: Category Extension Test Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-RING-README
  - JM-BIBLE-520
related_documents:
  - JM-BIBLE-534
implementation_status: current
professional_validation: not_required
normative: true
---

# Category Extension Test Model

This document maps the brief's own named architecture test concepts to
the **real** test classes/methods that satisfy them, in
[`backend/tests/test_jewelry_category_extension.py`](../../../backend/tests/test_jewelry_category_extension.py)
and
[`backend/tests/test_ring_architecture.py`](../../../backend/tests/test_ring_architecture.py).
Where no real test covers a named concept, that is stated plainly rather
than forcing a fake mapping.

## Mapping

| Brief concept | Real test(s) | File |
|---|---|---|
| `CATEGORY_REGISTRY_EXTENSION_TEST` | `TestJewelryCategoryRegistry` (all methods): `test_ring_is_current_and_generation_supported`, `test_reserved_future_categories_are_planned_and_not_generatable` (parametrized over `earring`/`pendant`/`bracelet`/`necklace`/`charm`), `test_unknown_category_returns_none`, `test_is_generation_supported_matches_capability_flag` | `test_jewelry_category_extension.py` |
| `NON_RING_DEFINITION_NO_RING_FIELD_ACCESS_TEST` | `TestNonRingCategoryExtension::test_dummy_category_definition_never_carries_a_ring_field` (asserts `DummyPendantDefinition` has no `ring`/`band`/`basket`/`setting`/`stone` attribute); reinforced structurally inside `_dummy_pendant_generator()` itself, which asserts the same at call time | `test_jewelry_category_extension.py` |
| `UNSUPPORTED_CATEGORY_ERROR_TEST` | `TestPlannedCategoryNotGeneratable::test_planned_category_cannot_be_dispatched_through_production_registry` (raises `JewelryCategoryNotGeneratableError` for a recognized-but-planned category) and `test_unknown_category_is_unsupported_not_not_generatable` (raises `JewelryCategoryUnsupportedError` for an unrecognized category — proving the two error types are distinct, not conflated) | `test_jewelry_category_extension.py` |
| `RING_DISPATCH_TEST` | `TestCategoryDispatch::test_generate_for_category_calls_the_registered_generator` (generic dispatch mechanism) and `TestBackwardCompatibleJdl::test_default_definition_still_generates_through_the_new_dispatch` (the real, production `generate_jewelry()` path for a ring) | `test_jewelry_category_extension.py`, `test_ring_architecture.py` |
| `SOLITAIRE_DISPATCH_TEST` | `TestSolitaireFamilyDispatch::test_generate_ring_dispatches_to_the_real_solitaire_builder`, `test_solitaire_is_the_only_registered_family`, `test_unsupported_ring_family_raises_a_clean_error`, `test_reserved_planned_families_have_no_generator_yet` | `test_ring_architecture.py` |
| `SHARED_MATERIAL_REUSE_TEST` | **No dedicated test exists this Sprint.** Neither test file asserts that `material.metal`/`MaterialSpec` is reused unmodified by Ring Architecture. The closest indirect evidence is structural, not test-verified: `ring/models.py::RingDefinition` has no `material` field at all (confirmed by reading the file), so there is nothing to duplicate — but no test encodes this as a regression guard. | — |
| `SHARED_STONE_CONTRACT_TEST` | `TestRingDefinitionAdapter::test_stone_arrangement_mapping` — proves `stone.diameter`/`stone.depth` flow unmodified into `StoneArrangementDefinition.stone` via the real `StoneSpec.model_copy()` call in `ring/adapter.py` | `test_ring_architecture.py` |
| `GENERIC_FOUNDRY_BOUNDARY_TEST` | **No dedicated test exists this Sprint.** Grep of both `test_ring_architecture.py` and `test_jewelry_category_extension.py` for `Foundry`/`export_step`/`export_stl` returns no matches. Foundry (`exporters/`) was not modified this Sprint, so no new boundary test was written against it. | — |
| `GENERIC_VISION_BOUNDARY_TEST` | **No dedicated test exists this Sprint.** Same grep, same result, for `Vision`/`preview`. Vision (`frontend/src/vision/`) was not modified this Sprint either. | — |

## Honest summary

Six of the nine brief-named concepts have real, direct test coverage
today. Three do not:
`SHARED_MATERIAL_REUSE_TEST`, `GENERIC_FOUNDRY_BOUNDARY_TEST`, and
`GENERIC_VISION_BOUNDARY_TEST`. This is consistent with what actually
changed this Sprint — Foundry and Vision were untouched, and material
reuse was verified only by inspection of `ring/models.py`'s field list,
not by an executable test. Adding these three tests remains a real,
identifiable gap, not a claim this document manufactures coverage for
(see [`536-current-code-mapping-and-gaps.md`](536-current-code-mapping-and-gaps.md)
for the full gap register).

## What the 44 real tests, in aggregate, prove

Across `test_ring_architecture.py` (20 tests),
`test_jewelry_category_extension.py` (16 tests), and
`test_ring_architecture_schemas.py` (8 tests) — 44 tests total, verified
by running `pytest --collect-only` against all three files — the real,
tested claims are:

1. The JDL -> `RingDefinition` v2 adapter maps every field correctly and
   deterministically (`TestRingDefinitionAdapter`).
2. The solitaire family dispatches to the real, unmodified geometry
   builder, and an unsupported/reserved family fails cleanly
   (`TestSolitaireFamilyDispatch`).
3. The new dispatch path produces identical output to the old direct
   call, for a real definition (`TestBackwardCompatibleJdl`).
4. LAW-006 stone/metal separation survives the new dispatch path
   (`TestStoneReferenceRegression`).
5. Forge rule scope classification is correct and never crashes on an
   unknown prefix (`TestForgeScope`).
6. The category registry correctly reports `ring` as current/generatable
   and every other category as planned/not-generatable
   (`TestJewelryCategoryRegistry`).
7. Planned and unknown categories fail with the correct, distinct error
   types (`TestPlannedCategoryNotGeneratable`).
8. The generic dispatch function works with an arbitrary test-local
   registry (`TestCategoryDispatch`).
9. A wholly unrelated, non-ring category (`DummyPendantDefinition`)
   dispatches through the exact same `generate_for_category()` function
   `ring` uses, without ever touching the real production registry
   (`TestNonRingCategoryExtension`) — the mandatory extensibility proof
   this Sprint's README calls out as its single most important finding.
10. Every schema in `specs/jewelry-architecture/v1/` and `specs/ring/v2/`
    is valid JSON Schema, the category registry file matches the live
    Python registry, and the recorded examples/vectors are reproducible
    against real code (`test_ring_architecture_schemas.py`).
