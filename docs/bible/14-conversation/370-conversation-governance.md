---
id: JM-BIBLE-370
title: Conversation Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-290
  - JM-BIBLE-330
related_documents:
  - JM-BIBLE-371
implementation_status: current
professional_validation: not_required
normative: true
---

# Conversation Governance

## CONV-GOV-001 through CONV-GOV-020

| ID | Rule |
|---|---|
| **CONV-GOV-001** | Conversation state must never replace canonical JDL. `ConversationSession` (`backend/jewelmind/conversation/schemas.py`) carries no `JewelryDefinition` field at all — only `currentJDLHash`, a content hash of whatever the caller's own `currentJDL` was on this request. It is not, and must never become, a second source of design truth. |
| **CONV-GOV-002** | Accepted JDL remains authoritative. `ConversationEngine` never stores or mutates a `JewelryDefinition` server-side; `_handle_accept()` (`service.py`) only confirms a proposal is safe to apply and returns the already-computed `candidateJDL` for the caller to apply through the same `useProjectStore.applyDesignerProposal()` path Designer's own UI already uses. |
| **CONV-GOV-003** | Accepted DesignIntent remains authoritative. Symmetrically, `ConversationSession` carries `currentIntentHash`, never a `DesignIntent` object; the frontend's `useDesignIntentStore.applyIntent()` remains the only place a `DesignIntent` is actually stored. |
| **CONV-GOV-004** | Conversation history is evidence/context, never authoritative. `ConversationSummary` (`compact_summary()` in `context.py`) exists purely to give a provider bounded context; nothing in `ConversationEngine` ever reconstructs `currentJDL`/`currentDesignIntent` by replaying `session.turns` — both always come fresh from the caller on every request (see [`377-design-state-synchronization.md`](377-design-state-synchronization.md)). |
| **CONV-GOV-005** | An unaccepted proposal never silently mutates the current design. `ConversationProposal.status` starts `ACTIVE` and only becomes `ACCEPTED` through an explicit `ACCEPT_PROPOSAL` turn (`_handle_accept()`); nothing in `process_turn()` applies a candidate JDL as a side effect of creating or reviewing it. |
| **CONV-GOV-006** | Unspecified technical values must be preserved during modification. Conversation never constructs its own JDL patch — every `MODIFY_DESIGN_PROPOSAL`-routed turn calls the real `DesignerService.interpret()` with `interactionMode="MODIFY"`, which is what actually preserves every field the request didn't touch (Designer's own DESIGNER-GOV rule, reused here rather than re-implemented — see [`391-conversation-designer-integration.md`](391-conversation-designer-integration.md)). Verified live by `test-vectors/preservation-vectors.json`. |
| **CONV-GOV-007** | A clarification answer resolves only its own question. `_handle_answer_clarification()` reads `session.pendingClarification` — the one thread currently open — and `clarifications.close_answered()` closes exactly that thread; there is no code path that resolves a different, unrelated open question with an answer meant for another. |
| **CONV-GOV-008** | Stale conversational context must not overwrite newer accepted state. `state.refresh_hashes()` recomputes `currentJDLHash`/`currentIntentHash` from the caller's actual current values on every single request (never trusted from a prior turn), and `state.is_proposal_stale()` compares a proposal's `baseDefinitionHash`/`baseIntentHash` against them before `_handle_accept()` will apply anything — see [`402-stale-context-and-concurrent-editing.md`](402-stale-context-and-concurrent-editing.md). |
| **CONV-GOV-009** | References ("it", "that", "the band", "leave the stone") resolve against structured current context, never free association. `references.py::resolve_implicit_target()` only ever returns a target that is an explicit vocabulary match, a safe material-word match, or `session.lastReferencedTarget` — never a guess derived from the pronoun text alone. |
| **CONV-GOV-010** | Ambiguous references trigger clarification, never arbitrary mutation. When `resolve_implicit_target()` reports `is_ambiguous=True` (a bare pronoun with a comparative/dimensional marker and no established topic), `_handle_designer_routed()` opens a `REQUEST_CLARIFICATION` thread instead of guessing a target — it never proceeds to call Designer with an unresolved reference. |
| **CONV-GOV-011** | Intent-only changes must never mark geometry stale. `_resolve_designer_proposal()` only calls `applyDesignerProposal()` (frontend) when `proposal.diff.some(d => d.changed)` is true; a proposal with zero technical `diff` entries and only `designIntent.statements` never touches `currentDefinition`/`isStale`. Verified by CASE B (`TestCaseB_IntentOnlyNeverStalesGeometry`). |
| **CONV-GOV-012** | Geometry-driving accepted changes do mark geometry stale. The same `applyDesignerProposal()` call is the existing `withUpdatedDefinition()` path (Sprint 1's own mechanism) — a real technical field change continues to set `isStale: true` exactly as it always has; Conversation adds no exception to this. |
| **CONV-GOV-013** | Provider failure must not affect manual Studio operation. A `DESIGNER_PROVIDER_UNAVAILABLE` (503) response leaves `ConfigurationPanel` fully interactive; `ConversationPanel.tsx` only disables its own input while `isLoading`, never any other part of Studio. Verified live (this Sprint's own browser verification pass, see [`SPRINT-12-VALIDATION-REPORT.md`](SPRINT-12-VALIDATION-REPORT.md)). |
| **CONV-GOV-014** | Conversation must stay constrained to jewelry-design interaction. `designer_normalizer.detect_prompt_injection_risk()` (Designer's existing screen, Sprint 10) runs on every turn's raw text before classification — Conversation adds no separate, weaker entry point around it (see [`397-conversation-security.md`](397-conversation-security.md)). |
| **CONV-GOV-015** | The provider must not receive unlimited history. `context.py::MAX_RECENT_TURNS_IN_CONTEXT = 6` bounds what `build_turn_context()` includes — a turn-count bound, deliberately not an invented, unverifiable token budget (see [`387-context-window-policy.md`](387-context-window-policy.md)). |
| **CONV-GOV-016** | Summaries never replace exact accepted state. `compact_summary()` only ever compacts turns that have already scrolled out of the recent window; `TurnContext`'s `activeProposalId`/`pendingClarificationQuestion` fields — structured, exact, current — are never derived from the summary. |
| **CONV-GOV-017** | Corrections must be explicitly represented. A turn arriving while a proposal is `ACTIVE` and not matching an accept/reject phrase classifies as `MODIFY_DESIGN_PROPOSAL` (a correction), which supersedes (not merges into) the prior proposal — `session.activeProposal.status` becomes `SUPERSEDED` before the new one is created (`_handle_designer_routed()`). See [`383-correction-model.md`](383-correction-model.md). |
| **CONV-GOV-018** | Rejected/cancelled proposals never affect accepted state. `_handle_reject()` and `_handle_cancel()` only ever clear `session.activeProposal`/`session.pendingClarification` to `None` — neither calls anything that could write to `session.acceptedChangeHistory` or `session.summary.acceptedDecisions`. |
| **CONV-GOV-019** | Every accepted change is auditable as a structured diff. `_handle_accept()` extends `session.acceptedChangeHistory` and `session.summary.acceptedDecisions` from the real `DesignerProposal.diff`/`designIntent.statements` — never from `turn.sourceText` prose. See [`385-conversational-diff-model.md`](385-conversational-diff-model.md). |
| **CONV-GOV-020** | Conversation cannot bypass Designer/JDL validation/Forge. Every `MODIFY_DESIGN_PROPOSAL`/`CREATE_DESIGN_PROPOSAL`-routed turn calls the real `DesignerService.interpret()`, which itself runs the real `JewelryDefinition.model_validate()` and `validate_definition()` — `backend/jewelmind/conversation/` contains no direct `cadquery` import, no direct Forge rule evaluation, and no code path that constructs a `candidateJDL` without going through Designer first. |

## Relationship to LAW-003 and LAW-011

CONV-GOV-020 is this Sprint's restatement of [`LAW-003`](../00-foundation/004-jewelmind-constitution.md) ("no runtime LLM dependency for deterministic geometry generation") at the interaction layer: an LLM (via `DesignerProvider`) may help *interpret* a turn, but it never decides geometry directly, and it is never the only gate a change passes through. This document, together with the code changes it governs, is itself an instance of [`LAW-011`](../00-foundation/004-jewelmind-constitution.md) ("tests and documentation must accompany architectural changes").

## When an ADR is required

Letting Conversation write directly to `candidateJDL` without routing through `DesignerService`, moving conversation session persistence server-side, changing which layer owns staleness detection, or any change that violates CONV-GOV-001 through 020 without superseding this document first.

## When an RFC is required

A new conversational capability beyond the 13 `ConversationActionType` values, multi-session/multi-user conversation, voice or image input to Conversation, or long-term personal memory across sessions; see [`404-conversation-gap-analysis-and-open-questions.md`](404-conversation-gap-analysis-and-open-questions.md).
