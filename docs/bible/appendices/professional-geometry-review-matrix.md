---
id: JM-BIBLE-A88
title: "Appendix: Professional Geometry Review Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-420
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Professional Geometry Review Matrix

The 14 geometry review dimensions from [`420-geometry-validation-process.md`](../15-professional-validation/420-geometry-validation-process.md), crossed with which of the 8 `ReviewerRole` values would typically assess each. "Typically" reflects the professional expertise described in [`professional-reviewer-role-catalog.md`](professional-reviewer-role-catalog.md) (`JM-BIBLE-A81`) — it is not a requirement that every marked role review every marked dimension, and it invents no numeric threshold for any dimension (see [`420-geometry-validation-process.md`](../15-professional-validation/420-geometry-validation-process.md), "No invented numeric thresholds").

Roles: CAD = `JEWELRY_CAD_DESIGNER`, GS = `GOLDSMITH_BENCH_JEWELER`, SS = `STONE_SETTER`, CAST = `CASTING_SPECIALIST`, RESIN = `RESIN_PRINTING_SPECIALIST`, MFG = `JEWELRY_MANUFACTURING_ENGINEER`, GEM = `GEMOLOGIST`, INTEROP = `CAD_INTEROPERABILITY_SPECIALIST`.

| Geometry review dimension | CAD | GS | SS | CAST | RESIN | MFG | GEM | INTEROP |
|---|---|---|---|---|---|---|---|---|
| Overall construction logic | Yes | Yes | — | — | — | Yes | — | — |
| Component placement | Yes | Yes | Yes | — | — | — | — | — |
| Band geometry | Yes | Yes | — | Yes | Yes | — | — | — |
| Basket geometry | Yes | Yes | Yes | Yes | — | — | — | — |
| Prong geometry | Yes | Yes | Yes | Yes | — | — | — | — |
| Component connectivity | Yes | Yes | — | Yes | Yes | Yes | — | — |
| Stone relationship | — | — | Yes | — | — | — | Yes | — |
| Seat/bearing | — | — | Yes | — | — | — | Yes | — |
| Setting accessibility | — | — | Yes | — | — | — | — | — |
| Plausibility for intended workflow | Yes | Yes | — | Yes | Yes | Yes | — | — |
| Model editability | Yes | — | — | — | — | — | — | Yes |
| Unexpected surfaces or bodies | Yes | — | — | Yes | Yes | — | — | Yes |
| Overbuilt or underbuilt areas | Yes | Yes | — | Yes | Yes | Yes | — | — |
| CAD cleanliness | Yes | — | — | — | — | — | — | Yes |

## Notes on this matrix's scope

- This matrix is descriptive, drawn from [`420-geometry-validation-process.md`](../15-professional-validation/420-geometry-validation-process.md)'s own dimension list and the role descriptions in [`413-reviewer-role-model.md`](../15-professional-validation/413-reviewer-role-model.md) — it is not itself a new checklist, and it does not replace the 4 role-specific checklists in [`professional-review-checklist-catalog.md`](professional-review-checklist-catalog.md) (`JM-BIBLE-A83`).
- `RESIN_PRINTING_SPECIALIST` and `CASTING_SPECIALIST` are marked identically on several rows because both process-specific roles typically assess the same physical-geometry dimensions (band thickness, connectivity, overbuilt/underbuilt regions) through the lens of their own manufacturing method — a `ReviewObservation`'s `scope.manufacturingMethod` is what actually distinguishes their findings, not the dimension list itself.
- `JEWELRY_MANUFACTURING_ENGINEER` is marked only on dimensions that are genuinely cross-process (construction logic, connectivity, workflow plausibility, overbuilt/underbuilt) — per [`413-reviewer-role-model.md`](../15-professional-validation/413-reviewer-role-model.md), this role is relevant to feasibility questions not specific to one manufacturing method.
- No row in this matrix implies any dimension has actually been reviewed by any role — the active registry contains zero `ValidationRecord`s.

## Cross-references

- [`420-geometry-validation-process.md`](../15-professional-validation/420-geometry-validation-process.md) — the full dimension list, process flow diagram, and the real 4-component list (`band`, `stone_reference`, `prongs`, `basket_support`) a reviewer actually sees.
- [`atlas-component-catalog.md`](atlas-component-catalog.md) — the underlying real component/volume data these dimensions are evaluated against.
- [`422-setting-validation-process.md`](../15-professional-validation/422-setting-validation-process.md) — the current, simplified state of basket/prong/seat geometry these dimensions point to.
