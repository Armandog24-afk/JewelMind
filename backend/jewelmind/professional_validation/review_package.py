"""Generates a real Professional Review Package for a generated model.

A review package is a ZIP of CURRENT, REAL JewelMind artifacts (STEP, STL,
canonical JDL JSON, technical specification, the real Forge validation
report, real geometry metadata, and an empty reviewer observation form) —
never a placeholder, never fabricated geometry values. This is separate
from, and does not replace, Foundry's ordinary per-artifact export
endpoints (`/api/models/export/step` etc.) — see
docs/bible/15-professional-validation/426-review-package-contract.md.

Nothing generated here ever claims professional validation has occurred;
the review form explicitly asks the reviewer to supply real evidence, and
the README explicitly says current software validation is not
manufacturability certification.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from jewelmind import __version__
from jewelmind.domain.schema import SCHEMA_VERSION
from jewelmind.professional_validation.errors import ReviewPackageGenerationFailedError
from jewelmind.professional_validation.schemas import ReviewPackageFile, ReviewPackageManifest

if TYPE_CHECKING:
    from jewelmind.services.model_service import ModelRecord, ModelService

_FORGE_REGISTRY_PATH = (
    Path(__file__).resolve().parents[3] / "specs" / "forge" / "v1" / "current-rule-registry.json"
)


def _forge_registry_version() -> str:
    try:
        data = json.loads(_FORGE_REGISTRY_PATH.read_text(encoding="utf-8"))
        return str(data.get("registryVersion", "unknown"))
    except OSError:
        return "unknown"


def _readme_text(*, case_id: str, project_name: str, definition_hash: str, include_stone: bool) -> str:
    stone_note = (
        "The stone reference solid IS included in this package's STEP/STL files, "
        "to help you assess the setting — it is a non-metal reference geometry, not "
        "production metal, and must never be manufactured as metal."
        if include_stone
        else "The stone reference solid is NOT included in this package's STEP/STL "
        "files — only production metal is present."
    )
    return f"""# JewelMind Professional Review Package

## What JewelMind is

JewelMind is a parametric jewelry CAD prototype. It generates preliminary
solid models from a small set of structured design parameters. It is
software-generated geometry — it has never been reviewed by a jewelry
professional as manufacturing-ready, and this package does not claim
otherwise.

## What you are being asked to evaluate

Review case: `{case_id}`
Design name: {project_name}
Definition hash: `{definition_hash}`

Please evaluate the enclosed model on its own terms: as a starting point
for professional jewelry CAD work, not as a finished, production-ready
design. There is no need to be diplomatic — the most useful feedback
tells us plainly what is wrong, missing, or would need to be rebuilt.

## Known prototype limitations

- Prong and basket geometry is deliberately simplified — this is an early
  parametric prototype, not a finished setting design.
- No seat/bearing cutting strategy has been professionally reviewed.
- Only round stones and prong settings currently exist in JewelMind.
- Manufacturing-method selection (casting vs. resin printing) is
  currently metadata/context only — no manufacturing-specific geometry
  adjustment happens yet.
- {stone_note}

## Current software validation does not constitute manufacturability certification

JewelMind runs automated geometric and dimensional checks ("Forge
diagnostics", included in this package as `forge-report.json`) before a
model can even be generated. These are software checks, not professional
judgment — see `forge-report.json` for the exact rules and their current
status. None of them, and no automated test in JewelMind's own codebase,
constitutes a professional validation of any kind.

## How to record feedback

Use `review-form.md` in this package. It is intentionally open-ended —
please write directly on it, or reference it in your own notes. There is
no scoring system; a rejection or a "needs substantial rework" answer is
just as valuable as an acceptance.

## Package contents

See `manifest.json` for the complete file list with checksums.
"""


def _review_form_text(*, case_id: str) -> str:
    return f"""# JewelMind Review Form — case `{case_id}`

Reviewer name:
Reviewer professional role:
Review date:

## Questions

- Is the band geometry suitable as a professional starting point?
- Are the prongs positioned in a manner consistent with practical setting workflows?
- What essential prong/seat geometry is missing?
- Is the basket structurally plausible?
- Are component transitions appropriate?
- Does the STEP file import at expected scale?
- Are production-metal components organized usefully?
- Which portions would you rebuild before manufacturing?
- Which current JewelMind assumptions are incorrect?
- Which issues are blocking versus merely stylistic?

## Open observations

(Add as many as needed — one per finding, however small.)

## Overall assessment

(Free text — there is no scoring system. A clear "not ready, here's why" is a
complete and valuable answer.)
"""


def _geometry_metadata(record: ModelRecord) -> dict:
    gm = record.generated_model
    return {
        "definitionHash": gm.definition_hash,
        "generatorVersion": gm.generator_version,
        "generationDurationSeconds": gm.generation_duration_s,
        "componentVolumesMm3": gm.component_volumes(),
        "combinedMetalVolumeMm3": gm.combined_metal_volume_mm3,
        "boundingBoxMm": gm.bounding_box.as_dict(),
        "warnings": gm.warnings,
    }


def _forge_report(record: ModelRecord) -> dict:
    return {
        "forgeRegistryVersion": _forge_registry_version(),
        "results": [r.model_dump() for r in record.validation_results],
        "hasErrors": any(r.severity == "error" for r in record.validation_results),
    }


def build_review_package(
    model_service: ModelService,
    model_id: str,
    *,
    case_id: str,
    include_stone_reference: bool = True,
) -> tuple[Path, ReviewPackageManifest]:
    """Builds a review-package ZIP for an already-generated model.

    Returns `(zip_path, manifest)`. The caller owns cleanup of `zip_path`
    (mirrors every other export in `ModelService` — see
    `api/routes.py::_delete_file`).
    """

    record = model_service.get_record(model_id)
    generated_at = datetime.now(UTC).isoformat()

    exported_step: Path | None = None
    exported_stl: Path | None = None
    try:
        exported_step = model_service.export_step_file(model_id, include_stone=include_stone_reference)
        exported_stl = model_service.export_stl_file(model_id, include_stone=include_stone_reference)
        jdl_text = model_service.export_json_text(model_id)
        spec_text = model_service.export_specification_text(model_id)

        readme_text = _readme_text(
            case_id=case_id,
            project_name=record.definition.project.name,
            definition_hash=record.generated_model.definition_hash,
            include_stone=include_stone_reference,
        )
        review_form_text = _review_form_text(case_id=case_id)
        forge_report = _forge_report(record)
        geometry_metadata = _geometry_metadata(record)
        component_manifest = {
            name: {"file": entry.get("file"), "geometryRole": entry.get("geometryRole")}
            for name, entry in record.preview_manifest.items()
        }

        entries: dict[str, bytes] = {
            "README.md": readme_text.encode("utf-8"),
            "review-form.md": review_form_text.encode("utf-8"),
            "design.json": jdl_text.encode("utf-8"),
            "technical-specification.md": spec_text.encode("utf-8"),
            "forge-report.json": (json.dumps(forge_report, indent=2, sort_keys=True) + "\n").encode("utf-8"),
            "geometry-metadata.json": (
                json.dumps(geometry_metadata, indent=2, sort_keys=True) + "\n"
            ).encode("utf-8"),
            "component-manifest.json": (
                json.dumps(component_manifest, indent=2, sort_keys=True) + "\n"
            ).encode("utf-8"),
            # Real runtime geometric facts (Sprint 14) — never presented as
            # approval, only as evidence a reviewer can consult. See
            # docs/bible/16-geometry-inspection/README.md's "Inspection +
            # Professional Validation" integration note.
            "geometry-inspection.json": (
                record.inspection_report.model_dump_json(indent=2) + "\n"
            ).encode("utf-8"),
            "model.step": exported_step.read_bytes(),
            "model.stl": exported_stl.read_bytes(),
        }

        included_files = []
        for name, content in sorted(entries.items()):
            digest = hashlib.sha256(content).hexdigest()
            included_files.append(ReviewPackageFile(name=name, sha256=digest, sizeBytes=len(content)))

        package_id = f"review-package-{model_id}-{case_id}"
        manifest = ReviewPackageManifest(
            packageId=package_id,
            caseId=case_id,
            generatedAt=generated_at,
            sourceDefinitionHash=record.generated_model.definition_hash,
            jdlVersion=SCHEMA_VERSION,
            compilerVersion=__version__,
            forgeVersion=_forge_registry_version(),
            atlasVersion=record.generated_model.generator_version,
            includedFiles=included_files,
            checksums={f.name: f.sha256 for f in included_files},
            missingOptionalFiles=[
                "presentation.png (Vision capture is browser-only; not produced by the backend)"
            ],
            knownLimitations=[
                "Prong/basket geometry is a simplified prototype, not a reviewed setting design.",
                "No external CAD import of this exact package has been professionally verified.",
            ],
        )
        entries["manifest.json"] = (manifest.model_dump_json(indent=2) + "\n").encode("utf-8")

        fd, raw_zip_path = tempfile.mkstemp(prefix=f"jewelmind_{model_id}_review_", suffix=".zip")
        os.close(fd)
        zip_path = Path(raw_zip_path)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, content in entries.items():
                zf.writestr(name, content)

        return zip_path, manifest
    except Exception as exc:  # noqa: BLE001 - any failure maps to one honest error
        raise ReviewPackageGenerationFailedError(f"Review package generation failed: {exc}") from exc
    finally:
        if exported_step is not None:
            exported_step.unlink(missing_ok=True)
        if exported_stl is not None:
            exported_stl.unlink(missing_ok=True)
