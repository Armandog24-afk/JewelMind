---
id: JM-BIBLE-VISION-README
title: Vision v1 — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-ATLAS-README
  - JM-BIBLE-ALCHEMIST-README
  - JM-BIBLE-FOUNDRY-README
related_documents:
  - JM-BIBLE-README
implementation_status: partial
professional_validation: not_required
normative: false
---

# Vision v1 — Index

This is **Sprint 8** of the Technical Bible: **Vision v1**. Vision is the visual-output layer — the boundary between an already-generated Atlas geometry and what a person actually sees on screen. Unlike prior sprints, **Vision v1 is not documentation-only**: this Sprint both formalizes the visual-output architecture and materially rebuilds the viewer, adding a Technical/Presentation view split, a camera-preset system, a centralized material system, studio lighting and grounding for Presentation mode, and a real PNG image-capture feature — all consuming the exact same Atlas-generated preview meshes that already powered the viewer before this Sprint.

**Read this README, then [`220-vision-governance.md`](220-vision-governance.md), before changing anything in `frontend/src/components/ModelViewport.tsx`, `frontend/src/vision/`, or `frontend/src/store/useVisionStore.ts`.**

## The five-layer architecture Vision sits inside

| Layer | Owns |
|---|---|
| JDL (Sprint 3) | Declarative design definition |
| Forge (Sprint 4) | Rule evaluation and eligibility |
| Alchemist (Sprint 6) | Orchestration and deterministic compilation planning |
| Atlas (Sprint 5) | Geometry construction and geometric facts |
| Foundry (Sprint 7) | Artifact generation and export-integrity validation |
| **Vision** (this Sprint) | **Visual-output rendering: Technical inspection and Presentation display** |

Vision owns no jewelry-domain thresholds (Forge), no geometry construction (Atlas), no STEP/STL serialization (Foundry), and no compilation orchestration (Alchemist). It owns exactly one thing: turning already-generated, already-validated geometry into something a person can look at, from two different angles of intent — inspection and presentation.

## Reading order

1. [`220-vision-governance.md`](220-vision-governance.md) — 15 non-negotiable rules.
2. [`221-vision-architecture-overview.md`](221-vision-architecture-overview.md), [`222-visual-representation-model.md`](222-visual-representation-model.md), [`223-atlas-to-vision-contract.md`](223-atlas-to-vision-contract.md), [`224-preview-mesh-contract.md`](224-preview-mesh-contract.md), [`225-scene-graph-model.md`](225-scene-graph-model.md), [`226-component-visual-identity.md`](226-component-visual-identity.md).
3. The two views: [`227-technical-view-contract.md`](227-technical-view-contract.md), [`228-presentation-view-contract.md`](228-presentation-view-contract.md).
4. Camera, lighting, material: [`229-camera-system.md`](229-camera-system.md), [`230-lighting-system.md`](230-lighting-system.md), [`231-material-system.md`](231-material-system.md), [`232-metal-material-model.md`](232-metal-material-model.md), [`233-stone-material-model.md`](233-stone-material-model.md), [`234-background-and-environment-model.md`](234-background-and-environment-model.md), [`235-shadows-and-grounding.md`](235-shadows-and-grounding.md).
5. Interaction: [`236-component-visibility-model.md`](236-component-visibility-model.md), [`237-model-framing-and-fit.md`](237-model-framing-and-fit.md), [`238-image-capture-contract.md`](238-image-capture-contract.md).
6. State and reliability: [`239-render-state-model.md`](239-render-state-model.md), [`240-stale-and-last-good-preview.md`](240-stale-and-last-good-preview.md), [`241-rendering-errors-and-diagnostics.md`](241-rendering-errors-and-diagnostics.md), [`242-performance-and-gpu-resource-model.md`](242-performance-and-gpu-resource-model.md), [`243-accessibility-and-input-model.md`](243-accessibility-and-input-model.md).
7. [`244-visual-consistency-contract.md`](244-visual-consistency-contract.md), [`245-visual-regression-strategy.md`](245-visual-regression-strategy.md), [`246-current-viewer-code-mapping.md`](246-current-viewer-code-mapping.md).
8. [`247-vision-gap-analysis.md`](247-vision-gap-analysis.md), [`248-open-vision-questions.md`](248-open-vision-questions.md).

## Appendices

[`vision-component-style-catalog.md`](../appendices/vision-component-style-catalog.md), [`vision-camera-preset-catalog.md`](../appendices/vision-camera-preset-catalog.md), [`vision-material-catalog.md`](../appendices/vision-material-catalog.md), [`vision-render-state-catalog.md`](../appendices/vision-render-state-catalog.md), [`vision-diagnostic-catalog.md`](../appendices/vision-diagnostic-catalog.md), [`vision-code-mapping.md`](../appendices/vision-code-mapping.md), [`vision-test-matrix.md`](../appendices/vision-test-matrix.md).

## Machine-readable specification

[`specs/vision/v1/`](../../../specs/vision/v1/README.md) holds 6 JSON Schemas, 6 example scene states (1 technical + 1 presentation per current metal), and 5 test-vector files. No Three.js object appears in any schema — see [`239-render-state-model.md`](239-render-state-model.md).

## The single most important finding of this Sprint

**Vision v1 is a real product improvement, not only a specification.** Prior sprints formalized architecture that already existed in the running application; this Sprint ships new, user-visible functionality — a Technical/Presentation view switch, 5 camera presets, centralized 5-metal material presentation, StoneReference-distinct presentation materials, studio lighting with a procedural (non-CDN) environment, contact-shadow grounding, and client-side PNG capture — while proving, via the full test suite and a live generation run, that none of it altered STEP/STL export output or the pre-existing stale/last-good-preview guarantees. See [`SPRINT-8-VALIDATION-REPORT.md`](SPRINT-8-VALIDATION-REPORT.md).

## Validation of this sprint

See [`SPRINT-8-VALIDATION-REPORT.md`](SPRINT-8-VALIDATION-REPORT.md) for the checks run against this section and the findings from that pass.
