"""Structured result types for runtime geometry inspection.

Atlas inspection reports geometric facts; it never interprets them as
jewelry-domain or manufacturing judgments (INSPECT-GOV-001/002 — see
docs/bible/16-geometry-inspection/460-inspection-governance.md). Every
model here is kernel-neutral: no field ever holds a raw CadQuery
`Shape`/`Workplane` or an OCP object, only plain structured values, so
Forge (and any other consumer) can depend on inspection results without
importing CadQuery (INSPECT-GOV-016/017).
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

FactType = Literal[
    "SHAPE_EXISTS",
    "SHAPE_VALID",
    "SOLID_COUNT",
    "VOLUME",
    "BOUNDING_BOX",
    "COMPONENT_COUNT",
    "INTERSECTION_EXISTS",
    "INTERSECTION_VOLUME",
    "MIN_DISTANCE",
    "CONNECTED",
    "DISCONNECTED",
    "COMPONENT_PRESENT",
    "PRONG_COUNT",
    "STONE_METAL_SEPARATE",
    "BOOLEAN_RESULT_VALID",
    "FALLBACK_USED",
]

InspectionStatus = Literal["PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE", "NOT_IMPLEMENTED", "ERROR"]

IntersectionStatus = Literal["INTERSECTS", "TOUCHES", "NO_INTERSECTION", "UNKNOWN"]

InspectionDiagnosticCode = Literal[
    "INSPECTION_COMPONENT_MISSING",
    "INSPECTION_SHAPE_INVALID",
    "INSPECTION_VOLUME_FAILED",
    "INSPECTION_BOUNDING_BOX_FAILED",
    "INSPECTION_CONNECTIVITY_FAILED",
    "INSPECTION_INTERSECTION_FAILED",
    "INSPECTION_DISTANCE_FAILED",
    "INSPECTION_TOPOLOGY_FAILED",
    "INSPECTION_KERNEL_UNAVAILABLE",
    "INSPECTION_UNSUPPORTED",
    "INSPECTION_INTERNAL_ERROR",
]


class InspectionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class InspectionDiagnostic(InspectionModel):
    code: InspectionDiagnosticCode
    severity: Literal["info", "warning", "error"]
    message: str
    componentIds: list[str] = Field(default_factory=list)


class GeometricFact(InspectionModel):
    factId: str
    factType: FactType
    inspectionVersion: str
    scope: Literal["COMPONENT", "ASSEMBLY", "PAIR"]
    componentIds: list[str] = Field(default_factory=list)
    value: float | int | bool | str | None
    unit: str | None = None
    status: InspectionStatus
    tolerance: float | None = None
    sourceOperation: str
    generatedAt: str
    diagnostic: InspectionDiagnostic | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BoundingBoxFact(InspectionModel):
    xmin: float
    ymin: float
    zmin: float
    xmax: float
    ymax: float
    zmax: float
    sizeX: float
    sizeY: float
    sizeZ: float
    centerX: float
    centerY: float
    centerZ: float


class TopologyCounts(InspectionModel):
    solids: int
    shells: int
    faces: int
    edges: int
    vertices: int


class ComponentInspectionResult(InspectionModel):
    componentId: str
    exists: bool
    status: InspectionStatus
    shapeType: str | None = None
    solidCount: int | None = None
    volumeMm3: float | None = None
    boundingBox: BoundingBoxFact | None = None
    topology: TopologyCounts | None = None
    shapeValid: bool | None = None
    fallbackUsed: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    diagnostics: list[InspectionDiagnostic] = Field(default_factory=list)


class DistanceResult(InspectionModel):
    componentA: str
    componentB: str
    minDistanceMm: float | None
    status: InspectionStatus
    unit: str = "mm"
    tolerance: float


class IntersectionResult(InspectionModel):
    componentA: str
    componentB: str
    status: IntersectionStatus
    intersectionVolumeMm3: float | None = None
    intersectionSolidCount: int | None = None
    unit: str = "mm3"
    tolerance: float
    note: str = ""


class ConnectivityEdge(InspectionModel):
    componentA: str
    componentB: str
    connected: bool
    basis: Literal["DISTANCE", "INTERSECTION", "UNKNOWN"]


class ConnectivityGraph(InspectionModel):
    """Nodes and edges for one connectivity graph. Two distinct graphs are
    always built (production-only, and full-assembly-including-reference)
    — see docs/bible/16-geometry-inspection/470-component-connectivity-model.md."""

    graphType: Literal["PRODUCTION", "FULL_ASSEMBLY"]
    nodes: list[str]
    edges: list[ConnectivityEdge]
    connectedGroups: list[list[str]]
    isFullyConnected: bool
    disconnectedGroupCount: int


class StoneMetalSeparationResult(InspectionModel):
    stoneReferenceExists: bool
    productionIncluded: bool
    intersectsProductionComponents: list[str] = Field(default_factory=list)
    fusedIntoProductionMetal: bool
    status: InspectionStatus
    note: str = ""


class ProngCountResult(InspectionModel):
    requestedCount: int
    generatedCount: int
    matches: bool
    status: InspectionStatus


class BooleanOperationResult(InspectionModel):
    operation: Literal["FUSE", "CUT", "COMMON"]
    inputComponentIds: list[str]
    outputComponentId: str
    succeeded: bool
    fallbackUsed: bool
    outputSolidCount: int | None = None
    outputVolumeMm3: float | None = None
    note: str = ""


class AssemblyInspectionResult(InspectionModel):
    requiredComponentsPresent: bool
    missingComponentIds: list[str] = Field(default_factory=list)
    componentCount: int
    productionComponentCount: int
    referenceComponentCount: int
    totalProductionVolumeMm3: float
    assemblyBoundingBox: BoundingBoxFact
    productionConnectivity: ConnectivityGraph
    fullAssemblyConnectivity: ConnectivityGraph
    intersections: list[IntersectionResult]
    distances: list[DistanceResult]
    stoneMetalSeparation: StoneMetalSeparationResult
    prongCount: ProngCountResult
    booleanOperations: list[BooleanOperationResult] = Field(default_factory=list)


class InspectionPerformance(InspectionModel):
    totalDurationMs: float
    componentInspectionMs: float
    distanceInspectionMs: float
    intersectionInspectionMs: float
    topologyInspectionMs: float


class GeometryInspectionReport(InspectionModel):
    inspectionId: str
    inspectionVersion: str
    definitionHash: str
    geometryGeneratorVersion: str
    kernelVersion: str | None = None
    startedAt: str
    completedAt: str
    status: InspectionStatus
    componentResults: list[ComponentInspectionResult]
    assemblyResult: AssemblyInspectionResult
    geometricFacts: list[GeometricFact]
    diagnostics: list[InspectionDiagnostic] = Field(default_factory=list)
    performance: InspectionPerformance
    unavailableInspections: list[str] = Field(default_factory=list)
