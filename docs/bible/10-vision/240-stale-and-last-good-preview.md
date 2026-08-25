---
id: JM-BIBLE-240
title: Stale and Last-Good Preview
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-220
related_documents:
  - JM-BIBLE-238
implementation_status: current
professional_validation: not_required
normative: true
---

# Stale and Last-Good Preview

## Preserved exactly, not reimplemented

This Sprint changed **zero lines** of `useProjectStore.ts`'s generation/staleness logic. The pre-existing behavior remains:

1. Editing any parameter after a successful generation sets `isStale: true` (`withUpdatedDefinition()`, unchanged).
2. `lastSuccessfulPreview` is only ever overwritten by a **successful** `generate()` call — a failed regeneration leaves it untouched.
3. `ModelViewport.tsx` renders geometry from `lastSuccessfulPreview`, never from `generatedModel` directly — so a stale or failed state never blanks the viewport while a previously-valid model exists.

Confirmed unchanged by `useProjectStore.test.ts::'keeps the last successful preview visible when a later generation fails'` and `'marks the definition stale after a parameter changes post-generation'` — both pre-existing tests, both still passing after this Sprint's changes.

## What Vision adds on top: capture is blocked, not merely labeled

Per this Sprint's own explicit preference ("Prefer blocking image export from stale geometry unless current UX strongly supports another safe approach"), `captureBlockedReason(hasModel, isStale)` (`frontend/src/vision/capture.ts`) returns `'stale'` whenever `isStale` is true, disabling the "Save render" button outright and showing the reason as a hint — never allowing a stale-model capture that could be mistaken for representing the current parameters.

## View-mode switching never affects staleness

Switching between Technical and Presentation reads `isStale` from `useProjectStore` but never writes to it — restating VISION-GOV-008/014: the stale banner and its underlying flag behave identically regardless of which view is active.

## Regeneration failure

If a regeneration fails after edits, `generationStatus` becomes `'error'`, `generationError` is set, and — critically — `lastSuccessfulPreview` (and therefore the rendered geometry) is untouched, so Vision continues showing the last model that actually succeeded, with an `ErrorBanner` explaining the failure alongside it. Vision never implies the still-visible geometry represents the failed regeneration's new parameters — the stale banner remains visible throughout, since `isStale` was already `true` before the failed attempt and nothing clears it on failure.
