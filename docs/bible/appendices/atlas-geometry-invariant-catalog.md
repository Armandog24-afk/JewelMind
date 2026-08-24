---
id: JM-BIBLE-A23
title: "Appendix: Atlas Geometry Invariant Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-124
  - JM-BIBLE-136
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Atlas Geometry Invariant Catalog

Every fixed geometric constant currently used by the geometry builders, including the constants formally documented for the first time in this Sprint.

| Constant | Value | Role | Previously documented? |
|---|---|---|---|
| `EMBED_MM` | 0.4mm | Cross-component embedding depth to guarantee genuine 3D overlap | Yes — `docs/geometry-conventions.md` |
| `_CROWN_FRACTION` | 0.35 | Stone reference crown height fraction of `stone.depth` | Yes — `docs/known-limitations.md` |
| `_PAVILION_FRACTION` | 0.65 | Stone reference pavilion height fraction | Yes — `docs/known-limitations.md` |
| `_TABLE_TO_GIRDLE_RATIO` | 0.56 | Stone reference table radius as a fraction of girdle radius | Yes — `docs/known-limitations.md` |
| `_CULET_RADIUS_MM` | 0.05mm | Stone reference culet point radius | **No — first documented in this Sprint** ([`07-atlas/124-geometric-primitives.md`](../07-atlas/124-geometric-primitives.md)) |
| `_COMFORT_FLARE_MM` | 0.3mm | Comfort-fit inner-edge flare amount | **No — first documented in this Sprint** ([`07-atlas/126-curve-and-profile-model.md`](../07-atlas/126-curve-and-profile-model.md)) |
| `_FILLET_FRACTION` | 0.15 | Outer-rim fillet radius, fraction of band width/thickness | **No — first documented in this Sprint** ([`07-atlas/135-fillets-rounding-and-fallbacks.md`](../07-atlas/135-fillets-rounding-and-fallbacks.md)) |
| `_FILLET_MAX_MM` | 0.25mm | Outer-rim fillet radius cap | **No — first documented in this Sprint** |
| (inline) fillet-attempt threshold | 0.02mm | Minimum fillet radius worth attempting | **No — first documented in this Sprint** |
| `_MIN_INNER_RADIUS_MM` | 0.2mm | Basket support minimum inner-radius floor | **No — first documented in this Sprint** ([`07-atlas/125-transformations.md`](../07-atlas/125-transformations.md)) |
| `FlatCircleAtRadius.tol` | 1e-3 mm | Edge-selection geometric-comparison tolerance | **No — first documented in this Sprint** ([`07-atlas/136-tolerance-model.md`](../07-atlas/136-tolerance-model.md)) |

**7 previously-undocumented magic numbers were found and formally documented in this Sprint**: `_CULET_RADIUS_MM`, `_COMFORT_FLARE_MM`, `_FILLET_FRACTION`, `_FILLET_MAX_MM`, the inline `0.02` fillet-attempt threshold, `_MIN_INNER_RADIUS_MM`, and `FlatCircleAtRadius.tol`. None was found to be a defect requiring a code fix; all are working, reasonable geometric constants.
