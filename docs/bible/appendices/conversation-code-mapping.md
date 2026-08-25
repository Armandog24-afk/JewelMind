---
id: JM-BIBLE-A79
title: "Appendix: Conversation Code Mapping"
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

# Appendix: Conversation Code Mapping

A denser, table-only re-mapping of [`370-conversation-governance.md`](../14-conversation/370-conversation-governance.md)'s own 20 CONV-GOV rules, adding the specific real test(s) that exercise each — largely a structured re-table of that document's own content, per this appendix's brief. Mirrors [`designer-code-mapping.md`](designer-code-mapping.md) and [`intent-code-mapping.md`](intent-code-mapping.md)'s style: honest about a rule having only indirect or structural coverage rather than forcing a weak mapping.

| Rule | Real function/file | Real test(s) |
|---|---|---|
| **CONV-GOV-001** (conversation state never replaces canonical JDL) | `ConversationSession` (`conversation/schemas.py`) — no `JewelryDefinition` field, only `currentJDLHash` | No dedicated test asserts the field's absence directly; verified structurally by `schemas.py`'s own field list and by every test in `test_conversation_api.py` sending `currentJDL` fresh on every request. |
| **CONV-GOV-002** (accepted JDL remains authoritative) | `ConversationEngine._handle_accept()` (`service.py`) — returns the already-computed `candidateJDL`, never stores it | `TestCaseA_TechnicalModifyPreservesUnrelatedFields` (`test_conversation_engine.py`), `TestStaleProposalProtection::test_accepting_against_the_same_unchanged_jdl_succeeds` |
| **CONV-GOV-003** (accepted DesignIntent remains authoritative) | `ConversationSession.currentIntentHash` (`schemas.py`), `state.intent_hash()` | `test_conversation.py::TestHashing::test_intent_hash_changes_when_intent_changes` |
| **CONV-GOV-004** (history is evidence, never authoritative) | `context.py::compact_summary()`/`build_turn_context()` never read/write `currentJDL`/`currentDesignIntent` | Partial — indirectly demonstrated by `TestCaseA_TechnicalModifyPreservesUnrelatedFields` re-supplying `currentJDL` fresh on every call; no test asserts the negative property directly. |
| **CONV-GOV-005** (unaccepted proposal never silently mutates) | `ConversationProposal.status` starts `"ACTIVE"` (`schemas.py`); nothing in `process_turn()` applies it as a side effect | `TestRejectAndCancel::test_reject_discards_proposal_without_mutation`, corpus cases `proposal-reject-01`/`02` |
| **CONV-GOV-006** (unspecified technical values preserved) | `ConversationEngine._handle_designer_routed()` calls `DesignerService.interpret()` with `interactionMode="MODIFY"` — never builds its own patch | `TestCaseA_TechnicalModifyPreservesUnrelatedFields`, `TestCaseD_PreserveStoneWhileChangingMaterial`, corpus category `PRESERVE_UNSPECIFIED` (6 cases), `specs/conversation/v1/test-vectors/preservation-vectors.json` |
| **CONV-GOV-007** (a clarification answer resolves only its own question) | `ConversationEngine._handle_answer_clarification()` reads `session.pendingClarification` (the single open thread); `clarifications.close_answered()` closes exactly that thread | `test_conversation.py::TestActionClassification::test_pending_clarification_always_wins` (confirms an open thread always captures the next turn); `TestCaseC_ClarificationThenResolution` |
| **CONV-GOV-008** (stale context must not overwrite newer accepted state) | `state.refresh_hashes()`, `state.is_proposal_stale()` (`state.py`) | `test_conversation.py::TestHashing::test_is_proposal_stale_true_when_jdl_differs`, `TestStaleProposalProtection` (both tests, `test_conversation_engine.py`), corpus category `STALE_CONTEXT` (2 cases) |
| **CONV-GOV-009** (references resolve against structured context, never free association) | `references.py::resolve_implicit_target()` | `test_conversation.py::TestReferences` (all 8 tests) |
| **CONV-GOV-010** (ambiguous references trigger clarification, never a guess) | `ConversationEngine._handle_designer_routed()` opening a `REQUEST_CLARIFICATION` thread when `is_ambiguous=True` | `test_conversation.py::TestReferences::test_bare_pronoun_with_no_context_is_ambiguous`, corpus category `AMBIGUOUS_REFERENCE` (3 cases) |
| **CONV-GOV-011** (intent-only changes never mark geometry stale) | `ConversationEngine._resolve_designer_proposal()`'s `technical_changes`/`intent_changes` split (`service.py`); frontend `proposal.diff.some(d => d.changed)` gate (`DesignerPanel.tsx`, reused by `ConversationPanel.tsx`) | `TestCaseB_IntentOnlyNeverStalesGeometry` |
| **CONV-GOV-012** (geometry-driving accepted changes do mark geometry stale) | The existing `withUpdatedDefinition()` path (Sprint 1), reused unchanged via `applyDesignerProposal()` | No new backend test — this is a frontend-store guarantee predating this Sprint, covered by `frontend/src/store/useProjectStore.test.ts`, not re-tested here. |
| **CONV-GOV-013** (provider failure must not affect manual Studio operation) | `ConversationPanel.tsx` only disables its own input while `isLoading` | `test_conversation_api.py::test_manual_endpoints_are_unaffected_when_conversation_provider_is_unavailable` (backend analog: `/api/health` stays 200 when the Designer provider is unavailable); frontend behavior verified live per `docs/bible/14-conversation/SPRINT-12-VALIDATION-REPORT.md`, not by an automated frontend test in this appendix's scope. |
| **CONV-GOV-014** (Conversation stays constrained to jewelry-design interaction) | `designer_normalizer.detect_prompt_injection_risk()` run on every turn in `ConversationEngine.process_turn()` before classification | `TestSecurity::test_prompt_injection_is_rejected` (`test_conversation_engine.py`), corpus category `MALICIOUS_HISTORY` (6 cases), `test_conversation_api.py::test_turn_rejects_malicious_text_with_400` |
| **CONV-GOV-015** (provider must not receive unlimited history) | `context.py::MAX_RECENT_TURNS_IN_CONTEXT = 6` | `test_conversation.py::TestContext::test_compact_summary_preserves_accepted_decisions_from_older_turns` (uses 9 turns, exceeding the bound of 6); `specs/conversation/v1/test-vectors/context-compaction-vectors.json` |
| **CONV-GOV-016** (summaries never replace exact accepted state) | `TurnContext.activeProposalId`/`pendingClarificationQuestion` (`schemas.py`) always structured/exact, never derived from `compactConversationSummary` | `test_conversation.py::TestContext::test_build_turn_context_reflects_pending_clarification` |
| **CONV-GOV-017** (corrections must be explicitly represented) | `ConversationEngine._handle_designer_routed()` sets `session.activeProposal.status = "SUPERSEDED"` before building the new proposal | `TestCaseF_CorrectionSupersedesWithoutIntermediateMutation`, corpus category `PROPOSAL_CORRECTION` (5 cases) |
| **CONV-GOV-018** (rejected/cancelled proposals never affect accepted state) | `ConversationEngine._handle_reject()`/`_handle_cancel()` only clear `session.activeProposal`/`session.pendingClarification` | `TestRejectAndCancel` (all 4 tests, `test_conversation_engine.py`), corpus category `PROPOSAL_REJECTION` (2 cases) |
| **CONV-GOV-019** (every accepted change is auditable as a structured diff) | `ConversationEngine._handle_accept()` extends `session.acceptedChangeHistory`/`session.summary.acceptedDecisions` from `DesignerProposal.diff` | `TestCaseA_TechnicalModifyPreservesUnrelatedFields` (asserts `r3.turn.technicalChanges == ["material.metal"]`) |
| **CONV-GOV-020** (Conversation cannot bypass Designer/JDL/Forge validation) | Every `MODIFY_DESIGN_PROPOSAL`/`CREATE_DESIGN_PROPOSAL`-routed turn calls the real `DesignerService.interpret()`; no `cadquery` import anywhere in `backend/jewelmind/conversation/` | Verified structurally (no such import exists in the package); exercised functionally by every corpus case and `test_conversation_api.py::test_turn_with_fake_provider_returns_a_proposal`, since every one of them only produces a `candidateJDL` via the real Designer pipeline. |

## Notes grounded in the real code

- CONV-GOV-001, CONV-GOV-004, and CONV-GOV-012 are marked with partial or indirect coverage rather than a single named test, matching this Bible's own established pattern (see `intent-test-matrix.md`'s "Notes on honesty of coverage") of not forcing a weak mapping where the underlying property is structural rather than behaviorally test-asserted.
- CONV-GOV-013's frontend half (Studio's `ConfigurationPanel` staying interactive) is a UI claim verified by a live browser session during this Sprint's own validation pass, not by an automated frontend test — the backend analog cited here (`/api/health` unaffected) is the closest automated equivalent this appendix could ground the rule in.
