---
id: JM-BIBLE-377
title: Design State Synchronization
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
  - JM-BIBLE-386
  - JM-BIBLE-402
implementation_status: current
professional_validation: not_required
normative: true
---

# Design State Synchronization

`state.py::is_proposal_stale()`'s own docstring cites this document. It governs both halves of design state — JDL and DesignIntent — together, per CONV-GOV-008; there is no separate document for intent synchronization, because the mechanism is identical for both and lives in the same two functions.

## Conversation never replays prose to reconstruct state

`ConversationEngine` never rebuilds `currentJDL`/`currentDesignIntent` by walking `session.turns` and re-applying each accepted change in order. Both values always come fresh from the caller on every single request — `ConversationTurnRequest.currentJDL`/`currentDesignIntent` are required fields, not optional ones the backend could choose to fall back to history for. `session.turns` is read-only evidence for context-building (`context.py`) and summarization; it is never the source of truth for what the design currently is (CONV-GOV-004).

## Two real, parallel hashing functions

- `definition_hash()` — `jewelmind.utils.hashing`, used across the whole backend (not conversation-specific) as the canonical content hash of a `JewelryDefinition`.
- `intent_hash()` — `backend/jewelmind/conversation/state.py`, new in this Sprint. Its own docstring states it "mirrors `jewelmind.utils.hashing.definition_hash()` exactly — same canonical-JSON-then-sha256 technique," deliberately scoped to `conversation/` rather than added to `design_intent/schemas.py` itself, "since Design Intent Model v1 has no other use for a content hash of its own."

Both compute `hashlib.sha256(json.dumps(model.model_dump(mode="json"), sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()` (truncated to 16 hex characters for `intent_hash()`) — a deterministic function of the model's content alone, with no dependency on wall-clock time or object identity.

## `refresh_hashes()` runs on every request, unconditionally

```python
state.refresh_hashes(session, request.currentJDL, request.currentDesignIntent)
```

is the second line of `process_turn()`, run before `classify_action()` and before any handler. It overwrites `session.currentJDLHash`/`currentIntentHash` in place from the caller's actual current values — never trusted from a prior turn, never merged with a prior value. If the session arriving on this request carries a stale hash from three turns ago (because, say, the frontend applied an accepted change and is now sending the updated JDL), `refresh_hashes()` immediately brings the session's own record of "what the design currently is" back in line with reality before anything else happens.

## The caller's accepted JDL always wins — no merge, no negotiation

If a session's own history implies one value (e.g. `acceptedChangeHistory` records `material.metal` was set to `"platinum"` two turns ago) but the `currentJDL` the caller sends on this request has a different value for that field (because the user, or another client, edited it manually in `ConfigurationPanel` in the meantime), there is no reconciliation logic anywhere in `conversation/` that compares the two and decides which should win. The caller's `currentJDL` **is** current, unconditionally — `refresh_hashes()` simply recomputes `currentJDLHash` from it, overwriting whatever was there. `acceptedChangeHistory` is a record of what was proposed and confirmed through this session's own turns; it is not consulted to validate or contest what the caller now claims is current.

The one place this divergence has a visible consequence is proposal acceptance: `state.is_proposal_stale()` compares a specific `ConversationProposal`'s `baseDefinitionHash`/`baseIntentHash` (captured at the moment that proposal was created) against the session's freshly refreshed `currentJDLHash`/`currentIntentHash`. A mismatch on either raises `ConversationStaleContextError` from `_handle_accept()`, rather than applying a proposal that was computed against a design that no longer exists — see [`402-stale-context-and-concurrent-editing.md`](402-stale-context-and-concurrent-editing.md) for the full accept-time contract, and [`386-state-preservation-policy.md`](386-state-preservation-policy.md) for how this interacts with field preservation.

## `specs/conversation/v1/test-vectors/stale-context-vectors.json`

Three real, generated cases exercise `is_proposal_stale()` directly:

| Scenario | `isStale` |
|---|---|
| `unchanged_jdl_and_intent` | `false` |
| `jdl_changed_since_proposal` | `true` |
| `intent_changed_since_proposal` | `true` |

Both halves — JDL and DesignIntent — are checked independently by `is_proposal_stale()` (`jdl_changed or intent_changed`), and either one alone is sufficient to make a proposal stale.
