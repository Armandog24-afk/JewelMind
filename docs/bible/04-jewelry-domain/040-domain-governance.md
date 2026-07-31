---
id: JM-BIBLE-040
title: Domain Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-000
related_documents:
  - JM-BIBLE-DOMAIN-README
  - JM-BIBLE-054
  - JM-BIBLE-058
implementation_status: current
professional_validation: not_required
---

# Domain Governance

This document defines how jewelry-domain knowledge is admitted into
JewelMind, and how every statement in
[`04-jewelry-domain/`](README.md) must be classified. It extends
[`00-foundation/000-bible-governance.md`](../00-foundation/000-bible-governance.md)'s
CURRENT/PARTIAL/PLANNED/VISION rule with jewelry-specific categories,
because "is this implemented" and "is this professionally correct" are
two independent questions that rule alone does not separate.

## Classification of domain statements

Every domain statement in this section (a definition, a rule, a
parameter, a relationship) must be tagged with exactly one of the
following:

| Classification | Meaning | Who/what confirms it |
|---|---|---|
| **IMPLEMENTED FACT** | Directly supported by current code and at least one test. | A file path and a test name. |
| **PRELIMINARY SOFTWARE RULE** | Currently implemented for prototype safety, internal consistency, or a reasonable engineering guess — but not yet reviewed and accepted as a professional jewelry standard. | The code exists; no professional reviewer has signed off (see the register below). |
| **PROFESSIONALLY VALIDATED RULE** | Reviewed and accepted by an identified, named, qualified jewelry professional through the process in [`058-professional-validation-register.md`](058-professional-validation-register.md). | A completed register entry with reviewer name, role, date, and scope. |
| **PLANNED DOMAIN CONCEPT** | Not implemented; a concrete, near-term intention exists. | No implementation evidence required, but must not be described in present tense. |
| **VISION CONCEPT** | Not implemented; a long-term possibility. Must not influence current functionality without an ADR or (future) RFC. | Same as PLANNED, further out. |
| **UNKNOWN** | An unresolved question requiring research or professional consultation before it can be classified further. | Logged in [`057-open-domain-questions.md`](057-open-domain-questions.md). |

As of this Sprint, the count of PROFESSIONALLY VALIDATED RULEs in this
repository is **zero** — see
[`058-professional-validation-register.md`](058-professional-validation-register.md).
Every numeric validation rule currently in
`backend/jewelmind/validation/engine.py` is, at best, a PRELIMINARY
SOFTWARE RULE. This is stated here once, explicitly, so it does not need
restating with a caveat in every downstream document — but downstream
documents still tag each individual statement per the table above.

## Rules

1. **No undocumented professional assumptions.** A statement that reads
   as jewelry-industry knowledge (a tolerance, a proportion, a technique
   name) must carry its classification and, where applicable, its
   provenance (which file/constant it comes from).
2. **No invented measurements.** A number not present in the actual
   schema, geometry code, or an accepted register entry must not appear
   in a Bible document as if it were a real default or standard. Where a
   plausible future parameter needs illustrating, describe it without a
   numeric value, or explicitly mark the value as an example, not a
   default.
3. **Code does not automatically make a rule professionally correct.**
   Existence in `validation/engine.py` proves the rule is IMPLEMENTED. It
   never, by itself, proves PROFESSIONALLY VALIDATED.
4. **Preliminary rules must remain clearly labelled** — in this Bible,
   and (per the Constitution, see below) never described elsewhere as an
   industry standard.
5. **Professional validation must record reviewer role, date, and
   scope.** An entry in
   [`058-professional-validation-register.md`](058-professional-validation-register.md)
   without these three fields is incomplete and does not confer
   PROFESSIONALLY VALIDATED status.
6. **Conflicting professional opinions must be preserved, not silently
   merged.** If two reviewers disagree, the register keeps both entries
   with their own scope/date rather than averaging or picking a winner
   silently.
7. **Domain terminology must be consistent** across documentation, code,
   and UI. [`00-foundation/008-glossary.md`](../00-foundation/008-glossary.md)
   is the single glossary; every domain document links to it rather than
   redefining a term differently.
8. **Changes to core domain entities require an ADR or future RFC** — see
   [`056-domain-extension-strategy.md`](056-domain-extension-strategy.md)
   for the workflow and
   [`00-foundation/000-bible-governance.md`](../00-foundation/000-bible-governance.md)
   for when an ADR is required generally.
9. **Implementation status and professional-validation status are
   independent axes.** A concept can be `current` and
   `professional_validation: preliminary` at the same time (most of this
   repository today); a concept can also be `planned` and already have a
   `professional_validation: required` note attached, meaning it must not
   ship without review. Neither axis implies the other.

## Relationship to the Constitution

This governance model does not introduce new laws; it operationalizes
[LAW-010](../00-foundation/004-jewelmind-constitution.md#LAW-010) (no
manufacturing-readiness claims) and
[LAW-012](../00-foundation/004-jewelmind-constitution.md#LAW-012)
(current vs. planned vs. vision must stay distinct) specifically for
jewelry-domain content, where the risk of an implicit, unearned
professional claim is highest.

## Front matter field added this Sprint

Every document under `04-jewelry-domain/` (and the four new appendices)
adds one field beyond the Sprint 1 front matter:

```yaml
professional_validation: not_required | preliminary | required
```

- `not_required`: the document is structural/governance content with no
  jewelry-technical claims to validate (this document, for example).
- `preliminary`: the document contains PRELIMINARY SOFTWARE RULEs or
  IMPLEMENTED FACTs about current code; nothing in it has been
  professionally reviewed yet.
- `required`: the document describes a concept that must not be shipped,
  relied upon, or acted on without professional review first (typically
  PLANNED concepts flagged for expert input).
