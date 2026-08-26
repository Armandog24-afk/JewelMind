---
id: JM-BIBLE-472
title: Component Distance Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-465
  - JM-BIBLE-470
  - JM-BIBLE-471
implementation_status: current
professional_validation: not_required
normative: true
---

# Component Distance Model

## The real algorithm

`distance.py::inspect_distance(name_a, shape_a, name_b, shape_b) -> DistanceResult` calls `shape_a.distance(shape_b)` inside a `try`/`except Exception`. This is CadQuery's wrapper around OCP's `BRepExtrema_DistShapeShape`, which this Sprint's investigation confirmed is multi-threaded (`SetMultiThread(True)` in the underlying implementation, per the module's own docstring, itself grounded in reading the real `cadquery.Shape.distance()` source — reproducible via `python -c "import inspect, cadquery as cq; print(inspect.getsource(cq.Shape.distance))"` against the installed `cadquery==2.8.0`). On success, the result is `status="PASS"`, `minDistanceMm=value`, `tolerance=CONTACT_TOLERANCE_MM`. On any kernel exception, the result is `status="ERROR"`, `minDistanceMm=None` — never a guessed value, per INSPECT-GOV-006.

## Real measured pairwise distances, default solitaire

`band` ↔ `stone_reference`: **0.9mm** — the one genuinely separated pair. All other 5 pairs (`band`↔`basket_support`, `basket_support`↔`prongs`, `prongs`↔`stone_reference`, `basket_support`↔`stone_reference`, `band`↔`prongs`): **0.0mm** — touching or already overlapping.

## Never an "acceptable" jewelry distance

`distance.py`'s own module docstring states this directly: this module "never defines an 'acceptable' jewelry distance — only measures a real one." `inspect_distance()` has no concept of a minimum clearance, a manufacturing gap requirement, or any jewelry-domain threshold — its only comparison point is `CONTACT_TOLERANCE_MM`, a pure kernel numerical-precision constant (see [`470-component-connectivity-model.md`](470-component-connectivity-model.md)), used solely to classify "touching" versus "separated" for connectivity purposes, never to judge whether a real gap is professionally appropriate.

## Real measured performance

Distance is markedly cheaper than intersection: roughly tens of milliseconds total for all 6 pairs of the default solitaire, versus roughly 200 milliseconds to 1.8 seconds total for the same 6 pairs' intersection checks (dominated by the `prongs` compound's 6 independent sub-solids, each of which the boolean-common operation must consider). This asymmetry is exactly why `assembly.py::inspect_assembly()` always computes every pairwise distance first, unconditionally, and only then decides — via `should_skip_intersection()` — which of the more expensive intersection checks can be skipped. See [`484-inspection-performance-model.md`](484-inspection-performance-model.md) for the full timing model.

## Kernel-failure isolation

`inspect_distance()`'s own `try`/`except` means a distance-measurement failure for one pair can never crash the rest of `pairwise_distances()`'s loop — each pair is independent. `backend/tests/test_geometry_inspection.py::TestInspectionErrorRecovery::test_distance_with_a_kernel_failure_returns_error_not_a_crash` verifies this directly, using a synthetic shape object whose `distance()` method raises `RuntimeError`, confirming the result is `status="ERROR"`, `minDistanceMm=None` rather than an unhandled exception propagating out of `inspect_model()`.

## Cross-references

[`470-component-connectivity-model.md`](470-component-connectivity-model.md) for how `DistanceResult`s become connectivity edges; [`471-component-intersection-model.md`](471-component-intersection-model.md) for how a distance result gates the more expensive intersection check. `backend/tests/test_geometry_inspection.py::TestComponentDistance` and `TestInspectionErrorRecovery::test_distance_with_a_kernel_failure_returns_error_not_a_crash` exercise this directly.
