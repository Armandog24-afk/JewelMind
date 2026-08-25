---
id: JM-BIBLE-265
title: Layout System
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

# Layout System

## The real desktop grid, confirmed already correct

`.app-body { display: grid; grid-template-columns: 340px 1fr 380px }` — the center column (the 3D viewport) is the only `1fr` track, meaning it absorbs 100% of any extra window width beyond the two fixed side panels. This already satisfies "viewport should receive the largest useful area" and "avoid equal-width three-column layouts if they make the 3D viewer too small" — confirmed by inspection, no change was needed here.

## No resizable/collapsible panels added

Per this Sprint's own conditional instruction ("use resizable/collapsible panels only if implementation remains robust"), none were added — a resizable-panel implementation robust against the existing 3D canvas resize-observer behavior (see [`10-vision/242-performance-and-gpu-resource-model.md`](../10-vision/242-performance-and-gpu-resource-model.md) for the ResizeObserver-timing finding from Sprint 8) was judged out of proportion to this Sprint's scope. Recorded as `STUDIO-OQ-011` in [`284-open-studio-questions.md`](284-open-studio-questions.md).

## The one collapsible element this Sprint did add

The Advanced/technical parameters `<details>` disclosure inside `ConfigurationPanel` — a content-level collapse, not a panel-level one, using the native HTML element rather than a custom implementation (free keyboard accessibility, no JS state needed for open/closed).

## Fixed breakpoints, confirmed by direct inspection

`1180px` (narrows the side panels) and `980px` (collapses to a single stacked column) — both pre-existing, re-verified this Sprint via a live resize test; see [`266-responsive-behaviour.md`](266-responsive-behaviour.md) for what was actually observed at each.
