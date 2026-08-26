---
id: JM-BIBLE-463
title: Inspection Subsystem Model
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
  - JM-BIBLE-461
  - JM-BIBLE-464
  - JM-BIBLE-465
implementation_status: current
professional_validation: not_required
normative: true
---

# Inspection Subsystem Model

This document goes one level deeper than [`461-inspection-architecture-overview.md`](461-inspection-architecture-overview.md): for each module that does real inspection work, the real function signatures and what they return.

## `shape.py` — pure shape-level primitives

```python
def solid_count(shape: cq.Shape) -> int
def shape_is_valid(shape: cq.Shape) -> bool
def topology_counts(shape: cq.Shape) -> TopologyCounts
def bounding_box_fact(shape: cq.Shape) -> BoundingBoxFact
def bounding_box_fact_from_box(bbox: BoundingBox) -> BoundingBoxFact
```

`solid_count()` is `len(shape.Solids())`. `shape_is_valid()` is a direct call to `shape.isValid()`. `topology_counts()` builds a `TopologyCounts(solids, shells, faces, edges, vertices)` from the five corresponding CadQuery accessors. `bounding_box_fact()` wraps `BoundingBox.from_shape()` (`geometry/model.py`) and derives `sizeX/Y/Z` and `centerX/Y/Z` from the six min/max values; `bounding_box_fact_from_box()` does the same starting from an already-computed `BoundingBox` (used for the assembly-level bounding box, which is a union of two components' boxes, not a fresh shape query).

## `distance.py` — one pairwise distance

```python
def inspect_distance(name_a: str, shape_a: cq.Shape, name_b: str, shape_b: cq.Shape) -> DistanceResult
```

Calls `shape_a.distance(shape_b)` inside a `try`/`except Exception`. On success, returns `DistanceResult(status="PASS", minDistanceMm=value, tolerance=CONTACT_TOLERANCE_MM)`. On any kernel exception, returns `DistanceResult(status="ERROR", minDistanceMm=None, tolerance=CONTACT_TOLERANCE_MM)` — never a guessed value (INSPECT-GOV-006).

## `intersection.py` — one pairwise boolean-common, plus broad-phase elimination

```python
def should_skip_intersection(min_distance_mm: float | None, tolerance: float = CONTACT_TOLERANCE_MM) -> bool
def inspect_intersection(name_a, shape_a, name_b, shape_b, *, known_separated: bool = False) -> IntersectionResult
```

`should_skip_intersection()` is a one-line comparison: `min_distance_mm is not None and min_distance_mm > tolerance`. `inspect_intersection()` either short-circuits (`known_separated=True`, returning `NO_INTERSECTION` with a note explaining the skip) or calls `shape_a.intersect(shape_b)` inside a `try`/`except Exception` and classifies the result into `INTERSECTS`/`TOUCHES`/`NO_INTERSECTION`/`UNKNOWN` based on solid count and volume against `CONTACT_TOLERANCE_MM`. See [`471-component-intersection-model.md`](471-component-intersection-model.md) for the full classification logic.

## `topology.py` — solid-level counts and validity, with kernel-failure isolation

```python
def inspect_topology(shape: cq.Shape) -> tuple[TopologyCounts | None, bool | None, InspectionStatus]
```

Two independent `try`/`except` blocks: one around `topology_counts()`, one around `shape_is_valid()`. This means a bounding-box or validity-check kernel failure can never prevent the other from being reported — `counts`/`is_valid` are `None` only if their own specific kernel call raised.

## `components.py` — one named component, end to end

```python
def inspect_component(name: str, component: GeneratedComponent) -> ComponentInspectionResult
```

Orchestrates, in order: existence (`shape.Solids()`), bounding box (`bounding_box_fact()`, wrapped in its own `try`/`except` producing `INSPECTION_BOUNDING_BOX_FAILED` on failure), topology (`inspect_topology()`), and volume finiteness/non-negativity (`component.volume_mm3`). The full contract is documented in [`464-component-inspection-contract.md`](464-component-inspection-contract.md).

## `connectivity.py` — pairwise distances into a graph

```python
def pairwise_distances(shapes: dict[str, cq.Shape]) -> list[DistanceResult]
def build_connectivity_graph(node_names: list[str], distances: list[DistanceResult], graph_type: str) -> ConnectivityGraph
def _connected_components(nodes: list[str], adjacency: dict[str, set[str]]) -> list[list[str]]
```

`pairwise_distances()` runs `inspect_distance()` over `itertools.combinations(shapes.items(), 2)` — every pair, no sampling. `build_connectivity_graph()` filters the given `distances` down to pairs whose both names are in `node_names`, builds a `ConnectivityEdge` per pair (`connected = minDistanceMm <= CONTACT_TOLERANCE_MM`), and calls `_connected_components()` — an explicit iterative DFS/union-style traversal (a stack-based DFS over an adjacency-set graph, not `itertools`/`networkx`) that groups nodes reachable from each other through `connected` edges. Full algorithm walkthrough in [`470-component-connectivity-model.md`](470-component-connectivity-model.md).

## `assembly.py` — the whole-model orchestrator

```python
def inspect_assembly(model: GeneratedModel, component_results: dict[str, ComponentInspectionResult]) -> tuple[AssemblyInspectionResult, dict[str, float]]
```

Plus three private helpers: `_stone_metal_separation()`, `_prong_count()`, `_boolean_operations()`. Full contract in [`465-assembly-inspection-contract.md`](465-assembly-inspection-contract.md).

## `inspector.py` — the top-level entry point

```python
def inspect_model(model: GeneratedModel) -> GeometryInspectionReport
```

Calls `inspect_component()` for every entry in `model.components`, then `inspect_assembly()` once, then flattens both into the `geometricFacts` list, aggregates diagnostics, and computes `overall_status` (`FAIL` if any required component is missing or any diagnostic has `severity == "error"`, `PASS` otherwise).

## Why this is 8 small modules and not one giant `inspect()` function

The Sprint 14 brief's explicit instruction was to decompose by concern rather than write one large inspection routine, and the real module boundaries reflect three genuinely different concerns:

1. **Shape-level** (`shape.py`, `topology.py`): operates on exactly one `cq.Shape`, knows nothing about component names or the assembly.
2. **Pairwise** (`distance.py`, `intersection.py`, `connectivity.py`): operates on exactly two named shapes (or a set of pairs), knows nothing about which components are "required" or what role each plays.
3. **Assembly-level orchestration** (`components.py`, `assembly.py`, `inspector.py`): the only layer that knows component names, required-component lists, roles (`jewelmind.geometry.roles`), and how to combine shape-level and pairwise results into one report.

Each module can be tested and reasoned about independently — `backend/tests/test_geometry_inspection.py` exercises `inspect_component()`, `inspect_distance()`, `inspect_intersection()`, and `build_connectivity_graph()` directly, not only through the top-level `inspect_model()` — and a future change to, say, how intersection is classified touches only `intersection.py`, never `components.py` or `inspector.py`.
