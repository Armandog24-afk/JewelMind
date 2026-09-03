"""FastAPI application factory."""

from __future__ import annotations

import math
import os
import time
import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from jewelmind import __version__
from jewelmind.api.errors import AppError
from jewelmind.api.routes import router
from jewelmind.utils.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

_DEFAULT_ORIGINS = "http://localhost:3000,http://localhost:5173"


def _json_safe(value: Any) -> Any:
    """Recursively replace non-finite floats with a safe string.

    Pydantic's `ValidationError.errors()` echoes back the raw invalid
    `input` a client sent — which, for a rejected `Infinity`/`NaN` numeric
    field (see domain/schema.py's `allow_inf_nan=False`), is itself a
    non-finite float. Starlette's JSONResponse renders with
    `allow_nan=False` (correctly — a JSON response body must not contain
    the bare literals `Infinity`/`NaN`), so embedding that raw value
    verbatim in the error response crashes the error handler itself while
    trying to report the very error that rejected it. This must be applied
    to any error payload built from arbitrary echoed request input before
    it reaches JSONResponse.
    """

    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    # ANY other object, stringified.
    #
    # The non-finite-float case above is one instance of a general problem:
    # `errors()` echoes back whatever a validator put in `ctx`, and a
    # `model_validator` that raises `ValueError` puts the exception OBJECT
    # there. Serializing that crashed the handler, so a request rejected by a
    # cross-field rule came back as an opaque 500 instead of a 422 naming the
    # field — found in Sprint 21 against `stone.gem` (a custom gem with no
    # name), but the same fault applied to every `ValueError`-raising validator
    # in the schema, including the Stone v2 outline rules from Sprint 20.
    #
    # `str()` on a pydantic `ValueError` yields the validator's own message,
    # which is written by this codebase and carries no server path or stack
    # trace (FOUNDRY-GOV-011).
    return str(value)


def _cors_origins() -> list[str]:
    raw = os.environ.get("JEWELMIND_CORS_ORIGINS", _DEFAULT_ORIGINS)
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def create_app() -> FastAPI:
    app = FastAPI(
        title="JewelMind Backend",
        version=__version__,
        description=(
            "Parametric jewelry CAD backend. Generates preliminary geometry only — "
            "see /api/health and the project README for the professional review disclaimer."
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_id_and_timing(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-Id"] = request_id
        logger.info(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            durationMs=round(duration_ms, 2),
            requestId=request_id,
        )
        return response

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning("app_error", code=exc.code, message=exc.message, requestId=request_id)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "requestId": request_id,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "REQUEST_VALIDATION_ERROR",
                    "message": "The request body did not match the expected schema.",
                    "requestId": request_id,
                    "details": _json_safe(exc.errors()),
                }
            },
        )

    @app.exception_handler(ValidationError)
    async def handle_pydantic_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "REQUEST_VALIDATION_ERROR",
                    "message": "The request body did not match the expected schema.",
                    "requestId": request_id,
                    "details": _json_safe(exc.errors()),
                }
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error("unhandled_error", error=str(exc), requestId=request_id)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred. No further details are available.",
                    "requestId": request_id,
                    "details": [],
                }
            },
        )

    app.include_router(router)
    return app


app = create_app()
