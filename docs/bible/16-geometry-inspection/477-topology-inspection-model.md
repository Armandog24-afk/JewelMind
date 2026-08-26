---
id: JM-BIBLE-477
title: Topology Inspection Model
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
  - JM-BIBLE-464
  - JM-BIBLE-483
implementation_status: current
professional_validation: not_required
normative: true
---

# Topology Inspection Model

## `TopologyCounts`

```python
class TopologyCounts(InspectionModel):
    solids: int
    shells: int
    faces: int
    edges: int
    vertices: int
```

(`backend/jewelmind/geometry/inspection/models.py:98-104`.) Each field is a direct count from the corresponding real CadQuery API — `shape.py::topology_counts()`:

```python
TopologyCounts(
    solids=len(shape.Solids()),
    shells=len(shape.Shells()),
    faces=len(shape.Faces()),
    edges=len(shape.Edges()),
    vertices=len(shape.Vertices()),
)
```

## `inspect_topology()`'s real return contract

```python
def inspect_topology(shape: cq.Shape) -> tuple[TopologyCounts | None, bool | None, InspectionStatus]:
```

(`topology.py:22-36`.) The function makes two independent kernel calls, each guarded separately:

1. `counts = topology_counts(shape)` inside its own `try`/`except`. If this raises, the function returns `(None, None, "ERROR")` immediately — no topology counts and no validity result.
2. `valid = shape_is_valid(shape)` (a thin wrapper around `cadquery.Shape.isValid()`, itself wrapping OCP's `BRepCheck_Analyzer`) inside a second, separate `try`/`except`. If *this* raises — after step 1 already succeeded — the function returns `(counts, None, "ERROR")`: the real counts from step 1 are preserved and returned, only the validity flag is lost.

This two-stage structure is deliberate: a later kernel call's failure does not discard results a prior kernel call already obtained. If both calls succeed, the function returns `(counts, valid, "PASS" if valid else "FAIL")` — topology status is `PASS`/`FAIL` based purely on kernel-reported validity, never `UNKNOWN`; `ERROR` is reserved for an actual kernel exception, not for "the shape is invalid but the check itself worked."

`inspect_component()` (`components.py:56-65`) only reacts to the `topology_status == "ERROR"` branch by appending an `INSPECTION_TOPOLOGY_FAILED` diagnostic with `severity="error"` — it does not append a diagnostic for a merely-invalid-but-successfully-checked shape (`status == "FAIL"` from `inspect_topology()` alone); `ComponentInspectionResult.shapeValid` carries that fact directly instead.

## Real measured topology for the band component

Verified by actually running `topology_counts()` against the real default-solitaire band (not assumed from the brief, independently re-run during this Sprint's documentation pass):

```
solids=1  shells=1  faces=6  edges=10  vertices=6
```

This matches the band's real shape: a revolved solid with an outer-rim fillet applied (`filletApplied: true` in the band's own `metadata`), which is why `edges`/`vertices` are not the plain 4-face/8-edge/8-vertex counts a sharp rectangular-cross-section revolve would otherwise produce — the fillet operation adds and reshapes faces/edges at the outer rim.

## What topology counts are for, and what they are not for

Per the brief's own instruction and INSPECT-GOV-001: topology counts are useful for **regression detection** (a future code change that unexpectedly alters `faces`/`edges`/`vertices` for a component whose dimensions did not change is a real signal worth investigating) and **debugging** (distinguishing a clean single-shell solid from a multi-shell or degenerate one when something else looks wrong). They are explicitly **not** a professional-interpretation signal — a raw edge or vertex count says nothing about jewelry quality, manufacturability, or aesthetic judgment, and no code in `backend/jewelmind/geometry/inspection/` ever compares a topology count against a jewelry-domain threshold (INSPECT-GOV-002).

## Tests

No dedicated `TestTopologyInspection` class exists in `backend/tests/test_geometry_inspection.py`; topology counts are exercised indirectly through `TestSolidCount` (`test_prongs_solid_count_matches_generated_count`, `test_band_is_a_single_solid`) and through every component-level assertion that reads `ComponentInspectionResult.solidCount`/`.shapeValid`, since those fields are populated from `inspect_topology()`'s return values.

## Cross-references

- [`464-component-inspection-contract.md`](464-component-inspection-contract.md) — where `TopologyCounts` is attached to `ComponentInspectionResult.topology`.
- [`483-inspection-error-model.md`](483-inspection-error-model.md) — `INSPECTION_TOPOLOGY_FAILED`'s real usage.
- [`07-atlas/128-brep-and-topology-model.md`](../07-atlas/128-brep-and-topology-model.md) — the underlying B-Rep/topology model this inspection measures against.
