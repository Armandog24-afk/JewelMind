"""HTTP routes."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import FileResponse, PlainTextResponse, Response

from jewelmind import __version__
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
from jewelmind.services.model_service import model_service
from jewelmind.validation.engine import has_errors

router = APIRouter()


@router.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    cad_ready = True
    try:
        import cadquery  # noqa: F401
    except Exception:
        cad_ready = False

    return HealthResponse(
        status="ok",
        service="jewelmind-backend",
        version=__version__,
        cadEngine="cadquery",
        cadEngineReady=cad_ready,
    )


@router.post("/api/models/validate", response_model=ValidateResponse)
def validate_model(definition: JewelryDefinition) -> ValidateResponse:
    results = model_service.validate(definition)
    return ValidateResponse(results=results, hasErrors=has_errors(results))


@router.post("/api/models/generate", response_model=GenerateResponse)
def generate_model(definition: JewelryDefinition) -> GenerateResponse:
    record = model_service.generate(definition)
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
    path = model_service.preview_file(model_id, component_name)
    return FileResponse(path, media_type="model/stl", filename=f"{component_name}.stl")


@router.post("/api/models/export/step")
def export_step_route(payload: ExportStepRequest) -> FileResponse:
    record = model_service.get_record(payload.modelId)
    path = model_service.export_step_file(
        payload.modelId, include_stone=payload.includeStoneReference
    )
    filename = sanitize_filename(record.definition.project.name, default="jewelmind-model") + ".step"
    return FileResponse(path, media_type="application/step", filename=filename)


@router.post("/api/models/export/stl")
def export_stl_route(payload: ExportStlRequest) -> FileResponse:
    record = model_service.get_record(payload.modelId)
    path = model_service.export_stl_file(
        payload.modelId,
        include_stone=payload.includeStoneReference,
        mesh_tolerance=payload.meshTolerance,
        angular_tolerance=payload.angularTolerance,
    )
    filename = sanitize_filename(record.definition.project.name, default="jewelmind-model") + ".stl"
    return FileResponse(path, media_type="model/stl", filename=filename)


@router.post("/api/models/export/json")
def export_json_route(payload: ExportJsonRequest) -> Response:
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
