---
id: JM-BIBLE-241
title: Rendering Errors and Diagnostics
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-220
related_documents:
  - JM-BIBLE-A45
implementation_status: partial
professional_validation: not_required
normative: true
---

# Rendering Errors and Diagnostics

## The 9 conceptual codes, mapped to real behavior

| Conceptual code | Real current handling |
|---|---|
| `VISION_MESH_LOAD_FAILED` | `useComponentGeometries()`'s fetch `catch` block sets `hasError: true`; `ModelViewport` shows an `ErrorBanner` while keeping the previous geometry set on screen. No dedicated error code string exists — the real code is a caught JS exception, logged via `console.error('Failed to load preview mesh:', err)`. |
| `VISION_MESH_PARSE_FAILED` | Same `catch` block also covers `STLLoader.parse()` throwing on a malformed buffer — indistinguishable from a fetch failure today. A real, honest gap: the two failure modes are not currently reported separately. |
| `VISION_WEBGL_UNAVAILABLE` | **Not implemented.** No code checks for WebGL availability before mounting `<Canvas>`; a browser without WebGL would fail inside `@react-three/fiber` itself, with whatever error message that library produces, not a JewelMind-specific message. |
| `VISION_RENDER_FAILED` | **Not implemented** as a distinct catch. React error boundaries are not used around `<Canvas>` today, so a runtime exception inside the R3F render tree would propagate as an unhandled React error, not a graceful in-app message. |
| `VISION_CAMERA_FAILED` | `applyPose()` guards against a null `camera`/`controls` ref (returns early, does nothing) — this prevents a crash but does not surface any message to the user; a preset click on an unmounted canvas is silently a no-op. |
| `VISION_CAPTURE_FAILED` | `handleCapture()`'s `gl.domElement.toBlob()` callback checks `if (blob)` before proceeding; a `null` blob (which `toBlob` can return in rare browser-internal failure cases) is silently ignored today — no error message shown. A real, honest gap. |
| `VISION_COMPONENT_MISSING` | Not a distinct error — a component absent from `previewComponents` simply never renders and never appears in the visibility panel; there is no "expected 4, got 3" check. |
| `VISION_MATERIAL_FALLBACK` | `resolveMetalMaterial()`'s fallback to `yellow_gold_18k` for an unrecognized key is silent — no warning is logged or shown, since `MetalType`'s closed union makes this path currently unreachable through normal UI interaction. |
| `VISION_GPU_RESOURCE_ERROR` | Not implemented — no code detects or reports a WebGL context-loss event (`webglcontextlost`) today. |

## Honest summary

**0 of 9 conceptual Vision diagnostic codes exist as named, distinct error types in the running application.** Two real failure paths exist and behave safely (mesh load/parse failure preserves the last good preview; camera-ref-not-ready is a safe no-op), but neither is reported with a stable, user-facing code — restating the same honesty this Bible applied to Foundry's `ExportFailedError` finding in Sprint 7: a documented vocabulary is not the same claim as an implemented one.

## What is guaranteed regardless

Per VISION-GOV-009, no rendering failure of any kind — mesh load, parse, camera, capture — ever marks the backend `GeneratedModel` invalid, deletes `lastSuccessfulPreview`, or blocks a subsequent STEP/STL/JSON/specification export. This is architecturally true because Vision's rendering code has no write access to `useProjectStore` at all (only reads), confirmed by inspection of every Vision-owned file's imports.

## Recorded as gaps, not silently accepted

See [`247-vision-gap-analysis.md`](247-vision-gap-analysis.md) for `VISION-GAP` entries tracking which of the 9 codes are worth implementing and in what priority order.
