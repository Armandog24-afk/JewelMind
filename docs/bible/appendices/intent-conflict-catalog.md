---
id: JM-BIBLE-A68
title: "Appendix: Intent Conflict Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-DESIGN-INTENT-README
  - JM-BIBLE-330
related_documents:
  - JM-BIBLE-346
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Intent Conflict Catalog

The 5 `ConflictType` values (`backend/jewelmind/design_intent/schemas.py`). Verified by grepping every `type=`/`conflict_type =` assignment site in `backend/jewelmind/design_intent/conflicts.py` — only 3 of the 5 values are ever actually produced by v1 code. A conflict is always recorded and surfaced, never silently rejected, and never blocks a proposal from being returned (`docs/bible/13-design-intent/346-intent-conflict-model.md`).

| `ConflictType` | Currently produced? | Real detection condition | Real corpus example |
|---|---|---|---|
| `EXPLICIT_CONTRADICTION` | Yes | `conflicts.py::_value_conflicts` — two statements on the same `(target, concept)` pair whose continuum distance is `>= max_distance` (i.e. opposite ends of the continuum) and not both `strength == "REQUIRED"` | `"delicate but very substantial"` (corpus `conflict-02`): `VISUAL_WEIGHT` `DELICATE` vs `SUBSTANTIAL` |
| `SOFT_TENSION` | Yes | `conflicts.py::_value_conflicts` — two statements on the same `(target, concept)` pair whose continuum distance is `> 1` but `< max_distance` (a real tension, not a full contradiction) | Not present as a standalone corpus case in `test_design_intent_corpus.py`'s `CONFLICT` category (all 3 corpus conflict cases are 4-value continuums at maximum distance, see below); reachable in `backend/tests/test_design_intent.py` indirectly through any 5-value continuum pair at distance 2-3, though no dedicated unit test names this type explicitly |
| `TARGET_CONFLICT` | Yes | `conflicts.py::_relation_conflicts` — two relations sharing the same `(subject, object)` pair whose predicates are opposites per `_OPPOSITE_PREDICATE` (`DOMINANT_OVER`/`SUBORDINATE_TO`, `NARROWER_THAN`/`BROADER_THAN`) | No dedicated corpus case in `test_design_intent_corpus.py`; covered structurally by `_OPPOSITE_PREDICATE`'s definition, not by a named test in the current suite |
| `PRIORITY_CONFLICT` | Yes (narrow case) | `conflicts.py::_value_conflicts` — same as `EXPLICIT_CONTRADICTION`'s distance condition, but produced instead of it specifically when **both** statements have `strength == "REQUIRED"` | No dedicated corpus case exercises two `REQUIRED`-strength statements at maximum continuum distance; the corpus's 3 `CONFLICT` cases all use the default `PREFERRED` strength, so they produce `EXPLICIT_CONTRADICTION`, never `PRIORITY_CONFLICT` |
| `RESOLUTION_CONFLICT` | No | Declared in the type; not assigned anywhere in `conflicts.py`. Reserved for a future conflict arising during resolution (e.g. two competing deterministic mappings), which cannot occur while zero `IntentProfile`s are registered — see `docs/bible/13-design-intent/362-design-intent-gap-analysis.md`. | n/a |

## Notes grounded in the real code

- The corpus's 3 `CONFLICT` cases (`conflict-01` "minimal and highly ornate", `conflict-02` "delicate but very substantial", `conflict-03` "understated but also a real statement piece") all pair the two extreme values of a continuum at default `PREFERRED` strength, so all 3 currently produce `EXPLICIT_CONTRADICTION` — none produces `SOFT_TENSION`, `TARGET_CONFLICT`, or `PRIORITY_CONFLICT` by name; each is checked only via `has_conflict_count(1)`, not by asserting a specific `type`.
- `backend/tests/test_design_intent.py::TestBuildDesignIntent::test_adjacent_continuum_values_are_not_a_conflict` verifies the negative case: two statements one step apart on a continuum (`DELICATE`/`LIGHT`) produce zero conflicts and keep `resolutionStatus == "PRESERVED"`.
- Conflict detection module docstring (`conflicts.py`) states `PRIORITY_CONFLICT` and `RESOLUTION_CONFLICT` are "reserved for richer future detection" — this appendix confirms `PRIORITY_CONFLICT`'s narrow branch does exist in code (unlike `RESOLUTION_CONFLICT`, which has zero implementation), but no test currently exercises the two-`REQUIRED`-statements path that would trigger it.
