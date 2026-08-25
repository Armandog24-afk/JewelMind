---
id: JM-BIBLE-220
title: Vision Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-120
  - JM-BIBLE-160
  - JM-BIBLE-190
related_documents:
  - JM-BIBLE-VISION-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Vision Governance

## VISION-GOV-001 through VISION-GOV-015

| ID | Rule |
|---|---|
| **VISION-GOV-001** | Vision must consume Atlas-derived geometry. Every mesh rendered in `ModelViewport.tsx` comes from `useComponentGeometries()` parsing a real backend-generated STL — never a shape constructed in the frontend. |
| **VISION-GOV-002** | Vision must never independently reconstruct jewelry geometry from JDL. No frontend code reads `band.width`, `stone.diameter`, or any other dimension to build a `THREE.BufferGeometry` — geometry always arrives pre-built from `/api/models/{id}/preview/{component}`. |
| **VISION-GOV-003** | The visual model and exported CAD model must share the same geometric origin — both are tessellated from the identical `GeneratedModel` produced by one `ModelService.generate()` call; see [`223-atlas-to-vision-contract.md`](223-atlas-to-vision-contract.md). |
| **VISION-GOV-004** | Visual materials must not alter source geometry. `resolveComponentMaterial()` (`frontend/src/vision/materials.ts`) only ever returns color/metalness/roughness/transmission-style parameters for a `meshPhysicalMaterial` — it never touches vertex data. |
| **VISION-GOV-005** | Presentation rendering must not be presented as proof of manufacturability — restates LAW-010 at the Vision layer; see [`228-presentation-view-contract.md`](228-presentation-view-contract.md) and the image-status statement in [`238-image-capture-contract.md`](238-image-capture-contract.md). |
| **VISION-GOV-006** | StoneReference must remain semantically distinct from production metal — every mesh's stone/metal classification comes from the explicit `geometryRole` field (added this Sprint to the preview manifest), never string-matched ambiguously; see [`226-component-visual-identity.md`](226-component-visual-identity.md). |
| **VISION-GOV-007** | Preview failure must not destroy the last successful visual model — restates the pre-existing, unchanged `lastSuccessfulPreview` behavior in `useProjectStore.ts`; see [`240-stale-and-last-good-preview.md`](240-stale-and-last-good-preview.md). |
| **VISION-GOV-008** | Stale visual state must be clearly detectable — the existing `isStale` flag and stale banner are preserved unchanged and now also gate presentation image capture. |
| **VISION-GOV-009** | Frontend rendering failures must not invalidate otherwise valid CAD geometry — a WebGL/mesh-parse failure surfaces an `ErrorBanner` and falls back to the last good preview; it never marks the backend `GeneratedModel` or its STEP/STL artifacts as invalid. |
| **VISION-GOV-010** | Visual assets must not introduce hidden external-runtime dependencies — the Presentation environment uses `three-stdlib`'s procedural `RoomEnvironment`, not a remote HDRI or CDN asset; see [`234-background-and-environment-model.md`](234-background-and-environment-model.md). |
| **VISION-GOV-011** | All component visibility must use explicit component identity — `useVisionStore`'s `componentVisibility` is always keyed by the real component name from the preview manifest, never by array index or render order. |
| **VISION-GOV-012** | Screenshot output must represent the current generated model — capture is blocked outright (not merely labeled) when the model is stale or absent; see [`238-image-capture-contract.md`](238-image-capture-contract.md). |
| **VISION-GOV-013** | No AI-generated render may substitute the actual CAD-derived model — Vision v1 contains no AI image-generation call anywhere. |
| **VISION-GOV-014** | Presentation styling must remain downstream from geometry — `viewMode`/material/camera state lives entirely in `useVisionStore`, structurally unable to influence `useProjectStore`'s definition or trigger `generate()`. |
| **VISION-GOV-015** | Visual improvements must not alter STEP/STL geometry — no file touched this Sprint under `backend/jewelmind/exporters/` changes export output; see [`SPRINT-8-VALIDATION-REPORT.md`](SPRINT-8-VALIDATION-REPORT.md) for the confirming test run. |

## When an ADR is required

Replacing Three.js/React Three Fiber, moving Vision state into `useProjectStore`, changing which coordinate transform maps Atlas space to scene space, or any change that violates VISION-GOV-001 through VISION-GOV-015 without superseding this document first.

## When an RFC is required

A new visual artifact class (e.g. turntable video, AR preview), a server-side rendering pipeline, or a structural change to the Technical/Presentation view split itself. Adding a single new camera preset or material preset does not require an RFC.
