---
id: JM-BIBLE-012
title: Current User Journey
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-011
  - JM-BIBLE-013
implementation_status: current
---

# Current User Journey

This is the actual, current, observable flow through the application
today — every step is backed by a specific component or endpoint.

1. **Open application.** The frontend loads with either the default
   `JewelryDefinition` or a previously saved one from `localStorage`
   (`frontend/src/store/persistence.ts`). The permanent professional-review
   notice is visible in the header (`ProfessionalReviewNotice.tsx`).

2. **Configure solitaire parameters.** The user edits ring, band, stone,
   setting, material, and manufacturing fields in the left panel
   (`ConfigurationPanel.tsx`). The JSON tab updates immediately
   (`JsonViewer.tsx`).

3. **Review validation.** The Validation tab shows live results from the
   frontend mirror (`shared/validation/engine.ts`) as the user types
   (`ValidationPanel.tsx`).

4. **Generate model.** Pressing "Generate model" calls
   `POST /api/models/generate`; the backend re-validates authoritatively
   and, if valid, builds real geometry and returns preview mesh URLs plus
   metadata (`ProjectActions.tsx`, `useProjectStore.ts::generate`).

5. **Inspect preview.** The center viewport renders the returned
   component meshes in an orbit-controllable 3D view, with grid/axes
   toggles and per-component visibility checkboxes
   (`ModelViewport.tsx`).

6. **Modify parameters.** Any further edit updates `currentDefinition`
   and marks the currently-shown model **stale**
   (`useProjectStore.ts`'s `isStale` flag) — the viewport shows a "
   Parameters changed — regenerate model." banner, and export buttons
   disable.

7. **Regenerate stale model.** Pressing "Regenerate model" repeats step 4.
   If regeneration fails, the last successful preview stays visible
   instead of blanking (`useComponentGeometries.ts`).

8. **Export files.** Once a non-stale, error-free model exists, "Export
   STEP", "Export STL", and "Export JSON" become enabled; the
   Specification tab renders the Markdown technical specification
   (`TechnicalSpecification.tsx`, `POST /api/models/specification`).

9. **Submit files to professional review.** This step happens outside
   JewelMind — the application's role ends at producing the preliminary
   files and repeating the review requirement in every export (LAW-010).

## What this journey does not include (today)

- No account creation or login — there is nothing to sign in to.
- No save-to-server — only `localStorage` persists a project across
  sessions, and only one project at a time (see
  [`005-current-product-status.md`](../00-foundation/005-current-product-status.md)).
- No collaboration step — one browser tab, one user, one project.
