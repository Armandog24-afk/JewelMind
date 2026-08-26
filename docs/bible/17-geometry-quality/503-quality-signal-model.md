---
id: JM-BIBLE-503
title: Quality Signal Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-500
related_documents:
  - JM-BIBLE-504
  - JM-BIBLE-508
  - JM-BIBLE-460
implementation_status: current
professional_validation: not_required
normative: true
---

# Quality Signal Model

`QualitySignalType` (`backend/jewelmind/geometry_quality/models.py`) names the seven categories of geometric fact this Sprint can compare. Six are implemented in `compare_snapshot()`/`step_roundtrip_check()`/`stl_structure_check()`; the seventh, `PROFESSIONAL_QUALITY`, is explicitly out of scope for this subsystem.

## The 6 implemented signal types

### `EXACT_INVARIANT`

A fact that must match exactly — any difference is a regression, never a tolerance question. Produces an `ExactChange` in `GeometryDiff.exactChanges`. Real examples from `compare.py`:

- `assembly.componentCount`, `assembly.productionComponentCount`, `assembly.referenceComponentCount`, `assembly.productionConnectivityGroups`, `assembly.productionIsFullyConnected`.
- `designConsistency.stoneReferenceIsProductionMetal` (QUALITY-GOV-013, restating LAW-006/INSPECT-GOV-008 at this layer), `designConsistency.requestedProngCount`, `designConsistency.generatedProngCount`, `designConsistency.prongCountMatches` (QUALITY-GOV-014).
- Per-component `role`, `present`, `fallbackUsed`.
- `components.missing` / `components.unexpected` when the set of component IDs itself differs (QUALITY-GOV-011).

### `NUMERIC_REGRESSION`

A floating-point fact compared with tolerance. Produces a `NumericFactDiff` in `GeometryDiff.numericChanges`. Real examples: `assembly.boundingBox.*`, per-component `volumeMm3`, per-component `boundingBox.*`, and relationship `minDistanceMm`. See [`505-comparison-tolerance-policy.md`](505-comparison-tolerance-policy.md) for the tolerance itself.

### `RELATIONSHIP_REGRESSION`

A pairwise fact between two components. Produces a `RelationshipChange` in `GeometryDiff.relationshipChanges`. Real examples: a flipped `connected` boolean (QUALITY-GOV-012) or a changed `intersectionStatus` categorical value (`INTERSECTS`/`TOUCHES`/`NO_INTERSECTION`/`UNKNOWN`) between the same component pair.

### `TOPOLOGY_REGRESSION`

A structural count on one component. Produces a `TopologyChange` in `GeometryDiff.topologyChanges`. Real examples: per-component `solidCount`, and any key inside `ComponentSnapshot.topology` (the `dict[str, int]` populated from the component's inspection topology facts, e.g. face/edge counts) that differs between expected and actual. Topology changes are the one category whose severity depends on version context — see [`504-regression-comparison-model.md`](504-regression-comparison-model.md) and QUALITY-GOV-010.

### `ARTIFACT_REGRESSION`

An export-format-level fact, only checked when `verify_golden(..., check_artifacts=True)`. Produces an `ArtifactChange` in `GeometryDiff.artifactChanges`. Real examples from `artifact_regression.py`: STEP roundtrip solid-count/volume/bounding-box mismatches, an empty STEP/STL export, a zero-triangle STL, or an STL mesh bounding box inconsistent with the source B-Rep. See [`509-artifact-regression-model.md`](509-artifact-regression-model.md).

### `PERFORMANCE_OBSERVATION`

Not exercised by any comparison logic read for this document — `compare_snapshot()` and `GeometrySnapshot` deliberately exclude performance/timing fields by construction (see `snapshot.py`'s docstring and `TestVolatileFieldNormalization` in `backend/tests/test_geometry_quality_snapshot.py`, which asserts `"performance"` never appears in a dumped snapshot). The enum member exists as a named placeholder for a future signal category; no current code path produces one.

## `PROFESSIONAL_QUALITY` — never automatically inferred

`QualitySignalType` does **not** include `PROFESSIONAL_QUALITY`, and no combination of `EXACT_INVARIANT`/`NUMERIC_REGRESSION`/`RELATIONSHIP_REGRESSION`/`TOPOLOGY_REGRESSION`/`ARTIFACT_REGRESSION` signals may be interpreted as one. A `PASS` `QualityResult` means "this geometry matches its last accepted software baseline" — it says nothing about whether that baseline itself was ever professionally reviewed. Determining that requires the real [`15-professional-validation/`](../15-professional-validation/README.md) framework: a named `Reviewer`, real `ValidationEvidence`, and a real `ValidationRecord` in the active registry (PROVAL-GOV-006/007). See [`514-professional-validation-boundary.md`](514-professional-validation-boundary.md) for the full boundary statement.
