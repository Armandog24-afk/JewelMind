---
id: JM-BIBLE-A90
title: "Appendix: Professional Validation Code Mapping"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-450
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Professional Validation Code Mapping

A denser, table-only re-mapping of [`410-validation-governance.md`](../15-professional-validation/410-validation-governance.md)'s own 20 PROVAL-GOV rules, adding the specific real function/file and real test for each. Mirrors [`conversation-code-mapping.md`](conversation-code-mapping.md)'s style: honest about a rule having only structural/indirect coverage rather than forcing a weak mapping to a test that does not actually exist.

| Rule | Real function/file | Real test(s) |
|---|---|---|
| **PROVAL-GOV-001** (no validation claim without a record) | `count_validated()` (`backend/jewelmind/professional_validation/registry.py`) — the only code path counting real `ValidationRecord`s | `test_professional_validation_registry.py::TestZeroValidationDefault::test_count_validated_on_the_real_registry_is_zero` |
| **PROVAL-GOV-002** (exact object and version) | `ValidationTarget.objectId`/`version` (`schemas.py`) — required, non-optional fields | `test_professional_validation_schemas.py::TestValidationRecordSchema::test_a_minimal_valid_record_round_trips`; structurally, `test_professional_validation_cli.py::test_missing_required_field_is_invalid` |
| **PROVAL-GOV-003** (explicit scope, always present) | `ValidationRecord.scope` (`ValidationScope`, `schemas.py`) — defaults to an all-`None` instance, never omitted | `test_professional_validation_scope.py::test_empty_scope_matches_any_context` |
| **PROVAL-GOV-004** (reviewer qualification must match review domain) | `ReviewerQualification.role`/`professionalFocus` (`schemas.py`) | `test_professional_validation_schemas.py::TestReviewerRole::test_every_documented_role_is_accepted`, `test_an_invented_role_is_rejected` |
| **PROVAL-GOV-005** (implementer cannot self-certify) | No code path in `backend/jewelmind/` constructs a `ValidationRecord` from a merge/test/implementation event | Structural — verified by code inspection (no such construction site exists); not exercised by a dedicated test. |
| **PROVAL-GOV-006** (passing tests ≠ professional validation) | `registry.py::load_active_registry()` reads only the active registry file, independent of test outcomes | `test_professional_validation_registry.py::TestZeroValidationDefault` (all 4 tests) |
| **PROVAL-GOV-007** (AI output ≠ professional validation) | `EvidenceQualityClass` includes `AI_ASSISTED`/`SOFTWARE_ONLY` (`schemas.py`) so they can be named and excluded | Documentation-level rule, stated in [`440-evidence-quality-model.md`](../15-professional-validation/440-evidence-quality-model.md); no mechanical enforcement code exists yet to block a `VALIDATED` status backed only by these two classes — a real gap, see [`451-validation-gap-analysis.md`](../15-professional-validation/451-validation-gap-analysis.md). |
| **PROVAL-GOV-008** (feedback cannot silently become a Forge rule) | No code in `professional_validation/` writes to `backend/jewelmind/validation/engine.py`; the intermediate workflow lives entirely in [`435-validation-to-forge-workflow.md`](../15-professional-validation/435-validation-to-forge-workflow.md) as process, not code | Structural — verified by the absence of any such import/write path; not exercised by a dedicated test. |
| **PROVAL-GOV-009** (accepted findings require review before changing runtime behaviour) | Same boundary as PROVAL-GOV-008 — `ValidationRecord` has no execution semantics | Structural — no `professional_validation/` module imports `jewelmind.validation.engine` or `jewelmind.geometry`. |
| **PROVAL-GOV-010** (conditional acceptance requires conditions) | `cli.py::validate_review_record_dict()` — checks `decision == "ACCEPTED_WITH_CONDITIONS"` implies non-empty `conditions` | `test_professional_validation_cli.py::test_accepted_with_conditions_requires_nonempty_conditions`, `test_accepted_with_conditions_and_real_conditions_is_valid` |
| **PROVAL-GOV-011** (rejected findings remain in audit history) | No delete/hide path exists for a `REJECTED` `ValidationRecord` | `test_professional_validation_schemas.py::TestRejectedValidation::test_a_rejected_record_still_carries_full_evidence_and_rationale` |
| **PROVAL-GOV-012** (conflicting reviews remain visible) | `DisagreementRecord.recordIds` (`schemas.py`) names both conflicting records; `registry.py` has no merge/average function | `test_professional_validation_schemas.py::TestDisagreementPreservation` (both tests) |
| **PROVAL-GOV-013** (implementation changes trigger impact analysis) | `versioning.py::classify_version_impact()` — the real, tested classifier behind [`434-implementation-change-impact.md`](../15-professional-validation/434-implementation-change-impact.md) | `test_professional_validation_versioning.py::TestVersionChangeImpact` (4 tests) |
| **PROVAL-GOV-014** (validation can expire) | `ValidationRecord.expirationOrReviewTrigger` (`schemas.py`) — real, optional field | No dedicated expiration-logic test exists (there is no automated expiration *process* to test yet, only the field); real triggers are documented in [`433-validation-expiration-and-revalidation.md`](../15-professional-validation/433-validation-expiration-and-revalidation.md). |
| **PROVAL-GOV-015** (validation scope never exceeds the evidence) | `scope_matches()` (`backend/jewelmind/professional_validation/scope.py`) | `test_professional_validation_scope.py::test_a_scope_field_left_unset_never_narrows_the_match` |
| **PROVAL-GOV-016** (manufacturing-specific validation does not generalize) | `ValidationScope.manufacturingMethod` via `scope_matches()` | `test_professional_validation_scope.py::test_round_lost_wax_scope_does_not_cover_oval_resin_context` |
| **PROVAL-GOV-017** (material-specific validation does not generalize) | `ValidationScope.material`/`alloy` via the same `scope_matches()` mechanism | Same generic function tested by `test_professional_validation_scope.py`; no material/alloy-specific test vector exists — the mechanism is proven generically (all `_SCOPE_FIELDS` are treated identically by `scope_matches()`), not per-field. |
| **PROVAL-GOV-018** (a reviewed example does not cover every parameter combination) | `ValidationRecord.scope.sizeRange`/`stoneDimensionRangeMm` (`schemas.py`) — nothing outside a named range is asserted covered | No dedicated test; documented as a sampling-breadth concern in [`441-review-sampling-strategy.md`](../15-professional-validation/441-review-sampling-strategy.md). |
| **PROVAL-GOV-019** (records must be auditable) | `ValidationRecord.recordId`/`reviewerId`/`reviewDate`/`evidenceIds`/`rationale` (`schemas.py`) — all required together | `test_professional_validation_cli.py::test_empty_reviewer_id_is_invalid`, `test_empty_evidence_id_entry_is_invalid`; `rationale` is a required (non-`Optional`) field enforced by Pydantic on every model construction. |
| **PROVAL-GOV-020** (approval never removes case-specific manufacturing review) | `review_package.py::_readme_text()` — the generated `README.md` states current software validation is not manufacturability certification | Documentation-level — verified by reading `_readme_text()`'s real output directly; no test asserts this exact wording string. |

## Notes grounded in the real code

- PROVAL-GOV-005, 007, 008, 009, 014, and 018 are marked with structural or documentation-level coverage rather than a single named test — each of these rules describes an absence (no code path exists to violate them) or a documentation commitment, not a behavior a unit test currently exercises. This matches this Bible's established pattern (see `conversation-code-mapping.md`'s own notes) of not forcing a weak mapping where the underlying property is structural.
- PROVAL-GOV-017 shares its enforcing function (`scope_matches()`) with PROVAL-GOV-016 rather than having a dedicated material/alloy test vector — `scope.py`'s `_SCOPE_FIELDS` loop treats every `ValidationScope` field identically, so the one real regression test (`test_round_lost_wax_scope_does_not_cover_oval_resin_context`) proves the mechanism generically across all fields, including `material`/`alloy`.

## Cross-references

- [`410-validation-governance.md`](../15-professional-validation/410-validation-governance.md) — the narrative source for all 20 rules.
- [`450-current-code-mapping.md`](../15-professional-validation/450-current-code-mapping.md) — the full file/responsibility inventory this table draws its function references from.
- [`professional-test-matrix.md`](professional-test-matrix.md) (`JM-BIBLE-A91`) — real, verified per-file test counts.
