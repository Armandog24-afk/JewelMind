---
id: JM-BIBLE-378
title: Turn Role and Message Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
  - JM-BIBLE-374
related_documents:
  - JM-BIBLE-372
  - JM-BIBLE-385
implementation_status: current
professional_validation: not_required
normative: false
---

# Turn Role and Message Model

## The field

`ConversationTurn.role: Literal["user", "system"] = "user"` (`backend/jewelmind/conversation/schemas.py`).

## `role` is always `"user"` today

`_make_turn()` (`service.py`) hardcodes `role="user"` on every `ConversationTurn` it constructs — there is exactly one construction site for a `ConversationTurn` in the entire backend, and it never passes any other value for `role`. A grep of `backend/jewelmind/conversation/` for the literal string `"system"` used as a role value returns no matches. `"system"` is a valid value per the schema and per `specs/conversation/v1/conversation-turn.schema.json`, but no current code path ever produces a turn with it.

## There is no separate assistant-authored message

A chat-style transcript typically alternates user messages and assistant messages as two different records. Conversation Engine does not do this. JewelMind's "side" of the exchange — what would otherwise be a separate assistant reply — is represented on the *same* turn the user's text produced, via its structured fields: `interpretedAction` (what kind of thing happened), `result` (a short human-readable summary), `clarification` (a question, if one was opened), `technicalChanges`/`intentChanges` (what a proposal actually contains), `unsupportedFeatures`, and `diagnostics`. `frontend/src/components/ConversationPanel.tsx` renders this directly: `turn.sourceText` under a `"You"` label, and `turn.result` (plus proposal detail) under a `"JewelMind"` label, both from the one `ConversationTurn` object — there is no second turn or message object involved.

## Why this is the deliberate design, not an oversight

This is a direct consequence of the Sprint's core principle: "conversation is a sequence of structured design transactions, not a stream of authoritative prose" (README). A free-text assistant reply would itself be exactly the kind of unstructured, unreviewable prose the whole Sprint exists to avoid treating as ground truth. Every one of the 13 `ConversationActionType` values already carries everything a UI needs to describe "what JewelMind did" in response to a turn — there was never a need for a second, separately-authored message whose content isn't backed by a structured field.

## `"system"` remains schema-complete for a possible future use

The value is kept in the `Literal` and the JSON Schema deliberately, not removed, because a plausible future use exists (e.g. a turn injected by the backend itself — a system notice, a migration note, or a session-opened marker — that isn't a response to any user text at all). Building that capability is out of scope for Sprint 12; nothing in `README.md`'s reading order or CONV-GOV list describes it. This is the same honest-gap pattern used elsewhere in the Bible for a schema-complete-but-currently-unreachable value — compare `ProposalStatus.REJECTED`/`STALE` ([`372-conversation-domain-model.md`](372-conversation-domain-model.md)), `ResolutionStatus`'s five unused values (`docs/bible/13-design-intent/348-intent-resolution-model.md`), and Designer's own unused `ProposalStatus.ACCEPTED`/`REJECTED` (`docs/bible/12-designer/294-design-proposal-model.md`).
