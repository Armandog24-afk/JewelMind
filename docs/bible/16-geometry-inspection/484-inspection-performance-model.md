---
id: JM-BIBLE-484
title: Inspection Performance Model
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
  - JM-BIBLE-481
  - JM-BIBLE-491
implementation_status: current
professional_validation: not_required
normative: false
---

# Inspection Performance Model

## `InspectionPerformance`

```python
class InspectionPerformance(InspectionModel):
    totalDurationMs: float
    componentInspectionMs: float
    distanceInspectionMs: float
    intersectionInspectionMs: float
    topologyInspectionMs: float
```

Every field is a real measurement via `time.perf_counter()`, not a placeholder. `inspect_assembly()` (`assembly.py`) returns `(result, timing_ms)` where `timing_ms` is a real dict with `distance`/`intersection`/`topology` durations measured directly around the corresponding real kernel-call blocks (`pairwise_distances()`, the `_ALL_PAIRS` intersection loop, `_boolean_operations()`'s `inspect_topology(model.combined_metal)` call). `inspector.py::inspect_model()` destructures this tuple and passes the real numbers straight into `InspectionPerformance` — it does not recompute or approximate them.

This was an explicit fix made during this Sprint: an initial draft used placeholder zeros for `distanceInspectionMs`/`intersectionInspectionMs`/`topologyInspectionMs`, with an inline admission that the pipeline was "not double-instrumented." The fix replaced that with real per-phase timing captured inside `inspect_assembly()` itself and threaded back out through its return tuple — every number in `InspectionPerformance` today is a real measurement of the current run, not a constant.

## Real measured ranges (vary run to run — report as ranges, not exact figures)

Verified directly by running the real pipeline against the default solitaire (numbers vary between runs due to JIT/cache effects, OS scheduling, and OCCT's own internal caching — a single run's exact figures are not the point):

| Phase | Real measured range | What it measures |
|---|---|---|
| Component inspection | ~80 ms | 4 components × (bounding box + topology counts + validity + volume check). |
| Distance inspection | ~10–90 ms for all 6 pairs | `BRepExtrema_DistShapeShape`, real, multi-threaded, cheap. |
| Intersection inspection | ~195 ms–1.8 s for the pairs actually computed | `BRepAlgoAPI_Common`, expensive, dominated by the `prongs` compound's 6 sub-solids. |
| Topology/shape-validity | ~15 ms | The `combined_metal` topology call inside `_boolean_operations()`. |
| Full inspection overhead | ~350 ms–1 s total, on top of ~350–400 ms of raw geometry generation | The whole `inspect_model()` call. |

One real run captured during this documentation pass: `totalDurationMs=354.96`, `componentInspectionMs=79.51`, `distanceInspectionMs=61.01`, `intersectionInspectionMs=198.70`, `topologyInspectionMs=15.23` — consistent with the ranges above. Distance is roughly 2–20x cheaper than intersection depending on the run, which is exactly why the broad-phase ordering below exists.

## The real broad-phase optimization

`intersection.py::should_skip_intersection(min_distance_mm, tolerance=CONTACT_TOLERANCE_MM)` returns `True` when a pair's own prior real distance measurement already proves separation beyond the kernel contact tolerance (`1e-6` mm). `inspect_assembly()` computes every pair's distance first (cheap), then for each of the 6 pairs in `_ALL_PAIRS`, checks `should_skip_intersection(d.minDistanceMm)` before deciding whether to actually call `inspect_intersection()`'s real `Shape.intersect()` path:

```python
d = distance_by_pair.get(frozenset((name_a, name_b)))
known_separated = d is not None and should_skip_intersection(d.minDistanceMm)
intersections.append(
    inspect_intersection(name_a, shapes[name_a], name_b, shapes[name_b], known_separated=known_separated)
)
```

When `known_separated=True`, `inspect_intersection()` short-circuits with a `NO_INTERSECTION` result (`intersectionVolumeMm3=0.0`) and never invokes `Shape.intersect()` at all. For the default solitaire this skips exactly 1 of the 6 pairs: `band` & `stone_reference`, whose real prior distance is `0.9000000000000004` mm — well beyond the `1e-6` mm tolerance — so the more expensive boolean-common call is never run for that pair. The other 5 pairs all have a real distance of `0.0`, so intersection is actually computed for all 5.

## Forward-looking scaling note — deliberately not solved this Sprint

The current solitaire (4 components, 6 possible pairs) is small enough that full pairwise inspection is practical on every real generation — the measured ~350 ms–1 s overhead sits comfortably alongside the ~350–400 ms raw geometry-generation time it runs after. This is explicitly flagged as a **future scaling risk, not a current problem**: intersection inspection is `O(n²)` in the number of components, and a pavé setting, a many-stone assembly, or a many-prong configuration with individually-tracked prongs (see [`475-prong-count-and-identity-inspection.md`](475-prong-count-and-identity-inspection.md) for why that does not exist today) would multiply the number of pairs quickly. This Sprint does **not** attempt to prematurely optimize beyond the real broad-phase distance-before-intersection ordering already implemented — no caching, no sampling, no pair-pruning heuristic beyond `should_skip_intersection()` exists yet. Solving `O(n²)` scaling for a larger future assembly is left as a real, documented concern for a later sprint (see [`491-runtime-inspection-policy.md`](491-runtime-inspection-policy.md), INSPECT-GOV-018).

## Cross-references

- [`471-component-intersection-model.md`](471-component-intersection-model.md) — the intersection mechanism itself.
- [`472-component-distance-model.md`](472-component-distance-model.md) — the distance mechanism the broad-phase check depends on.
- [`491-runtime-inspection-policy.md`](491-runtime-inspection-policy.md) — the classification of which inspections run always vs. conditionally, INSPECT-GOV-018.
