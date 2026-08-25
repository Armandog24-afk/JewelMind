---
id: JM-BIBLE-A54
title: "Appendix: Studio Code Mapping"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-282
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Studio Code Mapping

Restates [`11-studio/282-current-ui-code-mapping.md`](../11-studio/282-current-ui-code-mapping.md) as a standalone quick reference.

| File | Classification |
|---|---|
| `frontend/src/studio/modelState.ts` | STUDIO (new) |
| `frontend/src/studio/outputEligibility.ts` | STUDIO (new) |
| `frontend/src/studio/keyboardShortcuts.ts` | STUDIO (new) |
| `frontend/src/components/ModelStatusBadge.tsx` | STUDIO (new) |
| `frontend/src/components/OutputsPanel.tsx` | STUDIO (new) |
| `frontend/src/components/ArtifactRow.tsx` | STUDIO (new) |
| `frontend/src/components/AppHeader.tsx` | STUDIO |
| `frontend/src/components/ProjectActions.tsx` | STUDIO |
| `frontend/src/components/ConfigurationPanel.tsx` | STUDIO |
| `frontend/src/components/NumericField.tsx` | STUDIO |
| `frontend/src/components/RightPanelTabs.tsx` | STUDIO |
| `frontend/src/components/ModelViewport.tsx` | MIXED (VISION + STUDIO) |
| `frontend/src/components/ViewportToolbar.tsx` | VISION |
| `frontend/src/store/useProjectStore.ts` | ALCHEMIST-like (unchanged classification) |
| `frontend/src/store/useVisionStore.ts` | VISION |
| `frontend/src/hooks/useComponentGeometries.ts` | ATLAS_INTERFACE |
| `frontend/src/api/client.ts` | API |

**Mixed-responsibility files: 1** (`ModelViewport.tsx`), named honestly per [`11-studio/282-current-ui-code-mapping.md`](../11-studio/282-current-ui-code-mapping.md).
