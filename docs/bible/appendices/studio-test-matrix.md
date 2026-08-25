---
id: JM-BIBLE-A55
title: "Appendix: Studio Test Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-250
related_documents:
  - JM-BIBLE-SPRINT9-REPORT
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Studio Test Matrix

## Test categories from this Sprint's own checklist

| Category | Covered? | Where |
|---|---|---|
| `INITIAL_STATE_TEST` | Yes | `modelState.test.ts::'is NO_MODEL before any generation has ever succeeded'`, `useVisionStore.test.ts` defaults |
| `PARAMETER_EDIT_TEST` | Yes | `ConfigurationPanel.test.tsx` |
| `VALIDATION_STATE_TEST` | Yes (pre-existing, unchanged) | `ProjectActions.test.tsx` |
| `GENERATION_READY_TEST` | Yes | `ProjectActions.test.tsx` |
| `GENERATION_BLOCKED_TEST` | Yes | `ProjectActions.test.tsx` |
| `GENERATION_SUCCESS_TEST` | Yes | `modelState.test.ts` |
| `GENERATION_FAILURE_TEST` | Yes | `modelState.test.ts` |
| `LAST_GOOD_MODEL_TEST` | Yes (pre-existing, unchanged) | `useProjectStore.test.ts` |
| `STALE_MODEL_TEST` | Yes | `modelState.test.ts`, `outputEligibility.test.ts` |
| `REGENERATION_TEST` | Yes | `modelState.test.ts` |
| `VIEW_MODE_STATE_TEST` | Yes (pre-existing, unchanged) | `useVisionStore.test.ts` |
| `VISUAL_CHANGE_NO_REGENERATION_TEST` | Yes (pre-existing, unchanged) | `useVisionStore.test.ts` |
| `OUTPUT_AVAILABLE_TEST` | Yes | `OutputsPanel.test.tsx`, `outputEligibility.test.ts` |
| `OUTPUT_STALE_BLOCKED_TEST` | Yes | `OutputsPanel.test.tsx`, `outputEligibility.test.ts` |
| `EXPORT_ERROR_TEST` | Partial — covered by `outputEligibility.test.ts`'s `FAILED` case; no component test simulates a real network failure | — |
| `LOCAL_STORAGE_RECOVERY_TEST` | Yes (pre-existing, unchanged) | `persistence.test.ts` |
| `RESPONSIVE_LAYOUT_LOGIC_TEST` | Partial — verified via live browser resize + computed-style inspection, not an automated test | See `SPRINT-9-VALIDATION-REPORT.md` |
| `ACCESSIBLE_CONTROL_TEST` | Partial — covered by existing label-presence tests (`ConfigurationPanel.test.tsx`); no automated axe scan | — |
| `KEYBOARD_SHORTCUT_TEST` | Yes | `keyboardShortcuts.test.ts` |

## New test files this Sprint

`frontend/src/studio/modelState.test.ts` (9), `outputEligibility.test.ts` (8), `keyboardShortcuts.test.ts` (7), `frontend/src/components/OutputsPanel.test.tsx` (5 new file) — plus meaningful extensions to `ConfigurationPanel.test.tsx` (+4) and `ProjectActions.test.tsx` (+2).

## Full frontend suite

**107 passed** (72 pre-existing from Sprint 8 + 35 new/changed), 17 test files.

## E2E / browser flow

No dedicated browser-automation E2E test file was added to the repository — see [`11-studio/253-user-workflow-model.md`](../11-studio/253-user-workflow-model.md) for the 17-step primary workflow that was instead exercised **live**, once, via the Browser pane tool during this Sprint's own verification, with real network requests confirmed (`generate`, `export/step`) rather than mocked. Per this Sprint's own instruction ("if full browser automation is too fragile for the current CI, document the reason and create deterministic component/integration tests instead"): this session's Browser pane tool cannot reliably composite frames (see `10-vision/242-performance-and-gpu-resource-model.md`'s `document.visibilityState` finding from Sprint 8, reconfirmed this Sprint), making it unsuitable as a committed, repeatable CI E2E suite. The deterministic component/integration tests above are the durable substitute; the live session is recorded as a one-time verification, not a repeatable test.
