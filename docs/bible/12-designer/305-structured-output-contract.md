---
id: JM-BIBLE-305
title: Structured Output Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-304
related_documents:
  - JM-BIBLE-306
implementation_status: current
professional_validation: not_required
normative: true
---

# Structured Output Contract

## `RawDesignerResponse` is the only thing any provider may return

`designer/schemas.py::RawDesignerResponse` is the exact and complete shape both `FakeDesignerProvider` and `AnthropicDesignerProvider` produce, and the only shape `DesignerService._build_proposal()` ever consumes. It has five fields, all defaulting to empty:

| Field | Shape | Meaning |
|---|---|---|
| `proposedCanonicalValues` | `list[RawProposedValue]` | `{field, value, sourceText}` — a dotted JDL path the provider believes the user specified or implied, and the raw token for it |
| `unresolvedDescriptors` | `list[str]` | Non-technical descriptive language preserved verbatim (e.g. `"delicate"`) — never converted into a dimension by the provider itself |
| `detectedUnsupportedFeatures` | `list[RawUnsupportedFeature]` | `{feature, sourceText, suggestedSupportedAlternative}` — a concept the provider itself recognized as unsupported |
| `ambiguities` | `list[RawAmbiguity]` | `{field, sourceText, candidateValues}` — a term naming a category without picking one member |
| `clarificationCandidates` | `list[RawClarification]` | `{field, question, options}` — a question the provider believes is worth asking |

## JewelMind's own code builds the candidate JDL — never the provider

Nothing in `RawDesignerResponse` is a JDL fragment, a `JewelryDefinition`, or anything resembling one. `pv.value` in a `RawProposedValue` is an untyped, unvalidated token (`str | float | int | bool`) — it could be `"oro giallo"`, `"6"`, or `"halo"`. Turning that into a real canonical value is entirely `service.py::_build_proposal()`'s job, via `normalizer.normalize_enum_token()`, `normalizer.is_numeric_field()`, and `capability.is_known_field()`. The provider never sees, constructs, or influences the actual `JewelryDefinition.model_validate()` call in `_apply_patch()` — it only ever hands over raw tokens for JewelMind's own deterministic pipeline to interpret.

## Why this separation matters

A provider swap — a different model, a different vendor, even a hypothetical future non-LLM interpretation source — only has to satisfy this one Pydantic contract to work with the rest of Designer unchanged. Conversely, if a provider ever attempted to return something field-shaped-but-JDL-flavored (e.g. a `material.metal` value the schema does not recognize), it fails the exact same `capability.is_known_field()` / `normalize_enum_token()` gates any other input would (DESIGNER-GOV-004), because the pipeline treats every `RawProposedValue` identically regardless of source.

See [`306-prompt-architecture.md`](306-prompt-architecture.md) for how a real provider is told what shape to return, and [`308-designer-validation-pipeline.md`](308-designer-validation-pipeline.md) for the full ordered pipeline this contract feeds into.
