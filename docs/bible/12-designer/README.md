---
id: JM-BIBLE-DESIGNER-README
title: Designer v1 — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-JDL-README
  - JM-BIBLE-FORGE-README
  - JM-BIBLE-ALCHEMIST-README
  - JM-BIBLE-STUDIO-README
related_documents:
  - JM-BIBLE-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Designer v1 — Index

This is **Sprint 10** of the Technical Bible: **Designer v1**. Designer is the first controlled natural-language design layer in JewelMind: a user describes a design or a change to one, in Italian or English, and receives a structured, reviewable `DesignerProposal` — never raw geometry, never a bypass of JDL/Forge validation, never a manufacturability claim, and never a silently-invented value for something the user didn't specify and no sanctioned default exists for. Like Sprint 8 (Vision) and Sprint 9 (Studio), this Sprint is **not documentation-only**: it ships a real backend package (`backend/jewelmind/designer/`), a real `POST /api/designer/interpret` endpoint, and a real Studio UI (`frontend/src/components/DesignerPanel.tsx`).

**Read this README, then [`290-designer-governance.md`](290-designer-governance.md), before changing anything in `backend/jewelmind/designer/` or `frontend/src/components/DesignerPanel.tsx`.**

## Where Designer sits

Designer is upstream of every existing layer and authoritative over none of them:

```
USER LANGUAGE
  ↓
DESIGNER            (this Sprint — proposal only, no authority)
  ↓
STRUCTURED DESIGN PROPOSAL
  ↓
JDL CANDIDATE
  ↓
JDL VALIDATOR + FORGE
  ↓
USER REVIEW / ACCEPTANCE
  ↓
ALCHEMIST
  ↓
ATLAS
```

Designer never communicates geometric construction instructions to Atlas, never generates a STEP/STL mesh itself, and is never a source of jewelry-domain truth. Its interpretation is always a proposal requiring deterministic validation (JDL schema + Forge) and explicit user review/acceptance before it can affect the authoritative design state (`useProjectStore.currentDefinition`) or trigger generation.

## Reading order

1. [`290-designer-governance.md`](290-designer-governance.md) — 18 non-negotiable rules (DESIGNER-GOV-001 through 018).
2. [`291-designer-architecture-overview.md`](291-designer-architecture-overview.md), [`292-natural-language-input-contract.md`](292-natural-language-input-contract.md), [`293-intent-extraction-model.md`](293-intent-extraction-model.md), [`294-design-proposal-model.md`](294-design-proposal-model.md), [`295-designer-to-jdl-contract.md`](295-designer-to-jdl-contract.md).
3. Scope: [`296-capability-awareness.md`](296-capability-awareness.md), [`297-supported-language-scope.md`](297-supported-language-scope.md), [`298-defaulting-policy.md`](298-defaulting-policy.md).
4. Uncertainty: [`299-ambiguity-model.md`](299-ambiguity-model.md), [`300-clarification-policy.md`](300-clarification-policy.md), [`301-unsupported-request-handling.md`](301-unsupported-request-handling.md), [`302-confidence-model.md`](302-confidence-model.md), [`303-field-provenance-model.md`](303-field-provenance-model.md).
5. The AI boundary: [`304-ai-output-constraining.md`](304-ai-output-constraining.md), [`305-structured-output-contract.md`](305-structured-output-contract.md), [`306-prompt-architecture.md`](306-prompt-architecture.md), [`307-provider-abstraction.md`](307-provider-abstraction.md).
6. Validation: [`308-designer-validation-pipeline.md`](308-designer-validation-pipeline.md), [`309-designer-forge-integration.md`](309-designer-forge-integration.md).
7. Review UX: [`310-user-review-and-acceptance.md`](310-user-review-and-acceptance.md), [`311-proposal-diff-model.md`](311-proposal-diff-model.md), [`312-designer-error-model.md`](312-designer-error-model.md).
8. Trust and safety: [`313-designer-security-model.md`](313-designer-security-model.md), [`314-prompt-injection-and-untrusted-input.md`](314-prompt-injection-and-untrusted-input.md), [`315-privacy-and-data-boundaries.md`](315-privacy-and-data-boundaries.md).
9. Operations: [`316-designer-observability.md`](316-designer-observability.md), [`317-designer-cost-and-latency-model.md`](317-designer-cost-and-latency-model.md), [`318-designer-evaluation-framework.md`](318-designer-evaluation-framework.md), [`319-designer-test-corpus.md`](319-designer-test-corpus.md).
10. [`320-current-studio-integration.md`](320-current-studio-integration.md), [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md), [`322-open-designer-questions.md`](322-open-designer-questions.md).

## Appendices

[`designer-supported-intent-catalog.md`](../appendices/designer-supported-intent-catalog.md), [`designer-field-provenance-catalog.md`](../appendices/designer-field-provenance-catalog.md), [`designer-clarification-catalog.md`](../appendices/designer-clarification-catalog.md), [`designer-unsupported-feature-catalog.md`](../appendices/designer-unsupported-feature-catalog.md), [`designer-diagnostic-catalog.md`](../appendices/designer-diagnostic-catalog.md), [`designer-test-case-catalog.md`](../appendices/designer-test-case-catalog.md), [`designer-code-mapping.md`](../appendices/designer-code-mapping.md), [`designer-test-matrix.md`](../appendices/designer-test-matrix.md) (`JM-BIBLE-A56` through `A63`, continuing directly from Sprint 9's last appendix, `A55`).

## Machine-readable specification

[`specs/designer/v1/`](../../../specs/designer/v1/README.md) holds 7 JSON Schemas, 6 examples, and 7 test-vector files, all generated by running the real `DesignerService` with `FakeDesignerProvider` — never hand-invented.

## The single most important finding of this Sprint

**No live AI provider credential exists in this development environment, and Designer v1 was built to be honest about that rather than to fake it.** `backend/jewelmind/designer/provider.py` implements a complete `DesignerProvider` interface, a real `AnthropicDesignerProvider` adapter (structured tool-use output, full error mapping), and a mandatory test-only `FakeDesignerProvider` — but `get_designer_provider()` returns `None` whenever no `ANTHROPIC_API_KEY` is configured, and the service raises `DESIGNER_PROVIDER_UNAVAILABLE` rather than silently substituting the fake provider for a real user. This was verified live: a real browser session against the running app shows the "AI interpretation is unavailable" banner and a fully functional manual parameter editor underneath it, with the actual `503` response confirmed over the network. The entire deterministic pipeline downstream of a provider response (normalization, capability checking, provenance/confidence tagging, unsupported-feature detection, candidate JDL construction, Forge evaluation, diffing) is fully implemented and tested against 108 backend tests, including a 62-case natural-language corpus across all 11 required categories — none of it depends on a live LLM call. See [`307-provider-abstraction.md`](307-provider-abstraction.md) and [`SPRINT-10-VALIDATION-REPORT.md`](SPRINT-10-VALIDATION-REPORT.md).

## Relationship to Sprint 9

Designer adds exactly one new Studio surface — `DesignerPanel`, rendered between the professional-review notice and `ConfigurationPanel` — and one new store action, `useProjectStore.applyDesignerProposal()`. It changes nothing about Studio's existing model-status, output-eligibility, or generation contracts: applying a proposal only ever writes to `currentDefinition` through the same `withUpdatedDefinition()` path every other `updateXxx()` action already uses, so a proposal that changes a geometry-driving field correctly marks the current model stale, and Generate/Regenerate remains a separate, deliberate action Designer never triggers automatically. See [`320-current-studio-integration.md`](320-current-studio-integration.md).

## Relationship to Sprint 11

[`13-design-intent/`](../13-design-intent/README.md) (Sprint 11) extends Designer's own structured-output contract without changing any Sprint 10 guarantee: `RawDesignerResponse` (`designer/schemas.py`) gains `designIntentStatements`/`designIntentRelations` (provider-reported aesthetic descriptors and relations), and `DesignerProposal` gains one new required field, `designIntent` (a `DesignIntent`, always present, possibly empty). Every existing Sprint 10 guarantee is unchanged: `candidateJDL` is still built exclusively from `proposedCanonicalValues` via `JewelryDefinition.model_validate()`, the same JDL schema validation and Forge evaluation still run over it, and CI still exercises only `FakeDesignerProvider` — Design Intent's own deterministic pipeline (`backend/jewelmind/design_intent/`) runs entirely independently of, and after, Designer's technical-field resolution in `service.py::_build_proposal()`. See [`13-design-intent/356-designer-intent-extraction.md`](../13-design-intent/356-designer-intent-extraction.md).

## Relationship to Sprint 12

[`14-conversation/`](../14-conversation/README.md) (Sprint 12) adds Conversation Engine, a multi-turn interaction-state layer that now orchestrates Designer for real Studio use — `ConversationPanel.tsx` supersedes `DesignerPanel.tsx` as the component actually mounted in `App.tsx` (though `DesignerPanel.tsx` remains in the codebase, tested standalone). Every `MODIFY_DESIGN_PROPOSAL`/`CREATE_DESIGN_PROPOSAL`-routed conversation turn still calls the exact same `DesignerService.interpret()` this Sprint built — Conversation adds zero duplication of Designer's technical extraction, unsupported-feature detection, field provenance, or JDL proposal construction; it only adds turn history, reference resolution, clarification-thread lifecycle, and proposal staleness on top. See [`14-conversation/391-conversation-designer-integration.md`](../14-conversation/391-conversation-designer-integration.md).

## Relationship to Sprint 13

[`15-professional-validation/`](../15-professional-validation/README.md) (Sprint 13) is the framework that would eventually review Designer's own output — a Designer-proposed `candidateJDL` is exactly the kind of preliminary software geometry this Sprint's framework exists to capture real professional review evidence about. Designer adds no new claim of readiness of its own; its output remains just as preliminary after Sprint 13 as before it, until a real `ValidationRecord` says otherwise for a specific object and version.

## Validation of this sprint

See [`SPRINT-10-VALIDATION-REPORT.md`](SPRINT-10-VALIDATION-REPORT.md) for the checks run against this section and the findings from that pass.
