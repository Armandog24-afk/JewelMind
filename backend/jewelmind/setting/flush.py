"""Flush / gypsy setting generator (Sprint 27).

WHAT A FLUSH SETTING IS, GEOMETRICALLY. A stone sunk INTO a mass of metal whose
top surface is level with part of its crown. So it has two halves, and both are
real:

    1. A SOLID COLLAR — the stone's own girdle outline offset outward and
       extruded from the attachment plane up past the girdle by `rimHeightMm`.
    2. A RECESS — the stone's own solid removed from that collar.

THE RECESS IS THE EXISTING SEAT CUT, NOT A NEW OPERATION. `dispatch.py` already
applies `REFERENCE_SEAT` relief to every production component of a setting, and
that path routes through `seat.py` — the module whose own source is asserted
never to call `.fuse()` on a stone shape. Reusing it means the stone is a
CUTTING TOOL here exactly as it is for a prong setting, and never becomes
production metal (LAW-006, SETTINGV2-GOV-008). A bespoke cut in this module
would be a second place the stone meets a boolean, which is precisely what
ATLAS-GOV-011 exists to prevent.

WHICH MAKES RELIEF A PRECONDITION, NOT AN OPTION. Without it the collar
occupies the stone's whole volume and the result is a lump of metal with a stone
buried inside it — not a flush setting, and not anything. So this generator
REFUSES a flush setting with `seatMode="NONE"` rather than building the lump,
and `JM-SETTING-010` reports the same refusal as a validation result before
generation is attempted.

THE OUTLINE OFFSET IS THE BEZEL'S, DELIBERATELY. `bezel.py::offset_stone_outline()`
carries a per-shape-verified repair for offset curves whose extruded surface does
not survive a STEP round-trip. A second offset here would eventually miss that
repair and ship a collar that re-imports as a zero-solid shell.

NO INVENTED PROFESSIONAL THRESHOLD. `collarWidthMm` and `rimHeightMm` are
CONSTRUCTION PARAMETERS from the document. Nothing here states a minimum metal
thickness around a flush-set stone, a burnishing allowance, or whether the
stone would be secure — each needs sourced professional evidence this project
does not have (SETTING-GOV-010).
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.geometry.model import BoundingBox, GeneratedComponent
from jewelmind.setting.bezel import offset_stone_outline
from jewelmind.setting.capability import compatibility_status
from jewelmind.setting.errors import (
    SettingGenerationFailedError,
    SettingStoneCombinationUnsupportedError,
)
from jewelmind.setting.frame import base_z, crown_height_mm
from jewelmind.setting.models import SettingDefinition, SettingGeometryResult
from jewelmind.setting.result import family_result
from jewelmind.setting.stone_interface import girdle_outline_wire

#: The component every flush setting produces.
FLUSH_COMPONENT = "flush_collar"


def generate_flush_setting(
    definition: SettingDefinition,
) -> tuple[dict[str, GeneratedComponent], SettingGeometryResult]:
    if definition.flush is None:
        raise SettingGenerationFailedError(
            "A flush setting was requested without flush parameters."
        )

    stone = definition.stone
    flush = definition.flush
    attachment = definition.attachment

    status = compatibility_status("flush", stone.shape)
    if status == "UNSUPPORTED":
        raise SettingStoneCombinationUnsupportedError(
            f"Flush setting is not supported for stone shape {stone.shape!r}. "
            "This is an explicit refusal, never a silent substitution of "
            "another setting family."
        )

    seat = definition.seat
    if seat is None or seat.mode == "NONE":
        raise SettingGenerationFailedError(
            "A flush setting requires seat relief (setting.seatMode = "
            "'REFERENCE_SEAT'). Without it the collar occupies the stone's "
            "whole volume and the result is a solid mass with the stone buried "
            "inside it. Raised rather than building that, and reported before "
            "generation by JM-SETTING-010."
        )

    crown = crown_height_mm(stone)
    if flush.rimHeightMm >= crown:
        raise SettingGenerationFailedError(
            f"The flush collar's rim height ({flush.rimHeightMm} mm) is not "
            f"below the stone's own crown height ({crown:.4f} mm), so the stone "
            "would be entirely buried and the recess would leave a closed "
            "cavity rather than an opening. A geometric precondition measured "
            "against the real generated stone, not a professional setting "
            "depth."
        )

    inner = girdle_outline_wire(stone)
    if stone.orientationDeg:
        inner = inner.rotate((0, 0, 0), (0, 0, 1), stone.orientationDeg)

    outer, fallback_events = offset_stone_outline(inner, flush.collarWidthMm)

    bottom_z = base_z(attachment) + flush.offsetZMm
    top_z = stone.girdlePlaneZMm + flush.rimHeightMm + flush.offsetZMm
    height = top_z - bottom_z
    if height <= 0:
        raise SettingGenerationFailedError(
            f"The flush collar's vertical extent is {height} mm. The collar "
            "spans from the attachment plane to above the stone's girdle, so a "
            "non-positive extent means the offsets place the top below the "
            "bottom."
        )

    try:
        # A FACE FROM THE OUTER WIRE ALONE — no hole. The recess comes from the
        # seat cut against the real stone solid, which follows the stone's whole
        # 3D profile; extruding a hole from the flat girdle outline would cut a
        # straight-walled bore the stone does not fill.
        face = cq.Face.makeFromWires(outer)
        solid = cq.Solid.extrudeLinear(face, cq.Vector(0, 0, height))
        solid = solid.translate((0, 0, bottom_z))
    except Exception as exc:  # noqa: BLE001 - OCC construction failures vary
        raise SettingGenerationFailedError(
            f"Could not construct the flush collar for stone shape "
            f"{stone.shape!r} (collarWidth={flush.collarWidthMm}, "
            f"rimHeight={flush.rimHeightMm}): {exc}. A real construction "
            "failure, never downgraded to another setting family."
        ) from exc

    if not solid.Solids() or not solid.isValid():
        raise SettingGenerationFailedError(
            f"The flush collar for stone shape {stone.shape!r} produced no "
            "valid solid."
        )

    if flush.offsetXMm or flush.offsetYMm:
        solid = solid.translate((flush.offsetXMm, flush.offsetYMm, 0.0))

    metadata = {
        "settingType": "flush",
        "settingModeId": definition.settingModeId,
        "stoneShape": stone.shape,
        "compatibilityStatus": status,
        "collarWidthMm": flush.collarWidthMm,
        "rimHeightMm": flush.rimHeightMm,
        "stoneCrownHeightMm": crown,
        "collarBottomZMm": bottom_z,
        "collarTopZMm": top_z,
        "outlineSource": "stone_girdle_outline",
        "stepSafetyRepairApplied": bool(fallback_events),
        # An explicit statement that the recess is a cut and where it comes
        # from, so a reader never has to infer it from the seat mode.
        "recessOperation": "CUT_STONE_FROM_METAL",
        "recessSource": "setting.seat",
        "solidCount": len(solid.Solids()),
    }

    component = GeneratedComponent(
        name=FLUSH_COMPONENT,
        shape=solid,
        volume_mm3=solid.Volume(),
        bounding_box=BoundingBox.from_shape(solid),
        warnings=[event.reason for event in fallback_events],
        metadata=metadata,
    )

    result = family_result(
        definition,
        [component],
        status,
        diagnostics=[event.reason for event in fallback_events],
    )
    return {FLUSH_COMPONENT: component}, result.model_copy(
        update={"fallbackEvents": fallback_events}
    )
