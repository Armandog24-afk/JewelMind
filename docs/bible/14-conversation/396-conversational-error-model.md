---
id: JM-BIBLE-396
title: Conversational Error Model
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
  - JM-BIBLE-397
  - JM-BIBLE-403
implementation_status: current
professional_validation: not_required
normative: true
---

# Conversational Error Model

## Two kinds of code, same split as Designer

`backend/jewelmind/conversation/errors.py`'s own docstring states the discipline directly: a code is an HTTP `AppError` (a non-200 response) only when a turn could not be processed into any result at all; an expected, normal outcome of a turn (an ambiguous reference, an invalid clarification answer) is instead an in-band `ConversationDiagnostic.code` inside a normal `200 ConversationResult`. This mirrors `docs/bible/12-designer/312-designer-error-model.md`'s identical split for Designer.

`errors.py` declares `ALL_CONVERSATION_ERROR_CODES`, a 10-entry tuple. Cross-checked against `schemas.py`'s `ConversationDiagnosticCode` Literal (3 values) and the `AppError` subclasses actually defined in `errors.py` (7 classes), the 10 codes split as 7 `AppError` codes + 3 diagnostic-only codes.

## Real reachability, verified by reading and grepping the code

| Code | Kind | Raised/emitted where | Status |
|---|---|---|---|
| `CONVERSATION_INVALID_STATE` | `AppError` (400) | `_handle_accept()` (no active proposal), `_handle_reject()` (no active proposal to reject) | **Reachable.** Tested by `test_conversation_engine.py::TestRejectAndCancel::test_reject_without_an_active_proposal_raises` and `::test_handle_answer_clarification_guards_against_a_missing_thread` (via `ConversationNoPendingClarificationError`, a distinct code — see below — but the same defensive-guard pattern). |
| `CONVERSATION_REFERENCE_AMBIGUOUS` | Diagnostic | `_handle_designer_routed()`, attached when `resolve_implicit_target()` reports `is_ambiguous=True` | **Reachable.** Exercised by the `AMBIGUOUS_REFERENCE` corpus category (3 cases) in `test_conversation_corpus.py`. |
| `CONVERSATION_NO_PENDING_CLARIFICATION` | `AppError` (400) | `_handle_answer_clarification()`, when `session.pendingClarification` is `None` or not `OPEN` | **Reachable.** Tested by `test_conversation_engine.py::TestRejectAndCancel::test_handle_answer_clarification_guards_against_a_missing_thread`. |
| `CONVERSATION_CLARIFICATION_INVALID` | Diagnostic | `_handle_answer_clarification()`, when `clarifications.try_resolve_answer()` returns `accepted=False` | **Reachable.** Exercised wherever the corpus/engine tests send an answer that fails type validation (e.g. a non-numeric answer to a `NUMERIC` clarification). |
| `CONVERSATION_PROPOSAL_SUPERSEDED` | `AppError` (409) | Class is defined in `errors.py`; grepping the entire `backend/jewelmind/` tree for `ConversationProposalSupersededError` finds only its own definition | **Schema-complete, currently unreachable.** No code path raises it — a superseded proposal (`session.activeProposal.status == "SUPERSEDED"`, set by `_handle_designer_routed()` when a correction arrives) is simply replaced in-session, never surfaced as an error to reject a stale accept attempt against it (that scenario is instead covered by `CONVERSATION_STALE_CONTEXT`, a hash-based check, not a status-based one). |
| `CONVERSATION_STALE_CONTEXT` | `AppError` (409) | `_handle_accept()`, via `state.is_proposal_stale()` | **Reachable.** Tested by `test_conversation_engine.py::TestStaleProposalProtection::test_accepting_after_a_concurrent_manual_edit_is_rejected` and the `STALE_CONTEXT` corpus category (2 cases). See [`402-stale-context-and-concurrent-editing.md`](402-stale-context-and-concurrent-editing.md). |
| `CONVERSATION_PROVIDER_FAILED` | `AppError` (502) | `_handle_designer_routed()` and `_handle_answer_clarification()`, in a bare `except Exception` around `self._designer.interpret(...)` | **Reachable**, but only for the case where something *other than* an `AppError` escapes Designer — a genuinely unexpected exception, not one of Designer's own documented failure codes (which propagate through unchanged, see below). Tested by `test_conversation_engine.py::TestProviderFailureDoesNotMutate::test_conversation_provider_failed_wraps_a_non_apperror_exception`, using a deliberately broken `_BrokenDesignerService` stand-in — the test's own comment calls this "currently unreachable via the real Designer integration" in production, since the real `DesignerService.interpret()` always raises its own typed `AppError` subclasses on failure. |
| `CONVERSATION_CONTEXT_TOO_LARGE` | `AppError` (400) | Class is defined in `errors.py`; grep finds only its own definition | **Schema-complete, currently unreachable.** No code path measures context size or raises this — `MAX_RECENT_TURNS_IN_CONTEXT` bounds what is *built* into a `TurnContext` (which is itself not currently wired into a real provider call, see [`390-provider-context-contract.md`](390-provider-context-contract.md)) but nothing rejects an oversized request with this code. `ConversationTurnRequest.text` does have a `max_length=2000` Pydantic constraint, but a violation of that raises a generic Pydantic/FastAPI validation error (422), not this typed `AppError`. |
| `CONVERSATION_ACTION_UNSUPPORTED` | `AppError` (400) | Class is defined in `errors.py`; grep finds only its own definition | **Schema-complete, currently unreachable.** `classify_action()` always returns one of the 13 real `ConversationActionType` values and `process_turn()`'s dispatch handles all of them (the final `else` branch routes to `_handle_designer_routed()`), so there is no "recognized but unsupported action" case in the current code to trigger this. |
| `CONVERSATION_STATE_SYNC_FAILED` | Diagnostic | Constant is defined in `errors.py`/`schemas.py`; grepping for `CONVERSATION_STATE_SYNC_FAILED` as a `ConversationDiagnostic(code=...)` construction site finds none | **Schema-complete, currently unreachable.** `state.refresh_hashes()` always succeeds (it is pure hash computation over caller-supplied Pydantic objects that have already passed validation) — there is no observed failure mode it would report today. |

Reachable: 6 of 10 (`CONVERSATION_INVALID_STATE`, `CONVERSATION_REFERENCE_AMBIGUOUS`, `CONVERSATION_NO_PENDING_CLARIFICATION`, `CONVERSATION_CLARIFICATION_INVALID`, `CONVERSATION_STALE_CONTEXT`, `CONVERSATION_PROVIDER_FAILED`). Schema-complete but currently unreachable in production: 4 of 10 (`CONVERSATION_PROPOSAL_SUPERSEDED`, `CONVERSATION_CONTEXT_TOO_LARGE`, `CONVERSATION_ACTION_UNSUPPORTED`, `CONVERSATION_STATE_SYNC_FAILED`).

This is the same honest pattern several Designer/DesignIntent diagnostic codes already document in earlier sprints — a reserved code for a stage or condition that does not currently occur, not a bug being concealed.

## No 11th, Conversation-specific security code

`errors.py` carries this comment directly above `ALL_CONVERSATION_ERROR_CODES`:

> "Security screening reuses `DesignerSecurityRejectedError` directly (imported by service.py) rather than inventing an 11th conversation-only code — every turn (including a clarification answer or correction) is untrusted input, screened the same way Designer already screens a natural-language request."

`process_turn()`'s first line calls `designer_normalizer.detect_prompt_injection_risk(request.text)` and raises `DesignerSecurityRejectedError` (Designer's own error type, `DESIGNER_SECURITY_REJECTED`, 400) directly — not a Conversation-namespaced wrapper. See [`397-conversation-security.md`](397-conversation-security.md).

## Cross-references

- [`397-conversation-security.md`](397-conversation-security.md) — the security screen and the reused Designer error code.
- [`402-stale-context-and-concurrent-editing.md`](402-stale-context-and-concurrent-editing.md) — `CONVERSATION_STALE_CONTEXT` in full detail.
- `docs/bible/12-designer/312-designer-error-model.md` — the identical split-discipline model this document follows.
- [`404-conversation-gap-analysis-and-open-questions.md`](404-conversation-gap-analysis-and-open-questions.md) — the 4 unreachable codes, tracked as gaps.
