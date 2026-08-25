---
id: JM-BIBLE-317
title: Designer Cost and Latency Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-316
related_documents:
  - JM-BIBLE-318
implementation_status: current
professional_validation: not_required
normative: true
---

# Designer Cost and Latency Model

## No real cost or latency numbers exist yet

This document contains no measured figure, because none can honestly be reported: `AnthropicDesignerProvider` has never been called against a live endpoint in this Sprint (see [`307-provider-abstraction.md`](307-provider-abstraction.md)), so there is no real token count, no real response latency, no real dollar cost, and no real failure rate to cite. Any number written here would be fabricated, which CLAUDE.md's jewelry-domain governance and this Bible's own fundamental rule both forbid for measurements the same way they forbid it for jewelry-domain constants — a number without a traceable source is not permitted, whether it's a stone tolerance or an inference latency.

`FakeDesignerProvider`'s responses are synchronous, in-process Python object construction with no network call — its "latency" (sub-millisecond, dominated by test harness overhead) says nothing meaningful about what a real Anthropic Messages API round trip would cost in time, and is not reported here as if it did.

## What would need measuring once a real provider is configured

Once `DESIGNER_PROVIDER=anthropic` and a valid `ANTHROPIC_API_KEY` are actually configured in a running environment, the following would need real measurement before any cost or latency claim could be made:

- **Tokens per request** — input tokens (system prompt + capabilities block + current-design JSON on `MODIFY` + user text) and output tokens (the structured tool-use response), which vary with request complexity and, for `MODIFY`, with how large the current `JewelryDefinition` is.
- **Latency distribution** — not just a mean, but p50/p95/p99, since a single slow outlier is what actually triggers `DESIGNER_PROVIDER_TIMEOUT` in production use.
- **Failure rate** — the real-world frequency of `DESIGNER_PROVIDER_ERROR`, `DESIGNER_PROVIDER_TIMEOUT`, `DESIGNER_INVALID_RESPONSE`, and `DESIGNER_SCHEMA_VIOLATION` against live traffic, as opposed to their current test coverage via `FakeDesignerProvider(raise_error=...)` (see [`designer-diagnostic-catalog.md`](../appendices/designer-diagnostic-catalog.md)'s coverage notes).
- **Cost per interpretation**, derived from the above once a specific model and pricing are fixed — `provider.py::DEFAULT_ANTHROPIC_MODEL` names a default, but no pricing assumption is encoded anywhere in this codebase.

## Why this matters beyond honesty for its own sake

A future decision about whether to expose cost/latency information to end users (see question 12 in [`322-open-designer-questions.md`](322-open-designer-questions.md)), or whether Designer's response time is acceptable for interactive use, cannot be made responsibly from guesses. This document exists to make sure that decision, whenever it is made, starts from real measurement rather than an assumption inherited from this Sprint's necessarily provider-less development environment.

## Relationship to observability

Real cost/latency measurement depends on the same missing structured-event infrastructure described in [`316-designer-observability.md`](316-designer-observability.md) — without a `PROVIDER_CALLED`/`PROVIDER_FAILED` event pair carrying timing data, there is no systematic place to even begin collecting the numbers this document says are missing. The two gaps should likely be closed together, not independently.
