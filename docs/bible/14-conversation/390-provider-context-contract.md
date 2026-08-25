---
id: JM-BIBLE-390
title: Provider Context Contract
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
  - JM-BIBLE-387
  - JM-BIBLE-391
implementation_status: current
professional_validation: not_required
normative: true
---

# Provider Context Contract

## What a real `DesignerProvider` actually receives

Every turn that reaches Designer does so through exactly one of two call sites in `backend/jewelmind/conversation/service.py`, both constructing a `NaturalLanguageDesignRequest` (`backend/jewelmind/designer/schemas.py`):

`_handle_designer_routed()`:

```python
designer_result = self._designer.interpret(
    NaturalLanguageDesignRequest(
        requestId=turn_id,
        text=request.text,
        locale=request.locale,
        interactionMode=interaction_mode,
        currentJDL=request.currentJDL,
        currentDesignIntent=request.currentDesignIntent,
    )
)
```

`_handle_answer_clarification()` constructs the same shape, with `text` replaced by `combined_text = f"{thread.question} {request.text}"` (the clarification question prefixed to the raw answer) and `interactionMode` fixed to `"MODIFY"`.

## `NaturalLanguageDesignRequest`'s real fields

Reading `backend/jewelmind/designer/schemas.py` directly, `NaturalLanguageDesignRequest` has exactly these fields: `requestId`, `text`, `locale`, `interactionMode`, `currentJDL`, `currentDesignIntent`. There is **no `context` field, no `TurnContext` field, and no field of any kind carrying turn history, a proposal ID, a pending-clarification question, or a conversation summary.**

## The honest gap: `TurnContext` is schema-complete but not wired into the real Designer call

[`375-turn-context-model.md`](375-turn-context-model.md) documents `TurnContext` as "what a real provider would receive — compact, never raw CAD geometry, never the entire turn history" (the docstring on the class itself uses this exact framing). That describes the *intended* shape of provider context. Verified by reading `service.py` in full and grepping the whole `backend/jewelmind/` tree for `build_turn_context(` and `TurnContext(`:

- `build_turn_context()` is defined once, in `context.py`.
- It is called from exactly two places: its own module is not self-calling in a loop, and the only other call site in the entire backend is `backend/tests/test_conversation.py::TestContext`.
- `service.py` — the only module that actually talks to Designer — never imports `build_turn_context` or `TurnContext` at all.

So today, a real (or `FakeDesignerProvider`-simulated) provider call never receives an `activeProposalId`, `pendingClarificationQuestion`, `recentAcceptedChanges`, `compactConversationSummary`, or `modelCurrentOrStale` value. Designer sees exactly the same request shape it saw before Conversation Engine existed: raw text, locale, interaction mode, current JDL, current DesignIntent. Everything Designer knows about "what's going on in this conversation" is inferred solely from `text` itself — for a clarification answer, that inference is carried entirely by string-concatenating the original question onto the answer (`combined_text`), not by structured context.

This is the same honest-gap pattern this codebase uses elsewhere (e.g. several `INTENT_*`/`DESIGNER_*` diagnostic codes documented as schema-complete-but-unreachable in earlier sprints): the shape exists, is validated by schema tests, and is a real target for a future change — but it is not currently exercised by the production code path. It is not a bug being hidden; it is recorded here and in [`404-conversation-gap-analysis-and-open-questions.md`](404-conversation-gap-analysis-and-open-questions.md) as a gap, per this Bible's own governance rule against silently changing meaning.

## What this means for multi-turn quality in practice

Because Designer's own `currentJDL`/`currentDesignIntent` are always the caller's real current values (never stale — see [`377-design-state-synchronization.md`](377-design-state-synchronization.md)), and because a clarification answer is combined with its originating question before being sent, Designer still has enough information to interpret most individual turns correctly in isolation. What it does *not* have is any signal about turns further back than the current one-shot text — no awareness of `recentAcceptedChanges`, no compacted summary of rejected directions or previously-discussed unsupported features. Conversation Engine's own state (`ConversationSession`) carries that history faithfully; it is simply not yet forwarded to the provider.

## Cross-references

- [`375-turn-context-model.md`](375-turn-context-model.md) — the `TurnContext` shape as specified.
- [`387-context-window-policy.md`](387-context-window-policy.md) — the bound `build_turn_context()` would enforce if wired in.
- [`391-conversation-designer-integration.md`](391-conversation-designer-integration.md) — the full integration contract this document is one honest sub-finding of.
- [`404-conversation-gap-analysis-and-open-questions.md`](404-conversation-gap-analysis-and-open-questions.md) — this gap, tracked alongside the others found while writing this Sprint's documentation.
