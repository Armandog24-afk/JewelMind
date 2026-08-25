---
id: JM-BIBLE-233
title: Stone Material Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-231
related_documents:
  - JM-BIBLE-143
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Material Model

## StoneReference is not a certified gemstone model

Restating LAW-006/[`07-atlas/143-stone-metal-separation-contract.md`](../07-atlas/143-stone-metal-separation-contract.md): `stone_reference` is a placeholder geometric reference for the stone's size and position, never a gemological reproduction. This document's material choices exist to make that reference *visually legible as "a stone"* in Presentation mode — never to simulate a diamond's actual optical behavior.

## The two presets, exactly as shipped

| Parameter | Technical | Presentation |
|---|---|---|
| Color | `#bfe3ff` (light reference-blue) | `#eaf6ff` (near-white) |
| Metalness | 0.1 | 0 |
| Roughness | 0.05 | 0.03 |
| Opacity | 0.55 | 1 (opacity is irrelevant once transmission is active) |
| Transmission | 0 | 0.92 |
| IOR | 1.0 | 2.4 |
| Thickness | 0 | 1.2 |
| Clearcoat | 0 | 1 |

Technical mode's semi-transparent light blue matches the pre-Sprint-8 viewer's stone appearance exactly (`STONE_COLOR = '#bfe3ff'`, `opacity: 0.55` were the original hardcoded constants) — deliberately preserved for continuity, now sourced from `materials.ts` instead of being inline in `ModelViewport.tsx`.

## Why `ior: 2.4` in Presentation mode, without claiming diamond-accurate optics

2.4 is in the general neighborhood of diamond's real refractive index (~2.417), chosen because it produces a visually convincing "faceted gem" transmission effect with Three.js's `MeshPhysicalMaterial`, not because this codebase claims to simulate a diamond's actual dispersion, faceting, or brilliance pattern — `stone_reference`'s geometry itself is a simple reference solid (see [`07-atlas`](../07-atlas/) domain docs), not a faceted gem mesh, so no amount of material tuning could produce real gemological optics regardless of the IOR chosen. This is stated explicitly so the number is never later mistaken for a precision claim.

## Investigated and chosen: `MeshPhysicalMaterial` transmission, not a custom shader

Three.js's built-in `transmission`/`ior`/`thickness`/`clearcoat` properties on `MeshPhysicalMaterial` were used exactly as the task's own investigation pointed toward — no custom GLSL shader was written, avoiding the stability and maintenance risk a bespoke shader would add for a Sprint whose scope explicitly favors safe, well-supported building blocks.

## Always distinct from every metal

`materials.test.ts::'keeps the stone visually distinct from every metal color'` asserts the stone's technical color never collides with any of the 5 metal colors — a structural guarantee, not a visual judgment call left untested.
