---
id: JM-BIBLE-290
title: Designer Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-DESIGNER-README
related_documents:
  - JM-BIBLE-250
implementation_status: current
professional_validation: not_required
normative: true
---

# Designer Governance

## DESIGNER-GOV-001 through DESIGNER-GOV-018

| ID | Rule |
|---|---|
| **DESIGNER-GOV-001** | Designer has proposal-only authority. `DesignerService.interpret()` returns a `DesignerProposal`; nothing in `backend/jewelmind/designer/` ever writes to a `JewelryDefinition` that a generation or export call will read — only `useProjectStore.applyDesignerProposal()`, called from an explicit user action, does that. |
| **DESIGNER-GOV-002** | Designer cannot bypass JDL validation. Every `candidateJDL` is constructed via `JewelryDefinition.model_validate()` (`service.py::_apply_patch`) — the same strict Pydantic schema every other entry point uses; a shape that doesn't validate becomes `proposalStatus: INVALID`, never a raw dict returned to the caller. |
| **DESIGNER-GOV-003** | Designer cannot bypass Forge. `_build_proposal()` always calls the real `validate_definition()`/`has_errors()` from `jewelmind.validation.engine` and returns the true result in `forgeEvaluation` — it never re-implements or waives a rule. |
| **DESIGNER-GOV-004** | Designer cannot invent unsupported JDL enum values. `capability.py::is_known_field()`/`enum_capability_key()` and `normalizer.py::normalize_enum_token()` gate every enum field; an unrecognized token becomes an `UnsupportedFeature`, never a smuggled value — verified by `TestUnsupportedFeature.test_unsupported_stone_shape_value_is_caught_deterministically` and `TestUnsupportedFeature.test_unknown_field_from_provider_is_rejected_not_smuggled_into_jdl` in `backend/tests/test_designer.py`. |
| **DESIGNER-GOV-005** | Designer must identify unsupported requested features explicitly, never approximate them as supported. See [`301-unsupported-request-handling.md`](301-unsupported-request-handling.md); `UnsupportedFeature.blocking` and `.suggestedSupportedAlternative` make the gap and the nearest real alternative explicit rather than silent. |
| **DESIGNER-GOV-006** | Designer must distinguish explicit, inferred, and defaulted values. See [`303-field-provenance-model.md`](303-field-provenance-model.md) — the 8-value `FieldProvenance` enum is mandatory on every `ProposedField`. |
| **DESIGNER-GOV-007** | A geometry-driving AI-inferred value must be reviewable before generation. Every `ProposedField` with `provenance: AI_INTERPRETATION` is rendered in the "JewelMind understood" review section (`DesignerPanel.tsx`) before `applyDesignerProposal()` can be called — there is no path from provider response to `currentDefinition` that skips this review. |
| **DESIGNER-GOV-008** | Designer must not invent professional manufacturing rules. `capability.py::KNOWN_UNSUPPORTED_CONCEPTS` and every `UnsupportedFeature.reason` describe *support*, not manufacturability; Designer never emits a Forge-style rule of its own. |
| **DESIGNER-GOV-009** | Designer must not claim manufacturability. No string in `backend/jewelmind/designer/` or `DesignerPanel.tsx` asserts a design is production-ready; LAW-010's disclaimer is untouched by this Sprint. |
| **DESIGNER-GOV-010** | AI confidence must not replace deterministic validation. See [`302-confidence-model.md`](302-confidence-model.md) — `ConfidenceCategory` is derived entirely by JewelMind's own code from provenance/normalization facts; no raw provider confidence score is read, stored, or displayed anywhere. |
| **DESIGNER-GOV-011** | Every proposed field must have provenance. `ProposedField.provenance` is a required (non-optional) field in `designer/schemas.py`; there is no code path that constructs one without it. |
| **DESIGNER-GOV-012** | Unsupported requests must not be silently downgraded. A field the provider names that has no supported mapping becomes an `UnsupportedFeature`, not a nearby supported value substituted without telling the user (see `capability.KNOWN_UNSUPPORTED_CONCEPTS` and `TestUnsupportedFeature`). |
| **DESIGNER-GOV-013** | Ambiguous requests must not be silently resolved when they materially affect design intent. See [`299-ambiguity-model.md`](299-ambiguity-model.md) — a bare metal reference like "gold"/"oro" always becomes a `ClarificationQuestion`, never a guessed enum value (`normalizer.AMBIGUOUS_METAL_TERMS`). |
| **DESIGNER-GOV-014** | The runtime geometry pipeline must continue working without Designer. `/api/models/generate`, `/validate`, and every exporter route are untouched by this Sprint and have zero import-time or runtime dependency on `jewelmind.designer`. |
| **DESIGNER-GOV-015** | Designer provider failures must not break manual Studio operation. `get_designer_provider()` returning `None` only affects `/api/designer/interpret`; verified live in this Sprint (see the README's "single most important finding") — the parameter editor, generation, and export all continued working with `DESIGNER_PROVIDER_UNAVAILABLE` in effect. |
| **DESIGNER-GOV-016** | Provider-specific response formats must not leak into core domain architecture. `AnthropicDesignerProvider.interpret()` is the only place `anthropic`-shaped objects exist; it returns a plain `RawDesignerResponse` (a JewelMind-owned Pydantic model) to `DesignerService`, which never imports `anthropic`. |
| **DESIGNER-GOV-017** | LLM output must be constrained to machine-validated structured output. See [`305-structured-output-contract.md`](305-structured-output-contract.md) — `AnthropicDesignerProvider` uses forced tool-use (`tool_choice: {"type": "tool", ...}`) against a fixed JSON Schema, and the result is always re-validated as `RawDesignerResponse` before any other code sees it. |
| **DESIGNER-GOV-018** | The user must approve/edit proposed intent before generation whenever AI introduced a non-trivial inferred geometry-driving value. See [`310-user-review-and-acceptance.md`](310-user-review-and-acceptance.md) — `applyDesignerProposal()` never runs automatically, and applying a proposal never itself calls `generate()`. |

## When an ADR is required

Letting Designer write directly to generation/export state, moving JDL/Forge validation authority into Designer, adding a second AI-facing geometry construction path, or any change that violates DESIGNER-GOV-001 through 018 without superseding this document first.

## When an RFC is required

A new major natural-language capability — multi-turn conversation, a Design Intent Model translating aesthetic language into deterministic rules (planned as Sprint 11), reference-image/sketch input, or a new jewelry-domain intent category; see [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md).
