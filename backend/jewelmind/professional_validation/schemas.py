"""Data shapes for the Professional Validation Framework.

See docs/bible/15-professional-validation/412-validation-object-model.md
through 418-validation-decision-model.md. Every model here describes
structured evidence *about* a professional review — none of these types,
on their own, constitute validation; a `ValidationRecord` only means
anything once it names a real reviewer, real evidence, and a real
decision (PROVAL-GOV-001).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ReviewerRole = Literal[
    "JEWELRY_CAD_DESIGNER",
    "GOLDSMITH_BENCH_JEWELER",
    "STONE_SETTER",
    "CASTING_SPECIALIST",
    "RESIN_PRINTING_SPECIALIST",
    "JEWELRY_MANUFACTURING_ENGINEER",
    "GEMOLOGIST",
    "CAD_INTEROPERABILITY_SPECIALIST",
]

ReviewerVerificationStatus = Literal["UNVERIFIED", "SELF_ATTESTED", "VERIFIED"]

ValidationObjectType = Literal[
    "FORGE_RULE",
    "DOMAIN_STATEMENT",
    "GEOMETRY_COMPONENT",
    "GEOMETRY_RELATIONSHIP",
    "COMPLETE_MODEL",
    "MANUFACTURING_PROFILE",
    "MATERIAL_PROFILE",
    "SETTING_BEHAVIOUR",
    "EXPORT_WORKFLOW",
    "CAD_INTEROPERABILITY_WORKFLOW",
    "DESIGN_PROFILE",
]

EvidenceType = Literal[
    "LIVE_SOFTWARE_OBSERVATION",
    "CAD_FILE_INSPECTION",
    "STEP_IMPORT_INSPECTION",
    "STL_INSPECTION",
    "PHYSICAL_PRINT",
    "CAST_SAMPLE",
    "BENCH_WORK",
    "STONE_SETTING_TEST",
    "MEASUREMENT",
    "REFERENCE_DOCUMENT",
    "MANUFACTURER_GUIDANCE",
    "PROFESSIONAL_EXPERIENCE",
    "COMPARATIVE_CAD_MODEL",
    "PHOTO",
    "VIDEO",
    "ANNOTATED_SCREENSHOT",
    "WRITTEN_REVIEW",
]

EvidenceQualityClass = Literal[
    "DIRECT_PHYSICAL",
    "DIRECT_CAD",
    "DIRECT_WORKFLOW",
    "DOCUMENTED_REFERENCE",
    "PROFESSIONAL_JUDGMENT",
    "SOFTWARE_ONLY",
    "AI_ASSISTED",
]

ValidationDecisionType = Literal[
    "ACCEPTED",
    "ACCEPTED_WITH_CONDITIONS",
    "REJECTED",
    "INSUFFICIENT_EVIDENCE",
    "OUT_OF_SCOPE",
    "SUPERSEDED",
]

ValidationStatus = Literal[
    "NOT_REVIEWED",
    "REVIEW_PLANNED",
    "UNDER_REVIEW",
    "INSUFFICIENT_EVIDENCE",
    "VALIDATED",
    "VALIDATED_WITH_CONDITIONS",
    "REJECTED",
    "REVALIDATION_REQUIRED",
    "SUPERSEDED",
]

FindingSeverity = Literal["NOTE", "MINOR", "MODERATE", "MAJOR", "CRITICAL"]

DisagreementType = Literal[
    "AGREEMENT",
    "SCOPE_DIFFERENCE",
    "METHOD_DIFFERENCE",
    "PROFESSIONAL_DISAGREEMENT",
    "INSUFFICIENT_CONTEXT",
]

ImportOutcome = Literal[
    "IMPORT_SUCCESS",
    "IMPORT_WITH_WARNINGS",
    "IMPORT_FAILURE",
    "EDITABLE_WITHOUT_REBUILD",
    "EDITABLE_WITH_REWORK",
    "REQUIRES_SUBSTANTIAL_REBUILD",
]


class ProvalModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ReviewerQualification(ProvalModel):
    """Fit-for-review, not a prestige score (PROVAL-GOV-004). No field here
    invents a credentialing standard that doesn't exist."""

    reviewerId: str
    role: ReviewerRole
    yearsOfExperience: float | None = None
    professionalFocus: str
    processes: list[str] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    softwareExperience: list[str] = Field(default_factory=list)
    relevantPortfolioOrEvidence: str | None = None
    geographicPractice: str | None = None
    qualificationNotes: str = ""
    verificationStatus: ReviewerVerificationStatus = "UNVERIFIED"


class ValidationScope(ProvalModel):
    """A record's scope is never broader than the evidence supports
    (PROVAL-GOV-015/016/017/018). Every field is optional — a scope only
    states what it actually constrains."""

    jewelryCategory: str | None = None
    ringStyle: str | None = None
    component: str | None = None
    material: str | None = None
    alloy: str | None = None
    manufacturingMethod: str | None = None
    stoneShape: str | None = None
    stoneDimensionRangeMm: str | None = None
    settingType: str | None = None
    sizeRange: str | None = None
    cadApplication: str | None = None
    exporterVersion: str | None = None
    forgeRuleVersion: str | None = None
    atlasVersion: str | None = None
    jdlVersion: str | None = None
    geographicOrWorkshopConstraints: str | None = None


class ValidationTarget(ProvalModel):
    objectType: ValidationObjectType
    objectId: str
    version: str
    description: str
    implementationReferences: list[str] = Field(default_factory=list)
    relatedTests: list[str] = Field(default_factory=list)
    currentValidationStatus: ValidationStatus = "NOT_REVIEWED"


class ValidationEvidence(ProvalModel):
    evidenceId: str
    type: EvidenceType
    qualityClass: EvidenceQualityClass
    source: str
    date: str
    relatedReviewCaseId: str | None = None
    description: str
    fileOrReference: str | None = None
    limitations: str = ""


class ReviewObservation(ProvalModel):
    observationId: str
    caseId: str
    reviewerId: str
    target: str
    category: str
    severity: FindingSeverity
    observation: str
    evidenceIds: list[str] = Field(default_factory=list)
    suggestedChange: str | None = None
    blockingRecommendation: bool = False
    confidence: str | None = None
    scope: ValidationScope = Field(default_factory=ValidationScope)
    relatedRuleIds: list[str] = Field(default_factory=list)
    relatedComponentIds: list[str] = Field(default_factory=list)


class ValidationDecision(ProvalModel):
    decision: ValidationDecisionType
    reviewerId: str
    statementValidated: str
    conditions: str | None = None
    rationale: str
    scope: ValidationScope = Field(default_factory=ValidationScope)
    evidenceIds: list[str] = Field(default_factory=list)
    reviewDate: str
    revalidationTrigger: str | None = None


class ReviewCase(ProvalModel):
    """Must be reproducible: given the same JDL and the same pinned
    Forge/Atlas/JDL versions, regenerating this case's artifacts produces
    the same definitionHash and the same geometry."""

    caseId: str
    purpose: str
    jdlDocument: dict = Field(default_factory=dict)
    definitionHash: str
    compilationFingerprint: str | None = None
    forgeRuleSetVersion: str
    atlasVersion: str
    exportedArtifacts: list[str] = Field(default_factory=list)
    expectedQuestions: list[str] = Field(default_factory=list)
    reviewScope: ValidationScope = Field(default_factory=ValidationScope)
    evidenceGeneratedIds: list[str] = Field(default_factory=list)


class ReviewSession(ProvalModel):
    sessionId: str
    date: str
    reviewerId: str
    reviewType: str
    scope: ValidationScope = Field(default_factory=ValidationScope)
    jewelmindVersions: dict[str, str] = Field(default_factory=dict)
    reviewedCaseIds: list[str] = Field(default_factory=list)
    evidenceIds: list[str] = Field(default_factory=list)
    observationIds: list[str] = Field(default_factory=list)
    decisionIds: list[str] = Field(default_factory=list)
    unresolvedQuestions: list[str] = Field(default_factory=list)
    followUpRequired: bool = False


class ValidationRecord(ProvalModel):
    """The one artifact that can ever claim professional validation
    occurred — and only when `isTemplate` is False and it lives in the
    active registry file, never an examples/fixtures directory
    (registry.py enforces both). PROVAL-GOV-001/002/003."""

    recordId: str
    target: ValidationTarget
    scope: ValidationScope = Field(default_factory=ValidationScope)
    reviewerId: str
    sessionId: str | None = None
    decision: ValidationDecisionType
    status: ValidationStatus
    evidenceIds: list[str] = Field(default_factory=list)
    conditions: str | None = None
    rationale: str
    reviewDate: str
    expirationOrReviewTrigger: str | None = None
    supersedesRecordId: str | None = None
    isTemplate: bool = False


class DisagreementRecord(ProvalModel):
    disagreementId: str
    objectId: str
    type: DisagreementType
    recordIds: list[str] = Field(default_factory=list)
    description: str


class ReviewPackageFile(ProvalModel):
    name: str
    sha256: str
    sizeBytes: int


class ReviewPackageManifest(ProvalModel):
    packageId: str
    caseId: str
    generatedAt: str
    sourceDefinitionHash: str
    jdlVersion: str
    compilerVersion: str | None = None
    forgeVersion: str | None = None
    atlasVersion: str | None = None
    includedFiles: list[ReviewPackageFile] = Field(default_factory=list)
    checksums: dict[str, str] = Field(default_factory=dict)
    missingOptionalFiles: list[str] = Field(default_factory=list)
    knownLimitations: list[str] = Field(default_factory=list)
