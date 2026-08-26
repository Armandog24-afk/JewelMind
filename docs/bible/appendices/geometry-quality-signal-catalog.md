---
id: JM-BIBLE-A101
title: "Appendix: Geometry Quality Signal Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-500
related_documents:
  - JM-BIBLE-503
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Geometry Quality Signal Catalog

The 6 real `QualitySignalType` categories (`backend/jewelmind/geometry_quality/models.py`), plus `PROFESSIONAL_QUALITY`, which is deliberately never automatically inferred.

| Signal | Real example fields | Where in `compare_snapshot()` |
|---|---|---|
| `EXACT_INVARIANT` | `assembly.componentCount`, `assembly.productionComponentCount`, `assembly.referenceComponentCount`, `assembly.productionConnectivityGroups`, `assembly.productionIsFullyConnected`, `designConsistency.requestedProngCount`/`generatedProngCount`/`prongCountMatches`, `designConsistency.stoneReferenceIsProductionMetal`, `components.<id>.role`/`present`/`fallbackUsed`, presence/absence of a component | `exactChanges` list |
| `NUMERIC_REGRESSION` | `components.<id>.volumeMm3`, `components.<id>.boundingBox.*`, `assembly.boundingBox.*`, `relationships.<pair>.minDistanceMm` | `numericChanges` list, each a `NumericFactDiff` (expected/actual/absoluteDelta/relativeDelta/tolerance/withinTolerance) |
| `RELATIONSHIP_REGRESSION` | `relationships.<pair>.connected`, `relationships.<pair>.intersectionStatus` | `relationshipChanges` list |
| `TOPOLOGY_REGRESSION` | `components.<id>.solidCount`, `components.<id>.topology.{solids,shells,faces,edges,vertices}` | `topologyChanges` list |
| `ARTIFACT_REGRESSION` | STEP roundtrip (solid count/volume/bounding box after re-import), STL structural checks (non-empty, triangle count, approximate bounding box) | `artifactChanges` list — only populated when `verify_golden(..., check_artifacts=True)` |
| `PERFORMANCE_OBSERVATION` | Generation/inspection/export durations | Not currently collected by the Golden harness itself (see [`515-performance-baseline-model.md`](../17-geometry-quality/515-performance-baseline-model.md)); never a pass/fail signal |
| `PROFESSIONAL_QUALITY` | — | **Never automatically inferred.** No code path in `geometry_quality/` ever sets a professional-validation field. See [`514-professional-validation-boundary.md`](../17-geometry-quality/514-professional-validation-boundary.md). |

## Why topology gets special severity treatment

Unlike the other 4 pass/fail-capable categories, a `TOPOLOGY_REGRESSION` alone does not unconditionally mean `REGRESSION`. `compare_snapshot()` checks whether `kernelVersion`/`ocpVersion`/`atlasGeneratorVersion` differ between the expected and actual `VersionFingerprint`; if they do, the same topology change is classified `VERSION_REVIEW_REQUIRED` instead (QUALITY-GOV-010) — both statuses still require a human to look, neither is silently accepted. See [`version-mismatch-vectors.json`](../../../specs/geometry-quality/v1/test-vectors/version-mismatch-vectors.json) for the real generated proof.

## Cross-references

- [`503-quality-signal-model.md`](../17-geometry-quality/503-quality-signal-model.md) — the full narrative.
- [`geometry-regression-metric-catalog.md`](geometry-regression-metric-catalog.md) (A102) — the concrete per-metric tolerance table.
