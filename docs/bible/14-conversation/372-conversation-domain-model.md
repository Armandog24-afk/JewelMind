---
id: JM-BIBLE-372
title: Conversation Domain Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
  - JM-BIBLE-371
related_documents:
  - JM-BIBLE-373
  - JM-BIBLE-374
  - JM-BIBLE-375
implementation_status: current
professional_validation: not_required
normative: true
---

# Conversation Domain Model

All shapes below are `backend/jewelmind/conversation/schemas.py`, whose own module docstring cites this document. Every model extends `ConversationModel(BaseModel)` with `model_config = ConfigDict(extra="forbid")` — an unrecognized field on any conversation payload is a hard validation error, never silently ignored.

## Type aliases

- `ConversationActionType` — the 13 canonical values: `CREATE_DESIGN_PROPOSAL`, `MODIFY_DESIGN_PROPOSAL`, `ADD_INTENT`, `MODIFY_INTENT`, `REMOVE_INTENT`, `PRESERVE_TARGET`, `REQUEST_CLARIFICATION`, `ANSWER_CLARIFICATION`, `REPORT_UNSUPPORTED`, `ACCEPT_PROPOSAL`, `REJECT_PROPOSAL`, `CANCEL_INTERACTION`, `NO_CHANGE`. Note `ADD_INTENT`/`MODIFY_INTENT`/`REMOVE_INTENT` are declared in the type but the only intent-labeled outcome `service.py` ever actually produces is `MODIFY_INTENT`, and only as a relabeling of an otherwise-Designer-routed turn (`_resolve_designer_proposal()`, see [`374-conversation-turn-model.md`](374-conversation-turn-model.md)) — `ADD_INTENT`/`REMOVE_INTENT` are schema-complete but never emitted by any current code path.
- `SessionStatus` — 7 values, see [`373-conversation-session-lifecycle.md`](373-conversation-session-lifecycle.md).
- `ClarificationStatus` — `OPEN`, `ANSWERED`, `CANCELLED`, `SUPERSEDED`.
- `ExpectedAnswerType` — `NUMERIC`, `ENUM_CHOICE`, `FREE_TEXT`, `CONFIRMATION`.
- `ProposalStatus` — `ACTIVE`, `ACCEPTED`, `REJECTED`, `SUPERSEDED`, `STALE`. Only `ACTIVE`, `ACCEPTED`, and `SUPERSEDED` are ever assigned by `service.py`; `REJECTED` and `STALE` are schema-reserved values never written by current code (a rejected proposal is cleared to `None`, not relabeled `REJECTED`; staleness raises `ConversationStaleContextError` rather than setting the status — see [`384-accept-reject-cancel-semantics.md`](384-accept-reject-cancel-semantics.md) and [`402-stale-context-and-concurrent-editing.md`](402-stale-context-and-concurrent-editing.md)).
- `ConversationDiagnosticCode` — `CONVERSATION_REFERENCE_AMBIGUOUS`, `CONVERSATION_CLARIFICATION_INVALID`, `CONVERSATION_STATE_SYNC_FAILED`. Of these, only the first two are ever actually constructed by `service.py`; `CONVERSATION_STATE_SYNC_FAILED` is schema-reserved (see [`396-conversational-error-model.md`](396-conversational-error-model.md)).

## `ClarificationThread`

| Field | Type | Purpose |
|---|---|---|
| `clarificationId` | `str` | `clarification-{uuid4}`. |
| `originatingTurnId` | `str` | The `turnId` of the turn that opened this thread. |
| `question` | `str` | The question text shown to the user. |
| `target` | `str \| None` | The JDL field path or design-intent target the question concerns, if known. |
| `expectedAnswerType` | `ExpectedAnswerType` | Governs how `try_resolve_answer()` validates a reply. |
| `allowedChoices` | `list[str]` | Populated for `ENUM_CHOICE` questions; empty otherwise. |
| `required` | `bool` | Always `True` in current code — no code path ever constructs an optional clarification. |
| `status` | `ClarificationStatus` | `OPEN` on creation. |
| `createdAt` / `resolvedAt` | `str \| None` | ISO-8601 timestamps. |
| `answer` | `str \| None` | The raw answer text once closed. |

## `ClarificationAnswer`

| Field | Type | Purpose |
|---|---|---|
| `clarificationId` | `str` | Which thread this answer targets. |
| `turnId` | `str` | The turn that supplied the answer. |
| `rawAnswer` | `str` | Exactly what the user typed. |
| `resolvedValue` | `str \| float \| None` | The parsed value, if accepted. |
| `accepted` | `bool` | Whether validation succeeded. |

This model is schema-complete and validated by `specs/conversation/v1/clarification-answer.schema.json`, but no code in `service.py` constructs a `ClarificationAnswer` instance directly — `_handle_answer_clarification()` calls `clarifications.try_resolve_answer()` and works with its raw `(resolved_value, accepted)` tuple return instead of wrapping it in this model. The model exists as the schema's canonical shape for that outcome, not as an object that flows through the running code.

## `ConversationProposal`

Declared as a top-level class in `schemas.py` (not nested inside `ConversationSession` or `ConversationTurn`, though it is used as the type of `ConversationSession.activeProposal`):

| Field | Type | Purpose |
|---|---|---|
| `proposalId` | `str` | `conv-proposal-{uuid4}`. |
| `turnId` | `str` | The turn that produced it. |
| `baseDefinitionHash` / `baseIntentHash` | `str` | The JDL/intent hashes it was computed against — the staleness anchor. |
| `designerProposal` | `DesignerProposal` | The full Sprint 10 proposal object, unmodified, embedded whole rather than re-summarized. |
| `status` | `ProposalStatus` | `ACTIVE` on creation. |

## `ConversationSummary`

Five parallel `list[str]` fields, all deterministically derived, never LLM-generated (see [`389-conversation-summary-model.md`](389-conversation-summary-model.md)): `acceptedDecisions`, `intentThemes`, `unresolvedQuestions`, `rejectedDirections`, `unsupportedDiscussed`.

## `ConversationDiagnostic`

`code: ConversationDiagnosticCode`, `severity: Literal["info", "warning", "error"]`, `message: str`. In practice only `"info"` (reference ambiguity) and `"warning"` (invalid clarification answer) severities are ever emitted by current code; `"error"` is a valid schema value never produced.

## `ConversationTurn`

See [`374-conversation-turn-model.md`](374-conversation-turn-model.md) for the full field-by-field treatment; summarized here for completeness: `turnId`, `sequence`, `role`, `sourceText`, `timestamp`, `interpretedAction`, `references`, `technicalChanges`, `intentChanges`, `clarification`, `unsupportedFeatures`, `proposalId`, `result`, `accepted`, `relatedJDLHashBefore`/`After`, `relatedIntentHashBefore`/`After`, `diagnostics`.

## `ConversationSession`

| Field | Type | Purpose |
|---|---|---|
| `sessionId` | `str` | `session-{uuid4}`. |
| `sessionVersion` | `str` | `"1.0.0"`. |
| `currentJDLHash` / `currentIntentHash` | `str` | Real content hashes, recomputed every request by `state.refresh_hashes()` — **never a copy of the design itself**. |
| `turns` | `list[ConversationTurn]` | Full turn history for this session. |
| `pendingClarification` | `ClarificationThread \| None` | At most one open question at a time. |
| `activeProposal` | `ConversationProposal \| None` | At most one unreviewed proposal at a time. |
| `acceptedChangeHistory` | `list[str]` | Dotted JDL paths accepted so far, appended by `_handle_accept()`. |
| `lastReferencedTarget` | `str \| None` | The most recently resolved reference target — the anchor `resolve_implicit_target()` uses for bare pronouns. |
| `summary` | `ConversationSummary` | Compacted older-turn digest. |
| `status` | `SessionStatus` | See [`373`](373-conversation-session-lifecycle.md). |
| `createdAt` / `updatedAt` | `str` | ISO-8601 timestamps. |

`ConversationSession` never carries its own copy of `JewelryDefinition` or `DesignIntent` — CONV-GOV-001/002/003, enforced structurally by the absence of any such field in this class, not just by convention. This is **not** a Project-persistence mechanism (a future concept, out of scope for Sprint 12 per the README's "Explicitly out of scope" list in `CLAUDE.md`): the session has no name, no owner, no save/load semantics, no database row, and is discarded the moment the frontend stops sending it back.

## `TurnContext`

See [`375-turn-context-model.md`](375-turn-context-model.md).

## `ConversationTurnRequest`

`text: str` (`min_length=1, max_length=2000`), `locale: SupportedLocale | None`, `currentJDL: JewelryDefinition`, `currentDesignIntent: DesignIntent`, `session: ConversationSession | None`. A `None` session means "start a new one" — handled in `service.py::process_turn()` via `request.session or state.new_session(...)`.

## `ConversationResult`

`session: ConversationSession`, `turn: ConversationTurn` — the entire response body of `POST /api/conversation/turn`.
