---
id: JM-BIBLE-384
title: Accept, Reject, and Cancel Semantics
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
  - JM-BIBLE-376
related_documents:
  - JM-BIBLE-383
  - JM-BIBLE-386
implementation_status: current
professional_validation: not_required
normative: true
---

# Accept, Reject, and Cancel Semantics

## `_handle_accept()` (`ACCEPT_PROPOSAL`)

```python
def _handle_accept(self, turn_id, request, session, now) -> ConversationTurn:
    proposal = session.activeProposal
    if proposal is None or proposal.status != "ACTIVE":
        raise ConversationInvalidStateError("There is no active proposal to accept.")

    if state.is_proposal_stale(proposal, request.currentJDL, request.currentDesignIntent):
        raise ConversationStaleContextError(...)

    accepted_proposal = proposal.model_copy(update={"status": "ACCEPTED"})
    technical_changes = [d.path for d in accepted_proposal.designerProposal.diff if d.changed]
    intent_changes = [f"{s.target}.{s.concept}" for s in accepted_proposal.designerProposal.designIntent.statements]
    session.acceptedChangeHistory.extend(technical_changes)
    for change in technical_changes:
        if change not in session.summary.acceptedDecisions:
            session.summary.acceptedDecisions.append(change)
    session.activeProposal = None
    session.status = "ACTIVE"
    return self._make_turn(..., "ACCEPT_PROPOSAL", "Proposal accepted.",
        proposal_id=accepted_proposal.proposalId, technical_changes=technical_changes,
        intent_changes=intent_changes, accepted=True)
```

1. **Existence/state guard.** No active proposal, or one whose `status` isn't `"ACTIVE"` (e.g. already `SUPERSEDED`), raises `ConversationInvalidStateError` (400).
2. **Staleness guard.** `state.is_proposal_stale()` compares the proposal's `baseDefinitionHash`/`baseIntentHash` against the caller's actual current values (freshly hashed at the top of `process_turn()`). A mismatch raises `ConversationStaleContextError` (409) — the accept is refused outright, not degraded to a partial or best-effort apply. See [`377-design-state-synchronization.md`](377-design-state-synchronization.md).
3. **Relabels the proposal `"ACCEPTED"`** (a local `model_copy`, not written back into `session.activeProposal` — see next step).
4. **Extends history.** `session.acceptedChangeHistory` gets every changed dotted path appended (duplicates allowed — it's a full chronological log); `session.summary.acceptedDecisions` gets the same paths appended only if not already present (a deduplicated running set, consistent with `ConversationSummary`'s role as a compact digest).
5. **Clears `session.activeProposal` to `None`** and sets `session.status = "ACTIVE"`.
6. **Returns a turn with `accepted=True`.**

Note what `_handle_accept()` does *not* do: it never touches `request.currentJDL` or `request.currentDesignIntent`, never calls any apply/persist function, and never returns anything other than the same already-computed `candidateJDL` that was already sitting inside `accepted_proposal.designerProposal.candidateJDL` before this call — the caller (`useProjectStore.applyDesignerProposal()`/`useDesignIntentStore.applyIntent()`) is the only thing that actually writes the accepted values anywhere (CONV-GOV-002/003).

## `_handle_reject()` (`REJECT_PROPOSAL`)

```python
def _handle_reject(self, turn_id, request, session, now) -> ConversationTurn:
    proposal = session.activeProposal
    if proposal is None:
        raise ConversationInvalidStateError("There is no active proposal to reject.")
    session.activeProposal = None
    session.status = "IDLE"
    return self._make_turn(..., "REJECT_PROPOSAL", "Proposal discarded — no changes applied.",
        proposal_id=proposal.proposalId, accepted=False)
```

Requires an active proposal to exist at all (any status, not necessarily `"ACTIVE"` — a looser guard than `_handle_accept()`'s, since rejecting a proposal that happens to be `SUPERSEDED` is still a coherent thing to do defensively); raises `ConversationInvalidStateError` if `None`. On success, clears `activeProposal` and sets `status="IDLE"` — **no** history write of any kind: `session.acceptedChangeHistory` and `session.summary.acceptedDecisions` are both left untouched (CONV-GOV-018). Verified directly by `backend/tests/test_conversation_engine.py::TestRejectAndCancel::test_reject_discards_proposal_without_mutation` and, for the guard itself, `test_reject_without_an_active_proposal_raises`.

## `_handle_cancel()` (`CANCEL_INTERACTION`)

```python
def _handle_cancel(self, turn_id, request, session, now) -> ConversationTurn:
    if session.pendingClarification is not None:
        session.pendingClarification = None
    if session.activeProposal is not None:
        session.activeProposal = None
    session.status = "IDLE"
    return self._make_turn(..., "CANCEL_INTERACTION", "Cleared the current interaction. No changes were made.")
```

Unconditionally clears both `pendingClarification` and `activeProposal` (the `is not None` checks are purely to avoid a redundant assignment — the effect is the same either way) and always sets `status="IDLE"`. Unlike `_handle_accept()`/`_handle_reject()`, this handler **never raises**, even if both fields are already `None` — cancelling when there is nothing to cancel is a valid, silent no-op, not an error condition.

`CANCEL_INTERACTION` is "the general safety valve": `classify_action()` checks `_UNDO_MARKERS` (`"undo"`, `"annulla l'ultima"`, `"revert"`) **before** it checks `has_clarification` or `has_active_proposal` — the very first branch in the function. This means an explicit cancel phrase always wins, regardless of what else is open, so a user is never trapped inside an open clarification or an unwanted proposal with no way to back out. Verified by `backend/tests/test_conversation_engine.py::TestRejectAndCancel::test_cancel_clears_pending_clarification`.

## Comparison

| Handler | Guard | On success | History touched? | Can be called with nothing pending? |
|---|---|---|---|---|
| `_handle_accept()` | active proposal must exist and be `ACTIVE`; must not be stale | `activeProposal -> None`, `status -> ACTIVE` | Yes — `acceptedChangeHistory`, `summary.acceptedDecisions` | No — raises |
| `_handle_reject()` | a proposal must exist (any status) | `activeProposal -> None`, `status -> IDLE` | No | No — raises |
| `_handle_cancel()` | none | `pendingClarification -> None`, `activeProposal -> None`, `status -> IDLE` | No | Yes — silent no-op |
