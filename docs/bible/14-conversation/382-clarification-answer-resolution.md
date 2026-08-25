---
id: JM-BIBLE-382
title: Clarification Answer Resolution
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
  - JM-BIBLE-381
related_documents:
  - JM-BIBLE-374
  - JM-BIBLE-391
implementation_status: current
professional_validation: not_required
normative: true
---

# Clarification Answer Resolution

`clarifications.py` cites this document (alongside [`381`](381-clarification-thread-model.md)) as the place `_handle_answer_clarification()`'s orchestration is documented in full.

## `_handle_answer_clarification()` step by step

```python
def _handle_answer_clarification(self, turn_id, request, session, now) -> ConversationTurn:
    thread = session.pendingClarification
    if thread is None or thread.status != "OPEN":
        raise ConversationNoPendingClarificationError(...)

    resolved_value, accepted = clarifications.try_resolve_answer(thread, request.text)
    if not accepted:
        return self._make_turn(..., "ANSWER_CLARIFICATION",
            f"Could not understand that as an answer to: {thread.question}",
            clarification=thread,
            diagnostics=[ConversationDiagnostic(code=CONVERSATION_CLARIFICATION_INVALID, ...)])

    closed = clarifications.close_answered(thread, request.text, resolved_value, now)
    session.pendingClarification = None

    combined_text = f"{thread.question} {request.text}"
    designer_result = self._designer.interpret(NaturalLanguageDesignRequest(
        requestId=turn_id, text=combined_text, locale=request.locale,
        interactionMode="MODIFY", currentJDL=request.currentJDL,
        currentDesignIntent=request.currentDesignIntent))

    turn = self._resolve_designer_proposal(turn_id, request, session, now, designer_result.proposal, "MODIFY_DESIGN_PROPOSAL")
    return turn.model_copy(update={"clarification": closed, "interpretedAction": "ANSWER_CLARIFICATION"})
```

1. **Reads `session.pendingClarification` — the one thread currently open.** No lookup by ID, no scan across a list of threads; `ConversationSession` only ever holds at most one pending clarification (`pendingClarification: ClarificationThread | None`), so "the open question" is unambiguous by construction.
2. **Defensive guard.** If there is no open thread (`thread is None or thread.status != "OPEN"`), raises `ConversationNoPendingClarificationError` (400). `classify_action()` only ever routes to `ANSWER_CLARIFICATION` when `has_clarification` is true, so this branch is unreachable via the normal `process_turn()` path — it exists to protect a direct call to the handler (see `backend/tests/test_conversation_engine.py::TestRejectAndCancel::test_handle_answer_clarification_guards_against_a_missing_thread`, which calls `eng._handle_answer_clarification(...)` directly to prove the guard).
3. **Validates via `try_resolve_answer()`.** An invalid/ambiguous answer returns to the **same** open thread with a `CONVERSATION_CLARIFICATION_INVALID` diagnostic (`severity="warning"`) — the thread is not closed, `session.pendingClarification` is left untouched, and the resulting turn's `clarification` field is set to the still-open `thread`. The backend never silently guesses a value from an answer it couldn't validate.
4. **Closes the thread and clears the session's pending pointer.** Only on `accepted=True`.
5. **Builds `combined_text = f"{thread.question} {request.text}"`** before calling Designer. This is necessary because the raw answer alone often has no meaning out of context — `"2.7 mm"` on its own tells `DesignerService.interpret()` nothing about *which* field it's meant for; prefixing the original question ("What band width would you like? 2.7 mm") gives the same natural-language pipeline Designer already uses for a fresh request enough context to resolve the field, exactly as it would if the user had typed the combined sentence themselves in one turn. This is the same interpretation channel, not a special clarification-only code path in Designer.
6. **Always calls Designer in `interactionMode="MODIFY"`**, regardless of whether the *original* turn that opened the clarification was a `CREATE` or `MODIFY` request — an answer to a clarification question is inherently a refinement of an already-in-progress interpretation, never a fresh "start over."
7. **Routes through the same `_resolve_designer_proposal()` every other Designer-routed turn uses**, then overwrites the resulting turn's `clarification` (to the now-closed thread, not `None`) and `interpretedAction` (forced to `"ANSWER_CLARIFICATION"`, overriding whatever `_resolve_designer_proposal()` itself would have classified the outcome as, e.g. `MODIFY_INTENT`) via `model_copy(update=...)`.

## CONV-GOV-007: resolves only its own question

Because `session.pendingClarification` is a single optional field, not a collection, there is no code path anywhere that could resolve a different, unrelated open question with an answer meant for another — there is structurally only ever one candidate thread to resolve against. This is the mechanism, not merely a convention: CONV-GOV-007 is enforced by the shape of `ConversationSession` itself.

## Reject, never guess

An invalid answer is never silently coerced into a best-effort value and never triggers a fallback interpretation. `try_resolve_answer()`'s type-specific validation (see [`381`](381-clarification-thread-model.md)) is deliberately strict — a `NUMERIC` question rejects `"not a number"` outright rather than attempting any numeric extraction from free text, and an `ENUM_CHOICE` question rejects an answer that names a real, otherwise-legitimate JDL enum value but isn't one of *this specific* thread's `allowedChoices` (see the `"platinum"` row in [`381`](381-clarification-thread-model.md)'s real example table — a genuine metal enum value, still rejected because it wasn't among the choices that particular open thread listed). The user simply sees the same question again with a diagnostic explaining the mismatch, and can answer again on the next turn.
