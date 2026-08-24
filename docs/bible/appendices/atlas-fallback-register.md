---
id: JM-BIBLE-A25
title: "Appendix: Atlas Fallback Register"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-135
related_documents:
  - JM-BIBLE-134
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Atlas Fallback Register

**These are the only two fallback paths that exist anywhere in the current geometry codebase.**

## `ATLAS-FALLBACK-001` — Band outer-rim fillet

| Field | Value |
|---|---|
| Operation | `.fillet(fillet_radius)` on the band's outer-rim edges |
| Trigger | The fillet call raises an exception, or succeeds but yields zero solids |
| Primary behavior | A band with a rounded outer rim (radius up to 0.25mm) |
| Fallback behavior | The pre-fillet, sharp-edged solid |
| Affected component | `band` |
| User-visible warning | `"Outer rim fillet could not be applied ({exc}); falling back to sharp edges."` |
| Regression tests | **None** — no test forces this fallback to trigger; it is verified only by code review |
| Risk | Low — purely cosmetic difference; band dimensions (inner/outer radius, width) are unaffected either way |

## `ATLAS-FALLBACK-002` — Combined-metal boolean fuse

| Field | Value |
|---|---|
| Operation | `band.fuse(basket).fuse(prongs)` |
| Trigger | The fuse raises an exception, or succeeds but `fused.Solids()` is empty |
| Primary behavior | A single fused solid (`combined_metal.Solids()` has length 1) |
| Fallback behavior | `cq.Compound.makeCompound([band, basket, prongs])` — all three original solids, unfused |
| Affected component | `combined_metal` (assembly-level, not a single named component) |
| User-visible warning | `"Combined metal union failed ({exc}); exporting band, prongs, and basket as a multi-solid compound instead of a single fused solid."` |
| Regression tests | **None** — no test forces this fallback to trigger; it is verified only by code review |
| Risk | Low for correctness (no component is dropped — LAW-005), but STEP/STL consumers receive a 3-solid file instead of 1, which some downstream CAD/manufacturing tools may treat differently |

## Not hidden

Both fallbacks are stated plainly in `docs/known-limitations.md`, `docs/geometry-conventions.md`, and now formally in [`07-atlas/135-fillets-rounding-and-fallbacks.md`](../07-atlas/135-fillets-rounding-and-fallbacks.md) / [`134-boolean-operation-strategy.md`](../07-atlas/134-boolean-operation-strategy.md) — neither is a newly-discovered secret; this Sprint's contribution is formalizing them into one comparable register with the three previously-undocumented magic numbers involved in the fillet fallback.
