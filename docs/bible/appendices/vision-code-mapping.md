---
id: JM-BIBLE-A46
title: "Appendix: Vision Code Mapping"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-246
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Vision Code Mapping

Restates [`10-vision/246-current-viewer-code-mapping.md`](../10-vision/246-current-viewer-code-mapping.md) as a standalone quick reference.

| File | Classification |
|---|---|
| `frontend/src/components/ModelViewport.tsx` | VISION (orchestrator) |
| `frontend/src/components/ComponentMesh.tsx` | VISION |
| `frontend/src/components/ViewModeSwitch.tsx` | VISION (new) |
| `frontend/src/components/ViewportToolbar.tsx` | VISION |
| `frontend/src/components/ComponentVisibilityPanel.tsx` | VISION |
| `frontend/src/components/PresentationPanel.tsx` | VISION (new) |
| `frontend/src/vision/*.ts` | VISION (pure logic) |
| `frontend/src/store/useVisionStore.ts` | VISION (new) |
| `frontend/src/hooks/useComponentGeometries.ts` | ATLAS_INTERFACE (unchanged) |
| `frontend/src/store/useProjectStore.ts` | MIXED (unchanged; JDL state + generation orchestration) |
| `backend/jewelmind/preview/mesh.py` | ATLAS_INTERFACE, additively extended |
| `backend/jewelmind/api/routes.py::generate_model()` | API (unchanged) |

**Mixed-responsibility modules: 1** (`useProjectStore.ts`), unchanged from the frontend-orchestration finding implicit in prior sprints' backend-side equivalent.
