---
id: JM-BIBLE-235
title: Shadows and Grounding
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-228
related_documents:
  - JM-BIBLE-123
implementation_status: current
professional_validation: not_required
normative: true
---

# Shadows and Grounding

## Investigated: does the coordinate orientation support a ground plane?

Yes. Per [`07-atlas/123-coordinate-system-and-orientation.md`](../07-atlas/123-coordinate-system-and-orientation.md), the finger-hole axis (backend Y) maps to the horizontal scene Z axis, and the stone-pointing axis (backend Z) maps to the vertical scene Y (up) axis — see [`225-scene-graph-model.md`](225-scene-graph-model.md). This means the ring's natural pose after the existing `-90°` rotation already has it "standing on edge," exactly how solitaire rings are conventionally displayed in product photography (upright, viewed three-quarter or from the side) — not lying flat or hole-up. A ground plane at the model's true bounding-box minimum Y is a physically sensible choice here, not an unnatural pose. **No geometry rotation was added or changed to achieve this** — the existing transform already produces the right orientation; only the camera and the ground's Y position needed to be computed correctly.

## Implementation: `ContactShadows`, not a literal ground mesh

`@react-three/drei`'s `ContactShadows` component (a soft, blurred shadow-catching plane rendered from an offscreen camera beneath the model) was used instead of a literal lit ground plane with `receiveShadow`. This was a deliberate choice: `ContactShadows` produces a clean, professional-looking soft shadow without needing to tune a full shadow-mapped directional light's bias/resolution for a physical ground material, and it never risks the ground plane itself catching a stray reflection that looks like an unintended floor.

## Positioning, grounded in the real bounding box

`computeGroundY(bbox)` (in `frontend/src/vision/camera.ts`) returns the scene-space minimum Y of the model's real bounding box; `ContactShadows` is positioned at `[0, groundY - 0.05, 0]` — a small `0.05`-unit offset below the model's true bottom to avoid Z-fighting with the model's own bottom faces. This is never a fixed constant independent of model size — confirmed by `camera.test.ts::computeGroundY`.

## Technical mode has no grounding

`ContactShadows` and the ground concept generally are Presentation-only — Technical mode's grid (when enabled) already serves as the spatial reference technical inspection needs, and adding a shadow-catcher there would only add GPU cost without inspection value.

## Camera moves; geometry never does

Restating this Sprint's own explicit instruction: no component's rotation or position was changed to produce a "better shot." Every camera preset moves only the camera and `OrbitControls.target` — the model's geometry, as received from the backend, is rendered exactly as delivered, always through the same single, pre-existing `-90°` group rotation.
