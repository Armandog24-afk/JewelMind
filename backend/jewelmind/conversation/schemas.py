"""Conversation data shapes.

See docs/bible/14-conversation/372-conversation-domain-model.md.
ConversationSession never carries its own copy of the design — it always
defers to the caller's `currentJDL`/`currentDesignIntent`
(CONV-GOV-002/003) and only ever stores dotted-path/target-key summaries
plus real hashes for staleness detection, never a duplicate authoritative
copy of state.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from jewelmind.design_intent.schemas import DesignIntent
from jewelmind.designer.schemas import DesignerProposal, SupportedLocale
from jewelmind.domain.schema import JewelryDefinition

ConversationActionType = Literal[
    "CREATE_DESIGN_PROPOSAL",
    "MODIFY_DESIGN_PROPOSAL",
    "ADD_INTENT",
    "MODIFY_INTENT",
    "REMOVE_INTENT",
    "PRESERVE_TARGET",
    "REQUEST_CLARIFICATION",
    "ANSWER_CLARIFICATION",
    "REPORT_UNSUPPORTED",
    "ACCEPT_PROPOSAL",
    "REJECT_PROPOSAL",
    "CANCEL_INTERACTION",
    "NO_CHANGE",
]

SessionStatus = Literal[
    "ACTIVE",
    "WAITING_FOR_CLARIFICATION",
    "PROPOSAL_READY",
    "WAITING_FOR_ACCEPTANCE",
    "IDLE",
    "CLOSED",
    "FAILED",
]

ClarificationStatus = Literal["OPEN", "ANSWERED", "CANCELLED", "SUPERSEDED"]

ExpectedAnswerType = Literal["NUMERIC", "ENUM_CHOICE", "FREE_TEXT", "CONFIRMATION"]

ProposalStatus = Literal["ACTIVE", "ACCEPTED", "REJECTED", "SUPERSEDED", "STALE"]

ConversationDiagnosticCode = Literal[
    "CONVERSATION_REFERENCE_AMBIGUOUS",
    "CONVERSATION_CLARIFICATION_INVALID",
    "CONVERSATION_STATE_SYNC_FAILED",
]


class ConversationModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ClarificationThread(ConversationModel):
    clarificationId: str
    originatingTurnId: str
    question: str
    target: str | None = None
    expectedAnswerType: ExpectedAnswerType
    allowedChoices: list[str] = Field(default_factory=list)
    required: bool = True
    status: ClarificationStatus = "OPEN"
    createdAt: str
    resolvedAt: str | None = None
    answer: str | None = None


class ClarificationAnswer(ConversationModel):
    clarificationId: str
    turnId: str
    rawAnswer: str
    resolvedValue: str | float | None = None
    accepted: bool


class ConversationProposal(ConversationModel):
    proposalId: str
    turnId: str
    baseDefinitionHash: str
    baseIntentHash: str
    designerProposal: DesignerProposal
    status: ProposalStatus = "ACTIVE"


class ConversationSummary(ConversationModel):
    acceptedDecisions: list[str] = Field(default_factory=list)
    intentThemes: list[str] = Field(default_factory=list)
    unresolvedQuestions: list[str] = Field(default_factory=list)
    rejectedDirections: list[str] = Field(default_factory=list)
    unsupportedDiscussed: list[str] = Field(default_factory=list)


class ConversationDiagnostic(ConversationModel):
    code: ConversationDiagnosticCode
    severity: Literal["info", "warning", "error"]
    message: str


class ConversationTurn(ConversationModel):
    turnId: str
    sequence: int
    role: Literal["user", "system"] = "user"
    sourceText: str
    timestamp: str
    interpretedAction: ConversationActionType
    references: list[str] = Field(default_factory=list)
    technicalChanges: list[str] = Field(default_factory=list)
    intentChanges: list[str] = Field(default_factory=list)
    clarification: ClarificationThread | None = None
    unsupportedFeatures: list[str] = Field(default_factory=list)
    proposalId: str | None = None
    result: str
    accepted: bool | None = None
    relatedJDLHashBefore: str
    relatedJDLHashAfter: str
    relatedIntentHashBefore: str
    relatedIntentHashAfter: str
    diagnostics: list[ConversationDiagnostic] = Field(default_factory=list)


class ConversationSession(ConversationModel):
    sessionId: str
    sessionVersion: str = "1.0.0"
    currentJDLHash: str
    currentIntentHash: str
    turns: list[ConversationTurn] = Field(default_factory=list)
    pendingClarification: ClarificationThread | None = None
    activeProposal: ConversationProposal | None = None
    acceptedChangeHistory: list[str] = Field(default_factory=list)
    lastReferencedTarget: str | None = None
    summary: ConversationSummary = Field(default_factory=ConversationSummary)
    status: SessionStatus = "IDLE"
    createdAt: str
    updatedAt: str


class TurnContext(ConversationModel):
    """What a real provider would receive — compact, never raw CAD
    geometry, never the entire turn history. See
    docs/bible/14-conversation/375-turn-context-model.md."""

    activeProposalId: str | None = None
    pendingClarificationQuestion: str | None = None
    recentAcceptedChanges: list[str] = Field(default_factory=list)
    compactConversationSummary: ConversationSummary | None = None
    modelCurrentOrStale: Literal["CURRENT", "STALE", "NONE"] = "NONE"


class ConversationTurnRequest(ConversationModel):
    text: str = Field(min_length=1, max_length=2000)
    locale: SupportedLocale | None = None
    currentJDL: JewelryDefinition
    currentDesignIntent: DesignIntent
    session: ConversationSession | None = None


class ConversationResult(ConversationModel):
    session: ConversationSession
    turn: ConversationTurn
