---
id: JM-BIBLE-299
title: Ambiguity Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-298
related_documents:
  - JM-BIBLE-300
implementation_status: current
professional_validation: not_required
normative: true
---

# Ambiguity Model

## The 3-level `AmbiguityLevel` enum

`backend/jewelmind/designer/schemas.py::AmbiguityLevel`:

| Value | Meaning as used in code |
|---|---|
| `LOW_IMPACT_AMBIGUITY` | Declared in the schema; not currently assigned by any pipeline code path today — reserved for a future case where an ambiguity has negligible design consequence. |
| `HIGH_IMPACT_AMBIGUITY` | The deterministic backstop (`AMBIGUOUS_METAL_TERMS`) and any provider-reported ambiguity (`RawAmbiguity`) for a **known** field path. |
| `UNSUPPORTED_AMBIGUITY` | A provider-reported ambiguity for a field path Designer doesn't recognize, or a `RawClarification` with no `options`. |

`service.py::_build_proposal()` assigns the level for provider-reported ambiguities directly from whether the field is known: `"HIGH_IMPACT_AMBIGUITY" if capability.is_known_field(amb.field) else "UNSUPPORTED_AMBIGUITY"`.

## Two independent sources of ambiguity

1. **Deterministic backstop**: `normalizer.AMBIGUOUS_METAL_TERMS = frozenset({"gold", "oro"})`. If a `RawProposedValue` for `material.metal` normalizes to one of these bare tokens, `normalize_enum_token()` returns `(None, is_ambiguous=True)` regardless of what the provider itself thought — this check runs even if the provider never flagged the term as ambiguous itself.
2. **Provider-reported**: `RawAmbiguity{field, sourceText, candidateValues}` — a provider can proactively report that a term maps to more than one supported value, listing the candidates it considered.

Both paths converge on the same `ClarificationQuestion` shape, so the review UI treats them identically — there is no visible distinction between "JewelMind's own code caught this" and "the provider flagged this."

## Why bare "gold" is ambiguous, not defaulted

`"gold"`/`"oro"` names a real, recognized concept — the user clearly means a gold alloy — but JewelMind supports three gold colors (`yellow_gold_18k`, `white_gold_18k`, `rose_gold_18k`) with no schema-level "default gold." Silently picking one would be an invented preference, forbidden by [`298-defaulting-policy.md`](298-defaulting-policy.md); the only honest response is a `ClarificationQuestion` offering the three real options. This is DESIGNER-GOV-013 verbatim.

## Ambiguity vs. unsupported vs. clarification, in one place

These three concepts overlap in the code and are easy to conflate:

| Concept | Trigger | Doc |
|---|---|---|
| Ambiguity | A term names more than one supported value | This document |
| Unsupported feature | A term names zero supported values (a genuinely missing capability) | [`301-unsupported-request-handling.md`](301-unsupported-request-handling.md) |
| Clarification question | The **user-facing artifact** produced for an ambiguity (always) or an unsupported feature with a worthwhile alternative (sometimes) | [`300-clarification-policy.md`](300-clarification-policy.md) |

Every ambiguity becomes a clarification question; not every unsupported feature does.

See [`300-clarification-policy.md`](300-clarification-policy.md) for exactly when a clarification is warranted.
