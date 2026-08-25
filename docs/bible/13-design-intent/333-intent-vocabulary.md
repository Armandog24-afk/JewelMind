---
id: JM-BIBLE-333
title: Intent Vocabulary
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-332
related_documents:
  - JM-BIBLE-334
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Vocabulary

## Six concept categories, six ordered continua

`backend/jewelmind/design_intent/vocabulary.py` defines exactly 6 `IntentConceptCategory` values (`design_intent/schemas.py`'s `IntentConceptCategory` enum), each a `ConceptCategory(order, synonyms)` NamedTuple:

| Category | Ordered continuum (`order`) |
|---|---|
| `VISUAL_WEIGHT` | `DELICATE`, `LIGHT`, `BALANCED`, `SUBSTANTIAL`, `BOLD` |
| `SIMPLICITY` | `MINIMAL`, `CLEAN`, `BALANCED`, `DETAILED`, `ORNATE` |
| `STYLE_TEMPORALITY` | `CLASSIC`, `TIMELESS`, `CONTEMPORARY`, `MODERN` |
| `VISUAL_EMPHASIS` | `UNDERSTATED`, `BALANCED`, `CENTER_FOCUSED`, `STATEMENT` |
| `PROPORTIONAL_CHARACTER` | `SLIM`, `BALANCED`, `BROAD` |
| `STRUCTURAL_CHARACTER` | `SOFT`, `CLEAN`, `STRONG` |

The order is not decorative — `continuum_distance()` (see [`346-intent-conflict-model.md`](346-intent-conflict-model.md)) uses each tuple's index positions to measure how far apart two values are, which is the real mechanism that distinguishes an adjacent nuance ("light" vs "balanced") from an outright contradiction ("delicate" vs "bold"). See [`338-style-continuum-model.md`](338-style-continuum-model.md) for the full cross-cutting rationale of ordered-continuum-not-number.

## Controlled, not exhaustive

Each category's `synonyms` dict maps a closed set of real IT/EN words to one canonical value. This is a deliberate, small, controlled vocabulary — not an attempt to classify every adjective a user might type. A word can legitimately belong to more than one category's table (`"clean"` is both a `SIMPLICITY` and a `STRUCTURAL_CHARACTER` synonym); which category a raw word is checked against is decided by the provider, with full sentence context, before `normalize_descriptor()` ever runs — see [`335-aesthetic-descriptor-model.md`](335-aesthetic-descriptor-model.md).

## Deliberately excluded words

Genuinely ambiguous words are left out of every table rather than guessed. The real, documented example is Italian `"importante"`, which can mean either "substantial" (`VISUAL_WEIGHT`) or "eye-catching" (`VISUAL_EMPHASIS`) depending on context — it appears in neither synonym table. A statement using it falls through `normalize_descriptor()` returning `(None, False)`, so `resolver.py` routes it to `DesignIntent.unresolvedDescriptors` with an `INTENT_UNKNOWN_DESCRIPTOR` diagnostic instead of silently picking one meaning. This is the concrete mechanism behind INTENT-GOV-006.

## Multilingual by canonical convergence, not by locale

`VISUAL_WEIGHT`'s table maps `"delicate"`, `"delicato"`, and `"delicata"` all to the single canonical value `DELICATE` — Italian and English words that mean the same aesthetic idea converge on one language-neutral token (INTENT-GOV-013). There is no separate "Italian vocabulary" or "English vocabulary"; it is one table per concept, with multiple input spellings per canonical value. The `MULTILINGUAL` category of `backend/tests/test_design_intent_corpus.py` exercises this convergence directly.

## Targets are a separate table

`TARGET_SYNONYMS` (also in `vocabulary.py`) is the analogous mapping for the 10 `IntentTarget` values — see [`334-intent-target-model.md`](334-intent-target-model.md).

## Versioning

`DesignIntent.version` (`"1.0.0"`) exists precisely so a future vocabulary change is a documented version bump, not a silent edit (INTENT-GOV-012). `specs/design-intent/v1/vocabulary.json` is the machine-readable mirror of this same table, generated from real code — see [`../../../specs/design-intent/v1/README.md`](../../../specs/design-intent/v1/README.md).
