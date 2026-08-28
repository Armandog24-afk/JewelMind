"""Human-readable technical specification export (Markdown)."""

from __future__ import annotations

from jewelmind.domain.disclaimer import PROFESSIONAL_REVIEW_NOTICE
from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.inspection.models import GeometryInspectionReport
from jewelmind.geometry.model import GeneratedModel
from jewelmind.validation.rules import ValidationResult


def _fmt_mm(value: float) -> str:
    return f"{value:.3f} mm"


def build_specification(
    definition: JewelryDefinition,
    model: GeneratedModel,
    validation_results: list[ValidationResult],
    generated_at: str,
    inspection_report: GeometryInspectionReport | None = None,
) -> str:
    """Render the Markdown specification.

    `generated_at` must be the timestamp captured when the model was
    originally generated (see ModelRecord.generated_at in
    services/model_service.py) — NOT the current time. Downloading the same
    specification twice must produce the same "Generated at" value; only the
    content of the file should ever change, and only if the underlying
    model changes.
    """

    bb = model.bounding_box

    lines: list[str] = []
    lines.append(f"# Technical Specification — {definition.project.name}")
    lines.append("")
    lines.append(f"- Schema version: {definition.schemaVersion}")
    lines.append(f"- Generator version: {model.generator_version}")
    lines.append(f"- Generated at: {generated_at}")
    lines.append(f"- Definition hash: {model.definition_hash}")
    lines.append(f"- Units: {definition.project.units}")
    lines.append("")

    lines.append("## Ring")
    lines.append(f"- Size system: {definition.ring.sizeSystem}")
    lines.append(f"- Size: {definition.ring.size:g}")
    lines.append(f"- Inner diameter: {_fmt_mm(definition.ring.innerDiameter)}")
    lines.append("")

    lines.append("## Band")
    lines.append(f"- Profile: {definition.band.profile}")
    lines.append(f"- Width: {_fmt_mm(definition.band.width)}")
    lines.append(f"- Thickness: {_fmt_mm(definition.band.thickness)}")
    lines.append("")

    lines.append("## Stone (reference only, not a gemological reproduction)")
    lines.append(f"- Shape: {definition.stone.shape}")
    if definition.stone.shape == "round":
        lines.append(f"- Diameter: {_fmt_mm(definition.stone.diameter)}")
    else:
        lines.append(f"- Length: {_fmt_mm(definition.stone.length)}")
        lines.append(f"- Width: {_fmt_mm(definition.stone.width)}")
        lines.append(f"- Orientation: {definition.stone.orientation:g} deg")
    lines.append(f"- Depth: {_fmt_mm(definition.stone.depth)}")
    lines.append("")

    lines.append("## Setting")
    lines.append(f"- Type: {definition.setting.type}")
    if definition.setting.type == "prong":
        lines.append(f"- Prong count: {definition.setting.prongCount}")
        lines.append(f"- Prong diameter: {_fmt_mm(definition.setting.prongDiameter)}")
        lines.append(f"- Prong height: {_fmt_mm(definition.setting.prongHeight)}")
    else:
        lines.append(f"- Bezel wall thickness: {_fmt_mm(definition.setting.bezelWallThickness)}")
        lines.append(f"- Bezel wall height: {_fmt_mm(definition.setting.bezelWallHeight)}")
    lines.append(f"- Basket height: {_fmt_mm(definition.setting.basketHeight)}")

    setting_result = getattr(model, "setting_result", None)
    if setting_result is not None:
        lines.append(f"- Generated setting components: {', '.join(setting_result.generatedComponents)}")
        if setting_result.settingType == "prong":
            lines.append(
                f"- Prong count requested/generated: "
                f"{setting_result.requestedProngCount}/{setting_result.generatedProngCount}"
            )
            lines.append(f"- Prong placement strategy: {setting_result.placementStrategy}")
        lines.append(
            f"- Setting/stone compatibility: {setting_result.compatibilityStatus} "
            f"(software capability status — NOT a professional approval)"
        )
        lines.append(
            "- Professional validation of this setting: NOT_REVIEWED. No qualified "
            "human review of this setting geometry has taken place."
        )
        if setting_result.compatibilityStatus == "EXPERIMENTAL":
            lines.append(
                "- NOTE: this stone/setting combination is EXPERIMENTAL. The setting "
                "geometry generates, but its placement is a provisional software "
                "layout that has not been optimized for this stone shape."
            )
        for event in setting_result.fallbackEvents:
            lines.append(f"- Geometry fallback ({event.stage}): {event.reason}")
    lines.append("")

    lines.append("## Material & manufacturing")
    lines.append(f"- Metal: {definition.material.metal}")
    lines.append(f"- Manufacturing method: {definition.manufacturing.method}")
    lines.append("")

    lines.append("## Model volumes")
    for name, component in model.components.items():
        lines.append(f"- {name}: {component.volume_mm3:.2f} mm³")
    lines.append(f"- Combined metal (band + prongs + basket): {model.combined_metal_volume_mm3:.2f} mm³")
    lines.append("")

    lines.append("## Bounding box (mm)")
    lines.append(f"- X: {bb.xmin:.2f} to {bb.xmax:.2f}")
    lines.append(f"- Y: {bb.ymin:.2f} to {bb.ymax:.2f}")
    lines.append(f"- Z: {bb.zmin:.2f} to {bb.zmax:.2f}")
    lines.append("")

    lines.append("## Validation results")
    if not validation_results:
        lines.append("- No validation findings.")
    else:
        for r in validation_results:
            lines.append(f"- [{r.severity.upper()}] {r.ruleId} ({r.parameter}): {r.message}")
    lines.append("")

    lines.append("## Known generation warnings")
    if not model.warnings:
        lines.append("- None recorded for this generation run.")
    else:
        for w in model.warnings:
            lines.append(f"- {w}")
    lines.append("")

    if inspection_report is not None:
        lines.append("## Geometry inspection summary")
        lines.append(f"- Inspection status: {inspection_report.status}")
        lines.append(f"- Inspection version: {inspection_report.inspectionVersion}")
        connectivity = inspection_report.assemblyResult.productionConnectivity
        if connectivity.isFullyConnected:
            connectivity_summary = "fully connected"
        else:
            connectivity_summary = f"{connectivity.disconnectedGroupCount} disconnected group(s)"
        lines.append(f"- Production connectivity: {connectivity_summary}")
        # PRONG_ONLY (Sprint 19): a bezel has no prongs, and reporting
        # "0 vs. 0" would read as a defect rather than as not-applicable.
        prong_count = inspection_report.assemblyResult.prongCount
        if prong_count.status != "NOT_APPLICABLE":
            lines.append(
                f"- Requested vs. generated prong count: "
                f"{prong_count.requestedCount} vs. {prong_count.generatedCount}"
            )
        lines.append(
            "- This is a geometric fact summary, not a manufacturability or "
            "professional-quality assessment — see docs/bible/16-geometry-inspection/."
        )
        lines.append("")

    lines.append("## Professional review disclaimer")
    lines.append(PROFESSIONAL_REVIEW_NOTICE)
    lines.append("")

    return "\n".join(lines)
