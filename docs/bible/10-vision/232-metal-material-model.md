---
id: JM-BIBLE-232
title: Metal Material Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-231
related_documents:
  - JM-BIBLE-A43
implementation_status: current
professional_validation: not_required
normative: true
---

# Metal Material Model

## The 5 current presets, exactly as shipped

| Metal | Color | Presentation metalness / roughness | Technical metalness / roughness | `envMapIntensity` (presentation / technical) |
|---|---|---|---|---|
| `yellow_gold_18k` | `#d4af37` | 0.95 / 0.28 | 0.55 / 0.55 | 1 / 0 |
| `white_gold_18k` | `#e7e7ea` | 0.95 / 0.20 | 0.55 / 0.55 | 1 / 0 |
| `rose_gold_18k` | `#e3b7a4` | 0.95 / 0.30 | 0.55 / 0.55 | 1 / 0 |
| `platinum` | `#dcdcdc` | 0.95 / 0.18 | 0.55 / 0.55 | 1 / 0 |
| `silver` | `#c8c8ce` | 0.95 / 0.24 | 0.55 / 0.55 | 1 / 0 |

Technical mode's `metalness`/`roughness`/`envMapIntensity` are identical across all 5 metals by design (`0.55` / `0.55` / `0`) — only the base `color` differs, per the product requirement that Technical mode prioritize inspection clarity over a beauty pass. Presentation mode varies `roughness` slightly per metal (platinum shiniest at `0.18`, rose gold softest at `0.30`) to give each metal a subtly distinct character, consistent with typical jewelry-photography expectations, without claiming spectral accuracy.

## Never a transparent fake metal

Every metal preset uses `opacity: 1`, `transmission: 0` — restating the product requirement directly: metal is never rendered translucent or see-through in either view mode.

## Consistency across a model

Every `production_metal` component (band, prongs, basket_support) receives the identical resolved material for a given metal/view-mode pair — there is no per-component metal variation; `resolveComponentMaterial(false, metal, mode)` returns the same object for all three, confirmed by `materials.test.ts` implicitly (single resolver call site, deterministic by `metal`+`mode` only).

## Fallback behavior

An unrecognized metal key (should never occur given `MetalType`'s closed union, but defensively handled) falls back to `yellow_gold_18k`'s preset rather than throwing or rendering an undefined color — confirmed by `materials.test.ts::'falls back to a known preset for an unrecognized metal key rather than throwing'`.
