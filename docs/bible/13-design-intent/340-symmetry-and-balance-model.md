---
id: JM-BIBLE-340
title: Symmetry And Balance Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-338
related_documents:
  - JM-BIBLE-341
implementation_status: current
professional_validation: not_required
normative: true
---

# Symmetry And Balance Model

## `BALANCED` appears in three continua

`BALANCED` is a real value in three of the 6 concept categories:

| Category | Position of `BALANCED` |
|---|---|
| `VISUAL_WEIGHT` | Middle of `DELICATE`…`BOLD` |
| `SIMPLICITY` | Middle of `MINIMAL`…`ORNATE` |
| `PROPORTIONAL_CHARACTER` | Middle of `SLIM`…`BROAD` |

(`VISUAL_EMPHASIS` also has a `BALANCED` value, between `UNDERSTATED` and `CENTER_FOCUSED`/`STATEMENT` — see [`339-emphasis-and-hierarchy-model.md`](339-emphasis-and-hierarchy-model.md).) In every case it means the same structural thing: the midpoint of that specific continuum, a real synonym target (`"balanced"`/`"bilanciato"`/`"bilanciata"`), nothing more.

## Geometric symmetry is not the same claim as aesthetic balance

This is the one caution this doc exists to make explicit. JewelMind's current solitaire assembly has real, inherent rotational symmetry — the band is a body of revolution, the prong arrangement is evenly spaced (see [`../07-atlas/123-coordinate-system-and-orientation.md`](../07-atlas/123-coordinate-system-and-orientation.md)). That is a geometric fact Atlas can compute directly from the B-Rep. It is a completely different claim from a `VISUAL_WEIGHT: BALANCED` or `SIMPLICITY: BALANCED` intent statement, which records what the *user said or implied* about how the piece should read aesthetically.

No code in `backend/jewelmind/design_intent/` inspects a `JewelryDefinition`'s actual geometric symmetry and emits a `BALANCED` statement on its behalf. The `BALANCED` value only ever arrives the same way every other intent value does — through a raw statement resolved by `normalize_descriptor()` from something the user actually said. A structurally symmetric ring generated from a request that never mentioned balance carries no `BALANCED` intent statement at all; Design Intent never infers one just because the geometry happens to be even.

## Why this distinction matters

Conflating the two would violate the same boundary Atlas and Forge already respect for geometric facts versus domain-rule interpretations (see [`../07-atlas/README.md`](../07-atlas/README.md), ATLAS-GOV-001/002): a geometric property is a fact about the shape; an aesthetic descriptor is a claim about how a person experiences that shape. Design Intent's job is to preserve the second kind of claim faithfully, never to manufacture one from the first.

## No dedicated symmetry concept exists

There is no `SYMMETRY` entry in `IntentConceptCategory` and no plan to add one without an RFC (see [`362-design-intent-gap-analysis.md`](362-design-intent-gap-analysis.md) and `docs/bible/06-forge/090-forge-governance.md`'s analogous RFC requirement for new rule families, echoed here by [`330-intent-governance.md`](330-intent-governance.md)'s "When an RFC is required" section). If a future Sprint wants JewelMind to reason about geometric symmetry as a jewelry-domain concept, that belongs in Forge/Atlas, not in this subjective-language layer.
