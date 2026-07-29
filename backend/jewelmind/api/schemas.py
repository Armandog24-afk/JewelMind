"""Request/response models for the HTTP API (kept separate from the domain
schema so API concerns — e.g. optional override fields — never leak into
the canonical JewelryDefinition).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from jewelmind.validation.rules import ValidationResult


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    cadEngine: str
    cadEngineReady: bool


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
    validation: list[ValidationResult]


class ExportStepRequest(BaseModel):
    modelId: str
    includeStoneReference: bool = False


class ExportStlRequest(BaseModel):
    modelId: str
    includeStoneReference: bool = False
    meshTolerance: float | None = None
    angularTolerance: float | None = None


class ExportJsonRequest(BaseModel):
    modelId: str


class SpecificationRequest(BaseModel):
    modelId: str
