---
id: JM-BIBLE-246
title: Current Viewer Code Mapping
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-221
related_documents:
  - JM-BIBLE-A46
implementation_status: current
professional_validation: not_required
normative: true
---

# Current Viewer Code Mapping

Every viewer-adjacent file, classified by its actual responsibility, confirmed by direct inspection during this Sprint.

| File | Classification | Notes |
|---|---|---|
| `frontend/src/components/ModelViewport.tsx` | VISION, with orchestration | Owns the scene graph, camera refs, capture logic, and reads (never writes) `useProjectStore` — the single largest Vision file, by design (it is the one place the scene tree is assembled) |
| `frontend/src/components/ComponentMesh.tsx` | VISION | Pure presentational component; takes fully-resolved material parameters, no logic of its own |
| `frontend/src/components/ViewModeSwitch.tsx` | VISION | New this Sprint |
| `frontend/src/components/ViewportToolbar.tsx` | VISION | Extended this Sprint with camera presets; view-mode-aware (hides grid/axes in Presentation) |
| `frontend/src/components/ComponentVisibilityPanel.tsx` | VISION | Extended this Sprint with quick actions and status labels |
| `frontend/src/components/PresentationPanel.tsx` | VISION | New this Sprint |
| `frontend/src/vision/*.ts` | VISION | Pure logic — no React, no Three.js import in `types.ts`/`materials.ts`/`camera.ts`/`filename.ts`/`capture.ts` |
| `frontend/src/store/useVisionStore.ts` | VISION | New this Sprint; zero import from `useProjectStore` |
| `frontend/src/hooks/useComponentGeometries.ts` | ATLAS_INTERFACE | Fetches and parses backend-generated STL — the real boundary between Atlas-derived data and the Vision scene; unchanged this Sprint |
| `frontend/src/store/useProjectStore.ts` | MIXED (ALCHEMIST-like orchestration + JDL state), unchanged | Owns generation/stale/last-good logic — restates the frontend half of the same `ModelService`-like orchestration role Sprint 6 identified on the backend; Vision reads from it but does not modify it |
| `frontend/src/components/ModelInformation.tsx` | UI | Displays already-computed metadata; not touched this Sprint |
| `backend/jewelmind/preview/mesh.py` | ATLAS_INTERFACE, with one small additive extension | Tessellates and writes STL (Atlas-owned operation); this Sprint added the `geometryRole`/`productionRole`/`meshSource`/`generationStatus` manifest fields, still within this file's existing responsibility (describing components), not a new responsibility |
| `backend/jewelmind/api/routes.py`'s `generate_model()` | API | Assembles the HTTP response from `preview_manifest`; unchanged this Sprint beyond consuming the new fields transparently (already `dict[str, Any]`-typed) |

## Mixed-responsibility modules found

**1**, unchanged from every prior sprint's finding: `useProjectStore.ts` (frontend JDL state + generation orchestration + stale tracking, all in one store) — restates the same architectural note Sprint 6 made about `ModelService.generate()` on the backend, now observed at the frontend orchestration layer. Not addressed this Sprint (out of scope; Vision's job was to consume this store, not restructure it).

## What this Sprint did NOT touch

`useComponentGeometries.ts`, `useProjectStore.ts`'s generation logic, `ConfigurationPanel.tsx`, `RightPanelTabs.tsx`, `ValidationPanel.tsx`, `TechnicalSpecification.tsx`, `JsonViewer.tsx`, `ModelInformation.tsx`, `AppHeader.tsx`, `ProfessionalReviewNotice.tsx`, `App.tsx`'s overall 3-panel layout, or any backend exporter/geometry-construction file.
