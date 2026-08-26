---
id: JM-BIBLE-449
title: Validation Evaluation Framework
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
  - JM-BIBLE-412
  - JM-BIBLE-445
  - JM-BIBLE-451
implementation_status: current
professional_validation: not_required
normative: false
---

# Validation Evaluation Framework

This document defines 11 conceptual metrics for tracking the health of
JewelMind's professional-validation effort over time. It is a
**conceptual framework**, not a dashboard that exists in the running
application — none of these metrics is computed anywhere in the frontend
today. For the 10 metrics computable from real code right now, this
document states the actual current value and the real function (or
honest absence of one) behind it. One metric is marked FUTURE and is not
computable from anything that exists today.

## Why a framework, not a score

None of these metrics is, or may ever become, a stand-in for a
`ValidationRecord`. A high `RULES_VALIDATED` count communicates real
progress; it never itself validates anything (PROVAL-GOV-001). These
metrics exist to make the state of the *effort* legible, not to replace
the review process the effort tracks.

## The 11 metrics

### 1. `RULES_AWAITING_REVIEW`

**Definition:** count of Forge rules whose `professionalValidationStatus`
is `preliminary` — rules that exist, run, and gate generation, but have
never been reviewed by a professional.

**Real current value: 16.** Verified directly against
`specs/forge/v1/current-rule-registry.json` (registryVersion `1.0.0`,
21 rules total; 16 `preliminary`, 5 `not_required`, 0 `validated`). No
dedicated function computes this today — it is a direct count over the
Forge registry file, not the professional-validation registry.

### 2. `RULES_VALIDATED`

**Definition:** count of Forge rules a `ValidationRecord` in the active
professional-validation registry marks `VALIDATED` or
`VALIDATED_WITH_CONDITIONS`.

**Real current value: 0.** Real function:
`registry.py::count_validated(load_active_registry())`. Because the
active registry has zero records of any `target.objectType`, this call
returns `0` today without needing any `FORGE_RULE`-specific filtering —
once real records exist, computing this metric specifically for Forge
rules would require filtering `count_validated()`'s input by
`target.objectType == "FORGE_RULE"` first, which no code does yet.

### 3. `RULES_REJECTED`

**Definition:** count of Forge rules with at least one `ValidationRecord`
whose `status` is `REJECTED`.

**Real current value: 0.** Real function:
`registry.py::count_by_status(records, "REJECTED")`, same
`FORGE_RULE`-filtering caveat as above. `0` today because the input list
is empty.

### 4. `CONDITIONAL_VALIDATIONS`

**Definition:** count of records across all object types (not only Forge
rules) with `status == "VALIDATED_WITH_CONDITIONS"`.

**Real current value: 0.** Real function:
`registry.py::count_by_status(records, "VALIDATED_WITH_CONDITIONS")`.

### 5. `GEOMETRY_FINDINGS`

**Definition:** count of recorded `ReviewObservation`s targeting geometry
(`category` values like `"basket_geometry"`, per
[`420-geometry-validation-process.md`](420-geometry-validation-process.md)).

**Real current value: 0 — but honestly, for a different reason than
metrics 2-4.** `ReviewObservation` is a real, fully-defined Pydantic
model in `schemas.py`, but **no active, loadable store for
`ReviewObservation` instances exists anywhere in this codebase**, unlike
`ValidationRecord`'s active registry file. There is no
`registry.py`-equivalent loader for observations, and no
`current-observations.json` or similar file. The value is `0` because
nothing has been persisted anywhere, not because a real counting function
ran against a real (empty) store and returned zero. This distinction
matters and should not be flattened into the same sentence as metrics
2-4 — see [`451-validation-gap-analysis.md`](451-validation-gap-analysis.md).

### 6. `CRITICAL_FINDINGS`

**Definition:** count of `ReviewObservation`s with `severity ==
"CRITICAL"`.

**Real current value: 0, same caveat as metric 5.** No persisted
observation store exists to count over.

### 7. `REVIEW_CASE_COVERAGE`

**Definition:** how many distinct, real `ReviewCase`s (per
[`412-validation-object-model.md`](412-validation-object-model.md)) have
actually been reviewed, as a fraction of some meaningful design-space
sample (see
[`441-review-sampling-strategy.md`](441-review-sampling-strategy.md) for
the sampling model this would draw on).

**Real current value: 0 real review cases.** `ReviewCase` instances exist
today only inside test code (e.g.
`backend/tests/test_professional_validation_versioning.py::TestReviewCaseReproducibility`,
which builds one from `default_definition()` purely to prove
reproducibility of `definitionHash`) and in
`specs/professional-validation/v1/examples/` — none of which represents
an actual professional review that occurred. There is no active,
loadable `ReviewCase` store, and no denominator ("total meaningful design
space") has been defined anywhere in code, so this metric cannot
currently be expressed even as `0 / N` — only as "zero reviewed cases."

### 8. `PROFESSIONAL_DISAGREEMENTS`

**Definition:** count of real `DisagreementRecord`s
(PROVAL-GOV-012, [`430-professional-disagreement-model.md`](430-professional-disagreement-model.md)).

**Real current value: 0, same caveat as metrics 5-7.** No active,
loadable `DisagreementRecord` store exists; the schema and its
preservation tests (`test_professional_validation_schemas.py::TestDisagreementPreservation`)
are real, but there is nowhere a real disagreement would currently be
recorded outside a test fixture.

### 9. `REVALIDATION_REQUIRED`

**Definition:** count of `ValidationRecord`s whose `status` is
`REVALIDATION_REQUIRED` — objects whose prior validation was invalidated
by a MAJOR implementation change (per
[`432-validation-versioning.md`](432-validation-versioning.md) and
[`434-implementation-change-impact.md`](434-implementation-change-impact.md)).

**Real current value: 0.** Real function:
`registry.py::count_by_status(records, "REVALIDATION_REQUIRED")` against
the active registry — `0` because the registry itself is empty, not
because the classification logic has never run: unlike metrics 5-8, the
classification function this metric depends on for *future* nonzero
values genuinely exists and is tested —
`backend/jewelmind/professional_validation/versioning.py::classify_version_impact(validated_version, current_version)`,
verified by `backend/tests/test_professional_validation_versioning.py`
(6 tests, including
`test_a_validated_rule_does_not_silently_carry_forward_after_a_major_change`).
This is a real building block toward eventually automating this metric's
future nonzero values, even though nothing currently invokes it against a
real code diff (see [`451-validation-gap-analysis.md`](451-validation-gap-analysis.md)).

### 10. `EXTERNAL_CAD_WORKFLOWS_TESTED`

**Definition:** count of distinct `(objectId, cadApplication)` pairs with
a real, recorded `ImportOutcome` (e.g. `IMPORT_SUCCESS`,
`EDITABLE_WITHOUT_REBUILD`) from an actual external CAD import test, per
[`424-cad-workflow-validation-process.md`](424-cad-workflow-validation-process.md).

**Real current value: 0, same caveat as metrics 5-8.** `ImportOutcome`
is a real `Literal` type in `schemas.py`; no code path anywhere records
an actual instance of one. FOUNDRY-GOV-014 already states the
governing rule this metric enforces: an `IMPORT_TESTED`/
`WORKFLOW_VALIDATED` claim requires an actual recorded test run, never an
assumed format compatibility — and as of this writing, zero such test
runs have been recorded.

### 11. FUTURE: `REVIEW_TO_IMPLEMENTATION_LEAD_TIME`

**Definition (proposed, not implemented):** elapsed time between a
`ReviewObservation`'s `blockingRecommendation: true` finding and a
corresponding Forge rule-version or geometry change landing in the
codebase, were the workflow in
[`435-validation-to-forge-workflow.md`](435-validation-to-forge-workflow.md)
(not yet written at the time of this document) ever fully instrumented
end to end.

**This metric is marked FUTURE deliberately.** No timestamped linkage
between a `ReviewObservation` and a resulting code change exists anywhere
in this codebase — there is no field on any model here that records "this
commit resolved that finding." Computing this metric would require new
data (a persisted observation store with resolution timestamps, per
metric 5's gap) that does not exist today; it is listed here as a
direction, not a current capability.

## Summary table

| Metric | Real current value | Real function today |
|---|---|---|
| `RULES_AWAITING_REVIEW` | 16 | none (direct count over Forge registry) |
| `RULES_VALIDATED` | 0 | `registry.py::count_validated()` |
| `RULES_REJECTED` | 0 | `registry.py::count_by_status(..., "REJECTED")` |
| `CONDITIONAL_VALIDATIONS` | 0 | `registry.py::count_by_status(..., "VALIDATED_WITH_CONDITIONS")` |
| `GEOMETRY_FINDINGS` | 0 | none — no observation store exists |
| `CRITICAL_FINDINGS` | 0 | none — no observation store exists |
| `REVIEW_CASE_COVERAGE` | 0 reviewed cases | none — no case store exists |
| `PROFESSIONAL_DISAGREEMENTS` | 0 | none — no disagreement store exists |
| `REVALIDATION_REQUIRED` | 0 | `registry.py::count_by_status(..., "REVALIDATION_REQUIRED")`, building on the real `versioning.py::classify_version_impact()` |
| `EXTERNAL_CAD_WORKFLOWS_TESTED` | 0 | none — no import-outcome store exists |
| `REVIEW_TO_IMPLEMENTATION_LEAD_TIME` | — | FUTURE — not implemented |

## Cross-references

- [`445-professional-validation-register.md`](445-professional-validation-register.md) — the register these registry-backed metrics read from.
- [`432-validation-versioning.md`](432-validation-versioning.md) — the classification vocabulary `REVALIDATION_REQUIRED` depends on.
- [`451-validation-gap-analysis.md`](451-validation-gap-analysis.md) — the absent persisted stores behind metrics 5-8 and 10, tracked as real gaps rather than repeated here per-metric.
