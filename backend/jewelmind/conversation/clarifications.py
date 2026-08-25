"""Clarification thread lifecycle — OPEN -> ANSWERED/CANCELLED/SUPERSEDED.

See docs/bible/14-conversation/381-clarification-thread-model.md and
382-clarification-answer-resolution.md. A clarification answer resolves
only the thread it was opened for (CONV-GOV-007) — never a different,
unrelated open question.
"""

from __future__ import annotations

import uuid

from jewelmind.conversation.schemas import ClarificationThread, ExpectedAnswerType

_CONFIRMATION_YES: frozenset[str] = frozenset({"yes", "y", "si", "sì", "ok", "va bene", "d'accordo"})
_CONFIRMATION_NO: frozenset[str] = frozenset({"no", "not really", "niente"})


def open_clarification(
    turn_id: str,
    question: str,
    target: str | None,
    expected_answer_type: ExpectedAnswerType,
    now: str,
    allowed_choices: list[str] | None = None,
    required: bool = True,
) -> ClarificationThread:
    return ClarificationThread(
        clarificationId=f"clarification-{uuid.uuid4()}",
        originatingTurnId=turn_id,
        question=question,
        target=target,
        expectedAnswerType=expected_answer_type,
        allowedChoices=allowed_choices or [],
        required=required,
        status="OPEN",
        createdAt=now,
    )


def try_resolve_answer(thread: ClarificationThread, raw_answer: str) -> tuple[str | float | None, bool]:
    """Validates `raw_answer` against `thread`'s expected answer type.

    Returns ``(resolved_value, accepted)``. Never mutates `thread` —
    the caller decides whether/how to close it based on `accepted`.
    """

    token = raw_answer.strip()

    if thread.expectedAnswerType == "NUMERIC":
        # Accept "2.7", "2.7mm", "2.7 mm" — reject anything that isn't
        # fundamentally a number, rather than guessing.
        candidate = token.lower().replace("mm", "").strip()
        try:
            return float(candidate), True
        except ValueError:
            return None, False

    if thread.expectedAnswerType == "ENUM_CHOICE":
        lowered = token.lower()
        for choice in thread.allowedChoices:
            if choice.lower() == lowered:
                return choice, True
        return None, False

    if thread.expectedAnswerType == "CONFIRMATION":
        lowered = token.lower()
        if lowered in _CONFIRMATION_YES:
            return "yes", True
        if lowered in _CONFIRMATION_NO:
            return "no", True
        return None, False

    # FREE_TEXT always accepts non-empty text as-is.
    return (token, True) if token else (None, False)


def close_answered(
    thread: ClarificationThread, raw_answer: str, resolved_value: str | float, now: str
) -> ClarificationThread:
    return thread.model_copy(update={"status": "ANSWERED", "answer": raw_answer, "resolvedAt": now})


def cancel(thread: ClarificationThread, now: str) -> ClarificationThread:
    return thread.model_copy(update={"status": "CANCELLED", "resolvedAt": now})


def supersede(thread: ClarificationThread, now: str) -> ClarificationThread:
    return thread.model_copy(update={"status": "SUPERSEDED", "resolvedAt": now})
