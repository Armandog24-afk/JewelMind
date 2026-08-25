"""Designer data shapes.

Pydantic models for every concept in the Designer contract: the incoming
natural-language request, the raw constrained structured output a provider
must return, and the outgoing `DesignerProposal`/`DesignerResult`. See
docs/bible/12-designer/294-design-proposal-model.md and
295-designer-to-jdl-contract.md.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.validation.rules import ValidationResult

SupportedLocale = Literal["it", "en"]
InteractionMode = Literal["CREATE", "MODIFY"]

FieldProvenance = Literal[
    "USER_EXPLICIT",
    "USER_CONTEXT",
    "CURRENT_DESIGN",
    "SYSTEM_DEFAULT",
    "DETERMINISTIC_DERIVATION",
    "AI_INTERPRETATION",
    "CLARIFICATION_RESPONSE",
    "UNRESOLVED",
]

ConfidenceCategory = Literal[
    "EXACT",
    "NORMALIZED",
    "INFERRED",
    "DEFAULTED",
    "AMBIGUOUS",
    "UNSUPPORTED",
]

AmbiguityLevel = Literal[
    "LOW_IMPACT_AMBIGUITY",
    "HIGH_IMPACT_AMBIGUITY",
    "UNSUPPORTED_AMBIGUITY",
]

ProposalStatus = Literal[
    "COMPLETE",
    "NEEDS_CLARIFICATION",
    "PARTIALLY_SUPPORTED",
    "UNSUPPORTED",
    "INVALID",
    "READY_FOR_REVIEW",
    "ACCEPTED",
    "REJECTED",
]

DiagnosticCode = Literal[
    "DESIGNER_UNSUPPORTED_FEATURE",
    "DESIGNER_AMBIGUOUS_REQUEST",
    "DESIGNER_CLARIFICATION_REQUIRED",
    "DESIGNER_PROPOSAL_INVALID",
    "DESIGNER_CAPABILITY_MISMATCH",
]

DiagnosticSeverity = Literal["info", "warning", "error"]


class DesignerModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --- Inbound request -------------------------------------------------------


class NaturalLanguageDesignRequest(DesignerModel):
    requestId: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=2000)
    locale: SupportedLocale | None = None
    interactionMode: InteractionMode = "CREATE"
    currentJDL: JewelryDefinition | None = None


# --- Raw provider output (constrained structured output contract) ---------


class RawProposedValue(DesignerModel):
    """One field the provider believes the user specified or implied.

    `field` is a dotted JDL path (e.g. ``material.metal``); `value` is
    whatever token the provider extracted — normalization into a real
    canonical enum/number happens deterministically in normalizer.py,
    never trusted as already-correct from the provider itself.
    """

    field: str
    value: str | float | int | bool
    sourceText: str = ""


class RawUnsupportedFeature(DesignerModel):
    feature: str
    sourceText: str = ""
    suggestedSupportedAlternative: str | None = None


class RawAmbiguity(DesignerModel):
    field: str
    sourceText: str = ""
    candidateValues: list[str] = Field(default_factory=list)


class RawClarification(DesignerModel):
    field: str | None = None
    question: str
    options: list[str] = Field(default_factory=list)


class RawDesignerResponse(DesignerModel):
    """The exact shape a provider's structured output must validate against.

    JewelMind's own deterministic code (service.py/normalizer.py), never
    the provider, turns this into a candidate JDL — see
    305-structured-output-contract.md.
    """

    proposedCanonicalValues: list[RawProposedValue] = Field(default_factory=list)
    unresolvedDescriptors: list[str] = Field(default_factory=list)
    detectedUnsupportedFeatures: list[RawUnsupportedFeature] = Field(default_factory=list)
    ambiguities: list[RawAmbiguity] = Field(default_factory=list)
    clarificationCandidates: list[RawClarification] = Field(default_factory=list)


# --- Outbound proposal ------------------------------------------------------


class ProposedField(DesignerModel):
    path: str
    value: str | float | int | bool
    provenance: FieldProvenance
    confidence: ConfidenceCategory
    sourceText: str | None = None
    previousValue: str | float | int | bool | None = None


class ClarificationQuestion(DesignerModel):
    field: str | None = None
    question: str
    options: list[str] = Field(default_factory=list)
    ambiguityLevel: AmbiguityLevel


class UnsupportedFeature(DesignerModel):
    feature: str
    sourceText: str
    reason: str
    currentCapability: str | None = None
    futureRoadmapReference: str | None = None
    blocking: bool = True
    suggestedSupportedAlternative: str | None = None


class DesignerDiagnostic(DesignerModel):
    code: DiagnosticCode
    severity: DiagnosticSeverity
    message: str
    field: str | None = None


class ForgeEvaluationSummary(DesignerModel):
    results: list[ValidationResult]
    hasErrors: bool


class FieldDiff(DesignerModel):
    path: str
    previousValue: str | float | int | bool | None
    proposedValue: str | float | int | bool | None
    changed: bool


class DesignerProposal(DesignerModel):
    proposalId: str
    sourceText: str
    interactionMode: InteractionMode
    unresolvedIntent: list[str] = Field(default_factory=list)
    unsupportedFeatures: list[UnsupportedFeature] = Field(default_factory=list)
    proposedFields: list[ProposedField] = Field(default_factory=list)
    clarificationQuestions: list[ClarificationQuestion] = Field(default_factory=list)
    diagnostics: list[DesignerDiagnostic] = Field(default_factory=list)
    candidateJDL: JewelryDefinition | None = None
    validation: list[ValidationResult] = Field(default_factory=list)
    forgeEvaluation: ForgeEvaluationSummary | None = None
    diff: list[FieldDiff] = Field(default_factory=list)
    proposalStatus: ProposalStatus


class DesignerResult(DesignerModel):
    requestId: str
    proposal: DesignerProposal
