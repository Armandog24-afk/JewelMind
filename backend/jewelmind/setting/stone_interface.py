"""Stone -> Setting interface (brief section 20).

Builds the kernel-neutral `StoneSettingReference` a Setting is allowed to
consume, from a real generated stone component plus its `StoneSpec`. This
is the ONLY place Setting reads stone facts, which is what keeps
SETTING-GOV-003 enforceable: a Setting consumes these facts and never
redefines stone geometry.

Depends on the Stone System's public contracts (`domain/stone_dimensions.py`,
`geometry/stone/outline.py`) — never on Stone builder internals, and never
on `jewelmind.ring`.
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.domain.schema import StoneSpec
from jewelmind.domain.stone_dimensions import (
    resolved_depth_mm,
    resolved_length_mm,
    resolved_width_mm,
)
from jewelmind.geometry.model import GeneratedComponent
from jewelmind.geometry.stone import outline as stone_outline
from jewelmind.setting.models import StoneSettingReference

#: Shapes that are bilaterally symmetric about BOTH horizontal midplanes.
#: `pear` is deliberately absent — it is symmetric about one axis only, and
#: a placement strategy must not assume otherwise (SETTING-GOV-008).
_BILATERALLY_SYMMETRIC_SHAPES: frozenset[str] = frozenset(
    {"round", "oval", "emerald", "cushion", "princess", "marquise"}
)

#: Shapes with a distinguished tip, and the local-Y direction it points at
#: `orientation = 0`. Sourced from the real outline construction in
#: `geometry/stone/outline.py` (pear starts at `(0, +half_length)`).
_TIP_DIRECTION_Y: dict[str, float] = {"pear": +1.0}

#: The outline builders, keyed by shape. Round takes a radius; every other
#: shape takes half-length/half-width. Mirrors
#: `geometry/stone/builder.py::_NON_ROUND_OUTLINE_BUILDERS` plus round.
_OUTLINE_BUILDERS = {
    "oval": stone_outline.oval_outline,
    "marquise": stone_outline.marquise_outline,
    "pear": stone_outline.pear_outline,
    "emerald": stone_outline.emerald_outline,
    "princess": stone_outline.princess_outline,
    "cushion": stone_outline.cushion_outline,
}


def build_stone_setting_reference(
    stone: StoneSpec,
    component: GeneratedComponent,
    stone_id: str = "stone_reference",
) -> StoneSettingReference:
    """Extract the Setting-consumable facts from a real generated stone."""

    bb = component.bounding_box
    girdle_z = float(component.metadata["girdleZMm"])

    return StoneSettingReference(
        stoneId=stone_id,
        shape=stone.shape,
        lengthMm=resolved_length_mm(stone),
        widthMm=resolved_width_mm(stone),
        depthMm=resolved_depth_mm(stone),
        orientationDeg=stone.orientation,
        girdlePlaneZMm=girdle_z,
        centerXMm=(bb.xmin + bb.xmax) / 2,
        centerYMm=(bb.ymin + bb.ymax) / 2,
        boundingBoxMinMm=(bb.xmin, bb.ymin, bb.zmin),
        boundingBoxMaxMm=(bb.xmax, bb.ymax, bb.zmax),
        isBilaterallySymmetric=stone.shape in _BILATERALLY_SYMMETRIC_SHAPES,
        tipDirectionY=_TIP_DIRECTION_Y.get(stone.shape),
    )


def girdle_outline_wire(reference: StoneSettingReference) -> cq.Wire:
    """The stone's own girdle outline, as a closed planar wire at Z=0.

    This is the authoritative bezel path (brief section 17) and the source
    of cardinal anchors for shape-aware prong placement. It calls the real
    Stone System outline primitives rather than re-deriving a silhouette,
    so a future custom outline flows through the same pipeline
    (brief section 19).

    The wire is returned in the stone's own unrotated local frame; callers
    apply `orientationDeg` themselves so a rotated stone and its setting
    rotate together.
    """

    if reference.shape == "round":
        return stone_outline.round_outline(reference.widthMm / 2, 1.0)

    builder = _OUTLINE_BUILDERS.get(reference.shape)
    if builder is None:  # pragma: no cover - StoneShape is a closed enum
        raise KeyError(f"No outline builder registered for stone shape {reference.shape!r}")
    return builder(reference.lengthMm / 2, reference.widthMm / 2, 1.0)
