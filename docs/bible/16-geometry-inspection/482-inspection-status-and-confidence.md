---
id: JM-BIBLE-482
title: Inspection Status and Confidence
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
  - JM-BIBLE-483
implementation_status: current
professional_validation: not_required
normative: true
---

# Inspection Status and Confidence

## The 6 real `InspectionStatus` values

```python
InspectionStatus = Literal["PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE", "NOT_IMPLEMENTED", "ERROR"]
```

(`backend/jewelmind/geometry/inspection/models.py:37`.) This one literal type is reused across every result model that reports a status: `ComponentInspectionResult.status`, `DistanceResult.status`, `GeometryInspectionReport.status`, `GeometricFact.status`, `StoneMetalSeparationResult.status`, `ProngCountResult.status`, and the tuple `inspect_topology()` returns.

## No fake confidence score anywhere

Stated plainly, per the brief's own instruction: **there is no numeric confidence value — 0-100 or otherwise — anywhere in this system.** Every kernel computation either genuinely provides a fact (a real number, boolean, or count, reported with `status: "PASS"`) or it does not (`"UNKNOWN"`, `"ERROR"`, or, in principle, `"NOT_IMPLEMENTED"`). `GeometricFact.value` is typed `float | int | bool | str | None` — never a probability, a percentage, or a fuzzy quality score. This is a direct restatement of INSPECT-GOV-006 ("UNKNOWN is preferable to fabricated PASS") holding at every layer of the model, not only at the top-level report.

## What each value actually means, grounded by real usage

Verified by grepping every real assignment of each literal across `backend/jewelmind/geometry/inspection/*.py` (not assumed):

| Value | Real meaning | Where it is actually assigned |
|---|---|---|
| `PASS` | A measurement succeeded and the underlying condition held (or, for a report-level `status`, no failing condition was found). | Widely — e.g. `inspect_distance()` on a successful `Shape.distance()` call; `inspect_topology()` when `valid is True`; every `_component_facts()` entry when its underlying value is present; `inspect_model()`'s overall `status` by default. |
| `FAIL` | A measurement succeeded and the underlying condition did **not** hold. | `inspect_component()` when any diagnostic has `severity == "error"`; `inspect_topology()` when `valid is False`; `_prong_count()` when `requested != generated`; `_stone_metal_separation()` when the stone does not exist; `inspect_model()`'s overall `status` when a required component is missing or any diagnostic is an error. |
| `UNKNOWN` | The kernel call itself raised, or a required input was missing, so no real value could be produced — never guessed. | `inspect_intersection()` on a kernel exception; `_prong_count()` when `requestedCount`/`generatedCount` metadata keys are absent; the `INTERSECTION_VOLUME`/`MIN_DISTANCE` facts in `inspector.py` when the underlying result's own status is `UNKNOWN`. |
| `ERROR` | A kernel call raised an exception during a check that is otherwise expected to succeed (distinguished from `UNKNOWN`, which is used specifically for the intersection/prong-count "no reliable value" case). | `inspect_distance()` on a kernel exception; `inspect_topology()` on either of its two internal kernel-call failures. |
| `NOT_APPLICABLE` | Reserved — see below. | **Never actually assigned anywhere in the current code.** |
| `NOT_IMPLEMENTED` | Reserved — see below. | **Never actually assigned anywhere in the current code**, aside from a comment in `topology.py` describing what a future, genuinely-unavailable check should report. |

## `NOT_APPLICABLE` and `NOT_IMPLEMENTED`: neither is reachable today

This is the honest finding from a direct grep of the package, not an assumption carried over from the brief. Both values are real, schema-complete members of `InspectionStatus`, but as of this Sprint:

- **`NOT_APPLICABLE`** is never constructed anywhere in `backend/jewelmind/geometry/inspection/`. There is currently no case where an inspection is skipped because a condition makes it structurally meaningless for a given model (e.g. a check that would only make sense for a jewelry category this codebase does not yet support) — every current inspection either runs for real, or fails/errors, for every one of the current 4 solitaire components.
- **`NOT_IMPLEMENTED`** is likewise never constructed. `topology.py`'s module docstring explicitly anticipates it ("a genuinely unavailable future check should still report NOT_IMPLEMENTED rather than fabricate a result") but no current inspection has actually hit that "genuinely unavailable" case — every kernel operation this Sprint's investigation attempted (`Shape.distance()`, `.intersect()`, `.isValid()`, the five topology-count methods) was verified to work against the installed `cadquery==2.8.0` build (see [`466-shape-validity-inspection.md`](466-shape-validity-inspection.md)).

Both values exist for a real reason — a future inspection whose kernel support turns out to be unavailable, or a future jewelry category where a current check would not apply — but reporting either as "in active use today" would be inaccurate. `GeometryInspectionReport.unavailableInspections` (see [`481-inspection-result-model.md`](481-inspection-result-model.md)) is the closer real analog for "genuinely unavailable," and it too is currently always `[]`.

## Cross-references

- [`481-inspection-result-model.md`](481-inspection-result-model.md) — `GeometryInspectionReport.status`'s own real computation.
- [`483-inspection-error-model.md`](483-inspection-error-model.md) — how a diagnostic's `severity` relates to (but is distinct from) a fact's `status`.
- [`466-shape-validity-inspection.md`](466-shape-validity-inspection.md) — the kernel-capability investigation that grounds why every current check succeeded rather than needing `NOT_IMPLEMENTED`.
