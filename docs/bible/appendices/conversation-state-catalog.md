---
id: JM-BIBLE-A74
title: "Appendix: Conversation State Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
related_documents:
  - JM-BIBLE-CONVERSATION-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Conversation State Catalog

The 7 `SessionStatus` values (`backend/jewelmind/conversation/schemas.py`). "Reachable?" was verified by grepping every assignment to `session.status` (and the `new_session()`/`ConversationSession` default) across `backend/jewelmind/conversation/`.

| Status | Meaning | Reachable in real code? | Where assigned |
|---|---|---|---|
| `IDLE` | No open clarification, no active proposal — the resting state. | Yes | `state.new_session()`'s default (`ConversationSession.status: SessionStatus = "IDLE"`); explicitly re-set by `ConversationEngine._handle_reject()` and `ConversationEngine._handle_cancel()` (`service.py`) |
| `WAITING_FOR_CLARIFICATION` | A `ClarificationThread` is open and needs an answer. | Yes | `ConversationEngine._handle_designer_routed()` (ambiguous-reference case) and `ConversationEngine._resolve_designer_proposal()` (Designer-returned clarification question) — both in `service.py` |
| `PROPOSAL_READY` | A `ConversationProposal` is active and awaiting accept/reject/correction. | Yes | `ConversationEngine._resolve_designer_proposal()` (`service.py`), once a proposal is successfully built with no clarification/unsupported-only outcome |
| `ACTIVE` | A turn resolved (accepted, or reported as unsupported) and the session is ready for the next turn, distinct from the initial `IDLE` resting state. | Yes | `ConversationEngine._resolve_designer_proposal()` (unsupported-feature branch) and `ConversationEngine._handle_accept()` (`service.py`) |
| `WAITING_FOR_ACCEPTANCE` | Schema-defined status for a proposal specifically awaiting the caller's acceptance step. | **No.** Confirmed by grep: no assignment to this literal exists anywhere in `backend/jewelmind/conversation/`. `PROPOSAL_READY` is the status actually used for this situation. | N/A |
| `CLOSED` | Schema-defined status for a terminated session. | **No.** Confirmed by grep: no assignment to this literal exists anywhere in `backend/jewelmind/conversation/`. There is no code path that ever closes a session — `_handle_cancel()` resets to `IDLE`, not `CLOSED`. | N/A |
| `FAILED` | Schema-defined status for a session that failed processing. | **No.** Confirmed by grep: no assignment to this literal exists anywhere in `backend/jewelmind/conversation/`. Every processing failure in `ConversationEngine.process_turn()` raises an `AppError` (or a Designer-originated error) before a `ConversationTurn`/updated `session.status` is ever produced — the session object itself is never mutated to record a failed status. | N/A |

## Notes grounded in the real code

- 4 of the 7 `SessionStatus` values are reachable; 3 (`WAITING_FOR_ACCEPTANCE`, `CLOSED`, `FAILED`) are schema-complete but currently dead states. This mirrors the same honest-gap pattern documented for `ConversationActionType` in [`conversation-action-catalog.md`](conversation-action-catalog.md) (`ADD_INTENT`/`REMOVE_INTENT`) and for Forge/Designer/Design-Intent's own catalogs in earlier Sprints.
- Because the backend is stateless per request (CONV-GOV-002, restated in `docs/bible/14-conversation/README.md`'s "single most important finding"), a session that would conceptually be `FAILED` in a stateful system instead simply never gets a new turn appended — the caller's own error handling (an HTTP error response) is what a client actually observes, not a `FAILED` session status round-tripped back to it.
