---
id: JM-BIBLE-A77
title: "Appendix: Conversation Diagnostic Catalog"
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

# Appendix: Conversation Diagnostic Catalog

The 10 `CONVERSATION_*` codes named in the Sprint 12 brief, drawn from `backend/jewelmind/conversation/errors.py` and `schemas.py::ConversationDiagnosticCode`. "Raised today?" was verified individually by grepping every usage of each error class / diagnostic code across `backend/jewelmind/conversation/` — not assumed from the class existing.

| Code | HTTP status | Severity | Raised today? |
|---|---|---|---|
| `CONVERSATION_INVALID_STATE` | 400 (`ConversationInvalidStateError`) | n/a (HTTP error, not an in-band diagnostic) | Yes — `ConversationEngine._handle_accept()` (no active/`ACTIVE`-status proposal) and `ConversationEngine._handle_reject()` (no active proposal), both in `service.py` |
| `CONVERSATION_REFERENCE_AMBIGUOUS` | n/a (in-band `ConversationDiagnostic` on a normal 200 response) | `info` | Yes — `ConversationEngine._handle_designer_routed()` (`service.py`), attached to the `REQUEST_CLARIFICATION` turn opened when `resolve_implicit_target()` reports `is_ambiguous=True` |
| `CONVERSATION_NO_PENDING_CLARIFICATION` | 400 (`ConversationNoPendingClarificationError`) | n/a (HTTP error) | Yes — `ConversationEngine._handle_answer_clarification()` (`service.py`), a defensive guard for a direct call with no genuinely open thread (`classify_action()` itself only ever routes here when a thread is actually open) |
| `CONVERSATION_CLARIFICATION_INVALID` | n/a (in-band `ConversationDiagnostic` on a normal 200 response) | `warning` | Yes — `ConversationEngine._handle_answer_clarification()` (`service.py`), attached when `clarifications.try_resolve_answer()` returns `accepted=False` |
| `CONVERSATION_PROPOSAL_SUPERSEDED` | 409 (`ConversationProposalSupersededError`) | n/a (HTTP error) | **No.** Confirmed by grep: the class is defined in `errors.py` but never instantiated/raised anywhere in `backend/jewelmind/conversation/`. Superseding an active proposal (CONV-GOV-017) is instead handled silently in-line, by `ConversationEngine._handle_designer_routed()` setting `session.activeProposal.status = "SUPERSEDED"` before building the new one — never by raising this error. |
| `CONVERSATION_STALE_CONTEXT` | 409 (`ConversationStaleContextError`) | n/a (HTTP error) | Yes — `ConversationEngine._handle_accept()` (`service.py`), when `state.is_proposal_stale()` returns `True` |
| `CONVERSATION_PROVIDER_FAILED` | 502 (`ConversationProviderFailedError`) | n/a (HTTP error) | Yes — `ConversationEngine._handle_designer_routed()` and `ConversationEngine._handle_answer_clarification()` (`service.py`), both as the fallback `except Exception` branch wrapping a non-`AppError` failure from `DesignerService.interpret()`. Note: an `AppError` raised by Designer itself (e.g. `DesignerProviderError`, `DesignerProviderUnavailableError`) is deliberately re-raised as-is and never reaches this wrapper — see the code comment quoted below. |
| `CONVERSATION_CONTEXT_TOO_LARGE` | 400 (`ConversationContextTooLargeError`) | n/a (HTTP error) | **No.** Confirmed by grep: the class is defined in `errors.py` but never instantiated/raised anywhere. `ConversationTurnRequest.text` is bounded by Pydantic's `max_length=2000` at the schema layer (a 422, not this 400), and `context.py::MAX_RECENT_TURNS_IN_CONTEXT` bounds history structurally rather than by rejecting an oversized request. |
| `CONVERSATION_ACTION_UNSUPPORTED` | 400 (`ConversationActionUnsupportedError`) | n/a (HTTP error) | **No.** Confirmed by grep: the class is defined in `errors.py` but never instantiated/raised anywhere. Every one of the 13 `ConversationActionType` values that `classify_action()`/`service.py` can actually produce has a real handler branch in `ConversationEngine.process_turn()`; there is currently no code path that reaches an action it cannot handle. |
| `CONVERSATION_STATE_SYNC_FAILED` | n/a (in-band `ConversationDiagnostic` — also listed in `ALL_CONVERSATION_ERROR_CODES`) | n/a | **No.** Confirmed by grep: the constant is defined in `errors.py` and is a member of `ConversationDiagnosticCode` (`schemas.py`), but no `ConversationDiagnostic(code=CONVERSATION_STATE_SYNC_FAILED, ...)` is ever constructed anywhere in `backend/jewelmind/conversation/`. `state.refresh_hashes()` runs unconditionally and cannot itself fail in a way this code would report. |

## No separate conversation-specific security-rejection code

Unlike the 10 codes above, prompt-injection/security screening deliberately reuses Designer's own error rather than adding an 11th. The comment in `backend/jewelmind/conversation/errors.py` (quoted verbatim):

> "Security screening reuses `DesignerSecurityRejectedError` directly (imported by service.py) rather than inventing an 11th conversation-only code — every turn (including a clarification answer or correction) is untrusted input, screened the same way Designer already screens a natural-language request. See 397-conversation-security-model.md."

This is confirmed live: `ConversationEngine.process_turn()` (`service.py`) calls `designer_normalizer.detect_prompt_injection_risk(request.text)` on every turn before classification, and raises `DesignerSecurityRejectedError` (400, `DESIGNER_SECURITY_REJECTED`) — never a conversation-namespaced code — when it fires.

## Notes grounded in the real code

- 6 of the 10 named codes are actually reachable today (`CONVERSATION_INVALID_STATE`, `CONVERSATION_REFERENCE_AMBIGUOUS`, `CONVERSATION_NO_PENDING_CLARIFICATION`, `CONVERSATION_CLARIFICATION_INVALID`, `CONVERSATION_STALE_CONTEXT`, `CONVERSATION_PROVIDER_FAILED`). The remaining 4 (`CONVERSATION_PROPOSAL_SUPERSEDED`, `CONVERSATION_CONTEXT_TOO_LARGE`, `CONVERSATION_ACTION_UNSUPPORTED`, `CONVERSATION_STATE_SYNC_FAILED`) are schema-complete but currently unreachable — this is the same deliberate, documented pattern already established for Forge/Designer/Design-Intent's own diagnostic catalogs in earlier Sprints, not an oversight specific to this appendix.
- The code comment in `errors.py` references a file named `397-conversation-security-model.md`; the actual reading-order filename in `docs/bible/14-conversation/README.md` is `397-conversation-security.md` (no `-model` suffix). This appendix quotes the comment verbatim rather than silently correcting it — flagged here as a real, minor cross-reference discrepancy in the current code, not fixed as part of this appendix-only change.
