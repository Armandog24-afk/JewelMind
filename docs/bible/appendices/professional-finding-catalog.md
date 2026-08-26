---
id: JM-BIBLE-A85
title: "Appendix: Professional Finding Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-429
  - JM-BIBLE-430
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Professional Finding Catalog

Two tables from `backend/jewelmind/professional_validation/schemas.py`, a table-only re-statement of [`429-severity-and-finding-classification.md`](../15-professional-validation/429-severity-and-finding-classification.md) and [`430-professional-disagreement-model.md`](../15-professional-validation/430-professional-disagreement-model.md).

## The 5 `FindingSeverity` values

Ordered least to most severe. Every `ReviewObservation.severity` must be one of these. Deliberately separate from `ValidationDecisionType` (an outcome of a formal decision), Forge's own lowercase `Severity` (`error`/`warning`/`information`, a deterministic blocking consequence), and automated test pass/fail — there is no mechanical mapping from `FindingSeverity` to any of the three.

| Value | Meaning | Concrete jewelry-review example |
|---|---|---|
| `NOTE` | A cosmetic preference or stylistic remark, not a defect. | "I'd personally taper the prong tips a bit more, but this is a matter of house style, not a functional concern." |
| `MINOR` | A real but low-impact observation, unlikely to affect manufacturability or wearability on its own. | "The transition between basket and band is slightly abrupt; a goldsmith would smooth this by hand during finishing without difficulty." |
| `MODERATE` | A genuine concern needing attention before production, plausibly correctable without redesigning the piece. | "Prong height looks marginal for a secure setting at this stone size — I'd want to see this specific combination bench-tested before signing off." |
| `MAJOR` | A significant problem expected to actually block or substantially delay production as generated. | "Prong tips are not tapered — would need bench finishing before setting" (the real example from `test_professional_validation_schemas.py::TestReviewObservationIsNotADecision`). |
| `CRITICAL` | Would definitely fail in production as generated — a defect a reviewer would never let through. | "This prong geometry could not hold this stone size securely under normal wear — this is not a finishing-stage fix, the geometry itself needs to change." |

A `CRITICAL` observation does not, on its own, produce a `REJECTED` decision — a reviewer must still separately author a `ValidationDecision` naming the exact `statementValidated`.

## The 5 `DisagreementType` values

Records that two (or more) `ValidationRecord`s concerning the same `objectId` relate to each other in one of these ways. A `DisagreementRecord` never picks a side and never averages the underlying records — both remain fully visible and independently queryable (PROVAL-GOV-012).

| Value | Meaning | Concrete jewelry-review example |
|---|---|---|
| `AGREEMENT` | Reviewers reached the same conclusion — recorded to make the absence of conflict explicit and auditable. | Two `STONE_SETTER` reviewers both accept `JM-PRONG-003` for the same scope, with a `DisagreementRecord` of type `AGREEMENT` making that concordance an explicit, queryable fact rather than an implicit absence of conflict. |
| `SCOPE_DIFFERENCE` | Both records are correct within their own stated scope — not actually disagreeing about the same claim once scopes are read precisely. | The real worked example: Reviewer A accepts `JM-PRONG-003` for `manufacturingMethod: lost_wax_casting`; Reviewer B rejects the same rule for `manufacturingMethod: direct_resin_printing` — see `specs/professional-validation/v1/examples/conflicting-review-example.json`. |
| `METHOD_DIFFERENCE` | Reviewers used different evaluation methods (e.g. different evidence types) and reached different conclusions as a result. | One reviewer accepts a basket-geometry claim based on `DIRECT_CAD` inspection alone; a second reviewer, using `DIRECT_PHYSICAL` inspection of a cast sample, finds a seat problem the CAD-only review could not see. |
| `PROFESSIONAL_DISAGREEMENT` | Reviewers genuinely disagree about the same claim, under the same scope, using comparable methods — an actual difference of professional judgment. | Two `GOLDSMITH_BENCH_JEWELER` reviewers, both working `lost_wax_casting`, both inspecting the same STEP file, reach opposite conclusions about whether the band/basket transition is bench-finishable as generated. |
| `INSUFFICIENT_CONTEXT` | Not enough recorded context to classify the disagreement as any of the above yet. | Two conflicting records exist, but neither reviewer's `rationale`/`scope` says enough to determine whether the conflict is scope-based, method-based, or genuine professional disagreement. |

## The real worked example, in full

`specs/professional-validation/v1/examples/conflicting-review-example.json` (both records `isTemplate: true` — illustrative, not a real review):

- `JM-PV-EXAMPLE-CONFLICT-A` — target `JM-PRONG-003`, scope `manufacturingMethod: "lost_wax_casting"`, decision `ACCEPTED`, status `VALIDATED`.
- `JM-PV-EXAMPLE-CONFLICT-B` — same target `JM-PRONG-003`, scope `manufacturingMethod: "direct_resin_printing"`, decision `REJECTED`, status `REJECTED`.
- `disagreement`: `disagreementId: "disagreement-example-1"`, `objectId: "JM-PRONG-003"`, `type: "SCOPE_DIFFERENCE"`, `recordIds: ["JM-PV-EXAMPLE-CONFLICT-A", "JM-PV-EXAMPLE-CONFLICT-B"]`.

`backend/tests/test_professional_validation_schemas.py::TestDisagreementPreservation::test_two_conflicting_records_are_never_merged_into_one` proves this mechanically.

## Cross-references

- [`429-severity-and-finding-classification.md`](../15-professional-validation/429-severity-and-finding-classification.md) — the full 3-way boundary against `ValidationDecisionType`, Forge `Severity`, and test pass/fail.
- [`430-professional-disagreement-model.md`](../15-professional-validation/430-professional-disagreement-model.md) — the `DisagreementRecord` field table and the "never silently average" rule.
