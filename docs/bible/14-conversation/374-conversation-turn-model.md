---
id: JM-BIBLE-374
title: Conversation Turn Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
  - JM-BIBLE-372
related_documents:
  - JM-BIBLE-373
  - JM-BIBLE-377
  - JM-BIBLE-378
implementation_status: current
professional_validation: not_required
normative: true
---

# Conversation Turn Model

`ConversationTurn` (`backend/jewelmind/conversation/schemas.py`) is the single record produced by every call to `ConversationEngine.process_turn()`. Its schema counterpart, `specs/conversation/v1/conversation-turn.schema.json`, cites this document directly.

## Fields

| Field | Type | Set by |
|---|---|---|
| `turnId` | `str` | `f"turn-{uuid.uuid4()}"`, generated once in `process_turn()` and threaded through every handler. |
| `sequence` | `int` | `len(session.turns) + 1` at the moment `_make_turn()` runs — 1-indexed, monotonically increasing within a session. |
| `role` | `Literal["user", "system"]` | Always `"user"` in current code — see [`378-turn-role-and-message-model.md`](378-turn-role-and-message-model.md). |
| `sourceText` | `str` | `request.text`, verbatim. |
| `timestamp` | `str` | ISO-8601, from `_now()` (`datetime.now(UTC).isoformat()`). |
| `interpretedAction` | `ConversationActionType` | The classified/resolved action for this turn. |
| `references` | `list[str]` | Populated only by the `PRESERVE_TARGET` short-circuit in `_handle_designer_routed()` (`reference_list=[preserve_target]`); empty on every other path. |
| `technicalChanges` | `list[str]` | Dotted JDL paths from `proposal.diff` where `changed` is true. |
| `intentChanges` | `list[str]` | `"{target}.{concept}"` strings from `proposal.designIntent.statements`. |
| `clarification` | `ClarificationThread \| None` | The thread just opened, or (on `ANSWER_CLARIFICATION`) the thread just closed. |
| `unsupportedFeatures` | `list[str]` | Feature names from `DesignerProposal.unsupportedFeatures`. |
| `proposalId` | `str \| None` | The `ConversationProposal.proposalId` this turn produced or resolved, if any. |
| `result` | `str` | A short human-readable summary string, always set. |
| `accepted` | `bool \| None` | `True` on `ACCEPT_PROPOSAL`, `False` on `REJECT_PROPOSAL`, `None` otherwise. |
| `relatedJDLHashBefore` / `relatedJDLHashAfter` | `str` | See below. |
| `relatedIntentHashBefore` / `relatedIntentHashAfter` | `str` | See below. |
| `diagnostics` | `list[ConversationDiagnostic]` | Populated on ambiguous-reference and invalid-clarification-answer outcomes. |

## `relatedJDLHashAfter`/`relatedIntentHashAfter` always equal `Before`

`_make_turn()` (`service.py`) sets all four hash fields from the same two session values:

```python
relatedJDLHashBefore=session.currentJDLHash,
relatedJDLHashAfter=session.currentJDLHash,
relatedIntentHashBefore=session.currentIntentHash,
relatedIntentHashAfter=session.currentIntentHash,
```

This is an honest, documented fact about the architecture, not a bug to fix. `session.currentJDLHash`/`currentIntentHash` were already refreshed once, at the very top of `process_turn()`, via `state.refresh_hashes(session, request.currentJDL, request.currentDesignIntent)` — before any handler runs. Because CONV-GOV-002 forbids Conversation from mutating a stored design itself (`_handle_accept()` only *confirms* a proposal is safe to apply and returns the already-computed candidate; it never writes `request.currentJDL` in place), there is no point within a single `process_turn()` call where the "current" design actually changes. "After" is always the same as "before" from the backend's own perspective — the design only actually changes once the caller applies the accepted `candidateJDL` and sends it back as the *new* `currentJDL` on the next request, at which point that next turn's `Before` value reflects the change. The field pair exists in the schema to describe a design-state transition per turn; in the current one-shot-per-request architecture, that transition, if any, happens entirely on the caller's side, between requests, not inside a single `process_turn()` call.

## Cross-reference

`specs/conversation/v1/examples/preserve-unspecified-values.json` shows a concrete instance: a `MODIFY_DESIGN_PROPOSAL` turn with `technicalChanges: ["material.metal"]` and both hash-before/after pairs identical (`"355ddca57e7e49ad"` / `"355ddca57e7e49ad"` and `"120c58f04f73bc92"` / `"120c58f04f73bc92"`), even though the turn's own proposal, once accepted on a *later* turn, would in fact change `material.metal`.
