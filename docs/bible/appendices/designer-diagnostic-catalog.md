---
id: JM-BIBLE-A60
title: "Appendix: Designer Diagnostic Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-DESIGNER-README
  - JM-BIBLE-290
related_documents:
  - JM-BIBLE-312
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Designer Diagnostic Catalog

The 11 verbatim `DESIGNER_*` codes from `backend/jewelmind/designer/errors.py`, the single vocabulary used both for HTTP failures (`AppError` subclasses) and in-band `DesignerDiagnostic.code` values inside a 200 `DesignerResult` (per JDL-GOV-007-style code stability discipline — see `errors.py`'s own module docstring).

| Code | Kind | HTTP status | Real trigger condition |
|---|---|---|---|
| `DESIGNER_PROVIDER_UNAVAILABLE` | HTTP `AppError` | 503 | `get_designer_provider()` returns `None` (no `ANTHROPIC_API_KEY`/`DESIGNER_PROVIDER` configured); raised in `DesignerService.interpret()` before any provider call |
| `DESIGNER_PROVIDER_TIMEOUT` | HTTP `AppError` | 504 | `AnthropicDesignerProvider.interpret()` catches `anthropic.APITimeoutError` from the live Messages API call |
| `DESIGNER_PROVIDER_ERROR` | HTTP `AppError` | 502 | Either `AnthropicDesignerProvider.interpret()` catches a non-timeout `anthropic.APIError`, or `DesignerService.interpret()`'s generic `except Exception` wraps any other provider-raised exception |
| `DESIGNER_INVALID_RESPONSE` | HTTP `AppError` | 502 | `AnthropicDesignerProvider.interpret()` finds no `tool_use` content block in the Anthropic response |
| `DESIGNER_SCHEMA_VIOLATION` | HTTP `AppError` | 502 | `AnthropicDesignerProvider.interpret()`'s `RawDesignerResponse.model_validate(tool_uses[0].input)` raises (the tool-use JSON parsed but didn't match the structured-output contract) |
| `DESIGNER_SECURITY_REJECTED` | HTTP `AppError` | 400 | `normalizer.detect_prompt_injection_risk(request.text)` matches one of the `_INJECTION_MARKERS` phrases; raised in `DesignerService.interpret()` before any provider call |
| `DESIGNER_UNSUPPORTED_FEATURE` | In-band diagnostic | n/a (200 response) | Emitted in `_build_proposal()` for both (a) an enum value that fails `normalize_enum_token()` and (b) any provider-reported `RawUnsupportedFeature` |
| `DESIGNER_AMBIGUOUS_REQUEST` | In-band diagnostic | n/a (200 response) | Emitted in `_build_proposal()` for both (a) a bare ambiguous metal term (`is_ambiguous=True`) and (b) any provider-reported `RawAmbiguity` |
| `DESIGNER_CLARIFICATION_REQUIRED` | In-band diagnostic | n/a (200 response) | Emitted in `_build_proposal()` for every provider-reported `RawClarification` turned into a `ClarificationQuestion` |
| `DESIGNER_PROPOSAL_INVALID` | In-band diagnostic | n/a (200 response) | Emitted in `_build_proposal()` for either (a) a non-numeric value submitted for a numeric field, or (b) `_apply_patch()` returning `None` because the assembled patch failed `JewelryDefinition.model_validate()` |
| `DESIGNER_CAPABILITY_MISMATCH` | In-band diagnostic | n/a (200 response) | Emitted in `_build_proposal()` when `capability.is_known_field(path)` is `False` for a provider-proposed field path (e.g. `stone.color`, which does not exist in the schema) |

## Verified test coverage

- HTTP-level: `backend/tests/test_designer_api.py::test_interpret_without_a_configured_provider_returns_503` (`DESIGNER_PROVIDER_UNAVAILABLE`), `test_interpret_rejects_malicious_text_with_400` (`DESIGNER_SECURITY_REJECTED`).
- Unit-level: `backend/tests/test_designer.py::TestProviderUnavailable`, `TestSecurityRejection`, `TestProviderFailure` (`DesignerProviderError`, `DesignerProviderTimeoutError`), `TestUnsupportedFeature` (`DESIGNER_CAPABILITY_MISMATCH`, unsupported-feature status), `TestInvalidAiOutput::test_non_numeric_value_for_numeric_field_is_ignored_not_crashed` (`DESIGNER_PROPOSAL_INVALID`).
- `DESIGNER_PROVIDER_TIMEOUT`, `DESIGNER_PROVIDER_ERROR` (Anthropic-specific `except` branches), `DESIGNER_INVALID_RESPONSE`, and `DESIGNER_SCHEMA_VIOLATION` are exercised only at the `DesignerProviderTimeoutError`/generic-exception level via `FakeDesignerProvider(raise_error=...)` in `test_designer.py::TestProviderFailure`, not against a live Anthropic call — consistent with `provider.py`'s own statement that `AnthropicDesignerProvider` "has not been exercised against a live API in this environment."
