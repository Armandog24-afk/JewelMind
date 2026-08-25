---
id: JM-BIBLE-A48
title: "Appendix: Studio Screen Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-252
related_documents:
  - JM-BIBLE-266
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Studio Screen Catalog

JewelMind has exactly **one screen** — there is no router. This catalog lists its zones and responsive breakpoints instead of separate screens, per [`11-studio/264-navigation-model.md`](../11-studio/264-navigation-model.md).

| Zone | Contents | Desktop width | Tablet width | Stacked (≤980px) |
|---|---|---|---|---|
| Header | Brand, `ModelStatusBadge`, `ProjectActions`, `BackendStatus` | Full width | Full width | Full width |
| DESIGN (left panel) | `ProfessionalReviewNotice`, `ConfigurationPanel` | 340px | 300px | Full width, stacked first |
| REVIEW (center panel) | `ModelViewport` (Technical/Presentation) | `1fr` (remaining space) | `1fr` | Full width, `min-height: 420px`, stacked second |
| VALIDATION/OUTPUT (right panel) | `RightPanelTabs`: Validation, Outputs, Specification, JSON, Model info | 380px | 320px | Full width, stacked third |
