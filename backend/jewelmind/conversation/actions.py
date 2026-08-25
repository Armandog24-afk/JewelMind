"""Deterministic classification of a raw turn into a `ConversationActionType`.

Every meaningful turn produces one explicit outcome — never free-form
prose as the source of truth (the "fundamental conversation principle",
docs/bible/14-conversation/README.md). Classification here is
context-aware (it depends on whether a clarification or proposal is
currently open) but never depends on an AI provider — the same phrase
classifies the same way every time.
"""

from __future__ import annotations

from jewelmind.conversation import references as reference_resolution
from jewelmind.conversation.schemas import ConversationActionType, ConversationSession

_ACCEPT_PHRASES: frozenset[str] = frozenset(
    {
        "ok", "okay", "va bene", "perfetto", "accetta", "apply", "applica",
        "yes", "si", "sì", "d'accordo", "accept", "conferma", "confirm",
    }
)

_REJECT_PHRASES: frozenset[str] = frozenset(
    {
        "no", "annulla", "cancel", "lascia perdere", "non farlo", "rifiuta",
        "reject", "no grazie",
    }
)

# A no-op acknowledgment ONLY when nothing is actually pending — see
# 049-no-op-handling in the Sprint 12 brief. When a proposal or
# clarification IS pending, these same words mean something else (accept,
# or a confirmation answer) — handled by the caller's ordering, not here.
_NOOP_PHRASES: frozenset[str] = frozenset(
    {
        "ok", "okay", "va bene", "perfetto", "lascia tutto così", "fine", "alright", "good",
        "lascia perdere", "never mind", "nevermind",
    }
)

_CORRECTION_MARKERS: tuple[str, ...] = (
    "no,", "actually", "invece", "no wait", "no aspetta", "piuttosto",
)

_START_OVER_MARKERS: tuple[str, ...] = (
    "start over", "from scratch", "ricomincia", "da zero", "ricominciamo",
)

_UNDO_MARKERS: tuple[str, ...] = ("undo", "annulla l'ultima", "revert")


def _matches_any(text: str, phrases: frozenset[str]) -> bool:
    lowered = text.strip().lower().rstrip(".!")
    return lowered in phrases


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    lowered = text.strip().lower()
    return any(marker in lowered for marker in markers)


def classify_action(text: str, session: ConversationSession) -> ConversationActionType:
    pending = session.pendingClarification
    has_clarification = pending is not None and pending.status == "OPEN"
    has_active_proposal = session.activeProposal is not None and session.activeProposal.status == "ACTIVE"

    # An explicit "undo"/"annulla" always wins, even over an open
    # clarification or proposal — it is the general safety valve from
    # CANCEL_CURRENT_INTERACTION (see the Sprint 12 brief, section 19):
    # the user must always be able to back out, regardless of state.
    if _contains_any(text, _UNDO_MARKERS):
        return "CANCEL_INTERACTION"

    if has_clarification:
        # An open question always takes priority — even a phrase that
        # would otherwise look like accept/reject is first offered to the
        # clarification as a candidate answer (see 382, CONV-GOV-007).
        return "ANSWER_CLARIFICATION"

    if has_active_proposal:
        if _matches_any(text, _ACCEPT_PHRASES):
            return "ACCEPT_PROPOSAL"
        if _matches_any(text, _REJECT_PHRASES):
            return "REJECT_PROPOSAL"
        # Any other substantive text while a proposal is open (including
        # an explicit correction marker, or a "No, ..." prefix that is
        # NOT an exact match for a bare rejection) is treated as a
        # correction to it, never a silent second, unrelated change —
        # see CASE F in the Sprint 12 brief.
        return "MODIFY_DESIGN_PROPOSAL"

    if _matches_any(text, _NOOP_PHRASES):
        return "NO_CHANGE"

    if _contains_any(text, _START_OVER_MARKERS):
        return "CREATE_DESIGN_PROPOSAL"

    if len(text.split()) <= 6 and reference_resolution.find_preserve_target(text) is not None:
        return "PRESERVE_TARGET"

    return "MODIFY_DESIGN_PROPOSAL"
