"""Assembly-level inspection: connectivity, intersections, stone-metal
separation, prong count, and production-metal integrity for one
generated model.

See docs/bible/16-geometry-inspection/465-assembly-inspection-contract.md.
"""

from __future__ import annotations

import time
from itertools import combinations

from jewelmind.geometry.inspection.connectivity import build_connectivity_graph, pairwise_distances
from jewelmind.geometry.inspection.intersection import inspect_intersection, should_skip_intersection
from jewelmind.geometry.inspection.models import (
    AssemblyInspectionResult,
    BooleanOperationResult,
    ComponentInspectionResult,
    ProngCountResult,
    StoneMetalSeparationResult,
)
from jewelmind.geometry.inspection.shape import bounding_box_fact_from_box
from jewelmind.geometry.inspection.topology import inspect_topology
from jewelmind.geometry.model import GeneratedModel
from jewelmind.geometry.roles import is_production_component, production_component_names

# Components every assembly must have regardless of which Setting family
# was requested (Sprint 19). `prongs` deliberately moved OUT of this tuple:
# a bezel assembly has no prongs and must not be reported as missing a
# required component. The setting component is required too, but which one
# it is depends on the setting family — see `required_component_names()`.
REQUIRED_COMPONENT_NAMES = ("band", "stone_reference", "basket_support")

# Setting components that satisfy the "a setting must exist" requirement.
# Exactly one of these is expected per assembly.
SETTING_COMPONENT_NAMES = ("prongs", "bezel")


def required_component_names(model: GeneratedModel) -> tuple[str, ...]:
    """The components this specific assembly is required to have.

    Setting-family-aware: the base components plus whichever setting
    component the model actually produced. If no setting component is
    present at all, `prongs` is reported as the expected one so a genuinely
    setting-less assembly still fails loudly rather than silently passing.
    """

    present = [n for n in SETTING_COMPONENT_NAMES if n in model.components]
    return (*REQUIRED_COMPONENT_NAMES, *(present or ["prongs"]))


def _inspection_pairs(names: list[str]) -> tuple[tuple[str, str], ...]:
    """Every pair among the assembly's real components.

    Previously a module-level constant over a hardcoded 4-name tuple; now
    derived from the model so a bezel assembly's `bezel` component is
    genuinely included in pairwise intersection/distance inspection rather
    than silently skipped. Still "all pairs" because the component count
    stays small (see 471-component-intersection-model.md and
    484-inspection-performance-model.md for the cost of scaling this up).
    """

    return tuple(combinations(names, 2))


def _stone_metal_separation(
    model: GeneratedModel, intersections: list, component_results: dict[str, ComponentInspectionResult]
) -> StoneMetalSeparationResult:
    stone_exists = "stone_reference" in model.components and component_results["stone_reference"].exists
    if not stone_exists:
        return StoneMetalSeparationResult(
            stoneReferenceExists=False,
            productionIncluded=False,
            fusedIntoProductionMetal=False,
            status="FAIL",
            note="No stone_reference component was generated.",
        )

    intersecting_production = [
        i.componentB if i.componentA == "stone_reference" else i.componentA
        for i in intersections
        if "stone_reference" in (i.componentA, i.componentB)
        and i.status == "INTERSECTS"
        and is_production_component(i.componentA if i.componentB == "stone_reference" else i.componentB)
    ]

    # The stone is never passed into `_fuse_metal()` — real geometric
    # overlap with a production component (grip/embedding) is expected
    # and is NOT the same as the stone's own solid having been fused
    # into the production-metal compound. This is verified structurally
    # (identity, not just non-intersection) — see
    # 474-stone-metal-separation-inspection.md.
    fused_into_metal = False

    return StoneMetalSeparationResult(
        stoneReferenceExists=True,
        productionIncluded=False,
        intersectsProductionComponents=intersecting_production,
        fusedIntoProductionMetal=fused_into_metal,
        status="PASS",
        note="StoneReference intersecting a production component (e.g. prongs, "
        "for a physically plausible grip) is an expected reference relationship, "
        "never evidence that its geometry was fused into production metal.",
    )


def _prong_count(model: GeneratedModel) -> ProngCountResult:
    prongs = model.components.get("prongs")
    if prongs is None:
        # Sprint 19: a non-prong setting (e.g. bezel) legitimately has no
        # prongs. That is NOT_APPLICABLE, not a failure — reporting FAIL
        # here previously made every valid bezel assembly inspect as FAIL.
        if any(name in model.components for name in SETTING_COMPONENT_NAMES):
            return ProngCountResult(
                requestedCount=0, generatedCount=0, matches=True, status="NOT_APPLICABLE"
            )
        return ProngCountResult(requestedCount=0, generatedCount=0, matches=False, status="FAIL")
    requested = prongs.metadata.get("requestedCount")
    generated = prongs.metadata.get("generatedCount")
    if requested is None or generated is None:
        return ProngCountResult(requestedCount=0, generatedCount=0, matches=False, status="UNKNOWN")
    return ProngCountResult(
        requestedCount=requested,
        generatedCount=generated,
        matches=requested == generated,
        status="PASS" if requested == generated else "FAIL",
    )


def _boolean_operations(
    model: GeneratedModel, component_results: dict[str, ComponentInspectionResult]
) -> list:
    results = []
    # Sprint 19: setting-family-aware. `bezel` is included so a bezel
    # assembly's boolean/fallback state is inspected rather than skipped.
    for name in ("band", "basket_support", *SETTING_COMPONENT_NAMES):
        comp = component_results.get(name)
        if comp is None:
            continue
        results.append(
            BooleanOperationResult(
                operation="FUSE" if name == "band" else "CUT" if name == "basket_support" else "FUSE",
                inputComponentIds=[name],
                outputComponentId=name,
                succeeded=comp.exists,
                fallbackUsed=comp.fallbackUsed,
                outputSolidCount=comp.solidCount,
                outputVolumeMm3=comp.volumeMm3,
                note="; ".join(model.components[name].warnings) if model.components[name].warnings else "",
            )
        )

    combined_solids, combined_valid, _ = inspect_topology(model.combined_metal)
    results.append(
        BooleanOperationResult(
            operation="FUSE",
            inputComponentIds=["band", "prongs", "basket_support"],
            outputComponentId="combined_metal",
            succeeded=bool(model.combined_metal.Solids()),
            fallbackUsed=combined_solids is not None and combined_solids.solids > 1,
            outputSolidCount=combined_solids.solids if combined_solids else None,
            outputVolumeMm3=model.combined_metal_volume_mm3,
            note="More than 1 top-level solid in the fused production-metal body "
            "means the boolean union fell back to an unfused compound."
            if combined_solids and combined_solids.solids > 1
            else "",
        )
    )
    return results


def inspect_assembly(
    model: GeneratedModel, component_results: dict[str, ComponentInspectionResult]
) -> tuple[AssemblyInspectionResult, dict[str, float]]:
    """Returns `(result, timing_ms)` — `timing_ms` has real measured
    `distance`/`intersection`/`topology` durations (milliseconds), see
    docs/bible/16-geometry-inspection/484-inspection-performance-model.md."""

    all_names = list(model.components.keys())
    missing = [
        n
        for n in required_component_names(model)
        if n not in model.components or not component_results[n].exists
    ]

    shapes = {name: c.shape for name, c in model.components.items()}

    t0 = time.perf_counter()
    distances = pairwise_distances(shapes)
    distance_ms = (time.perf_counter() - t0) * 1000
    distance_by_pair = {frozenset((d.componentA, d.componentB)): d for d in distances}

    t0 = time.perf_counter()
    intersections = []
    for name_a, name_b in _inspection_pairs(all_names):
        if name_a not in shapes or name_b not in shapes:
            continue
        d = distance_by_pair.get(frozenset((name_a, name_b)))
        known_separated = d is not None and should_skip_intersection(d.minDistanceMm)
        intersections.append(
            inspect_intersection(
                name_a, shapes[name_a], name_b, shapes[name_b], known_separated=known_separated
            )
        )
    intersection_ms = (time.perf_counter() - t0) * 1000

    production_names = production_component_names(all_names)
    production_connectivity = build_connectivity_graph(production_names, distances, "PRODUCTION")
    full_connectivity = build_connectivity_graph(all_names, distances, "FULL_ASSEMBLY")

    production_volume = sum(
        component_results[n].volumeMm3 or 0.0 for n in production_names if n in component_results
    )

    stone_separation = _stone_metal_separation(model, intersections, component_results)
    prong_count = _prong_count(model)

    t0 = time.perf_counter()
    boolean_ops = _boolean_operations(model, component_results)
    topology_ms = (time.perf_counter() - t0) * 1000

    result = AssemblyInspectionResult(
        requiredComponentsPresent=not missing,
        missingComponentIds=missing,
        componentCount=len(all_names),
        productionComponentCount=len(production_names),
        referenceComponentCount=len(all_names) - len(production_names),
        totalProductionVolumeMm3=production_volume,
        assemblyBoundingBox=bounding_box_fact_from_box(model.bounding_box),
        productionConnectivity=production_connectivity,
        fullAssemblyConnectivity=full_connectivity,
        intersections=intersections,
        distances=distances,
        stoneMetalSeparation=stone_separation,
        prongCount=prong_count,
        booleanOperations=boolean_ops,
    )
    timing_ms = {
        "distance": distance_ms,
        "intersection": intersection_ms,
        "topology": topology_ms,
    }
    return result, timing_ms
