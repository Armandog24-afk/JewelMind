"""Session state helpers — hashing, creation, and status transitions.

A `ConversationSession` never carries its own copy of the design; it only
ever stores real hashes of whatever `currentJDL`/`currentDesignIntent` the
caller supplied on this request, computed fresh every call — see
docs/bible/14-conversation/377-design-state-synchronization.md and
CONV-GOV-008 (stale conversational context must not overwrite newer
accepted state).
"""

from __future__ import annotations

import hashlib
import json
import uuid

from jewelmind.conversation.schemas import (
    ConversationProposal,
    ConversationSession,
    ConversationSummary,
)
from jewelmind.design_intent.schemas import DesignIntent
from jewelmind.designer.schemas import DesignerProposal
from jewelmind.domain.schema import JewelryDefinition
from jewelmind.utils.hashing import definition_hash


def intent_hash(intent: DesignIntent) -> str:
    """Deterministic hex digest identifying a DesignIntent's content.

    Mirrors `jewelmind.utils.hashing.definition_hash()` exactly — same
    canonical-JSON-then-sha256 technique, scoped to the conversation
    layer's staleness-detection need rather than added to
    `design_intent/` itself, since Design Intent Model v1 has no other use
    for a content hash of its own.
    """

    data = intent.model_dump(mode="json")
    payload = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def new_session(
    current_jdl: JewelryDefinition, current_intent: DesignIntent, now: str
) -> ConversationSession:
    return ConversationSession(
        sessionId=f"session-{uuid.uuid4()}",
        currentJDLHash=definition_hash(current_jdl),
        currentIntentHash=intent_hash(current_intent),
        turns=[],
        pendingClarification=None,
        activeProposal=None,
        acceptedChangeHistory=[],
        lastReferencedTarget=None,
        summary=ConversationSummary(),
        status="IDLE",
        createdAt=now,
        updatedAt=now,
    )


def refresh_hashes(
    session: ConversationSession, current_jdl: JewelryDefinition, current_intent: DesignIntent
) -> None:
    """Updates the session's hashes in place to reflect what the caller
    actually sent this request — the session must never keep displaying a
    stale hash from an earlier turn."""

    session.currentJDLHash = definition_hash(current_jdl)
    session.currentIntentHash = intent_hash(current_intent)


def is_proposal_stale(
    proposal: ConversationProposal, current_jdl: JewelryDefinition, current_intent: DesignIntent
) -> bool:
    """True when the design/intent the proposal was computed against no
    longer matches what the caller says is current now — e.g. the user
    manually edited a field in ConfigurationPanel while the proposal sat
    unaccepted. See docs/bible/14-conversation/377 and the "concurrent
    manual editing" scenario in the Sprint 12 brief; the correct response
    is to reject the accept, never to silently apply."""

    jdl_changed = proposal.baseDefinitionHash != definition_hash(current_jdl)
    intent_changed = proposal.baseIntentHash != intent_hash(current_intent)
    return jdl_changed or intent_changed


def make_proposal(
    turn_id: str,
    current_jdl: JewelryDefinition,
    current_intent: DesignIntent,
    designer_proposal: DesignerProposal,
) -> ConversationProposal:
    return ConversationProposal(
        proposalId=f"conv-proposal-{uuid.uuid4()}",
        turnId=turn_id,
        baseDefinitionHash=definition_hash(current_jdl),
        baseIntentHash=intent_hash(current_intent),
        designerProposal=designer_proposal,
        status="ACTIVE",
    )
