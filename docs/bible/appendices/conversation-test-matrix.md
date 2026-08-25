---
id: JM-BIBLE-A80
title: "Appendix: Conversation Test Matrix"
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

# Appendix: Conversation Test Matrix

Real counts verified by running `pytest tests/test_conversation*.py --collect-only -q` (backend) and `npm run test -- --run src/components/ConversationPanel.test.tsx src/store/useConversationStore.test.ts` (frontend) during this appendix's own preparation — not copied from the Sprint 12 brief without checking.

| Test file | Layer | Count (verified) | Key scenarios covered |
|---|---|---|---|
| `backend/tests/test_conversation.py` | Unit (backend, deterministic building blocks) | 26 | Hashing determinism/change-detection (`TestHashing`), reference resolution for explicit/implicit/ambiguous/material-word targets (`TestReferences`), clarification answer validation and thread immutability (`TestClarifications`), `classify_action()` branch coverage — pending-clarification priority, no-op, undo, start-over, preserve, default-to-modify (`TestActionClassification`), turn-context construction and summary compaction (`TestContext`). |
| `backend/tests/test_conversation_engine.py` | Integration (backend, `ConversationEngine.process_turn()`) | 15 | The 6 required CASE A-F scenarios (technical-preserve, intent-only-never-stale, clarify-then-resolve, preserve-stone, unsupported-then-abandon, correction-supersedes); stale-proposal rejection/acceptance (`TestStaleProposalProtection`); reject/cancel/defensive-guard behavior (`TestRejectAndCancel`, 4 tests); prompt-injection rejection (`TestSecurity`); provider-failure propagation, both Designer's own specific `AppError` and a generic wrapped exception (`TestProviderFailureDoesNotMutate`, 2 tests). **Note:** the Sprint 12 brief describes this file as having 16 tests ("16 tests incl. 6 required CASE A-F"); the real, verified collected count is **15** — reported here as found, not silently reconciled to the brief's number. |
| `backend/tests/test_conversation_api.py` | API (backend, `POST /api/conversation/turn` via `TestClient`) | 6 | 503 when no provider is configured; a successful proposal round-trip with `FakeDesignerProvider`; a full multi-turn accept round-trip through the HTTP layer; 400 on malicious input; 422 on an unknown request field (`extra="forbid"`); manual endpoints (`/api/health`) staying unaffected when the Designer provider is unavailable. |
| `backend/tests/test_conversation_corpus.py` | Corpus (backend, deterministic multi-turn natural-language cases) | 82 | 80 parametrized cases (`test_corpus_case`) across the 17 required categories (see [`conversation-test-case-catalog.md`](conversation-test-case-catalog.md)) + `test_corpus_has_at_least_80_cases` + `test_corpus_covers_all_required_categories`. |
| `backend/tests/test_conversation_schemas.py` | Schema (backend, `specs/conversation/v1/` vs. real implementation) | 8 | All 9 JSON Schemas are valid Draft 2020-12; all 7 examples validate against `conversation-result`/`conversation-session`/`conversation-turn` schemas; all 7 test-vector files exist and are non-empty; state-transition vectors validate against `conversation-state.schema.json`; every example shows genuinely distinct per-turn state (the mutable-session-snapshot regression guard); `create-and-refine.json` is reproducible by re-running the real `ConversationEngine` live and diffing against the recorded file (ID/timestamp fields stripped). |
| `frontend/src/components/ConversationPanel.test.tsx` | Frontend component | 7 | Send stays disabled until text is entered; a proposal review renders and Accept applies it to the design/intent stores; Reject applies nothing; an "unavailable" state renders without breaking manual editing when no provider is configured; a clarification card with enum choices sends the chosen option as the next turn; unsupported features surface without being silently dropped; multi-turn history renders compactly, differentiating the user's request from the interpreted result. |
| `frontend/src/store/useConversationStore.test.ts` | Frontend store | 3 | Starts with no current session; `setSession` replaces the session wholesale; `resetSession` clears back to `null`. |

## Totals

- **Backend Conversation tests: 137** (26 + 15 + 6 + 82 + 8), verified by `pytest tests/test_conversation.py tests/test_conversation_engine.py tests/test_conversation_api.py tests/test_conversation_corpus.py tests/test_conversation_schemas.py --collect-only -q`, matching the combined collection total for all five files run together.
- **Frontend Conversation tests: 10** (7 + 3) across the two Conversation-specific frontend test files. The Sprint 12 brief's "131 frontend tests total" figure refers to the entire frontend suite (all Sprints combined), not the Conversation-specific subset — this appendix reports only the Conversation-specific count, consistent with this table's own scope.

## Notes on honesty of coverage

- The one discrepancy found while verifying counts for this appendix is `test_conversation_engine.py`: the Sprint 12 brief states 16 tests; the real, collected count is 15 (6 CASE A-F + 2 `TestStaleProposalProtection` + 4 `TestRejectAndCancel` + 1 `TestSecurity` + 2 `TestProviderFailureDoesNotMutate` = 15). This is reported as found rather than adjusted to match the brief.
- Every other file's real count matches the brief's stated count exactly: `test_conversation.py` (26), `test_conversation_api.py` (6), `test_conversation_corpus.py` (82, i.e. "80 real multi-turn cases" plus its 2 meta-tests), `test_conversation_schemas.py` (8).
