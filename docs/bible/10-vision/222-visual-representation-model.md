---
id: JM-BIBLE-222
title: Visual Representation Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-221
related_documents:
  - JM-BIBLE-192
implementation_status: current
professional_validation: not_required
normative: true
---

# Visual Representation Model

## Two representations, one geometric source

| Representation | Purpose | Category (restating [`09-foundry/192-artifact-domain-model.md`](../09-foundry/192-artifact-domain-model.md)) |
|---|---|---|
| Technical View | Engineering/design inspection: orbit, presets, component isolation, status | `PREVIEW_ARTIFACT` (on-screen only) |
| Presentation View | Visually evaluating the jewelry as an object | `PREVIEW_ARTIFACT`; its PNG capture output is its own artifact, see [`238-image-capture-contract.md`](238-image-capture-contract.md) |

Both representations are views over the identical `THREE.BufferGeometry` set produced by `useComponentGeometries()` for the current `lastSuccessfulPreview` — switching between them never re-fetches, re-parses, or re-tessellates anything.

## What varies between the two views

| Aspect | Technical | Presentation |
|---|---|---|
| Material | Flatter, `envMapIntensity: 0`, metal color still follows JDL selection | Full PBR, environment-lit, per-metal roughness variation |
| Stone | Opaque-ish reference blue, `transmission: 0` | Transmissive, clear "gemstone-like" look |
| Lighting | 1 ambient + 2 directional (unchanged from the pre-Sprint-8 viewer) | 1 soft ambient + 3 directional (key/fill/rim) + procedural `RoomEnvironment` |
| Background | Dark neutral (`#15171a`, matches the app's own dark theme) | Light neutral studio gray (`#dedad5`) |
| Grid/axes | Available, toggleable | Always off |
| Grounding/shadow | None | `ContactShadows`, grounded at the model's real bounding-box minimum |
| Camera default | Same presets, same bounding-box-driven distance | Same presets, same bounding-box-driven distance |

## What never varies

Component identity, component visibility state, the underlying `BufferGeometry` vertex data, the coordinate transform, and the definition/model that's being shown — restating [`244-visual-consistency-contract.md`](244-visual-consistency-contract.md)'s core guarantee at the representation level.
