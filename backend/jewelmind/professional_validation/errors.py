"""Error types for the Professional Validation Framework."""

from __future__ import annotations

from jewelmind.api.errors import AppError


class ReviewPackageGenerationFailedError(AppError):
    status_code = 500
    code = "REVIEW_PACKAGE_GENERATION_FAILED"


class ReviewRecordInvalidError(AppError):
    """Raised by the `validate-review-record` CLI/validator when a
    ValidationRecord fails schema or structural checks. Never raised to
    say a reviewer's judgment is wrong — only that the record itself is
    malformed (missing a required reference, an unknown decision value,
    etc.). See docs/bible/15-professional-validation/README.md, section
    on `validate-review-record`."""

    status_code = 400
    code = "REVIEW_RECORD_INVALID"


class TemplateRecordInRegistryError(AppError):
    """Raised if a record with `isTemplate=True` is ever found in the
    active validation registry — a hard structural guard, not expected to
    ever actually trigger, protecting PROVAL-GOV-001's zero-fabrication
    guarantee even against an accidental copy-paste from an example
    fixture into the real registry file."""

    status_code = 500
    code = "TEMPLATE_RECORD_IN_REGISTRY"
