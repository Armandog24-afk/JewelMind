---
id: JM-BIBLE-A47
title: "Appendix: Vision Test Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-220
related_documents:
  - JM-BIBLE-245
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Vision Test Matrix

## Test categories from this Sprint's own checklist

| Category | Covered? | Where |
|---|---|---|
| `VIEW_MODE_TEST` | Yes | `useVisionStore.test.ts` |
| `CAMERA_PRESET_TEST` | Yes | `camera.test.ts` |
| `FIT_TO_MODEL_TEST` | Yes | `camera.test.ts` |
| `COMPONENT_VISIBILITY_TEST` | Yes | `useVisionStore.test.ts` |
| `MATERIAL_RESOLUTION_TEST` | Yes | `materials.test.ts` |
| `STONE_MATERIAL_TEST` | Yes | `materials.test.ts` |
| `STALE_PREVIEW_TEST` | Yes (pre-existing, unchanged) | `useProjectStore.test.ts` |
| `LAST_GOOD_PREVIEW_TEST` | Yes (pre-existing, unchanged) | `useProjectStore.test.ts` |
| `IMAGE_CAPTURE_STATE_TEST` | Yes | `capture.test.ts` |
| `RESOURCE_DISPOSAL_TEST` | Yes (pre-existing, unchanged, re-verified) | `useComponentGeometries.test.ts` |
| `EMPTY_STATE_TEST` | Partial — covered by manual browser verification, not a unit test | See `SPRINT-8-VALIDATION-REPORT.md` |
| `ERROR_STATE_TEST` | Partial — same as above | See `SPRINT-8-VALIDATION-REPORT.md` |
| `MODEL_REGENERATION_TEST` | Yes (pre-existing, unchanged) | `useProjectStore.test.ts` |
| `VIEW_MODE_NO_REGENERATION_TEST` | Yes | `useVisionStore.test.ts` |

## New test files this Sprint

`camera.test.ts` (8), `materials.test.ts` (8), `filename.test.ts` (4), `capture.test.ts` (5), `useVisionStore.test.ts` (6) — **31 new tests**, 5 new test files.

## Full frontend suite

**72 passed** (41 pre-existing + 31 new), 13 test files, unchanged in outcome from before this Sprint for every pre-existing test.

## Why `EMPTY_STATE_TEST`/`ERROR_STATE_TEST` are not unit tests

Both states depend on `ModelViewport`'s conditional JSX rendering inside a `<Canvas>` tree, which requires a real (or realistically mocked) WebGL context to mount without error in a test environment — jsdom has no WebGL. These were instead verified via a live browser session against the running dev server; see [`10-vision/245-visual-regression-strategy.md`](../10-vision/245-visual-regression-strategy.md) for why a heavier browser-based test harness was not added this Sprint.
