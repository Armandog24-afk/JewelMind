---
id: JM-BIBLE-429
title: Severity and Finding Classification
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-428
  - JM-BIBLE-099
  - JM-BIBLE-418
implementation_status: current
professional_validation: not_required
normative: true
---

# Severity and Finding Classification

## `FindingSeverity`: 5 values

`FindingSeverity` (`backend/jewelmind/professional_validation/schemas.py`)
is a closed `Literal` of exactly 5 values, ordered from least to most
severe: `NOTE`, `MINOR`, `MODERATE`, `MAJOR`, `CRITICAL`. Every
`ReviewObservation.severity` (see
[`428-review-observation-model.md`](428-review-observation-model.md)) must
be one of these five.

| Value | Meaning at the level of a jewelry review | Worked example |
|---|---|---|
| `NOTE` | A cosmetic preference or stylistic remark, not a defect. | "I'd personally taper the prong tips a bit more, but this is a matter of house style, not a functional concern." |
| `MINOR` | A real but low-impact observation — unlikely to affect manufacturability or wearability on its own. | "The transition between basket and band is slightly abrupt; a goldsmith would smooth this by hand during finishing without difficulty." |
| `MODERATE` | A genuine concern that would need attention before production, but is plausibly correctable without redesigning the piece. | "Prong height looks marginal for a secure setting at this stone size — I'd want to see this specific combination bench-tested before signing off." |
| `MAJOR` | A significant problem that a professional would expect to actually block or substantially delay production as generated. | "Prong tips are not tapered — would need bench finishing before setting" (the real example from `test_professional_validation_schemas.py::TestReviewObservationIsNotADecision`). |
| `CRITICAL` | Would definitely fail in production as generated — a defect a reviewer would never let through, e.g. a prong too thin to hold the stone, or a component that would not physically hold together. | "This prong geometry could not hold this stone size securely under normal wear — this is not a finishing-stage fix, the geometry itself needs to change." |

## Deliberately separate from three other classification systems

`FindingSeverity` looks similar to other severity-shaped concepts already in
this codebase. It is deliberately kept structurally and semantically
separate from each of them, and this document states the boundary
explicitly so no future change quietly merges them.

### (a) `ValidationDecisionType`

A `FindingSeverity` describes how bad one specific observed finding is. A
`ValidationDecisionType` (`ACCEPTED` / `ACCEPTED_WITH_CONDITIONS` /
`REJECTED` / `INSUFFICIENT_EVIDENCE` / `OUT_OF_SCOPE` / `SUPERSEDED`, see
[`418-validation-decision-model.md`](418-validation-decision-model.md))
describes the outcome of a formal decision about a precise claim. These are
different `Literal` types on different models (`ReviewObservation.severity`
vs. `ValidationDecision.decision`) and neither can substitute for the other.
A `CRITICAL` observation does not, on its own, produce a `REJECTED`
decision — a reviewer must still separately author a `ValidationDecision`
naming the exact `statementValidated` being rejected and why.

### (b) Forge's own severity

Forge's `Severity` type (`backend/jewelmind/validation/rules.py`, line 9)
is `Literal["error", "warning", "information"]` — three values, lowercase,
describing whether a Forge rule result blocks generation/export (see
[`06-forge/099-severity-and-blocking-semantics.md`](../06-forge/099-severity-and-blocking-semantics.md)).
`FindingSeverity` has 5 values, uppercase, and describes a professional
reviewer's subjective judgment of a finding's real-world significance — it
has no blocking semantics of its own at all (a `ReviewObservation`'s
`blockingRecommendation` field is a reviewer's opinion about blocking, not a
mechanism that blocks anything; see
[`428-review-observation-model.md`](428-review-observation-model.md)).

### (c) Automated test pass/fail

JewelMind's 675+ automated tests (per
[`410-validation-governance.md`](410-validation-governance.md), PROVAL-GOV-006)
produce a binary pass/fail per test. `FindingSeverity` has no relationship
to this at all — a test passing says nothing about whether a professional
reviewer would rate a related finding `NOTE` through `CRITICAL`, and a test
failing is not itself a `ReviewObservation`.

## No mechanical mapping between layers

This is the operative rule, stated directly: **there is no mechanical
mapping from `FindingSeverity` to Forge `Severity`, and no code anywhere in
`backend/jewelmind/` computes one.** A `CRITICAL` professional finding does
not automatically become a Forge `error`. A Forge `warning` does not
automatically become a `MINOR` finding. Each layer's classification is
independently meaningful, reflects a different kind of judgment (a Forge
severity is a deterministic, versioned, pre-declared consequence of a rule
condition; a `FindingSeverity` is one reviewer's subjective assessment of
one specific finding on one specific review), and moving a professional
finding into Forge's rule system requires the full intermediate workflow in
[`435-validation-to-forge-workflow.md`](435-validation-to-forge-workflow.md)
— never a lookup table between the two `Literal` types.
