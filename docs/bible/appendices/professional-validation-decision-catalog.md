---
id: JM-BIBLE-A84
title: "Appendix: Professional Validation Decision Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-418
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Professional Validation Decision Catalog

Two tables from `backend/jewelmind/professional_validation/schemas.py`, a table-only re-statement of [`418-validation-decision-model.md`](../15-professional-validation/418-validation-decision-model.md). Neither `PASS` nor `FAIL` is a valid value in either enum (`test_professional_validation_schemas.py::TestValidationStatusAndDecisionVocabulary::test_pass_fail_is_not_a_valid_decision`).

## The 6 `ValidationDecisionType` values

A reviewer's act, decided in one sitting about one precise `statementValidated`.

| Value | One-line meaning |
|---|---|
| `ACCEPTED` | The reviewer confirms the exact statement is correct, unconditionally. |
| `ACCEPTED_WITH_CONDITIONS` | The reviewer confirms the statement is correct only if named conditions hold; `conditions` is required non-empty (PROVAL-GOV-010). |
| `REJECTED` | The reviewer confirms the exact statement is incorrect. |
| `INSUFFICIENT_EVIDENCE` | The reviewer could not reach a decision with the evidence available. |
| `OUT_OF_SCOPE` | The object under review falls outside what this reviewer is qualified/was asked to review. |
| `SUPERSEDED` | This decision replaces an earlier decision (e.g. after a version change or a correction). |

## The 9 `ValidationStatus` values

The object's resulting standing in the registry — can also change for reasons other than a fresh decision (e.g. an implementation change moving a `VALIDATED` object to `REVALIDATION_REQUIRED`, PROVAL-GOV-013).

| Value | One-line meaning |
|---|---|
| `NOT_REVIEWED` | No review has occurred. Default `ValidationTarget.currentValidationStatus`. |
| `REVIEW_PLANNED` | A reviewer has been assigned and scheduled, review has not begun. |
| `UNDER_REVIEW` | A review session is actively in progress. |
| `INSUFFICIENT_EVIDENCE` | A review was attempted but could not reach a decision with available evidence. |
| `VALIDATED` | A reviewer accepted the exact statement, unconditionally. |
| `VALIDATED_WITH_CONDITIONS` | A reviewer accepted the exact statement, subject to stated conditions. |
| `REJECTED` | A reviewer confirmed the statement is incorrect. Remains in the audit history permanently (PROVAL-GOV-011). |
| `REVALIDATION_REQUIRED` | A prior `VALIDATED`/`VALIDATED_WITH_CONDITIONS` record no longer applies as-is because of a MAJOR version change to the underlying object. |
| `SUPERSEDED` | A newer record for the same object/version has been accepted, replacing this one. |

`registry.py::count_validated()` only ever counts `status in {VALIDATED, VALIDATED_WITH_CONDITIONS}` — an `ACCEPTED` decision on its own, without a corresponding `status`, is not what the registry counts.

## Decision → resulting status (real transitions, `status-transition-vectors.json`)

Quoted directly from `specs/professional-validation/v1/test-vectors/status-transition-vectors.json`:

| From | To | Trigger |
|---|---|---|
| `NOT_REVIEWED` | `REVIEW_PLANNED` | A reviewer is assigned and scheduled. |
| `REVIEW_PLANNED` | `UNDER_REVIEW` | The review session begins. |
| `UNDER_REVIEW` | `VALIDATED` | Reviewer decision: `ACCEPTED`. |
| `UNDER_REVIEW` | `VALIDATED_WITH_CONDITIONS` | Reviewer decision: `ACCEPTED_WITH_CONDITIONS`. |
| `UNDER_REVIEW` | `REJECTED` | Reviewer decision: `REJECTED`. |
| `UNDER_REVIEW` | `INSUFFICIENT_EVIDENCE` | Reviewer decision: `INSUFFICIENT_EVIDENCE`. |
| `VALIDATED` | `REVALIDATION_REQUIRED` | A MAJOR change to the validated rule/geometry version invalidates the prior record. |
| `VALIDATED_WITH_CONDITIONS` | `REVALIDATION_REQUIRED` | Same as above — a conditional acceptance is equally invalidated by a MAJOR change. |
| `VALIDATED` | `SUPERSEDED` | A newer record for the same object/version is accepted. |
| `REVALIDATION_REQUIRED` | `UNDER_REVIEW` | Re-review begins at the new version. |

`OUT_OF_SCOPE` and `SUPERSEDED` decisions have no dedicated transition row above because they do not map to a single mechanical status transition in the current vector set — an `OUT_OF_SCOPE` decision means the object was never actually reviewed under this record, and `SUPERSEDED` as a decision documents that a new decision exists, which is what drives the `VALIDATED`→`SUPERSEDED` status row already listed.

## `statementValidated` must be the precise claim

`"JM-PRONG-003 v1.0.0: 4 prongs blocked when stone diameter > 8mm."` is valid; `"The prong rules are fine."` is not — it does not say which rule, which version, or which specific behavior was reviewed. See [`418-validation-decision-model.md`](../15-professional-validation/418-validation-decision-model.md).

## Cross-references

- [`418-validation-decision-model.md`](../15-professional-validation/418-validation-decision-model.md) — full field tables and the PASS/FAIL rejection test excerpt.
- [`professional-validation-status-matrix.md`](professional-validation-status-matrix.md) (`JM-BIBLE-A86`) — how the 21 real Forge rules map onto `ValidationStatus`.
