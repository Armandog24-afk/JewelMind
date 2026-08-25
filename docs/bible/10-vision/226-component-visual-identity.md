---
id: JM-BIBLE-226
title: Component Visual Identity
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-223
related_documents:
  - JM-BIBLE-236
implementation_status: current
professional_validation: not_required
normative: true
---

# Component Visual Identity

## Identity source

Every mesh in the Vision scene is keyed by the real component name (`band`, `prongs`, `basket_support`, `stone_reference`) — the same key used by `model.components` on the backend, `previewComponents` in the API response, and `componentVisibility` in `useVisionStore`. Render order (`Object.entries(geometries).map(...)`) never determines identity; it is only iteration order over an already-keyed structure.

## Stone/metal classification

`ModelViewport.tsx` resolves whether a mesh is the stone via `entry?.geometryRole ?? (name === 'stone_reference' ? 'stone_reference' : 'production_metal')` — the explicit `geometryRole` field (see [`223-atlas-to-vision-contract.md`](223-atlas-to-vision-contract.md)) is checked first; the name-based fallback exists only for resilience against a manifest that predates this Sprint's addition, never as the primary mechanism. This directly satisfies VISION-GOV-006 and VISION-GOV-011.

## Selection identity

`useVisionStore.selectedComponent` also stores the real component name, not an index or a mesh reference — clicking a name in [`236-component-visibility-model.md`](236-component-visibility-model.md)'s panel sets this value, and the corresponding `ComponentMesh` receives a highlight (`emissive: '#ffcc66'`) by matching that same name during the render map, never by object identity or array position.

## What happens to an unrecognized component name

If a future Atlas component introduces a fifth name, `metalComponentNames` (derived from `geometryRole !== 'stone_reference'`... actually from `geometryRole === 'production_metal'`, see code) would only include it if its `geometryRole` is explicitly `production_metal`; an unset `geometryRole` defaults to `production_metal` in the frontend's own fallback (`entry.geometryRole ?? 'production_metal'`), meaning a genuinely new non-metal, non-stone component would currently be visually treated as metal until this document and the backend's `_GEOMETRY_ROLE` mapping are both updated — a real, honest limitation, not a silent failure (the component would still render and be toggleable, just with an incorrect default material).
