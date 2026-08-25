---
id: JM-BIBLE-400
title: Conversation Evaluation Framework
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
  - JM-BIBLE-401
  - JM-BIBLE-359
implementation_status: current
professional_validation: not_required
normative: true
---

# Conversation Evaluation Framework

Mirrors [`13-design-intent/359-intent-evaluation-framework.md`](../13-design-intent/359-intent-evaluation-framework.md)'s structure: name the metrics, name the real test(s) that proxy for each today, and state honestly what this framework is not.

## The 11 metrics

| Metric | What it measures | Real test class that exercises it |
|---|---|---|
| `MULTI_TURN_STATE_RETENTION` | Whether a `ConversationSession`'s fields (`acceptedChangeHistory`, `lastReferencedTarget`, `summary`) correctly carry forward across turns without loss. | `TestCaseA_TechnicalModifyPreservesUnrelatedFields` (`backend/tests/test_conversation_engine.py`) — a 3-turn sequence where the second accepted proposal's field survives into a third, independent turn. |
| `UNSPECIFIED_FIELD_PRESERVATION` | Whether a field the user's turn never mentioned survives a `MODIFY` correction untouched. | `TestCaseA_TechnicalModifyPreservesUnrelatedFields`, `TestCaseD_PreserveStoneWhileChangingMaterial` — plus the corpus's `PRESERVE_UNSPECIFIED` category (6 cases, `backend/tests/test_conversation_corpus.py`). |
| `REFERENCE_RESOLUTION_ACCURACY` | Whether "it"/"that"/an explicit component name/a material word resolves to the correct target, and whether an unresolvable bare pronoun is correctly reported as ambiguous rather than guessed. | `test_conversation.py::TestReferences` (8 tests); corpus categories `REFERENCE_TO_PREVIOUS_COMPONENT` (5 cases), `PRONOUN_RESOLUTION` (2 cases), `AMBIGUOUS_REFERENCE` (3 cases). |
| `CLARIFICATION_RESOLUTION_ACCURACY` | Whether a clarification answer is correctly validated against its `ExpectedAnswerType` (`NUMERIC`/`ENUM_CHOICE`/`FREE_TEXT`/`CONFIRMATION`) and, once accepted, correctly applied. | `TestCaseC_ClarificationThenResolution`; corpus categories `CLARIFICATION` (3 cases) and `CLARIFICATION_CORRECTION` (1 case, an unresolvable answer leaving the thread open). |
| `CORRECTION_ACCURACY` | Whether a correction to an active proposal replaces (never merges into) the prior value, and never mutates the original design. | `TestCaseF_CorrectionSupersedesWithoutIntermediateMutation`; corpus category `PROPOSAL_CORRECTION` (5 cases). |
| `STALE_CONTEXT_REJECTION` | Whether an accept against a JDL/DesignIntent that no longer matches the proposal's base hashes is correctly rejected rather than silently applied. | `TestStaleProposalProtection` (both tests); corpus category `STALE_CONTEXT` (2 cases); `specs/conversation/v1/test-vectors/stale-context-vectors.json`. See [`402-stale-context-and-concurrent-editing.md`](402-stale-context-and-concurrent-editing.md). |
| `INTENT_PRESERVATION` | Whether a pure design-intent statement survives into the proposal without being converted into a technical field, and is correctly labeled `MODIFY_INTENT`. | `TestCaseB_IntentOnlyNeverStalesGeometry`; corpus category `INTENT_ONLY_MODIFICATION` (14 cases). |
| `UNSUPPORTED_FEATURE_RETENTION` | Whether an unsupported feature is reported honestly (never silently dropped or approximated) and remains recorded in `session.summary.unsupportedDiscussed` across a follow-up no-op turn. | `TestCaseE_UnsupportedThenAbandoned`; corpus categories `UNSUPPORTED_FEATURE` (3 cases) and `PARTIAL_SUPPORT` (1 case, an unsupported feature reported alongside a real technical change in the same turn). |
| `HALLUCINATED_CHANGE_RATE` | Whether any turn ever produces a technical field change the user's text did not request. | Every `field_unchanged(...)` assertion across the corpus's `PRESERVE_UNSPECIFIED` category, plus `TestCaseA`/`TestCaseD`'s explicit unrelated-field assertions. |
| `UNAUTHORIZED_STATE_MUTATION_RATE` | Whether an unaccepted proposal, a rejected proposal, or a cancelled interaction ever mutates `acceptedChangeHistory`/`summary.acceptedDecisions`. | `TestRejectAndCancel` (all 4 tests); corpus category `PROPOSAL_REJECTION` (2 cases); `TestCaseF`'s explicit assertion that `JewelryDefinition().setting.prongCount == 6` (the schema default) after a superseded proposal changed it to a different value only in the discarded candidate. |
| `CONVERSATION_COMPLETION_RATE` | Whether a multi-turn interaction (create → clarify → correct → accept, or create → report-unsupported → abandon) reaches a real terminal outcome (`ACCEPT_PROPOSAL`, `REJECT_PROPOSAL`, or `NO_CHANGE`) rather than getting stuck. | All 6 CASE A-F classes collectively (each is itself a complete multi-turn flow reaching a terminal action); the corpus's `CREATE_THEN_MODIFY` category (3 cases, each a create-accept-modify sequence). |

## `HALLUCINATED_CHANGE_RATE` and `UNAUTHORIZED_STATE_MUTATION_RATE` are demonstrated to be zero — not merely approaching zero

This distinction matters. On the current deterministic corpus (82 collected tests in `test_conversation_corpus.py`, 15 in `test_conversation_engine.py`, all running exclusively against `FakeDesignerProvider`), every case that asserts a field-unchanged or no-mutation property does so as a hard `assert`, not a statistical sample — a single failing case fails the whole suite, and the whole suite passes today. This is the same status [`13-design-intent/359-intent-evaluation-framework.md`](../13-design-intent/359-intent-evaluation-framework.md) documents for Design Intent's own `FALSE_NUMERIC_RESOLUTION_RATE`: a provably-zero rate on a deterministic, exhaustively-checked corpus, not a live-traffic statistic. It says nothing about what rate a live, non-deterministic AI provider's actual outputs would produce in production — that would require the real observability instrumentation named as a gap in [`399-conversation-observability.md`](399-conversation-observability.md), which does not exist yet.

## What the 80-case corpus plus the 6 CASE A-F scenarios are, and are not, a proxy for today

`test_conversation_corpus.py`'s 80 parametrized cases and `test_conversation_engine.py`'s 6 CASE A-F integration tests together give direct, passing coverage for every metric in the table above except `CONVERSATION_COMPLETION_RATE`, which is only indirectly demonstrated (each test *is* a complete flow reaching a terminal state, but nothing counts or tracks a completion rate across many independent real sessions). None of these metrics are running production telemetry — there is no dashboard, no live-traffic sampling, and no scoring service. They are the vocabulary this Bible uses to reason about Conversation's quality, backed entirely by deterministic `FakeDesignerProvider`-only tests, exactly as [`401-conversation-test-corpus.md`](401-conversation-test-corpus.md) documents for the corpus itself.

## What this framework is not

It is not a live dashboard, a scoring service, or an automated regression gate beyond the existing pytest suite. It does not measure how well a real (non-fake) `DesignerProvider`'s natural-language interpretation performs — that quality question belongs to Designer's own evaluation framework (`docs/bible/12-designer/318-designer-evaluation-framework.md`), which Conversation inherits unchanged rather than re-measuring.

## Cross-references

- [`13-design-intent/359-intent-evaluation-framework.md`](../13-design-intent/359-intent-evaluation-framework.md) — the structural template this document follows.
- `docs/bible/12-designer/318-designer-evaluation-framework.md` — the technical-interpretation-quality metrics this framework does not duplicate.
- [`401-conversation-test-corpus.md`](401-conversation-test-corpus.md) — the corpus these metrics are proxied against, in full detail.
- [`399-conversation-observability.md`](399-conversation-observability.md) — the real telemetry gap that separates "provably zero on this corpus" from "measured zero in production."
