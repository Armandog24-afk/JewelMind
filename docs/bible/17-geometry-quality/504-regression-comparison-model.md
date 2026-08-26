---
id: JM-BIBLE-504
title: Regression Comparison Model
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
  - JM-BIBLE-503
  - JM-BIBLE-508
  - JM-BIBLE-505
implementation_status: current
professional_validation: not_required
normative: true
---

# Regression Comparison Model

`compare_snapshot()` (`backend/jewelmind/geometry_quality/compare.py`) walks two `GeometrySnapshot`s field-by-field and returns one `GeometryDiff`. `verify_golden()` (`backend/jewelmind/geometry_quality/harness.py`) then maps that diff's `severity` to a `QualityResultStatus` for the caller.

## `compare_snapshot()`'s real algorithm, in order

1. **Assembly-level exact invariants** — `componentCount`, `productionComponentCount`, `referenceComponentCount`, `productionConnectivityGroups`, `productionIsFullyConnected` are compared with `!=`; any mismatch appends an `ExactChange`.
2. **Assembly bounding box** — every key in `assembly.boundingBox` present on both sides is compared numerically via `_numeric_diff()` (tolerance-based; see [`505-comparison-tolerance-policy.md`](505-comparison-tolerance-policy.md)).
3. **Design-consistency exact invariants** — `requestedProngCount`, `generatedProngCount`, `prongCountMatches`, `stoneReferenceIsProductionMetal` (QUALITY-GOV-013/014).
4. **Component set membership** — components present in `expected` but missing from `actual` produce one `ExactChange` at `components.missing`; components present only in `actual` produce one at `components.unexpected` (QUALITY-GOV-011).
5. **Per-component facts**, for every component ID present on both sides: `role`/`present`/`fallbackUsed` as exact invariants; `solidCount` as a `TopologyChange` when it differs; every key in `topology` present on both sides as a `TopologyChange` when it differs; `volumeMm3` and every `boundingBox` key as `NumericFactDiff`s.
6. **Relationships**, for every `(componentA, componentB)` pair present in both snapshots: `connected` and `intersectionStatus` as `RelationshipChange`s when they differ; `minDistanceMm` as a `NumericFactDiff`.
7. **Severity derivation** (see below).

Artifact checks (`step_roundtrip_check()`/`stl_structure_check()`) are **not** part of `compare_snapshot()` itself — they only run when `verify_golden(..., check_artifacts=True)` calls them separately and appends their `ArtifactChange`s onto the already-computed `diff.artifactChanges` afterward. See [`509-artifact-regression-model.md`](509-artifact-regression-model.md).

## `DiffSeverity` derivation (the real logic, in order)

```python
regression_numeric = [n for n in numeric_changes if not n.withinTolerance]
kernel_differs = _kernel_related_fields_differ(expected_fingerprint, actual_fingerprint)

if exact_changes or relationship_changes or regression_numeric:
    severity = "REGRESSION"
elif topology_changes:
    severity = "VERSION_REVIEW_REQUIRED" if kernel_differs else "REGRESSION"
elif numeric_changes:
    severity = "INFO"
else:
    severity = "NONE"
```

In plain terms: **any** exact-invariant change, **any** relationship change, or **any** numeric change beyond tolerance is an unconditional `REGRESSION` — checked first, regardless of whether topology also changed. Only when none of those three fired, but a topology count did change, does the kernel/OCP/Atlas-generator-version fingerprint comparison get consulted (QUALITY-GOV-010): matching versions still means `REGRESSION` (a topology change with no version excuse is a real regression), differing versions downgrades it to `VERSION_REVIEW_REQUIRED`. If nothing above fired but at least one numeric fact changed *within* tolerance, severity is `INFO` — informational, not a regression. `requiresBaselineReview` is `True` for `REGRESSION` and `VERSION_REVIEW_REQUIRED`, `False` for `INFO`/`NONE`.

## `verify_golden()`'s `QualityResultStatus` mapping

`harness.py::verify_golden()` — after optionally folding artifact changes into the diff (see below) — maps `diff.severity` to a result status:

| `diff.severity` | `QualityResultStatus` |
|---|---|
| `"REGRESSION"` | `REGRESSION_DETECTED` |
| `"VERSION_REVIEW_REQUIRED"` | `VERSION_REVIEW_REQUIRED` |
| anything else, when `golden.knownLimitations` is non-empty | `PASS_WITH_KNOWN_LIMITATIONS` |
| anything else | `PASS` |

Two additional statuses are produced entirely outside `compare_snapshot()`: `BASELINE_MISSING` when `load_golden()` raises `FileNotFoundError` (no accepted `snapshot.json` for that `goldenId` yet), and `ERROR` when `generate_snapshot()` itself raises (e.g. a validation failure) — `verify_golden()` catches that broadly and reports it as `ERROR` rather than letting the harness crash, "report, never crash the harness" per the code's own comment.

## How artifact checks fold into severity

When `check_artifacts=True`, `verify_golden()` runs `step_roundtrip_check()`/`stl_structure_check()` and appends their results to `diff.artifactChanges`. It then applies: `if diff.artifactChanges and diff.severity in ("NONE", "INFO"): diff.severity = "REGRESSION"`. A real artifact regression always escalates `diff.severity` to at least `REGRESSION` — it is never masked by a prior `INFO`-level (within-tolerance) numeric diff. An earlier draft of this rule only escalated from `NONE`, which would have let a real artifact regression hide behind an unrelated `INFO`-level numeric drift; this was caught and fixed before Sprint 15 shipped, and `TestArtifactSeverityEscalation::test_artifact_regression_escalates_even_when_geometric_diff_is_info` (`backend/tests/test_geometry_quality_harness.py`) is the real regression test proving it.

## Cross-reference

`compare_snapshot()` never imports `jewelmind.validation` or references a Forge rule ID — a `REGRESSION_DETECTED` result is a claim about geometric equivalence to a prior software baseline, never a jewelry-domain judgment. See [`460-inspection-governance.md`](../16-geometry-inspection/460-inspection-governance.md)'s INSPECT-GOV-002 for the analogous rule one layer down, and [`514-professional-validation-boundary.md`](514-professional-validation-boundary.md) for the professional-validation boundary this document does not cross.
