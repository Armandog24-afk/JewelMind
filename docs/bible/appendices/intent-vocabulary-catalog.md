---
id: JM-BIBLE-A64
title: "Appendix: Intent Vocabulary Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-DESIGN-INTENT-README
  - JM-BIBLE-330
related_documents:
  - JM-BIBLE-333
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Intent Vocabulary Catalog

The 6 real `ConceptCategory` entries from `backend/jewelmind/design_intent/vocabulary.py`'s `CATEGORIES` dict, mirrored verbatim in `specs/design-intent/v1/vocabulary.json` (`version: "1.0.0"`). Each category is an **ordered continuum** (never a numeric score) — see `docs/bible/13-design-intent/338-style-continuum-model.md`. A word may appear in more than one category's synonym table (e.g. "clean" is both `SIMPLICITY` and `STRUCTURAL_CHARACTER`); the caller (a provider, re-validated deterministically) decides which category a given statement targets.

| Concept category | Ordered continuum values | Sample IT/EN synonyms per value |
|---|---|---|
| `VISUAL_WEIGHT` | `DELICATE` -> `LIGHT` -> `BALANCED` -> `SUBSTANTIAL` -> `BOLD` | `DELICATE`: "delicato"/"delicata"/"fine"; `LIGHT`: "leggero"/"lightweight-looking"; `BALANCED`: "bilanciato"/"balanced"; `SUBSTANTIAL`: "sostanzioso"/"substantial"; `BOLD`: "audace"/"bold" |
| `SIMPLICITY` | `MINIMAL` -> `CLEAN` -> `BALANCED` -> `DETAILED` -> `ORNATE` | `MINIMAL`: "minimalista"/"minimal"; `CLEAN`: "pulito"/"semplice"/"simple"; `DETAILED`: "dettagliato"/"detailed"; `ORNATE`: "elaborato"/"ornate" |
| `STYLE_TEMPORALITY` | `CLASSIC` -> `TIMELESS` -> `CONTEMPORARY` -> `MODERN` | `CLASSIC`: "classico"/"classic"; `TIMELESS`: "timeless" (no IT synonym registered); `CONTEMPORARY`: "contemporaneo"/"contemporary"; `MODERN`: "moderno"/"modern" |
| `VISUAL_EMPHASIS` | `UNDERSTATED` -> `BALANCED` -> `CENTER_FOCUSED` -> `STATEMENT` | `UNDERSTATED`: "discreto"/"sobrio"/"understated"; `CENTER_FOCUSED`: no direct synonym entry (only reachable as an exact canonical token, see note below); `STATEMENT`: "vistoso"/"statement" |
| `PROPORTIONAL_CHARACTER` | `SLIM` -> `BALANCED` -> `BROAD` | `SLIM`: "sottile"/"narrow"/"snella"; `BALANCED`: "balanced" (no IT synonym registered); `BROAD`: "largo"/"ampio"/"broad" |
| `STRUCTURAL_CHARACTER` | `SOFT` -> `CLEAN` -> `STRONG` | `SOFT`: "morbido"/"soft"; `CLEAN`: "pulito"/"clean"; `STRONG`: "robusto"/"solido"/"strong" |

## Notes grounded in the real code

- `CENTER_FOCUSED` (`VISUAL_EMPHASIS`) has no entry in `VISUAL_EMPHASIS.synonyms` at all — it can currently only be reached if a provider (or a test, see `test_design_intent_corpus.py::rel-04`) submits the exact canonical token `"center_focused"`/`"CENTER_FOCUSED"`, which `normalize_descriptor()`'s exact-match branch accepts case-insensitively. Any lowercase free-text synonym for it would fall through to `unresolvedDescriptors`.
- `TIMELESS` (`STYLE_TEMPORALITY`) and `BALANCED` (`PROPORTIONAL_CHARACTER`) likewise have no Italian synonym registered — only their English/canonical spelling resolves them today.
- `BALANCED` appears as a value in four categories (`VISUAL_WEIGHT`, `SIMPLICITY`, `VISUAL_EMPHASIS`, `PROPORTIONAL_CHARACTER`) but is a genuinely distinct value per category — `normalize_descriptor()` always scopes the lookup to the single `concept` the statement targets, never across categories.
- "Deliberately excluded" words are not a bug: `backend/tests/test_design_intent.py::TestNormalizeDescriptor::test_ambiguous_word_deliberately_excluded` verifies Italian "importante" resolves to `None` on purpose (it can mean either "substantial" or "eye-catching" depending on context) — see `vocabulary.py`'s module docstring.
