"""Top-level entry point: `inspect_model()` runs every current runtime
inspection against one already-generated `GeneratedModel` and returns a
complete, kernel-neutral `GeometryInspectionReport`.

Read-only throughout — nothing here mutates or repairs the shapes it
inspects (INSPECT-GOV-013/014). See
docs/bible/16-geometry-inspection/463-inspection-subsystem-model.md and
491-runtime-inspection-policy.md for which checks run on every
generation vs. are considered optional/expensive.
"""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime

import cadquery as cq

from jewelmind.geometry.inspection.assembly import inspect_assembly
from jewelmind.geometry.inspection.components import inspect_component
from jewelmind.geometry.inspection.models import (
    ComponentInspectionResult,
    GeometricFact,
    GeometryInspectionReport,
    InspectionDiagnostic,
    InspectionPerformance,
    InspectionStatus,
)
from jewelmind.geometry.inspection.version import INSPECTION_VERSION
from jewelmind.geometry.model import GeneratedModel


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _kernel_version() -> str | None:
    try:
        return cq.__version__
    except Exception:  # noqa: BLE001 - version introspection must never break inspection
        return None


def _component_facts(now: str, result: ComponentInspectionResult) -> list[GeometricFact]:
    facts = [
        GeometricFact(
            factId=f"component.{result.componentId}.exists",
            factType="COMPONENT_PRESENT",
            inspectionVersion=INSPECTION_VERSION,
            scope="COMPONENT",
            componentIds=[result.componentId],
            value=result.exists,
            status="PASS" if result.exists else "FAIL",
            sourceOperation="Shape.Solids()",
            generatedAt=now,
        ),
        GeometricFact(
            factId=f"component.{result.componentId}.solidCount",
            factType="SOLID_COUNT",
            inspectionVersion=INSPECTION_VERSION,
            scope="COMPONENT",
            componentIds=[result.componentId],
            value=result.solidCount,
            status="PASS" if result.solidCount is not None else "UNKNOWN",
            sourceOperation="Shape.Solids()",
            generatedAt=now,
        ),
        GeometricFact(
            factId=f"component.{result.componentId}.volume",
            factType="VOLUME",
            inspectionVersion=INSPECTION_VERSION,
            scope="COMPONENT",
            componentIds=[result.componentId],
            value=result.volumeMm3,
            unit="mm3",
            status="PASS" if result.volumeMm3 is not None else "UNKNOWN",
            sourceOperation="Shape.Volume",
            generatedAt=now,
        ),
        GeometricFact(
            factId=f"component.{result.componentId}.shapeValid",
            factType="SHAPE_VALID",
            inspectionVersion=INSPECTION_VERSION,
            scope="COMPONENT",
            componentIds=[result.componentId],
            value=result.shapeValid,
            status="PASS" if result.shapeValid else ("UNKNOWN" if result.shapeValid is None else "FAIL"),
            sourceOperation="Shape.isValid()",
            generatedAt=now,
        ),
    ]
    if result.boundingBox is not None:
        facts.append(
            GeometricFact(
                factId=f"component.{result.componentId}.boundingBox",
                factType="BOUNDING_BOX",
                inspectionVersion=INSPECTION_VERSION,
                scope="COMPONENT",
                componentIds=[result.componentId],
                value=None,
                status="PASS",
                sourceOperation="Shape.BoundingBox()",
                generatedAt=now,
                metadata=result.boundingBox.model_dump(),
            )
        )
        if result.componentId == "stone_reference":
            facts.extend(_stone_dimension_facts(now, result))
    return facts


def _stone_dimension_facts(now: str, result: ComponentInspectionResult) -> list[GeometricFact]:
    """Requested-vs-measured dimension facts for the stone reference
    (brief section 31; docs/bible/20-stone/574-stone-inspection-contract.md).

    STONE_REQUESTED_* comes from the component's own build-time metadata —
    CONSTRUCTION_PARAMETER, the same value used to build the geometry,
    never independently re-measured (mirrors Shank's `widthSamplesMm`
    convention, Sprint 17). STONE_MEASURED_* comes from the real,
    independently computed bounding box (`BoundingBoxFact.sizeY`/`sizeX`/
    `sizeZ`) — genuine MEASURED_GEOMETRY, catching an accidental scaling
    or shape regression. `sizeY`/`sizeX` correspond to length/width only
    at `orientation=0`; a rotated stone's axis-aligned bounding box no
    longer isolates length from width exactly — a known, documented
    simplification, not silently assumed exact for every orientation.
    """

    meta = result.metadata
    bbox = result.boundingBox
    assert bbox is not None
    requested_length = meta.get("lengthMm")
    requested_width = meta.get("widthMm")
    requested_depth = meta.get("depthMm")

    def _fact(fact_id_suffix: str, fact_type: str, value: float | None, source: str) -> GeometricFact:
        return GeometricFact(
            factId=f"component.{result.componentId}.{fact_id_suffix}",
            factType=fact_type,
            inspectionVersion=INSPECTION_VERSION,
            scope="COMPONENT",
            componentIds=[result.componentId],
            value=value,
            unit="mm",
            status="PASS" if value is not None else "UNKNOWN",
            sourceOperation=source,
            generatedAt=now,
        )

    return [
        _fact("requestedLength", "STONE_REQUESTED_LENGTH", requested_length, "GeneratedComponent.metadata"),
        _fact("measuredLength", "STONE_MEASURED_LENGTH", bbox.sizeY, "Shape.BoundingBox()"),
        _fact("requestedWidth", "STONE_REQUESTED_WIDTH", requested_width, "GeneratedComponent.metadata"),
        _fact("measuredWidth", "STONE_MEASURED_WIDTH", bbox.sizeX, "Shape.BoundingBox()"),
        _fact("requestedDepth", "STONE_REQUESTED_DEPTH", requested_depth, "GeneratedComponent.metadata"),
        _fact("measuredDepth", "STONE_MEASURED_DEPTH", bbox.sizeZ, "Shape.BoundingBox()"),
    ]


def inspect_model(model: GeneratedModel) -> GeometryInspectionReport:
    started_at = _now()
    t_start = time.perf_counter()

    t0 = time.perf_counter()
    component_results = {name: inspect_component(name, comp) for name, comp in model.components.items()}
    component_ms = (time.perf_counter() - t0) * 1000

    assembly_result, assembly_timing_ms = inspect_assembly(model, component_results)
    distance_ms = assembly_timing_ms["distance"]
    intersection_ms = assembly_timing_ms["intersection"]
    topology_ms = assembly_timing_ms["topology"]

    diagnostics: list[InspectionDiagnostic] = []
    for result in component_results.values():
        diagnostics.extend(result.diagnostics)

    geometric_facts: list[GeometricFact] = []
    now = _now()
    for result in component_results.values():
        geometric_facts.extend(_component_facts(now, result))

    geometric_facts.append(
        GeometricFact(
            factId="assembly.componentCount",
            factType="COMPONENT_COUNT",
            inspectionVersion=INSPECTION_VERSION,
            scope="ASSEMBLY",
            componentIds=list(model.components.keys()),
            value=assembly_result.componentCount,
            status="PASS",
            sourceOperation="len(model.components)",
            generatedAt=now,
        )
    )
    geometric_facts.append(
        GeometricFact(
            factId="assembly.prongCount",
            factType="PRONG_COUNT",
            inspectionVersion=INSPECTION_VERSION,
            scope="ASSEMBLY",
            componentIds=["prongs"],
            value=assembly_result.prongCount.generatedCount,
            status=assembly_result.prongCount.status,
            sourceOperation="prongs.metadata",
            generatedAt=now,
            metadata=assembly_result.prongCount.model_dump(),
        )
    )
    geometric_facts.append(
        GeometricFact(
            factId="assembly.stoneMetalSeparate",
            factType="STONE_METAL_SEPARATE",
            inspectionVersion=INSPECTION_VERSION,
            scope="ASSEMBLY",
            componentIds=["stone_reference"],
            value=not assembly_result.stoneMetalSeparation.fusedIntoProductionMetal,
            status=assembly_result.stoneMetalSeparation.status,
            sourceOperation="assembly.stoneMetalSeparation",
            generatedAt=now,
        )
    )
    for intersection in assembly_result.intersections:
        geometric_facts.append(
            GeometricFact(
                factId=f"pair.{intersection.componentA}.{intersection.componentB}.intersectionVolume",
                factType="INTERSECTION_VOLUME",
                inspectionVersion=INSPECTION_VERSION,
                scope="PAIR",
                componentIds=[intersection.componentA, intersection.componentB],
                value=intersection.intersectionVolumeMm3,
                unit="mm3",
                status="PASS" if intersection.status != "UNKNOWN" else "UNKNOWN",
                tolerance=intersection.tolerance,
                sourceOperation="Shape.intersect()",
                generatedAt=now,
            )
        )
    for distance in assembly_result.distances:
        geometric_facts.append(
            GeometricFact(
                factId=f"pair.{distance.componentA}.{distance.componentB}.minDistance",
                factType="MIN_DISTANCE",
                inspectionVersion=INSPECTION_VERSION,
                scope="PAIR",
                componentIds=[distance.componentA, distance.componentB],
                value=distance.minDistanceMm,
                unit="mm",
                status=distance.status,
                tolerance=distance.tolerance,
                sourceOperation="Shape.distance()",
                generatedAt=now,
            )
        )
    production_groups = assembly_result.productionConnectivity.connectedGroups
    for group in production_groups:
        fact_type = "CONNECTED" if len(production_groups) == 1 else "DISCONNECTED"
        geometric_facts.append(
            GeometricFact(
                factId=f"production.connectivity.group.{'-'.join(group)}",
                factType=fact_type,
                inspectionVersion=INSPECTION_VERSION,
                scope="ASSEMBLY",
                componentIds=group,
                value=True,
                status="PASS",
                sourceOperation="connectivity graph (Shape.distance())",
                generatedAt=now,
            )
        )

    total_ms = (time.perf_counter() - t_start) * 1000
    completed_at = _now()

    overall_status: InspectionStatus = "PASS"
    if not assembly_result.requiredComponentsPresent:
        overall_status = "FAIL"
    elif any(d.severity == "error" for d in diagnostics):
        overall_status = "FAIL"

    return GeometryInspectionReport(
        inspectionId=f"inspection-{uuid.uuid4()}",
        inspectionVersion=INSPECTION_VERSION,
        definitionHash=model.definition_hash,
        geometryGeneratorVersion=model.generator_version,
        kernelVersion=_kernel_version(),
        startedAt=started_at,
        completedAt=completed_at,
        status=overall_status,
        componentResults=list(component_results.values()),
        assemblyResult=assembly_result,
        geometricFacts=geometric_facts,
        diagnostics=diagnostics,
        performance=InspectionPerformance(
            totalDurationMs=total_ms,
            componentInspectionMs=component_ms,
            distanceInspectionMs=distance_ms,
            intersectionInspectionMs=intersection_ms,
            topologyInspectionMs=topology_ms,
        ),
        unavailableInspections=[],
    )
