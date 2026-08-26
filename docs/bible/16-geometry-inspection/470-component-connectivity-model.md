---
id: JM-BIBLE-470
title: Component Connectivity Model
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
  - JM-BIBLE-471
  - JM-BIBLE-472
  - JM-BIBLE-473
  - JM-BIBLE-141
implementation_status: current
professional_validation: not_required
normative: true
---

# Component Connectivity Model

This is the most architecturally important document in this batch: it is the runtime realization of a gap Sprint 5's [`07-atlas/141-connectivity-and-component-integrity.md`](../07-atlas/141-connectivity-and-component-integrity.md) recorded as entirely `PLANNED` — "number of disconnected metal bodies... currently only implicitly known via the fuse-vs-compound outcome (1 vs. 3), never reported as an explicit count."

## Two distinct graphs, always both built

`assembly.py::inspect_assembly()` always builds exactly two `ConnectivityGraph`s from the same underlying pairwise-distance measurements:

- **`PRODUCTION`** — nodes are `jewelmind.geometry.roles.production_component_names(all_names)`, i.e. every component whose `GEOMETRY_ROLE` is `"production_metal"` (`band`, `prongs`, `basket_support` for the current solitaire). `stone_reference` is never a node in this graph.
- **`FULL_ASSEMBLY`** — nodes are every component in the model, `stone_reference` included.

This split is INSPECT-GOV-009 made real: production geometry and reference geometry are inspected as separate connectivity questions, never conflated into one graph that would make "the stone touches the prongs" look like the same kind of fact as "the band, prongs, and basket form one connected metal body."

## The real algorithm — never bounding-box comparison alone

`connectivity.py::pairwise_distances(shapes)` runs `inspect_distance()` (a real `cadquery.Shape.distance()` call, itself `BRepExtrema_DistShapeShape`) over every pair via `itertools.combinations(shapes.items(), 2)` — all `C(4,2) = 6` pairs for the current 4-component solitaire, computed once and shared by both graphs. `build_connectivity_graph(node_names, distances, graph_type)` then:

1. Filters `distances` down to pairs where both names are in `node_names`.
2. For each remaining pair, builds a `ConnectivityEdge`. If the distance measurement itself failed (`status != "PASS"` or `minDistanceMm is None`), the edge is `connected=False, basis="UNKNOWN"`. Otherwise, `connected = minDistanceMm <= CONTACT_TOLERANCE_MM` and `basis="DISTANCE"`.
3. Builds an adjacency set from every `connected=True` edge.
4. Calls `_connected_components(node_names, adjacency)` — an explicit, iterative stack-based depth-first traversal (not `networkx`, not a formal union-find data structure, though it computes the same result: for each unvisited node, push it on a stack, pop, mark visited, push its unvisited neighbors, repeat, and the accumulated group becomes one connected component) that groups every node reachable from every other through `connected` edges.

`ConnectivityGraph.isFullyConnected = len(groups) <= 1`; `disconnectedGroupCount = max(len(groups) - 1, 0)`.

This is a direct, explicit fulfillment of the Sprint 14 brief's prohibition against a bounding-box-comparison shortcut for connectivity: `connectivity.py`'s own module docstring states it plainly — "Bounding-box overlap is used only as a broad-phase filter to skip an unnecessary kernel call for pairs that are obviously separated; it is never itself the connectivity signal." In current code, that broad-phase filter is applied to the more expensive *intersection* step (via `should_skip_intersection()`, gated on the real distance already measured), not to connectivity itself — connectivity always uses the real `Shape.distance()` result directly, with no bounding-box shortcut in its own decision path.

## `CONTACT_TOLERANCE_MM` — a pure kernel tolerance

`version.py::CONTACT_TOLERANCE_MM = 1e-6`. Documented as one order of magnitude looser than OpenCascade's own default geometric confusion tolerance, `Precision::Confusion() = 1e-7` — chosen to stay robust to the small numerical noise real boolean/revolve operations can leave behind, while remaining many orders of magnitude tighter than any real jewelry dimension. This is never a jewelry-domain clearance or gap tolerance; it answers only "are these two solids touching or overlapping, at the level of kernel numerical precision."

## Real result for the default solitaire

**Production graph**: fully connected, one group `["band", "basket_support", "prongs"]` (`disconnectedGroupCount = 0`). **Full-assembly graph**: also fully connected, one group of all 4 components. `stone_reference` genuinely touches `prongs` and `basket_support` (real measured distance 0.0mm for both pairs) even though it is excluded from the production graph — this is a definitional exclusion by role (`GEOMETRY_ROLE["stone_reference"] == "stone_reference"`, not `"production_metal"`), never evidence that the stone is disconnected from the rest of the assembly. `band`↔`stone_reference` is the one genuinely separated pair, at 0.9mm.

## Test-fixture-only counter-example

`backend/tests/test_geometry_inspection.py::TestDisconnectedFixture::test_two_far_apart_boxes_are_reported_as_two_disconnected_groups` builds two plain cubes 100mm apart (explicitly marked `TEST FIXTURE ONLY` in the test file's own docstring — never a supported jewelry model) and confirms `build_connectivity_graph()` correctly reports `isFullyConnected=False`, `disconnectedGroupCount=1`, and 2 connected-component groups. `TestIntersectingFixture` provides the complementary positive case (two overlapping boxes reporting a real intersection). These fixtures exist specifically to exercise the disconnected/intersecting code paths, which the real solitaire (being fully connected by construction) never triggers on its own.

## Cross-references

[`465-assembly-inspection-contract.md`](465-assembly-inspection-contract.md) for where both graphs fit into the wider assembly orchestration; [`471-component-intersection-model.md`](471-component-intersection-model.md) for how a positive distance result feeds broad-phase intersection elimination; [`472-component-distance-model.md`](472-component-distance-model.md) for the underlying pairwise-distance primitive itself; [`473-production-metal-integrity.md`](473-production-metal-integrity.md) for how `disconnectedGroupCount` on the production graph specifically feeds the production-metal integrity summary; [`07-atlas/141-connectivity-and-component-integrity.md`](../07-atlas/141-connectivity-and-component-integrity.md) for the Sprint 5 planning document this Sprint makes real.
