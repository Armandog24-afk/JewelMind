---
id: JM-BIBLE-228
title: Presentation View Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-222
related_documents:
  - JM-BIBLE-231
implementation_status: current
professional_validation: not_required
normative: true
---

# Presentation View Contract

## Naming

This feature is called **"Presentation View"** or **"Presentation Rendering"** everywhere in this codebase and its documentation — never "photorealistic," "cinematic," or "path-traced." It uses real-time WebGL rasterization (Three.js's standard forward renderer with PBR materials and an image-based-lighting environment), not ray/path tracing, and no measurement exists to support a photorealism claim.

## What Presentation mode provides, exactly

| Requirement | Implementation |
|---|---|
| Realistic-enough metal appearance | `meshPhysicalMaterial`, `metalness: 0.95`, per-metal roughness, `envMapIntensity: 1`, lit by a procedural `RoomEnvironment` |
| Distinguishable stone appearance | `transmission: 0.92`, `ior: 2.4`, `clearcoat: 1` — a stylized clear/refractive look, explicitly not a claim of accurate diamond optics |
| Professional lighting | 1 soft ambient + key/fill/rim directional lights + environment lighting; see [`230-lighting-system.md`](230-lighting-system.md) |
| Clean background | Flat light neutral gray (`#dedad5`), no pattern, no remote texture |
| Shadows/contact grounding | `ContactShadows`, grounded at the model's real bounding-box minimum Y; see [`235-shadows-and-grounding.md`](235-shadows-and-grounding.md) |
| Perspective camera | Same `PerspectiveCamera` as Technical mode — no separate camera type |
| Controlled camera framing | Same 5 bounding-box-driven presets as Technical mode |
| Screenshot/image export | "Save render" button, real client-side PNG capture; see [`238-image-capture-contract.md`](238-image-capture-contract.md) |
| No debug overlays by default | Grid/axes are force-disabled in Presentation mode regardless of the stored toggle |

## No paid assets, no remote dependency

The environment is `three-stdlib`'s `RoomEnvironment()` (a small procedural Three.js scene), converted to a reflection/lighting environment via drei's `<Environment>` in "portal" mode (rendering the given `children`/`scene` into an offscreen PMREM target) — no HDRI file, no CDN fetch, no paid asset pack. Confirmed by inspection: `Environment`'s `scene`/portal-children path never issues a network request, unlike its `preset`/`files` modes (which this codebase does not use). See [`234-background-and-environment-model.md`](234-background-and-environment-model.md).

## Never a manufacturability claim

Restating VISION-GOV-005/LAW-010: nothing in Presentation mode's UI ever states or implies that the rendered image demonstrates the ring is ready for production. The professional-review notice remains visible in the same header area regardless of view mode.
