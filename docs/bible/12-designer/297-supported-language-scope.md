---
id: JM-BIBLE-297
title: Supported Language Scope
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-296
related_documents:
  - JM-BIBLE-298
implementation_status: current
professional_validation: not_required
normative: true
---

# Supported Language Scope

## Italian and English, and only those

Designer supports exactly two natural languages: Italian and English. This isn't a soft claim — it's a direct consequence of what actually has coverage:

- `backend/jewelmind/designer/normalizer.py`'s synonym tables (`METAL_SYNONYMS`, `BAND_PROFILE_SYNONYMS`, `STONE_SHAPE_SYNONYMS`, `SETTING_TYPE_SYNONYMS`, `MANUFACTURING_SYNONYMS`, `PRONG_COUNT_WORDS`) hand-author IT/EN tokens only (e.g. `"oro giallo"`, `"yellow gold"` both map to `"yellow_gold_18k"`; `"sei"`, `"six"` both map to prong count 6).
- `backend/tests/test_designer_corpus.py`'s `MULTILINGUAL` category and its Italian-language cases throughout the other 10 categories are the only real-language test evidence that exists.
- `NaturalLanguageDesignRequest.locale` is typed `Literal["it", "en"] | None` — no third value is even structurally possible without a schema change.

Any other language is not rejected outright, but has zero normalizer coverage: a real provider might still extract structured values from, say, French text (an LLM's underlying language capability isn't gated), but any enum synonym specific to French input has no deterministic mapping and behaves the same as an unrecognized token — an `UnsupportedFeature` or, for a truly novel term, silent absence from `proposedCanonicalValues`.

## `locale` is a hint, not a gate

`request.locale` is never checked against the request text, never used to pick a different normalizer table, and never used to reject a request. `prompts.py::build_user_message()` includes it only as an annotation for a real provider: `f"USER REQUEST{locale_note}:\n{text}"`. The deterministic normalization tables in `normalizer.py` are locale-agnostic dictionaries checked against lower-cased tokens regardless of what `locale` says.

## Multilingual convergence

Regardless of which supported language a request uses, every canonical output value is the same enum member. `"oro giallo"` and `"yellow gold"` both normalize to `"yellow_gold_18k"`; `"sei"` and `"six"` both normalize to prong count `6`. `test_designer_corpus.py`'s `MULTILINGUAL` category exists specifically to assert this convergence — a design described in Italian and the same design described in English must produce an identical `candidateJDL` for the fields they both specify.

## Why not more languages yet

Adding a third language means writing and testing a full synonym table plus a meaningful slice of the natural-language corpus in that language — not a trivial addition, and not scoped for Sprint 10. See [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md) for this listed as a real, deferred gap rather than an oversight.

See [`298-defaulting-policy.md`](298-defaulting-policy.md) for what happens to a field no language, supported or not, ever specifies.
