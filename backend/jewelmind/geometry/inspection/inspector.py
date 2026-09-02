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
from jewelmind.geometry.roles import GEOMETRY_ROLE


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
            facts.extend(_stone_identity_facts(now, result))
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


def _stone_identity_facts(
    now: str, result: ComponentInspectionResult
) -> list[GeometricFact]:
    """Stone v2 identity, source and provenance facts (brief section 45).

    Every value is read from the component metadata the Stone System already
    recorded; nothing here re-derives geometry, and nothing here judges it. A
    fact that genuinely does not apply is emitted with `status="NOT_APPLICABLE"`
    rather than omitted, so a reader can tell "this stone has no measured
    reference class" from "inspection forgot to look" (ATLAS-GOV-006's spirit,
    applied to facts).

    Pre-Sprint-20 components (and the byte-identical round fast path) carry only
    a subset of these keys. A missing key produces NOT_APPLICABLE, never a
    fabricated default.
    """

    meta = result.metadata
    facts: list[GeometricFact] = []

    def _fact(
        suffix: str, fact_type: str, value, source: str = "GeneratedComponent.metadata",
        unit: str | None = None,
    ) -> GeometricFact:
        return GeometricFact(
            factId=f"component.{result.componentId}.{suffix}",
            factType=fact_type,
            inspectionVersion=INSPECTION_VERSION,
            scope="COMPONENT",
            componentIds=[result.componentId],
            value=value,
            unit=unit,
            status="PASS" if value is not None else "NOT_APPLICABLE",
            sourceOperation=source,
            generatedAt=now,
        )

    # The round fast path predates `sourceMode`; reporting the mode it actually
    # is, rather than NOT_APPLICABLE, keeps the fact meaningful for every stone.
    facts.append(
        _fact("sourceMode", "STONE_SOURCE_MODE", meta.get("sourceMode", "PARAMETRIC_REFERENCE"))
    )
    facts.append(_fact("shapeIdentity", "STONE_SHAPE_IDENTITY", meta.get("shape")))
    facts.append(
        _fact(
            "profileIdentity",
            "STONE_PROFILE_IDENTITY",
            meta.get("profile", "FACETED_REFERENCE"),
        )
    )
    facts.append(_fact("shapeFamily", "STONE_SHAPE_FAMILY", meta.get("family")))
    facts.append(_fact("symmetryClass", "STONE_SYMMETRY_CLASS", meta.get("symmetry")))
    facts.append(
        _fact("representation", "STONE_REPRESENTATION", meta.get("representation", "PARAMETRIC"))
    )
    facts.append(
        _fact("dimensionProvenance", "STONE_DIMENSION_PROVENANCE", meta.get("dimensionProvenance"))
    )
    facts.append(
        _fact(
            "measuredReferenceClass",
            "STONE_MEASURED_REFERENCE_CLASS",
            meta.get("measuredReferenceClass"),
        )
    )
    facts.append(_fact("orientationDeg", "STONE_ORIENTATION_DEG", meta.get("orientationDeg"), unit="deg"))

    outline_available = meta.get("outlineAvailable")
    facts.append(_fact("outlineAvailable", "STONE_OUTLINE_AVAILABLE", outline_available))
    facts.append(
        _fact("outlinePointCount", "STONE_OUTLINE_POINT_COUNT", meta.get("outlinePointCount"))
    )
    anchors = meta.get("anchors")
    facts.append(
        _fact("anchorCount", "STONE_ANCHOR_COUNT", len(anchors) if anchors is not None else None)
    )

    provenance = meta.get("provenance") or {}
    facts.append(
        _fact(
            "generatorVersion",
            "STONE_GENERATOR_VERSION",
            provenance.get("generatorVersion") or meta.get("referenceGeometryVersion"),
        )
    )
    facts.append(_fact("importerVersion", "STONE_IMPORTER_VERSION", provenance.get("importerVersion")))
    facts.append(
        _fact("sourceAssetHash", "STONE_SOURCE_ASSET_HASH", provenance.get("sourceAssetHash"))
    )
    operations = provenance.get("normalizationOperations")
    facts.append(
        _fact(
            "normalizationOperationCount",
            "STONE_NORMALIZATION_OPERATION_COUNT",
            len(operations) if operations is not None else None,
        )
    )

    # A structural fact, not a measurement: the stone reference is never metal.
    # Read from the role registry rather than from geometry, because that is
    # where the invariant actually lives (LAW-006, INSPECT-GOV-008).
    facts.append(
        _fact(
            "isProductionMetal",
            "STONE_IS_PRODUCTION_METAL",
            GEOMETRY_ROLE.get(result.componentId) == "production_metal",
            source="geometry.roles.GEOMETRY_ROLE",
        )
    )
    return facts


def _setting_facts(now: str, model: GeneratedModel) -> list[GeometricFact]:
    """Setting-level runtime facts (brief section 25;
    docs/bible/21-setting/setting-inspection-contract.md).

    Reads the structured `SettingGeometryResult` the Setting System already
    produced — it does not re-derive anything, and it makes no quality
    judgement (SETTING-GOV-016). Prong-specific facts are emitted only for
    the prong family and bezel-specific facts only for bezel, so a fact's
    presence is itself honest about what was built.

    Returns an empty list when a model carries no setting result (e.g. a
    hand-constructed test fixture), rather than inventing defaults.
    """

    result = model.setting_result
    if result is None:
        return []

    facts: list[GeometricFact] = []
    components = list(result.generatedComponents)

    def _fact(suffix: str, fact_type: str, value, source: str, unit: str | None = None) -> GeometricFact:
        return GeometricFact(
            factId=f"setting.{suffix}",
            factType=fact_type,
            inspectionVersion=INSPECTION_VERSION,
            scope="ASSEMBLY",
            componentIds=components,
            value=value,
            unit=unit,
            status="PASS" if value is not None else "UNKNOWN",
            sourceOperation="SettingGeometryResult",
            generatedAt=now,
        )

    facts.append(_fact("type", "SETTING_TYPE", result.settingType, "SettingGeometryResult"))
    facts.append(
        _fact(
            "compatibilityStatus",
            "SETTING_COMPATIBILITY_STATUS",
            result.compatibilityStatus,
            "SettingGeometryResult",
        )
    )
    facts.append(
        _fact(
            "componentCount",
            "SETTING_COMPONENT_COUNT",
            len(result.generatedComponents),
            "SettingGeometryResult",
        )
    )

    if result.settingType == "prong":
        facts.append(
            _fact(
                "requestedProngCount",
                "SETTING_REQUESTED_PRONG_COUNT",
                result.requestedProngCount,
                "SettingGeometryResult",
            )
        )
        facts.append(
            _fact(
                "generatedProngCount",
                "SETTING_GENERATED_PRONG_COUNT",
                result.generatedProngCount,
                "SettingGeometryResult",
            )
        )
        facts.append(
            _fact(
                "placementStrategy",
                "SETTING_PLACEMENT_STRATEGY",
                result.placementStrategy,
                "SettingGeometryResult",
            )
        )

    if result.settingType == "bezel":
        bezel = model.components.get("bezel")
        outline_source = bezel.metadata.get("outlineSource") if bezel else None
        facts.append(
            _fact(
                "bezelOutlineSource",
                "BEZEL_OUTLINE_SOURCE",
                outline_source,
                "GeneratedComponent.metadata",
            )
        )
        # Continuity here means the wall is exactly one closed solid — a
        # real topological fact, never a claim about professional coverage.
        continuous = None
        if bezel is not None:
            continuous = len(bezel.shape.Solids()) == 1
        facts.append(
            _fact(
                "bezelWallContinuous",
                "BEZEL_WALL_CONTINUOUS",
                continuous,
                "Shape.Solids()",
            )
        )

    return facts


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

    geometric_facts.extend(_setting_facts(now, model))

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
