---
id: JM-BIBLE-230
title: Lighting System
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-228
related_documents:
  - JM-BIBLE-234
implementation_status: current
professional_validation: not_required
normative: true
---

# Lighting System

## Technical mode (unchanged from the pre-Sprint-8 viewer)

| Light | Value |
|---|---|
| `ambientLight` | intensity `0.65` |
| `directionalLight` (key) | position `[25, 35, 15]`, intensity `1.1` |
| `directionalLight` (fill) | position `[-20, 10, -15]`, intensity `0.35` |

No environment map, no shadows — kept intentionally simple and cheap, since inspection (not visual polish) is Technical mode's job.

## Presentation mode (new this Sprint)

| Light | Value | Role |
|---|---|---|
| `ambientLight` | intensity `0.35` | Soft fill, lower than Technical's since the environment map now contributes ambient-like reflections too |
| `directionalLight` (key) | position `[25, 35, 15]`, intensity `1.2`, `castShadow` | Primary light, casts the `ContactShadows` grounding shadow |
| `directionalLight` (fill) | position `[-20, 12, 15]`, intensity `0.45` | Softens the key light's shadow side |
| `directionalLight` (rim) | position `[-8, 18, -25]`, intensity `0.5`, color `#dce8ff` (cool white) | Separates the model's silhouette from the background |
| `Environment` (procedural `RoomEnvironment`) | resolution `256` | Provides realistic metal reflections without any HDRI file or network fetch |

## Deliberately not "jewelry advertising" lighting

Values were chosen for readability and even illumination rather than dramatic contrast — no colored gel lights, no single hard spotlight, no lens flares. The rim light's cool tint is the only deliberately stylistic choice, included only to help the model separate from the light neutral background, not for drama.

## Real, not assumed

Every value above is copied directly from `frontend/src/components/ModelViewport.tsx` as actually shipped — this document does not describe a target lighting rig different from what runs.
