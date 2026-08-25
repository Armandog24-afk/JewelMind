---
id: JM-BIBLE-338
title: Style Continuum Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-333
related_documents:
  - JM-BIBLE-339
implementation_status: current
professional_validation: not_required
normative: true
---

# Style Continuum Model

## Ordered categories, never numbers

Every one of the 6 concept categories in `backend/jewelmind/design_intent/vocabulary.py` is an ordered tuple of named values — never a millimeter, a percentage, or an invented 0–100 "style score." This is a foundational, cross-cutting rule for the whole Design Intent layer, not just a detail of any one concept:

| Category | Ordered continuum |
|---|---|
| `VISUAL_WEIGHT` | `DELICATE`, `LIGHT`, `BALANCED`, `SUBSTANTIAL`, `BOLD` |
| `SIMPLICITY` | `MINIMAL`, `CLEAN`, `BALANCED`, `DETAILED`, `ORNATE` |
| `STYLE_TEMPORALITY` | `CLASSIC`, `TIMELESS`, `CONTEMPORARY`, `MODERN` |
| `VISUAL_EMPHASIS` | `UNDERSTATED`, `BALANCED`, `CENTER_FOCUSED`, `STATEMENT` |
| `PROPORTIONAL_CHARACTER` | `SLIM`, `BALANCED`, `BROAD` |
| `STRUCTURAL_CHARACTER` | `SOFT`, `CLEAN`, `STRONG` |

## Why order matters even without numbers

An ordered tuple lets JewelMind measure *relative* distance between two named values without ever assigning either one a magnitude. `continuum_distance(concept, value_a, value_b)` (`vocabulary.py`) returns `abs(order.index(value_a) - order.index(value_b))` — an integer index distance, not a claim about how far apart the values are in any real physical or perceptual sense. `DELICATE` and `BOLD` on `VISUAL_WEIGHT` are 4 apart because they are the two ends of a 5-value list, not because JewelMind has measured that they differ by "4 units" of anything. This index distance is exactly what powers conflict detection (see [`346-intent-conflict-model.md`](346-intent-conflict-model.md)) and nothing else — it never feeds a geometry calculation.

## Why not a 0–100 score

A numeric score invites exactly the false precision this Sprint's core principle forbids: it would imply JewelMind can place "delicate" at, say, 12 and "bold" at 91, as if aesthetic intensity were measured on a calibrated instrument. A named, ordered value makes no such claim — it says "this is more X than that," never "this is X-ness 73." See INTENT-GOV-014: every concept category and value here is a JewelMind software taxonomy, not an assertion of universal aesthetic truth.

## Each concept category has its own continuum

Continua are not comparable across categories — `SIMPLICITY.MINIMAL` and `VISUAL_WEIGHT.DELICATE` are different concepts with different tables, even though a real piece might plausibly be both. `continuum_distance()` only ever compares two values within the same category (`_value_conflicts()` groups statements by `(target, concept)` before comparing). There is no cross-category ordering and none is claimed.

## Where each continuum is documented in depth

[`337-visual-weight-model.md`](337-visual-weight-model.md) (`VISUAL_WEIGHT`), [`339-emphasis-and-hierarchy-model.md`](339-emphasis-and-hierarchy-model.md) (`VISUAL_EMPHASIS`), [`341-simplicity-and-complexity-model.md`](341-simplicity-and-complexity-model.md) (`SIMPLICITY`), [`342-classic-contemporary-model.md`](342-classic-contemporary-model.md) (`STYLE_TEMPORALITY`). `PROPORTIONAL_CHARACTER` and `STRUCTURAL_CHARACTER` do not have dedicated docs of their own in this Sprint's reading order — they are covered here and in [`340-symmetry-and-balance-model.md`](340-symmetry-and-balance-model.md) (their shared `BALANCED` value) and [`336-relative-proportion-intent.md`](336-relative-proportion-intent.md) (relations that touch proportion).
