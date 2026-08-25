"""Conversation orchestration.

`ConversationEngine` coordinates interaction state around the existing
`DesignerService` (Sprint 10) — it never duplicates Designer's technical
extraction, unsupported-feature detection, field provenance, or JDL
proposal construction (docs/bible/14-conversation/391-conversation-designer-integration.md).
The backend stays stateless per request, exactly like Designer: accepting
a proposal here only confirms it is safe to apply and returns the
already-computed candidate JDL/DesignIntent for the caller to apply via
the same `useProjectStore.applyDesignerProposal()`/
`useDesignIntentStore.applyIntent()` paths Designer's own UI already
uses — the backend never mutates a stored design itself.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from jewelmind.api.errors import AppError
from jewelmind.conversation import clarifications, state
from jewelmind.conversation import references as reference_resolution
from jewelmind.conversation.actions import classify_action
from jewelmind.conversation.errors import (
    CONVERSATION_CLARIFICATION_INVALID,
    ConversationInvalidStateError,
    ConversationNoPendingClarificationError,
    ConversationProviderFailedError,
    ConversationStaleContextError,
)
from jewelmind.conversation.schemas import (
    ConversationActionType,
    ConversationDiagnostic,
    ConversationResult,
    ConversationSession,
    ConversationTurn,
    ConversationTurnRequest,
)
from jewelmind.designer import normalizer as designer_normalizer
from jewelmind.designer.errors import DesignerSecurityRejectedError
from jewelmind.designer.schemas import DesignerProposal, NaturalLanguageDesignRequest
from jewelmind.designer.service import DesignerService

_KNOWN_TARGETS = (
    "RING", "BAND", "STONE", "SETTING", "PRONGS", "BASKET",
    "MATERIAL_APPEARANCE", "OVERALL_PROPORTION", "VISUAL_HIERARCHY", "JEWELRY_PRODUCT",
)


def _now() -> str:
    return datetime.now(UTC).isoformat()


class ConversationEngine:
    def __init__(self, designer_service: DesignerService) -> None:
        self._designer = designer_service

    def process_turn(self, request: ConversationTurnRequest) -> ConversationResult:
        injection_reason = designer_normalizer.detect_prompt_injection_risk(request.text)
        if injection_reason is not None:
            raise DesignerSecurityRejectedError(injection_reason)

        now = _now()
        session = request.session or state.new_session(request.currentJDL, request.currentDesignIntent, now)
        state.refresh_hashes(session, request.currentJDL, request.currentDesignIntent)

        action = classify_action(request.text, session)
        turn_id = f"turn-{uuid.uuid4()}"

        if action == "ANSWER_CLARIFICATION":
            turn = self._handle_answer_clarification(turn_id, request, session, now)
        elif action == "ACCEPT_PROPOSAL":
            turn = self._handle_accept(turn_id, request, session, now)
        elif action == "REJECT_PROPOSAL":
            turn = self._handle_reject(turn_id, request, session, now)
        elif action == "CANCEL_INTERACTION":
            turn = self._handle_cancel(turn_id, request, session, now)
        elif action == "NO_CHANGE":
            turn = self._make_turn(turn_id, request, session, now, "NO_CHANGE", "No design change requested.")
        else:
            turn = self._handle_designer_routed(turn_id, request, session, now, action)

        session.turns.append(turn)
        session.updatedAt = now
        return ConversationResult(session=session, turn=turn)

    # --- action handlers -----------------------------------------------

    def _handle_designer_routed(
        self,
        turn_id: str,
        request: ConversationTurnRequest,
        session: ConversationSession,
        now: str,
        action: ConversationActionType,
    ) -> ConversationTurn:
        short_message = len(request.text.split()) <= 6
        preserve_target = reference_resolution.find_preserve_target(request.text) if short_message else None
        if preserve_target is not None and action != "CREATE_DESIGN_PROPOSAL":
            session.lastReferencedTarget = preserve_target
            label = preserve_target.title().replace("_", " ")
            return self._make_turn(
                turn_id, request, session, now, "PRESERVE_TARGET",
                f"{label} preserved — no changes requested.",
                reference_list=[preserve_target],
            )

        target, is_ambiguous = reference_resolution.resolve_implicit_target(
            request.text, session.lastReferencedTarget
        )
        if is_ambiguous:
            thread = clarifications.open_clarification(
                turn_id,
                question="Which part of the design do you mean?",
                target=None,
                expected_answer_type="ENUM_CHOICE",
                now=now,
                allowed_choices=list(_KNOWN_TARGETS),
            )
            session.pendingClarification = thread
            session.status = "WAITING_FOR_CLARIFICATION"
            return self._make_turn(
                turn_id, request, session, now, "REQUEST_CLARIFICATION", thread.question,
                clarification=thread,
                diagnostics=[
                    ConversationDiagnostic(
                        code="CONVERSATION_REFERENCE_AMBIGUOUS",
                        severity="info",
                        message="Could not determine which component this refers to without more context.",
                    )
                ],
            )
        if target is not None:
            session.lastReferencedTarget = target

        if session.activeProposal is not None and session.activeProposal.status == "ACTIVE":
            session.activeProposal = session.activeProposal.model_copy(update={"status": "SUPERSEDED"})

        interaction_mode = "CREATE" if action == "CREATE_DESIGN_PROPOSAL" else "MODIFY"
        try:
            designer_result = self._designer.interpret(
                NaturalLanguageDesignRequest(
                    requestId=turn_id,
                    text=request.text,
                    locale=request.locale,
                    interactionMode=interaction_mode,
                    currentJDL=request.currentJDL,
                    currentDesignIntent=request.currentDesignIntent,
                )
            )
        except AppError:
            # Propagate Designer's own specific code (e.g. 503
            # DESIGNER_PROVIDER_UNAVAILABLE, 400 DESIGNER_SECURITY_REJECTED)
            # as-is — never mask a more specific, already-honest error
            # behind a generic CONVERSATION_PROVIDER_FAILED.
            raise
        except Exception as exc:  # noqa: BLE001 - anything else is a generic provider failure
            raise ConversationProviderFailedError(
                f"Conversation could not interpret this turn: {exc}"
            ) from exc

        return self._resolve_designer_proposal(
            turn_id, request, session, now, designer_result.proposal, action
        )

    def _resolve_designer_proposal(
        self,
        turn_id: str,
        request: ConversationTurnRequest,
        session: ConversationSession,
        now: str,
        proposal: DesignerProposal,
        action: ConversationActionType,
    ) -> ConversationTurn:
        if proposal.clarificationQuestions:
            question = proposal.clarificationQuestions[0]
            expected_type = "ENUM_CHOICE" if question.options else (
                "NUMERIC" if designer_normalizer.is_numeric_field(question.field or "") else "FREE_TEXT"
            )
            thread = clarifications.open_clarification(
                turn_id,
                question=question.question,
                target=question.field,
                expected_answer_type=expected_type,
                now=now,
                allowed_choices=list(question.options),
            )
            session.pendingClarification = thread
            session.status = "WAITING_FOR_CLARIFICATION"
            return self._make_turn(
                turn_id, request, session, now, "REQUEST_CLARIFICATION", thread.question, clarification=thread
            )

        if proposal.unsupportedFeatures and not proposal.proposedFields:
            features = [f.feature for f in proposal.unsupportedFeatures]
            for feature in features:
                if feature not in session.summary.unsupportedDiscussed:
                    session.summary.unsupportedDiscussed.append(feature)
            session.status = "ACTIVE"
            return self._make_turn(
                turn_id, request, session, now, "REPORT_UNSUPPORTED",
                "; ".join(f.reason for f in proposal.unsupportedFeatures),
                unsupported_features=features,
            )

        conv_proposal = state.make_proposal(
            turn_id, request.currentJDL, request.currentDesignIntent, proposal
        )
        session.activeProposal = conv_proposal
        session.status = "PROPOSAL_READY"
        technical_changes = [d.path for d in proposal.diff if d.changed]
        intent_changes = [f"{s.target}.{s.concept}" for s in proposal.designIntent.statements]
        unsupported = [f.feature for f in proposal.unsupportedFeatures]
        interpreted_action: ConversationActionType = (
            "MODIFY_INTENT" if not technical_changes and intent_changes else action
        )
        summary = (
            f"Proposal ready: {len(technical_changes)} technical change(s), "
            f"{len(intent_changes)} intent statement(s)."
        )
        return self._make_turn(
            turn_id, request, session, now, interpreted_action, summary,
            proposal_id=conv_proposal.proposalId,
            technical_changes=technical_changes,
            intent_changes=intent_changes,
            unsupported_features=unsupported,
        )

    def _handle_answer_clarification(
        self, turn_id: str, request: ConversationTurnRequest, session: ConversationSession, now: str
    ) -> ConversationTurn:
        thread = session.pendingClarification
        if thread is None or thread.status != "OPEN":
            raise ConversationNoPendingClarificationError("There is no open question to answer right now.")

        resolved_value, accepted = clarifications.try_resolve_answer(thread, request.text)
        if not accepted:
            return self._make_turn(
                turn_id, request, session, now, "ANSWER_CLARIFICATION",
                f"Could not understand that as an answer to: {thread.question}",
                clarification=thread,
                diagnostics=[
                    ConversationDiagnostic(
                        code=CONVERSATION_CLARIFICATION_INVALID,
                        severity="warning",
                        message=f"'{request.text}' did not match the expected answer type for this question.",
                    )
                ],
            )

        closed = clarifications.close_answered(thread, request.text, resolved_value, now)
        session.pendingClarification = None

        combined_text = f"{thread.question} {request.text}"
        try:
            designer_result = self._designer.interpret(
                NaturalLanguageDesignRequest(
                    requestId=turn_id,
                    text=combined_text,
                    locale=request.locale,
                    interactionMode="MODIFY",
                    currentJDL=request.currentJDL,
                    currentDesignIntent=request.currentDesignIntent,
                )
            )
        except AppError:
            raise
        except Exception as exc:  # noqa: BLE001 - anything else is a generic provider failure
            raise ConversationProviderFailedError(
                f"Conversation could not interpret this answer: {exc}"
            ) from exc

        turn = self._resolve_designer_proposal(
            turn_id, request, session, now, designer_result.proposal, "MODIFY_DESIGN_PROPOSAL"
        )
        return turn.model_copy(update={"clarification": closed, "interpretedAction": "ANSWER_CLARIFICATION"})

    def _handle_accept(
        self, turn_id: str, request: ConversationTurnRequest, session: ConversationSession, now: str
    ) -> ConversationTurn:
        proposal = session.activeProposal
        if proposal is None or proposal.status != "ACTIVE":
            raise ConversationInvalidStateError("There is no active proposal to accept.")

        if state.is_proposal_stale(proposal, request.currentJDL, request.currentDesignIntent):
            raise ConversationStaleContextError(
                "The design changed since this proposal was created — please describe the change again."
            )

        accepted_proposal = proposal.model_copy(update={"status": "ACCEPTED"})
        technical_changes = [d.path for d in accepted_proposal.designerProposal.diff if d.changed]
        intent_changes = [
            f"{s.target}.{s.concept}" for s in accepted_proposal.designerProposal.designIntent.statements
        ]
        session.acceptedChangeHistory.extend(technical_changes)
        for change in technical_changes:
            if change not in session.summary.acceptedDecisions:
                session.summary.acceptedDecisions.append(change)
        session.activeProposal = None
        session.status = "ACTIVE"
        return self._make_turn(
            turn_id, request, session, now, "ACCEPT_PROPOSAL", "Proposal accepted.",
            proposal_id=accepted_proposal.proposalId,
            technical_changes=technical_changes,
            intent_changes=intent_changes,
            accepted=True,
        )

    def _handle_reject(
        self, turn_id: str, request: ConversationTurnRequest, session: ConversationSession, now: str
    ) -> ConversationTurn:
        proposal = session.activeProposal
        if proposal is None:
            raise ConversationInvalidStateError("There is no active proposal to reject.")
        session.activeProposal = None
        session.status = "IDLE"
        return self._make_turn(
            turn_id, request, session, now, "REJECT_PROPOSAL", "Proposal discarded — no changes applied.",
            proposal_id=proposal.proposalId, accepted=False,
        )

    def _handle_cancel(
        self, turn_id: str, request: ConversationTurnRequest, session: ConversationSession, now: str
    ) -> ConversationTurn:
        if session.pendingClarification is not None:
            session.pendingClarification = None
        if session.activeProposal is not None:
            session.activeProposal = None
        session.status = "IDLE"
        return self._make_turn(
            turn_id, request, session, now, "CANCEL_INTERACTION",
            "Cleared the current interaction. No changes were made.",
        )

    # --- helpers ---------------------------------------------------------

    def _make_turn(
        self,
        turn_id: str,
        request: ConversationTurnRequest,
        session: ConversationSession,
        now: str,
        action: ConversationActionType,
        result: str,
        *,
        reference_list: list[str] | None = None,
        technical_changes: list[str] | None = None,
        intent_changes: list[str] | None = None,
        clarification=None,
        unsupported_features: list[str] | None = None,
        proposal_id: str | None = None,
        accepted: bool | None = None,
        diagnostics: list[ConversationDiagnostic] | None = None,
    ) -> ConversationTurn:
        return ConversationTurn(
            turnId=turn_id,
            sequence=len(session.turns) + 1,
            role="user",
            sourceText=request.text,
            timestamp=now,
            interpretedAction=action,
            references=reference_list or [],
            technicalChanges=technical_changes or [],
            intentChanges=intent_changes or [],
            clarification=clarification,
            unsupportedFeatures=unsupported_features or [],
            proposalId=proposal_id,
            result=result,
            accepted=accepted,
            relatedJDLHashBefore=session.currentJDLHash,
            relatedJDLHashAfter=session.currentJDLHash,
            relatedIntentHashBefore=session.currentIntentHash,
            relatedIntentHashAfter=session.currentIntentHash,
            diagnostics=diagnostics or [],
        )
