---
id: JM-BIBLE-483
title: Inspection Error Model
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
  - JM-BIBLE-482
  - JM-BIBLE-481
implementation_status: current
professional_validation: not_required
normative: true
---

# Inspection Error Model

## The core rule

A diagnostic never implies geometry invalidity on its own — unless the condition it reports is itself a required invariant. A missing required component **is** invalid (it flips `GeometryInspectionReport.status` to `FAIL` via `AssemblyInspectionResult.requiredComponentsPresent`). An intersection-measurement kernel failure on one optional pair **is not** — it produces `status: "UNKNOWN"`/`"ERROR"` on that one `IntersectionResult`/`DistanceResult` and does not, by itself, fail the whole report (INSPECT-GOV-019). `diagnostics.py`'s own module docstring states this directly: a diagnostic "means 'this specific inspection could not produce a fact,' which is different from 'the geometry itself is invalid.'"

## The 11 real `InspectionDiagnosticCode` values, and whether each is actually raised

Verified by grepping every real `InspectionDiagnostic(code=...)` construction across `backend/jewelmind/geometry/inspection/*.py` — not assumed from the code list or the diagnostics module's own definitions.

| Code | Actually constructed anywhere? | Where |
|---|---|---|
| `INSPECTION_COMPONENT_MISSING` | **Yes.** | `components.py:35` — when `inspect_component()` finds `shape.Solids()` empty. `severity="warning"`. |
| `INSPECTION_BOUNDING_BOX_FAILED` | **Yes.** | `components.py:49` — when `bounding_box_fact(shape)` raises. `severity="error"`. |
| `INSPECTION_TOPOLOGY_FAILED` | **Yes.** | `components.py:60` — when `inspect_topology()` returns `topology_status == "ERROR"`. `severity="error"`. |
| `INSPECTION_VOLUME_FAILED` | **Yes.** | `components.py:72` — when `component.volume_mm3` is missing, negative, or non-finite (a NaN self-inequality check). `severity="error"`. |
| `INSPECTION_SHAPE_INVALID` | **No.** | Defined in `models.py`/`diagnostics.py` only. `inspect_topology()`'s own validity check produces a `FAIL`/`ERROR` *status*, but `inspect_component()` never wraps an invalid-shape result in an `INSPECTION_SHAPE_INVALID` diagnostic — `ComponentInspectionResult.shapeValid` carries that fact directly instead, with no accompanying diagnostic entry. |
| `INSPECTION_CONNECTIVITY_FAILED` | **No.** | Never constructed. `build_connectivity_graph()` reports a failed distance measurement as `ConnectivityEdge(connected=False, basis="UNKNOWN")` — a real, honest edge value — without ever emitting a diagnostic for it. |
| `INSPECTION_INTERSECTION_FAILED` | **No.** | Never constructed. `inspect_intersection()`'s `except` branch returns `IntersectionResult(status="UNKNOWN", ...)` directly; `intersection.py` never imports `InspectionDiagnostic` at all. |
| `INSPECTION_DISTANCE_FAILED` | **No.** | Never constructed. `inspect_distance()`'s `except` branch returns `DistanceResult(status="ERROR", ...)` directly; `distance.py` never imports `InspectionDiagnostic` either. |
| `INSPECTION_KERNEL_UNAVAILABLE` | **No.** | Never constructed anywhere. |
| `INSPECTION_UNSUPPORTED` | **No.** | Never constructed anywhere. |
| `INSPECTION_INTERNAL_ERROR` | **No.** | Never constructed anywhere. |

**Only 4 of the 11 codes are actually raised today** — all 4 inside `components.py::inspect_component()`. The remaining 7 are schema-complete but currently unreachable, the same honest pattern used throughout this codebase in every prior Sprint (e.g. `348-intent-resolution-model.md`'s `ResolutionStatus` values, `482-inspection-status-and-confidence.md`'s `NOT_APPLICABLE`/`NOT_IMPLEMENTED`).

## A real, notable gap this creates: distance and intersection failures produce no diagnostic

`inspect_distance()` and `inspect_intersection()` each catch their own kernel exception and set the failing result's own `status` field (`"ERROR"` and `"UNKNOWN"` respectively) — but neither function constructs an `InspectionDiagnostic` at all. This means a kernel failure on a specific pair's distance or intersection measurement is visible if a caller reads that pair's own `DistanceResult.status`/`IntersectionResult.status`, or the corresponding `MIN_DISTANCE`/`INTERSECTION_VOLUME` `GeometricFact`'s `status` (both flattened into `geometricFacts` by `inspector.py`) — but it never appears in `GeometryInspectionReport.diagnostics`, and it can never trigger `INSPECTION_DISTANCE_FAILED`/`INSPECTION_INTERSECTION_FAILED`, because nothing constructs those codes. `diagnostics` is populated exclusively from `component_results.values()`'s own `.diagnostics` lists (`inspector.py:125-126`) — assembly-level pairwise failures never reach it. This is a real, honest current gap, not a fabricated smoothing-over: the two dedicated diagnostic codes for exactly this situation exist in the schema and are simply not wired up to the functions whose failure they were named for.

## Tests proving the UNKNOWN/ERROR paths work, even without a diagnostic

`backend/tests/test_geometry_inspection.py::TestInspectionErrorRecovery` — `test_intersection_with_a_kernel_failure_returns_unknown_not_a_crash` and `test_distance_with_a_kernel_failure_returns_error_not_a_crash`, both using a fake shape object whose `.intersect()`/`.distance()` methods raise `RuntimeError`, proving the pipeline returns a structured `UNKNOWN`/`ERROR` result rather than crashing — exactly the real behavior described above, including the real absence of an accompanying diagnostic entry.

## Cross-references

- [`482-inspection-status-and-confidence.md`](482-inspection-status-and-confidence.md) — the `InspectionStatus` values a diagnostic's underlying result carries, distinct from the diagnostic itself.
- [`481-inspection-result-model.md`](481-inspection-result-model.md) — how `diagnostics` feeds `GeometryInspectionReport.status`.
- [`appendices/inspection-diagnostic-catalog.md`](../appendices/inspection-diagnostic-catalog.md) — the full catalog this document's table is drawn from.
