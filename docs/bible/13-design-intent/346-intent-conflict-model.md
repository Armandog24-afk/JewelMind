---
id: JM-BIBLE-346
title: Intent Conflict Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-332
related_documents:
  - JM-BIBLE-347
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Conflict Model

## `detect_conflicts()`, real and always-on

`backend/jewelmind/design_intent/conflicts.py::detect_conflicts(statements, relations)` runs on every `build_design_intent()` call, over the full merged statement/relation set (after MODIFY merging — see [`353-intent-preservation.md`](353-intent-preservation.md)). It returns `_value_conflicts(statements) + _relation_conflicts(relations)`.

## Value conflicts — continuum distance thresholds

`_value_conflicts()` groups statements by `(target, concept)`. For every pair within a group, it computes `continuum_distance(concept, a.value, b.value)` (index distance on that concept's ordered tuple — see [`338-style-continuum-model.md`](338-style-continuum-model.md)) and classifies:

| Distance | Both `REQUIRED`? | Classification |
|---|---|---|
| `<= 1` (adjacent, or identical) | — | No conflict at all |
| `>= 2` but below the continuum's max | either | `SOFT_TENSION` |
| At the continuum's max (opposite ends) | no | `EXPLICIT_CONTRADICTION` |
| At the continuum's max (opposite ends) | **yes** | `PRIORITY_CONFLICT` |

`max_distance = len(order) - 1`. Two adjacent values — e.g. `DELICATE` and `LIGHT` on `VISUAL_WEIGHT` (distance 1) — are never flagged; the design principle is that adjacent nuance is normal human language, not contradiction. A concept with fewer than 2 values in its continuum is skipped entirely (none currently have fewer than 3).

## Relation conflicts — opposite predicates on the same pair

`_relation_conflicts()` groups relations by `(subject, object)`. Two relations sharing that exact pair are a `TARGET_CONFLICT` if their predicates are registered opposites in `_OPPOSITE_PREDICATE`: `DOMINANT_OVER`↔`SUBORDINATE_TO`, `NARROWER_THAN`↔`BROADER_THAN`. `DISCREET_RELATIVE_TO` and `BALANCED_WITH` have no registered opposite, so they never trigger this check.

## `RESOLUTION_CONFLICT` — reserved, never produced

`ConflictType` has 5 members; only `EXPLICIT_CONTRADICTION`, `SOFT_TENSION`, `TARGET_CONFLICT`, and `PRIORITY_CONFLICT` are ever constructed by `conflicts.py`. `RESOLUTION_CONFLICT` is schema-reserved for a future conflict arising during an actual resolution step (which doesn't exist yet — see [`348-intent-resolution-model.md`](348-intent-resolution-model.md)); no current code path produces it.

## Real corpus examples

From `backend/tests/test_design_intent_corpus.py`'s `CONFLICT` category: "minimal and highly ornate" (both `SIMPLICITY`, opposite ends → `EXPLICIT_CONTRADICTION` unless both `REQUIRED`) and "delicate but very substantial" (both `VISUAL_WEIGHT` — `SUBSTANTIAL` is one step short of the `BOLD` end, so depending on the exact pair this can land as `SOFT_TENSION` rather than the maximal contradiction; the corpus exercises the real boundary, not an assumption).

## Conflicts are surfaced, never rejected

Every produced `IntentConflict` marks its involved statements/relations `resolutionStatus: CONFLICTING` (done by the caller, `resolver.py`, via `conflicting_ids()`) and appends an `INTENT_CONFLICT` diagnostic at `"warning"` severity. A conflict never removes a statement, never blocks `build_design_intent()` from returning, and never fails the HTTP request. The explicit design principle (see [`330-intent-governance.md`](330-intent-governance.md), INTENT-GOV-007): not every tension is invalid. A sophisticated design can intentionally combine contrasting intent — "delicate band, bold stone" is a real and coherent design brief, not a bug — so JewelMind's job is to surface the tension for human review (see [`357-studio-intent-review.md`](357-studio-intent-review.md)'s "Conflicting intent" section), never to auto-reject or silently pick a side.
