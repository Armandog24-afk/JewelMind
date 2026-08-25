---
id: JM-BIBLE-335
title: Aesthetic Descriptor Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-334
related_documents:
  - JM-BIBLE-336
implementation_status: current
professional_validation: not_required
normative: true
---

# Aesthetic Descriptor Model

## `normalize_descriptor()`'s exact contract

```python
def normalize_descriptor(concept: str, raw_value: str) -> tuple[str | None, bool]
```

(`backend/jewelmind/design_intent/normalizer.py`). Two-step check against one already-identified concept category:

1. If `concept` isn't a key in `CATEGORIES` (`vocabulary.py`), returns `(None, False)` immediately — an unknown concept can never resolve a value.
2. Otherwise, uppercase the raw text and check it against that category's `order` tuple directly — if it's already the canonical value, returns `(value, True)` (`is_exact=True`, no synonym lookup needed).
3. Otherwise, lowercase the raw text and look it up in that category's `synonyms` dict — returns `(value, False)` on a hit, or `(None, False)` if the word isn't in that category's table at all.

## The concept is the caller's job, not the normalizer's

This is the load-bearing design decision of this whole layer: `normalize_descriptor()` never guesses which of the 6 concept categories a bare word belongs to. It only validates a raw value against the ONE category it was already told to check. The provider (an LLM, seeing the full sentence) decides, e.g., that "delicate" in a given sentence is a `VISUAL_WEIGHT` descriptor rather than a `STRUCTURAL_CHARACTER` one; `normalize_descriptor("VISUAL_WEIGHT", "delicate")` then deterministically re-validates that classification against the real table. If the provider's chosen category and the word don't actually match a real entry, the result is `(None, False)`, not a fallback guess into a different category.

This separation keeps the deterministic half of the pipeline testable in total isolation from any AI provider — `backend/tests/test_design_intent.py` exercises `normalize_descriptor()` directly with plain Python strings, no provider involved.

## What happens on a miss

In `resolver.py::_resolve_statements()`, a `(None, ...)` result routes the whole raw statement to `unresolvedDescriptors` (keyed by `sourceText` or, failing that, the raw value) plus an `INTENT_UNKNOWN_DESCRIPTOR` diagnostic at `"info"` severity — never a hard error, never silently dropped (INTENT-GOV-006). The same happens one step earlier if the target itself doesn't resolve, or if the claimed concept string isn't a member of `KNOWN_CONCEPTS` at all.

## Why ambiguous words are excluded, not guessed

See [`333-intent-vocabulary.md`](333-intent-vocabulary.md) for the concrete `"importante"` example. The design principle generalizes: a synonym table entry is a permanent, reviewable claim ("this word means this canonical value"), so it is only added for words whose meaning is stable enough to commit to across contexts. A word whose real-world meaning depends on the rest of the sentence is deliberately left out — the cost of excluding it is an occasional unresolved descriptor a human reviews; the cost of guessing it would be a wrong classification presented with false confidence.

## Confidence is a direct function of this contract

`resolver.py` sets `confidenceClass="EXACT"` when `is_exact` is `True` and `"HIGH_CONFIDENCE_NORMALIZATION"` otherwise — see [`345-intent-confidence.md`](345-intent-confidence.md) for the full enum and why the other 3 values are never emitted by current code.
