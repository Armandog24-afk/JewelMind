"""Structured types for the geometry quality / golden model subsystem.

A Golden Model is a versioned software regression reference — never a
professional approval, manufacturing-readiness claim, or aesthetic
judgment (QUALITY-GOV-001). See
docs/bible/17-geometry-quality/501-golden-model-contract.md.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

QualitySignalType = Literal[
    "EXACT_INVARIANT",
    "NUMERIC_REGRESSION",
    "RELATIONSHIP_REGRESSION",
    "TOPOLOGY_REGRESSION",
    "ARTIFACT_REGRESSION",
    "PERFORMANCE_OBSERVATION",
]

QualityResultStatus = Literal[
    "PASS",
    "PASS_WITH_KNOWN_LIMITATIONS",
    "REGRESSION_DETECTED",
    "VERSION_REVIEW_REQUIRED",
    "BASELINE_MISSING",
    "ERROR",
]

DiffSeverity = Literal["NONE", "INFO", "REGRESSION", "VERSION_REVIEW_REQUIRED"]

BaselineStatus = Literal["INITIAL", "STABLE", "CANDIDATE", "KNOWN_LIMITATION"]


class QualityModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class VersionFingerprint(QualityModel):
    jdlSchemaVersion: str
    forgeRuleSetVersion: str
    compilerVersion: str
    atlasGeneratorVersion: str
    inspectionVersion: str
    kernelVersion: str
    ocpVersion: str | None = None


class ComponentSnapshot(QualityModel):
    componentId: str
    role: Literal["PRODUCTION", "REFERENCE"]
    present: bool
    solidCount: int | None = None
    volumeMm3: float | None = None
    boundingBox: dict[str, float] | None = None
    topology: dict[str, int] | None = None
    fallbackUsed: bool = False


class RelationshipSnapshot(QualityModel):
    componentA: str
    componentB: str
    connected: bool | None = None
    intersectionStatus: Literal["INTERSECTS", "TOUCHES", "NO_INTERSECTION", "UNKNOWN"] | None = None
    minDistanceMm: float | None = None


class DesignConsistencySnapshot(QualityModel):
    requestedProngCount: int
    generatedProngCount: int
    prongCountMatches: bool
    stoneReferenceIsProductionMetal: bool


class AssemblySnapshot(QualityModel):
    componentCount: int
    productionComponentCount: int
    referenceComponentCount: int
    productionConnectivityGroups: int
    productionIsFullyConnected: bool
    boundingBox: dict[str, float]


class GeometrySnapshot(QualityModel):
    """Stable, normalized geometric facts for one golden case — built
    entirely from real Sprint 14 inspection output, never hand-invented
    (QUALITY-GOV-002/015). Timestamps, inspection/request IDs, and other
    volatile fields are excluded by construction, not filtered after the
    fact."""

    snapshotVersion: str
    definitionHash: str
    assembly: AssemblySnapshot
    components: list[ComponentSnapshot]
    relationships: list[RelationshipSnapshot]
    designConsistency: DesignConsistencySnapshot


class ArtifactExpectation(QualityModel):
    artifactType: Literal["STEP", "STL", "JSON", "SPECIFICATION"]
    nonEmpty: bool = True
    minSolidCount: int | None = None


class GoldenModel(QualityModel):
    goldenId: str
    description: str
    sourceJDLPath: str
    definitionHash: str
    versionFingerprint: VersionFingerprint
    expectedComponents: list[str]
    geometrySnapshot: GeometrySnapshot
    artifactExpectations: list[ArtifactExpectation] = Field(default_factory=list)
    baselineStatus: BaselineStatus
    knownLimitations: list[str] = Field(default_factory=list)
    createdAt: str
    acceptedAt: str | None = None
    notes: str = ""


class ExactChange(QualityModel):
    path: str
    expected: Any
    actual: Any


class NumericFactDiff(QualityModel):
    path: str
    expected: float
    actual: float
    absoluteDelta: float
    relativeDelta: float | None
    tolerance: float
    withinTolerance: bool


class RelationshipChange(QualityModel):
    componentA: str
    componentB: str
    field: str
    expected: Any
    actual: Any


class TopologyChange(QualityModel):
    componentId: str
    field: str
    expected: int
    actual: int


class ArtifactChange(QualityModel):
    artifactType: str
    description: str


class GeometryDiff(QualityModel):
    """A structured comparison result. `severity`/`requiresBaselineReview`
    are derived, never asserted directly — see
    docs/bible/17-geometry-quality/508-geometry-diff-model.md."""

    goldenId: str
    expectedFingerprint: VersionFingerprint
    actualFingerprint: VersionFingerprint
    exactChanges: list[ExactChange] = Field(default_factory=list)
    numericChanges: list[NumericFactDiff] = Field(default_factory=list)
    relationshipChanges: list[RelationshipChange] = Field(default_factory=list)
    topologyChanges: list[TopologyChange] = Field(default_factory=list)
    artifactChanges: list[ArtifactChange] = Field(default_factory=list)
    severity: DiffSeverity
    requiresBaselineReview: bool

    def human_readable(self) -> str:
        if self.severity == "NONE":
            return f"Golden: {self.goldenId}\nStatus: no regression detected."

        lines = [f"Golden: {self.goldenId}", f"Severity: {self.severity}"]
        for c in self.exactChanges:
            lines.append(
                f"Exact invariant changed: {c.path}\n  Expected: {c.expected}\n  Actual:   {c.actual}"
            )
        for n in self.numericChanges:
            status = "within tolerance" if n.withinTolerance else "REGRESSION"
            lines.append(
                f"Metric: {n.path}\n"
                f"  Expected: {n.expected}\n"
                f"  Actual:   {n.actual}\n"
                f"  Delta:    {n.absoluteDelta} (relative {n.relativeDelta})\n"
                f"  Tolerance: {n.tolerance}\n"
                f"  Status:   {status}"
            )
        for r in self.relationshipChanges:
            lines.append(
                f"Relationship changed: {r.componentA} <-> {r.componentB} ({r.field})\n"
                f"  Expected: {r.expected}\n"
                f"  Actual:   {r.actual}"
            )
        for t in self.topologyChanges:
            lines.append(
                f"Topology changed: {t.componentId}.{t.field}\n"
                f"  Expected: {t.expected}\n"
                f"  Actual:   {t.actual}"
            )
        for a in self.artifactChanges:
            lines.append(f"Artifact regression: {a.artifactType}\n  {a.description}")
        lines.append(f"Requires baseline review: {self.requiresBaselineReview}")
        return "\n".join(lines)


class QualityResult(QualityModel):
    goldenId: str
    status: QualityResultStatus
    diff: GeometryDiff | None = None
    message: str
