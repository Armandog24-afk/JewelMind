---
id: JM-BIBLE-A72
title: "Appendix: Intent Test Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-DESIGN-INTENT-README
  - JM-BIBLE-330
related_documents:
  - JM-BIBLE-360
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Intent Test Matrix

Maps each of the 18 rules in [`330-intent-governance.md`](../13-design-intent/330-intent-governance.md) to the real, currently-passing test(s) that verify it. Mirrors [`designer-test-matrix.md`](designer-test-matrix.md)'s style: honest about partial or missing coverage rather than forcing a weak mapping.

## Rule -> test mapping

| Rule | Covered? | Real test(s) |
|---|---|---|
| **INTENT-GOV-001** (subjective language never silently becomes numeric geometry) | Yes | `backend/tests/test_designer_intent_integration.py::TestNoArbitraryNumericMapping` (`test_delicate_band_never_changes_band_width`, `test_bolder_never_increases_band_width_stone_diameter_or_prong_diameter`, `test_pure_intent_request_produces_no_changed_jdl_diff`); `backend/tests/test_design_intent.py::TestBuildDesignIntent::test_recognized_statement_is_preserved_never_resolved_to_geometry` (`relatedJDLPaths == []`); the 10-case `NO_ARBITRARY_NUMERIC_MAPPING` category in `test_design_intent_corpus.py`. |
| **INTENT-GOV-002** (every intent statement identifies its target) | Partial | `IntentStatement.target` is a required Pydantic field, so an omission fails at construction time — no test names this directly. The real behavior is exercised negatively by `test_design_intent.py::TestBuildDesignIntent::test_unknown_target_is_preserved_as_unresolved`: an unresolvable target never becomes an `IntentStatement` at all. |
| **INTENT-GOV-003** (every intent statement has provenance) | Yes | `test_design_intent.py::TestBuildDesignIntent::test_recognized_statement_is_preserved_never_resolved_to_geometry` asserts `statement.provenance == "AI_NORMALIZED"`. |
| **INTENT-GOV-004** (intent and JDL remain separate models) | Partial | Structural: `design_intent/schemas.py` and `domain/schema.py` share no field names by inspection; `frontend/src/store/useProjectStore.ts:167` calls `useDesignIntentStore.getState().clearIntent()` on `resetProject()`. No test in `useProjectStore.test.ts` or `useDesignIntentStore.test.ts` asserts this one-way reset call specifically. |
| **INTENT-GOV-005** (unresolved intent must be preservable) | Yes | `test_design_intent.py::TestBuildDesignIntent::test_unrecognized_descriptor_is_preserved_as_unresolved_text` and `test_provider_level_unresolved_descriptors_pass_through`; the 8-case `UNRESOLVED_DESCRIPTOR` category in `test_design_intent_corpus.py`. |
| **INTENT-GOV-006** (unsupported intent not silently discarded) | Partial | `test_design_intent.py::test_unrecognized_descriptor_is_preserved_as_unresolved_text` and `test_unknown_target_is_preserved_as_unresolved`; the 2-case `UNKNOWN_DESCRIPTOR` corpus category. No test asserts the specific `INTENT_UNKNOWN_DESCRIPTOR` diagnostic code is present by name — only the resulting `unresolvedDescriptors` entry is checked. |
| **INTENT-GOV-007** (conflicting intent must be explicit) | Partial | Backend: `test_design_intent.py::test_contradictory_statements_are_flagged_conflicting`, `test_adjacent_continuum_values_are_not_a_conflict`; the 3-case `CONFLICT` corpus category (`has_conflict_count(1)`). No frontend test exercises the "Conflicting intent" section actually rendering in `DesignerPanel.tsx`. |
| **INTENT-GOV-008** (intent strength must not be confused with geometric magnitude) | No | No test asserts the general property that `IntentStrength` never influences a numeric JDL value anywhere in the codebase; this is true only by code inspection (`strength` is read only in `conflicts.py`'s `PRIORITY_CONFLICT`-vs-`EXPLICIT_CONTRADICTION` classification, never in any geometry or JDL-writing path). |
| **INTENT-GOV-009** (AI interpretation remains non-authoritative) | Partial | Indirectly covered by the same tests as INTENT-GOV-001/003/016 (provenance is always `AI_NORMALIZED`, and `TestDesignerTechnicalVsIntentSeparation` proves the technical JDL/Forge gate is untouched by intent statements) — no test is framed specifically around "AI interpretation is non-authoritative" as its own assertion. |
| **INTENT-GOV-010** (only deterministic approved mappings may automatically influence JDL) | Yes | `backend/tests/test_design_intent_schemas.py::test_deterministic_resolution_vectors_never_show_a_numeric_mapping` and `test_vocabulary_file_exists_and_has_no_numeric_cad_mapping` (asserts `"mm"`, `"band.width"`, `"stone.diameter"`, `"prongDiameter"` are absent from `vocabulary.json`). |
| **INTENT-GOV-011** (professional manufacturing rules don't belong in the intent model) | No | No automated test scans `backend/jewelmind/design_intent/` for a manufacturing tolerance/density/Forge-style threshold; asserted only by code review, the same honest gap noted for the equivalent `DESIGNER-GOV-008` in `designer-test-matrix.md`. |
| **INTENT-GOV-012** (intent vocabulary must be versioned) | Partial | `DesignIntent.version` (default `"1.0.0"`) and `vocabulary.json`'s own `"version": "1.0.0"` field are present and implicitly exercised by every schema-validation test in `test_design_intent_schemas.py`, but no test explicitly asserts the version value or that a vocabulary content change must bump it. |
| **INTENT-GOV-013** (language-specific synonyms resolve to language-neutral canonical concepts) | Yes | `backend/tests/test_designer_intent_integration.py::TestMultilingualIntent::test_italian_and_english_delicate_converge_on_the_same_canonical_value`; the 8-case `MULTILINGUAL` corpus category. |
| **INTENT-GOV-014** (aesthetic concepts must not claim universal human meaning) | No | This is a documentation-framing rule about how `vocabulary.py`/Bible docs describe the taxonomy, not a runtime behavior; not testable by an automated test. |
| **INTENT-GOV-015** (intent resolution must remain reviewable) | Yes | `frontend/src/components/DesignerPanel.test.tsx::'shows design intent separately from technical fields and preserves it on apply'` — the "Design intent" section renders before "Apply proposal" is clicked, and `useDesignIntentStore.currentIntent` only updates after that explicit click. |
| **INTENT-GOV-016** (user-explicit technical values override subjective interpretations) | Yes | `backend/tests/test_designer_intent_integration.py::TestDesignerTechnicalVsIntentSeparation::test_technical_and_aesthetic_are_reported_separately` — asserts `proposedFields` contains only the technical paths and `not any(f.path.startswith("band") for f in proposal.proposedFields)`. |
| **INTENT-GOV-017** (existing JDL values not overwritten merely because an aesthetic descriptor is present) | Yes | `backend/tests/test_designer_intent_integration.py::TestNoArbitraryNumericMapping::test_bolder_never_increases_band_width_stone_diameter_or_prong_diameter` — cited verbatim in `330-intent-governance.md` itself. |
| **INTENT-GOV-018** (future intent-to-geometry profiles must have provenance and versioning) | No | `IntentProfile` (`design_intent/schemas.py`) requires `provenance`, `version`, and `professionalReview` with no default on the first two, so an omission fails Pydantic validation structurally — but no test in the suite constructs or validates an `IntentProfile` instance at all. |

## Test suite totals

- **Backend: 444 tests pass overall** — 132 new this Sprint: 28 in `backend/tests/test_design_intent.py`, 89 in `backend/tests/test_design_intent_corpus.py` (88 parametrized corpus cases + `test_corpus_has_at_least_60_cases`), 7 in `backend/tests/test_design_intent_schemas.py`, 8 in `backend/tests/test_designer_intent_integration.py`.
- **Frontend: 121 tests pass overall** — 10 new this Sprint (`frontend/src/store/useDesignIntentStore.test.ts` and the Design Intent cases added to `frontend/src/components/DesignerPanel.test.tsx`).

## Notes on honesty of coverage

Several rules above are marked "Partial" or "No" rather than "Yes" even though the underlying code exists and behaves correctly by inspection. Per this Sprint's own instruction not to force a weak mapping: a rule is marked "Yes" only when a specific named test asserts the exact behavior the rule states, not merely a related behavior in the same code path.
