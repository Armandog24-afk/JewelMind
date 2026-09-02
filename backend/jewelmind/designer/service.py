"""Designer orchestration — the full deterministic interpretation pipeline.

Raw provider output -> enum normalization -> field/capability validation ->
provenance + confidence tagging -> unsupported-feature/ambiguity handling ->
candidate JDL construction -> JDL/Pydantic validation -> Forge evaluation ->
diff -> proposal status. No AI output reaches a candidate JDL without
passing through every one of these steps — see
docs/bible/12-designer/308-designer-validation-pipeline.md.
"""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import ValidationError

from jewelmind.api.errors import AppError
from jewelmind.design_intent.resolver import RawRelationInput, RawStatementInput, build_design_intent
from jewelmind.designer import capability, normalizer
from jewelmind.designer.errors import (
    DESIGNER_AMBIGUOUS_REQUEST,
    DESIGNER_CAPABILITY_MISMATCH,
    DESIGNER_CLARIFICATION_REQUIRED,
    DESIGNER_PROPOSAL_INVALID,
    DESIGNER_UNSUPPORTED_FEATURE,
    DesignerProviderError,
    DesignerProviderUnavailableError,
    DesignerSecurityRejectedError,
)
from jewelmind.designer.provider import DesignerContext, DesignerProvider
from jewelmind.designer.schemas import (
    ClarificationQuestion,
    DesignerDiagnostic,
    DesignerProposal,
    DesignerResult,
    ForgeEvaluationSummary,
    NaturalLanguageDesignRequest,
    ProposedField,
    RawDesignerResponse,
    UnsupportedFeature,
)
from jewelmind.domain.schema import JewelryDefinition
from jewelmind.validation.engine import has_errors, validate_definition

#: The dimensions each stone shape needs, and the question to ask when one is
#: missing. Derived from the Stone System registry so a new shape's requirements
#: cannot drift from what the schema actually enforces.
_STONE_DIMENSION_QUESTIONS: dict[str, str] = {
    "diameter": "What diameter should the stone be, in millimetres?",
    "length": "What length should the stone be, in millimetres?",
    "width": "What width should the stone be, in millimetres?",
    "narrowWidth": (
        "This shape is tapered. What should its narrow-end width be, in "
        "millimetres?"
    ),
}


def _missing_stone_dimensions(patch: dict[str, Any]) -> list[tuple[str, str]]:
    """Which stone dimensions a proposed shape needs but the patch omits.

    Returns `(field path, question)` pairs. Never fills a dimension in — the
    whole point is that JewelMind asks instead of inventing a proportion
    (brief section 39).
    """

    from jewelmind.stone.capability import get_shape_capability

    shape = patch.get("stone.shape")
    if not isinstance(shape, str):
        return []

    entry = get_shape_capability(shape)
    if entry is None:
        return []

    questions: list[tuple[str, str]] = []
    for dimension in entry.requiredDimensions:
        # `depth` always has a usable schema default, and `outline` is not a
        # numeric dimension a user can answer in one value.
        if dimension in ("depth", "outline"):
            continue
        path = f"stone.{dimension}"
        if path in patch:
            continue
        question = _STONE_DIMENSION_QUESTIONS.get(dimension)
        if question is not None:
            questions.append((path, question))
    return questions


def _apply_patch(base: JewelryDefinition, patch: dict[str, Any]) -> JewelryDefinition | None:
    data = base.model_dump(mode="python")
    for path, value in patch.items():
        section, field_name = path.split(".", 1)
        data.setdefault(section, {})[field_name] = value
    try:
        return JewelryDefinition.model_validate(data)
    except ValidationError:
        return None


class DesignerService:
    def __init__(self, provider: DesignerProvider | None) -> None:
        self._provider = provider

    def interpret(self, request: NaturalLanguageDesignRequest) -> DesignerResult:
        injection_reason = normalizer.detect_prompt_injection_risk(request.text)
        if injection_reason is not None:
            raise DesignerSecurityRejectedError(injection_reason)

        if self._provider is None:
            raise DesignerProviderUnavailableError(
                "No Designer AI provider is configured for this backend process."
            )

        base = (
            JewelryDefinition()
            if request.interactionMode == "CREATE"
            else (request.currentJDL or JewelryDefinition())
        )
        context = DesignerContext(
            currentJDL=base,
            interactionMode=request.interactionMode,
            currentDesignIntent=request.currentDesignIntent,
        )

        try:
            raw = self._provider.interpret(request, context)
        except AppError:
            # Already one of DesignerProviderTimeoutError/DesignerProviderError/
            # DesignerInvalidResponseError/DesignerSchemaViolationError (see
            # AnthropicDesignerProvider) — propagate the specific code as-is.
            raise
        except Exception as exc:  # noqa: BLE001 - anything else is a generic provider error
            raise DesignerProviderError(f"Designer provider failed: {exc}") from exc

        proposal = self._build_proposal(request, base, raw)
        return DesignerResult(requestId=request.requestId, proposal=proposal)

    def _build_proposal(
        self,
        request: NaturalLanguageDesignRequest,
        base: JewelryDefinition,
        raw: RawDesignerResponse,
    ) -> DesignerProposal:
        capabilities = capability.current_capabilities()
        proposed_fields: list[ProposedField] = []
        unsupported_features: list[UnsupportedFeature] = []
        clarification_questions: list[ClarificationQuestion] = []
        diagnostics: list[DesignerDiagnostic] = []
        patch: dict[str, Any] = {}

        for pv in raw.proposedCanonicalValues:
            path = pv.field
            if not capability.is_known_field(path):
                diagnostics.append(
                    DesignerDiagnostic(
                        code=DESIGNER_CAPABILITY_MISMATCH,
                        severity="warning",
                        message=f"'{path}' is not a JDL field JewelMind recognizes; ignored.",
                        field=path,
                    )
                )
                continue

            enum_key = capability.enum_capability_key(path)
            if enum_key is not None:
                normalized, is_ambiguous = normalizer.normalize_enum_token(path, str(pv.value))
                if is_ambiguous:
                    clarification_questions.append(
                        ClarificationQuestion(
                            field=path,
                            question=(
                                f"You asked for '{pv.value}'. Which supported option do you mean?"
                            ),
                            options=[str(v) for v in capabilities.get(enum_key, [])],
                            ambiguityLevel="HIGH_IMPACT_AMBIGUITY",
                        )
                    )
                    diagnostics.append(
                        DesignerDiagnostic(
                            code=DESIGNER_AMBIGUOUS_REQUEST,
                            severity="info",
                            message=f"'{pv.value}' does not identify one supported value for {path}.",
                            field=path,
                        )
                    )
                    continue
                if normalized is None:
                    reason = capability.KNOWN_UNSUPPORTED_CONCEPTS.get(
                        str(pv.value).strip().lower(),
                        f"'{pv.value}' is not a supported value for {path}.",
                    )
                    unsupported_features.append(
                        UnsupportedFeature(
                            feature=str(pv.value),
                            sourceText=pv.sourceText,
                            reason=reason,
                            currentCapability=", ".join(str(v) for v in capabilities.get(enum_key, [])),
                            blocking=True,
                        )
                    )
                    diagnostics.append(
                        DesignerDiagnostic(
                            code=DESIGNER_UNSUPPORTED_FEATURE,
                            severity="warning",
                            message=reason,
                            field=path,
                        )
                    )
                    continue

                value: Any = int(normalized) if path == "setting.prongCount" else normalized
                already_canonical = str(pv.value).strip().lower() == str(value).strip().lower()
                confidence = "EXACT" if already_canonical else "NORMALIZED"
                proposed_fields.append(
                    ProposedField(
                        path=path,
                        value=value,
                        provenance="AI_INTERPRETATION",
                        confidence=confidence,
                        sourceText=pv.sourceText or None,
                    )
                )
                patch[path] = value
                continue

            if path == "project.name":
                proposed_fields.append(
                    ProposedField(
                        path=path,
                        value=str(pv.value),
                        provenance="AI_INTERPRETATION",
                        confidence="EXACT",
                        sourceText=pv.sourceText or None,
                    )
                )
                patch[path] = str(pv.value)
                continue

            if normalizer.is_numeric_field(path):
                try:
                    numeric_value = float(pv.value)
                except (TypeError, ValueError):
                    diagnostics.append(
                        DesignerDiagnostic(
                            code=DESIGNER_PROPOSAL_INVALID,
                            severity="warning",
                            message=f"'{pv.value}' is not a numeric value for {path}; ignored.",
                            field=path,
                        )
                    )
                    continue
                proposed_fields.append(
                    ProposedField(
                        path=path,
                        value=numeric_value,
                        provenance="AI_INTERPRETATION",
                        confidence="INFERRED",
                        sourceText=pv.sourceText or None,
                    )
                )
                patch[path] = numeric_value

        for amb in raw.ambiguities:
            level = (
                "HIGH_IMPACT_AMBIGUITY"
                if capability.is_known_field(amb.field)
                else "UNSUPPORTED_AMBIGUITY"
            )
            reference = amb.sourceText or amb.field
            clarification_questions.append(
                ClarificationQuestion(
                    field=amb.field,
                    question=f"'{reference}' could mean more than one supported thing — which do you mean?",
                    options=amb.candidateValues,
                    ambiguityLevel=level,
                )
            )
            diagnostics.append(
                DesignerDiagnostic(
                    code=DESIGNER_AMBIGUOUS_REQUEST,
                    severity="info",
                    message=f"Ambiguous reference for {amb.field}.",
                    field=amb.field,
                )
            )

        for feat in raw.detectedUnsupportedFeatures:
            unsupported_features.append(
                UnsupportedFeature(
                    feature=feat.feature,
                    sourceText=feat.sourceText,
                    reason=f"'{feat.feature}' is not currently supported by JewelMind.",
                    suggestedSupportedAlternative=feat.suggestedSupportedAlternative,
                    blocking=True,
                )
            )
            diagnostics.append(
                DesignerDiagnostic(
                    code=DESIGNER_UNSUPPORTED_FEATURE,
                    severity="warning",
                    message=f"Requested feature '{feat.feature}' is not currently supported.",
                )
            )

        for clar in raw.clarificationCandidates:
            clarification_questions.append(
                ClarificationQuestion(
                    field=clar.field,
                    question=clar.question,
                    options=clar.options,
                    ambiguityLevel="HIGH_IMPACT_AMBIGUITY" if clar.options else "UNSUPPORTED_AMBIGUITY",
                )
            )
            diagnostics.append(
                DesignerDiagnostic(
                    code=DESIGNER_CLARIFICATION_REQUIRED,
                    severity="info",
                    message=clar.question,
                    field=clar.field,
                )
            )

        unresolved_intent = list(raw.unresolvedDescriptors)

        design_intent = build_design_intent(
            source_text=request.text,
            mode=request.interactionMode,
            previous=request.currentDesignIntent,
            raw_statements=[
                RawStatementInput(
                    target=s.target,
                    concept=s.concept,
                    value=s.value,
                    strength=s.strength,
                    sourceText=s.sourceText or s.value,
                )
                for s in raw.designIntentStatements
            ],
            raw_relations=[
                RawRelationInput(
                    subject=r.subject,
                    predicate=r.predicate,
                    object=r.object,
                    strength=r.strength,
                    sourceText=r.sourceText,
                )
                for r in raw.designIntentRelations
            ],
            raw_unresolved_descriptors=list(raw.unresolvedDescriptors),
        )

        candidate = _apply_patch(base, patch) if patch or request.interactionMode == "CREATE" else base

        if candidate is None:
            # A shape that needs dimensions the request never supplied is the
            # commonest way to land here, and it deserves a QUESTION rather than
            # a dead end. Brief section 39 is explicit: JewelMind must not infer
            # that a heart is 8 x 8mm, so the honest response to a missing
            # dimension is to ask for it (STONEV2-GOV-006's discipline applied
            # to natural language).
            missing = _missing_stone_dimensions(patch)
            for field_path, question in missing:
                clarification_questions.append(
                    ClarificationQuestion(
                        field=field_path,
                        question=question,
                        options=[],
                        ambiguityLevel="HIGH_IMPACT_AMBIGUITY",
                    )
                )
            diagnostics.append(
                DesignerDiagnostic(
                    code=DESIGNER_PROPOSAL_INVALID,
                    severity="error",
                    message=(
                        "The proposed values could not form a valid design "
                        "definition; the stone's required dimensions are missing."
                        if missing
                        else "The proposed values could not form a valid design definition."
                    ),
                )
            )
            validation: list = []
            forge_evaluation = None
            diff: list = []
            status = "INVALID"
        else:
            validation = validate_definition(candidate)
            forge_evaluation = ForgeEvaluationSummary(results=validation, hasErrors=has_errors(validation))
            # Compared against whatever the caller says is currently loaded,
            # regardless of interactionMode — CREATE's `base` still starts
            # from schema defaults (unaffected), but the diff itself always
            # reflects "what would actually change in the design currently
            # open in Studio," which is what the frontend uses to decide
            # whether applying this proposal should mark the model stale
            # (see docs/bible/13-design-intent/353-intent-preservation.md).
            diff = normalizer.compute_diff(request.currentJDL, candidate)
            status = self._resolve_status(
                clarification_questions, unsupported_features, proposed_fields, unresolved_intent
            )

        return DesignerProposal(
            proposalId=f"proposal-{uuid.uuid4()}",
            sourceText=request.text,
            interactionMode=request.interactionMode,
            unresolvedIntent=unresolved_intent,
            unsupportedFeatures=unsupported_features,
            proposedFields=proposed_fields,
            clarificationQuestions=clarification_questions,
            diagnostics=diagnostics,
            candidateJDL=candidate,
            validation=validation,
            forgeEvaluation=forge_evaluation,
            diff=diff,
            proposalStatus=status,
            designIntent=design_intent,
        )

    @staticmethod
    def _resolve_status(
        clarification_questions: list[ClarificationQuestion],
        unsupported_features: list[UnsupportedFeature],
        proposed_fields: list[ProposedField],
        unresolved_intent: list[str],
    ) -> str:
        if clarification_questions:
            return "NEEDS_CLARIFICATION"
        if unsupported_features and not proposed_fields:
            return "UNSUPPORTED"
        if unsupported_features:
            return "PARTIALLY_SUPPORTED"
        if unresolved_intent or any(f.confidence in ("INFERRED", "DEFAULTED") for f in proposed_fields):
            return "READY_FOR_REVIEW"
        return "COMPLETE"
