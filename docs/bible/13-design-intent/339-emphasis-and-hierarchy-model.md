---
id: JM-BIBLE-339
title: Emphasis And Hierarchy Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-338
related_documents:
  - JM-BIBLE-340
implementation_status: current
professional_validation: not_required
normative: true
---

# Emphasis And Hierarchy Model

## The `VISUAL_EMPHASIS` continuum

`UNDERSTATED` → `BALANCED` → `CENTER_FOCUSED` → `STATEMENT` (`backend/jewelmind/design_intent/vocabulary.py`). Real synonyms: `understated`/`discreto`/`discreta`/`sobrio`/`sobria` → `UNDERSTATED`, `balanced` → `BALANCED`, `statement`/`vistoso`/`vistosa` → `STATEMENT`. There is no synonym entry mapping directly to `CENTER_FOCUSED` in the current table — it exists as a valid continuum value a provider or a future synonym addition can target, but no current word resolves to it.

## Center-stone dominance is a relation, not a dedicated enum value

A request like "the stone should dominate the ring" is not expressed as a `VISUAL_EMPHASIS` value such as a hypothetical `CENTER_STONE_DOMINANT` — no such enum member exists anywhere in `design_intent/schemas.py`. It is expressed as an `IntentRelation(subject=STONE, predicate=DOMINANT_OVER, object=RING)`. This keeps the concept-category vocabulary about *how the whole piece reads* (`UNDERSTATED` vs `STATEMENT`) separate from *which named part dominates which other named part*, which is exactly what `IntentRelation` exists for — see [`336-relative-proportion-intent.md`](336-relative-proportion-intent.md).

## `VISUAL_HIERARCHY` target, not yet reachable by free text

`IntentTarget` includes `VISUAL_HIERARCHY` as a whole-piece descriptive label distinct from any single component — see [`334-intent-target-model.md`](334-intent-target-model.md). As of v1 no `TARGET_SYNONYMS` entry maps ordinary language to it, so a statement targeting `VISUAL_HIERARCHY` can currently only arrive if a provider emits the canonical token directly. It is reserved specifically for statements about how attention is distributed across a design as a whole, once multi-component designs make that distinction meaningful.

## More valuable as multi-component designs expand

Today's real assembly is a single solitaire (see [`../07-atlas/149-current-solitaire-geometry-mapping.md`](../07-atlas/149-current-solitaire-geometry-mapping.md)), so emphasis statements have limited room to matter — there is essentially one setting, one band, one stone, arranged in one fixed topology. `VISUAL_EMPHASIS` and relation predicates like `DOMINANT_OVER` are preserved now precisely because they generalize cleanly to a future multi-stone or multi-component design (e.g. a three-stone ring, where "the center stone should dominate the side stones" becomes a meaningful, distinguishable statement from today's degenerate single-stone case). Nothing in current code assumes or requires that future — the model is simply already shaped for it.

## Still never a numeric resolution

Restating the Sprint's core principle for this concept specifically: no `VISUAL_EMPHASIS` value or `DOMINANT_OVER`/`SUBORDINATE_TO` relation changes a stone diameter, a prong count, or a basket dimension in current code. Emphasis is preserved as structured intent, reviewed in Studio (see [`357-studio-intent-review.md`](357-studio-intent-review.md)), never auto-resolved.

## Relationship to `VISUAL_WEIGHT` and `SIMPLICITY`

A request can combine emphasis with weight or simplicity language in one sentence — "a bold, statement-making ring" plausibly yields both a `VISUAL_WEIGHT: BOLD` statement and a `VISUAL_EMPHASIS: STATEMENT` statement, on two independent concept categories. `conflicts.py` never compares across categories (see [`346-intent-conflict-model.md`](346-intent-conflict-model.md)), so these two statements coexist without interaction, exactly like any other pair of concepts attached to the same target.

