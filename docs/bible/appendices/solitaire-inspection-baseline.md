---
id: JM-BIBLE-A99
title: "Appendix: Solitaire Inspection Baseline"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-A92
  - JM-BIBLE-A94
  - JM-BIBLE-A95
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Solitaire Inspection Baseline

Real baseline facts captured by running `inspect_model()` against the default six-prong solitaire and the four-prong variant, as recorded in `specs/geometry-inspection/v2/examples/default-solitaire-inspection.json` and `four-prong-inspection.json`. These are the same values `backend/tests/test_geometry_inspection.py::TestInspectionRegression` checks against, within tolerance — a stable classification baseline, **not a promise that exact volumes never move by floating-point noise**, per the brief's own instruction to avoid storing brittle exact intersection volumes unless tolerances are appropriate.

`kernelVersion: "2.8.0"`. `geometryGeneratorVersion: "0.1.0"`. `inspectionVersion: "1.0.0"`.

## Default solitaire (6 prongs) — per-component facts

| Component | Solids | Volume (mm³) | Bounding box size (X × Y × Z, mm) | Shape valid |
|---|---|---|---|---|
| `band` | 1 | 250.9917 | 21.400 × 2.400 × 21.400 | true |
| `stone_reference` | 1 | 58.2214 | 6.500 × 6.500 × 4.000 | true |
| `prongs` | 6 | 29.6504 | 7.270 × 6.443 × 5.200 | true |
| `basket_support` | 1 | 83.1558 | 7.270 × 7.270 × 3.900 | true |

- Assembly bounding box: 21.400 × 7.270 × 26.300 mm.
- `totalProductionVolumeMm3`: 363.7978 (sum of band+prongs+basket_support raw volumes, pre-fuse).
- `combined_metal` (post-fuse) volume: 341.4433 mm³, 1 solid — lower than the raw sum because fusing removes the real overlap volume shown in the intersection table below.

## Four-prong variant — per-component facts (deltas from default only)

| Component | Solids | Volume (mm³) |
|---|---|---|
| `prongs` | 4 (vs. 6) | 19.7669 (vs. 29.6504) |
| `combined_metal` | 1 | 338.9725 (vs. 341.4433) |

`band`, `stone_reference`, and `basket_support` facts are identical to the default solitaire — prong count does not affect any other component's geometry (see [`052-parametric-dependency-model.md`](../04-jewelry-domain/052-parametric-dependency-model.md)).

## Pairwise intersection/distance baseline — default solitaire (6 prongs)

| Pair | Min. distance (mm) | Status | Intersection volume (mm³) |
|---|---|---|---|
| band ↔ stone_reference | 0.9000 | NO_INTERSECTION (skipped, broad-phase) | 0.0 |
| band ↔ prongs | 0.0 | INTERSECTS | 0.0223 |
| band ↔ basket_support | 0.0 | INTERSECTS | 0.1168 |
| stone_reference ↔ prongs | 0.0 | INTERSECTS | 2.1008 |
| stone_reference ↔ basket_support | 0.0 | INTERSECTS | 3.6190 |
| prongs ↔ basket_support | 0.0 | INTERSECTS | 22.2378 |

## Pairwise intersection baseline — four-prong variant (deltas only)

| Pair | Intersection volume (mm³) |
|---|---|
| stone_reference ↔ prongs | 1.4005 (vs. 2.1008 — fewer prongs, less overlap) |
| prongs ↔ basket_support | 14.8252 (vs. 22.2378) |

All other pairs are identical to the default solitaire — fewer prongs only reduces overlap with components the prongs themselves touch.

## Connectivity baseline (both variants)

- `PRODUCTION` graph (`band`, `prongs`, `basket_support`): 1 connected group, `isFullyConnected: true`, `disconnectedGroupCount: 0`.
- `FULL_ASSEMBLY` graph (adds `stone_reference`): 1 connected group of all 4 — `stone_reference` is not directly connected to `band` (0.9mm apart) but reaches the group through `prongs`/`basket_support`.

## Structural baseline

- `stoneMetalSeparation.fusedIntoProductionMetal`: `false` in both variants — the stone's shape is never an argument to `_fuse_metal()`.
- `prongCount.matches`: `true` in both variants (6/6 and 4/4).
- `booleanOperations`: 4 real operations recorded per inspection — `FUSE(band)`, `CUT(basket_support)`, `FUSE(prongs)`, `FUSE(band, prongs, basket_support) → combined_metal`. None used a fallback in either baseline run.

## Performance baseline (informational only, not a regression gate)

| Phase | Default solitaire (ms) | Four-prong (ms) |
|---|---|---|
| Component inspection | 119.3 | 74.5 |
| Distance inspection | 121.7 | 55.6 |
| Intersection inspection | 274.7 | 229.4 |
| Topology inspection | 51.6 | 23.8 |
| **Total** | **568.9** | **384.5** |

See [`484-inspection-performance-model.md`](../16-geometry-inspection/484-inspection-performance-model.md) — these numbers are real, single-run, machine-dependent measurements; they document real cost, not a committed SLA.

## Cross-references

- `specs/geometry-inspection/v2/examples/default-solitaire-inspection.json`, `four-prong-inspection.json` — the full, real, unabridged reports this table summarizes.
- `specs/geometry-inspection/v2/test-vectors/regression-vectors.json` — the vectors `TestInspectionRegression` asserts against.
- [`geometry-fact-catalog.md`](geometry-fact-catalog.md) (A92) — the 22 `FactType` definitions these values instantiate.
