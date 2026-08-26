---
id: JM-BIBLE-434
title: Implementation Change Impact
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
  - JM-BIBLE-432
  - JM-BIBLE-433
  - JM-BIBLE-108
implementation_status: current
professional_validation: not_required
normative: false
---

# Implementation Change Impact

## PROVAL-GOV-013

Changes to validated semantics trigger impact analysis. This document
defines the flow
([`410-validation-governance.md`](410-validation-governance.md),
PROVAL-GOV-013): CHANGE → affected validated objects → impact analysis →
status downgrade if necessary → revalidation queue.

## The flow

```mermaid
flowchart TD
    CH["CHANGE\n(code, geometry algorithm, Forge rule,\nCAD kernel, schema)"]
    FIND["Find affected validated objects\n(registry.py: match target.objectId/version\nagainst every ValidationRecord)"]
    NONE{"Any ValidationRecord\ntargets this object?"}
    NOOP["No professional-validation impact\n(implementation change proceeds normally\nthrough its own review/test process)"]
    IMPACT["Impact analysis\n(classify per 432-validation-versioning.md)"]
    UNCHANGED["VALIDATION_VERSION_UNCHANGED\nrecord stays VALIDATED /\nVALIDATED_WITH_CONDITIONS"]
    REVIEW["REVIEW_REQUIRED\na human confirms before\nassuming no impact"]
    REVAL["REVALIDATION_REQUIRED\n(MAJOR change per\n06-forge/108-rule-versioning.md)"]
    DOWNGRADE["Status downgrade\nrecord.status -> REVALIDATION_REQUIRED\ntarget reverts to pre-validation\nconfidence level"]
    QUEUE["Revalidation queue\n(443-current-preliminary-rule-review-plan.md /\n444-current-solitaire-review-plan.md)"]

    CH --> FIND --> NONE
    NONE -- no --> NOOP
    NONE -- yes --> IMPACT
    IMPACT --> UNCHANGED
    IMPACT --> REVIEW
    IMPACT --> REVAL
    REVAL --> DOWNGRADE --> QUEUE
    REVIEW -->|confirmed no behavioral change| UNCHANGED
    REVIEW -->|confirmed behavioral change| REVAL
```

## Worked example from the original Sprint brief

> Prong-builder algorithm changes substantially. Existing professional
> validation of old prong geometry cannot automatically validate new
> output.

Walking this through the flow above: the CHANGE is a substantial rewrite of
`backend/jewelmind/geometry/components/prongs.py` (a
`geometry_algorithm_change` trigger, per
[`433-validation-expiration-and-revalidation.md`](433-validation-expiration-and-revalidation.md)).
Finding affected validated objects means checking every `ValidationRecord`
in the active registry whose `target.objectType` is
`GEOMETRY_COMPONENT`/`GEOMETRY_RELATIONSHIP`/`COMPLETE_MODEL` and whose
`target.objectId` names the prong component or anything downstream of it
(a basket/prong relationship, a complete solitaire model). Impact analysis
classifies the change: a substantial algorithm rewrite is exactly the
`prong_builder_algorithm_rewritten` scenario already present, generated,
and classified `REVALIDATION_REQUIRED` in
`specs/professional-validation/v1/test-vectors/version-impact-vectors.json`
(see [`432-validation-versioning.md`](432-validation-versioning.md)) —
because the new generator output is not the same geometry the original
reviewer actually looked at, no amount of similarity to the old algorithm
lets the prior record's `VALIDATED`/`VALIDATED_WITH_CONDITIONS` status carry
forward automatically. Every affected record's `status` would be downgraded
toward `REVALIDATION_REQUIRED`, and the affected object(s) would enter the
revalidation queue for a new review against the new algorithm's actual
output.

## This flow has never executed for a real record

Stated plainly, not glossed over: **the active validation registry
(`specs/professional-validation/v1/current-validation-registry.json`)
currently contains zero records** (verified by
`backend/tests/test_professional_validation_registry.py::TestZeroValidationDefault::test_count_validated_on_the_real_registry_is_zero`,
cited in the README's "Current state: zero professional validation"
section). Because there are zero validated objects, the "find affected
validated objects" step of this flow has never, in the real history of this
codebase, actually found a nonempty result — every implementation change
made so far, including substantial ones, has taken the `NOOP` branch of the
diagram above by simple virtue of there being nothing in the registry to
affect. There is also no automated code in
`backend/jewelmind/professional_validation/` today that runs this flow
against a real code diff; the flow is a conceptual model plus the real
classification vocabulary from
[`432-validation-versioning.md`](432-validation-versioning.md), not a
CI-integrated check.

This absence of execution history is itself worth stating directly, rather
than treating the diagram above as proven-in-production: this document
describes a model that is **ready** for the moment JewelMind's registry
holds its first real `VALIDATED`/`VALIDATED_WITH_CONDITIONS` record and a
subsequent implementation change touches that record's target — at that
point, and only at that point, this flow will run for real for the first
time. Until then, PROVAL-GOV-013's flow remains correctly documented,
not-yet-executed infrastructure, exactly as
[`410-validation-governance.md`](410-validation-governance.md) already
states: "currently zero validated objects exist, so this flow has never yet
had to run, but the model exists ready for when it must."
