---
id: JM-BIBLE-STUDIO-README
title: Studio v1 — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-JDL-README
  - JM-BIBLE-FORGE-README
  - JM-BIBLE-ATLAS-README
  - JM-BIBLE-ALCHEMIST-README
  - JM-BIBLE-FOUNDRY-README
  - JM-BIBLE-VISION-README
related_documents:
  - JM-BIBLE-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Studio v1 — Index

This is **Sprint 9** of the Technical Bible: **Studio v1**. Studio is the product-workspace layer — it owns the end-to-end human workflow (input → validation → generation → review → output) around the systems every prior Sprint formalized. Like Sprint 8 (Vision), this Sprint is **not documentation-only**: it reorganizes the parameter editor into design/advanced groups, introduces a single centralized model-status indicator, consolidates every export action into one Outputs area, adds a small discoverable keyboard-shortcut set, and closes several small, real accessibility/consistency gaps found by auditing the pre-Sprint-9 UI — all while preserving every JDL/Forge/Alchemist/Atlas/Foundry/Vision guarantee unchanged.

**Read this README, then [`250-studio-governance.md`](250-studio-governance.md), before changing anything in `frontend/src/studio/`, `frontend/src/components/AppHeader.tsx`, `ConfigurationPanel.tsx`, `OutputsPanel.tsx`, or `RightPanelTabs.tsx`.**

## Where Studio sits

Studio owns user workflow. It does not own jewelry rules (Forge), geometry (Atlas), compiler logic (Alchemist), exporter logic (Foundry), or rendering geometry (Vision) — restating this Sprint's own product principle:

```
Studio
  ↓
JDL / UI State
  ↓
Forge
  ↓
Alchemist
  ↓
Atlas
  ↓
Vision + Foundry
```

## Reading order

1. [`250-studio-governance.md`](250-studio-governance.md) — 15 non-negotiable rules.
2. [`251-product-workspace-overview.md`](251-product-workspace-overview.md), [`252-information-architecture.md`](252-information-architecture.md), [`253-user-workflow-model.md`](253-user-workflow-model.md), [`254-project-session-model.md`](254-project-session-model.md).
3. The editor: [`255-design-editing-contract.md`](255-design-editing-contract.md), [`256-parameter-editor-model.md`](256-parameter-editor-model.md).
4. The workflow states: [`257-validation-experience.md`](257-validation-experience.md), [`258-generation-experience.md`](258-generation-experience.md), [`259-model-state-experience.md`](259-model-state-experience.md).
5. Review and output: [`260-output-review-experience.md`](260-output-review-experience.md), [`261-export-experience.md`](261-export-experience.md), [`262-technical-review-workspace.md`](262-technical-review-workspace.md), [`263-presentation-review-workspace.md`](263-presentation-review-workspace.md).
6. Structure: [`264-navigation-model.md`](264-navigation-model.md), [`265-layout-system.md`](265-layout-system.md), [`266-responsive-behaviour.md`](266-responsive-behaviour.md).
7. Feedback: [`267-status-and-feedback-system.md`](267-status-and-feedback-system.md), [`268-loading-and-progress-model.md`](268-loading-and-progress-model.md), [`269-error-recovery-model.md`](269-error-recovery-model.md), [`270-empty-state-model.md`](270-empty-state-model.md), [`271-confirmation-and-destructive-actions.md`](271-confirmation-and-destructive-actions.md).
8. Access: [`272-accessibility-contract.md`](272-accessibility-contract.md), [`273-keyboard-and-input-model.md`](273-keyboard-and-input-model.md).
9. Persistence: [`274-local-persistence-model.md`](274-local-persistence-model.md), [`275-session-recovery.md`](275-session-recovery.md).
10. Foundations: [`276-design-system-foundations.md`](276-design-system-foundations.md), [`277-ui-component-architecture.md`](277-ui-component-architecture.md), [`278-frontend-state-architecture.md`](278-frontend-state-architecture.md), [`279-api-interaction-model.md`](279-api-interaction-model.md).
11. Language: [`280-product-copy-and-terminology.md`](280-product-copy-and-terminology.md), [`281-user-guidance-model.md`](281-user-guidance-model.md).
12. [`282-current-ui-code-mapping.md`](282-current-ui-code-mapping.md), [`283-studio-gap-analysis.md`](283-studio-gap-analysis.md), [`284-open-studio-questions.md`](284-open-studio-questions.md).

## Appendices

[`studio-screen-catalog.md`](../appendices/studio-screen-catalog.md), [`studio-state-catalog.md`](../appendices/studio-state-catalog.md), [`studio-action-catalog.md`](../appendices/studio-action-catalog.md), [`studio-status-catalog.md`](../appendices/studio-status-catalog.md), [`studio-ui-component-catalog.md`](../appendices/studio-ui-component-catalog.md), [`studio-copy-catalog.md`](../appendices/studio-copy-catalog.md), [`studio-code-mapping.md`](../appendices/studio-code-mapping.md), [`studio-test-matrix.md`](../appendices/studio-test-matrix.md).

## Machine-readable specification

[`specs/studio/v1/`](../../../specs/studio/v1/README.md) holds 5 JSON Schemas, 6 example states, and 6 test-vector files.

## The single most important finding of this Sprint

**Export actions were scattered across three unrelated UI locations before this Sprint** (the header's `ProjectActions`, the right panel's `Specification` tab, and the viewport's Presentation panel) — and one artifact type (the technical specification's *download*, as opposed to its inline preview) had no button anywhere at all, despite `runExport('specification')` already existing in `useProjectStore`. This Sprint's consolidated `OutputsPanel` fixes both problems at once: every artifact now renders through one `ArtifactRow` component sharing one eligibility rule (`computeOutputEligibility()`), and the previously-unreachable specification download is now wired up. See [`260-output-review-experience.md`](260-output-review-experience.md) and [`282-current-ui-code-mapping.md`](282-current-ui-code-mapping.md).

## Validation of this sprint

See [`SPRINT-9-VALIDATION-REPORT.md`](SPRINT-9-VALIDATION-REPORT.md) for the checks run against this section and the findings from that pass.

## Relationship to Sprint 10

[`12-designer/`](../12-designer/README.md) (Sprint 10) adds exactly one new Studio surface, `DesignerPanel` (rendered between the professional-review notice and `ConfigurationPanel`), and one new store action, `useProjectStore.applyDesignerProposal()`. `DesignerPanel` sends a natural-language request to `POST /api/designer/interpret`, renders the returned `DesignerProposal` for review ("JewelMind understood"/unsupported-feature/clarification sections), and only calls `applyDesignerProposal()` on an explicit user click — that action writes through the same `withUpdatedDefinition()` path every other `updateXxx()` action already uses, so a proposal that changes a geometry-driving field correctly marks the current model stale through the existing mechanism. This Sprint changes nothing about `computeModelState()`, `computeOutputEligibility()`, or any other existing Studio guarantee: Designer is additive UI and one additive store action, not a new state model. See [`12-designer/320-current-studio-integration.md`](../12-designer/320-current-studio-integration.md).
