---
id: JM-BIBLE-433
title: Validation Expiration and Revalidation
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
  - JM-BIBLE-418
  - JM-BIBLE-432
  - JM-BIBLE-434
implementation_status: current
professional_validation: not_required
normative: false
---

# Validation Expiration and Revalidation

## `expirationOrReviewTrigger`: real, optional, never a blanket policy

`ValidationRecord.expirationOrReviewTrigger` (`str | None`,
`backend/jewelmind/professional_validation/schemas.py`) is a real,
optional field on every validation record. It is deliberately **not**
mandatory, and JewelMind does not force an arbitrary annual (or any other
fixed-interval) expiration on a validation record unless a specific
reviewer states a specific trigger for that specific record. This is
PROVAL-GOV-014 ([`410-validation-governance.md`](410-validation-governance.md)):
> Validation can expire. `ValidationRecord.expirationOrReviewTrigger` is a
> real, optional field ... never an arbitrary annual expiration unless a
> reviewer states one.

Expiration in this framework is therefore **per-record and
evidence-driven**, not a system-wide policy default. A record with
`expirationOrReviewTrigger: null` does not expire on any schedule — it
remains at its recorded `status` until something else (a MAJOR change to
the validated object, per
[`432-validation-versioning.md`](432-validation-versioning.md); or a real
trigger event, per below) causes it to need revisiting.

## The 9 real trigger scenarios

`specs/professional-validation/v1/test-vectors/expiration-vectors.json`
contains 9 real, already-generated trigger scenarios, each with a concrete
example string:

| Trigger | Example |
|---|---|
| `rule_semantic_change` | "JM-PRONG-003 threshold changed from 8mm to 7mm." |
| `geometry_algorithm_change` | "Prong builder rewritten to add a taper." |
| `new_material_added` | "A 6th metal option is added to MaterialSpec." |
| `new_manufacturing_process` | "A 3rd ManufacturingMethod value is added." |
| `new_stone_shape` | "Oval stones are added beyond the current round-only support." |
| `new_setting_system` | "Bezel or pave settings are added beyond prong-only." |
| `cad_kernel_major_change` | "OpenCascade major version upgrade changes geometry output." |
| `contradictory_field_evidence` | "A production failure contradicts a prior VALIDATED record." |
| `reviewer_imposed_expiration` | "Reviewer explicitly states 'revisit in 12 months'." |

These 9 triggers fall into three natural groups, though the schema does not
enforce this grouping structurally (`expirationOrReviewTrigger` is a single
free-text-shaped string field, not a closed enum):

1. **Implementation-change triggers** — `rule_semantic_change`,
   `geometry_algorithm_change`, `cad_kernel_major_change`. These overlap
   directly with the MAJOR-change concept in
   [`432-validation-versioning.md`](432-validation-versioning.md) and
   [`06-forge/108-rule-versioning.md`](../06-forge/108-rule-versioning.md)
   — a validated object's underlying behavior changed.
2. **New-capability triggers** — `new_material_added`,
   `new_manufacturing_process`, `new_stone_shape`, `new_setting_system`.
   These do not change the *validated* object's own behavior, but they
   expand the space of contexts a prior scope-limited record did not (and
   could not have) considered — see PROVAL-GOV-018
   ([`410-validation-governance.md`](410-validation-governance.md)) on a
   reviewed example never automatically validating combinations it never
   saw.
3. **Evidence-driven and reviewer-driven triggers** —
   `contradictory_field_evidence`, `reviewer_imposed_expiration`. These are
   the two triggers closest to "expiration" in the everyday sense: real
   contradicting evidence surfacing later, or a reviewer proactively naming
   a revisit condition (a date, a milestone, or any other real trigger) at
   review time.

## Only the reviewer names a trigger; the system does not invent one

The last row, `reviewer_imposed_expiration`, is the one case where a
recurring schedule appears at all — and even there, it exists only because
"Reviewer explicitly states 'revisit in 12 months'" is something a specific
named reviewer wrote into a specific record's
`expirationOrReviewTrigger` field, not because JewelMind applies a default
12-month (or any other) expiration window across the registry. There is no
code in `backend/jewelmind/professional_validation/` that computes a
default expiration date from `reviewDate`, and none should be added without
first updating this document and PROVAL-GOV-014 — doing so would silently
convert "per-record, evidence-driven" into "blanket policy," which is
exactly what PROVAL-GOV-014 rules out.

## Relationship to revalidation

A trigger firing (any of the 9 above) does not, by itself, delete or
downgrade a `ValidationRecord`'s `status` — no code path in
`backend/jewelmind/professional_validation/` currently automates that
transition (the active registry has zero records; see the README). What a
fired trigger conceptually does, per PROVAL-GOV-013 and
[`434-implementation-change-impact.md`](434-implementation-change-impact.md),
is place the affected object into the revalidation queue described there,
using the same `REVIEW_REQUIRED`/`REVALIDATION_REQUIRED` vocabulary defined
in [`432-validation-versioning.md`](432-validation-versioning.md).
