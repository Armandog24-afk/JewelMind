---
id: JM-BIBLE-319
title: Designer Test Corpus
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-318
related_documents:
  - JM-BIBLE-320
implementation_status: current
professional_validation: not_required
normative: true
---

# Designer Test Corpus

The exhaustive case-by-category breakdown lives in [`designer-test-case-catalog.md`](../appendices/designer-test-case-catalog.md) — this document summarizes and explains rather than duplicating it.

## What the corpus is

`backend/tests/test_designer_corpus.py::CASES` holds 62 real natural-language cases spanning all 11 required categories: `EXACT_SUPPORTED`, `SUPPORTED_SYNONYM`, `MULTI_FIELD`, `MODIFY_EXISTING`, `AMBIGUOUS`, `VAGUE`, `UNSUPPORTED`, `PARTIALLY_SUPPORTED`, `MALICIOUS`, `INVALID_NUMERIC`, `MULTILINGUAL`. `test_corpus_covers_all_11_named_categories` asserts exact coverage of that set; `test_corpus_has_at_least_50_cases` asserts a floor of 50, which the real 62 satisfies with margin.

## `FakeDesignerProvider`-only discipline

Every one of the 62 cases runs against `FakeDesignerProvider`, constructed with a fixed `RawDesignerResponse` matching what a correctly-behaving provider would have extracted from that case's input text — never a live AI call. `test_designer_corpus.py`'s own module docstring states this discipline directly. This means the corpus tests Designer's deterministic pipeline (normalization, capability checking, ambiguity/unsupported detection, Forge integration, diffing, status resolution) exhaustively, while saying nothing about how well a real LLM would actually extract structured intent from the same 62 raw texts — that question can only be answered once a live provider exists, per [`307-provider-abstraction.md`](307-provider-abstraction.md).

## Why CI needs zero external AI calls

Because every corpus case, and all 108 backend tests more broadly, run entirely against `FakeDesignerProvider`, CI never depends on network access to a third-party AI vendor, never depends on a valid `ANTHROPIC_API_KEY` being present in the CI environment, never incurs a per-run AI cost, and never produces a flaky result from provider-side latency or rate limiting. This is the same discipline this codebase already applies to CAD generation (no dependency on a GUI application) and to every other external-service boundary: the test suite proves the deterministic logic Designer actually owns, and treats the provider itself as a swappable, mockable dependency rather than a thing CI needs to trust.

## Growing the corpus safely

Adding a new corpus case never requires touching a live provider either — a contributor writes the input text and the `RawDesignerResponse` a correctly-behaving provider should have produced for it, and the assertion checks the deterministic pipeline's handling of that fixture. This keeps the corpus growable by anyone working on `backend/jewelmind/designer/`, without requiring API access, while still directly exercising the exact same code path a live call would eventually run through.

See [`318-designer-evaluation-framework.md`](318-designer-evaluation-framework.md) for how this same corpus doubles as a first deterministic proxy for several evaluation metrics, and `specs/designer/v1/README.md` for the 6 examples and 7 test-vector files also generated from real `DesignerService` runs.
