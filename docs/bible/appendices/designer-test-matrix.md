---
id: JM-BIBLE-A63
title: "Appendix: Designer Test Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-290
related_documents:
  - JM-BIBLE-319
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Designer Test Matrix

Maps each of the 18 rules in [`290-designer-governance.md`](../12-designer/290-designer-governance.md) to the real, currently-passing test(s) that verify it. Mirrors [`studio-test-matrix.md`](studio-test-matrix.md)'s style: honest about partial or missing coverage rather than forcing a weak mapping.

## Rule -> test mapping

| Rule | Covered? | Real test(s) |
|---|---|---|
| **DESIGNER-GOV-001** (proposal-only authority) | Yes | `frontend/src/components/DesignerPanel.test.tsx::'shows a proposal review after a successful interpretation and applies it on request'` — `useProjectStore.currentDefinition` only changes after the explicit "Apply proposal" click, never on interpretation alone. |
| **DESIGNER-GOV-002** (cannot bypass JDL validation) | Partial | `backend/tests/test_designer.py::TestUnsupportedFeature::test_unknown_field_from_provider_is_rejected_not_smuggled_into_jdl` (an unknown field never reaches `JewelryDefinition`) and `TestModifyProposalAndPreservation` (candidate always constructed via `JewelryDefinition.model_validate()` in `_apply_patch`). No test directly forces `_apply_patch()` to return `None` (a patch that is schema-known-field-valid per-field but fails whole-model validation) and asserts `proposalStatus == "INVALID"` — that branch of `service.py::_build_proposal` is implemented but not exercised by name. |
| **DESIGNER-GOV-003** (cannot bypass Forge) | Yes | `backend/tests/test_designer.py::TestForgeIntegration::test_forge_warning_is_surfaced_on_the_proposal` (real `JM-BAND-002` warning) and `test_forge_error_does_not_block_the_proposal_from_being_returned` (real Forge error surfaced, proposal still returned). |
| **DESIGNER-GOV-004** (cannot invent unsupported enum values) | Yes | `backend/tests/test_designer.py::TestUnsupportedFeature::test_unsupported_stone_shape_value_is_caught_deterministically` and `test_unknown_field_from_provider_is_rejected_not_smuggled_into_jdl` (also cited verbatim in `290-designer-governance.md` itself). |
| **DESIGNER-GOV-005** (unsupported features reported explicitly) | Yes | `backend/tests/test_designer.py::TestUnsupportedFeature::test_provider_flagged_unsupported_feature_is_reported_not_silently_dropped` and `frontend/src/components/DesignerPanel.test.tsx::'surfaces unsupported features without silently dropping them'`. |
| **DESIGNER-GOV-006** (distinguish explicit/inferred/defaulted values) | Partial | `backend/tests/test_designer.py::TestExplicitFieldExtraction` (`EXACT`), `TestEnumNormalization` (`NORMALIZED`), `TestInvalidAiOutput` (numeric fields tagged `INFERRED`), `TestSystemDefault::test_unspecified_fields_use_system_defaults_on_create` (unspecified fields equal schema defaults). In the real pipeline every constructed `ProposedField` carries `provenance="AI_INTERPRETATION"` — the other 7 `FieldProvenance` values (`USER_EXPLICIT`, `USER_CONTEXT`, `CURRENT_DESIGN`, `SYSTEM_DEFAULT`, `DETERMINISTIC_DERIVATION`, `CLARIFICATION_RESPONSE`, `UNRESOLVED`) are declared in `designer/schemas.py` but never assigned by any current code path (see `designer-code-mapping.md`'s note on topic 321), so "defaulted" is observable only as *absence* from `proposedFields`, never as a tagged provenance value. |
| **DESIGNER-GOV-007** (geometry-driving AI-inferred value reviewable before generation) | Yes | `frontend/src/components/DesignerPanel.test.tsx::'shows a proposal review after a successful interpretation and applies it on request'` — the "JewelMind understood" section renders `proposedFields` before the apply button is clickable. |
| **DESIGNER-GOV-008** (must not invent professional manufacturing rules) | Partial | Indirectly exercised by `backend/tests/test_designer.py::TestUnsupportedFeature::test_unsupported_stone_shape_value_is_caught_deterministically`, which reads a `capability.KNOWN_UNSUPPORTED_CONCEPTS` reason string — but no test asserts the general property that no `UnsupportedFeature.reason` in the codebase invents a manufacturing constraint. |
| **DESIGNER-GOV-009** (must not claim manufacturability) | No | No automated test scans `backend/jewelmind/designer/` or `DesignerPanel.tsx` strings for a manufacturability claim; this is asserted only by code review, the same as the equivalent gap noted for `RESPONSIVE_LAYOUT_LOGIC_TEST` in `studio-test-matrix.md`. |
| **DESIGNER-GOV-010** (AI confidence must not replace deterministic validation) | Partial | `RawProposedValue` (`designer/schemas.py`) has no `confidence` field at all, so a provider cannot submit one; `backend/tests/test_designer.py::TestExplicitFieldExtraction` and `TestEnumNormalization` confirm `ConfidenceCategory` is instead derived by `service.py::_build_proposal` from normalization facts. No dedicated test asserts "a confidence field on the wire is rejected/ignored" because the wire schema (`_TOOL_INPUT_SCHEMA` in `provider.py`) never defines one to reject. |
| **DESIGNER-GOV-011** (every proposed field has provenance) | Partial | `ProposedField.provenance` is a required (non-Optional, no-default) field in `designer/schemas.py`, so any construction site omitting it fails at Pydantic validation time; every real construction site in `service.py::_build_proposal` supplies it, verified indirectly by the `field.provenance == "AI_INTERPRETATION"` assertions in `TestExplicitFieldExtraction`. No test named specifically for "omitting provenance raises". |
| **DESIGNER-GOV-012** (unsupported requests not silently downgraded) | Yes | `backend/tests/test_designer.py::TestUnsupportedFeature::test_unsupported_stone_shape_value_is_caught_deterministically` — an unsupported `oval` stays reported as unsupported and `candidateJDL.stone.shape` stays at the schema default (`round`), never silently substituted. |
| **DESIGNER-GOV-013** (ambiguous requests not silently resolved) | Yes | `backend/tests/test_designer.py::TestAmbiguity::test_bare_gold_triggers_clarification_not_a_guess` and `test_provider_reported_ambiguity_is_surfaced`. |
| **DESIGNER-GOV-014** (runtime geometry pipeline works without Designer) | Partial | No dedicated test proves `/api/models/generate`/`/validate`/exporter routes have zero dependency on `jewelmind.designer`; the closest real evidence is `backend/tests/test_designer_api.py::test_manual_endpoints_are_unaffected_when_designer_provider_is_unavailable` (only checks `/api/health`) plus the fact that all 204 pre-existing backend tests continue to pass unmodified in the same suite run alongside the 108 new Designer tests. |
| **DESIGNER-GOV-015** (provider failures don't break manual Studio operation) | Yes | `backend/tests/test_designer_api.py::test_manual_endpoints_are_unaffected_when_designer_provider_is_unavailable` and `frontend/src/components/DesignerPanel.test.tsx::'shows an "unavailable" message, without breaking manual editing, when no provider is configured'`. |
| **DESIGNER-GOV-016** (provider-specific formats don't leak past `provider.py`) | Partial | Structural: `designer/service.py` never imports `anthropic`, and every test in `test_designer.py`/`test_designer_corpus.py`/`test_designer_api.py` exercises the pipeline only through `RawDesignerResponse` (a JewelMind-owned model) via `FakeDesignerProvider`, never an `anthropic`-shaped object. No test asserts this as an explicit negative (e.g. an import-linter rule). |
| **DESIGNER-GOV-017** (LLM output constrained to machine-validated structured output) | Partial | `RawDesignerResponse.model_validate(...)` re-validation exists in `AnthropicDesignerProvider.interpret()` and its failure path is exercised via `DesignerSchemaViolationError` availability in `designer/errors.py`, but — consistent with `designer-diagnostic-catalog.md`'s own note — this has "not been exercised against a live API in this environment", so no test drives an actual `tool_choice`-constrained Anthropic response through this path; coverage is structural (Pydantic `extra="forbid"` on every `DesignerModel`) rather than a live-call test. |
| **DESIGNER-GOV-018** (user must approve/edit before generation) | Yes | `frontend/src/components/DesignerPanel.test.tsx::'shows a proposal review after a successful interpretation and applies it on request'` — `applyDesignerProposal()` runs only from the explicit "Apply proposal" click and the test's mocked `generateModel` is never invoked as part of that flow. |

## Test suite totals

- **Backend: 312 tests pass** — 204 pre-existing + 108 new this Sprint: 32 in `backend/tests/test_designer.py` (26 `def test_...` functions, expanded to 32 by `@pytest.mark.parametrize` on `TestEnumNormalization::test_metal_synonym_normalization` (5 cases) and `TestSecurityRejection::test_detect_prompt_injection_risk_flags_known_markers` (3 cases)), 5 in `backend/tests/test_designer_api.py`, 64 in `backend/tests/test_designer_corpus.py` (62 corpus cases + `test_corpus_has_at_least_50_cases` + `test_corpus_covers_all_11_named_categories`), 7 in `backend/tests/test_designer_schemas.py`.
- **Frontend: 111 tests pass** — 107 pre-existing + 4 new in `frontend/src/components/DesignerPanel.test.tsx`.

## Notes on honesty of coverage

Several rules above are marked "Partial" or "No" rather than "Yes" even though the underlying code path exists and is exercised indirectly by other tests. Per this Sprint's own instruction not to force a weak mapping: a rule is marked "Yes" only when a specific named test asserts the exact behavior the rule states, not merely a related behavior in the same code path.
