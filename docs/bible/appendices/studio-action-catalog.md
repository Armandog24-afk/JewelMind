---
id: JM-BIBLE-A50
title: "Appendix: Studio Action Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-258
related_documents:
  - JM-BIBLE-273
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Studio Action Catalog

| Action | Trigger(s) | Store call |
|---|---|---|
| Generate / Regenerate | Click, or `G` (not while typing, not blocked) | `useProjectStore.generate()` |
| Reset project | Click + `window.confirm()` | `useProjectStore.resetProject()` |
| Download STEP / STL / JDL JSON / Technical specification | Click (Outputs tab) | `useProjectStore.runExport(kind)` |
| Save render (Presentation PNG) | Click (Presentation panel, or Outputs tab) | `useVisionStore.setViewMode('presentation')` + `requestCapture()` → `ModelViewport.handleCapture()` |
| Switch Technical/Presentation | Click | `useVisionStore.setViewMode()` |
| Camera preset (Perspective/Front/Side/Top/Three-quarter) | Click, or `1`–`4` | `ModelViewport`'s local `handleCameraPreset()` (imperative Three.js ref mutation) |
| Fit / Reset camera | Click, or `F` (Fit only) | Same as above |
| Toggle component visibility | Click | `useVisionStore.toggleComponentVisible()` |
| Show all / Metal only | Click | `useVisionStore.showAllComponents()` / `showOnlyComponents()` |
| Toggle Grid / Axes | Click | `useVisionStore.toggleShowGrid()` / `toggleShowAxes()` |
| Expand/collapse Advanced parameters | Click (native `<summary>`) | No store — native `<details>` element state |
| Edit a design parameter | Typing/selecting | `useProjectStore.updateXxx()` |

Every action above was either verified live this Sprint (Generate/Regenerate, Reset+confirm, all 4 downloads, Save render from Outputs, camera presets via keyboard, Advanced-parameters toggle) or carried over unchanged and re-tested from Sprint 8 (view mode, component visibility, camera presets via click).
