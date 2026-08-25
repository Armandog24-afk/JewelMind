---
id: JM-BIBLE-269
title: Error Recovery Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-268
related_documents:
  - JM-BIBLE-259
implementation_status: current
professional_validation: not_required
normative: true
---

# Error Recovery Model

## What every failure tells the user, concretely

| Failure | What failed | Is the last model still available? | What can be retried | Do inputs need changing? |
|---|---|---|---|---|
| Generation fails | `ErrorBanner` shows `generationError` (the real backend message) | Yes, if one existed (`FAILED_WITH_LAST_GOOD`) — restated by the header badge and viewport banner | Press Generate/Regenerate again | Only if the message indicates a validation problem the client-side check missed |
| An export fails | `ArtifactRow` shows the error inline, eligibility becomes `FAILED` | Yes — export failure never touches `generatedModel`/`lastSuccessfulPreview` | Click the same Download button again | No — export failures are almost always transient/backend-side, not input problems |
| Preview mesh fails to load | `ErrorBanner`: "Could not load the 3D preview mesh from the backend. Showing the last successful preview, if any." | Yes — the geometry itself is unaffected, only its on-screen rendering | Regenerate, or simply wait/retry | No |

Every row above matches this Sprint's own required disclosure list exactly (what failed, last-model availability, retry path, input-change need) — none required new code to satisfy, since `generationError`/`exportError`/preview-mesh-error banners already existed; this Sprint's contribution was confirming each one still says all four things and pairing them with the new, centralized model-status vocabulary.

## No full-page reload required for any recoverable error

Confirmed by inspection: every failure path above sets React state (`generationStatus: 'error'`, `exportStatus[kind]: 'error'`, `hasError: true`) and re-renders in place — none calls `window.location.reload()` or throws an uncaught exception that would force one. A truly unrecoverable error (e.g. the backend process itself being down) is instead surfaced continuously via `BackendStatus`'s "Backend unreachable" indicator, polled every 15 seconds, rather than a one-time failure message.

## Real examples used for this Sprint's schemas

`specs/studio/v1/examples/generation-error-with-last-good.json` is grounded in this exact `FAILED_WITH_LAST_GOOD` path, not invented.
