---
id: JM-BIBLE-312
title: Designer Error Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-311
related_documents:
  - JM-BIBLE-313
implementation_status: current
professional_validation: not_required
normative: true
---

# Designer Error Model

The exhaustive table of all 11 `DESIGNER_*` codes, their kind, HTTP status, and real trigger condition lives in [`designer-diagnostic-catalog.md`](../appendices/designer-diagnostic-catalog.md) — this document is the narrative explanation of why the model is shaped the way it is, not a duplicate of that table.

## Why 11 codes share one vocabulary

`designer/errors.py`'s own module docstring states the reason directly: a code is raised as an `AppError` (an HTTP failure) only when interpretation could not produce *any* proposal at all — provider unreachable, provider timed out, provider returned unparseable output, or the request itself was rejected as a security risk before ever reaching a provider. Every other designer-specific failure mode is an expected, normal outcome of interpreting a real request: an unsupported feature, an ambiguous term, a clarification the pipeline wants to ask, a candidate that failed schema validation, or a field the provider named that Designer doesn't recognize. Those five are never HTTP failures — they are `DesignerDiagnostic.code` values inside an ordinary `200` `DesignerResult`.

Keeping all 11 in one `ALL_DESIGNER_ERROR_CODES` tuple, in one file, means there is exactly one place a future code addition or removal has to be reasoned about, and exactly one vocabulary a frontend or API consumer needs to recognize — never two parallel code namespaces that happen to look similar.

## Why only 6 are HTTP failures

The six `AppError` subclasses — `DESIGNER_PROVIDER_UNAVAILABLE` (503), `DESIGNER_PROVIDER_TIMEOUT` (504), `DESIGNER_PROVIDER_ERROR` (502), `DESIGNER_INVALID_RESPONSE` (502), `DESIGNER_SCHEMA_VIOLATION` (502), and `DESIGNER_SECURITY_REJECTED` (400) — all correspond to a state where `DesignerService.interpret()` cannot construct a `DesignerProposal` at all, because the request never even reached `_build_proposal()`. The remaining five are all raised from inside `_build_proposal()` itself, where a proposal — possibly with `proposalStatus: UNSUPPORTED`, `NEEDS_CLARIFICATION`, or `INVALID` — is always successfully constructed and returned. This distinction is what lets `DesignerPanel.tsx` treat a `DESIGNER_PROVIDER_UNAVAILABLE` response completely differently (an unavailability banner, no proposal to show) from a `DESIGNER_UNSUPPORTED_FEATURE` diagnostic (a normal proposal with a "not currently supported" section).

## Stability discipline

Per DESIGNER-GOV (restating JDL-GOV-007's discipline for this Sprint), no code here may ever be renamed or reused once published. `ALL_DESIGNER_ERROR_CODES` exists precisely so a future contributor can enumerate the full vocabulary in one place before adding a twelfth code, rather than risk colliding with or shadowing an existing one.

See [`313-designer-security-model.md`](313-designer-security-model.md) for the one HTTP-failure code (`DESIGNER_SECURITY_REJECTED`) that has its own dedicated trust-boundary treatment, and the appendix's "Verified test coverage" section for exactly which codes are exercised at the HTTP level versus the unit level only.
