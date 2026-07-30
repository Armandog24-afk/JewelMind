"""HTTP routes."""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import APIRouter, Response
from fastapi.responses import FileResponse, PlainTextResponse
from starlette.background import BackgroundTask

from jewelmind import __version__
from jewelmind.api.errors import (
    CadEngineUnavailableError,
    ModelGenerationFailedError,
    StepExportFailedError,
    StlExportFailedError,
    ValidationBlockedError,
)
from jewelmind.api.schemas import (
    ExportJsonRequest,
    ExportStepRequest,
    ExportStlRequest,
    GenerateResponse,
    HealthResponse,
    ModelMetadataResponse,
    SpecificationRequest,
    ValidateResponse,
)
from jewelmind.domain.schema import JewelryDefinition
from jewelmind.exporters.filenames import sanitize_filename
from jewelmind.services.cad_engine import cad_engine_error, cad_engine_ready
from jewelmind.validation.engine import has_errors, validate_definition

if TYPE_CHECKING:
    from jewelmind.services.model_service import ModelService

router = APIRouter()

# `services.model_service` (transitively) imports the geometry package,
# which imports cadquery unconditionally at module scope. That import must
# stay lazy here — not at module scope in this file — so a broken CadQuery
# install only breaks the CAD-dependent endpoints below, instead of
# crashing the whole backend before it can even serve /api/health or
# /api/models/validate.
_model_service_instance: ModelService | None = None


def _get_model_service() -> ModelService:
    global _model_service_instance
    if _model_service_instance is not None:
        return _model_service_instance
    try:
        from jewelmind.services.model_service import model_service
    except Exception as exc:  # noqa: BLE001 - any import failure means "unavailable"
        raise CadEngineUnavailableError(
            f"The CAD engine is not available in this backend process: {exc}"
        ) from exc
    _model_service_instance = model_service
    return _model_service_instance


def _delete_file(path: str | Path) -> None:
    """Background cleanup for a one-off export temp file (see ModelService)."""

    with contextlib.suppress(OSError):
        Path(path).unlink(missing_ok=True)


@router.get("/api/health", response_model=HealthResponse)
def health(response: Response) -> HealthResponse:
    ready = cad_engine_ready()
    if not ready:
        # Non-2xx so container/orchestrator health checks (and CI) correctly
        # treat this as "not ready" rather than reporting a broken CAD
        # engine as healthy.
        response.status_code = 503

    return HealthResponse(
        status="ok" if ready else "degraded",
        service="jewelmind-backend",
        version=__version__,
        cadEngine="cadquery",
        cadEngineReady=ready,
        cadEngineError=None if ready else cad_engine_error(),
    )


@router.post("/api/models/validate", response_model=ValidateResponse)
def validate_model(definition: JewelryDefinition) -> ValidateResponse:
    # Deliberately does not go through model_service: validation is pure
    # business logic with no CadQuery dependency, so it must keep working
    # even when the CAD engine itself is unavailable.
    results = validate_definition(definition)
    return ValidateResponse(results=results, hasErrors=has_errors(results))


@router.post("/api/models/generate", response_model=GenerateResponse)
def generate_model(definition: JewelryDefinition) -> GenerateResponse:
    model_service = _get_model_service()
    try:
        record = model_service.generate(definition)
    except (ValidationBlockedError, CadEngineUnavailableError):
        raise
    except Exception as exc:  # noqa: BLE001 - any other failure is a generation failure
        raise ModelGenerationFailedError(f"Model generation failed: {exc}") from exc

    gm = record.generated_model

    preview_components = {
        name: {
            **{k: v for k, v in entry.items() if k != "file"},
            "url": (
                f"/api/models/{record.model_id}/preview/{name}"
                if entry.get("file") is not None
                else None
            ),
        }
        for name, entry in record.preview_manifest.items()
    }

    return GenerateResponse(
        modelId=record.model_id,
        definitionHash=gm.definition_hash,
        validation=record.validation_results,
        metadata={
            "generatorVersion": gm.generator_version,
            "generationDurationSeconds": gm.generation_duration_s,
            "componentVolumesMm3": gm.component_volumes(),
            "combinedMetalVolumeMm3": gm.combined_metal_volume_mm3,
            "boundingBoxMm": gm.bounding_box.as_dict(),
            "prongs": record.generated_model.components["prongs"].metadata,
        },
        previewComponents=preview_components,
        warnings=gm.warnings,
        generatedAt=record.generated_at,
    )


@router.get("/api/models/{model_id}/metadata", response_model=ModelMetadataResponse)
def model_metadata(model_id: str) -> ModelMetadataResponse:
    model_service = _get_model_service()
    record = model_service.get_record(model_id)
    gm = record.generated_model
    return ModelMetadataResponse(
        modelId=record.model_id,
        definitionHash=gm.definition_hash,
        generatorVersion=gm.generator_version,
        generatedAt=record.generated_at,
        generationDurationSeconds=gm.generation_duration_s,
        componentVolumesMm3=gm.component_volumes(),
        combinedMetalVolumeMm3=gm.combined_metal_volume_mm3,
        boundingBoxMm=gm.bounding_box.as_dict(),
        warnings=gm.warnings,
        validation=record.validation_results,
    )


@router.get("/api/models/{model_id}/preview/{component_name}")
def model_preview(model_id: str, component_name: str) -> FileResponse:
    model_service = _get_model_service()
    path = model_service.preview_file(model_id, component_name)
    return FileResponse(path, media_type="model/stl", filename=f"{component_name}.stl")


@router.post("/api/models/export/step")
def export_step_route(payload: ExportStepRequest) -> FileResponse:
    model_service = _get_model_service()
    record = model_service.get_record(payload.modelId)
    try:
        path = model_service.export_step_file(
            payload.modelId, include_stone=payload.includeStoneReference
        )
    except Exception as exc:  # noqa: BLE001 - any export failure maps to STEP_EXPORT_FAILED
        raise StepExportFailedError(f"STEP export failed: {exc}") from exc

    filename = sanitize_filename(record.definition.project.name, default="jewelmind-model") + ".step"
    # The exported file is a unique per-request temp file (see
    # ModelService.export_step_file); delete it once the response has
    # finished streaming so temp files never accumulate.
    return FileResponse(
        path,
        media_type="application/step",
        filename=filename,
        background=BackgroundTask(_delete_file, path),
    )


@router.post("/api/models/export/stl")
def export_stl_route(payload: ExportStlRequest) -> FileResponse:
    model_service = _get_model_service()
    record = model_service.get_record(payload.modelId)
    try:
        path = model_service.export_stl_file(
            payload.modelId,
            include_stone=payload.includeStoneReference,
            mesh_tolerance=payload.meshTolerance,
            angular_tolerance=payload.angularTolerance,
        )
    except Exception as exc:  # noqa: BLE001 - any export failure maps to STL_EXPORT_FAILED
        raise StlExportFailedError(f"STL export failed: {exc}") from exc

    filename = sanitize_filename(record.definition.project.name, default="jewelmind-model") + ".stl"
    return FileResponse(
        path,
        media_type="model/stl",
        filename=filename,
        background=BackgroundTask(_delete_file, path),
    )


@router.post("/api/models/export/json")
def export_json_route(payload: ExportJsonRequest) -> Response:
    model_service = _get_model_service()
    record = model_service.get_record(payload.modelId)
    text = model_service.export_json_text(payload.modelId)
    filename = sanitize_filename(record.definition.project.name, default="jewelmind-project") + ".json"
    return Response(
        content=text,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/api/models/specification")
def specification_route(payload: SpecificationRequest) -> PlainTextResponse:
    model_service = _get_model_service()
    record = model_service.get_record(payload.modelId)
    text = model_service.export_specification_text(payload.modelId)
    filename = (
        sanitize_filename(record.definition.project.name, default="jewelmind-specification")
        + "-specification.md"
    )
    return PlainTextResponse(
        content=text,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
