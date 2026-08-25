"""Design Intent data shapes.

See docs/bible/13-design-intent/332-intent-domain-model.md. Every field
here exists to keep subjective language structured without letting it
silently become a numeric geometry parameter — see
docs/bible/13-design-intent/330-intent-governance.md, INTENT-GOV-001.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

IntentTarget = Literal[
    "JEWELRY_PRODUCT",
    "RING",
    "BAND",
    "STONE",
    "SETTING",
    "PRONGS",
    "BASKET",
    "MATERIAL_APPEARANCE",
    "OVERALL_PROPORTION",
    "VISUAL_HIERARCHY",
]

IntentConceptCategory = Literal[
    "VISUAL_WEIGHT",
    "SIMPLICITY",
    "STYLE_TEMPORALITY",
    "VISUAL_EMPHASIS",
    "PROPORTIONAL_CHARACTER",
    "STRUCTURAL_CHARACTER",
]

IntentStrength = Literal["OPTIONAL", "PREFERRED", "IMPORTANT", "REQUIRED"]

IntentProvenance = Literal[
    "USER_EXPLICIT",
    "USER_CONTEXT",
    "AI_NORMALIZED",
    "SYSTEM_PROFILE",
    "EXISTING_PROJECT",
    "CLARIFICATION_RESPONSE",
    "DERIVED_RELATION",
    "UNRESOLVED",
]

IntentConfidence = Literal[
    "EXACT",
    "HIGH_CONFIDENCE_NORMALIZATION",
    "AMBIGUOUS",
    "INFERRED",
    "UNRESOLVED",
]

ResolutionStatus = Literal[
    "UNRESOLVED",
    "PRESERVED",
    "DETERMINISTICALLY_RESOLVED",
    "USER_RESOLVED",
    "PROFILE_RESOLVED",
    "UNSUPPORTED",
    "CONFLICTING",
]

ConflictType = Literal[
    "EXPLICIT_CONTRADICTION",
    "SOFT_TENSION",
    "TARGET_CONFLICT",
    "PRIORITY_CONFLICT",
    "RESOLUTION_CONFLICT",
]

IntentDiagnosticCode = Literal[
    "INTENT_UNKNOWN_DESCRIPTOR",
    "INTENT_AMBIGUOUS_DESCRIPTOR",
    "INTENT_CONFLICT",
    "INTENT_UNSUPPORTED_TARGET",
    "INTENT_NO_DETERMINISTIC_RESOLUTION",
    "INTENT_PROFILE_UNAVAILABLE",
    "INTENT_RESOLUTION_REQUIRES_CONFIRMATION",
    "INTENT_INVALID_RELATION",
    "INTENT_PRESERVED_UNRESOLVED",
]

RelationPredicate = Literal[
    "NARROWER_THAN",
    "BROADER_THAN",
    "DOMINANT_OVER",
    "SUBORDINATE_TO",
    "DISCREET_RELATIVE_TO",
    "BALANCED_WITH",
]


class IntentModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IntentStatement(IntentModel):
    intentId: str
    target: IntentTarget
    concept: IntentConceptCategory
    value: str
    strength: IntentStrength = "PREFERRED"
    priority: int = 0
    provenance: IntentProvenance
    confidenceClass: IntentConfidence
    sourceText: str
    resolutionStatus: ResolutionStatus
    relatedJDLPaths: list[str] = Field(default_factory=list)
    diagnostics: list[str] = Field(default_factory=list)


class IntentRelation(IntentModel):
    relationId: str
    subject: IntentTarget
    predicate: RelationPredicate
    object: IntentTarget
    strength: IntentStrength = "PREFERRED"
    provenance: IntentProvenance
    resolutionStatus: ResolutionStatus
    sourceText: str = ""


class IntentConflict(IntentModel):
    conflictId: str
    type: ConflictType
    statementIds: list[str] = Field(default_factory=list)
    description: str


class IntentDiagnostic(IntentModel):
    code: IntentDiagnosticCode
    severity: Literal["info", "warning", "error"]
    message: str
    statementId: str | None = None


class DesignIntent(IntentModel):
    version: str = "1.0.0"
    sourceText: str
    statements: list[IntentStatement] = Field(default_factory=list)
    relationships: list[IntentRelation] = Field(default_factory=list)
    unresolvedDescriptors: list[str] = Field(default_factory=list)
    conflicts: list[IntentConflict] = Field(default_factory=list)
    profile: str | None = None
    diagnostics: list[IntentDiagnostic] = Field(default_factory=list)


class IntentResolution(IntentModel):
    """A record of how one IntentStatement was, or wasn't, resolved.

    Not currently persisted anywhere — see
    docs/bible/13-design-intent/348-intent-resolution-model.md. Modeled now
    so a future profile-driven resolution step has a real target shape to
    write into, per INTENT-GOV-018.
    """

    intentId: str
    status: ResolutionStatus
    resultingJDLChanges: list[str] = Field(default_factory=list)
    resolutionMethod: Literal["NONE", "DETERMINISTIC_RULE", "USER_CONFIRMATION", "PROFILE"] = "NONE"
    ruleOrProfile: str | None = None
    userConfirmationRequired: bool = False
    notes: str = ""


class IntentDiffEntry(IntentModel):
    key: str
    previousValue: str | None = None
    newValue: str | None = None
    changeType: Literal["ADDED", "REMOVED", "CHANGED", "UNCHANGED"]


class IntentProfile(IntentModel):
    """A future, versioned, deterministic intent-to-JDL mapping.

    No profile is registered in v1 — see
    docs/bible/13-design-intent/355-intent-profile-model.md and
    349-deterministic-resolution-policy.md for why zero automatic
    subjective-to-numeric mappings is the correct, deliberate v1 state.
    """

    profileId: str
    version: str
    supportedDomain: str
    resolvedIntent: list[str] = Field(default_factory=list)
    jdlMapping: dict[str, float | str] = Field(default_factory=dict)
    provenance: str
    professionalReview: Literal["not_required", "preliminary", "required", "validated"] = "not_required"
    deterministicMapping: bool = True
    applicableCapabilityVersion: str = "0.1.0"
