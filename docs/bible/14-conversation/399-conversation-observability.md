---
id: JM-BIBLE-399
title: Conversation Observability
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
  - JM-BIBLE-398
  - JM-BIBLE-404
implementation_status: current
professional_validation: not_required
normative: true
---

# Conversation Observability

Follows the same discipline `docs/bible/12-designer/316-designer-observability.md` established for Designer: name the taxonomy a future observability pass would want, then state plainly which of it is actually emitted today.

## A PLANNED taxonomy of 12 conceptual events

A future, richer observability layer for Conversation would plausibly want a distinct structured log event for each meaningful transition already visible as a real branch or call site in `service.py`, `references.py`, and `clarifications.py`:

1. `CONVERSATION_STARTED` — `state.new_session()`, the first turn of a session.
2. `TURN_RECEIVED` — the top of `process_turn()`, before classification.
3. `TURN_INTERPRETATION_STARTED` — immediately before either real `self._designer.interpret(...)` call in `_handle_designer_routed()`/`_handle_answer_clarification()`.
4. `REFERENCE_RESOLVED` — `references.py::resolve_implicit_target()` returning a non-ambiguous, non-`None` target.
5. `REFERENCE_AMBIGUOUS` — the same function returning `is_ambiguous=True`, the trigger for `_handle_designer_routed()`'s `REQUEST_CLARIFICATION` branch.
6. `CLARIFICATION_OPENED` — `clarifications.open_clarification()`.
7. `CLARIFICATION_RESOLVED` — `clarifications.close_answered()`.
8. `PROPOSAL_CREATED` — `state.make_proposal()`.
9. `PROPOSAL_ACCEPTED` — `_handle_accept()`'s successful path.
10. `PROPOSAL_REJECTED` — `_handle_reject()`.
11. `STATE_UPDATED` — `state.refresh_hashes()`, called once per `process_turn()`.
12. `CONVERSATION_ERROR` — any of the `AppError` subclasses in `conversation/errors.py` being raised.

This list names real transition points that exist in the current implementation — it is not speculative about what the code *could* do, only about what it does not yet report as a distinct structured event.

## None of these are currently emitted — stated plainly

Grepping `backend/jewelmind/conversation/` and `backend/jewelmind/api/routes.py` for `logging`, `logger`, and `structlog` finds no matches at all inside the conversation package, and `conversation_turn_route()` in `routes.py` contains no logging calls of its own. `POST /api/conversation/turn` receives exactly the same generic instrumentation every other route in the application gets, from `backend/jewelmind/api/app.py`'s app-wide middleware: a `request` log line on every call (`method`, `path`, `status`, `durationMs`, `requestId`) and, on a raised `AppError`, an `app_error` log line (`code`, `message`, `requestId`). Neither line distinguishes `CONVERSATION_STALE_CONTEXT` from `CONVERSATION_INVALID_STATE` in any way beyond the shared `code` field every route's errors already carry, and neither records which `ConversationActionType` a turn resolved into, whether a clarification was opened, or whether a proposal was ultimately accepted or rejected.

This is a documented target taxonomy for a future observability pass, not currently-implemented logging. No code path in this codebase emits any of the 12 events named above under that name, and this document does not claim otherwise.

## Why this gap is named rather than quietly filled

Emitting a partial subset of the 12 events, or logging something that looks like `PROPOSAL_ACCEPTED` when the actual "acceptance" the frontend acts on (`applyDesignerProposal()`/`applyIntent()` in `ConversationPanel.tsx`, see [`395-studio-integration.md`](395-studio-integration.md)) is a client-side store write with no further backend round trip, would create a misleading picture of what JewelMind can actually observe about a conversation. The backend's own `_handle_accept()` confirms an acceptance is *safe* and returns the already-computed values; it does not (and today cannot) observe whether the frontend actually went on to apply them to `currentDefinition`. Naming the full taxonomy as PLANNED, with zero of it emitted, keeps the gap between intended and actual observability honest and traceable in one place — the same reasoning `316-designer-observability.md` gives for the identical situation one layer down.

## Cross-references

- `docs/bible/12-designer/316-designer-observability.md` — the Sprint 10 sibling this document's structure and reasoning follow directly.
- [`398-conversation-privacy.md`](398-conversation-privacy.md) — what the generic request/error log lines do and do not contain.
- [`404-conversation-gap-analysis-and-open-questions.md`](404-conversation-gap-analysis-and-open-questions.md) — this gap, tracked alongside the others found while writing this Sprint's documentation.
