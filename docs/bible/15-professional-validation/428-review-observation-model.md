---
id: JM-BIBLE-428
title: Review Observation Model
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
  - JM-BIBLE-415
  - JM-BIBLE-416
  - JM-BIBLE-427
  - JM-BIBLE-429
  - JM-BIBLE-430
implementation_status: current
professional_validation: not_required
normative: false
---

# Review Observation Model

## An observation is a finding, not a decision

`ReviewObservation` (`backend/jewelmind/professional_validation/schemas.py`)
is the type a reviewer's checklist work (see
[`427-review-checklist-model.md`](427-review-checklist-model.md)) actually
produces. Stated as plainly and prominently as possible, because it is the
single most important fact about this type: **`ReviewObservation` has no
`decision` field and no `status` field at all.** This is not a matter of
policy discipline layered on top of a type that could technically hold a
decision — it is a structural fact about the Pydantic model itself. There is
no attribute path by which code, a reviewer, or an AI agent could set an
observation's "decision," because the field does not exist to be set. An
observation can never be mistaken for a `ValidationRecord` by accident,
because the two types do not share that shape.

This is proven, not merely asserted, by
`backend/tests/test_professional_validation_schemas.py::TestReviewObservationIsNotADecision::test_an_observation_alone_does_not_change_validation_status`:

```python
def test_an_observation_alone_does_not_change_validation_status(self):
    observation = ReviewObservation(
        observationId="obs-1",
        caseId="case-1",
        reviewerId="r1",
        target="setting.prongs",
        category="geometry",
        severity="MAJOR",
        observation="Prong tips are not tapered — would need bench finishing before setting.",
    )
    # An observation has no `decision`/`status` field at all — it is
    # structurally incapable of being mistaken for a ValidationRecord.
    assert not hasattr(observation, "decision")
    assert not hasattr(observation, "status")
```

An observation that a reviewer never carries forward into a
`ValidationDecision`/`ValidationRecord` (see
[`418-validation-decision-model.md`](418-validation-decision-model.md))
simply remains a recorded finding — it never silently accumulates into a
validation outcome, because nothing in the type system or in
`registry.py::count_validated()` reads `ReviewObservation` at all;
`count_validated()` only ever reads `ValidationRecord.status`.

## Fields

`ReviewObservation` has 14 fields:

| Field | Type | Notes |
|---|---|---|
| `observationId` | `str` | Required. Unique identifier for this one finding. |
| `caseId` | `str` | Required. The `ReviewCase` (see [`425-review-case-model.md`](425-review-case-model.md)) this observation was made against. |
| `reviewerId` | `str` | Required. Who made the observation. |
| `target` | `str` | Required. What the observation is about — a component path or model area, e.g. `"setting.prongs"`. |
| `category` | `str` | Required. A free-text grouping, e.g. `"geometry"`, `"finishing"`, `"manufacturability"` — not a closed enum, because reviewer categories vary by role and by review type. |
| `severity` | `FindingSeverity` | Required. One of 5 values — see [`429-severity-and-finding-classification.md`](429-severity-and-finding-classification.md). |
| `observation` | `str` | Required. The actual free-text finding — the substance of what the reviewer noticed. |
| `evidenceIds` | `list[str]` | Default empty. References into `ValidationEvidence.evidenceId` values that support this observation. |
| `suggestedChange` | `str \| None` | Optional. What the reviewer thinks should change, if anything — a suggestion, not an instruction that automatically alters runtime behavior (PROVAL-GOV-008/009). |
| `blockingRecommendation` | `bool` | Default `False`. The reviewer's opinion on whether this finding should block something — an opinion, not itself a blocking mechanism; only Forge's real `blockingScope` (`06-forge/099-severity-and-blocking-semantics.md`) actually blocks anything at runtime. |
| `confidence` | `str \| None` | Optional. Free-text statement of how confident the reviewer is in this specific observation. |
| `scope` | `ValidationScope` | Defaults to an empty scope. Same 16-field model as everywhere else in this framework — see [`415-validation-scope-model.md`](415-validation-scope-model.md). |
| `relatedRuleIds` | `list[str]` | Default empty. Forge rule IDs this observation relates to, if any. |
| `relatedComponentIds` | `list[str]` | Default empty. Geometry component identifiers this observation relates to, if any. |

## Where observations attach

A `ReviewSession` (`backend/jewelmind/professional_validation/schemas.py`)
carries `observationIds: list[str]` alongside its `decisionIds: list[str]`
— these are two separate lists on the same session, because a single review
session routinely produces several observations (findings noticed while
working through a checklist) without every one of them resolving into a
formal `ValidationDecision`. See
[`416-review-session-model.md`](416-review-session-model.md). An observation
is where a reviewer's raw professional judgment gets captured in structured
form; a decision is the narrower, later act of formally accepting,
rejecting, or conditioning a specific claim.

## Why the distinction matters in practice

Without this structural separation, it would be tempting for a review tool
(or a future agent extending this codebase) to treat "a reviewer wrote
something critical" as equivalent to "this rule is now rejected." The
`ReviewObservation`/`ValidationRecord` split makes that conflation
impossible at the type level: a `CRITICAL`-severity observation about a
component is still just an observation until a reviewer separately produces
a `ValidationDecision` with an actual `decision` value naming the precise
`statementValidated` it applies to (see
[`418-validation-decision-model.md`](418-validation-decision-model.md)).
