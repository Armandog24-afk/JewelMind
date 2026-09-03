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
    ProngStyle,
    SettingComponentFact,
    SettingDefinition,
    SettingGeometryResult,
)
from jewelmind.setting.placement import prong_positions
from jewelmind.setting.prong_styles import build_prong_solid

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

    # POSITIONS: derived from the stone, or stated explicitly (Sprint 23).
    #
    # Never a mix of the two. A caller either states every position or none of
    # them, because a layout half-derived from a strategy and half-overridden
    # has no determinate meaning — and the strategy that produced the other
    # half would silently depend on how many were overridden.
    assignments_by_index: dict[int, list[str]] = {}
    if prong.positionSource == "EXPLICIT":
        if not prong.positions:
            raise SettingGenerationFailedError(
                "A prong setting with positionSource='EXPLICIT' supplied no "
                "positions. Raised rather than falling back to the derived "
                "strategy, which would build a layout the caller did not ask for."
            )
        positions = [(spec.xMm, spec.yMm) for spec in prong.positions]
        strategy = prong.placementStrategy
        generated_count = len(positions)
        assignments_by_index = {
            index: list(spec.servesStoneInstanceIds)
            for index, spec in enumerate(prong.positions)
        }
    else:
        positions, strategy = prong_positions(
            stone, generated_count, prong_r, prong.placementStrategy
        )

    # STYLE per prong: a group may override the setting-wide style, which is
    # what makes "the two prongs at the tip are V prongs, the rest are round"
    # expressible without a second setting.
    style_by_index: dict[int, ProngStyle] = {}
    for group in prong.groups:
        if group.style is None:
            continue
        for index in group.positionIndices:
            if not 0 <= index < len(positions):
                raise SettingGenerationFailedError(
                    f"Prong group {group.groupId!r} names position index "
                    f"{index}, but only {len(positions)} prongs were placed. "
                    "Raised rather than ignoring the index, which would apply a "
                    "style the caller requested to nothing."
                )
            style_by_index[index] = group.style

    solids = []
    styles_used: list[ProngStyle] = []
    for index, (x, y) in enumerate(positions):
        style = style_by_index.get(index, prong.style)
        styles_used.append(style)
        solids.append(
            build_prong_solid(
                style, x, y, base_z, height, prong_r, prong.tipRatio
            )
        )

    compound = cq.Compound.makeCompound(solids) if solids else cq.Compound.makeCompound([])
    total_volume = sum(s.Volume() for s in solids)

    warnings: list[str] = []
    if prong.positionSource == "DERIVED" and requested_count != generated_count:
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
        # Sprint 23 facts. Reported per prong rather than only setting-wide, so
        # a mixed-style layout is legible downstream without re-deriving it.
        "prongStyle": prong.style,
        "positionSource": prong.positionSource,
        "stylesUsed": list(styles_used),
        "tipRatio": prong.tipRatio,
        "sharedProngCount": sum(
            1 for ids in assignments_by_index.values() if len(ids) > 1
        ),
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
        prongStyle=prong.style,
        seatMode=None,
        # THE SETTING -> STONE MAPPING (Sprint 23). Deterministic, and by ID
        # rather than by position: a consumer asks which stones this component
        # grips instead of inferring it from coordinates. The union of every
        # prong's own assignment, sorted so the value is stable.
        stoneInstanceAssignments={
            "prongs": sorted(
                {
                    instance_id
                    for ids in assignments_by_index.values()
                    for instance_id in ids
                }
            )
        },
    )

    return {"prongs": component}, result
