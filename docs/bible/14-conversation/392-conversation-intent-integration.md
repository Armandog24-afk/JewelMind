---
id: JM-BIBLE-392
title: Conversation Intent Integration
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
  - JM-BIBLE-DESIGN-INTENT-README
related_documents:
  - JM-BIBLE-391
  - JM-BIBLE-393
implementation_status: current
professional_validation: not_required
normative: true
---

# Conversation Intent Integration

## There is no separate "ask Design Intent directly" code path

Grepping `backend/jewelmind/conversation/` for any import of `jewelmind.design_intent.resolver`, `build_design_intent`, or any other Design Intent construction function finds none — `conversation/` imports only `jewelmind.design_intent.schemas.DesignIntent` (a type) and, in `references.py`, `jewelmind.design_intent.vocabulary.TARGET_SYNONYMS` (a read-only lookup table, not intent construction). Every `DesignIntent`/`IntentStatement` a `ConversationTurn` ever reports comes from `proposal.designIntent`, where `proposal` is the real `DesignerProposal` returned by `DesignerService.interpret()` — the exact same field Designer's own single-turn flow already produces (Sprint 10/11). Conversation turns never construct a `DesignIntent` directly.

## `intentChanges` construction

`_resolve_designer_proposal()` in `service.py` builds the turn's `intentChanges` list with one line:

```python
intent_changes = [f"{s.target}.{s.concept}" for s in proposal.designIntent.statements]
```

Each entry is a `target.concept` pair (e.g. `"RING.SIMPLICITY"`), one per `IntentStatement` Designer/Design-Intent extracted for this turn — never a numeric value, never a JDL path. This is the same list used both as the turn's own `intentChanges` field and, via `compact_summary()`, folded into `session.summary.intentThemes` once a turn scrolls out of the recent window (see [`388-history-compaction-model.md`](388-history-compaction-model.md)).

## Why an intent-only proposal is classified `MODIFY_INTENT`

Still in `_resolve_designer_proposal()`:

```python
interpreted_action: ConversationActionType = (
    "MODIFY_INTENT" if not technical_changes and intent_changes else action
)
```

When a proposal's `diff` has zero `changed` entries but its `designIntent.statements` is non-empty, the turn's `interpretedAction` is overridden from the caller-supplied action (`CREATE_DESIGN_PROPOSAL`/`MODIFY_DESIGN_PROPOSAL`) to `MODIFY_INTENT` — the turn is reported as what it actually did, not what the raw text superficially requested.

## CASE B: intent-only changes never touch technical state

`backend/tests/test_conversation_engine.py::TestCaseB_IntentOnlyNeverStalesGeometry` sends `"Fallo più minimal."` against a `FakeDesignerProvider` response containing only `designIntentStatements=[RawIntentStatement(target="ring", concept="SIMPLICITY", value="minimal")]` and asserts:

- `not any(d.changed for d in proposal.diff)` — no technical field changed.
- `proposal.designIntent.statements[0].value == "MINIMAL"` — the intent statement normalized correctly.
- `r.turn.interpretedAction == "MODIFY_INTENT"`.

`specs/conversation/v1/examples/intent-only-refinement.json` is the same scenario captured as a real generated `ConversationResult` example (CASE B), produced by actually running `ConversationEngine`.

## Why this matters for staleness (CONV-GOV-011)

Because `applyDesignerProposal()` (frontend, `useProjectStore.ts`) is only called when `proposal.diff.some(d => d.changed)` is true, and an intent-only proposal's `diff` is always empty of `changed` entries, accepting a `MODIFY_INTENT` turn never sets `isStale: true` on the design and never touches `currentDefinition` — only `useDesignIntentStore.applyIntent()` runs. This is the concrete mechanism behind CONV-GOV-011 ("intent-only changes must never mark geometry stale"); see [`386-state-preservation-policy.md`](386-state-preservation-policy.md) for the frontend side of this contract.

## Cross-references

- [`391-conversation-designer-integration.md`](391-conversation-designer-integration.md) — the shared `DesignerService.interpret()` call path both technical and intent changes flow through.
- [`393-conversation-jdl-integration.md`](393-conversation-jdl-integration.md) — the parallel technical-side integration document.
- `docs/bible/13-design-intent/350-intent-to-jdl-boundary.md` — the boundary this integration deliberately never crosses.
- CONV-GOV-011 in [`370-conversation-governance.md`](370-conversation-governance.md).
