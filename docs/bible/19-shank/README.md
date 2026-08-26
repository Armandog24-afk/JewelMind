---
id: JM-BIBLE-SHANK-README
title: Band & Shank System v1 — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-040
  - JM-BIBLE-090
  - JM-BIBLE-120
  - JM-BIBLE-RING-README
related_documents:
  - JM-BIBLE-README
  - JM-BIBLE-526
implementation_status: current
professional_validation: not_required
normative: false
---

# Band & Shank System v1 — Index

This is **Sprint 17** of the Technical Bible: **Band & Shank System v1** — the first REAL GEOMETRY milestone since Sprint 5's Atlas foundation. The pre-Sprint-17 ring band was a single-file, uniform-only construction (`geometry/components/band.py`). This Sprint replaces it with a reusable, parametric **Shank** subsystem — a strong geometric foundation for future ring architectures, not a library of decorative band styles.

**Read this README, then [`540-shank-governance.md`](540-shank-governance.md), before changing anything in `backend/jewelmind/geometry/shank/`, `backend/jewelmind/geometry/connection.py`, or `domain/schema.py::BandSpec`/`BandTaperSpec`.**

## The fundamental rule

> SHANK is an internal technical term for ring-specific geometry, layered strictly beneath Atlas. "Band" stays the user-facing and JDL name. Reusable primitives (profile/interpolation/curve-sampling/sweep utilities) may live in generic Atlas infrastructure; generic Atlas infrastructure must never depend on Ring semantics.

```
Atlas (geometry/, Sprint 5 — generic, Ring-agnostic)
  → geometry/connection.py       (ShankConnectionInterface — Atlas-layer, not Ring-layer)
  → geometry/shank/               (SHANK subsystem — this Sprint, ring-specific but lives in Atlas)
      profile.py    (flat / comfort_fit cross-sections)
      taper.py      (deterministic width/thickness interpolation around u ∈ [0,1))
      builder.py    (dispatch: uniform → revolve, tapered → loft)
      capability.py (CURRENT vs PLANNED capability registry)
  → geometry/components/band.py  (thin re-export: build_ring_band = build_shank)
Ring (ring/, Sprint 16)
  → ring/models.py::ShankDefinition (data mapping only — profile/widthMm/thicknessMm/widthTaper/thicknessTaper, 1:1 from JDL band.*)
```

## What changed vs. what didn't

**Changed (real geometry):** `domain/schema.py::BandSpec` gained `widthTaper`/`thicknessTaper` (both `BandTaperSpec`, default `mode: "NONE"`) — an additive, backward-compatible MINOR JDL change. A new `geometry/shank/` package builds real, deterministic non-uniform geometry: `mode: "TOWARD_BOTTOM"` linearly tapers width and/or thickness from the full base dimension at the head (`u=0`) to `bottomRatio * base` at the bottom (`u=0.5`), symmetric in both directions automatically. `geometry/connection.py::ShankConnectionInterface` now names the Shank → RingHead handoff explicitly (`topZMm`/`embedMm`/`headCenterRadiusMm`), replacing two separately-imported constants in `prongs.py`/`basket.py`.

**Unchanged (by design, verified by the Golden Suite):** Every uniform-shank configuration (no taper requested) uses the byte-identical pre-Sprint-17 `revolve()` construction, including the outer-rim fillet — zero Golden regression for all 9 existing cases. `band.profile`, `band.width`, `band.thickness` are unchanged. The `band` component's name, its exclusion from default exports' stone reference, and Ring Architecture v2 (Sprint 16) are unchanged.

## Reading order

1. [`540-shank-governance.md`](540-shank-governance.md) — the 15 SHANK-GOV-* governance rules.
2. [`541-shank-architecture-overview.md`](541-shank-architecture-overview.md), [`542-shank-domain-model.md`](542-shank-domain-model.md), [`543-shank-coordinate-model.md`](543-shank-coordinate-model.md).
3. Path and profile: [`544-shank-path-contract.md`](544-shank-path-contract.md), [`545-section-profile-contract.md`](545-section-profile-contract.md).
4. Variation model: [`546-width-function-model.md`](546-width-function-model.md), [`547-thickness-function-model.md`](547-thickness-function-model.md), [`548-taper-model.md`](548-taper-model.md), [`549-shoulder-transition-model.md`](549-shoulder-transition-model.md).
5. Integration: [`550-head-connection-interface.md`](550-head-connection-interface.md).
6. Generation: [`551-shank-generation-pipeline.md`](551-shank-generation-pipeline.md), [`552-shank-continuity-model.md`](552-shank-continuity-model.md).
7. Cross-system boundaries: [`553-shank-inspection-contract.md`](553-shank-inspection-contract.md), [`554-shank-forge-boundary.md`](554-shank-forge-boundary.md), [`555-shank-golden-strategy.md`](555-shank-golden-strategy.md).
8. Migration and capability: [`556-current-band-migration.md`](556-current-band-migration.md), [`557-shank-capability-model.md`](557-shank-capability-model.md).
9. [`558-current-code-mapping-and-gaps.md`](558-current-code-mapping-and-gaps.md), [`559-open-shank-questions.md`](559-open-shank-questions.md).

## Appendices

[`shank-profile-catalog.md`](../appendices/shank-profile-catalog.md), [`shank-capability-catalog.md`](../appendices/shank-capability-catalog.md), [`shank-inspection-fact-catalog.md`](../appendices/shank-inspection-fact-catalog.md), [`shank-test-matrix.md`](../appendices/shank-test-matrix.md).

## Machine-readable specification

[`specs/shank/v1/`](../../../specs/shank/v1/README.md) — 6 schemas, a real `capability-registry.json` generated from `geometry/shank/capability.py`, 5 examples, 6 test-vector files, all produced by actually running the real code.

## The single most important finding of this Sprint

**Loft, not sweep, and anchored at the head, not distributed evenly.** A real sweep-along-a-varying-profile experiment was tried first and abandoned — see [`551-shank-generation-pipeline.md`](551-shank-generation-pipeline.md) for why. The chosen design — a 48-section loft, with taper always anchored to the FULL base dimension exactly at the head (`u=0`) — is what guarantees the `ShankConnectionInterface` (and therefore prong/basket placement) never needs to change for any taper configuration, without writing a single special case into `prongs.py`/`basket.py` for tapered shanks.

## What was investigated, not invented

`SECTION_COUNT = 48` was chosen from a real measured volume-convergence table across 16/24/36/48/72 sections (see the validation report), not guessed. A real circular-import bug was found and fixed during this Sprint's own implementation — an earlier version of `geometry/connection.py` was placed inside `jewelmind/ring/`, which is a genuine Atlas/Ring layering violation, not just an import-ordering accident; it was moved to `jewelmind/geometry/connection.py` and verified from multiple real import orders. The `definitionHash` drift caused by the additive `BandSpec` field addition was investigated, confirmed to never affect Golden regression detection (`compare_snapshot()` never reads `definitionHash`), and documented explicitly rather than silently absorbed.

## Validation of this sprint

See [`SPRINT-17-VALIDATION-REPORT.md`](SPRINT-17-VALIDATION-REPORT.md) for the checks run against this section and the findings from that pass.
