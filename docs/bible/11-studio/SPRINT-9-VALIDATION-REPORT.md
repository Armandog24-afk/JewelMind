---
id: JM-BIBLE-SPRINT9-REPORT
title: Sprint 9 Validation Report
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-STUDIO-README
related_documents: []
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 9 Validation Report

## Studio documents created

`docs/bible/11-studio/README.md` plus 35 numbered documents (`250`–`284`), plus this report. 8 new appendices: `studio-screen-catalog.md`, `studio-state-catalog.md`, `studio-action-catalog.md`, `studio-status-catalog.md`, `studio-ui-component-catalog.md`, `studio-copy-catalog.md`, `studio-code-mapping.md`, `studio-test-matrix.md` (`JM-BIBLE-A48` through `A55`, continuing directly from Sprint 8's last appendix, `A47`).

## Schemas created

5 JSON Schemas (Draft 2020-12): `studio-state`, `project-session`, `generation-state`, `output-state`, `notification`. All validate. 6 real example workspace states and 6 test-vector files, all generated from live-verified browser sessions or the real frontend test suite, checked into `specs/studio/v1/`. New test file: `backend/tests/test_studio_schemas.py` (5 test cases).

## Frontend files materially changed

**14 files**: 3 new pure-logic modules (`studio/modelState.ts`, `outputEligibility.ts`, `keyboardShortcuts.ts`), 3 new components (`ModelStatusBadge.tsx`, `OutputsPanel.tsx`, `ArtifactRow.tsx`), 5 substantially modified components (`AppHeader.tsx`, `ProjectActions.tsx`, `ConfigurationPanel.tsx`, `NumericField.tsx`, `RightPanelTabs.tsx`), 1 mixed-modification component (`ModelViewport.tsx` — added the shared model-state banner, the cross-component capture-request bridge, and the keyboard-shortcut listener), `useProjectStore.ts` (added `updatePreview()`), `useVisionStore.ts` (added `viewMode` persistence and `requestCapture()`), and `global.css` (focus-visible, invalid-field, advanced-parameters, model-status, and outputs-panel styles).

## New Studio components

`ModelStatusBadge`, `OutputsPanel`, `ArtifactRow` — 3 new components, plus 3 new pure-logic modules under `frontend/src/studio/`.

## Old components removed/refactored

`ProjectActions.tsx`'s per-artifact export buttons (STEP/STL/JSON) were removed and replaced by `OutputsPanel`/`ArtifactRow`; `ConfigurationPanel.tsx` was reorganized (not removed) into Design + Advanced groups. No component was deleted outright — every refactor preserved the underlying store actions it called.

## End-to-end workflow status

**Verified live**, via a real browser session against the running backend (see [`253-user-workflow-model.md`](253-user-workflow-model.md) for the full 17-step table): generate → current model → export STEP (real `200 OK`) → edit a parameter → stale (all 5 outputs correctly blocked) → regenerate via the `G` keyboard shortcut (real `200 OK`) → current model again → switch Presentation → request a PNG capture from the Outputs tab (correctly switched view mode and triggered the capture handler with no errors).

## Current/stale status

**Implemented and verified.** `computeModelState()`'s 7-value state is shown identically by the header badge and the in-viewport banner; live-verified transitioning `Current model` → `Design changed` immediately upon an edit, and back to `Current model` after a successful regeneration.

## Output workflow status

**Implemented and verified.** All 5 outputs (STEP, STL, JDL JSON, technical specification, Presentation PNG) consolidated into one `OutputsPanel` tab; live-verified all 5 correctly transition from `Available` to `Design changed — regenerate first` on a stale edit, and back to `Available` after regeneration.

## Responsive states verified

**2 breakpoints checked live**: 768px (tablet-width, confirmed single-column `grid-template-columns` collapse) and a mobile-scale resize (confirmed the viewport's `min-height: 420px` floor holds even in the stacked layout). The 1180px tablet-narrowing breakpoint was confirmed by code inspection but not independently exercised in a live resize test this Sprint.

## Accessibility improvements

**4 concrete improvements**: (1) a site-wide `:focus-visible` outline replacing a prior `outline: none` rule that left only a subtle border-color change; (2) `aria-invalid` + a visible, `aria-describedby`-linked error message on out-of-range numeric fields; (3) a native, keyboard- and screen-reader-accessible confirmation dialog for the Reset action; (4) `role="status"`/`aria-live="polite"` on the new model-status badge.

## E2E flows actually executed

**1 full live session** covering the entire 17-step primary workflow (see above and [`253-user-workflow-model.md`](253-user-workflow-model.md)) — not a repeatable, committed CI test (see [`appendices/studio-test-matrix.md`](../appendices/studio-test-matrix.md) for why: this session's Browser pane tool cannot reliably composite frames for automated visual verification, the same `document.visibilityState` limitation identified in Sprint 8). Deterministic component/integration tests (35 new/changed) are the durable, repeatable substitute.

## Known UX gaps

22 new gaps catalogued in [`283-studio-gap-analysis.md`](283-studio-gap-analysis.md) (named projects, multiple designs, undo/redo, richer notifications, bundled downloads, per-artifact error messages, and more) — none requiring jewelry expertise, all explicitly out of this Sprint's scope.

## Architecture debt preserved (re-confirmed, not re-solved)

`ModelService.generate()` remains mixed-responsibility (Sprint 6); no explicit `GeometryPlan` runtime exists (Sprint 6); export-version-fingerprint gaps remain partial (Sprint 7); the `definitionHash`-only cache-identity risk remains (Sprint 6); STEP export remains geometrically-but-not-byte-for-byte deterministic (Sprint 7); external CAD interoperability remains unvalidated beyond CadQuery's own self-consistency (Sprint 7/8). None were touched this Sprint, per its own explicit instruction not to solve unrelated backend architecture debt.

## Validation results

| Check | Result |
|---|---|
| All 5 Studio JSON Schemas valid (Draft 2020-12) | Yes |
| All 6 examples pass their respective schemas | 6 / 6 |
| Every example lists exactly the 5 current outputs | Confirmed |
| State-transition vectors cover all 7 model states | Confirmed |
| Export-eligibility vectors cover all 5 states | Confirmed |
| Markdown relative links across `docs/bible/` (331 files checked) | All resolve, after this report's own file was created |
| Front matter completeness (all 10 fields, on all 44 Sprint 9 files) | Complete |
| Duplicate Bible document IDs | None found (331 files, 331 unique IDs) |
| Personal email addresses / absolute local Windows paths | None found in any Sprint 9 file |
| Technical View preserved | Yes |
| Presentation View preserved | Yes |
| STEP/STL/JSON export still work | Yes — real network calls confirmed live |
| Technical Specification still works | Yes |
| PNG capture still works | Yes — confirmed live via the new Outputs-tab entry point |
| Backend tests | **204 passed** (199 pre-existing + 5 new, `test_studio_schemas.py`) |
| Backend lint (`ruff check`) | Clean |
| Frontend tests | **107 passed** (72 pre-existing + 35 new/changed across 4 new/changed test files) |
| Frontend lint (`oxlint`) | Clean |
| Frontend type check (`tsc -b`) | Clean |
| Frontend production build (`vite build`) | Succeeds |
| Geometry/export/Vision/Studio-schema tests | **53 passed** (`test_geometry.py`, `test_atlas_registry.py`, `test_alchemist_registry.py`, `test_foundry_registry.py`, `test_export_integrity.py`, `test_filenames.py`, `test_vision_schemas.py`, `test_studio_schemas.py`) |

## What was, and was not, changed in application code

**Changed** (real product improvement, explicitly authorized by this Sprint's scope): 3 new frontend pure-logic modules, 3 new components, 5 modified components, 1 mixed-modification component, 2 store additions, CSS additions. **Not changed**: STEP/STL export output, any backend geometry/validation/export code, the public API request/response contracts, and Vision v1's core rendering pipeline (materials, lighting, camera math). Every claim above is backed by the full backend and frontend test suites passing, plus a live browser session exercising the real, running application end-to-end.
