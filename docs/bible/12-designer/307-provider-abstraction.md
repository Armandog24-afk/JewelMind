---
id: JM-BIBLE-307
title: Provider Abstraction
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-306
related_documents:
  - JM-BIBLE-308
implementation_status: partial
professional_validation: not_required
normative: true
---

# Provider Abstraction

`backend/jewelmind/designer/provider.py` decouples `DesignerService` from any specific AI vendor via one `Protocol`, and ships two implementations with very different verification status.

## `DesignerProvider` — the one interface the service depends on

A `Protocol` with a single method: `interpret(request: NaturalLanguageDesignRequest, context: DesignerContext) -> RawDesignerResponse`. `DesignerService.__init__` takes any `DesignerProvider | None` — it has never imported `anthropic` or any other vendor SDK directly (DESIGNER-GOV-016).

## `FakeDesignerProvider` — real, test-only, dependency-injected

A plain `@dataclass` with `response`, `responses_by_text`, and `raise_error` fields. It is never reachable through the runtime factory (`get_designer_provider()`, below) — every test that uses it constructs `DesignerService(provider=FakeDesignerProvider(...))` directly. This is what lets the entire deterministic pipeline (normalization, capability checking, provenance/confidence tagging, unsupported-feature detection, Forge evaluation, diffing) be exercised by 108 backend tests, including a 62-case corpus, with zero external AI calls (DESIGNER-GOV, "FakeProvider is mandatory"; see [`319-designer-test-corpus.md`](319-designer-test-corpus.md)).

## `AnthropicDesignerProvider` — real, complete, but never called live

A full implementation against the documented Anthropic Messages API: builds the layered system prompt via `prompts.py`, issues `self._client.messages.create()` with forced tool-use, and maps every SDK exception type it catches — `anthropic.APITimeoutError` -> `DesignerProviderTimeoutError`, `anthropic.APIError` -> `DesignerProviderError`, a missing `tool_use` block -> `DesignerInvalidResponseError`, a schema mismatch on the returned input -> `DesignerSchemaViolationError`.

**This code has never been exercised against a live Anthropic endpoint in this Sprint.** No `ANTHROPIC_API_KEY` is configured in this development environment. Its correctness rests on matching the documented API shape and passing type/unit review, not on an observed real response. This is stated here, in the provider module's own docstring, and in the README's "single most important finding" precisely so no future reader mistakes "implemented" for "verified live."

## `get_designer_provider()` — never a silent fake substitution

Reads `DESIGNER_PROVIDER` and, if `"anthropic"`, `ANTHROPIC_API_KEY` from the environment. Returns `AnthropicDesignerProvider` only when both are present; returns `None` in every other case — including `DESIGNER_PROVIDER=anthropic` with no key. `"fake"` is deliberately not a recognized selector value here at all, so there is no environment configuration that could accidentally put `FakeDesignerProvider` in front of a real user (DESIGNER-GOV-015). `DesignerService.interpret()` treats `None` as `DesignerProviderUnavailableError`, never as "substitute something."

See [`308-designer-validation-pipeline.md`](308-designer-validation-pipeline.md) for what happens once a provider (real or fake) does return, and the README's "single most important finding" for the live-verified evidence that manual Studio operation is unaffected when this returns `None`.
