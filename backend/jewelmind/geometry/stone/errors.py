"""Structured Stone System errors (brief section 56). Aligned with the
existing API error-code conventions — no stack trace leakage; every error
is caught at the API boundary and mapped the same way any other domain
error already is (see `api/app.py`'s existing exception handlers)."""

from __future__ import annotations


class StoneShapeUnsupportedError(Exception):
    """Raised for a `StoneShape` value with no registered generator —
    should be unreachable in practice since `StoneShape` is a closed
    Pydantic enum, but kept as a real, explicit guard rather than an
    implicit `KeyError` (STONE-GOV-007)."""


class StoneGenerationError(Exception):
    """A requested stone configuration could not be constructed. Raised
    rather than silently falling back to another shape (STONE-GOV-013)."""
