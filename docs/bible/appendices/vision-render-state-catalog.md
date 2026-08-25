---
id: JM-BIBLE-A44
title: "Appendix: Vision Render State Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-239
related_documents: []
implementation_status: partial
professional_validation: not_required
normative: true
---

# Appendix: Vision Render State Catalog

Restates [`10-vision/239-render-state-model.md`](../10-vision/239-render-state-model.md)'s field table as a standalone reference.

| Field | Owner | Status |
|---|---|---|
| `viewMode` | `useVisionStore` | CURRENT |
| `componentVisibility` | `useVisionStore` | CURRENT |
| `selectedComponent` | `useVisionStore` | CURRENT |
| `showGrid` / `showAxes` | `useVisionStore` | CURRENT |
| `cameraPreset` / `cameraPosition` / `cameraTarget` | Imperative (Three.js refs) | CURRENT, not mirrored into React state |
| `metalPresentation` | Derived from `useProjectStore` | CURRENT, derived |
| `stonePresentation` | Derived from `viewMode` | CURRENT, derived |
| `environmentPreset` / `backgroundMode` | Implicit (one value per mode) | CURRENT, not a selectable field |
| `stale` / `modelId` / `definitionHash` | `useProjectStore` | CURRENT, read-only from Vision's side |
| `SceneStateSnapshot` (composed) | `frontend/src/vision/types.ts` | PLANNED as a real runtime composition — CURRENT only as a type |
