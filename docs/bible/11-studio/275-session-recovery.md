---
id: JM-BIBLE-275
title: Session Recovery
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-274
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Session Recovery

## On page reload, exactly what happens

1. `useProjectStore`'s `initialDefinition = loadDefinition() ?? createDefaultDefinition()` restores the last saved, structurally-valid design (or falls back to the default) — confirmed live this Sprint: a `band.profile` change to `flat` made in an earlier session was still present after closing and reopening the app in a fresh browser tab.
2. `validationResults` is recomputed instantly from the restored definition — never restored from storage, since a stale validation result could describe an app version whose rules have since changed.
3. `generatedModel`/`lastSuccessfulPreview` start `null` — restating [`274-local-persistence-model.md`](274-local-persistence-model.md): the backend's model cache is not guaranteed to still hold a matching entry, so the frontend never pretends otherwise. `ModelStatusBadge` correctly shows `NO_MODEL` immediately after a reload, even though the design itself was restored.
4. `useVisionStore`'s `viewMode` is restored from its own storage key; every other Vision field (`componentVisibility`, `selectedComponent`, camera) resets to its default.

## Restored design vs. restored generated geometry — never conflated

This is the one distinction this document exists to make explicit: a user reopening the app sees their design parameters exactly as they left them, but must generate again to see geometry — the UI never shows a viewport as if a model existed when it does not. This was true before this Sprint (the backend cache was never persisted either) and is unchanged; this Sprint's contribution is naming and documenting it as a deliberate guarantee rather than leaving it as an unstated fact.

## What corrupted data does

If `localStorage`'s design entry is corrupted, unavailable, or structurally invalid, `loadDefinition()` returns `null` and the app silently starts from `createDefaultDefinition()` — no error dialog, no crash, no partial/garbled definition ever reaches the rest of the app. Confirmed unchanged by direct inspection of `persistence.ts` (untouched this Sprint).
