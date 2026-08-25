---
id: JM-BIBLE-387
title: Context Window Policy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
related_documents:
  - JM-BIBLE-375
  - JM-BIBLE-388
  - JM-BIBLE-389
  - JM-BIBLE-390
implementation_status: current
professional_validation: not_required
normative: true
---

# Context Window Policy

## The bound: `MAX_RECENT_TURNS_IN_CONTEXT = 6`

`backend/jewelmind/conversation/context.py` defines a single constant:

```python
MAX_RECENT_TURNS_IN_CONTEXT = 6
```

This is a **turn count**, not a token budget. The Sprint 12 brief was explicit that provider-specific token measurement is unverifiable at this layer — JewelMind cannot know a live provider's actual tokenizer, context window, or pricing tier from inside `context.py` — and instructed against inventing one. `MAX_RECENT_TURNS_IN_CONTEXT` is the "reasonable, configurable limit" the brief asked for instead: it bounds how many raw turns are treated as "recent" for context-building purposes, independent of how long any individual turn's text happens to be.

The constant is a plain module-level integer, not a settings/environment value — "configurable" here means "a single, easily-changed constant in one place," not that it is currently wired to an environment variable or a per-request override. No code path in `backend/jewelmind/conversation/` reads it from configuration.

## `build_turn_context()`

```python
def build_turn_context(session: ConversationSession, model_state: str) -> TurnContext:
    needs_summary = len(session.turns) > MAX_RECENT_TURNS_IN_CONTEXT
    return TurnContext(
        activeProposalId=session.activeProposal.proposalId if session.activeProposal else None,
        pendingClarificationQuestion=(
            session.pendingClarification.question if session.pendingClarification else None
        ),
        recentAcceptedChanges=list(session.acceptedChangeHistory[-MAX_RECENT_TURNS_IN_CONTEXT:]),
        compactConversationSummary=compact_summary(session) if needs_summary else None,
        modelCurrentOrStale=model_state,
    )
```

`TurnContext` is populated in this literal field order, and that order reflects a real priority: the two structured, exact-and-current facts (`activeProposalId`, `pendingClarificationQuestion`) come first, followed by a bounded slice of concrete accepted-change history (`recentAcceptedChanges`, itself capped to the same 6-item window), followed by the compacted prose-level summary (`compactConversationSummary`, only populated once turns have actually scrolled out of the recent window), and finally the coarse model-freshness flag (`modelCurrentOrStale`). A future provider integration reading this shape should treat it in the same order: exact structured state first, summarized history last.

## What "recent" means

`recent_turns(session)` returns `session.turns[-MAX_RECENT_TURNS_IN_CONTEXT:]` — the same 6-turn slice, available as its own helper for any caller that wants the raw turns rather than the derived `TurnContext`.

## Honest gap: `build_turn_context()` is not currently called by the real Designer integration

This constant and function are exercised directly by `backend/tests/test_conversation.py::TestContext` and indirectly by `specs/conversation/v1/test-vectors/context-compaction-vectors.json`, but `service.py`'s two real calls into `DesignerService.interpret()` (`_handle_designer_routed()` and `_handle_answer_clarification()`) construct a `NaturalLanguageDesignRequest` with only `requestId`, `text`, `locale`, `interactionMode`, `currentJDL`, `currentDesignIntent` — there is no `context` field on that request type at all (`backend/jewelmind/designer/schemas.py`), and no call site in `service.py` invokes `build_turn_context()`. This is documented in full in [`390-provider-context-contract.md`](390-provider-context-contract.md) and tracked as a gap in [`404-conversation-gap-analysis-and-open-questions.md`](404-conversation-gap-analysis-and-open-questions.md) — it is not hidden here.

## Cross-references

- [`375-turn-context-model.md`](375-turn-context-model.md) — the `TurnContext` shape itself.
- [`388-history-compaction-model.md`](388-history-compaction-model.md) — how `compactConversationSummary` is built.
- [`390-provider-context-contract.md`](390-provider-context-contract.md) — the honest gap between this policy and what a provider actually receives today.
- CONV-GOV-015, CONV-GOV-016 in [`370-conversation-governance.md`](370-conversation-governance.md).
