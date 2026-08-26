---
id: JM-BIBLE-490
title: Vision Inspection Integration
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-220
  - JM-BIBLE-447
normative: false
implementation_status: current
professional_validation: not_required
---

# Vision Inspection Integration

## The honest finding: no UI renders inspection data

Grepping `frontend/src/components/` for `fetchInspectionReport`, `InspectionSummary`, and `GeometryInspectionReport` finds exactly two files: `frontend/src/api/client.ts` (the function definition) and `frontend/src/api/types.ts` (the type definitions). **No React component imports or calls any of the three.** `frontend/src/components/ModelViewport.tsx` was grepped specifically (case-insensitive, for the substring `inspection`) and contains exactly one unrelated match — a comment referring to grid/axes as "technical-inspection aids," which predates this Sprint and has nothing to do with `GeometryInspectionReport`. There is no inspection-related code anywhere in `ModelViewport.tsx`.

`frontend/src/components/ProjectActions.test.tsx` and `frontend/src/components/OutputsPanel.test.tsx` each contain one match for the literal `inspection:` — both are mock `GenerateResponse.metadata` fixtures that include the now-required `inspection` field (the concise `InspectionSummary` shape) so the test mocks satisfy the TypeScript type. Neither test exercises any inspection-rendering behavior, because none exists to exercise.

## What is real

- `frontend/src/api/types.ts` — a complete, real TypeScript mirror of the backend contract: `InspectionSummary`, `ComponentInspectionResult`, `AssemblyInspectionResult`, `GeometryInspectionReport` (plus the nested `BoundingBoxFact`, `DistanceResult`, `IntersectionResult`, `ConnectivityGraph` types), and `ModelMetadataResponse`/`GenerateResponse.metadata` both carrying a required `inspection: InspectionSummary` field.
- `frontend/src/api/client.ts::fetchInspectionReport(modelId)` — a real fetch wrapper calling `GET /api/models/${modelId}/inspection`, returning `Promise<GeometryInspectionReport>`.

Both are genuinely complete and callable. What is missing is any component that calls `fetchInspectionReport()` or reads `metadata.inspection`/`ModelMetadataResponse.inspection` to render something on screen.

## Why this is a deliberate scope decision, not an oversight

This Sprint's own brief framed the UI question explicitly as conditional and bounded: *"If easy and safe, allow Technical View to show inspection information... Do not turn Studio into a debugging console. Advanced/review mode is appropriate."* Given that framing, shipping the real backend contract (types, client function, dedicated endpoint) while deferring the UI-consumption decision is the correct application of STUDIO-GOV-011's "no architecture-internal name in user-facing copy" and STUDIO-GOV-014's accessible-primary-controls requirement — neither of which this Sprint attempted to satisfy for a UI surface that does not exist, because building an unreviewed inspection widget under time pressure risks exactly the debugging-console outcome the brief warned against. This document records that decision plainly rather than implying a UI integration happened when it did not.

## Vision governance is unaffected

`docs/bible/10-vision/220-vision-governance.md`'s rules (VISION-GOV-001 through 014) govern how `ModelViewport.tsx` renders geometry from `useComponentGeometries()` parsing real STL. None of them are engaged by this Sprint, because this Sprint adds no rendering code to Vision at all — not even a disabled or hidden inspection overlay. `useVisionStore`'s separation from `useProjectStore` (VISION-GOV-014) is preserved trivially, by absence of change.

## The specific, actionable next step this document identifies

`docs/bible/15-professional-validation/447-studio-professional-review-mode.md` documents `ProfessionalReviewPanel.tsx` (Sprint 13) as an already-implemented "Review" tab in `RightPanelTabs.tsx`. Reading `ProfessionalReviewPanel.tsx` for this Sprint confirms it currently offers exactly one action — generating and downloading the Professional Review Package ZIP (which, per [`489-foundry-inspection-integration.md`](489-foundry-inspection-integration.md), already contains the real `geometry-inspection.json`) — gated by the same `computeOutputEligibility()` every other artifact uses. It does not render any inspection content inline; a reviewer only sees inspection facts by opening the downloaded ZIP.

This is a genuine, specific, actionable gap, not a vague "future work" placeholder: `ProfessionalReviewPanel` already exists, already has a natural place for a summary (alongside its existing description of what the package contains), and already has a real `fetchInspectionReport()` client function ready to call. A future Sprint could add an inline inspection summary (e.g. the same `InspectionSummary` fields already surfaced in `GenerateResponse.metadata.inspection`, so no new backend work would even be required) to `ProfessionalReviewPanel.tsx` without violating the brief's "not a debugging console" constraint, because that panel is explicitly the advanced/review-mode surface the brief anticipated. See [`494-current-runtime-inspection-gap-analysis.md`](494-current-runtime-inspection-gap-analysis.md) for this gap listed with complexity/value judgments.
