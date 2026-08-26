---
id: JM-BIBLE-418
title: Validation Decision Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-415
  - JM-BIBLE-417
  - JM-BIBLE-431
  - JM-BIBLE-430
normative: true
implementation_status: current
professional_validation: not_required
---

# Validation Decision Model

`ValidationDecision` (`backend/jewelmind/professional_validation/schemas.py`) is one reviewer's decision about one exact statement. It is the model this entire Sprint exists to make possible — everything in [`412-validation-object-model.md`](412-validation-object-model.md) through [`417-review-evidence-model.md`](417-review-evidence-model.md) exists so this decision can be recorded precisely.

## Fields

| Field | Type | Notes |
|---|---|---|
| `decision` | `ValidationDecisionType` | One of 6 values, below. Required. |
| `reviewerId` | `str` | Required, non-empty. |
| `statementValidated` | `str` | The precise claim reviewed. Required — see below. |
| `conditions` | `str \| None` | Required non-empty when `decision == "ACCEPTED_WITH_CONDITIONS"` (PROVAL-GOV-010). |
| `rationale` | `str` | Required. |
| `scope` | `ValidationScope` | Defaults to an empty scope. See [`415-validation-scope-model.md`](415-validation-scope-model.md). |
| `evidenceIds` | `str[]` | Default empty. References [`417-review-evidence-model.md`](417-review-evidence-model.md) entries. |
| `reviewDate` | `str` | Required. |
| `revalidationTrigger` | `str \| None` | Optional — when/why this decision should be re-reviewed. See [`433-validation-expiration-and-revalidation.md`](433-validation-expiration-and-revalidation.md). |

`ValidationRecord` (also in `schemas.py`) is the persisted, registry-eligible superset of this shape — it adds `recordId`, `target` (`ValidationTarget`), `sessionId`, `status` (`ValidationStatus`), `expirationOrReviewTrigger`, `supersedesRecordId`, and `isTemplate`. A `ValidationDecision` is the decision act; a `ValidationRecord` is what that act becomes once it is written into the active registry.

## The 6 `ValidationDecisionType` values

`ACCEPTED`, `ACCEPTED_WITH_CONDITIONS`, `REJECTED`, `INSUFFICIENT_EVIDENCE`, `OUT_OF_SCOPE`, `SUPERSEDED`.

## PASS/FAIL is deliberately not the vocabulary

None of the 6 decision values is `"PASS"` or `"FAIL"`, and neither string is a valid `ValidationDecisionType` — attempting either raises a Pydantic `ValidationError`, proven directly by `backend/tests/test_professional_validation_schemas.py::TestValidationStatusAndDecisionVocabulary::test_pass_fail_is_not_a_valid_decision`:

```python
def test_pass_fail_is_not_a_valid_decision(self):
    with pytest.raises(ValidationError):
        _record(decision="PASS")
    with pytest.raises(ValidationError):
        _record(decision="FAIL")
```

The reason is substantive, not stylistic: PASS/FAIL implies a binary, automated-test-style outcome — exactly the vocabulary of layer 1 (AUTOMATED VALIDATION, see [`411-professional-validation-overview.md`](411-professional-validation-overview.md)). Professional review outcomes are richer than binary: a reviewer can accept unconditionally, accept with named conditions, reject, state that available evidence was insufficient to decide either way, state that the object under review was outside the scope they were actually qualified/asked to review, or supersede an earlier decision. Forcing this range into PASS/FAIL would silently discard information a real reviewer actually communicated.

## `statementValidated` must be the precise claim, never the whole rule or an ambiguous paraphrase

`statementValidated` exists as its own field, separate from `ValidationTarget.description`, specifically so a decision names *exactly* what was accepted, rejected, or conditionally accepted — not the entire rule file, and not a vague restatement of the rule's general area. The correct form, restated from `README.md`'s own example:

- **VALID**: `"JM-PRONG-003 v1.0.0: 4 prongs blocked when stone diameter > 8mm."` — names the exact rule, exact version, and exact behavior.
- **INVALID (too broad)**: `"The prong rules are fine."` — does not say which prong rule, which version, or which specific behavior within `JM-PRONG-001` through `JM-PRONG-004` was actually reviewed.

A decision with an ambiguous `statementValidated` cannot be meaningfully scoped by `ValidationScope` either — scope narrows *who/what/where* a decision applies to, but only after the decision itself already names one exact claim to apply that scope to.

## PROVAL-GOV-010: conditions are required and non-empty for `ACCEPTED_WITH_CONDITIONS`

Enforced in `backend/jewelmind/professional_validation/cli.py::validate_review_record_dict()`:

```python
if record.decision in ("ACCEPTED_WITH_CONDITIONS",) and not (record.conditions or "").strip():
    errors.append("decision ACCEPTED_WITH_CONDITIONS requires non-empty conditions (PROVAL-GOV-010).")
```

This is a structural check performed by the `validate-review-record` CLI on any candidate `ValidationRecord` JSON file — it never judges whether the *content* of the conditions is reasonable, only that a decision claiming to be conditional actually carries its conditions. `backend/tests/test_professional_validation_cli.py::test_accepted_with_conditions_requires_nonempty_conditions` proves this live. The rule exists so a conditional acceptance can never be silently narrowed to an unconditional one by having its conditions dropped in transit — see [`431-conditional-acceptance-model.md`](431-conditional-acceptance-model.md) for the full conditional-acceptance lifecycle.

## `ValidationStatus` vs. `ValidationDecisionType`

These are two distinct enums on purpose. `ValidationDecisionType` is the reviewer's act (what they decided, in one sitting, about one statement). `ValidationStatus` — `NOT_REVIEWED`, `REVIEW_PLANNED`, `UNDER_REVIEW`, `INSUFFICIENT_EVIDENCE`, `VALIDATED`, `VALIDATED_WITH_CONDITIONS`, `REJECTED`, `REVALIDATION_REQUIRED`, `SUPERSEDED` — is the object's resulting standing in the registry, which can also change for reasons other than a fresh decision (e.g. an implementation change moving a previously `VALIDATED` object to `REVALIDATION_REQUIRED`, per PROVAL-GOV-013 and [`434-implementation-change-impact.md`](434-implementation-change-impact.md)). `registry.py::count_validated()` only ever counts `status in {"VALIDATED", "VALIDATED_WITH_CONDITIONS"}` — a `decision: ACCEPTED` on its own, without a corresponding `status`, is not what the registry counts.

## `evidenceIds` and `rationale` are both required for auditability

Per PROVAL-GOV-019, a decision is never recorded without its supporting trail — `rationale` is a required non-optional field on both `ValidationDecision` and `ValidationRecord`, and while `evidenceIds` can be an empty list structurally, a decision citing zero evidence should generally correspond to an `INSUFFICIENT_EVIDENCE` decision rather than `ACCEPTED`/`ACCEPTED_WITH_CONDITIONS` — this is a documented expectation for how the framework is meant to be used, not a constraint `cli.py` currently enforces mechanically; see [`452-open-professional-validation-questions.md`](452-open-professional-validation-questions.md).
