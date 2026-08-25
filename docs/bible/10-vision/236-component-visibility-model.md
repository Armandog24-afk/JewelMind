---
id: JM-BIBLE-236
title: Component Visibility Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-226
related_documents:
  - JM-BIBLE-195
implementation_status: current
professional_validation: not_required
normative: true
---

# Component Visibility Model

## State ownership

`componentVisibility: Record<string, boolean>` lives entirely in `useVisionStore` — a Vision-only concern, per VISION-GOV-011/014. Toggling a component's visibility never touches `useProjectStore`, never changes `definitionHash`, and has no effect on `includeStoneReference` or any other export option; restating [`09-foundry/195-component-inclusion-policy.md`](../09-foundry/195-component-inclusion-policy.md)'s boundary — Foundry's export inclusion and Vision's on-screen visibility are two entirely independent booleans that happen to often agree by user choice, never by code coupling.

## The 4 current toggles, plus 2 quick actions

| Control | Effect |
|---|---|
| Per-component checkbox (band, prongs, basket support, stone reference) | `toggleComponentVisible(name)` |
| "Show all" | `showAllComponents(names)` — sets every listed component to visible |
| "Metal only" | `showOnlyComponents(names, metalNames)` — visible set to exactly the `production_metal`-role components, hiding the stone |

"Metal only" determines which names count as metal from the live `geometryRole` data (see [`223-atlas-to-vision-contract.md`](223-atlas-to-vision-contract.md)), not a hardcoded `'stone_reference'` string check inside the store — `useVisionStore.showOnlyComponents()` itself is generic and takes the visible set as an argument, so a future fifth component with a different role would be classified correctly by the caller without touching the store.

## Default state

Every component defaults to visible (`isComponentVisible()` returns `true` for any name absent from the map) — a component only becomes hidden through an explicit user action, confirmed by `useVisionStore.test.ts::'defaults every component to visible'`.

## Real tests

`frontend/src/store/useVisionStore.test.ts` (6 tests) covers toggling a single component without affecting others, "show all," "metal only," and confirms visibility changes never touch `useProjectStore`'s state.
