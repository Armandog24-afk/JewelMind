"""Stone-seat relief: metal removed where the stone sits (Sprint 23).

A CUT, NEVER A FUSE, and the distinction is the whole reason this module can
exist at all.

LAW-006 and ATLAS-GOV-011 forbid the stone shape from ever reaching a
fuse/union of production metal, because a stone unioned into the metal body
would be exported as metal and quoted as metal. Using the stone as a CUTTING
TOOL is the opposite operation: metal is removed, the stone contributes no
material, and the stone solid is discarded the moment the cut returns. Nothing
here calls `.fuse()` on a stone shape, and `test_setting_v2.py` asserts that
structurally.

WHAT THIS IS NOT. It is not a cut seat with a bearing shoulder, not a bright
cut, and not a setter's seat of any kind. It is REFERENCE relief: the metal no
longer occupies the stone's volume, which is enough for a preview to read
correctly and for a volume figure to stop double-counting the intersection. No
claim is made that a stone would sit correctly in it, and `SeatMode` is
`REFERENCE_SEAT` rather than `SEAT` for exactly that reason.

OPT-IN, AND OFF BY DEFAULT. Applying relief changes prong and head volumes, so
`SeatMode.NONE` remains the default and every pre-Sprint-23 design keeps its
geometry byte-identically.
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.geometry.model import BoundingBox, GeneratedComponent
from jewelmind.setting.errors import SettingGenerationFailedError
from jewelmind.setting.models import SeatSettingDefinition


def _grown_tool(stone_shape: cq.Shape, clearance_mm: float) -> cq.Shape:
    """The cutting tool: the stone solid, grown by `clearance_mm`.

    Grown rather than used as-is because a boolean cut between two exactly
    tangent surfaces is where OCCT is least reliable — the same reasoning
    behind `embedMm` in the attachment interface. A GEOMETRIC ROBUSTNESS value,
    not a setting tolerance.

    Implemented as a uniform scale about the stone's own bounding-box centre.
    An offset/thicken would be more faithful and is markedly less robust on a
    faceted solid; the scale is documented here rather than presented as an
    exact clearance.
    """

    if clearance_mm <= 0.0:
        return stone_shape

    box = stone_shape.BoundingBox()
    span = max(box.xlen, box.ylen, box.zlen)
    if span <= 0.0:
        raise SettingGenerationFailedError(
            "Seat relief cannot size a cutting tool from a stone with zero extent."
        )
    factor = (span + 2.0 * clearance_mm) / span

    center = cq.Vector(
        (box.xmin + box.xmax) / 2.0,
        (box.ymin + box.ymax) / 2.0,
        (box.zmin + box.zmax) / 2.0,
    )
    # Scale about the centre: translate to the origin, scale, translate back.
    # `Shape.scale()` scales about the global origin, which would also displace
    # a stone that does not sit there.
    return (
        stone_shape.translate(center * -1.0).scale(factor).translate(center)
    )


def apply_seat_relief(
    component: GeneratedComponent,
    stone_shape: cq.Shape,
    seat: SeatSettingDefinition,
) -> tuple[GeneratedComponent, list[str]]:
    """Cut the stone's volume out of one metal component.

    Returns the relieved component and any diagnostics. A failed cut RAISES
    rather than returning the uncut component: reporting `REFERENCE_SEAT` while
    delivering unrelieved metal would be the silent substitution
    SETTING-GOV-013 forbids.
    """

    if seat.mode == "NONE":
        return component, []

    tool = _grown_tool(stone_shape, seat.clearanceMm)

    try:
        relieved = component.shape.cut(tool)
    except Exception as exc:  # noqa: BLE001 - OCC boolean failures vary widely
        raise SettingGenerationFailedError(
            f"Seat relief failed while cutting the stone volume out of "
            f"{component.name!r}: {exc}. Raised rather than returning unrelieved "
            "metal, which would report a seat that is not there."
        ) from exc

    if not relieved.Solids():
        raise SettingGenerationFailedError(
            f"Seat relief consumed the whole {component.name!r} component: the "
            "stone volume covers all of it. This is a real geometric conflict, "
            "reported rather than silently skipped."
        )

    volume = relieved.Volume()
    removed = component.volume_mm3 - volume
    diagnostics: list[str] = []
    if removed <= 0.0:
        # A no-op cut is a fact worth reporting: the stone and this component
        # do not overlap at all, so the requested seat changed nothing.
        diagnostics.append(
            f"Seat relief removed no material from {component.name!r}; the stone "
            "volume does not intersect it."
        )

    metadata = {
        **component.metadata,
        "seatMode": seat.mode,
        "seatClearanceMm": seat.clearanceMm,
        "seatRemovedVolumeMm3": removed,
        # An explicit, checkable statement of the operation performed, so no
        # reader has to trust that a cut rather than a fuse was used.
        "seatOperation": "CUT_STONE_FROM_METAL",
    }

    return (
        GeneratedComponent(
            name=component.name,
            shape=relieved,
            volume_mm3=volume,
            bounding_box=BoundingBox.from_shape(relieved),
            warnings=[*component.warnings, *diagnostics],
            metadata=metadata,
        ),
        diagnostics,
    )
