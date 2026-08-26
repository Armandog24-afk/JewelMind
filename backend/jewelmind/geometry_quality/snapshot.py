"""Builds a normalized GeometrySnapshot from real Atlas + Inspection output.

Uses the real JDL -> validation -> geometry -> inspection pipeline
(QUALITY-GOV-002/015) — never mocks geometry and never hand-invents a
fact. Volatile fields (inspection IDs, timestamps, performance timing) are
excluded by construction rather than filtered after the fact (see
docs/bible/17-geometry-quality/README.md's "snapshot normalization"
section).
"""

from __future__ import annotations

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.inspection.inspector import inspect_model
from jewelmind.geometry.inspection.models import GeometryInspectionReport
from jewelmind.geometry.model import GeneratedModel
from jewelmind.geometry.roles import is_production_component
from jewelmind.geometry_quality.models import (
    AssemblySnapshot,
    ComponentSnapshot,
    DesignConsistencySnapshot,
    GeometrySnapshot,
    RelationshipSnapshot,
)
from jewelmind.geometry_quality.version import QUALITY_VERSION
from jewelmind.jewelry_category.dispatch import generate_jewelry
from jewelmind.validation.engine import has_errors, validate_definition


def build_snapshot_from_report(
    definition_hash: str, report: GeometryInspectionReport
) -> GeometrySnapshot:
    components = [
        ComponentSnapshot(
            componentId=c.componentId,
            role="PRODUCTION" if is_production_component(c.componentId) else "REFERENCE",
            present=c.exists,
            solidCount=c.solidCount,
            volumeMm3=c.volumeMm3,
            boundingBox=c.boundingBox.model_dump() if c.boundingBox else None,
            topology=c.topology.model_dump() if c.topology else None,
            fallbackUsed=c.fallbackUsed,
        )
        for c in sorted(report.componentResults, key=lambda c: c.componentId)
    ]

    distance_by_pair = {(d.componentA, d.componentB): d for d in report.assemblyResult.distances}
    intersection_by_pair = {
        (i.componentA, i.componentB): i for i in report.assemblyResult.intersections
    }
    pairs = sorted(set(distance_by_pair) | set(intersection_by_pair))
    connectivity_edges = {
        (e.componentA, e.componentB): e.connected
        for e in report.assemblyResult.fullAssemblyConnectivity.edges
    }
    relationships = [
        RelationshipSnapshot(
            componentA=a,
            componentB=b,
            connected=connectivity_edges.get((a, b)),
            intersectionStatus=(
                intersection_by_pair[(a, b)].status if (a, b) in intersection_by_pair else None
            ),
            minDistanceMm=(
                distance_by_pair[(a, b)].minDistanceMm if (a, b) in distance_by_pair else None
            ),
        )
        for a, b in pairs
    ]

    assembly = AssemblySnapshot(
        componentCount=report.assemblyResult.componentCount,
        productionComponentCount=report.assemblyResult.productionComponentCount,
        referenceComponentCount=report.assemblyResult.referenceComponentCount,
        productionConnectivityGroups=len(
            report.assemblyResult.productionConnectivity.connectedGroups
        ),
        productionIsFullyConnected=report.assemblyResult.productionConnectivity.isFullyConnected,
        boundingBox=report.assemblyResult.assemblyBoundingBox.model_dump(),
    )

    design_consistency = DesignConsistencySnapshot(
        requestedProngCount=report.assemblyResult.prongCount.requestedCount,
        generatedProngCount=report.assemblyResult.prongCount.generatedCount,
        prongCountMatches=report.assemblyResult.prongCount.matches,
        stoneReferenceIsProductionMetal=report.assemblyResult.stoneMetalSeparation.fusedIntoProductionMetal,
    )

    return GeometrySnapshot(
        snapshotVersion=QUALITY_VERSION,
        definitionHash=definition_hash,
        assembly=assembly,
        components=components,
        relationships=relationships,
        designConsistency=design_consistency,
    )


def generate_snapshot(
    definition: JewelryDefinition,
) -> tuple[GeometrySnapshot, GeneratedModel, GeometryInspectionReport]:
    """Run the real pipeline and return a normalized snapshot alongside the
    underlying GeneratedModel/report (callers need those for version
    fingerprinting and artifact regression, without re-running generation)."""

    results = validate_definition(definition)
    if has_errors(results):
        raise ValueError(
            "Definition has validation errors; a Golden fixture must be a "
            f"valid definition: {[r.model_dump() for r in results if r.severity == 'error']}"
        )

    # Dispatched by jewelry.category, exactly like production generation
    # (ModelService.generate()) — see
    # docs/bible/18-ring-architecture/532-ring-generation-contract.md.
    model = generate_jewelry(definition)
    report = inspect_model(model)
    snapshot = build_snapshot_from_report(model.definition_hash, report)
    return snapshot, model, report
