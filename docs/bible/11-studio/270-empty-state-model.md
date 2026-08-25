---
id: JM-BIBLE-270
title: Empty State Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-268
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Empty State Model

## Every empty state, confirmed intentional

| Situation | Message shown | Component |
|---|---|---|
| No generated model, first use | "No model yet" / "Configure your design and generate a model to begin." | `ModelStatusBadge` (header, new this Sprint) |
| No generated model, viewport | "Configure your ring and press Generate model to see a preview." | `ModelViewport`'s empty-state paragraph, pre-existing |
| No diagnostics | "No validation findings — this definition looks good." | `ValidationPanel`, pre-existing |
| No outputs available yet | Every `ArtifactRow` shows `UNAVAILABLE` ("Generate a model first") rather than hiding itself | `OutputsPanel`, new this Sprint |
| No generated model, specification tab | "Generate a model to view its technical specification." | `TechnicalSpecification`, pre-existing |
| No generated model, model info tab | "No model generated yet." | `ModelInformation`, pre-existing |
| Preview mesh loading | Handled by `isLoading` in `useComponentGeometries` — the previous geometry (if any) stays visible; if none exists yet, the viewport's own empty state is what's shown, not a separate spinner | `ModelViewport` |

## A deliberate choice: Outputs never hides a row

Rather than hiding an artifact row entirely until a model exists, `OutputsPanel` always renders all 5 rows, with `UNAVAILABLE` as one of the 5 eligibility states — so a first-time user immediately sees the full shape of what JewelMind can produce, before generating anything, rather than discovering the Outputs tab is empty and wondering whether something is broken.

## No blank panels

Every panel and tab in the workspace has a defined state for "nothing to show yet" — confirmed by inspecting all 5 right-panel tabs and the viewport; none renders a literal empty `<div>` with no text.
