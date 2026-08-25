---
id: JM-BIBLE-278
title: Frontend State Architecture
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-221
related_documents:
  - JM-BIBLE-239
implementation_status: current
professional_validation: not_required
normative: true
---

# Frontend State Architecture

## The 6 conceptual state categories, mapped to real stores/modules

| Category | Real owner | Never does |
|---|---|---|
| DESIGN STATE | `useProjectStore.currentDefinition` | Never written by Vision or Studio-only UI |
| GENERATED MODEL STATE | `useProjectStore.{generatedModel, lastSuccessfulPreview, generationStatus, generationError, isStale}` | Never written outside `generate()`/`withUpdatedDefinition()` |
| VISION STATE | `useVisionStore` (viewMode, componentVisibility, selectedComponent, showGrid, showAxes, captureRequestToken) | Never imports `useProjectStore`; never calls `generate()` |
| VALIDATION STATE | `useProjectStore.validationResults` (client-computed, then server-confirmed) | Never diverges permanently from what the backend would compute — the backend's result always overwrites the client's after `generate()` |
| OUTPUT STATE | `useProjectStore.{exportStatus, exportError}`, plus the derived, stateless `computeOutputEligibility()` | Never blocks unrelated viewer interaction — exporting STEP does not disable the viewport or camera controls |
| NETWORK STATE | `useProjectStore.backendStatus` (health polling) | Never conflated with `generationStatus` — a slow/offline backend and an in-flight generation are reported independently |

## No single `isLoading` boolean

Confirmed by inspection: this codebase never had, and this Sprint did not introduce, one shared loading flag. `generationStatus`, `exportStatus` (one entry per artifact kind), `isCapturing` (Vision), and `backendStatus` are all independent, so a slow STEP export never makes the Generate button or the camera controls appear busy, and vice versa — directly satisfying this Sprint's explicit requirement.

## View-only state cannot mark design stale, by construction

`isStale` is only ever set inside `withUpdatedDefinition()`, which only runs from `useProjectStore`'s `updateXxx()` actions — none of which `useVisionStore` calls. This is not a runtime check but a structural guarantee: `useVisionStore.ts` has no import of `useProjectStore` at all, confirmed by its own file contents and asserted by `useVisionStore.test.ts`.

## Export loading never blocks the viewer

`exportStatus[kind] === 'exporting'` only disables that one `ArtifactRow`'s button — `ModelViewport`, `ConfigurationPanel`, and every other component read entirely different store fields and re-render independently (React/Zustand's selector-based subscription model, unchanged this Sprint).
