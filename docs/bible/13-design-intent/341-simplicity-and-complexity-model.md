---
id: JM-BIBLE-341
title: Simplicity And Complexity Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-338
related_documents:
  - JM-BIBLE-342
implementation_status: current
professional_validation: not_required
normative: true
---

# Simplicity And Complexity Model

## The continuum

`SIMPLICITY` (`backend/jewelmind/design_intent/vocabulary.py`):

`MINIMAL` → `CLEAN` → `BALANCED` → `DETAILED` → `ORNATE`

Real synonyms: `minimal`/`minimalista` → `MINIMAL`; `clean`/`pulito`/`pulita`/`simple`/`semplice` → `CLEAN`; `balanced`/`bilanciato`/`bilanciata` → `BALANCED`; `detailed`/`dettagliato`/`dettagliata` → `DETAILED`; `ornate`/`elaborato`/`elaborata` → `ORNATE`.

## Never equated with component count

A technically complex model — more construction steps, more assembled solids in Atlas's manifest, a basket with several supporting elements — may still appear visually minimal, and a technically simple model can appear visually busy. `SIMPLICITY` records the user's stated aesthetic impression, not a count of anything Atlas's manifest reports. No code in `backend/jewelmind/design_intent/` inspects a definition's component count, solid count, or construction complexity to infer or validate a `SIMPLICITY` value. The concept is populated exclusively from language, the same as every other continuum — see [`335-aesthetic-descriptor-model.md`](335-aesthetic-descriptor-model.md).

## `CLEAN` sits on two different continua

`"clean"` is a real synonym in both `SIMPLICITY` (mapping to `CLEAN`) and `STRUCTURAL_CHARACTER` (also mapping to its own `CLEAN` value). These are two different canonical values that happen to share a name — `SIMPLICITY.CLEAN` describes visual complexity ("not ornate, not overly plain either"), while `STRUCTURAL_CHARACTER.CLEAN` describes structural character ("not soft, not overtly strong-looking either"). Which one a given occurrence of the word "clean" resolves to depends entirely on which `concept` the provider attaches to the raw statement before `normalize_descriptor()` runs — the normalizer itself has no opinion and performs no disambiguation of its own; see [`335-aesthetic-descriptor-model.md`](335-aesthetic-descriptor-model.md) for why that split of responsibility is deliberate.

## Still never a numeric resolution

As with every concept category, a `SIMPLICITY` statement resolves to `resolutionStatus: PRESERVED`, never to a change in prong count, basket presence, or any other structural JDL field, in v1. `relatedJDLPaths` remains empty. See [`330-intent-governance.md`](330-intent-governance.md) INTENT-GOV-001 and the corpus's dedicated `NO_ARBITRARY_NUMERIC_MAPPING` test category in `backend/tests/test_design_intent_corpus.py`, which includes cases specifically phrased around minimal/ornate language.

## Relationship to `STYLE_TEMPORALITY`

"Minimal" and "classic" are not the same claim, even though they can co-occur — `SIMPLICITY` and `STYLE_TEMPORALITY` are separate concept categories with separate continua (see [`338-style-continuum-model.md`](338-style-continuum-model.md)). A request for "a minimal, classic solitaire" produces two independent statements, `SIMPLICITY: MINIMAL` and `STYLE_TEMPORALITY: CLASSIC`, both `PRESERVED`, with no code anywhere treating one as implying the other.

