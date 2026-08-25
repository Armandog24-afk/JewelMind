---
id: JM-BIBLE-342
title: Classic Contemporary Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-338
related_documents:
  - JM-BIBLE-343
implementation_status: current
professional_validation: not_required
normative: true
---

# Classic Contemporary Model

## The continuum

`STYLE_TEMPORALITY` (`backend/jewelmind/design_intent/vocabulary.py`):

`CLASSIC` → `TIMELESS` → `CONTEMPORARY` → `MODERN`

Real synonyms: `classic`/`classico`/`classica` → `CLASSIC`; `timeless` → `TIMELESS` (no Italian synonym is registered for it in current code); `contemporary`/`contemporaneo`/`contemporanea` → `CONTEMPORARY`; `modern`/`moderno`/`moderna` → `MODERN`.

## No technical geometry is universally "classic" or "modern"

This is the explicit caution for this concept: no code anywhere claims that a specific band profile, prong count, or setting type *is* classic or *is* modern in some absolute sense. `STYLE_TEMPORALITY` records what a user's language asserts about the intended feel of the piece — it is never used, in either direction, as a fact about JewelMind's own catalog of supported geometry values (`docs/bible/07-atlas/README.md`'s component catalog carries no temporality labels, and nothing in `design_intent/` reads it if it did).

## v1 only preserves, never resolves, this concept

A statement like "I want a classic solitaire" resolves to `IntentStatement(target=RING, concept=STYLE_TEMPORALITY, value=CLASSIC, resolutionStatus=PRESERVED)` and nothing further happens automatically. There is no deterministic rule anywhere that says `CLASSIC` implies, say, a round brilliant stone shape or a particular band profile — `relatedJDLPaths` stays empty, exactly as for every other concept (INTENT-GOV-001). If the user also wants a specific band profile or stone shape, that is a separate, explicit technical statement in Designer's own channel (`proposedFields`), resolved through the ordinary JDL/Forge pipeline — Design Intent contributes nothing to that resolution.

## Why this restraint matters here specifically

"Classic" and "modern" are unusually tempting concepts to over-resolve, because a designer might reasonably associate them with concrete choices (e.g. a classic build might lean toward simpler band profiles). JewelMind deliberately does not encode that association anywhere in v1 — doing so would require a professionally-reviewed, versioned mapping under `IntentProfile` (see [`349-deterministic-resolution-policy.md`](349-deterministic-resolution-policy.md) and [`355-intent-profile-model.md`](355-intent-profile-model.md)), and no such profile exists. Treating `STYLE_TEMPORALITY` as purely descriptive, with zero implied technical consequence, is the safe default until (and unless) such a profile is deliberately built and reviewed.

## Relationship to other continua

`STYLE_TEMPORALITY` is orthogonal to `SIMPLICITY` and `VISUAL_WEIGHT` — a request can combine "classic and minimal" or "modern and bold" as two independent statements on two independent concept categories, both preserved side by side with no cross-concept interaction in current code. See [`338-style-continuum-model.md`](338-style-continuum-model.md) for the full table.
