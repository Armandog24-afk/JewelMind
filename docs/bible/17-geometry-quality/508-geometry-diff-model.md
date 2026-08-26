---
id: JM-BIBLE-508
title: Geometry Diff Model
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
  - JM-BIBLE-504
implementation_status: current
professional_validation: not_required
normative: true
---

# Geometry Diff Model

`GeometryDiff` (`backend/jewelmind/geometry_quality/models.py`) is the structured output of `compare_snapshot()`. Its own docstring states plainly: "`severity`/`requiresBaselineReview` are derived, never asserted directly" — see [`504-regression-comparison-model.md`](504-regression-comparison-model.md) for how they're derived.

## `GeometryDiff` fields

| Field | Type | Meaning |
|---|---|---|
| `goldenId` | `str` | Which golden case this diff belongs to. |
| `expectedFingerprint` | `VersionFingerprint` | The accepted baseline's fingerprint. |
| `actualFingerprint` | `VersionFingerprint` | The current run's real, freshly collected fingerprint. |
| `exactChanges` | `list[ExactChange]` | See [`503-quality-signal-model.md`](503-quality-signal-model.md)'s `EXACT_INVARIANT`. |
| `numericChanges` | `list[NumericFactDiff]` | `NUMERIC_REGRESSION`. |
| `relationshipChanges` | `list[RelationshipChange]` | `RELATIONSHIP_REGRESSION`. |
| `topologyChanges` | `list[TopologyChange]` | `TOPOLOGY_REGRESSION`. |
| `artifactChanges` | `list[ArtifactChange]` | `ARTIFACT_REGRESSION`; only populated when `verify_golden(..., check_artifacts=True)`. |
| `severity` | `DiffSeverity` | `NONE \| INFO \| REGRESSION \| VERSION_REVIEW_REQUIRED`. |
| `requiresBaselineReview` | `bool` | `True` for `REGRESSION`/`VERSION_REVIEW_REQUIRED`, `False` otherwise. |

## The 5 change types, field-by-field

| Type | Fields |
|---|---|
| `ExactChange` | `path: str`, `expected: Any`, `actual: Any` |
| `NumericFactDiff` | `path: str`, `expected: float`, `actual: float`, `absoluteDelta: float`, `relativeDelta: float \| None`, `tolerance: float`, `withinTolerance: bool` |
| `RelationshipChange` | `componentA: str`, `componentB: str`, `field: str`, `expected: Any`, `actual: Any` |
| `TopologyChange` | `componentId: str`, `field: str`, `expected: int`, `actual: int` |
| `ArtifactChange` | `artifactType: str`, `description: str` |

`NumericFactDiff.relativeDelta` is `None` exactly when `expected == 0` (division by zero is avoided, not computed as `inf`), per `_numeric_diff()` in `compare.py`. `NumericFactDiff.tolerance` always records `RELATIVE_COMPARISON_TOLERANCE` (`1e-3`) regardless of whether the fact actually passed via the absolute or the relative branch of the OR check — see [`505-comparison-tolerance-policy.md`](505-comparison-tolerance-policy.md) for that logic.

## `human_readable()` — the real output format

`GeometryDiff.human_readable()` (defined directly on the model) is what every CLI subcommand and `QualityResult.message` actually prints. When `severity == "NONE"`:

```python
f"Golden: {self.goldenId}\nStatus: no regression detected."
```

Otherwise, it opens with `f"Golden: {self.goldenId}"` and `f"Severity: {self.severity}"`, then appends one block per change, using these exact f-string templates:

```python
# ExactChange
f"Exact invariant changed: {c.path}\n  Expected: {c.expected}\n  Actual:   {c.actual}"

# NumericFactDiff  (status is "within tolerance" or "REGRESSION")
f"Metric: {n.path}\n"
f"  Expected: {n.expected}\n"
f"  Actual:   {n.actual}\n"
f"  Delta:    {n.absoluteDelta} (relative {n.relativeDelta})\n"
f"  Tolerance: {n.tolerance}\n"
f"  Status:   {status}"

# RelationshipChange
f"Relationship changed: {r.componentA} <-> {r.componentB} ({r.field})\n"
f"  Expected: {r.expected}\n"
f"  Actual:   {r.actual}"

# TopologyChange
f"Topology changed: {t.componentId}.{t.field}\n"
f"  Expected: {t.expected}\n"
f"  Actual:   {t.actual}"

# ArtifactChange
f"Artifact regression: {a.artifactType}\n  {a.description}"
```

It closes with `f"Requires baseline review: {self.requiresBaselineReview}"`, and all lines are joined with `"\n"`.

## Satisfying the brief's diagnostic-quality requirement

The brief's stated bar is: "BAD: `AssertionError`. GOOD: `Golden: SOL-004 / Component: band / Metric: volume / ...`". The real `Metric:` block above satisfies this directly — a failing numeric comparison on, say, `SOL-004-four-prong-flat`'s band volume prints `Golden: SOL-004-four-prong-flat`, `Metric: components.band.volumeMm3`, both the `Expected:`/`Actual:` values, the `Delta:`/`Tolerance:`, and an explicit `Status: REGRESSION` line — never a bare stack trace. This is directly exercised by `TestHumanReadableDiff::test_failing_diff_names_the_metric_and_both_values` (`backend/tests/test_geometry_quality_harness.py`), which asserts the printed text contains `"band"`, `"volumeMm3"`, `"Expected:"`, `"Actual:"`, `"Delta:"`, and `"Tolerance:"` after mutating a copy of the real `SOL-001-default-solitaire` golden's band volume.
