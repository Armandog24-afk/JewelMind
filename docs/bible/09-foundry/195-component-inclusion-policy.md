---
id: JM-BIBLE-195
title: Component Inclusion Policy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-192
related_documents:
  - JM-BIBLE-196
  - JM-BIBLE-A36
implementation_status: current
professional_validation: not_required
normative: true
---

# Component Inclusion Policy

## The matrix, confirmed by direct code inspection

| Component | STEP | STL | JSON | Technical specification | Preview mesh |
|---|---|---|---|---|---|
| `band` | Included by default | Included by default | n/a (metadata only) | Included by default | Included by default |
| `prongs` | Included by default | Included by default | n/a (metadata only) | Included by default | Included by default |
| `basket_support` | Included by default | Included by default | n/a (metadata only) | Included by default | Included by default |
| `stone_reference` | Excluded by default, optional (`includeStoneReference: true`) | Excluded by default, optional | n/a (present as design metadata: `stone.diameter`/`stone.depth`) | Included by default, as dimensions only, labeled "(reference only, not a gemological reproduction)" | Included by default |

Real exported component sets, confirmed by inspecting `exporters/selection.py` and running a real export during Sprint 7: `STEP_default = STL_default = [band, prongs, basket_support]`; `STEP_with_stone = STL_with_stone = [band, prongs, basket_support, stone_reference]` — see `specs/foundry/v1/test-vectors/component-inclusion-vectors.json`.

## Why STEP and STL currently share identical component sets

Both call the same `select_export_shapes()` (see [`196-production-geometry-selection.md`](196-production-geometry-selection.md)) — a direct consequence of this Sprint's extraction, not a coincidence that could silently drift apart in the future. Before this Sprint, the two exporters independently duplicated the identical `shapes = [model.combined_metal]; if include_stone: shapes.append(...)` logic; a future edit to only one of them could previously have silently created a mismatch. This is now structurally impossible without touching the shared function both call.

## `stone_reference` is never unconditionally prohibited

For every artifact type, `stone_reference` is either optionally includable (STEP/STL), already included as non-geometric metadata (JSON, technical specification), or always visible (preview, since a preview exists to show the whole design, not to imitate a manufacturing file). No artifact type excludes it in a way the caller cannot override or that hides its existence entirely — this is a deliberate consequence of LAW-006 ("never union the stone into the metal body"), not the same thing as "the stone is never mentioned."

## Never inferred from material

Every inclusion/exclusion decision here is driven by explicit component identity (`model.components["stone_reference"]`, `model.combined_metal`) and an explicit `include_stone` boolean, never inferred from a shape's assigned viewer material or color — see [`196-production-geometry-selection.md`](196-production-geometry-selection.md) for why that distinction matters.
