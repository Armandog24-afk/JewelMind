---
id: JM-BIBLE-268
title: Loading and Progress Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-267
related_documents: []
implementation_status: partial
professional_validation: not_required
normative: true
---

# Loading and Progress Model

## Real stages, not fake percentages

| Stage | Real message | Where |
|---|---|---|
| Generating geometry | "Generating model…" | `LoadingOverlay`, shown during `generate()` |
| Regenerating | Same message — the overlay does not distinguish first-generation from regeneration, since the backend call is identical | `LoadingOverlay` |
| Loading specification | "Loading specification…" | `TechnicalSpecification.tsx`, pre-existing |
| Exporting an artifact | The artifact's own row shows "Preparing…" as its button label | `ArtifactRow`, new this Sprint |
| Capturing an image | `isCapturing` state renders "Rendering…" on the Presentation panel's button | `PresentationPanel.tsx`, Sprint 8 |

No stage anywhere shows a numeric percentage — confirmed by inspection: `generationStatus`, `exportStatus[kind]`, and `isCapturing` are all boolean/enum, never a 0–100 number, because the backend genuinely does not report incremental progress for any of these operations (each is one synchronous request/response). Per this Sprint's own instruction, no fake percentage was invented to fill that gap.

## "Validating…" is not a separate visible stage

Client-side validation (`shared/validation/engine.ts`) runs synchronously on every keystroke and completes in well under a frame — there is no meaningful window in which a "Validating…" message would be visible, so none was added. Server-side re-validation happens inside the same `generate()` call the "Generating model…" message already covers; a separate label for it would describe an internal step the user cannot distinguish from generation itself.

## No layout shift

`LoadingOverlay` is an absolutely-positioned overlay (`position: absolute; inset: 0`) rather than content that pushes surrounding elements — confirmed unchanged from before this Sprint. `ArtifactRow`'s "Preparing…" label replaces the button's own text in place, at the same size, so its row does not resize during an export.

## What remains PLANNED

Real, granular backend progress reporting (e.g. "meshing prongs… 2 of 4") does not exist and was not added this Sprint — the backend's `ModelService.generate()` remains a single synchronous call end-to-end; see [`08-alchemist/172-diagnostics-and-failure-propagation.md`](../08-alchemist/172-diagnostics-and-failure-propagation.md) for the same underlying architectural fact from the compiler side.
