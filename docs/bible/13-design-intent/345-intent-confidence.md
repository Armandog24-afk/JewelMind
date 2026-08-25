---
id: JM-BIBLE-345
title: Intent Confidence
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-344
related_documents:
  - JM-BIBLE-346
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Confidence

## The 5-value enum

`IntentConfidence` (`backend/jewelmind/design_intent/schemas.py`):

`EXACT`, `HIGH_CONFIDENCE_NORMALIZATION`, `AMBIGUOUS`, `INFERRED`, `UNRESOLVED`.

## How `resolver.py` actually assigns it

`_resolve_statements()` in `resolver.py`:

```python
value, is_exact = normalize_descriptor(concept, raw.value)
...
confidenceClass="EXACT" if is_exact else "HIGH_CONFIDENCE_NORMALIZATION",
```

The assignment is a direct, mechanical function of `normalize_descriptor()`'s `is_exact` boolean, described fully in [`335-aesthetic-descriptor-model.md`](335-aesthetic-descriptor-model.md):

- `EXACT`: the raw text, uppercased, already equalled the canonical value on that concept's continuum — no synonym lookup was needed. E.g. the provider emitted the literal word `"DELICATE"` or `"delicate"` for a `VISUAL_WEIGHT` statement.
- `HIGH_CONFIDENCE_NORMALIZATION`: the raw text matched a synonym-table entry rather than the canonical token itself — e.g. `"delicato"` mapped to `DELICATE` via `VISUAL_WEIGHT.synonyms`.

`IntentRelation` has no `confidenceClass` field at all — confidence is only ever assigned to statements, not relations.

## The other 3 values are never emitted by current code

A repo-wide check of `confidenceClass=` inside `backend/jewelmind/design_intent/` shows exactly one call site (`resolver.py::_resolve_statements()`), producing only `EXACT` or `HIGH_CONFIDENCE_NORMALIZATION`. `AMBIGUOUS`, `INFERRED`, and `UNRESOLVED` are schema-defined `Literal` members with no producer anywhere in the pipeline:

- `AMBIGUOUS` would mark a descriptor that plausibly matched more than one concept category or value — current code has no such multi-match detection; a word either resolves cleanly against the one concept it was checked against, or it doesn't resolve at all (falling to `unresolvedDescriptors`, which carries no confidence class since the statement was never constructed).
- `INFERRED` would mark a value JewelMind guessed from surrounding context rather than a direct descriptor match — no inference logic exists; `normalize_descriptor()` only ever does exact/synonym table lookups, never fuzzy or contextual guessing.
- `UNRESOLVED` would mark a statement retained with unknown confidence — in practice, an unresolvable descriptor never becomes an `IntentStatement` at all in v1, so there is no partially-built statement that could carry this value; it goes to `unresolvedDescriptors` instead.

## No invented percentages anywhere

`IntentConfidence` is a small named enum, not a numeric score. Nothing in `design_intent/`, the Studio review UI, or the specs computes or displays a confidence percentage, a probability, or a certainty number for any statement. This follows the same "ordered/named categories, not invented numbers" principle documented for the vocabulary continua themselves — see [`338-style-continuum-model.md`](338-style-continuum-model.md).

## Where this is verified

`backend/tests/test_design_intent.py` exercises both real branches directly against `normalize_descriptor()`'s `is_exact` return value; `backend/tests/test_design_intent_corpus.py`'s `NORMALIZATION` category includes cases distinguishing exact-token input from synonym input.
