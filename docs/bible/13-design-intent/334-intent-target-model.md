---
id: JM-BIBLE-334
title: Intent Target Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-333
related_documents:
  - JM-BIBLE-335
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Target Model

## The 10 canonical targets

`IntentTarget` (`backend/jewelmind/design_intent/schemas.py`) is a `Literal` of exactly 10 values, mirrored as `KNOWN_TARGETS` in `normalizer.py`:

`JEWELRY_PRODUCT`, `RING`, `BAND`, `STONE`, `SETTING`, `PRONGS`, `BASKET`, `MATERIAL_APPEARANCE`, `OVERALL_PROPORTION`, `VISUAL_HIERARCHY`.

## `TARGET_SYNONYMS`

`vocabulary.py`'s `TARGET_SYNONYMS` maps a controlled set of real IT/EN words to 7 of the 10 targets:

| Canonical target | Real synonyms |
|---|---|
| `RING` | `ring`, `anello`, `whole ring`, `overall` |
| `BAND` | `band`, `fascia` |
| `STONE` | `stone`, `pietra`, `diamond`, `diamante` |
| `SETTING` | `setting`, `castone` |
| `PRONGS` | `prongs`, `griffe` |
| `BASKET` | `basket` |
| `JEWELRY_PRODUCT` | `jewelry`, `gioiello`, `product` |

`normalize_target()` (`normalizer.py`) first checks whether the raw text, uppercased, is already one of the 10 canonical `KNOWN_TARGETS` — that covers a provider emitting the canonical token directly — and only falls back to `TARGET_SYNONYMS` (lowercased lookup) if not.

## Three targets with no synonym entry

`MATERIAL_APPEARANCE`, `OVERALL_PROPORTION`, and `VISUAL_HIERARCHY` appear in `KNOWN_TARGETS` (so a provider emitting the canonical string itself resolves correctly) but have no entry in `TARGET_SYNONYMS` — no free-text word maps to them today. They exist as whole-piece descriptive labels for future statements about the overall design rather than a single geometric component (e.g. "the piece should read as one cohesive statement" would conceptually target `VISUAL_HIERARCHY`, not any single part), but no current normalizer path routes ordinary language to them. This is a real, honest gap, not a hidden feature — see [`362-design-intent-gap-analysis.md`](362-design-intent-gap-analysis.md).

## Target support reflects the current solitaire domain

All 10 targets are valid semantic labels a statement's `target` field can legally hold — the schema does not scope them to "whatever the solitaire currently has." `PRONGS` and `BASKET` are recognized targets regardless of whether a given `JewelryDefinition` even includes a basket component. This mirrors the same distinction Atlas draws between a component existing in the schema and a component being geometrically present for a specific definition — see [`../07-atlas/149-current-solitaire-geometry-mapping.md`](../07-atlas/149-current-solitaire-geometry-mapping.md). A target being recognized never implies it maps to an adjustable geometry parameter today; see [`336-relative-proportion-intent.md`](336-relative-proportion-intent.md) and [`347-intent-compatibility-model.md`](347-intent-compatibility-model.md) for why recognition and technical resolution are different claims.

## Unrecognized target text

If neither the direct-canonical check nor `TARGET_SYNONYMS` resolves a raw target string, `normalize_target()` returns `None`, and `resolver.py` routes the whole statement to `unresolvedDescriptors` with an `INTENT_UNKNOWN_DESCRIPTOR` diagnostic — the same path as an unresolvable descriptor value (see [`335-aesthetic-descriptor-model.md`](335-aesthetic-descriptor-model.md)). A statement is only ever fully discarded if both its target and its descriptor value are unrecognized-and-unpreserved, which never happens in real code: an unrecognized target alone is enough to preserve the whole statement's source text.
