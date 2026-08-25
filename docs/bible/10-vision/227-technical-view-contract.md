---
id: JM-BIBLE-227
title: Technical View Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-222
related_documents:
  - JM-BIBLE-229
implementation_status: current
professional_validation: not_required
normative: true
---

# Technical View Contract

## What Technical mode provides, exactly

| Requirement | Implementation |
|---|---|
| Orbit / zoom / pan | `@react-three/drei`'s `OrbitControls`, `enableDamping`, unchanged from the pre-Sprint-8 viewer |
| Fit-to-model | `fitToView()` → `computeFitPose(bbox)`, bounding-box-driven (never a fixed distance) |
| Reset camera | `resetCamera()` → `computeCameraPreset('perspective', bbox)` |
| Standard camera presets | 5 presets — Perspective, Front, Side, Top, Three-quarter; see [`229-camera-system.md`](229-camera-system.md) |
| Component visibility | `ComponentVisibilityPanel`, plus "Show all"/"Metal only" quick actions |
| Technical component distinction | Metal keeps its selected JDL color but flatter/non-reflective (`envMapIntensity: 0`); the stone is opaque-ish light blue, clearly non-metal |
| Model status | Existing `ModelInformation` tab (component volumes, warnings, generation duration) — not duplicated inline, to avoid UI clutter |
| Stale-state indication | Existing `stale-banner`, unchanged, applies in both view modes |
| Generation warnings | Surfaced via the existing `ErrorBanner`/`ModelInformation` warnings list, unchanged |
| Optional grid/axes | `gridHelper`/`axesHelper`, toggleable, visible only in Technical mode |

## Selected-component highlighting

Implemented via the list-click mechanism in [`226-component-visual-identity.md`](226-component-visual-identity.md) rather than 3D raycasting/click-to-select — chosen deliberately as the lower-risk option ("if architecture allows safely," per this Sprint's own instruction), since it needs no pointer-event wiring inside the WebGL canvas and cannot misfire on an unrelated click.

## Deliberately not cluttered

No debug information is shown by default beyond what already existed (the grid was and remains on by default; axes were and remain off by default — both preserved unchanged in `useVisionStore`'s initial state). No FPS counter, no wireframe toggle, and no raw geometry stats were added to the primary viewer UI — that detail already lives in the `Model info` tab, which this Sprint did not duplicate.
