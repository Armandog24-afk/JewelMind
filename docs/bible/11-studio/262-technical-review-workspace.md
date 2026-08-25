---
id: JM-BIBLE-262
title: Technical Review Workspace
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-227
related_documents:
  - JM-BIBLE-259
implementation_status: current
professional_validation: not_required
normative: true
---

# Technical Review Workspace

## What Technical View already integrates, confirmed unchanged

Component visibility (`ComponentVisibilityPanel`), the component list with generation-status labels, camera controls (5 presets + Fit/Reset), and grid/axes — all from Sprint 8, untouched by this Sprint. This Sprint's additions are workspace-level, not viewport-level: the `ModelStatusBadge` (header) and the in-viewport stale/failed banner (both from [`259-model-state-experience.md`](259-model-state-experience.md)) are visible regardless of which Vision mode is active, so Technical View review always happens with an accurate, centrally-computed status alongside it.

## Validation results and model metadata

Both already live one tab away (`Validation`, `Model info`) rather than inline over the 3D view — a deliberate choice preserved from before this Sprint, avoiding cluttering the technical viewport itself while keeping both one click away. Dimensions/specification detail lives in the `Specification`/`Model info` tabs, not duplicated into the viewport.

## No CAD editor, confirmed by inspection

No mesh-editing, vertex-manipulation, or direct-geometry-mutation code exists anywhere in `frontend/src/vision/` or `frontend/src/components/ModelViewport.tsx` — restating VISION-GOV-001/002 and this Sprint's explicit instruction ("do not turn the viewer into a CAD editor yet. No direct mesh manipulation. No arbitrary vertex editing"). The viewer remains strictly a rendering surface for backend-generated geometry.

## What this Sprint did not add here

No measurement overlays, no section/cutaway views, no exploded view — all remain PLANNED, tracked as `VISION-GAP-008`/`009`/`010` (Sprint 8) and restated as `STUDIO-GAP` entries where they intersect Studio's workspace framing — see [`283-studio-gap-analysis.md`](283-studio-gap-analysis.md).
