---
id: JM-BIBLE-229
title: Camera System
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-225
related_documents:
  - JM-BIBLE-237
  - JM-BIBLE-A42
implementation_status: current
professional_validation: not_required
normative: true
---

# Camera System

## The 5 presets, grounded in the real coordinate convention

Direction vectors below are expressed in scene coordinates, after the `-90°` X-axis transform documented in [`225-scene-graph-model.md`](225-scene-graph-model.md) — none was chosen arbitrarily; each follows directly from [`07-atlas/123-coordinate-system-and-orientation.md`](../07-atlas/123-coordinate-system-and-orientation.md)'s confirmed facts: the finger-hole axis (backend Y) becomes scene `-Z`, and the stone-pointing axis (backend Z) becomes scene `Y` (up).

| Preset | Direction (scene space) | Rationale |
|---|---|---|
| `perspective` | `(1, 0.75, 1)` normalized | The general-purpose default/reset angle — a balanced three-quarter-like view, close to but distinct from the dedicated three-quarter preset |
| `front` | `(1, 0.12, 0.001)` normalized | Along the scene X axis (perpendicular to both the finger-hole axis and up) — shows the band's full circular profile with the stone rising near the top edge, a standard ring-elevation shot |
| `side` | `(0.001, 0.12, 1)` normalized | Along the scene Z axis — looking down the finger-hole axis, showing the band's width/thickness profile and the prong silhouette from the side |
| `top` | `(0.0001, 1, 0.0002)` normalized | Along the scene Y (up) axis — the stone-table view, looking straight down at the setting, as a solitaire ring is classically photographed standing upright |
| `three_quarter` | `(1, 0.8, 1)` normalized | The pre-existing fit-to-view diagonal angle, reused for continuity — matches what `fitToView()` already computed before this Sprint |

All 5 are implemented in one pure function, `frontend/src/vision/camera.ts::computeCameraPreset()`, with zero Three.js import — testable and tested (`camera.test.ts`, 8 tests) without a WebGL context.

## Bounding-box-driven distance, never fixed

Every preset computes `distance = size * marginFactor` from the model's real bounding box (`backendBoundingBoxToScene()`), where `size` is the diagonal length of the bounding box in scene units, floored at a minimum of 5mm-equivalent to avoid a degenerate distance for a zero-size or missing model. This directly satisfies the product requirement: "No hardcoded assumption that every future ring has identical size" — confirmed by `camera.test.ts`'s test comparing a small and a large bounding box.

## Known minor limitation: top view and OrbitControls

Setting the camera to look nearly straight down the Y axis (the `top` preset) can produce a brief control-orientation ambiguity in `OrbitControls` immediately after the jump, a well-known minor quirk of orbit-style controls near the pole of their orbit sphere — not fixed in this Sprint, and not considered blocking (the camera position/target are still set correctly; only the *initial* orbit drag direction right after clicking "Top" can feel slightly different than expected). Recorded in [`247-vision-gap-analysis.md`](247-vision-gap-analysis.md).

## Fit vs. Three-quarter

`computeFitPose()` is defined as exactly `computeCameraPreset('three_quarter', bbox)` — "Fit to view" and the "Three-quarter" preset button produce the identical camera pose today, confirmed by `camera.test.ts::'computeFitPose is equivalent to the three_quarter preset'`. This is an intentional simplification, not an oversight: both concepts mean "show me the whole model from a good angle," so unifying them avoids two subtly different distance formulas drifting apart over time.
