---
id: JM-BIBLE-375
title: Turn Context Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
  - JM-BIBLE-372
related_documents:
  - JM-BIBLE-387
  - JM-BIBLE-388
  - JM-BIBLE-390
implementation_status: current
professional_validation: not_required
normative: true
---

# Turn Context Model

`TurnContext` (`backend/jewelmind/conversation/schemas.py`) is built by `context.py::build_turn_context()`, which cites this document in its own module docstring. `TurnContext`'s own class docstring states its purpose directly: "What a real provider would receive — compact, never raw CAD geometry, never the entire turn history."

## Fields

| Field | Type | Source |
|---|---|---|
| `activeProposalId` | `str \| None` | `session.activeProposal.proposalId if session.activeProposal else None`. |
| `pendingClarificationQuestion` | `str \| None` | `session.pendingClarification.question if session.pendingClarification else None`. |
| `recentAcceptedChanges` | `list[str]` | `session.acceptedChangeHistory[-MAX_RECENT_TURNS_IN_CONTEXT:]` — the last 6 entries. |
| `compactConversationSummary` | `ConversationSummary \| None` | `compact_summary(session)` if `len(session.turns) > MAX_RECENT_TURNS_IN_CONTEXT`, else `None`. |
| `modelCurrentOrStale` | `Literal["CURRENT", "STALE", "NONE"]` | Passed in by the caller of `build_turn_context()` as the `model_state` argument — not computed inside `context.py` itself. |

## What "a real provider would receive" means today

`TurnContext` is a real, schema-validated, currently-constructible shape (`build_turn_context()` is unit-exercised and validated against `specs/conversation/v1/turn-context.schema.json`), but no current code path in `service.py` actually threads a `TurnContext` into the `DesignerContext`/`NaturalLanguageDesignRequest` passed to `DesignerService.interpret()`. `_handle_designer_routed()` and `_handle_answer_clarification()` both construct their `NaturalLanguageDesignRequest` directly from `request.text`/`request.locale`/`request.currentJDL`/`request.currentDesignIntent` — `TurnContext` is not one of that request's fields. This means `TurnContext` today documents the intended shape of provider context; it is exercised by tests and specs but not yet wired into the live `DesignerProvider` call. See [`390-provider-context-contract.md`](390-provider-context-contract.md) for how the existing `DesignerContext` (Sprint 10) differs from this shape, and [`404-conversation-gap-analysis-and-open-questions.md`](404-conversation-gap-analysis-and-open-questions.md) for this as a tracked gap rather than a silent omission.

## Why it's bounded the way it is

- **Never raw geometry.** No field on `TurnContext` can hold a `JewelryDefinition`, a mesh, or any CAD-derived data — Atlas/Vision output never reaches this layer at all.
- **Never the full turn history.** `recentAcceptedChanges` is capped at `MAX_RECENT_TURNS_IN_CONTEXT = 6` (`context.py`), and `session.turns` itself (the full list) has no field on `TurnContext` — only its *derived* summary (`compactConversationSummary`) and *derived* recent accepted-change list ever appear.
- **Exact, not fuzzy, for the two things that matter most right now.** `activeProposalId` and `pendingClarificationQuestion` are read directly off the session's current structured state, not reconstructed from prose or from the summary — CONV-GOV-016.

See [`387-context-window-policy.md`](387-context-window-policy.md) for why `MAX_RECENT_TURNS_IN_CONTEXT` is a turn count rather than a token budget.
