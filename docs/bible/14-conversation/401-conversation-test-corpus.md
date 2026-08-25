---
id: JM-BIBLE-401
title: Conversation Test Corpus
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
  - JM-BIBLE-400
  - JM-BIBLE-A78
implementation_status: current
professional_validation: not_required
normative: true
---

# Conversation Test Corpus

`backend/tests/test_conversation_corpus.py`'s own module docstring is the source of the requirement this document verifies against:

> Deterministic multi-turn test corpus for Conversation Engine v1. Every case is a short SEQUENCE of turns (1-3), each supplying the raw Designer response a correctly-behaving provider should have produced for that turn's text (never a live LLM call). At least 80 cases across the 17 categories from docs/bible/14-conversation/401-conversation-test-corpus.md and the Sprint 12 brief's section 39.

## 80 real cases, verified by grep, across 17 required categories

Counting the real `add(...)` calls (including those built inside `for` loops appending to `CASES`) in `test_conversation_corpus.py` gives exactly 80 cases, matching `test_corpus_has_at_least_80_cases()`'s own assertion and `test_corpus_covers_all_required_categories()`'s check that all 17 category names are present:

| Category | Real count |
|---|---|
| `CREATE_THEN_MODIFY` | 3 |
| `TECHNICAL_MODIFICATION` | 18 |
| `INTENT_ONLY_MODIFICATION` | 14 |
| `REFERENCE_TO_PREVIOUS_COMPONENT` | 5 |
| `PRONOUN_RESOLUTION` | 2 |
| `AMBIGUOUS_REFERENCE` | 3 |
| `CLARIFICATION` | 3 |
| `CLARIFICATION_CORRECTION` | 1 |
| `PROPOSAL_REJECTION` | 2 |
| `PROPOSAL_CORRECTION` | 5 |
| `PRESERVE_UNSPECIFIED` | 6 |
| `UNSUPPORTED_FEATURE` | 3 |
| `PARTIAL_SUPPORT` | 1 |
| `STALE_CONTEXT` | 2 |
| `MALICIOUS_HISTORY` | 6 |
| `ITALIAN` | 3 |
| `ENGLISH` | 3 |
| **Total** | **80** |

The full per-case breakdown (which `sourceText`/steps each ID covers) is already tabulated in [`../appendices/conversation-test-case-catalog.md`](../appendices/conversation-test-case-catalog.md) — this document summarizes rather than duplicating that table. Case IDs are not always contiguous within a category (e.g. `technical-mod-01`..`06`, then `07`..`12`, then `13`..`18` appear at different points in the file, since the corpus was built incrementally across several `for` loops); the appendix lists them in real `pytest` collection order.

Collecting the file directly (`pytest tests/test_conversation_corpus.py --collect-only -q`) yields 82 tests: the 80 parametrized `test_corpus_case` cases plus `test_corpus_has_at_least_80_cases` and `test_corpus_covers_all_required_categories`, the file's own two meta-tests confirming the corpus's own shape.

## Every case runs against `FakeDesignerProvider` — zero live AI calls in CI

`run_case()` constructs exactly one provider per case: `provider = FakeDesignerProvider()`, then sets `provider.response = step.raw` before each step and calls `eng.process_turn(request)`. Grepping every file under `backend/tests/test_conversation*.py` for `AnthropicDesignerProvider` or any other live-provider class finds no matches — only `FakeDesignerProvider` is ever imported or constructed in the entire Conversation test suite. This mirrors Designer's own Sprint 10 discipline (`docs/bible/12-designer/319-designer-test-corpus.md`) and Design Intent's Sprint 11 discipline (`13-design-intent/360-intent-test-corpus.md`): every deterministic case supplies the exact `RawDesignerResponse` a correctly-behaving provider *should* have produced for that turn's text, so the test proves Conversation's own orchestration logic (classification, reference resolution, staleness, preservation) rather than any live model's actual natural-language interpretation quality — that quality question belongs to Designer's own evaluation, not to this corpus.

## The 6 CASE A-F scenarios — a separate, more detailed integration layer

`backend/tests/test_conversation_engine.py` is a distinct file from the 80-case corpus, holding the 6 required multi-turn scenarios named directly in the Sprint 12 brief, each its own test class with a richer set of assertions than a single corpus case typically carries:

| Case | Class | What it proves |
|---|---|---|
| A | `TestCaseA_TechnicalModifyPreservesUnrelatedFields` | A 3-turn sequence (create solitaire in rose gold with six prongs → accept → change material to platinum) proves the prong count set two turns earlier, through an entirely different, already-accepted-and-cleared proposal, survives untouched into the new candidate. |
| B | `TestCaseB_IntentOnlyNeverStalesGeometry` | A pure aesthetic request produces zero changed technical `diff` entries and classifies as `MODIFY_INTENT`. |
| C | `TestCaseC_ClarificationThenResolution` | An underspecified technical request ("Allarga la fascia.") opens a real clarification thread, and the numeric answer that follows is correctly combined with the original question and applied to `candidateJDL.band.width`. |
| D | `TestCaseD_PreserveStoneWhileChangingMaterial` | An explicit "leave the stone as is" instruction alongside a material change leaves every stone field (`diameter`, `depth`) at the schema default while only the material field changes. |
| E | `TestCaseE_UnsupportedThenAbandoned` | An unsupported feature (halo) is reported honestly via `REPORT_UNSUPPORTED`, and a follow-up "Lascia perdere." resolves to a genuine `NO_CHANGE` with no proposal ever created. |
| F | `TestCaseF_CorrectionSupersedesWithoutIntermediateMutation` | A correction ("No, quattro griffe.") replaces rather than merges with the prior six-prong proposal, and `JewelryDefinition().setting.prongCount == 6` (the untouched schema default) proves the original design was never mutated by the superseded proposal. |

These 6 classes are not part of the 80-case corpus count — they live in a separate file, use a slightly different harness (`engine()`/`turn()` helpers rather than `run_case()`/`Case`/`Step`), and are explicitly named in the Sprint 12 brief as required scenarios distinct from the broader corpus. `test_conversation_engine.py` collects 15 tests total: the 6 CASE A-F classes plus `TestStaleProposalProtection` (2 tests), `TestRejectAndCancel` (4 tests), `TestSecurity` (1 test), and `TestProviderFailureDoesNotMutate` (2 tests) — see [`../appendices/conversation-test-matrix.md`](../appendices/conversation-test-matrix.md) for the verified count and its one documented discrepancy against the Sprint 12 brief's stated "16 tests."

## Cross-references

- [`../appendices/conversation-test-case-catalog.md`](../appendices/conversation-test-case-catalog.md) — the full per-case ID/category/description table.
- [`../appendices/conversation-test-matrix.md`](../appendices/conversation-test-matrix.md) — verified test counts across all five Conversation backend test files plus the two Conversation-specific frontend files.
- [`400-conversation-evaluation-framework.md`](400-conversation-evaluation-framework.md) — the metrics this corpus and the CASE A-F scenarios together proxy for.
- `docs/bible/12-designer/319-designer-test-corpus.md`, `13-design-intent/360-intent-test-corpus.md` — the Sprint 10/11 sibling documents this one follows in structure and in its `FakeDesignerProvider`-only discipline.
