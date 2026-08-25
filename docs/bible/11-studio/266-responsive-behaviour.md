---
id: JM-BIBLE-266
title: Responsive Behaviour
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-265
related_documents:
  - JM-BIBLE-A48
implementation_status: partial
professional_validation: not_required
normative: true
---

# Responsive Behaviour

## The 3 supported tiers, and what was actually verified this Sprint

| Tier | Breakpoint | Verified this Sprint? | Result |
|---|---|---|---|
| Desktop | > 1180px | Yes (primary development target) | Full 3-column workspace, viewport gets the largest area |
| Tablet | 981px–1180px | Partial | Narrower fixed side-panel widths (300px/320px vs 340px/380px), same 3-column structure. Not tested on a physical tablet this Sprint |
| Mobile/narrow | ≤ 980px | Yes, via a live resize test | Single stacked column (`grid-template-columns: 1fr`, `grid-auto-rows: auto`), confirmed via `window.dispatchEvent(new Event('resize'))` + `getComputedStyle()` inspection at both 768px and a ~559px effective width |

## What was actually observed, precisely

At 768px width, `.app-body`'s computed `grid-template-columns` resolved to a single full-width track, confirming the stacked layout activates correctly below the 980px breakpoint. The 3D viewport's `.viewport { min-height: 420px }` floor held even in the cramped mobile layout, confirmed by a direct `getBoundingClientRect()` read returning exactly `420` — this is what prevents the "force the entire desktop CAD-like workspace into tiny columns" failure mode this Sprint explicitly warned against.

## Stacked sections, not tabs, on narrow screens

At ≤980px, the three panels (`panel--left`, `panel--center`, `panel--right`) stack vertically in document order (Design, then Viewport, then Validation/Outputs/etc. tabs) rather than becoming a tab-switched single-panel view — a real, pre-existing behavior this Sprint verified rather than changed. This is a reasonable, honest "usable for inspection and light editing" mobile experience, not a claim of a purpose-built mobile redesign.

## What was NOT verified

No physical tablet or mobile device was used this Sprint — verification was a browser viewport resize plus computed-style inspection, not a real touch-input session. No claim of "perfect mobile support" is made anywhere in this Sprint's documentation, per its own explicit instruction.

## Known limitation carried forward

The 3D viewport's `OrbitControls` already supports touch (drei's default), per [`10-vision/243-accessibility-and-input-model.md`](../10-vision/243-accessibility-and-input-model.md) — this was not independently re-verified on a physical touch device this Sprint either.
