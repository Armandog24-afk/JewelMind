---
id: JM-BIBLE-439
title: Reviewer Independence and Conflicts
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
  - JM-BIBLE-413
  - JM-BIBLE-414
implementation_status: current
professional_validation: not_required
normative: false
---

# Reviewer Independence and Conflicts

## A real field, not an aspiration

`specs/professional-validation/v1/reviewer.schema.json` defines a real `conflicts` field on the reviewer identity record, quoted directly:

> `"conflicts"`: "Disclosed potential conflicts (e.g. 'JewelMind contributor', 'vendor relationship') — recorded transparently, not a legal independence certification."

## Example conflict types

- contributor to JewelMind's own implementation (writes code, reviewing their own or a close colleague's work);
- a vendor relationship (e.g. a casting house that would benefit commercially from a favorable review);
- a commercial incentive of any other kind;
- review of one's own prior design (a reviewer asked to evaluate geometry they themselves proposed earlier).

None of these automatically disqualifies a review. They are disclosed, not hidden, so a reader of the review can weigh it accordingly.

## No legal independence certification is implied

Recording `conflicts` is a transparency mechanism, not a legal or professional-ethics certification process. JewelMind does not claim, and this document does not imply, that a disclosed-conflict-free reviewer is thereby "independent" in any formal or auditable sense beyond "they told us what they know about their own relationship to this review."

## Direct reinforcement of PROVAL-GOV-005

**PROVAL-GOV-005**: *"A software developer cannot self-certify jewelry-domain validity merely by implementing the system."* This document is the practical mechanism behind that rule — a developer who also acts as a reviewer must disclose that fact in their own `conflicts` field, and any future review-package tooling or registry query should surface it plainly rather than let it disappear into an otherwise-normal-looking `ValidationRecord`.

## Cross-references

- [`410-validation-governance.md`](410-validation-governance.md) — PROVAL-GOV-005.
- [`414-reviewer-qualification-model.md`](414-reviewer-qualification-model.md) — the reviewer's fit-for-review profile, a separate concept from conflicts.
- `specs/professional-validation/v1/reviewer.schema.json` — the real schema.
