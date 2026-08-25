---
id: JM-BIBLE-A66
title: "Appendix: Intent Relation Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-DESIGN-INTENT-README
  - JM-BIBLE-330
related_documents:
  - JM-BIBLE-332
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Intent Relation Catalog

The 6 real `RelationPredicate` values (`backend/jewelmind/design_intent/schemas.py`), each expressing a relative (not absolute-numeric) statement between two `IntentTarget`s. Examples are the real corpus cases from the `RELATION` category in `backend/tests/test_design_intent_corpus.py` (6 cases: `rel-01` through `rel-06`).

| `RelationPredicate` | Example corpus sentence | Real `subject` / `predicate` / `object` triple |
|---|---|---|
| `NARROWER_THAN` | "La fascia deve sembrare sottile rispetto alla pietra." (`rel-01`) | `BAND` / `NARROWER_THAN` / `STONE` |
| `NARROWER_THAN` | "The band should look slim compared with the stone." (`rel-02`) | `BAND` / `NARROWER_THAN` / `STONE` |
| `BROADER_THAN` | Reachable via `"broader than"`/`"broader_than"` synonyms in `normalizer.py::PREDICATE_SYNONYMS`; no dedicated corpus case exists — see note below | `<subject>` / `BROADER_THAN` / `<object>` |
| `DOMINANT_OVER` | "Vorrei che la pietra fosse la protagonista." (`rel-03`) | `STONE` / `DOMINANT_OVER` / `RING` |
| `SUBORDINATE_TO` | Reachable via `"subordinate to"`/`"subordinate_to"` synonyms; no dedicated corpus case exists — see note below | `<subject>` / `SUBORDINATE_TO` / `<object>` |
| `DISCREET_RELATIVE_TO` | "Le griffe discrete rispetto alla pietra." (`rel-05`) | `PRONGS` / `DISCREET_RELATIVE_TO` / `STONE` |
| `BALANCED_WITH` | "Setting and stone should feel balanced with each other." (`rel-06`) | `SETTING` / `BALANCED_WITH` / `STONE` |

## Notes grounded in the real code

- `rel-04` ("Make the center stone the visual focus.") is **not** a relation example despite living in the `RELATION` category folder of the corpus — the case's raw input (`one_stmt("stone", "VISUAL_EMPHASIS", "center_focused", ...)`) is actually a single `IntentStatement`, not an `IntentRelation`; the corpus groups it with `RELATION` because the sentence is relational in natural language even though the deterministic extraction resolves it to a descriptor. This is called out here rather than silently smoothed over.
- `BROADER_THAN` and `SUBORDINATE_TO` are real, normalizer-recognized predicates (`normalize_predicate()` accepts both the canonical token and a phrase synonym for each — `normalizer.py::PREDICATE_SYNONYMS`) but have no dedicated positive corpus example in `test_design_intent_corpus.py`'s `RELATION` category; they are, however, exercised as the *opposite* predicate in `conflicts.py::_OPPOSITE_PREDICATE`'s `TARGET_CONFLICT` detection (a relation asserting `DOMINANT_OVER` and another asserting `SUBORDINATE_TO` between the same subject/object pair conflict).
- Every relation's `resolutionStatus` starts as `PRESERVED` (`resolver.py::_resolve_relations`), consistent with the same "never numerically resolved" rule that applies to statements (INTENT-GOV-001).
- An unrecognized subject, predicate, or object causes the whole relation to be dropped into `unresolvedDescriptors` with an `INTENT_INVALID_RELATION` diagnostic (`resolver.py::_resolve_relations`), never guessed.
