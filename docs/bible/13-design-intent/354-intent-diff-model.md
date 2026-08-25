---
id: JM-BIBLE-354
title: Intent Diff Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-353
related_documents:
  - JM-BIBLE-355
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Diff Model

## `compute_intent_diff()` — the real algorithm

`design_intent/resolver.py::compute_intent_diff(previous, after) -> list[IntentDiffEntry]` is pure and deterministic — no LLM involvement, no randomness:

1. Flatten `previous.statements` (or `{}` if `previous is None`) to a dict of `{target}.{concept} -> value`.
2. Flatten `after.statements` the same way.
3. For the union of both keysets, sorted, compare before/after values and classify each key as `ADDED` (missing before, present after), `REMOVED` (present before, missing after), `CHANGED` (present in both with a different value), or `UNCHANGED` (present in both with the same value).
4. Return one `IntentDiffEntry{key, previousValue, newValue, changeType}` per key.

This mirrors Designer v1's own `compute_diff()` for JDL fields (`../12-designer/311-proposal-diff-model.md`) almost exactly — same four-way classification, same "flatten to dotted keys, compare, done" shape — applied to the intent statement list instead of `JewelryDefinition` fields. Only statements are diffed; relations and unresolved descriptors are not currently part of `compute_intent_diff()`'s output.

## Where it is used today

`compute_intent_diff()` is a real, tested function (`backend/tests/test_design_intent.py`), but its output is not currently wired into the Designer request/response pipeline the way JDL's `compute_diff()` is (JDL's diff is attached to `DesignerProposal.diff` and drives the stale-model decision in `DesignerPanel.tsx`; see `../12-designer/311-proposal-diff-model.md`). No equivalent `DesignerProposal.intentDiff` field exists. The function is available for direct use (e.g. from tests, or from a future caller) but is not called anywhere in `designer/service.py` today.

## Not yet a dedicated UI

There is no dedicated "before -> after" widget for design intent in Studio today. The effect of a change is visible only implicitly: the persistent intent summary in `DesignerPanel.tsx` (see [`357-studio-intent-review.md`](357-studio-intent-review.md)) simply re-renders with whatever `currentIntent` looks like after `applyIntent()` is called — a user comparing turns has to remember what the tags looked like before, there is no highlighted-diff view. This is listed as a gap in [`362-design-intent-gap-analysis.md`](362-design-intent-gap-analysis.md), directly parallel to Designer v1's own still-open "richer proposal-diff UI" gap (`../12-designer/321-designer-gap-analysis.md`).

## Why it matters even unused today

`compute_intent_diff()` existing and being correct now means a future richer diff UI, or a future observability event ("3 statements changed this turn"), does not need new diffing logic — only a new caller. This is the same "data already computed, not yet surfaced" pattern Sprint 10 left behind for its own JDL diff before this Sprint wired it into the stale-model fix (see [`356-designer-intent-extraction.md`](356-designer-intent-extraction.md) for that fix).

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md) — INTENT-GOV-004.
- `../12-designer/311-proposal-diff-model.md` — the JDL-side sibling this mirrors.
- [`357-studio-intent-review.md`](357-studio-intent-review.md) — today's implicit, non-diffed rendering.
- [`362-design-intent-gap-analysis.md`](362-design-intent-gap-analysis.md) — the dedicated diff UI gap.
