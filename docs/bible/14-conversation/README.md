---
id: JM-BIBLE-CONVERSATION-README
title: Conversation Engine v1 — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-DESIGNER-README
  - JM-BIBLE-DESIGN-INTENT-README
related_documents:
  - JM-BIBLE-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Conversation Engine v1 — Index

This is **Sprint 12** of the Technical Bible: **Conversation Engine v1**. Designer (Sprint 10) interprets one natural-language request into one structured proposal; Design Intent (Sprint 11) gives subjective language a structured, non-numeric home. Neither, on its own, remembers what happened last turn. Conversation Engine is the interaction-state layer that makes progressive, multi-turn design refinement possible — "make it more classic", then "leave the stone as is", then "make the band wider" — while a fixed, non-negotiable principle holds: **conversation is a sequence of structured design transactions, not a stream of authoritative prose.**

**Read this README, then [`370-conversation-governance.md`](370-conversation-governance.md), before changing anything in `backend/jewelmind/conversation/` or `frontend/src/components/ConversationPanel.tsx`.**

## Where Conversation sits

Conversation sits above Designer and Design Intent, orchestrating both without duplicating either's logic, and — like both — has zero authority to bypass JDL/Forge validation:

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

Conversation Engine owns interaction state only — never geometry, never jewelry rules, never JDL semantics, never intent vocabulary, never manufacturing rules, never rendering, never export logic. It is not a chatbot: every meaningful turn resolves into exactly one of 13 canonical `ConversationActionType` values (see [`conversation-action.schema.json`](../../../specs/conversation/v1/conversation-action.schema.json)), never free-form assistant prose treated as ground truth.

## The core principle

> Conversation is a sequence of structured design transactions, not a stream of authoritative prose.

A turn's raw text is classified deterministically (`classify_action()`, never an LLM judgment call for this meta-level decision) into one action. Every action either produces a structured, reviewable artifact (a proposal, a clarification thread, an intent change) or an explicit no-op — never a mutation the user didn't structurally approve.

## Reading order

1. [`370-conversation-governance.md`](370-conversation-governance.md) — 20 non-negotiable rules (CONV-GOV-001 through 020).
2. [`371-conversation-architecture.md`](371-conversation-architecture.md), [`372-conversation-domain-model.md`](372-conversation-domain-model.md).
3. Session and turn shape: [`373-conversation-session-lifecycle.md`](373-conversation-session-lifecycle.md), [`374-conversation-turn-model.md`](374-conversation-turn-model.md), [`375-turn-context-model.md`](375-turn-context-model.md), [`376-conversation-state-machine.md`](376-conversation-state-machine.md), [`377-design-state-synchronization.md`](377-design-state-synchronization.md), [`378-turn-role-and-message-model.md`](378-turn-role-and-message-model.md).
4. Reference resolution: [`379-reference-resolution.md`](379-reference-resolution.md), [`380-pronoun-and-implicit-target-resolution.md`](380-pronoun-and-implicit-target-resolution.md).
5. Clarification: [`381-clarification-thread-model.md`](381-clarification-thread-model.md), [`382-clarification-answer-resolution.md`](382-clarification-answer-resolution.md).
6. Correction and lifecycle actions: [`383-correction-model.md`](383-correction-model.md), [`384-accept-reject-cancel-semantics.md`](384-accept-reject-cancel-semantics.md), [`385-conversational-diff-model.md`](385-conversational-diff-model.md), [`386-state-preservation-policy.md`](386-state-preservation-policy.md).
7. Context and history: [`387-context-window-policy.md`](387-context-window-policy.md), [`388-history-compaction-model.md`](388-history-compaction-model.md), [`389-conversation-summary-model.md`](389-conversation-summary-model.md), [`390-provider-context-contract.md`](390-provider-context-contract.md).
8. Integration: [`391-conversation-designer-integration.md`](391-conversation-designer-integration.md), [`392-conversation-intent-integration.md`](392-conversation-intent-integration.md), [`393-conversation-jdl-integration.md`](393-conversation-jdl-integration.md), [`394-conversation-forge-integration.md`](394-conversation-forge-integration.md), [`395-studio-integration.md`](395-studio-integration.md).
9. Cross-cutting: [`396-conversational-error-model.md`](396-conversational-error-model.md), [`397-conversation-security.md`](397-conversation-security.md), [`398-conversation-privacy.md`](398-conversation-privacy.md), [`399-conversation-observability.md`](399-conversation-observability.md).
10. Quality: [`400-conversation-evaluation-framework.md`](400-conversation-evaluation-framework.md), [`401-conversation-test-corpus.md`](401-conversation-test-corpus.md).
11. [`402-stale-context-and-concurrent-editing.md`](402-stale-context-and-concurrent-editing.md), [`403-current-code-mapping.md`](403-current-code-mapping.md), [`404-conversation-gap-analysis-and-open-questions.md`](404-conversation-gap-analysis-and-open-questions.md).

## Appendices

[`conversation-action-catalog.md`](../appendices/conversation-action-catalog.md), [`conversation-state-catalog.md`](../appendices/conversation-state-catalog.md), [`conversation-reference-catalog.md`](../appendices/conversation-reference-catalog.md), [`clarification-type-catalog.md`](../appendices/clarification-type-catalog.md), [`conversation-diagnostic-catalog.md`](../appendices/conversation-diagnostic-catalog.md), [`conversation-test-case-catalog.md`](../appendices/conversation-test-case-catalog.md), [`conversation-code-mapping.md`](../appendices/conversation-code-mapping.md), [`conversation-test-matrix.md`](../appendices/conversation-test-matrix.md) (`JM-BIBLE-A73` through `A80`, continuing directly from Sprint 11's last appendix, `A72`).

## Machine-readable specification

[`specs/conversation/v1/`](../../../specs/conversation/v1/README.md) holds 9 JSON Schemas, 7 examples, and 7 test-vector files, all generated by actually running the real `ConversationEngine` and its supporting modules — never hand-invented.

## The single most important finding of this Sprint

**The backend is stateless per request, exactly like Designer.** `ConversationEngine` never persists a `ConversationSession` server-side and never mutates a stored design itself — the entire session round-trips through the caller on every `POST /api/conversation/turn` call, and `ACCEPT_PROPOSAL` only confirms a proposal is safe to apply (via real content-hash staleness comparison, `state.is_proposal_stale()`) before returning the already-computed values for the frontend to apply through the *same* `applyDesignerProposal()`/`applyIntent()` paths Designer's own UI has used since Sprint 10. There is no new server-side mutation surface, and no new place a design can silently drift from what the user actually approved.

## Relationship to Sprint 10 and Sprint 11

Conversation adds no new technical extraction, unsupported-feature detection, field-provenance logic, or JDL proposal construction — every one of those still lives exclusively in `backend/jewelmind/designer/` and is reused as-is via `DesignerService.interpret()`. Conversation adds interaction-only capabilities on top: turn history, reference resolution, clarification-thread lifecycle, proposal correction/staleness, and deterministic action classification. Every Sprint 10/11 guarantee (JDL/Forge validation, provider abstraction, `FakeDesignerProvider`-only CI) is unchanged. See [`391-conversation-designer-integration.md`](391-conversation-designer-integration.md) and [`392-conversation-intent-integration.md`](392-conversation-intent-integration.md).

## Relationship to Sprint 13

[`15-professional-validation/`](../15-professional-validation/README.md) (Sprint 13) does not change how Conversation works. A design produced or modified through a multi-turn conversation is exactly as preliminary and unvalidated as one produced any other way — accepting a conversational proposal never confers any professional-validation status, and no conversation turn can create, modify, or reference a `ValidationRecord`.

## Validation of this sprint

See [`SPRINT-12-VALIDATION-REPORT.md`](SPRINT-12-VALIDATION-REPORT.md) for the checks run against this section and the findings from that pass.
