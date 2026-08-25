---
id: JM-BIBLE-238
title: Image Capture Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-228
related_documents:
  - JM-BIBLE-240
implementation_status: current
professional_validation: not_required
normative: true
---

# Image Capture Contract

## What "Save render" does, exactly

`ModelViewport.tsx::handleCapture()`, wired to the `PresentationPanel`'s "Save render" button:

1. Checked against `captureBlockedReason(hasModel, isStale)` (`frontend/src/vision/capture.ts`) — if a model doesn't exist yet or is stale, the button is disabled outright and the handler returns immediately.
2. Temporarily resizes the WebGL renderer and camera aspect to `1920×1080` (`gl.setSize(1920, 1080, false)`, `camera.aspect = 1920/1080`), independent of the visible canvas's on-screen size.
3. Calls `gl.render(scene, camera)` once, synchronously, to draw the high-resolution frame.
4. Calls `gl.domElement.toBlob(callback, 'image/png')` — this snapshots the canvas's current pixels **synchronously** at call time (per the HTML Canvas spec, only PNG *encoding* happens asynchronously), so no `preserveDrawingBuffer: true` renderer flag is needed for every normal frame.
5. In a `finally` block: restores the renderer/camera to their previous size and re-renders once, so the live, on-screen view is never left stretched or resized.
6. On a successful blob, builds a safe filename (`frontend/src/vision/filename.ts::buildCaptureFilename()`) and triggers a client-side download via the pre-existing `triggerBrowserDownload()` helper (already used for STEP/STL/JSON/specification exports).

## Trade-off, documented per this Sprint's own instruction

The alternative to steps 3–4 would be setting `preserveDrawingBuffer: true` on the renderer permanently, which disables a browser optimization and costs a small amount of performance on every single frame, forever, for a feature used occasionally. Rendering synchronously immediately before reading is the standard, well-documented Three.js/WebGL technique for occasional captures and was chosen instead — it has zero cost on frames where no capture occurs.

## Excludes UI overlays by construction

The captured image comes from the WebGL canvas's own pixel buffer, never a DOM/CSS screenshot of the viewport panel — the toolbar, component-visibility panel, and presentation panel are separate, absolutely-positioned HTML elements layered on top of the canvas via CSS, and are structurally invisible to `toDataURL`/`toBlob`, which only ever see what was actually drawn into the WebGL drawing buffer.

## Resolution

Fixed at `1920×1080` today — the one high-resolution capture size implemented this Sprint (see [`23. OPTIONAL HIGH-RES CAPTURE`] in the Sprint 8 brief). A square product-image variant was deliberately not added as a second UI control, to avoid interface clutter; `handleCapture()`'s resize/render/restore logic is resolution-agnostic, so adding a second size is a small, contained follow-up — recorded as `FOUNDRY`-style gap `VISION-GAP-004` in [`247-vision-gap-analysis.md`](247-vision-gap-analysis.md).

## Filename

`jewelmind-{sanitized-project-name}-presentation-{ISO-timestamp}.png` — sanitized by `frontend/src/vision/filename.ts::sanitizeForFilename()`, a small frontend-only utility conceptually mirroring (never calling) the backend's `exporters/filenames.py::sanitize_filename()`. No internal model ID or definition hash appears in the filename.

## Deterministic scene setup, honestly qualified

Given the same `modelId`, `viewMode`, `componentVisibility`, metal, and camera position, the capture is deterministic — no randomness or animation exists anywhere in the render path. What is **not** pinned automatically is the camera's exact position at the moment of capture (it reflects whatever orbit state the user left it in) — this is intentional, since the whole point of camera controls is to let the user choose the framing before capturing.

## Never a manufacturing artifact, never AI-generated, never a professional photograph

The captured PNG is a **Vision artifact** — restating VISION-GOV-005/013 and CLAUDE.md's constitution: it is not CAD, not a manufacturing artifact, not a gemological simulation, and not an AI-generated image. It is a real-time WebGL rasterization of the actual Atlas-derived geometry, captured client-side, nothing more and nothing less.

## What was and was not automated-tested

`frontend/src/vision/capture.test.ts` (5 tests) and `filename.test.ts` (4 tests) cover the pure gating and naming logic. The actual `gl.render()`/`toBlob()`/download sequence requires a real WebGL context and was exercised via a live browser session against the running dev server during this Sprint's manual verification pass — see [`SPRINT-8-VALIDATION-REPORT.md`](SPRINT-8-VALIDATION-REPORT.md) for exactly what that session did and did not confirm.
