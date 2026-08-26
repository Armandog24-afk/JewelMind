---
id: JM-BIBLE-A93
title: "Appendix: Inspection Type Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-463
  - JM-BIBLE-482
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Inspection Type Catalog

## Modules — `backend/jewelmind/geometry/inspection/`

| Module | Real function(s) | Purpose |
|---|---|---|
| `models.py` | — | Every Pydantic model and enum (`FactType`, `InspectionStatus`, `IntersectionStatus`, `InspectionDiagnosticCode`). |
| `version.py` | — | `INSPECTION_VERSION = "1.0.0"`, `CONTACT_TOLERANCE_MM = 1e-6`. |
| `diagnostics.py` | — | The 11 `INSPECTION_*` diagnostic code constants. |
| `shape.py` | `solid_count()`, `shape_is_valid()`, `topology_counts()`, `bounding_box_fact()`/`bounding_box_fact_from_box()` | Pure, read-only shape-level primitives. |
| `distance.py` | `inspect_distance()` | Wraps `cadquery.Shape.distance()` (OCP `BRepExtrema_DistShapeShape`). |
| `intersection.py` | `inspect_intersection()`, `should_skip_intersection()` | Wraps `cadquery.Shape.intersect()` (OCP `BRepAlgoAPI_Common`); broad-phase elimination. |
| `topology.py` | `inspect_topology()` | Solid/shell/face/edge/vertex counts + validity, with partial-result-on-failure handling. |
| `components.py` | `inspect_component()` | Per-component inspection orchestration. |
| `connectivity.py` | `pairwise_distances()`, `build_connectivity_graph()` | Real connectivity graph from real distance measurements. |
| `assembly.py` | `inspect_assembly()` | Assembly-level orchestration: connectivity, intersections, stone-metal separation, prong count, boolean operations. |
| `inspector.py` | `inspect_model()` | The one public top-level entry point; flattens everything into `geometricFacts`. |

## Status vocabulary — `InspectionStatus` (6 values)

| Status | Meaning | Reachable today? |
|---|---|---|
| `PASS` | The inspection produced a real, passing fact. | Yes |
| `FAIL` | The inspection produced a real fact that failed a structural check. | Yes |
| `UNKNOWN` | A kernel operation failed; no fact could be produced. | Yes |
| `ERROR` | A kernel operation raised; the inspection itself failed. | Yes |
| `NOT_APPLICABLE` | This inspection does not apply to this object. | **No — never constructed anywhere in the current code.** |
| `NOT_IMPLEMENTED` | This inspection has no implementation yet. | **No — never constructed anywhere in the current code.** |

## Intersection classification — `IntersectionStatus` (4 values)

| Status | Meaning |
|---|---|
| `INTERSECTS` | Real positive boolean-common volume above the contact tolerance. |
| `TOUCHES` | A boolean-common result exists but with zero-or-near-zero volume (surface contact). |
| `NO_INTERSECTION` | The boolean-common operation produced zero result solids. |
| `UNKNOWN` | The boolean-common (`Shape.intersect()`) call itself raised. |

## Cross-references

- [`463-inspection-subsystem-model.md`](../16-geometry-inspection/463-inspection-subsystem-model.md) — full module-by-module narrative.
- [`482-inspection-status-and-confidence.md`](../16-geometry-inspection/482-inspection-status-and-confidence.md) — why no fake confidence percentage exists anywhere in this system.
