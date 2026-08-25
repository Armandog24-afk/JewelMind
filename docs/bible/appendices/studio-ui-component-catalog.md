---
id: JM-BIBLE-A52
title: "Appendix: Studio UI Component Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-277
related_documents:
  - JM-BIBLE-A54
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Studio UI Component Catalog

| Component | Props (in) | Responsibility |
|---|---|---|
| `ModelStatusBadge` | `state: ModelStateKey` | Renders label + detail + tone for one of the 7 model states |
| `OutputsPanel` | none (reads stores directly) | Orchestrates 5 `ArtifactRow`s from `useProjectStore`/`useVisionStore` |
| `ArtifactRow` | `name, purpose, eligibility, actionLabel, onAction, errorMessage?` | Renders one output's name/purpose/status/action, identically for every artifact |
| `ProjectActions` | none | Generate/Regenerate button + Reset (with confirmation) |
| `ConfigurationPanel` | none | Design + Advanced parameter groups |
| `NumericField` | `id, label, value, onChange, min?, max?, step?, unit?, wide?` | One labeled numeric input with invalid-state feedback |
| `AppHeader` | none | Brand + `ModelStatusBadge` + `ProjectActions` + `BackendStatus` |
| `RightPanelTabs` | none | Tab switcher: Validation, Outputs, Specification, JSON, Model info |

See [`studio-code-mapping.md`](studio-code-mapping.md) for classification and [`11-studio/277-ui-component-architecture.md`](../11-studio/277-ui-component-architecture.md) for the conceptual-name mapping.
