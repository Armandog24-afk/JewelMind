"""Orchestrates validation, geometry generation, preview, and export.

Holds an in-memory registry of generated models keyed by model ID (the
definition hash). Each generated model owns a temporary directory holding
its preview mesh files; the registry evicts the oldest entries once a cap is
reached and always cleans up the corresponding temp directory, so preview
files do not accumulate unboundedly across a long-running server process.
"""

from __future__ import annotations

import atexit
import shutil
import tempfile
import threading
from collections import OrderedDict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.exporters.json_exporter import export_json
from jewelmind.exporters.specification import build_specification
from jewelmind.exporters.step_exporter import export_step
from jewelmind.exporters.stl_exporter import export_stl
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring
from jewelmind.geometry.model import GeneratedModel
from jewelmind.preview.mesh import write_component_previews
from jewelmind.utils.logging import get_logger
from jewelmind.validation.engine import has_errors, validate_definition
from jewelmind.validation.rules import ValidationResult

logger = get_logger(__name__)

MAX_CACHED_MODELS = 20


@dataclass
class ModelRecord:
    model_id: str
    definition: JewelryDefinition
    generated_model: GeneratedModel
    validation_results: list[ValidationResult]
    preview_manifest: dict
    temp_dir: Path
    generated_at: str


class ModelService:
    def __init__(self) -> None:
        self._records: OrderedDict[str, ModelRecord] = OrderedDict()
        self._lock = threading.Lock()
        atexit.register(self._cleanup_all)

    # -- validation -----------------------------------------------------

    def validate(self, definition: JewelryDefinition) -> list[ValidationResult]:
        return validate_definition(definition)

    # -- generation -------------------------------------------------------

    def generate(self, definition: JewelryDefinition) -> ModelRecord:
        from jewelmind.api.errors import ValidationBlockedError

        results = validate_definition(definition)
        if has_errors(results):
            raise ValidationBlockedError(
                "Definition has validation errors; fix them before generating a model.",
                details=[r.model_dump() for r in results],
            )

        generated_model = build_solitaire_ring(definition)
        model_id = generated_model.definition_hash

        temp_dir = Path(tempfile.mkdtemp(prefix=f"jewelmind_{model_id}_"))
        preview_manifest = write_component_previews(generated_model, definition, temp_dir)

        record = ModelRecord(
            model_id=model_id,
            definition=definition,
            generated_model=generated_model,
            validation_results=results,
            preview_manifest=preview_manifest,
            temp_dir=temp_dir,
            generated_at=datetime.now(UTC).isoformat(),
        )

        with self._lock:
            if model_id in self._records:
                # Same input regenerated: replace, discarding the old temp dir.
                self._evict(model_id)
            self._records[model_id] = record
            self._records.move_to_end(model_id)
            self._enforce_cap()

        logger.info(
            "model_generated",
            model_id=model_id,
            duration_s=generated_model.generation_duration_s,
            warnings=len(generated_model.warnings),
        )
        return record

    # -- retrieval --------------------------------------------------------

    def get_record(self, model_id: str) -> ModelRecord:
        from jewelmind.api.errors import ModelNotFoundError

        with self._lock:
            record = self._records.get(model_id)
            if record is None:
                raise ModelNotFoundError(f"No generated model found for id '{model_id}'.")
            self._records.move_to_end(model_id)
            return record

    # -- exports ------------------------------------------------------------

    def export_step_file(self, model_id: str, *, include_stone: bool) -> Path:
        record = self.get_record(model_id)
        destination = record.temp_dir / "model.step"
        return export_step(record.generated_model, destination, include_stone=include_stone)

    def export_stl_file(
        self,
        model_id: str,
        *,
        include_stone: bool,
        mesh_tolerance: float | None = None,
        angular_tolerance: float | None = None,
    ) -> Path:
        record = self.get_record(model_id)
        destination = record.temp_dir / "model.stl"
        return export_stl(
            record.generated_model,
            record.definition,
            destination,
            include_stone=include_stone,
            mesh_tolerance=mesh_tolerance,
            angular_tolerance=angular_tolerance,
        )

    def export_json_text(self, model_id: str) -> str:
        record = self.get_record(model_id)
        return export_json(record.definition)

    def export_specification_text(self, model_id: str) -> str:
        record = self.get_record(model_id)
        return build_specification(record.definition, record.generated_model, record.validation_results)

    def preview_file(self, model_id: str, component_name: str) -> Path:
        from jewelmind.api.errors import ModelNotFoundError

        record = self.get_record(model_id)
        entry = record.preview_manifest.get(component_name)
        if entry is None or entry.get("file") is None:
            raise ModelNotFoundError(
                f"No preview mesh available for component '{component_name}' of model '{model_id}'."
            )
        return record.temp_dir / entry["file"]

    # -- cache maintenance --------------------------------------------------

    def _enforce_cap(self) -> None:
        while len(self._records) > MAX_CACHED_MODELS:
            oldest_id = next(iter(self._records))
            self._evict(oldest_id)

    def _evict(self, model_id: str) -> None:
        record = self._records.pop(model_id, None)
        if record is not None:
            shutil.rmtree(record.temp_dir, ignore_errors=True)

    def _cleanup_all(self) -> None:
        with self._lock:
            for model_id in list(self._records.keys()):
                self._evict(model_id)


model_service = ModelService()
