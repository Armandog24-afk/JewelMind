---
id: JM-BIBLE-432
title: Validation Versioning
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
  - JM-BIBLE-412
  - JM-BIBLE-433
  - JM-BIBLE-434
  - JM-BIBLE-103
  - JM-BIBLE-108
implementation_status: current
professional_validation: not_required
normative: false
---

# Validation Versioning

## A record attaches to an exact version, never to "the current rule"

`ValidationTarget.version` (`backend/jewelmind/professional_validation/schemas.py`)
is a required, non-optional `str` field, alongside the required `objectId`.
PROVAL-GOV-002 ([`410-validation-governance.md`](410-validation-governance.md))
states this directly: a record naming "the prong rule" with no version is
not a valid `ValidationRecord`. Every professional validation statement is
therefore scoped not just to an object but to one exact version of that
object — a `FORGE_RULE` at `version: "1.0.0"`, a `GEOMETRY_COMPONENT` at a
specific Atlas version, and so on (see the 11 `ValidationObjectType` values
in [`412-validation-object-model.md`](412-validation-object-model.md)).

## Consistent with Forge's own rule-versioning model

This Sprint's versioning model does not invent a new versioning philosophy
— it is the professional-validation-layer restatement of a rule already
established at the Forge layer,
[`06-forge/108-rule-versioning.md`](../06-forge/108-rule-versioning.md),
which this document must stay consistent with rather than contradict.
`108-rule-versioning.md` defines three levels of rule-version change:

| Level | Definition |
|---|---|
| PATCH | Message wording only, or a documentation/provenance-notes correction that changes no behavior. |
| MINOR | An additional, non-breaking applicability condition, or a newly-added `suggestedValue` that wasn't there before. |
| MAJOR | A changed threshold, severity, or blocking behavior — or a changed meaning of what the rule checks. |

And states the professional-validation consequence directly:

> A professional validation record ... applies to one exact `ruleVersion`.
> A MAJOR change to a validated rule invalidates that record; the rule
> reverts to its pre-validation confidence level until re-reviewed, unless
> the original reviewer explicitly extends acceptance to the new version.

[`06-forge/103-professional-validation-lifecycle.md`](../06-forge/103-professional-validation-lifecycle.md)
states the identical framing:

> A MAJOR change to a validated rule (changed threshold, severity, or
> blocking behavior) invalidates that specific validation record — the rule
> reverts to `preliminary` until re-reviewed at the new version, unless the
> reviewer explicitly extends their acceptance to the new version in a new
> record.

This document adopts that exact framing for the professional-validation
framework as a whole (not only Forge rules): **a MAJOR change to any
validated `ValidationTarget` — a Forge rule, a geometry component, a
manufacturing profile, or any of the other 11 object types — does not
automatically transfer validation to the new version.** A change that is
genuinely a PATCH or MINOR change under the same 3-level model may leave
validation applicable, but this is never assumed silently — see the impact
outcomes below.

## Three conceptual outcomes

A change to a validated object's implementation is classified into exactly
one of three outcomes:

| Outcome | Meaning |
|---|---|
| `VALIDATION_VERSION_UNCHANGED` | The change has no behavioral effect on the reviewed claim — validation remains applicable to the new version without further review. |
| `REVIEW_REQUIRED` | The change's behavioral impact is not yet clear enough to assume `VALIDATION_VERSION_UNCHANGED` — a human must confirm before the prior validation can be treated as still applicable. |
| `REVALIDATION_REQUIRED` | The change is a MAJOR change (per the table above) to a previously-validated claim — the prior `ValidationRecord` is invalidated and the target reverts to its pre-validation status until a new review occurs. |

These three outcomes are the actual outcome vocabulary
[`434-implementation-change-impact.md`](434-implementation-change-impact.md)'s
impact-analysis step classifies into.

## Real generated worked examples

`specs/professional-validation/v1/test-vectors/version-impact-vectors.json`
contains 4 real scenarios, already classified:

```json
{
  "vectors": [
    {
      "scenario": "documentation_wording_change_only",
      "changeType": "VALIDATION_VERSION_UNCHANGED",
      "description": "Only prose wording in a Bible doc changes; the rule's threshold/severity/blocking is untouched."
    },
    {
      "scenario": "minor_clarifying_code_comment",
      "changeType": "REVIEW_REQUIRED",
      "description": "A code comment or internal refactor changes with no behavioral difference — a human should confirm before assuming VALIDATION_VERSION_UNCHANGED."
    },
    {
      "scenario": "forge_rule_threshold_changed",
      "changeType": "REVALIDATION_REQUIRED",
      "description": "A MAJOR rule-version change per 108-rule-versioning.md (changed threshold/severity/blocking) invalidates any prior professional validation of that rule."
    },
    {
      "scenario": "prong_builder_algorithm_rewritten",
      "changeType": "REVALIDATION_REQUIRED",
      "description": "Existing professional validation of old prong geometry cannot automatically validate new generator output."
    }
  ]
}
```

Read together, these 4 vectors show the intended discipline precisely: a
pure documentation-wording change (`documentation_wording_change_only`) is
the *only* scenario that gets the fully-automatic `VALIDATION_VERSION_UNCHANGED`
outcome; even a change described as having "no behavioral difference"
(`minor_clarifying_code_comment`) still routes to `REVIEW_REQUIRED` rather
than being assumed safe, because a code-level change is harder to be
certain about than prose alone. Both a Forge threshold change and an
unrelated geometry-algorithm rewrite (`prong_builder_algorithm_rewritten`)
land on `REVALIDATION_REQUIRED` — the outcome is driven by whether the
underlying behavior actually changed for the validated claim, not by
whether the change happened inside `validation/engine.py` specifically.

## If only documentation wording changes

Consistent with the first vector above: if only documentation wording
changes with no behavioral difference, validation *may* remain applicable
— but only after a documented impact review reaches
`VALIDATION_VERSION_UNCHANGED` explicitly. This is never assumed silently
by the mere absence of a code diff; per the second vector
(`minor_clarifying_code_comment`), even a change that turns out to have no
behavioral difference is treated as `REVIEW_REQUIRED` until that is
actually confirmed, not `VALIDATION_VERSION_UNCHANGED` by default.

## A real function implements this classification

`backend/jewelmind/professional_validation/versioning.py::classify_version_impact(validated_version, current_version)`
is a real, tested function that computes one of the three outcomes above
from a pair of version strings: identical versions return
`VALIDATION_VERSION_UNCHANGED`; a differing MAJOR component returns
`REVALIDATION_REQUIRED`; any other difference (same MAJOR, different
MINOR/PATCH) returns `REVIEW_REQUIRED`. It deliberately only compares
version strings — it has no opinion on whether a specific change is
actually safe, and never assumes `VALIDATION_VERSION_UNCHANGED` merely
because two version numbers happen to match without the caller having
confirmed *why*. Tested by `backend/tests/test_professional_validation_versioning.py`
(6 tests, including a direct regression for
[`06-forge/103-professional-validation-lifecycle.md`](../06-forge/103-professional-validation-lifecycle.md)'s
own MAJOR-change rule). This function is the version-string half of the
classification only — it does not itself decide *whether* a given code
change constitutes a MAJOR/MINOR/PATCH change in the first place (that
judgment, and the surrounding CHANGE → impact-analysis → revalidation-queue
flow, is [`434-implementation-change-impact.md`](434-implementation-change-impact.md)'s
subject) — and the active registry still has zero records to actually
apply it to (see the README's "Current state: zero professional
validation"), so this function has not yet run against a real record.
