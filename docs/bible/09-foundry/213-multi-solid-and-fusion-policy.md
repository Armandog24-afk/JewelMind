---
id: JM-BIBLE-213
title: Multi-Solid and Fusion Policy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-196
related_documents:
  - JM-BIBLE-143
implementation_status: current
professional_validation: not_required
normative: true
---

# Multi-Solid and Fusion Policy

## Two independent multi-solid concerns

1. **Metal fusion fallback** (Atlas's concern, restated here for export honesty): if `_fuse_metal(band, prongs, basket)` cannot produce a single fused solid, it falls back to a multi-solid compound — a real, documented CadQuery/OpenCascade behaviour, never a fake or partial shape. STEP export accepts a `TopoDS_Compound` directly (`exportStep()` never requires exactly one solid); STL export tessellates every solid in the compound. Confirmed by the default solitaire's real STEP export today producing exactly 1 solid — the fuse fallback path exists but is not the currently-exercised path for the default definition.
2. **Export-time compounding for the stone reference**: when `include_stone=True`, `select_export_shapes()` wraps `combined_metal` and `stone_reference` in a *new* `cq.Compound.makeCompound([...])`, constructed only for the duration of that export call — never stored back onto `GeneratedModel`, never fused. See [`196-production-geometry-selection.md`](196-production-geometry-selection.md).

## Solid-count discipline

`backend/tests/test_foundry_registry.py::test_component_inclusion_vectors_match_live_default_export` asserts that including the stone adds exactly one solid to the exported shape relative to the default (stone-excluded) export — never zero (which would mean the stone was silently dropped) and never merged into an existing solid's count (which would mean it was accidentally fused, violating LAW-006).

## Why this policy belongs to Foundry, not Atlas

Atlas decides whether the metal fuse succeeds or falls back (a construction decision). Foundry decides which already-built shapes to present together for one specific export request (a selection decision) — restating the same Atlas/Foundry boundary as [`196-production-geometry-selection.md`](196-production-geometry-selection.md), applied here specifically to the multi-solid/compound question rather than the metal/stone question.

## Real measured state

The default solitaire's `combined_metal` is currently 1 solid (the fuse succeeds); including the stone produces a 2-solid compound. No current test definition exercises the multi-solid fuse-fallback path for `combined_metal` itself — this remains a documented, real code path, not yet observed on real data by this Sprint's own runs.
