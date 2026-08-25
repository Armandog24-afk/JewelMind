---
id: JM-BIBLE-337
title: Visual Weight Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-333
related_documents:
  - JM-BIBLE-338
implementation_status: current
professional_validation: not_required
normative: true
---

# Visual Weight Model

## The continuum

`VISUAL_WEIGHT` (`backend/jewelmind/design_intent/vocabulary.py`), one of the 6 `IntentConceptCategory` values:

`DELICATE` → `LIGHT` → `BALANCED` → `SUBSTANTIAL` → `BOLD`

Real synonyms include `delicate`/`delicato`/`delicata`/`fine` → `DELICATE`, `light`/`leggero`/`leggera`/`lightweight-looking` → `LIGHT`, `balanced`/`bilanciato`/`bilanciata` → `BALANCED`, `substantial`/`sostanzioso`/`sostanziosa` → `SUBSTANTIAL`, `bold`/`audace` → `BOLD`.

## Never equated with mass, width, thickness, or volume

This is the single most important caution about this concept: no code anywhere converts a `VISUAL_WEIGHT` statement into `band.width`, `band.thickness`, a computed volume, or any other measured quantity. `IntentStatement.relatedJDLPaths` is always empty for a `VISUAL_WEIGHT` statement, same as for every other concept — this is verified directly by `backend/tests/test_designer_intent_integration.py::TestNoArbitraryNumericMapping.test_bolder_never_increases_band_width_stone_diameter_or_prong_diameter`, which proves that a statement carrying `BOLD` never causes `band.width`, `stone.diameter`, or `setting.prongDiameter` to increase.

## Semantic intent, not a computed judgment

A `VISUAL_WEIGHT` statement records what the user said or implied about how the piece should read visually — it is not JewelMind's own computed assessment of an existing design's actual mass. There is no reverse direction in v1 either: nothing inspects a `JewelryDefinition`'s real dimensions and emits a `VISUAL_WEIGHT` statement describing them. The concept only flows from language into a preserved statement, never the other way.

## A future profile might use it — none does yet

A later `IntentProfile` (see [`355-intent-profile-model.md`](355-intent-profile-model.md)) could plausibly map `DELICATE` to a coordinated adjustment across several parameters at once (band width, prong diameter, basket presence) rather than any single field — that is the kind of mapping the profile mechanism exists for. But `IntentProfile.jdlMapping` is an empty dict everywhere in the current codebase; no such profile is registered, reviewed, or even drafted. Until one is, `VISUAL_WEIGHT` statements exist purely as `resolutionStatus: PRESERVED` structured metadata.

## Relationship to `PROPORTIONAL_CHARACTER` and `STRUCTURAL_CHARACTER`

`VISUAL_WEIGHT` is not the only continuum that can sound like it's describing size. `PROPORTIONAL_CHARACTER` (`SLIM`/`BALANCED`/`BROAD`) and `STRUCTURAL_CHARACTER` (`SOFT`/`CLEAN`/`STRONG`) are separate concept categories with their own tables — a provider picks whichever one the sentence actually supports, and all three remain equally unresolved to geometry in v1. See [`338-style-continuum-model.md`](338-style-continuum-model.md) for the full table of all 6 continua side by side.
