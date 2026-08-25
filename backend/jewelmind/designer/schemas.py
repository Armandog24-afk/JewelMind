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

from jewelmind.design_intent.schemas import DesignIntent
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
    # Sprint 11 (Design Intent Model v1) — the current, previously-preserved
    # DesignIntent, required for a meaningful MODIFY merge (see
    # jewelmind.design_intent.resolver.build_design_intent) and ignored for
    # CREATE, exactly parallel to currentJDL.
    currentDesignIntent: DesignIntent | None = None


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


class RawIntentStatement(DesignerModel):
    """One aesthetic (non-technical) descriptor the provider extracted.

    `target`/`concept` are the provider's classification of what the
    descriptor is about and which of the 6 controlled concept categories
    it belongs to — see docs/bible/13-design-intent/356-designer-intent-extraction.md.
    Re-validated deterministically against the real vocabulary in
    `jewelmind.design_intent.normalizer`, never trusted as-is.
    """

    target: str
    concept: str
    value: str
    strength: str | None = None
    sourceText: str = ""


class RawIntentRelation(DesignerModel):
    subject: str
    predicate: str
    object: str
    strength: str | None = None
    sourceText: str = ""


class RawDesignerResponse(DesignerModel):
    """The exact shape a provider's structured output must validate against.

    JewelMind's own deterministic code (service.py/normalizer.py), never
    the provider, turns this into a candidate JDL — see
    305-structured-output-contract.md. `designIntentStatements`/
    `designIntentRelations` (Sprint 11) are the provider's separated-out
    aesthetic intent — see 332-intent-domain-model.md.
    """

    proposedCanonicalValues: list[RawProposedValue] = Field(default_factory=list)
    unresolvedDescriptors: list[str] = Field(default_factory=list)
    designIntentStatements: list[RawIntentStatement] = Field(default_factory=list)
    designIntentRelations: list[RawIntentRelation] = Field(default_factory=list)
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
    # Kept for backwards compatibility with Sprint 10 — a mirror of
    # `designIntent.unresolvedDescriptors` (see build_proposal's
    # construction). New code should read `designIntent` instead.
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
    # Sprint 11 (Design Intent Model v1) — the aesthetic intent separated
    # out of this same request, always present (possibly empty), never
    # merged into candidateJDL — see 350-intent-to-jdl-boundary.md.
    designIntent: DesignIntent


class DesignerResult(DesignerModel):
    requestId: str
    proposal: DesignerProposal
