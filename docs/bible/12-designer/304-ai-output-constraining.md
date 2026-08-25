---
id: JM-BIBLE-304
title: AI Output Constraining
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-303
related_documents:
  - JM-BIBLE-305
implementation_status: current
professional_validation: not_required
normative: true
---

# AI Output Constraining

Designer never treats a provider's response as free-form text to be parsed hopefully. Three independent mechanisms in `backend/jewelmind/designer/provider.py` constrain what a real LLM call can return, satisfying DESIGNER-GOV-017.

## 1. Forced tool-use

`AnthropicDesignerProvider.interpret()` calls the Anthropic Messages API with `tool_choice={"type": "tool", "name": "submit_design_interpretation"}`. This is not merely offering a tool the model may choose to use — it forces the model's only possible response to be an invocation of that one tool. There is no code path where the model can instead return prose, decline, or answer in free text; the API contract itself rules that out before `RawDesignerResponse.model_validate()` is ever reached.

## 2. A fixed JSON Schema

`provider.py::_TOOL_INPUT_SCHEMA` is a literal, hand-authored JSON Schema object describing exactly `RawDesignerResponse`'s shape — five arrays (`proposedCanonicalValues`, `unresolvedDescriptors`, `detectedUnsupportedFeatures`, `ambiguities`, `clarificationCandidates`), each with its own item shape, all five marked `required`. This schema is passed as the tool's `input_schema`, so the provider's own structured-output machinery is constrained to emit values matching it, not an open-ended object.

## 3. Mandatory re-validation after the call returns

Even though the provider is already constrained by (1) and (2), `AnthropicDesignerProvider.interpret()` never trusts the tool-use input as-is. It extracts the first `tool_use` content block and calls `RawDesignerResponse.model_validate(tool_uses[0].input)` — JewelMind's own Pydantic model, independent of whatever guarantees the Anthropic SDK itself makes. A shape mismatch here raises `DesignerSchemaViolationError` (`DESIGNER_SCHEMA_VIOLATION`, HTTP 502) rather than silently coercing or passing through malformed data. No content block missing `tool_use` at all raises `DesignerInvalidResponseError` (`DESIGNER_INVALID_RESPONSE`) first.

## Why three layers, not one

Any single layer could plausibly fail in isolation — a provider bug in tool-use handling, a schema authored slightly looser than the actual Pydantic model, a future SDK version changing its enforcement. Re-validating with JewelMind's own model after the call is the layer that cannot silently drift out of sync with the rest of the pipeline, because it is the exact same `RawDesignerResponse` type `FakeDesignerProvider` and `_build_proposal()` already depend on.

## What this does not constrain

Constraining the *shape* of the output is not the same as constraining its *content* — the tool schema forces a `field`/`value` pair to be well-formed JSON, but says nothing about whether `field` names a real JDL path or `value` is a supported enum member. That check happens one layer downstream, in `_build_proposal()`'s capability gating (see [`308-designer-validation-pipeline.md`](308-designer-validation-pipeline.md)), not here. This document is about the mechanical contract a provider must satisfy to be parsed at all; [`305-structured-output-contract.md`](305-structured-output-contract.md) covers what that contract actually contains, and [`307-provider-abstraction.md`](307-provider-abstraction.md) explains why this real implementation has never been exercised against a live endpoint in this environment.
