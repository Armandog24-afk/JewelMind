---
id: JM-BIBLE-102
title: Suggestions and Auto-Fix Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-098
related_documents: []
implementation_status: partial
professional_validation: not_required
normative: true
---

# Suggestions and Auto-Fix Contract

## Four distinct concepts

| Concept | Meaning | Current status |
|---|---|---|
| **DIAGNOSTIC** | A rule result reporting that a condition fired | CURRENT — every `ValidationResult` |
| **SUGGESTION** | A `suggestedValue` attached to a diagnostic | CURRENT — 7 of the 16 `JM-*` rules carry one in at least one of their branches (`JM-RING-003`, `JM-BAND-001`, `JM-BAND-002`, `JM-PRONG-001`, `JM-PRONG-002`, `JM-PRONG-003`, `JM-MANUFACTURING-001`), confirmed by inspecting `backend/jewelmind/validation/engine.py` directly |
| **AUTO-FIX PROPOSAL** | A machine-generated, not-yet-applied change the user could accept | NOT IMPLEMENTED — the frontend never offers a one-click "apply this fix" action today; a suggested value is display-only |
| **APPLIED FIX** | A change actually written back into the definition | NOT IMPLEMENTED |

**The current product supports only DIAGNOSTIC and SUGGESTION.** Nothing in this codebase automatically modifies a `JewelryDefinition`.

## Future auto-fix contract (PLANNED, not built)

Any future auto-fix implementation must:

1. Be deterministic — the same diagnostic always proposes the same fix.
2. Show what will change before applying it (a diff-like preview, not a silent write).
3. Identify the rule responsible for the proposal.
4. Preserve an audit record — which rule, which old value, which new value, when, and (if relevant) who confirmed it.
5. Never silently modify geometry-driving parameters — every one of the 16 current `JM-*` rules' `suggestedValue`s targets a geometry-driving field (`band.width`, `stone diameter` bounds, `prongCount`, etc.); applying any of them without explicit confirmation would violate FORGE-GOV-015.
6. Be reversible.
7. Require explicit user confirmation, **unless** classified as `SAFE_NORMALIZATION` — a category reserved for changes that cannot alter jewelry-domain meaning at all (e.g. trimming trailing whitespace from `project.name`). No current rule has `autoFixCapability: SAFE_NORMALIZATION`; every current `suggestedValue` is `SUGGEST_ONLY` at most, per `specs/forge/v1/rule.schema.json`.

## Why automatic jewelry-design correction is explicitly not implemented now

Per this Sprint's governing instruction, no automatic correction is implemented. This is also consistent with FORGE-GOV-015 (rules must not silently mutate user intent) and with the broader product principle that a suggested value is advice from a preliminary software rule, not a professionally-endorsed correction — auto-applying it would misrepresent a `PROTOTYPE_HEURISTIC` suggestion as more authoritative than it is.
