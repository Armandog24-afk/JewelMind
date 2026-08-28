"""Prong setting generator (brief sections 9/14).

Produces the `prongs` component. Round + RADIAL placement reproduces the
pre-Sprint-19 geometry byte-identically (SETTING-GOV-017); non-round shapes
use the shape-aware OUTLINE_CARDINAL strategy from `placement.py`.

Component identity note (brief section 14): prongs remain ONE compound
named `prongs`, unchanged. Splitting them into `prong_0` … `prong_n` would
change `GEOMETRY_ROLE`/`PRODUCTION_ROLE`, every preview manifest, every
export component list, and all 23 Golden baselines — far beyond "the
smallest safe refactor necessary". Individual prong identity is instead
reported as real per-prong facts (positions, count) which is what
inspection actually needs.
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.geometry.model import BoundingBox, GeneratedComponent
from jewelmind.setting.capability import compatibility_status
from jewelmind.setting.errors import (
    SettingGenerationFailedError,
    SettingStoneCombinationUnsupportedError,
)
from jewelmind.setting.models import (
    SettingComponentFact,
    SettingDefinition,
    SettingGeometryResult,
)
from jewelmind.setting.placement import prong_positions

#: Prong counts the generator will build. Matches the real Forge rule
#: `JM-PRONG-001`, which is the authority; kept in sync by test.
SUPPORTED_PRONG_COUNTS: tuple[int, ...] = (4, 6)


def generate_prong_setting(
    definition: SettingDefinition,
) -> tuple[dict[str, GeneratedComponent], SettingGeometryResult]:
    if definition.prong is None:
        raise SettingGenerationFailedError(
            "A prong setting was requested without prong parameters."
        )

    stone = definition.stone
    prong = definition.prong
    attachment = definition.attachment

    status = compatibility_status("prong", stone.shape)
    if status == "UNSUPPORTED":
        raise SettingStoneCombinationUnsupportedError(
            f"Prong setting is not supported for stone shape {stone.shape!r}. "
            "This is an explicit refusal, never a silent substitution of another setting."
        )

    requested_count = prong.prongCount
    generated_count = (
        requested_count if requested_count in SUPPORTED_PRONG_COUNTS else max(requested_count, 0)
    )

    prong_r = prong.prongDiameterMm / 2
    base_z = attachment.attachmentPlaneZMm - attachment.embedMm
    height = prong.prongHeightMm + attachment.embedMm

    positions, strategy = prong_positions(
        stone, generated_count, prong_r, prong.placementStrategy
    )

    solids = []
    for x, y in positions:
        solids.append(
            cq.Workplane("XY")
            .workplane(offset=base_z)
            .center(x, y)
            .circle(prong_r)
            .extrude(height)
            .val()
        )

    compound = cq.Compound.makeCompound(solids) if solids else cq.Compound.makeCompound([])
    total_volume = sum(s.Volume() for s in solids)

    warnings: list[str] = []
    if requested_count != generated_count:
        warnings.append(
            f"Requested prong count {requested_count} is unsupported; generated {generated_count} instead."
        )

    metadata = {
        "settingType": "prong",
        "requestedCount": requested_count,
        "generatedCount": generated_count,
        "prongRadiusMm": prong_r,
        "placementStrategy": strategy,
        "stoneShape": stone.shape,
        "compatibilityStatus": status,
        "positions": [{"x": x, "y": y} for x, y in positions],
        # Preserved for backward compatibility: the pre-Sprint-19 metadata
        # exposed `centerRadiusMm`. Only meaningful for RADIAL placement,
        # where every prong genuinely sits on one circle.
        "centerRadiusMm": (
            (positions[0][0] ** 2 + positions[0][1] ** 2) ** 0.5
            if positions and strategy == "RADIAL"
            else None
        ),
    }

    bbox = BoundingBox.from_shape(compound) if solids else BoundingBox(0, 0, 0, 0, 0, 0)

    component = GeneratedComponent(
        name="prongs",
        shape=compound,
        volume_mm3=total_volume,
        bounding_box=bbox,
        warnings=warnings,
        metadata=metadata,
    )

    result = SettingGeometryResult(
        settingId=definition.settingId,
        settingType="prong",
        generatedComponents=["prongs"],
        productionComponents=["prongs"],
        referenceComponents=[],
        attachmentInterfaces=[attachment],
        geometryFacts=[
            SettingComponentFact(
                componentId="prongs",
                solidCount=len(solids),
                volumeMm3=total_volume,
                boundingBoxMinMm=(bbox.xmin, bbox.ymin, bbox.zmin),
                boundingBoxMaxMm=(bbox.xmax, bbox.ymax, bbox.zmax),
            )
        ],
        diagnostics=list(warnings),
        compatibilityStatus=status,
        requestedProngCount=requested_count,
        generatedProngCount=generated_count,
        placementStrategy=strategy,
    )

    return {"prongs": component}, result
