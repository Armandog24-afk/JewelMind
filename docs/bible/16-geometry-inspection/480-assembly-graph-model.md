---
id: JM-BIBLE-480
title: Assembly Graph Model
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
  - JM-BIBLE-470
  - JM-BIBLE-471
  - JM-BIBLE-472
  - JM-BIBLE-474
implementation_status: current
professional_validation: not_required
normative: true
---

# Assembly Graph Model

## `ConnectivityGraph` / `ConnectivityEdge`

```python
class ConnectivityEdge(InspectionModel):
    componentA: str
    componentB: str
    connected: bool
    basis: Literal["DISTANCE", "INTERSECTION", "UNKNOWN"]

class ConnectivityGraph(InspectionModel):
    graphType: Literal["PRODUCTION", "FULL_ASSEMBLY"]
    nodes: list[str]
    edges: list[ConnectivityEdge]
    connectedGroups: list[list[str]]
    isFullyConnected: bool
    disconnectedGroupCount: int
```

(`backend/jewelmind/geometry/inspection/models.py:141-158`.) This is the real, kernel-neutral graph representation Atlas Inspection reports — plain component-name nodes and boolean/basis-tagged edges, never a raw shape or OCP object (INSPECT-GOV-016).

## Two distinct graphs, always both built

`inspect_assembly()` (`assembly.py:169-171`) always constructs exactly two graphs from the same underlying `distances` list:

```python
production_connectivity = build_connectivity_graph(production_names, distances, "PRODUCTION")
full_connectivity = build_connectivity_graph(all_names, distances, "FULL_ASSEMBLY")
```

`production_names = production_component_names(all_names)` (`geometry/roles.py`) excludes `stone_reference`; `all_names` includes it. This is the real, direct implementation of INSPECT-GOV-009 ("production geometry and reference geometry must be inspected separately"). `TestStoneReferenceRole::test_stone_reference_is_counted_as_the_only_reference_component` confirms `"stone_reference" not in productionConnectivity.nodes` and `"stone_reference" in fullAssemblyConnectivity.nodes` for the real default solitaire.

## How an edge's `connected`/`basis` is actually decided

`build_connectivity_graph()` (`connectivity.py:39-79`) never runs a fresh kernel call of its own — it consumes the `DistanceResult` list `inspect_assembly()` already computed via `pairwise_distances()`. For each distance result whose pair falls within the current graph's node set:

- If `d.status != "PASS"` or `d.minDistanceMm is None` (the underlying `Shape.distance()` call itself failed): `connected=False`, `basis="UNKNOWN"`.
- Otherwise: `connected = d.minDistanceMm <= CONTACT_TOLERANCE_MM` (`1e-6` mm, `version.py`), `basis="DISTANCE"`.

## `basis: "INTERSECTION"` is schema-complete but never assigned

This is a real, honest, currently-unreachable enum value — stated plainly, not hidden. `ConnectivityEdge.basis` is typed as one of three literals, but `build_connectivity_graph()`'s only two branches ever produce `"DISTANCE"` or `"UNKNOWN"`; there is no code path anywhere in `connectivity.py` that assigns `"INTERSECTION"`. Connectivity is decided purely by a real minimum-distance measurement against `CONTACT_TOLERANCE_MM`, never by intersection (boolean-common) volume — even though `inspect_assembly()` also computes real per-pair `IntersectionResult`s in the same function, those results feed `AssemblyInspectionResult.intersections` and (for stone-metal separation) `_stone_metal_separation()`, but never `build_connectivity_graph()`. `"INTERSECTION"` exists in the schema so a future connectivity definition could use it without a breaking schema change, not because any current code path reaches it.

## `connectedGroups`, `isFullyConnected`, `disconnectedGroupCount`

`_connected_components()` (`connectivity.py:82-98`) runs a plain depth-first traversal over the adjacency built from `connected=True` edges, producing `connectedGroups: list[list[str]]` — each inner list sorted alphabetically, one list per connected component of the graph (a node with no connected edges at all still appears as its own singleton group). `isFullyConnected = len(groups) <= 1`; `disconnectedGroupCount = max(len(groups) - 1, 0)`.

For the real default solitaire's `PRODUCTION` graph: `connectedGroups == [["band", "basket_support", "prongs"]]` — one group of all three production components, `isFullyConnected = True`, `disconnectedGroupCount = 0`. This matches the recorded regression baseline in `specs/geometry-inspection/v2/test-vectors/regression-vectors.json` (`productionConnectivityFullyConnected: true`) and the determinism vectors (`productionConnectedGroups: [["band", "basket_support", "prongs"]]` on both independent runs).

`inspector.py::inspect_model()` also flattens the production connectivity groups into `GeometricFact`s of type `CONNECTED` (if there is exactly one group) or `DISCONNECTED` (if there is more than one), one fact per group, `factId=f"production.connectivity.group.{'-'.join(group)}"`.

## What this module never does

`ConnectivityGraph`/`build_connectivity_graph()` never infers "professional structural adequacy" from the graph — it reports which components are geometrically connected (by the real distance-based test above), full stop. It never labels a disconnected group as a manufacturing defect, never assigns a severity to `isFullyConnected=False`, and never references a Forge rule ID. Whether a disconnected production assembly is actually a problem — and for which manufacturing method — is exclusively Forge's judgment to make, and no Forge rule currently reads `CONNECTED`/`DISCONNECTED` facts (`forgeConsumptionStatus: "not_consumed"`, `specs/geometry-inspection/v2/fact-registry.json`).

## Test fixtures proving both real outcomes

`backend/tests/test_geometry_inspection.py::TestProductionConnectivity` (`test_real_solitaire_production_metal_is_fully_connected`, `test_full_assembly_graph_includes_the_stone_reference`) covers the connected case against real solitaire geometry. `TestDisconnectedFixture` (`test_two_far_apart_boxes_are_reported_as_two_disconnected_groups`, `test_disconnection_is_never_hidden_or_silently_repaired`) uses a TEST-FIXTURE-ONLY pair of plain cubes placed far apart — never a supported jewelry model, per INSPECT-GOV-003 — to prove a real `DISCONNECTED` result actually gets reported rather than repaired or hidden. `TestIntersectingFixture::test_two_overlapping_boxes_report_a_real_intersection_volume` proves the reverse case for intersection specifically.

## Cross-references

- [`470-component-connectivity-model.md`](470-component-connectivity-model.md) — the underlying distance-based connectivity definition.
- [`471-component-intersection-model.md`](471-component-intersection-model.md) / [`472-component-distance-model.md`](472-component-distance-model.md) — the two pairwise measurements this graph is (and is not) built from.
- [`474-stone-metal-separation-inspection.md`](474-stone-metal-separation-inspection.md) — why `fullAssemblyConnectivity` including `stone_reference` is not itself a stone-metal-fusion signal.
- [`487-forge-fact-contract.md`](487-forge-fact-contract.md) — the current, honest non-consumption of connectivity facts by Forge.
