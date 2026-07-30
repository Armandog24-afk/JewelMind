"""Application error types and the shared error response schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    requestId: str
    details: list[Any] = []


class ErrorEnvelope(BaseModel):
    error: ErrorDetail


class AppError(Exception):
    """Base class for errors that map to a specific HTTP status and code."""

    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, *, details: list[Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or []


class ValidationBlockedError(AppError):
    status_code = 422
    code = "VALIDATION_BLOCKED"


class ModelNotFoundError(AppError):
    status_code = 404
    code = "MODEL_NOT_FOUND"


class ModelGenerationFailedError(AppError):
    status_code = 500
    code = "MODEL_GENERATION_FAILED"


class ExportFailedError(AppError):
    """Generic export failure (JSON / specification exports)."""

    status_code = 500
    code = "EXPORT_FAILED"


class StepExportFailedError(AppError):
    status_code = 500
    code = "STEP_EXPORT_FAILED"


class StlExportFailedError(AppError):
    status_code = 500
    code = "STL_EXPORT_FAILED"


class BadRequestError(AppError):
    status_code = 400
    code = "BAD_REQUEST"


class CadEngineUnavailableError(AppError):
    """Raised when CadQuery/OpenCascade failed to load in this process.

    503 (Service Unavailable) rather than 500: this signals a temporary,
    environment-level problem the caller cannot fix by changing their
    request, distinct from a genuine bug in geometry generation for a
    specific definition.
    """

    status_code = 503
    code = "CAD_ENGINE_UNAVAILABLE"
