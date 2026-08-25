---
id: JM-BIBLE-403
title: Current Code Mapping
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
  - JM-BIBLE-404
implementation_status: current
professional_validation: not_required
normative: true
---

# Current Code Mapping

## Backend: `backend/jewelmind/conversation/`

| File | Lines | Responsibility |
|---|---|---|
| `__init__.py` | 11 | Package docstring — Conversation's non-authoritative role, no code. |
| `errors.py` | 84 | 6 `AppError` subclasses (`ConversationInvalidStateError`, `ConversationNoPendingClarificationError`, `ConversationClarificationInvalidError`, `ConversationStaleContextError`, `ConversationProviderFailedError`, `ConversationActionUnsupportedError`), 3 diagnostic-only code constants, `ALL_CONVERSATION_ERROR_CODES`. No dedicated security-rejection code — reuses `DesignerSecurityRejectedError` directly (see [`397-conversation-security.md`](397-conversation-security.md)). |
| `schemas.py` | 169 | Every Pydantic model: `ClarificationThread`, `ClarificationAnswer`, `ConversationProposal`, `ConversationSummary`, `ConversationDiagnostic`, `ConversationTurn`, `ConversationSession`, `TurnContext`, `ConversationTurnRequest`, `ConversationResult`, plus the `ConversationActionType`/`SessionStatus`/`ClarificationStatus`/`ExpectedAnswerType`/`ProposalStatus`/`ConversationDiagnosticCode` type aliases. See [`372-conversation-domain-model.md`](372-conversation-domain-model.md). |
| `state.py` | 101 | `intent_hash()`, `new_session()`, `refresh_hashes()`, `is_proposal_stale()`, `make_proposal()` — hashing and session-lifecycle helpers. See [`377-design-state-synchronization.md`](377-design-state-synchronization.md) and [`402-stale-context-and-concurrent-editing.md`](402-stale-context-and-concurrent-editing.md). |
| `references.py` | 134 | `find_explicit_target()`, `find_preserve_target()`, `mentions_material_word()`, `mentions_comparative_marker()`, `resolve_implicit_target()`. See [`379-reference-resolution.md`](379-reference-resolution.md) and [`380-pronoun-and-implicit-target-resolution.md`](380-pronoun-and-implicit-target-resolution.md). |
| `clarifications.py` | 89 | `open_clarification()`, `try_resolve_answer()`, `close_answered()`, `cancel()`, `supersede()` — pure, `model_copy`-based thread lifecycle. See [`381-clarification-thread-model.md`](381-clarification-thread-model.md) and [`382-clarification-answer-resolution.md`](382-clarification-answer-resolution.md). |
| `actions.py` | 101 | `classify_action()` — the sole deterministic turn-classification entry point, plus its phrase/marker sets. See [`371-conversation-architecture.md`](371-conversation-architecture.md) and the appendix [`../appendices/conversation-action-catalog.md`](../appendices/conversation-action-catalog.md). |
| `context.py` | 83 | `MAX_RECENT_TURNS_IN_CONTEXT = 6`, `build_turn_context()`, `compact_summary()`, `recent_turns()`. See [`387-context-window-policy.md`](387-context-window-policy.md), [`388-history-compaction-model.md`](388-history-compaction-model.md), [`389-conversation-summary-model.md`](389-conversation-summary-model.md). |
| `service.py` | 375 | `ConversationEngine` — `process_turn()` and its private `_handle_*`/`_resolve_designer_proposal()`/`_make_turn()` methods; the sole orchestrator. See [`391-conversation-designer-integration.md`](391-conversation-designer-integration.md). |

## Backend: modified files outside `conversation/`

| File | Change this Sprint |
|---|---|
| `backend/jewelmind/api/routes.py` | Added `POST /api/conversation/turn` (`conversation_turn_route`), constructed the same way as `designer_interpret_route` — a fresh `DesignerService`/`ConversationEngine` per request, honest about provider availability, no server-persisted session. |

## Backend tests

| File | Tests | Layer |
|---|---|---|
| `backend/tests/test_conversation.py` | 26 | Unit — hashing, references, clarifications, action classification, context. |
| `backend/tests/test_conversation_engine.py` | 15 | Integration — the 6 required CASE A–F scenarios plus staleness/reject/cancel/security/provider-failure. |
| `backend/tests/test_conversation_api.py` | 6 | API — `TestClient` round trips through `POST /api/conversation/turn`. |
| `backend/tests/test_conversation_corpus.py` | 82 | Corpus — 80 deterministic multi-turn cases across 17 categories, plus 2 meta-tests. |
| `backend/tests/test_conversation_schemas.py` | 8 | Schema — validates `specs/conversation/v1/` against the real engine's output. |

All five files use `FakeDesignerProvider` exclusively — no test in this list imports or calls `AnthropicDesignerProvider`.

## Frontend

| File | Responsibility |
|---|---|
| `frontend/src/components/ConversationPanel.tsx` | The mounted multi-turn natural-language entry point (superseding `DesignerPanel.tsx` in `App.tsx` — that component still exists, still tested standalone, just no longer rendered). Turn history, clarification card, proposal review card, Accept/Reject/Cancel. See [`395-studio-integration.md`](395-studio-integration.md). |
| `frontend/src/components/ConversationPanel.test.tsx` | 7 tests covering input state, proposal apply/reject, provider-unavailable, clarification choice, unsupported reporting, multi-turn history rendering. |
| `frontend/src/store/useConversationStore.ts` | New Zustand store: `session`, `setSession()`, `resetSession()`. Not persisted across page reloads (same deliberate scope limit as `useDesignIntentStore`). |
| `frontend/src/store/useConversationStore.test.ts` | 3 tests covering initial state, `setSession`, `resetSession`. |
| `frontend/src/api/types.ts` (Conversation Engine v1 section) | `ConversationActionType`, `ConversationSessionStatus`, `ClarificationStatus`, `ExpectedAnswerType`, `ConversationProposalStatus`, `ClarificationThread`, `ConversationProposal`, `ConversationSummary`, `ConversationDiagnostic`, `ConversationTurn`, `ConversationSession`, `ConversationTurnRequest`, `ConversationResult` — the TypeScript mirror of `schemas.py`. |
| `frontend/src/api/client.ts` | `interpretConversationTurn()` — the one new fetch wrapper, calling `POST /api/conversation/turn`. |
| `frontend/src/App.tsx` | `DesignerPanel` import/render replaced with `ConversationPanel`. |

## Machine-readable specification: `specs/conversation/v1/`

| Path | Contents |
|---|---|
| `README.md` | Explains the schema set and the generation/validation discipline. |
| 9 `*.schema.json` files | `conversation-action`, `clarification-thread`, `clarification-answer`, `conversation-state`, `turn-context`, `conversation-turn`, `conversation-summary`, `conversation-session`, `conversation-result`. |
| `examples/` (7 files) | One real generated `ConversationResult` flow per required Sprint 12 scenario (create-and-refine, intent-only-refinement, clarification-flow, correction-flow, unsupported-request-flow, preserve-unspecified-values, cancelled-proposal-flow). |
| `test-vectors/` (7 files) | `state-transition-vectors`, `reference-resolution-vectors`, `clarification-resolution-vectors`, `correction-vectors`, `preservation-vectors`, `context-compaction-vectors`, `stale-context-vectors` — all generated by actually running the real engine. |

## What is deliberately absent from this table

No file under `backend/jewelmind/domain/`, `backend/jewelmind/validation/`, or `backend/jewelmind/geometry/` appears here, and no file under `backend/jewelmind/designer/` or `backend/jewelmind/design_intent/` was modified this Sprint (verify via `git diff --stat` against those directories) — Conversation's entire footprint is the new `conversation/` package, one new API route, the new frontend files above, and the machine-readable spec. This absence is itself evidence for [`391-conversation-designer-integration.md`](391-conversation-designer-integration.md) and [`392-conversation-intent-integration.md`](392-conversation-intent-integration.md)'s findings: Conversation orchestrates, it does not duplicate.

## Cross-references

- [`370-conversation-governance.md`](370-conversation-governance.md).
- [`../appendices/conversation-code-mapping.md`](../appendices/conversation-code-mapping.md) — the denser, CONV-GOV-rule-indexed appendix version of this same territory.
- [`../appendices/conversation-test-matrix.md`](../appendices/conversation-test-matrix.md) — the test-file-indexed counterpart to this doc's test-file table.
