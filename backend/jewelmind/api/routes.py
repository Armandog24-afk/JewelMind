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
    ReviewPackageRequest,
    SpecificationRequest,
    ValidateResponse,
)
from jewelmind.conversation.schemas import ConversationResult, ConversationTurnRequest
from jewelmind.conversation.service import ConversationEngine
from jewelmind.designer.schemas import DesignerResult, NaturalLanguageDesignRequest
from jewelmind.designer.service import DesignerService
from jewelmind.domain.schema import JewelryDefinition
from jewelmind.exporters.filenames import sanitize_filename
from jewelmind.exporters.integrity import sha256_checksum
from jewelmind.geometry.inspection.models import GeometryInspectionReport
from jewelmind.professional_validation.review_package import build_review_package
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


def _inspection_summary(record) -> dict:
    """A concise, model-metadata-sized inspection summary — never the full
    `GeometryInspectionReport` (that's available separately via
    `GET /api/models/{model_id}/inspection`). See
    docs/bible/16-geometry-inspection/README.md's model-metadata contract."""

    report = record.inspection_report
    production_ids = set(report.assemblyResult.productionConnectivity.nodes)
    production_solid_count = sum(
        r.solidCount or 0 for r in report.componentResults if r.componentId in production_ids
    )
    return {
        "status": report.status,
        "version": report.inspectionVersion,
        "componentCount": report.assemblyResult.componentCount,
        "productionSolidCount": production_solid_count,
        "disconnectedProductionGroups": report.assemblyResult.productionConnectivity.disconnectedGroupCount,
        "diagnosticsCount": len(report.diagnostics),
    }


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
            "inspection": _inspection_summary(record),
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
        inspection=_inspection_summary(record),
        validation=record.validation_results,
    )


@router.get("/api/models/{model_id}/inspection")
def model_inspection(model_id: str) -> GeometryInspectionReport:
    # The full GeometryInspectionReport, separate from the concise summary
    # embedded in /generate and /metadata — see docs/bible/16-geometry-inspection/
    # README.md's "why a separate endpoint" decision.
    model_service = _get_model_service()
    return model_service.inspection_report(model_id)


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
    checksum = sha256_checksum(path)
    # The exported file is a unique per-request temp file (see
    # ModelService.export_step_file); delete it once the response has
    # finished streaming so temp files never accumulate.
    return FileResponse(
        path,
        media_type="application/step",
        filename=filename,
        headers={"X-Content-SHA256": checksum},
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
    checksum = sha256_checksum(path)
    return FileResponse(
        path,
        media_type="model/stl",
        filename=filename,
        headers={"X-Content-SHA256": checksum},
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


@router.post("/api/designer/interpret", response_model=DesignerResult)
def designer_interpret_route(request: NaturalLanguageDesignRequest) -> DesignerResult:
    # Constructed per-request, not cached module-level: get_designer_provider()
    # re-reads environment configuration every call, which keeps this route
    # honest about provider availability without requiring a process restart
    # in dev/test setups that toggle DESIGNER_PROVIDER/ANTHROPIC_API_KEY.
    from jewelmind.designer.provider import get_designer_provider

    service = DesignerService(provider=get_designer_provider())
    return service.interpret(request)


@router.post("/api/conversation/turn", response_model=ConversationResult)
def conversation_turn_route(request: ConversationTurnRequest) -> ConversationResult:
    # Same per-request construction rationale as designer_interpret_route:
    # honest about provider availability, no server-persisted session
    # (Conversation Engine is stateless per request — the caller's own
    # `request.session` round-trip carries turn history; see
    # docs/bible/14-conversation/373-conversation-session-lifecycle.md).
    from jewelmind.designer.provider import get_designer_provider

    designer_service = DesignerService(provider=get_designer_provider())
    engine = ConversationEngine(designer_service=designer_service)
    return engine.process_turn(request)


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


@router.post("/api/professional-validation/review-package")
def review_package_route(payload: ReviewPackageRequest) -> FileResponse:
    # This is a Professional Validation Framework (Sprint 13) endpoint, not
    # an ordinary Foundry export — it packages CURRENT real artifacts for a
    # human reviewer, never a placeholder. See
    # docs/bible/15-professional-validation/426-review-package-contract.md.
    # Staleness protection (never packaging an out-of-date currentDefinition)
    # is the same frontend gate every other export button already uses
    # (isStale in useProjectStore) — the backend has no independent concept
    # of "stale" since model_id IS the content hash of what was generated.
    model_service = _get_model_service()
    record = model_service.get_record(payload.modelId)
    zip_path, manifest = build_review_package(
        model_service,
        payload.modelId,
        case_id=payload.caseId,
        include_stone_reference=payload.includeStoneReference,
    )
    base_name = sanitize_filename(record.definition.project.name, default="jewelmind-review")
    filename = f"{base_name}-review-package.zip"
    checksum = sha256_checksum(zip_path)
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=filename,
        headers={"X-Content-SHA256": checksum, "X-Package-Id": manifest.packageId},
        background=BackgroundTask(_delete_file, zip_path),
    )
