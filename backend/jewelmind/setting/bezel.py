"""Bezel setting generator (brief sections 16-19).

Real parametric B-Rep construction, derived from the stone's own girdle
outline — never a frontend visualization, never a ring around the origin,
never a scaled mesh. The pipeline is deliberately **outline-agnostic**
(brief section 19): it takes whatever closed wire the Stone System produces
and offsets it, so a future custom outline flows through unchanged rather
than needing an `if round / elif oval` branch.

    stone girdle outline
      -> constant geometric offset (cq.Wire.offset2D)
      -> STEP-safety repair of the offset wire (see below)
      -> annular face (outer wire with the stone outline as its hole)
      -> linear extrusion over the wall's vertical extent
      -> validity check

## The one real geometry-engine accommodation

`Wire.offset2D()` produces a genuine constant-distance offset. For a wire
made of lines and circular arcs the result is again lines and arcs, which
OpenCascade's STEP writer round-trips exactly. For an **ellipse** the
offset of an ellipse is not an ellipse: OCCT represents it with edges whose
`geomType()` is `"OFFSET"`, and an extruded `OFFSET`-curve surface does NOT
survive a STEP write/read cycle — it re-imports as a `Shell` with zero
solids, which `step_roundtrip_check()` correctly flags.

Verified per shape before implementing (offset edge `geomType()` sets):

    round     CIRCLE          -> CIRCLE
    oval      ELLIPSE         -> OFFSET        <- the only affected case
    emerald   LINE            -> CIRCLE, LINE
    princess  LINE            -> CIRCLE, LINE
    cushion   CIRCLE, LINE    -> CIRCLE, LINE
    marquise  CIRCLE          -> CIRCLE
    pear      CIRCLE, LINE    -> CIRCLE, LINE

So the repair is triggered by the real **curve type**, not by a shape name:
any offset wire containing an `OFFSET` edge is resampled into an explicit
periodic B-spline. That keeps the true constant-offset geometry (measured
deviation ~0.006% of volume) while producing a STEP-safe representation,
and it leaves the crisp corners of the angular shapes untouched — blanket
resampling was rejected precisely because it rounds those corners.

Rejected alternative: expanding the ellipse's semi-axes by the wall
thickness instead of offsetting. It exports cleanly but is not a constant
offset, so the wall would be thinner at the ends than at the sides.
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.geometry.model import BoundingBox, GeneratedComponent
from jewelmind.setting.capability import compatibility_status
from jewelmind.setting.errors import (
    BezelOutlineFailedError,
    BezelSolidInvalidError,
    SettingGenerationFailedError,
    SettingStoneCombinationUnsupportedError,
)
from jewelmind.setting.models import (
    SettingComponentFact,
    SettingDefinition,
    SettingFallbackEvent,
    SettingGeometryResult,
)
from jewelmind.setting.stone_interface import girdle_outline_wire

#: Edge geometry type whose extruded surface does not survive a STEP
#: round-trip in the installed OpenCascade. See the module docstring.
_STEP_UNSAFE_GEOM_TYPE = "OFFSET"

#: Samples used when resampling a STEP-unsafe offset wire into a periodic
#: B-spline. 96 was verified sufficient: the resulting solid round-trips
#: through STEP with a volume delta below 1e-11 mm3, and its volume differs
#: from the true offset by ~0.006%.
_RESAMPLE_POINTS = 96


def _needs_step_safety_repair(wire: cq.Wire) -> bool:
    return any(edge.geomType() == _STEP_UNSAFE_GEOM_TYPE for edge in wire.Edges())


def _resample_periodic(wire: cq.Wire, samples: int = _RESAMPLE_POINTS) -> cq.Wire:
    points = []
    for k in range(samples):
        p = wire.positionAt(k / samples)
        points.append((p.x, p.y))
    return cq.Workplane("XY").spline(points, periodic=True).close().val()


def _offset_outline(inner: cq.Wire, thickness_mm: float) -> tuple[cq.Wire, list[SettingFallbackEvent]]:
    """Offset the stone outline outward, repairing STEP-unsafe curve types."""

    try:
        offset = inner.offset2D(thickness_mm)
    except Exception as exc:  # noqa: BLE001 - OCC offset failures vary
        raise BezelOutlineFailedError(
            f"Could not offset the stone girdle outline by {thickness_mm} mm ({exc})."
        ) from exc

    outer = offset[0] if isinstance(offset, list) else offset
    if outer is None:
        raise BezelOutlineFailedError(
            f"Offsetting the stone girdle outline by {thickness_mm} mm produced no wire."
        )

    events: list[SettingFallbackEvent] = []
    if _needs_step_safety_repair(outer):
        outer = _resample_periodic(outer)
        events.append(
            SettingFallbackEvent(
                stage="bezel_outline_offset",
                reason=(
                    f"The offset outline contained {_STEP_UNSAFE_GEOM_TYPE} curve edges, whose "
                    "extruded surface does not survive a STEP round-trip; it was resampled into "
                    f"a periodic B-spline over {_RESAMPLE_POINTS} points. Geometry-engine "
                    "accommodation, not a design choice."
                ),
            )
        )

    return outer, events


def generate_bezel_setting(
    definition: SettingDefinition,
) -> tuple[dict[str, GeneratedComponent], SettingGeometryResult]:
    if definition.bezel is None:
        raise SettingGenerationFailedError(
            "A bezel setting was requested without bezel parameters."
        )

    stone = definition.stone
    bezel = definition.bezel
    attachment = definition.attachment

    status = compatibility_status("bezel", stone.shape)
    if status == "UNSUPPORTED":
        raise SettingStoneCombinationUnsupportedError(
            f"Bezel setting is not supported for stone shape {stone.shape!r}. "
            "This is an explicit refusal, never a silent substitution of another setting."
        )

    inner = girdle_outline_wire(stone)
    if stone.orientationDeg:
        inner = inner.rotate((0, 0, 0), (0, 0, 1), stone.orientationDeg)

    outer, fallback_events = _offset_outline(inner, bezel.wallThicknessMm)

    # Vertical extent: centred on the stone's girdle plane. An explicit,
    # symmetric rule — no fabricated crown/pavilion coverage split
    # (SETTING-GOV-010).
    half_height = bezel.wallHeightMm / 2
    bottom_z = stone.girdlePlaneZMm - half_height
    top_z = stone.girdlePlaneZMm + half_height

    try:
        face = cq.Face.makeFromWires(outer, [inner])
        solid = cq.Solid.extrudeLinear(face, cq.Vector(0, 0, bezel.wallHeightMm))
        solid = solid.translate((0, 0, bottom_z))
    except Exception as exc:  # noqa: BLE001 - OCC construction failures vary
        raise BezelSolidInvalidError(
            f"Could not construct the bezel wall for stone shape {stone.shape!r} "
            f"(thickness={bezel.wallThicknessMm}, height={bezel.wallHeightMm}): {exc}. "
            "This is a real construction failure, never downgraded to another setting family."
        ) from exc

    if not solid.Solids() or not solid.isValid():
        raise BezelSolidInvalidError(
            f"The bezel wall for stone shape {stone.shape!r} produced no valid solid."
        )

    bbox = BoundingBox.from_shape(solid)
    metadata = {
        "settingType": "bezel",
        "stoneShape": stone.shape,
        "compatibilityStatus": status,
        "wallThicknessMm": bezel.wallThicknessMm,
        "wallHeightMm": bezel.wallHeightMm,
        "verticalReference": bezel.verticalReference,
        "outlineOffsetMode": bezel.outlineOffsetMode,
        "girdlePlaneZMm": stone.girdlePlaneZMm,
        "wallBottomZMm": bottom_z,
        "wallTopZMm": top_z,
        "outlineSource": "stone_girdle_outline",
        "stepSafetyRepairApplied": bool(fallback_events),
    }

    component = GeneratedComponent(
        name="bezel",
        shape=solid,
        volume_mm3=solid.Volume(),
        bounding_box=bbox,
        warnings=[e.reason for e in fallback_events],
        metadata=metadata,
    )

    result = SettingGeometryResult(
        settingId=definition.settingId,
        settingType="bezel",
        generatedComponents=["bezel"],
        productionComponents=["bezel"],
        referenceComponents=[],
        attachmentInterfaces=[attachment],
        geometryFacts=[
            SettingComponentFact(
                componentId="bezel",
                solidCount=len(solid.Solids()),
                volumeMm3=solid.Volume(),
                boundingBoxMinMm=(bbox.xmin, bbox.ymin, bbox.zmin),
                boundingBoxMaxMm=(bbox.xmax, bbox.ymax, bbox.zmax),
            )
        ],
        fallbackEvents=fallback_events,
        compatibilityStatus=status,
    )

    return {"bezel": component}, result
