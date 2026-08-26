"""Connectivity graph construction from real pairwise geometric relationships.

Two nodes are connected when `Shape.distance()` between them is at or
below `CONTACT_TOLERANCE_MM` — a pure kernel/geometric contact tolerance,
never an invented jewelry tolerance (INSPECT-GOV-012). Bounding-box
overlap is used only as a broad-phase filter to skip an unnecessary
kernel call for pairs that are obviously separated; it is never itself
the connectivity signal (per the Sprint 14 brief's explicit instruction).
See docs/bible/16-geometry-inspection/470-component-connectivity-model.md.
"""

from __future__ import annotations

from itertools import combinations

import cadquery as cq

from jewelmind.geometry.inspection.distance import inspect_distance
from jewelmind.geometry.inspection.models import ConnectivityEdge, ConnectivityGraph, DistanceResult
from jewelmind.geometry.inspection.version import CONTACT_TOLERANCE_MM


def pairwise_distances(shapes: dict[str, cq.Shape]) -> list[DistanceResult]:
    """Real `Shape.distance()` measurement for every pair in `shapes`.

    Distance itself is cheap enough (single-digit-to-tens of milliseconds
    per pair on current solitaire components — see
    484-inspection-performance-model.md) that no broad-phase elimination
    is needed here; bounding-box-based elimination is instead applied to
    the more expensive intersection step, gated on these real distance
    results — see `intersection.should_skip_intersection()`."""

    results: list[DistanceResult] = []
    for (name_a, shape_a), (name_b, shape_b) in combinations(shapes.items(), 2):
        results.append(inspect_distance(name_a, shape_a, name_b, shape_b))
    return results


def build_connectivity_graph(
    node_names: list[str], distances: list[DistanceResult], graph_type: str
) -> ConnectivityGraph:
    """Builds a connectivity graph over exactly `node_names` from a set of
    real `DistanceResult`s (which may include pairs outside `node_names` —
    those are ignored)."""

    node_set = set(node_names)
    edges: list[ConnectivityEdge] = []
    adjacency: dict[str, set[str]] = {n: set() for n in node_names}

    for d in distances:
        if d.componentA not in node_set or d.componentB not in node_set:
            continue
        if d.status != "PASS" or d.minDistanceMm is None:
            edges.append(
                ConnectivityEdge(
                    componentA=d.componentA, componentB=d.componentB, connected=False, basis="UNKNOWN"
                )
            )
            continue
        connected = d.minDistanceMm <= CONTACT_TOLERANCE_MM
        edges.append(
            ConnectivityEdge(
                componentA=d.componentA, componentB=d.componentB, connected=connected, basis="DISTANCE"
            )
        )
        if connected:
            adjacency[d.componentA].add(d.componentB)
            adjacency[d.componentB].add(d.componentA)

    groups = _connected_components(node_names, adjacency)

    return ConnectivityGraph(
        graphType=graph_type,
        nodes=list(node_names),
        edges=edges,
        connectedGroups=groups,
        isFullyConnected=len(groups) <= 1,
        disconnectedGroupCount=max(len(groups) - 1, 0),
    )


def _connected_components(nodes: list[str], adjacency: dict[str, set[str]]) -> list[list[str]]:
    visited: set[str] = set()
    groups: list[list[str]] = []
    for node in nodes:
        if node in visited:
            continue
        group: list[str] = []
        stack = [node]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            group.append(current)
            stack.extend(adjacency.get(current, set()) - visited)
        groups.append(sorted(group))
    return groups
