---
id: JM-BIBLE-336
title: Relative Proportion Intent
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-332
related_documents:
  - JM-BIBLE-337
implementation_status: current
professional_validation: not_required
normative: true
---

# Relative Proportion Intent

## `IntentRelation`, not a dimension

Some requests describe how two parts of the piece should relate to each other, not an absolute property of either one. `IntentRelation` (see [`332-intent-domain-model.md`](332-intent-domain-model.md)) exists for exactly this: `{subject: IntentTarget, predicate: RelationPredicate, object: IntentTarget}`. It never carries a value from a concept continuum, and it never resolves to a number — a relation stays a relationship between two targets, full stop.

## The 6 real predicates

`RelationPredicate` (`schemas.py`), mirrored by `KNOWN_PREDICATES` in `normalizer.py`:

| Predicate | Meaning |
|---|---|
| `NARROWER_THAN` | Subject reads as narrower than object. |
| `BROADER_THAN` | Subject reads as broader than object. |
| `DOMINANT_OVER` | Subject reads as visually dominant over object. |
| `SUBORDINATE_TO` | Subject reads as visually subordinate to object. |
| `DISCREET_RELATIVE_TO` | Subject should stay understated next to object. |
| `BALANCED_WITH` | Subject and object should read as evenly weighted. |

`normalize_predicate()` accepts either the canonical uppercase token directly or a small `PREDICATE_SYNONYMS` table of literal phrasings (`"narrower than"`, `"should dominate"`, etc.) — deliberately small and literal, per the same "controlled, not guessed" principle as descriptor synonyms (see [`335-aesthetic-descriptor-model.md`](335-aesthetic-descriptor-model.md)). An unrecognized phrasing resolves to `None` and the whole relation is preserved as an unresolved descriptor with an `INTENT_INVALID_RELATION` diagnostic, never guessed into the nearest predicate.

## A real corpus example

From `backend/tests/test_design_intent_corpus.py`'s `RELATION` category: "the band should look slim compared with the stone" resolves to `IntentRelation(subject=BAND, predicate=NARROWER_THAN, object=STONE)`. Nothing about this relation says the band is 1.4mm or the stone is 6mm — it asserts an ordering between two targets, preserved exactly as a relationship.

## `DOMINANT_OVER`/`SUBORDINATE_TO` express emphasis, not a dedicated enum value

A request like "the stone should dominate the ring" is expressed as `IntentRelation(subject=STONE, predicate=DOMINANT_OVER, object=RING)` rather than as a special `CENTER_STONE_DOMINANT` value on some enum — there is no such enum member anywhere in `design_intent/schemas.py`. See [`339-emphasis-and-hierarchy-model.md`](339-emphasis-and-hierarchy-model.md) for why relations, not a growing list of special-case concept values, are the chosen mechanism for this kind of statement.

## Conflict detection over relations

Two relations sharing the same `(subject, object)` pair with opposite predicates (`DOMINANT_OVER`/`SUBORDINATE_TO`, `NARROWER_THAN`/`BROADER_THAN`) produce a `TARGET_CONFLICT` — see [`346-intent-conflict-model.md`](346-intent-conflict-model.md) for the full algorithm, implemented in `conflicts.py::_relation_conflicts()`.

## Never absolute dimensions

Restating INTENT-GOV-001 for this specific model: no code path converts an `IntentRelation` into a numeric JDL comparison, a percentage, or a ratio. `relatedJDLPaths` does not even exist on `IntentRelation` (only `IntentStatement` has that field, and it is always empty in v1). A relation is preserved with `resolutionStatus: PRESERVED`, exactly like a statement — it never becomes `band.width < stone.diameter` as an enforced or even suggested constraint anywhere in current code.
