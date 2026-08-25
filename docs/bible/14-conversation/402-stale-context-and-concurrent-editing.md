---
id: JM-BIBLE-402
title: Stale Context and Concurrent Editing
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
  - JM-BIBLE-386
  - JM-BIBLE-400
implementation_status: current
professional_validation: not_required
normative: true
---

# Stale Context and Concurrent Editing

CONV-GOV-008 in full operational detail: how staleness is actually detected, walked through the "concurrent manual editing" scenario named in the Sprint 12 brief, and why there is deliberately no merge/rebase logic anywhere in this layer.

## How staleness is detected — `state.py` in full

Two hashing functions establish content identity:

```python
def intent_hash(intent: DesignIntent) -> str:
    data = intent.model_dump(mode="json")
    payload = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]
```

(`definition_hash()`, the JDL equivalent, already exists in `jewelmind.utils.hashing` and is reused unmodified — `intent_hash()`'s own docstring: "Mirrors `jewelmind.utils.hashing.definition_hash()` exactly — same canonical-JSON-then-sha256 technique.")

A proposal captures both hashes at the moment it is created, from whatever the caller says is current *right now*:

```python
def make_proposal(turn_id, current_jdl, current_intent, designer_proposal) -> ConversationProposal:
    return ConversationProposal(
        proposalId=f"conv-proposal-{uuid.uuid4()}",
        turnId=turn_id,
        baseDefinitionHash=definition_hash(current_jdl),
        baseIntentHash=intent_hash(current_intent),
        designerProposal=designer_proposal,
        status="ACTIVE",
    )
```

And every accept request re-derives the caller's *current* hashes fresh, comparing them against those captured values:

```python
def is_proposal_stale(proposal, current_jdl, current_intent) -> bool:
    jdl_changed = proposal.baseDefinitionHash != definition_hash(current_jdl)
    intent_changed = proposal.baseIntentHash != intent_hash(current_intent)
    return jdl_changed or intent_changed
```

`ConversationEngine.process_turn()` also calls `state.refresh_hashes(session, request.currentJDL, request.currentDesignIntent)` on every single request — before classification even happens — so `session.currentJDLHash`/`currentIntentHash` never display a hash from an earlier turn; they always reflect exactly what the caller sent this time.

## `_handle_accept()` — where the check is enforced

```python
def _handle_accept(self, turn_id, request, session, now) -> ConversationTurn:
    proposal = session.activeProposal
    if proposal is None or proposal.status != "ACTIVE":
        raise ConversationInvalidStateError("There is no active proposal to accept.")

    if state.is_proposal_stale(proposal, request.currentJDL, request.currentDesignIntent):
        raise ConversationStaleContextError(
            "The design changed since this proposal was created — please describe the change again."
        )
    ...
```

This is the single enforcement point. There is no other code path anywhere in `backend/jewelmind/conversation/` that applies a proposal without first passing through `is_proposal_stale()` — `ConversationStaleContextError` maps to a 409 response (`errors.py`: `status_code = 409`, `code = "CONVERSATION_STALE_CONTEXT"`).

## Walking through the "concurrent manual editing" scenario

1. User sends a turn ("Usa il platino.") against `currentJDL` = the design's current state, call it `D0`. Designer proposes `material.metal = platinum`; `_resolve_designer_proposal()` calls `state.make_proposal()`, capturing `baseDefinitionHash = definition_hash(D0)`. The proposal is returned as `session.activeProposal`, status `ACTIVE`.
2. **Before accepting**, the user switches to `ConfigurationPanel` (which stays fully interactive throughout, per CONV-GOV-013) and manually edits `band.width` — a real, direct edit to `useProjectStore.currentDefinition`, producing a new design state `D1 ≠ D0`.
3. The user clicks Apply/Accept on the still-open conversation proposal. `ConversationPanel.tsx`'s `handleAccept()` sends the accept turn (`sendTurn('Accept')`), and — critically — the request body's `currentJDL` field is populated from `useProjectStore`'s *live* `currentDefinition`, which is now `D1`, not the `D0` the proposal was actually computed against.
4. On the backend, `_handle_accept()` calls `state.is_proposal_stale(proposal, D1, ...)`. Since `definition_hash(D1) != proposal.baseDefinitionHash` (which was `definition_hash(D0)`), `jdl_changed` is `True`, and `ConversationStaleContextError` is raised — a 409 response.
5. `ConversationPanel.tsx` catches the `ApiError` with `code === 'CONVERSATION_STALE_CONTEXT'` and renders the specific message: "The design changed since this proposal was created — please describe the change again." The stale proposal is never applied, and `D1` (the user's manual edit) is untouched and remains the design's current state.

This is exactly `TestStaleProposalProtection::test_accepting_after_a_concurrent_manual_edit_is_rejected` (`backend/tests/test_conversation_engine.py`), which constructs the identical scenario: propose a platinum change, then edit `band.width` on a copy of the definition before attempting accept, and asserts `ConversationStaleContextError` is raised. The negative control, `test_accepting_against_the_same_unchanged_jdl_succeeds`, confirms an accept against the *unchanged* base succeeds normally — staleness detection has no false positives on an ordinary, un-concurrent accept.

## No merge or rebase logic exists — verified, and deliberate

Reading `state.py` and `service.py` in full: there is no function anywhere in either module (or anywhere else in `backend/jewelmind/conversation/`) that attempts to reconcile a proposal computed against `D0` with a design that has since moved to `D1` — no three-way merge, no "apply what's still applicable," no partial-acceptance path. `is_proposal_stale()` returns a boolean; `_handle_accept()`'s only response to `True` is to refuse the entire accept, unconditionally. The Sprint 12 brief's own guidance — "prefer conservative stale-proposal rejection where merge certainty is insufficient" — is exactly what this is: a deliberate choice, not a missing feature. Merging `D0`'s proposed `material.metal = platinum` onto `D1`'s manually-edited `band.width = 3.9` might well be the "obviously correct" outcome in this particular example, but the general case (a proposal touching a field the manual edit *also* touched, or a manual edit that invalidates an assumption the AI's interpretation depended on) has no reliable, general resolution — silently guessing wrong here would mean applying a change the user never actually reviewed against the design they're now looking at.

## Real generated proof: `specs/conversation/v1/test-vectors/stale-context-vectors.json`

```json
{
  "vectors": [
    { "scenario": "unchanged_jdl_and_intent", "isStale": false },
    { "scenario": "jdl_changed_since_proposal", "isStale": true },
    { "scenario": "intent_changed_since_proposal", "isStale": true }
  ]
}
```

Three real, generated outputs of `is_proposal_stale()` — confirming a JDL-only change and an intent-only change *each independently* trigger staleness (the function's `or` between `jdl_changed`/`intent_changed`), not only a JDL change.

## The user's recovery path

`_handle_accept()`'s raised error message is the entire recovery instruction: "please describe the change again." There is no auto-retry, no automatic re-basing of the proposal onto `D1`. The user must issue a new turn; `_handle_designer_routed()` will call Designer fresh with `currentJDL = D1`, producing a new proposal computed against the design state the user is actually looking at. This keeps the guarantee simple and auditable at the cost of asking the user to re-state a change they may have already described once — a real, acknowledged UX cost, not concealed as free.

## Cross-references

- [`386-state-preservation-policy.md`](386-state-preservation-policy.md) — the sibling guarantee governing what happens *within* a single accepted proposal's field preservation, as opposed to this document's concern with staleness *between* proposal creation and acceptance.
- `backend/tests/test_conversation_engine.py::TestStaleProposalProtection` — both tests, in full.
- `specs/conversation/v1/test-vectors/stale-context-vectors.json` — the real generated data quoted above.
- [`400-conversation-evaluation-framework.md`](400-conversation-evaluation-framework.md) — `STALE_CONTEXT_REJECTION` as a formal evaluation metric.
