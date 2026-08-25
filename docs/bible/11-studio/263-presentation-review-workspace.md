---
id: JM-BIBLE-263
title: Presentation Review Workspace
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-228
related_documents:
  - JM-BIBLE-238
implementation_status: current
professional_validation: not_required
normative: true
---

# Presentation Review Workspace

## Priorities, confirmed unchanged from Sprint 8, now reachable from Outputs too

The jewelry image, metal, stone, camera, and clean appearance all remain exactly as Sprint 8 built them — `PresentationPanel` still shows the active metal and the "Save render" action directly over the viewport for in-context use. This Sprint adds a second, equally valid entry point: requesting a capture from the consolidated Outputs tab (`useVisionStore.requestCapture()` + `setViewMode('presentation')`), verified live this Sprint to correctly switch modes and trigger the capture handler without introducing a second, divergent capture implementation.

## No technical diagnostics over the jewelry

Confirmed by inspection: `PresentationPanel` renders only the metal name and the capture button — no validation list, no component-status text, no ruleId. Warnings remain reachable via the Validation tab, one click away in the same workspace, never overlaid on the presentation image.

## The one thing Presentation mode now always shows regardless of context

Per STUDIO-GOV-005/008, the header's `ModelStatusBadge` is visible in Presentation mode exactly as in Technical mode — a user viewing a stale model in Presentation mode still sees "Design changed" in the header, even though the viewport itself only shows the stale/failed banner in-context for the same two states as Technical mode ([`259-model-state-experience.md`](259-model-state-experience.md)).
