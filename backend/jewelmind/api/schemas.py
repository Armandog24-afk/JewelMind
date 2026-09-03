"""Request/response models for the HTTP API (kept separate from the domain
schema so API concerns — e.g. optional override fields — never leak into
the canonical JewelryDefinition).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from jewelmind.domain.schema import JdlGemIdentity
from jewelmind.validation.rules import ValidationResult


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    cadEngine: str
    cadEngineReady: bool
    cadEngineError: str | None = None


class ValidateResponse(BaseModel):
    results: list[ValidationResult]
    hasErrors: bool


class GenerateResponse(BaseModel):
    modelId: str
    definitionHash: str
    validation: list[ValidationResult]
    metadata: dict[str, Any]
    previewComponents: dict[str, Any]
    warnings: list[str]
    generatedAt: str


class ModelMetadataResponse(BaseModel):
    modelId: str
    definitionHash: str
    generatorVersion: str
    generatedAt: str
    generationDurationSeconds: float
    componentVolumesMm3: dict[str, float]
    combinedMetalVolumeMm3: float
    boundingBoxMm: dict[str, float]
    warnings: list[str]
    inspection: dict[str, Any]
    validation: list[ValidationResult]


class _StrictRequest(BaseModel):
    """Shared strictness for request bodies: reject unknown fields and
    reject type-coerced input (e.g. a numeric string for a float field).
    """

    model_config = ConfigDict(extra="forbid", strict=True)


class ExportStepRequest(_StrictRequest):
    modelId: str
    includeStoneReference: bool = False


class ExportStlRequest(_StrictRequest):
    modelId: str
    includeStoneReference: bool = False
    # Optional overrides for the definition's own preview.meshTolerance /
    # angularTolerance. Must be finite and strictly positive when provided —
    # an infinite or non-positive tolerance would hang or crash the
    # OpenCascade tessellator.
    meshTolerance: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    angularTolerance: float | None = Field(default=None, gt=0, allow_inf_nan=False)


class ExportJsonRequest(_StrictRequest):
    modelId: str


class SpecificationRequest(_StrictRequest):
    modelId: str


class ReviewPackageRequest(_StrictRequest):
    modelId: str
    caseId: str = Field(min_length=1, max_length=100)
    includeStoneReference: bool = True

class GemRegistryResponse(BaseModel):
    """The gem registry, for a client that needs to offer a choice.

    The backend is authoritative (brief section 11): the frontend reads this
    rather than defining its own entries, so a gem cannot exist in the UI that
    the backend does not know.
    """

    registryVersion: str
    gems: list[dict]
    visualProfiles: list[dict]
    #: Names JewelMind deliberately does not implement, so a client can explain
    #: an absence instead of silently omitting it.
    note: str


class GemResolveRequest(BaseModel):
    """Resolve a human term to a canonical gem ID."""

    term: str = Field(min_length=1, max_length=120)


class GemResolveResponse(BaseModel):
    term: str
    #: `None` when nothing matched. Never a guess (brief section 10).
    gemId: str | None
    gem: dict | None


class GemValidateRequest(BaseModel):
    """Validate a gem identity without generating anything."""

    gem: JdlGemIdentity


class GemValidateResponse(BaseModel):
    valid: bool
    results: list[ValidationResult]
    resolved: dict | None
