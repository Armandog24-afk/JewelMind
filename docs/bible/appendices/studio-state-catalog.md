---
id: JM-BIBLE-A49
title: "Appendix: Studio State Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-259
related_documents:
  - JM-BIBLE-261
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Studio State Catalog

Restates [`11-studio/259-model-state-experience.md`](../11-studio/259-model-state-experience.md) and [`261-export-experience.md`](../11-studio/261-export-experience.md) as one standalone reference.

## `ModelStateKey` (7 values)

`NO_MODEL`, `GENERATING_FIRST_MODEL`, `CURRENT`, `STALE`, `REGENERATING`, `FAILED_NO_MODEL`, `FAILED_WITH_LAST_GOOD` — computed by `frontend/src/studio/modelState.ts::computeModelState()`.

## `OutputEligibilityKey` (5 values)

`AVAILABLE`, `UNAVAILABLE`, `EXPORTING`, `FAILED`, `STALE_BLOCKED` — computed by `frontend/src/studio/outputEligibility.ts::computeOutputEligibility()`.

## Pre-existing state this Sprint reused rather than duplicated

`GenerationStatus` (`idle`/`generating`/`success`/`error`) and `ExportPhase` (`idle`/`exporting`/`success`/`error`), both in `useProjectStore.ts`, unchanged — `ModelStateKey`/`OutputEligibilityKey` are derived *from* these, never a replacement for them.
