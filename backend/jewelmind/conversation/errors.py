"""Conversation error codes.

Same split discipline as Designer's own error model
(docs/bible/12-designer/312-designer-error-model.md): a code is an HTTP
`AppError` only when a turn could not be processed into any result at
all. Codes that are expected, normal outcomes of a turn (an ambiguous
reference, an invalid clarification answer, a recovered state-sync
failure) are in-band `ConversationDiagnostic` codes instead — see
docs/bible/14-conversation/396-conversational-error-model.md.
"""

from __future__ import annotations

from jewelmind.api.errors import AppError


class ConversationInvalidStateError(AppError):
    """The requested action isn't valid for the session's current state
    (e.g. answering a clarification when none is open)."""

    status_code = 400
    code = "CONVERSATION_INVALID_STATE"


class ConversationNoPendingClarificationError(AppError):
    status_code = 400
    code = "CONVERSATION_NO_PENDING_CLARIFICATION"


class ConversationProposalSupersededError(AppError):
    status_code = 409
    code = "CONVERSATION_PROPOSAL_SUPERSEDED"


class ConversationStaleContextError(AppError):
    """The active proposal's base JDL/intent hash no longer matches the
    caller's current state — never blindly applied, per
    docs/bible/14-conversation/377-design-state-synchronization.md and
    the "concurrent manual editing" scenario in the Sprint 12 brief.
    """

    status_code = 409
    code = "CONVERSATION_STALE_CONTEXT"


class ConversationProviderFailedError(AppError):
    status_code = 502
    code = "CONVERSATION_PROVIDER_FAILED"


class ConversationContextTooLargeError(AppError):
    status_code = 400
    code = "CONVERSATION_CONTEXT_TOO_LARGE"


class ConversationActionUnsupportedError(AppError):
    status_code = 400
    code = "CONVERSATION_ACTION_UNSUPPORTED"


# Security screening reuses `DesignerSecurityRejectedError` directly
# (imported by service.py) rather than inventing an 11th conversation-only
# code — every turn (including a clarification answer or correction) is
# untrusted input, screened the same way Designer already screens a
# natural-language request. See 397-conversation-security.md.

# Diagnostic-only codes (never raised as AppError; used as
# ConversationDiagnostic.code values inside a normal 200 ConversationResult).
CONVERSATION_REFERENCE_AMBIGUOUS = "CONVERSATION_REFERENCE_AMBIGUOUS"
CONVERSATION_CLARIFICATION_INVALID = "CONVERSATION_CLARIFICATION_INVALID"
CONVERSATION_STATE_SYNC_FAILED = "CONVERSATION_STATE_SYNC_FAILED"

ALL_CONVERSATION_ERROR_CODES = (
    "CONVERSATION_INVALID_STATE",
    "CONVERSATION_REFERENCE_AMBIGUOUS",
    "CONVERSATION_NO_PENDING_CLARIFICATION",
    "CONVERSATION_CLARIFICATION_INVALID",
    "CONVERSATION_PROPOSAL_SUPERSEDED",
    "CONVERSATION_STALE_CONTEXT",
    "CONVERSATION_PROVIDER_FAILED",
    "CONVERSATION_CONTEXT_TOO_LARGE",
    "CONVERSATION_ACTION_UNSUPPORTED",
    "CONVERSATION_STATE_SYNC_FAILED",
)
