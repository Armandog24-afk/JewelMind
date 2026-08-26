---
id: JM-BIBLE-A113
title: "Appendix: Shank Test Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
related_documents:
  - JM-BIBLE-A19
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Shank Test Matrix

Every test class in `backend/tests/test_shank.py` (~77 tests, per the file's own module docstring listing 17 test classes) and `backend/tests/test_shank_schemas.py` (8 tests), mapped to the capability/contract it verifies.

## `backend/tests/test_shank.py`

| Test class | Verifies |
|---|---|
| `TestUniformShankBackwardCompatibility` | The default (no-taper) definition reproduces the exact pre-Sprint-17 recorded band/combined-metal volumes; confirms `widthTaper.mode`/`thicknessTaper.mode` default to `"NONE"` and dispatch to the uniform path (`variation == "UNIFORM"`) — SHANK-GOV-003. |
| `TestSectionProfiles` | `flat` and `comfort_fit` each produce a valid positive-volume solid with correct `metadata["profile"]`, and the two profiles differ in volume. |
| `TestWidthAndThicknessFunctions` | `taper_ratio()` is a no-op (`1.0`) for `mode == "NONE"` at any `u`; for `TOWARD_BOTTOM`, the ratio is exactly `1.0` at the head (`u=0`/`u=1`) and exactly `bottomRatio` at the bottom (`u=0.5`). |
| `TestWidthTaperGeneration` | A width-only taper produces exactly one valid solid with less volume than uniform, and `metadata["widthSamplesMm"]` reports the correct head/bottom values. |
| `TestThicknessTaperGeneration` | A thickness-only taper produces exactly one valid solid with less volume than uniform, and `metadata["thicknessSamplesMm"]` reports the correct head/bottom values. |
| `TestCombinedTaper` | Width and thickness taper applied together on a `flat` profile still produce exactly one valid solid with less volume than the equivalent uniform `flat` shank. |
| `TestTaperSymmetry` | `taper_ratio()` gives the same result at symmetric offsets from the head in either direction (`offset` vs. `1.0 - offset`), parametrized over 4 offsets — proves both shoulders share taper behaviour automatically (SHANK-GOV-005). |
| `TestInvalidTaper` | `JewelryDefinition.model_validate()` rejects `bottomRatio == 0.0`, `bottomRatio == 1.5`, negative `bottomRatio`, and an unrecognized taper `mode` (`"TOWARD_HEAD"`) — all via a fresh `model_validate()` call, never plain attribute assignment, since `StrictModel` lacks `validate_assignment=True`. |
| `TestDegenerateSection` | The smallest schema-permitted `bottomRatio` (`1e-6`) still produces a positive-volume solid — the schema-layer `bottomRatio > 0` bound structurally prevents a zero/negative tapered dimension. |
| `TestHeadConnection` | `ShankConnectionInterface.topZMm` is unchanged by a width taper, unchanged by a thickness taper, and the `band` component's own `metadata["connectionInterface"]` matches the interface computed independently — SHANK-GOV-011. Also verifies a tapered solitaire's head stays fully connected, stone/metal separated, and prong-count-matching via `inspect_model()`. |
| `TestShankVolumeAndBoundingBox` | A tapered shank's bounding box still reaches the full base outer radius at the head even though the bottom is thinner; tapered volume is positive and finite (explicit NaN check). |
| `TestShankConnectivity` | A tapered shank stays fully connected to the rest of the production assembly across both supported prong counts (4, 6), parametrized. |
| `TestShankStepExport` | A tapered solitaire's STEP roundtrip check (`step_roundtrip_check()`) returns no regressions, and the exported `.step` file is non-empty. |
| `TestShankStlExport` | A tapered solitaire's STL structure check (`stl_structure_check()`) returns no regressions, and the exported `.stl` file is non-empty. |
| `TestParameterSweep` | A bounded, representative parametrize sweep (`profile` x `width_ratio` x `thickness_ratio` x `prong_count` = 2x3x3x2 = 36 combinations) — every combination generates a single, finite, positive-volume, non-NaN/non-Inf solid; the module docstring documents this as the deliberate lightweight substitute for property-based testing (Hypothesis is not a backend dependency). |
| `TestShankConstructionErrorIsRaisedNotSwallowed` | `ShankConstructionError` is a real `Exception` subclass — structural proof a raised, non-silent failure path exists (SHANK-GOV-007). |
| `TestShankCapabilityRegistry` | The live capability registry matches what the builder actually produces (`uniform_shank` status vs. real `variation` metadata); no `planned` capability is `generatable`/`jdlExposed`; `taper_toward_head`/`split_shank`/`multi_rail_shank` are `planned`, not `current`; an unknown capability name returns `None`. |

## `backend/tests/test_shank_schemas.py`

| Test | Verifies |
|---|---|
| `test_all_schema_files_exist_and_are_valid_json_schema` | All 6 files under `specs/shank/v1/*.schema.json` parse as valid Draft 2020-12 JSON Schema. |
| `test_all_examples_validate_against_shank_definition_schema` | All 5 files under `specs/shank/v1/examples/` validate against `shank-definition.schema.json`. |
| `test_all_vector_files_exist_and_are_valid_json` | All 6 files under `specs/shank/v1/test-vectors/` exist, parse, and contain a non-empty `vectors` array. |
| `test_capability_registry_matches_the_real_capability_registry_live` | `specs/shank/v1/capability-registry.json` matches `SHANK_CAPABILITIES`, re-derived live from `geometry/shank/capability.py` — never a stale hand-copy. |
| `test_capability_registry_never_lists_a_planned_capability_as_generatable` | Every `status: "planned"` entry in the recorded registry has `generatable: false` and `jdlExposed: false`. |
| `test_only_toward_bottom_taper_mode_is_current` | `width_taper_toward_bottom`/`thickness_taper_toward_bottom` are `current`; `taper_toward_head` is not. |
| `test_uniform_comfort_fit_example_reproduces_live` | Re-running `build_shank()` on the default definition reproduces `examples/uniform-comfort-fit.json`'s recorded `variation`, `sectionCount`, and `volumeMm3` exactly. |
| `test_tapered_width_example_reproduces_live` | Re-running `build_shank()` with a 60%-bottom width taper reproduces `examples/tapered-width.json`'s recorded `widthSamplesMm` exactly. |

## Totals

**~77 tests in `test_shank.py`** (per the file's own docstring listing 17 classes) **+ 8 tests in `test_shank_schemas.py` = both fully passing.**

## Cross-references

- [`551-shank-generation-pipeline.md`](../19-shank/551-shank-generation-pipeline.md), [`552-shank-continuity-model.md`](../19-shank/552-shank-continuity-model.md) — the narrative contracts this matrix verifies.
- [`SPRINT-17-VALIDATION-REPORT.md`](../19-shank/SPRINT-17-VALIDATION-REPORT.md) — the full-suite pass count these tests contribute to.
- [`forge-rule-test-matrix.md`](forge-rule-test-matrix.md) — the equivalent per-rule test matrix for Forge, same table convention.
