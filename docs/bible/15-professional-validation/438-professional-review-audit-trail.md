---
id: JM-BIBLE-438
title: Professional Review Audit Trail
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
  - JM-BIBLE-445
implementation_status: current
professional_validation: not_required
normative: false
---

# Professional Review Audit Trail

## What must be recorded and permanently retained

For every professional review outcome: who reviewed (`reviewerId`), the exact version reviewed (`ValidationTarget.version`), the evidence relied on (`evidenceIds`), the findings (`ReviewObservation`s), the decision (`ValidationDecision`/`ValidationRecord`), any implementation consequences, later revisions, and — critically — any record a later one superseded.

## Rejected and obsolete records are never deleted

`ValidationStatus` includes `SUPERSEDED` as a first-class, real value (`backend/jewelmind/professional_validation/schemas.py`) precisely so an outdated or superseded record can be marked rather than removed. This directly restates:

- **PROVAL-GOV-011** — rejected findings remain in the audit history;
- **PROVAL-GOV-019** — professional review records must be auditable.

`ValidationRecord.supersedesRecordId` lets a new record name exactly which prior record it replaces, without deleting the prior one — the old record stays queryable, still shows its own real `reviewerId`/`evidenceIds`/`rationale`, and its `status` field is what changes, never its content.

## An honest scope limit: no database, no cryptographic tamper-evidence yet

The active registry (`specs/professional-validation/v1/current-validation-registry.json`) is, as of this Sprint, a single JSON file with no append-only log, no database transaction history, and no cryptographic signing or tamper-evidence mechanism. The audit-trail *guarantee* this Sprint provides is a **process and data-model guarantee** — the fields exist, and the discipline of "never delete, only supersede" is documented and testable (`backend/tests/test_professional_validation_registry.py`) — but nothing currently prevents a person with file-system access from hand-editing the JSON file directly, bypassing `validate-review-record` entirely. This is a real, named gap, not a claimed technical guarantee — see [`452-open-professional-validation-questions.md`](452-open-professional-validation-questions.md)'s question about cryptographic signing, and [`451-validation-gap-analysis.md`](451-validation-gap-analysis.md).

## Cross-references

- [`410-validation-governance.md`](410-validation-governance.md) — PROVAL-GOV-011 and PROVAL-GOV-019 in full.
- [`432-validation-versioning.md`](432-validation-versioning.md) — how a version change interacts with an existing record's status.
- [`445-professional-validation-register.md`](445-professional-validation-register.md) — the actual registry this document's guarantees apply to.
