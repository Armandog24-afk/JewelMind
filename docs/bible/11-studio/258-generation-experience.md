---
id: JM-BIBLE-258
title: Generation Experience
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-257
related_documents:
  - JM-BIBLE-259
implementation_status: current
professional_validation: not_required
normative: true
---

# Generation Experience

## The single Generate/Regenerate action

`ProjectActions.tsx` renders exactly one primary button, labeled `Generate model` (no model yet), `Regenerate model` (a model already exists), or `Generating…` (in flight) — restating this Sprint's explicit requirement ("one obvious primary generation action... do not present separate confusing generation buttons in multiple panels"). Confirmed by code inspection: no other component in this codebase calls `useProjectStore.generate()`.

## Blocking is explicit, never a false promise

When blocking (`error`-severity) validation results exist, the button is `disabled` and its `title` reads "Resolve the blocking validation errors first" — the button never appears clickable-but-doomed-to-fail. This was already true before this Sprint (`blockedByErrors` in `ProjectActions`); this Sprint added the explanatory `title` and the shortcut hint.

## During generation

- `LoadingOverlay` ("Generating model…") appears over the viewport — pre-existing, unchanged.
- The button itself becomes disabled and relabels to "Generating…", preventing a duplicate submission by construction (there is no separate "cancel and resubmit" path).
- `lastSuccessfulPreview` (and therefore the rendered geometry) is untouched during this window — the previous model, if any, remains fully visible and interactive.
- No fake percentage is shown — `generationStatus` is a 4-value enum (`idle`/`generating`/`success`/`error`), never a numeric progress value, because the backend does not report incremental progress (a single synchronous `POST /api/models/generate` call).

## After a successful generation

`generate()`'s success branch (unchanged this Sprint) updates `generatedModel`, `lastSuccessfulPreview`, `validationResults` (from the backend's own re-validation), `isStale: false`, and `generationStatus: 'success'` in one atomic `set()` call — so the UI never shows an inconsistent intermediate combination (e.g. a new `modelId` with the old `isStale: true`).

## Keyboard shortcut

`G` triggers the same `generate()` call as clicking the button, gated by the identical `canGenerate` check (not generating, no blocking errors) and ignored while a text field has focus — see [`273-keyboard-and-input-model.md`](273-keyboard-and-input-model.md). Verified live: pressing `G` after a stale edit produced a real `POST /api/models/generate` call and returned the model to `CURRENT`.
