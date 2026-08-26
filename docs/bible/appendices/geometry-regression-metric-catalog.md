---
id: JM-BIBLE-A102
title: "Appendix: Geometry Regression Metric Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-500
related_documents:
  - JM-BIBLE-504
  - JM-BIBLE-505
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Geometry Regression Metric Catalog

Every metric `compare_snapshot()` (`backend/jewelmind/geometry_quality/compare.py`) actually compares, one row per real check.

| Scope | Metric | Comparison kind | Tolerance |
|---|---|---|---|
| Assembly | `componentCount` | Exact | — |
| Assembly | `productionComponentCount` | Exact | — |
| Assembly | `referenceComponentCount` | Exact | — |
| Assembly | `productionConnectivityGroups` | Exact | — |
| Assembly | `productionIsFullyConnected` | Exact | — |
| Assembly | `boundingBox.{xmin,ymin,zmin,xmax,ymax,zmax,sizeX,sizeY,sizeZ,centerX,centerY,centerZ}` | Numeric | `RELATIVE_COMPARISON_TOLERANCE = 1e-3` / `ABSOLUTE_COMPARISON_TOLERANCE_MM = 1e-4` |
| Design consistency | `requestedProngCount` | Exact | — |
| Design consistency | `generatedProngCount` | Exact | — |
| Design consistency | `prongCountMatches` | Exact | — |
| Design consistency | `stoneReferenceIsProductionMetal` | Exact | — |
| Component | `role`, `present`, `fallbackUsed` | Exact | — |
| Component | `solidCount` | Topology | — (integer; a mismatch is `TOPOLOGY_REGRESSION`, not `NUMERIC_REGRESSION`) |
| Component | `topology.{solids,shells,faces,edges,vertices}` | Topology | — |
| Component | `volumeMm3` | Numeric | same as assembly bounding box |
| Component | `boundingBox.*` | Numeric | same as assembly bounding box |
| Relationship (per pair) | `connected` | Relationship | — |
| Relationship (per pair) | `intersectionStatus` | Relationship | — |
| Relationship (per pair) | `minDistanceMm` | Numeric | same as assembly bounding box |
| Component set | missing/unexpected component | Exact | — (always `severity: REGRESSION`) |

A numeric metric is only added to `GeometryDiff.numericChanges` at all when `expected != actual` — a bit-identical rerun (the normal local case, per `TestRepeatability`) produces an empty `numericChanges` list, not a list of zero-delta entries.

## Cross-references

- [`504-regression-comparison-model.md`](../17-geometry-quality/504-regression-comparison-model.md) — the full comparison algorithm.
- [`505-comparison-tolerance-policy.md`](../17-geometry-quality/505-comparison-tolerance-policy.md) — why the two tolerance constants have the values they do.
- [`geometry-quality-signal-catalog.md`](geometry-quality-signal-catalog.md) (A101) — the signal-category grouping of these same metrics.
