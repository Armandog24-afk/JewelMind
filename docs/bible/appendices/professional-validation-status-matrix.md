---
id: JM-BIBLE-A86
title: "Appendix: Professional Validation Status Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-443
  - JM-BIBLE-445
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Professional Validation Status Matrix

Every one of the 21 real rules in `specs/forge/v1/current-rule-registry.json`, its real `professionalValidationStatus` field (`preliminary` or `not_required` — there is no third value in that registry), and the equivalent `ValidationStatus` vocabulary from `backend/jewelmind/professional_validation/schemas.py` this Sprint introduces. **The active professional-validation registry (`specs/professional-validation/v1/current-validation-registry.json`) contains zero `ValidationRecord`s** — every `ValidationStatus` value below is the honest default/mapping, never a claim that a review has occurred.

## Why the mapping exists, and its limit

`professionalValidationStatus` (Forge's own field, Sprint 4) and `ValidationStatus` (this Sprint's field) are two distinct vocabularies for two distinct systems (see [`450-current-code-mapping.md`](../15-professional-validation/450-current-code-mapping.md)'s "three different things named Validation" table). There is no code anywhere that mechanically converts one into the other — this table is a **documentation-level correspondence**, drawn by a human/agent reading both registries side by side, not a computed join.

| Rule ID | Classification | `professionalValidationStatus` (Forge) | Equivalent `ValidationStatus` |
|---|---|---|---|
| JM-RING-001 | PROTOTYPE_HEURISTIC | preliminary | `NOT_REVIEWED` |
| JM-RING-002 | PROTOTYPE_HEURISTIC | preliminary | `NOT_REVIEWED` |
| JM-RING-003 | SEMANTIC_COMPATIBILITY | preliminary | `NOT_REVIEWED` |
| JM-BAND-001 | PROTOTYPE_HEURISTIC | preliminary | `NOT_REVIEWED` |
| JM-BAND-002 | PROTOTYPE_HEURISTIC | preliminary | `NOT_REVIEWED` |
| JM-BAND-003 | PROTOTYPE_HEURISTIC | preliminary | `NOT_REVIEWED` |
| JM-STONE-001 | PROTOTYPE_HEURISTIC | preliminary | `NOT_REVIEWED` |
| JM-STONE-002 | DOMAIN_INVARIANT | preliminary | `NOT_REVIEWED` |
| JM-PRONG-001 | PROTOTYPE_HEURISTIC | preliminary | `NOT_REVIEWED` |
| JM-PRONG-002 | PROTOTYPE_HEURISTIC | preliminary | `NOT_REVIEWED` |
| JM-PRONG-003 | PROTOTYPE_HEURISTIC | preliminary | `NOT_REVIEWED` |
| JM-PRONG-004 | SEMANTIC_COMPATIBILITY | preliminary | `NOT_REVIEWED` |
| JM-SETTING-001 | GEOMETRY_PRECONDITION | preliminary | `NOT_REVIEWED` |
| JM-SETTING-002 | PROTOTYPE_HEURISTIC | preliminary | `NOT_REVIEWED` |
| JM-MANUFACTURING-001 | MANUFACTURING_CONTEXT | preliminary | `NOT_REVIEWED` |
| JM-GEOMETRY-001 | GEOMETRY_PRECONDITION | preliminary | `NOT_REVIEWED` |
| FORGE-SCHEMA-001 | SCHEMA_INTEGRITY | not_required | n/a (see below) |
| FORGE-SAFETY-001 | SYSTEM_SAFETY | not_required | n/a (see below) |
| FORGE-SAFETY-002 | SYSTEM_SAFETY | not_required | n/a (see below) |
| FORGE-GEOM-001 | GEOMETRY_INSPECTION | not_required | n/a (see below) |
| FORGE-EXPORT-001 | EXPORT_PRECONDITION | not_required | n/a (see below) |

**16 preliminary → `NOT_REVIEWED`. 5 not_required → no meaningful `ValidationStatus` mapping.**

## Why every `preliminary` rule maps to `NOT_REVIEWED`, not something more specific

A `preliminary` rule is one whose `professionalValidationStatus` field states a professional review is expected eventually but has not happened. Because the active registry holds zero `ValidationRecord`s, no `ValidationTarget.currentValidationStatus` for any of these 16 rules has ever been set to anything other than its schema default, `"NOT_REVIEWED"` — not `REVIEW_PLANNED`, not `UNDER_REVIEW`. No rule in this codebase has been assigned to a reviewer or scheduled yet (see [`443-current-preliminary-rule-review-plan.md`](../15-professional-validation/443-current-preliminary-rule-review-plan.md) for the plan that would move a rule to `REVIEW_PLANNED`).

## Why `not_required` rules have no meaningful `ValidationStatus` mapping

The 5 `not_required` rules (`FORGE-SCHEMA-001`, `FORGE-SAFETY-001`, `FORGE-SAFETY-002`, `FORGE-GEOM-001`, `FORGE-EXPORT-001`) are software-integrity/safety/precondition checks — a schema-version literal, non-finite-float rejection, extra-field rejection, a fused-solid topology check, and an export-precondition check (see [`443-current-preliminary-rule-review-plan.md`](../15-professional-validation/443-current-preliminary-rule-review-plan.md)'s "Rules NOT needing professional review" table for the full rationale per rule). None of these is a jewelry-domain judgment call a `ReviewerRole` would evaluate — there is no professional review process this framework offers that applies to "is the JDL schema-version literal correct," so mapping them to `NOT_REVIEWED` would misleadingly imply a review is pending. They are correctly outside the scope of `ValidationStatus` entirely, not merely unreviewed within it.

## Cross-references

- [`443-current-preliminary-rule-review-plan.md`](../15-professional-validation/443-current-preliminary-rule-review-plan.md) — reviewer role, priority, evidence type, and boundary case per preliminary rule; compact table version in [`professional-rule-review-matrix.md`](professional-rule-review-matrix.md) (`JM-BIBLE-A87`).
- [`445-professional-validation-register.md`](../15-professional-validation/445-professional-validation-register.md) — where a resulting `ValidationRecord` would eventually live.
- `specs/forge/v1/current-rule-registry.json` — the source of every `professionalValidationStatus` value in this table.
