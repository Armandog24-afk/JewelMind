---
id: JM-BIBLE-225
title: Scene Graph Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-221
related_documents:
  - JM-BIBLE-123
implementation_status: current
professional_validation: not_required
normative: true
---

# Scene Graph Model

## The real scene, as rendered by `ModelViewport.tsx`

```
Canvas
├── PerspectiveCamera (makeDefault, ref: cameraRef)
├── OrbitControls (makeDefault, ref: controlsRef)
├── color (scene background — technical dark or presentation light neutral)
├── Lights (mode-dependent — see 230-lighting-system.md)
├── Environment (presentation only — procedural RoomEnvironment via PMREM)
├── ContactShadows (presentation only — grounding, see 235-shadows-and-grounding.md)
├── gridHelper / axesHelper (technical only, toggleable)
└── group (rotation: [-π/2, 0, 0] — the one, single Atlas→scene coordinate transform)
    ├── ComponentMesh "band"
    ├── ComponentMesh "prongs"
    ├── ComponentMesh "basket_support"
    └── ComponentMesh "stone_reference"
```

This matches the conceptual `VisionScene` shape from this Sprint's own specification exactly, with two honest naming differences: there is no separate `JewelryRoot` node (the `<group rotation=...>` plays that role directly) and `Ground` is `ContactShadows`, not a literal ground-plane mesh (see [`235-shadows-and-grounding.md`](235-shadows-and-grounding.md) for why a shadow-catcher was chosen over a literal plane).

## One transform, defined once

The `-90°` X-axis rotation is the single place Atlas's backend coordinate convention (Y = finger-hole axis, Z = toward the stone — see [`07-atlas/123-coordinate-system-and-orientation.md`](../07-atlas/123-coordinate-system-and-orientation.md)) is mapped into the scene's Y-up convention. It is applied exactly once, on the `<group>` wrapping every `ComponentMesh`. `frontend/src/vision/camera.ts::backendBoundingBoxToScene()` expresses the identical mapping in pure-function form for camera math, so the transform is never independently re-derived or allowed to drift between rendering and camera placement — both are grounded in the same documented fact: `(x, y, z)_backend -> (x, z, -y)_scene`.

## No duplicated transforms between backend and frontend

The backend never applies this rotation — `GeneratedModel`'s bounding box and every component's STL are in Atlas's own coordinate system throughout. The frontend applies the transform exactly once, at render time, never persisting a rotated copy anywhere.
