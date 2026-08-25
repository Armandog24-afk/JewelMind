---
id: JM-BIBLE-344
title: Intent Provenance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-332
related_documents:
  - JM-BIBLE-345
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Provenance

## The 8-value enum

`IntentProvenance` (`backend/jewelmind/design_intent/schemas.py`):

`USER_EXPLICIT`, `USER_CONTEXT`, `AI_NORMALIZED`, `SYSTEM_PROFILE`, `EXISTING_PROJECT`, `CLARIFICATION_RESPONSE`, `DERIVED_RELATION`, `UNRESOLVED`.

## Only `AI_NORMALIZED` is produced by current code

A repo-wide check of every `provenance=` assignment inside `backend/jewelmind/design_intent/` confirms exactly two call sites, both in `resolver.py` (`_resolve_statements()` and `_resolve_relations()`), and both hardcode `provenance="AI_NORMALIZED"`. No other value in the enum is ever assigned by real code. (Designer's own, separate `FieldProvenance` enum for technical fields, in `designer/service.py`, uses `"AI_INTERPRETATION"` — a similarly-named but distinct enum for a distinct channel; see [`303-field-provenance-model.md`](../12-designer/303-field-provenance-model.md).)

## What `AI_NORMALIZED` means — and does not mean

`AI_NORMALIZED` means: an AI provider recognized wording in the user's own request and normalized it into a canonical target/concept/value triple, deterministically re-validated by `normalizer.py` against the real controlled vocabulary. It does **not** mean the AI invented the intent, added a preference the user never expressed, or exercised any creative judgment about what the piece *should* be. The words being classified are still the user's own — "delicate," "minimal," "classic" came from the request text (`sourceText`), not from the model's imagination. `AI_NORMALIZED` is closer to "AI transcribed and classified" than "AI decided."

This distinction matters because INTENT-GOV-009 requires AI interpretation to remain non-authoritative — a provider recognizing that the user said "delicate" and mapping it to the canonical `DELICATE` token is a translation step, not an act of design authorship. JewelMind never asserts that the resulting statement reflects anything other than what the user themselves communicated.

## The other 7 values are schema-defined, not schema-fictional

Each remaining value has a clear, real future use that the current pipeline simply doesn't reach yet:

| Value | Intended future meaning |
|---|---|
| `USER_EXPLICIT` | A statement the user typed using the exact canonical vocabulary themselves, bypassing normalization entirely — not distinguished from a synonym-mapped one in v1. |
| `USER_CONTEXT` | Inferred from surrounding conversation rather than the sentence being classified — no multi-turn context model exists yet. |
| `SYSTEM_PROFILE` | Would come from a future `IntentProfile` default, not user language at all — no profile is registered (see [`355-intent-profile-model.md`](355-intent-profile-model.md)). |
| `EXISTING_PROJECT` | Would carry forward from a loaded/previous project's own stored intent, distinct from the current request's text. |
| `CLARIFICATION_RESPONSE` | Would mark a statement that arrived via an answered clarification question — mirrors the same, currently-unassigned gap Designer's own `FieldProvenance.CLARIFICATION_RESPONSE` has; see [`300-clarification-policy.md`](../12-designer/300-clarification-policy.md). |
| `DERIVED_RELATION` | Would mark a statement JewelMind itself derived from a relation rather than direct language — no such derivation logic exists. |
| `UNRESOLVED` | Would mark a statement whose provenance couldn't be determined — never needed since every current statement has a clear origin. |

None of these represent a broken promise; they represent a real enum shaped ahead of the mechanisms that would populate it, consistent with how `IntentResolution` and `IntentProfile` are also modeled ahead of their producers (see [`332-intent-domain-model.md`](332-intent-domain-model.md)).

## Where this is verified

Grep `backend/jewelmind/design_intent/resolver.py` for `provenance=` directly — both occurrences are literal `"AI_NORMALIZED"` strings, not a variable or a computed value, so there is no hidden branch that could produce anything else.
