---
id: JM-BIBLE-239
title: Render State Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-221
related_documents:
  - JM-BIBLE-A44
implementation_status: partial
professional_validation: not_required
normative: true
---

# Render State Model

## `VisionState` — the real store shape

`frontend/src/store/useVisionStore.ts`, exactly as implemented:

| Field | Type | Status |
|---|---|---|
| `viewMode` | `'technical' \| 'presentation'` | CURRENT |
| `componentVisibility` | `Record<string, boolean>` | CURRENT |
| `selectedComponent` | `string \| null` | CURRENT |
| `showGrid` | `boolean` | CURRENT |
| `showAxes` | `boolean` | CURRENT |

Fields this Sprint's own brief listed conceptually but that are **not** separate store fields, because they are either derived or already owned by `useProjectStore`:

| Conceptual field | Real source |
|---|---|
| `cameraPreset` | Not stored — camera changes are imperative (`camera.position.set()`/`controls.target.set()` via refs), never round-tripped back into state. A preset button press is a one-time pose application, not a persisted mode. |
| `cameraPosition` / `cameraTarget` | Live on the Three.js camera/controls objects themselves, never mirrored into React state (mirroring a value that changes on every orbit-drag frame into state would cause excessive re-renders) |
| `metalPresentation` | Derived at render time from `useProjectStore`'s `currentDefinition.material.metal` — Vision never stores its own copy, so it can never drift from the JDL-selected metal |
| `stonePresentation` | Not a separate flag — presentation-vs-technical stone material is entirely a function of `viewMode` |
| `environmentPreset` | Exactly one value exists today (`RoomEnvironment`); not worth a state field until a second option exists |
| `backgroundMode` | Same reasoning — one value per `viewMode`, not independently selectable yet |
| `stale`, `modelId`, `definitionHash` | Owned by `useProjectStore`, read directly where needed, never duplicated into `useVisionStore` |

## `SceneStateSnapshot` — a composed view, not a stored shape

`frontend/src/vision/types.ts::SceneStateSnapshot` exists as a **documentation and potential-future-use type**, composing fields from both stores at the moment something needs a combined snapshot (e.g. a future structured capture-metadata feature). No code in this Sprint actually constructs one at runtime — it is PLANNED as a real composed object, CURRENT only as a type definition. This is stated honestly rather than implying it is already wired into the capture flow.

## No Three.js object ever appears in public state

Confirmed by inspection: `vision/types.ts` contains only primitives, plain tuples, and string unions — no `THREE.Vector3`, no `THREE.Camera`, no `THREE.Material`. `CameraState.position`/`target` are `[number, number, number]` tuples, matching `computeCameraPreset()`'s own return type.

## Machine-readable schemas

`specs/vision/v1/scene-state.schema.json`, `camera-state.schema.json`, `component-visual-state.schema.json`, `material-presentation.schema.json` — all validated against `frontend/src/vision/types.ts`'s shapes by hand-checked correspondence (TypeScript and JSON Schema are two different type systems; there is no automatic generator between them in this codebase, so this correspondence is maintained by convention, not tooling, and should be re-checked whenever either side changes).
