---
id: JM-BIBLE-101
title: Conflicts, Precedence, and Resolution
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-100
related_documents: []
implementation_status: planned
professional_validation: not_required
normative: true
---

# Conflicts, Precedence, and Resolution

**The current implementation has no conflict-resolution mechanism, because no two current rules actually conflict.** `specs/forge/v1/test-vectors/precedence-vectors.json` documents every conceptual conflict type below against the real codebase and finds each either non-existent today or trivially non-conflicting (independent co-firing, not disagreement). This document defines the conceptual model for when a real conflict eventually can arise — it is PLANNED as an active resolution mechanism, though the precedence *ordering* below is a normative decision for when that day comes.

## Conflict types

| Type | Currently exists? |
|---|---|
| Same field, different threshold | No — every field has exactly one active rule per condition today |
| Different severity for the same condition | No — see `JM-BAND-002`/`JM-PRONG-002` in [`099`](099-severity-and-blocking-semantics.md): one rule, two branches, not two rules |
| Material-specific override | No — `material.metal` has zero validation rules |
| Manufacturing-specific override | Partially — `JM-MANUFACTURING-001` *adds* a resin-specific warning alongside generic band rules; it does not *override* them (see the co-firing example in `precedence-vectors.json`) |
| Geographic-profile difference | No — no geographic scoping exists anywhere in the current rule set |
| Professional reviewer disagreement | No — zero professional reviews have occurred |
| Experimental vs. accepted rule | No — every current rule is `lifecycleState: ACCEPTED` |
| Deprecated vs. active rule | No — no rule has ever been deprecated |

## Precedence ordering (conceptual, for future conflicts)

1. **System integrity** (`SCHEMA_INTEGRITY`, `SYSTEM_SAFETY`) — always wins; a structurally invalid document is invalid regardless of any domain rule's opinion.
2. **Accepted professional-scoped rule** (`PROFESSIONALLY_VALIDATED`, scoped to the relevant material/manufacturing/geographic context) — wins over any non-professionally-validated rule *within its declared scope only*.
3. **Accepted domain rule** (`DOMAIN_INVARIANT`, `SEMANTIC_COMPATIBILITY`, `GEOMETRY_PRECONDITION`) — wins over prototype heuristics.
4. **Preliminary prototype heuristic** (`PROTOTYPE_HEURISTIC`).
5. **Experimental rule** (`lifecycleState: EXPERIMENTAL`) — lowest precedence; per [`095-rule-lifecycle.md`](095-rule-lifecycle.md), an experimental rule never gains blocking authority regardless of this ordering.

## Critical caveat: professional scope must matter

**A casting rule must not automatically override a resin-printing context, and vice versa.** Precedence level 2 above is explicitly scoped — a professionally-validated rule for `lost_wax_casting` has no precedence claim whatsoever over a `direct_resin_printing` document; it simply does not apply there (see `applicableManufacturingMethods` in [`092-rule-anatomy.md`](092-rule-anatomy.md)). Precedence only matters *among rules that actually apply to the same context* — it is not a mechanism for one manufacturing profile to silently dominate another.

## Never silently discard conflicting expert opinions

If two qualified professionals ever disagree about the same rule (a real future scenario this document anticipates, not a current one), [`04-jewelry-domain/040-domain-governance.md`](../04-jewelry-domain/040-domain-governance.md) rule 6 already establishes the precedent this Sprint extends to Forge: **both entries are preserved in [`103-professional-validation-lifecycle.md`](103-professional-validation-lifecycle.md)'s validation register, with their own scope and date, never averaged or silently resolved to one winner.** Precedence in that case is a scope question ("which reviewer's stated scope actually covers this document"), not a popularity or seniority question.
