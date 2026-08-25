---
id: JM-BIBLE-237
title: Model Framing and Fit
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-229
related_documents:
  - JM-BIBLE-A42
implementation_status: current
professional_validation: not_required
normative: true
---

# Model Framing and Fit

## Algorithm, exactly

1. Read the current model's real bounding box (`GenerateResponse.metadata.boundingBoxMm`), or fall back to a fixed `[-10, 10]`-per-axis box when no model has been generated yet.
2. Map it into scene coordinates (`backendBoundingBoxToScene()` — the single, shared coordinate transform, see [`225-scene-graph-model.md`](225-scene-graph-model.md)).
3. Compute the center and the diagonal size, floored at a 5-unit minimum.
4. Position the camera at `center + normalize(direction) * size * 1.6` and set `OrbitControls.target = center`.

This is identical logic for "Fit to view" and every named camera preset — they differ only in `direction`, never in the framing algorithm itself.

## Verified against varying model sizes

`camera.test.ts::'scales camera distance with model size instead of using a fixed distance'` directly compares a small (8mm-scale) and a large (40mm-scale) bounding box and asserts the computed camera distance scales accordingly (more than 2× farther for the large model) — this is the concrete evidence behind "no hardcoded assumption that every future ring has identical size."

## Verified for an off-center model

`camera.test.ts::'targets the model bounding-box center, not the world origin, for an off-center model'` uses a bounding box centered far from the origin and confirms the computed target tracks the real center — relevant because a future component or assembly change is not guaranteed to keep everything centered at `(0,0,0)`.

## No clipping guarantee, and its limit

The `near`/`far` planes on the `PerspectiveCamera` (`0.1` / `2000`) are fixed constants, not derived from the model's size — for the realistic range of ring dimensions this system currently supports (millimeters to a few centimeters), this comfortably avoids near/far clipping. This is a real, if minor, hardcoded assumption that would need revisiting only if the system ever supported drastically different object scales (e.g. a full necklace) — noted honestly here rather than silently.

## What "component visibility changes" does to framing

Toggling a component's visibility does **not** automatically re-fit the camera — the bounding box used for framing is always the *full* model's bounding box (`lastSuccessfulPreview.metadata.boundingBoxMm`), regardless of which components are currently shown. This is a deliberate choice: re-fitting on every visibility toggle would make the camera jump unpredictably as a user experiments with hiding components, which is more disorienting than useful. A user who wants to reframe after hiding a component can press "Fit" again.
