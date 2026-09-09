"""Shared construction frame for the Sprint 27 setting families.

WHY ONE MODULE RATHER THAN A HELPER COPIED FOUR TIMES. `channel.py`, `bar.py`,
`flush.py` and `tension.py` all place prisms in the STONE'S OWN HORIZONTAL
FRAME: a direction in the XY plane, an extent along it, an extent across it,
and a vertical span anchored on the stone's girdle plane. Four copies of that
rotation would be four chances for one family's axis convention to drift from
another's, and a channel and the bars crossing it disagreeing about which way
is "along" would be invisible until someone looked at the solid.

EVERY FUNCTION HERE IS PURE GEOMETRY. Nothing reads a jewelry category, a band,
a ring size or a JDL document, and nothing states a dimension of its own: the
extents arrive as arguments. There is no constant in this module at all, which
is the simplest possible answer to "does it invent a threshold?"
(SETTING-GOV-010).

THE VERTICAL ANCHOR IS THE ATTACHMENT INTERFACE, NEVER A DERIVED HEIGHT.
`base_z()` reproduces the expression `head.py` and `prong.py` already use —
`attachmentPlaneZMm - embedMm` — so every Sprint 27 family sinks past the
attachment plane by exactly the amount the existing families do, and the fuse
into the host produces the same genuine 3D overlap rather than a tangent touch
(SETTING-GOV-014).
"""

from __future__ import annotations

import math

import cadquery as cq

from jewelmind.setting.errors import SettingGenerationFailedError
from jewelmind.setting.models import (
    SettingAttachmentInterface,
    StoneSettingReference,
)


def axis_direction(axis_deg: float) -> tuple[float, float]:
    """Unit vector of a horizontal direction, in the design's XY plane."""

    radians = math.radians(axis_deg)
    return math.cos(radians), math.sin(radians)


def stone_extent_along(stone: StoneSettingReference, axis_deg: float) -> float:
    """How far the stone reaches along a horizontal direction.

    MEASURED FROM THE STONE'S REAL BOUNDING BOX, not from `lengthMm`/`widthMm`.
    Those are the REQUESTED dimensions in the stone's own unrotated frame; the
    bounding box is the as-built extent of the solid that actually exists, so it
    already accounts for `orientationDeg` and for any shape whose outline does
    not fill its nominal box. Sprint 20 found four shapes whose requested and
    measured dimensions disagreed, which is exactly why the measured value is
    the one to use.

    For an axis-aligned box the extent along a direction is the box's support
    width, `|dx| * sizeX + |dy| * sizeY` — exact, not an approximation.
    """

    dx, dy = axis_direction(axis_deg)
    size_x = stone.boundingBoxMaxMm[0] - stone.boundingBoxMinMm[0]
    size_y = stone.boundingBoxMaxMm[1] - stone.boundingBoxMinMm[1]
    return abs(dx) * size_x + abs(dy) * size_y


def crown_height_mm(stone: StoneSettingReference) -> float:
    """How far the stone rises above its own girdle plane.

    A real measurement of the generated solid. Used by the flush family to
    refuse a rim that would bury the stone entirely — a geometric precondition,
    never a professional setting depth.
    """

    return stone.boundingBoxMaxMm[2] - stone.girdlePlaneZMm


def base_z(attachment: SettingAttachmentInterface) -> float:
    """The Z every family's geometry starts at.

    The same expression `head.py::_basket()` and `prong.py` use, stated once so
    a Sprint 27 family can never sink a different amount than a prong does.
    """

    return attachment.attachmentPlaneZMm - attachment.embedMm


def oriented_prism(
    center_x: float,
    center_y: float,
    bottom_z: float,
    top_z: float,
    along_mm: float,
    across_mm: float,
    axis_deg: float,
) -> cq.Shape:
    """One rectangular prism, oriented in the stone's horizontal frame.

    Built at the origin and then rotated and translated, in that order. Rotating
    about the GLOBAL Z axis before translating is what keeps the rotation about
    the prism's OWN centre: rotating after the translation would swing the prism
    around the design origin instead, which is the precise mistake Sprint 24
    documented for `cadquery.Shape.scale()` (FAMILY-GOV, "scale about the
    stone's OWN centre").

    Raises on a non-positive extent rather than producing a degenerate solid the
    kernel would later fail a boolean on.
    """

    height = top_z - bottom_z
    if along_mm <= 0 or across_mm <= 0 or height <= 0:
        raise SettingGenerationFailedError(
            f"A setting prism was requested with a non-positive extent "
            f"(along={along_mm}, across={across_mm}, height={height}). Raised "
            "rather than building a degenerate solid, which would fail a later "
            "boolean with a far less legible message."
        )

    prism = cq.Solid.makeBox(
        along_mm,
        across_mm,
        height,
        pnt=cq.Vector(-along_mm / 2.0, -across_mm / 2.0, bottom_z),
    )
    if axis_deg:
        prism = prism.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), axis_deg)
    return prism.translate((center_x, center_y, 0.0))


def fuse_all(solids: list[cq.Shape], stage: str) -> cq.Shape:
    """Fuse a family's pieces into one shape.

    RAISES on failure rather than returning the pieces it managed to join:
    reporting a two-wall channel while delivering one wall would be the silent
    substitution SETTING-GOV-013 forbids.
    """

    if not solids:
        raise SettingGenerationFailedError(
            f"{stage} produced no solids to fuse."
        )
    fused = solids[0]
    for solid in solids[1:]:
        try:
            fused = fused.fuse(solid)
        except Exception as exc:  # noqa: BLE001 - OCC boolean failures vary
            raise SettingGenerationFailedError(
                f"{stage} failed while fusing its pieces: {exc}. Raised rather "
                "than returning a partial structure, which would report metal "
                "that is not there."
            ) from exc
    if not fused.Solids():
        raise SettingGenerationFailedError(
            f"{stage} fused to no solids."
        )
    return fused
