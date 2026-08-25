---
id: JM-BIBLE-282
title: Current UI Code Mapping
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

# Current UI Code Mapping

## Every touched or audited file, classified

| File | Classification | Change this Sprint |
|---|---|---|
| `frontend/src/studio/modelState.ts` | STUDIO (new) | New — the 7-state model-status computation |
| `frontend/src/studio/outputEligibility.ts` | STUDIO (new) | New — the 5-state output-eligibility computation |
| `frontend/src/studio/keyboardShortcuts.ts` | STUDIO (new) | New — shortcut key resolution and typing-guard |
| `frontend/src/components/ModelStatusBadge.tsx` | STUDIO (new) | New |
| `frontend/src/components/OutputsPanel.tsx` | STUDIO (new) | New |
| `frontend/src/components/ArtifactRow.tsx` | STUDIO (new) | New |
| `frontend/src/components/AppHeader.tsx` | STUDIO | Added `ModelStatusBadge` |
| `frontend/src/components/ProjectActions.tsx` | STUDIO | Removed per-artifact export buttons (moved to `OutputsPanel`); added Reset confirmation and shortcut hint |
| `frontend/src/components/ConfigurationPanel.tsx` | STUDIO | Reorganized into Design + Advanced groups; added Preview-tolerance fields |
| `frontend/src/components/NumericField.tsx` | STUDIO | Added invalid-state styling/`aria-invalid` |
| `frontend/src/components/RightPanelTabs.tsx` | STUDIO | Added the `Outputs` tab |
| `frontend/src/components/ModelViewport.tsx` | MIXED (VISION + STUDIO) | Added the model-state banner (Studio), the capture-request bridge, and the keyboard-shortcut listener, alongside its pre-existing Vision responsibilities |
| `frontend/src/components/ViewportToolbar.tsx` | VISION | Added shortcut-key hints to button titles only |
| `frontend/src/store/useProjectStore.ts` | ALCHEMIST-like (unchanged classification from Sprint 8) | Added `updatePreview()` action only |
| `frontend/src/store/useVisionStore.ts` | VISION | Added `viewMode` persistence and `requestCapture()`/`captureRequestToken` |
| `frontend/src/hooks/useComponentGeometries.ts` | ATLAS_INTERFACE | Audited, unchanged |
| `frontend/src/api/client.ts` | API | Audited, unchanged — confirmed already centralized, see [`279-api-interaction-model.md`](279-api-interaction-model.md) |

## `ModelViewport.tsx`'s mixed classification, named honestly

`ModelViewport.tsx` was already Vision's largest file (Sprint 8); this Sprint added Studio-owned concerns (model-status banner, keyboard shortcuts) directly into it rather than creating a wrapper component, because both new concerns need direct access to refs (`cameraRef`, `controlsRef`) and state (`generationStatus`, `isStale`) that already live in this component. This is recorded as a real, acknowledged mixed-responsibility file — restating the same honest classification pattern Sprint 6 established for `ModelService.generate()` — rather than silently ignored.

## Code-audit findings (section 41 of this Sprint's brief), and what was done about each

| Finding | Real? | Action |
|---|---|---|
| Giant frontend components | No new one found; `ModelViewport.tsx` was already large (Sprint 8) and grew further — see mixed-classification note above | Recorded, not split (splitting risked breaking the ref-sharing needed for capture/shortcuts) |
| Duplicate button logic | Yes — STEP/STL/JSON export buttons each independently computed `disabled` in `ProjectActions.tsx` | Fixed — consolidated into `computeOutputEligibility()` + `ArtifactRow` |
| Duplicate diagnostics rendering | Not found — `ValidationPanel`/`ValidationItem` were already the single rendering path | No change needed |
| Inconsistent status wording | Yes — the viewport's stale banner had its own hardcoded string, independent of any other status text | Fixed — both now source from `describeModelState()` |
| Direct fetch calls scattered | Not found — confirmed all calls go through `api/client.ts` | No change needed |
| View state mixed with JDL | Not found — `useVisionStore`/`useProjectStore` were already correctly separated (Sprint 8) | No change needed |
| Redundant derived state | Not found | No change needed |
| Unsafe localStorage reads | Not found — `persistence.ts` was already defensive; this Sprint's own new `loadStoredViewMode()` was written to the same standard from the start | No change needed |
| Stale object URLs | Not found — `triggerBrowserDownload()` already creates and revokes synchronously | No change needed |
| Inaccessible icon-only buttons | Not found — every button already had a text label | No change needed |
| Form fields without labels | Not found — every field already had `<label htmlFor>` | No change needed |
| Loading states blocking the whole app | Not found — `generationStatus`/`exportStatus` were already scoped per-operation | No change needed |
| Duplicated export handlers | Yes — same issue as "duplicate button logic" above | Fixed |
| Unlabelled sliders / silent value coercion | Not found — every numeric input is a labeled `type="number"` field; `NumericField` never coerced an out-of-range value silently (it always passed the raw value through) — this Sprint added visible invalid-state feedback on top of that existing, correct behavior |

**2 real, concrete issues found and fixed: duplicated export/button logic, and inconsistent stale-state wording.** Everything else audited was already correct, confirmed rather than assumed.
