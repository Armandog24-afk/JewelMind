"""Category/family dispatch errors — align with `jewelmind.api.errors.AppError`
so they surface as clean HTTP responses, never a raw stack trace."""

from __future__ import annotations

from jewelmind.api.errors import AppError


class JewelryCategoryUnsupportedError(AppError):
    """The category string is not a recognized value at all."""

    status_code = 422
    code = "JEWELRY_CATEGORY_UNSUPPORTED"


class JewelryCategoryNotGeneratableError(AppError):
    """The category is recognized (possibly `status: planned`) but has no
    registered generator yet."""

    status_code = 422
    code = "JEWELRY_CATEGORY_NOT_GENERATABLE"


class RingFamilyUnsupportedError(AppError):
    status_code = 422
    code = "RING_FAMILY_UNSUPPORTED"


class RingDefinitionInvalidError(AppError):
    status_code = 422
    code = "RING_DEFINITION_INVALID"


class CategoryAdapterFailedError(AppError):
    """A JDL -> internal category-definition adapter could not map the
    input (e.g. `ring_definition_from_jdl` given a non-ring definition)."""

    status_code = 422
    code = "CATEGORY_ADAPTER_FAILED"
