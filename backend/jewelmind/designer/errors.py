"""Designer error codes.

Every code here is one of the 11 verbatim DESIGNER_* codes from
docs/bible/12-designer/312-designer-error-model.md. A code is raised as an
`AppError` (HTTP failure) only when interpretation could not produce *any*
proposal at all — provider unreachable, provider timed out, provider
returned something that isn't parseable/valid structured output, or the
request itself was rejected as a security risk. The remaining codes
(unsupported feature, ambiguous request, clarification required, proposal
invalid, capability mismatch) are expected, normal outcomes of
interpreting a real request — they never fail the HTTP call, and instead
appear as `DesignerDiagnostic.code` values inside a 200 `DesignerResult`,
using this same vocabulary so there is exactly one code namespace.
"""

from __future__ import annotations

from jewelmind.api.errors import AppError


class DesignerProviderUnavailableError(AppError):
    """No AI provider is configured for this backend process.

    Raised, never silently substituted with a fake provider — see
    DESIGNER-GOV-015. The frontend must show "AI interpretation
    unavailable" and leave manual editing fully functional.
    """

    status_code = 503
    code = "DESIGNER_PROVIDER_UNAVAILABLE"


class DesignerProviderTimeoutError(AppError):
    status_code = 504
    code = "DESIGNER_PROVIDER_TIMEOUT"


class DesignerProviderError(AppError):
    status_code = 502
    code = "DESIGNER_PROVIDER_ERROR"


class DesignerInvalidResponseError(AppError):
    """The provider returned something that isn't parseable structured output."""

    status_code = 502
    code = "DESIGNER_INVALID_RESPONSE"


class DesignerSchemaViolationError(AppError):
    """The provider's structured output parsed as JSON but failed schema validation."""

    status_code = 502
    code = "DESIGNER_SCHEMA_VIOLATION"


class DesignerSecurityRejectedError(AppError):
    """The request text itself was rejected before ever reaching a provider."""

    status_code = 400
    code = "DESIGNER_SECURITY_REJECTED"


# Diagnostic-only codes (never raised as AppError; used as
# DesignerDiagnostic.code values). Centralized here so the full 11-code
# vocabulary lives in one file and DESIGNER-GOV-... rules can reference it.
DESIGNER_UNSUPPORTED_FEATURE = "DESIGNER_UNSUPPORTED_FEATURE"
DESIGNER_AMBIGUOUS_REQUEST = "DESIGNER_AMBIGUOUS_REQUEST"
DESIGNER_CLARIFICATION_REQUIRED = "DESIGNER_CLARIFICATION_REQUIRED"
DESIGNER_PROPOSAL_INVALID = "DESIGNER_PROPOSAL_INVALID"
DESIGNER_CAPABILITY_MISMATCH = "DESIGNER_CAPABILITY_MISMATCH"

ALL_DESIGNER_ERROR_CODES = (
    "DESIGNER_PROVIDER_UNAVAILABLE",
    "DESIGNER_PROVIDER_TIMEOUT",
    "DESIGNER_PROVIDER_ERROR",
    "DESIGNER_INVALID_RESPONSE",
    "DESIGNER_SCHEMA_VIOLATION",
    "DESIGNER_UNSUPPORTED_FEATURE",
    "DESIGNER_AMBIGUOUS_REQUEST",
    "DESIGNER_CLARIFICATION_REQUIRED",
    "DESIGNER_PROPOSAL_INVALID",
    "DESIGNER_CAPABILITY_MISMATCH",
    "DESIGNER_SECURITY_REJECTED",
)
