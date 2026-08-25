---
id: JM-BIBLE-371
title: Conversation Architecture
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
  - JM-BIBLE-372
  - JM-BIBLE-391
implementation_status: current
professional_validation: not_required
normative: false
---

# Conversation Architecture

## Pipeline

Same shape as the README, restated here because every subsequent document in this Sprint refers back to a stage name in this diagram:

```
USER TURN
  ↓
CONVERSATION ENGINE        (this Sprint — interaction state only)
  ↓
TURN CONTEXT RESOLUTION
  ↓
DESIGNER                   (Sprint 10 — technical extraction, unchanged)
  ↓
DESIGN INTENT MODEL        (Sprint 11 — semantic extraction, unchanged)
  ↓
STRUCTURED PROPOSAL
  ↓
CLARIFICATION / REVIEW
  ↓
ACCEPTED STATE CHANGE
  ↓
JDL + DESIGN INTENT
  ↓
FORGE
  ↓
ALCHEMIST
  ↓
ATLAS
```

Conversation Engine sits entirely inside the first three stages. Everything from DESIGNER downward is Sprint 10/11 machinery, invoked, never reimplemented — see [`391-conversation-designer-integration.md`](391-conversation-designer-integration.md) and [`392-conversation-intent-integration.md`](392-conversation-intent-integration.md).

## Module layout

`backend/jewelmind/conversation/`:

| File | Lines (approx.) | Responsibility |
|---|---|---|
| `__init__.py` | 12 | Package docstring restating the core principle; no exports. |
| `errors.py` | 85 | `AppError` subclasses for conditions that abort a request (`ConversationInvalidStateError`, `ConversationNoPendingClarificationError`, `ConversationProposalSupersededError`, `ConversationStaleContextError`, `ConversationProviderFailedError`, `ConversationContextTooLargeError`, `ConversationActionUnsupportedError`), plus the 3 diagnostic-only string codes and `ALL_CONVERSATION_ERROR_CODES`. |
| `schemas.py` | 170 | Every Pydantic model — `ConversationSession`, `ConversationTurn`, `ClarificationThread`, `ClarificationAnswer`, `ConversationProposal`, `ConversationSummary`, `ConversationDiagnostic`, `TurnContext`, `ConversationTurnRequest`, `ConversationResult` — and the 5 `Literal` type aliases (`ConversationActionType`, `SessionStatus`, `ClarificationStatus`, `ExpectedAnswerType`, `ProposalStatus`). |
| `state.py` | 102 | `intent_hash()`, `new_session()`, `refresh_hashes()`, `is_proposal_stale()`, `make_proposal()` — session creation and the hash-based staleness mechanism. |
| `references.py` | 135 | `find_explicit_target()`, `find_preserve_target()`, `mentions_material_word()`, `mentions_comparative_marker()`, `resolve_implicit_target()` — deterministic reference resolution. |
| `clarifications.py` | 90 | `open_clarification()`, `try_resolve_answer()`, `close_answered()`, `cancel()`, `supersede()` — the `ClarificationThread` lifecycle. |
| `actions.py` | 102 | `classify_action()` — the single deterministic function that maps raw turn text plus session state to one of the 13 `ConversationActionType` values. |
| `context.py` | 84 | `build_turn_context()`, `compact_summary()`, `recent_turns()` — bounded provider-facing context and deterministic summarization. `MAX_RECENT_TURNS_IN_CONTEXT = 6`. |
| `service.py` | 376 | `ConversationEngine` — the orchestration class with `process_turn()` and its private `_handle_*`/`_resolve_designer_proposal()`/`_make_turn()` helpers. The only module that imports `DesignerService`. |

This is the same nine-file, single-package shape Designer (`backend/jewelmind/designer/`) and Design Intent (`backend/jewelmind/design_intent/`) already use — one `schemas.py`, one `errors.py`, one or more deterministic-logic modules, one orchestration `service.py`.

## Stateless-per-request architecture

`ConversationEngine` is constructed fresh on every HTTP call, exactly like `DesignerService`. `backend/jewelmind/api/routes.py::conversation_turn_route()` reads:

```python
designer_service = DesignerService(provider=get_designer_provider())
engine = ConversationEngine(designer_service=designer_service)
return engine.process_turn(request)
```

This mirrors `designer_interpret_route()` a few lines above it, which does the identical `DesignerService(provider=get_designer_provider())` construction per request. Neither route keeps a server-side singleton or session store. `ConversationEngine.__init__` takes only a `designer_service: DesignerService` — there is no database handle, no cache, no in-memory session dictionary. Every piece of state `process_turn()` needs (the session, the current JDL, the current DesignIntent) arrives in the `ConversationTurnRequest` body and is returned in the `ConversationResult` body for the caller to send back on the next turn. See [`373-conversation-session-lifecycle.md`](373-conversation-session-lifecycle.md).

## Import boundary

`backend/jewelmind/conversation/` imports, across its files:

- `jewelmind.designer` — `DesignerService` (`service.py`), `NaturalLanguageDesignRequest`/`DesignerProposal` schemas (`service.py`, `schemas.py`), `jewelmind.designer.errors.DesignerSecurityRejectedError` (`service.py`), and `jewelmind.designer.normalizer` for `detect_prompt_injection_risk()` and `is_numeric_field()` (`service.py`).
- `jewelmind.design_intent.vocabulary` — only `TARGET_SYNONYMS`, imported by `references.py`. No other Design Intent module (`normalizer.py`, `resolver.py`, `conflicts.py`, `diagnostics.py`) is imported anywhere in `conversation/`.
- `jewelmind.design_intent.schemas` — `DesignIntent`, imported by `schemas.py` and `state.py` purely as a type for fields/parameters (`currentDesignIntent`, `intent_hash()`'s argument).
- `jewelmind.domain.schema` — `JewelryDefinition`, imported by `schemas.py` and `state.py`, again purely as a type.
- `jewelmind.utils.hashing` — `definition_hash()`, imported by `state.py`.
- `jewelmind.api.errors` — `AppError`, the base class every conversation error extends (`errors.py`, `service.py`).

`backend/jewelmind/conversation/` does **not** import `cadquery` or anything under `jewelmind.geometry`, `jewelmind.exporters`, or `jewelmind.validation` (Forge). A grep of the package for `cadquery` and `jewelmind.geometry` returns no matches. This is CONV-GOV-020 verified at the import-graph level, not just asserted in prose.

## Where Studio calls in

`POST /api/conversation/turn` (`backend/jewelmind/api/routes.py`) is the only HTTP entry point. The frontend counterpart is `frontend/src/store/useConversationStore.ts` calling into `frontend/src/api/client.ts`, rendered by `frontend/src/components/ConversationPanel.tsx` — see [`395-studio-integration.md`](395-studio-integration.md).
