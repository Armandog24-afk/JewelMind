"""Tension setting generator (Sprint 27).

WHAT IS BUILT. Two opposing supports, one on each side of the stone along a
stated grip axis, each rising from the attachment plane past the stone's girdle
plane, and each reaching inward past the stone's own edge so the seat cut
leaves a real groove. Two real prisms, one component, and the grooves are the
existing `REFERENCE_SEAT` relief — the stone used as a cutting tool, never
fused (LAW-006, SETTINGV2-GOV-008).

WHAT IS DELIBERATELY NOT BUILT, AND THIS IS THE POINT OF THIS MODULE'S
DOCSTRING. A real tension setting's entire function is STRUCTURAL: the stone is
held by the elastic force two shoulders apply to it, and whether a given
geometry holds a given stone depends on the alloy, the cross-section, the work
hardening and the setter's execution. This module computes none of that. It
places two supports where a document says, and it makes NO claim that:

    - the supports would grip the stone;
    - the metal's spring-back is sufficient, or survivable;
    - the configuration is safe under load, wear or impact;
    - the geometry is manufacturable as a tension setting at all.

So the capability registry records this mode as PARTIAL with
`professionalReviewRequirement: REQUIRED`, and the result record carries the
same requirement so it travels with the geometry rather than living only in
documentation. That is not a validation verdict and never becomes one: it says
a qualified human must look, not that anyone has (PROVAL-GOV-006/007).

NO STRESS THRESHOLD IS INVENTED. There is no minimum shoulder section here, no
maximum span, no spring constant and no safety factor. Every dimension is a
CONSTRUCTION PARAMETER from the document; `padDepthMm` is a GEOMETRIC
ROBUSTNESS overlap in the class of `constants.EMBED_MM` and is explicitly not a
grip depth (SETTING-GOV-010, LAW-010).
"""

from __future__ import annotations

from jewelmind.geometry.model import BoundingBox, GeneratedComponent
from jewelmind.setting.capability import compatibility_status
from jewelmind.setting.errors import (
    SettingGenerationFailedError,
    SettingStoneCombinationUnsupportedError,
)
from jewelmind.setting.frame import (
    axis_direction,
    base_z,
    fuse_all,
    oriented_prism,
    stone_extent_along,
)
from jewelmind.setting.models import SettingDefinition, SettingGeometryResult
from jewelmind.setting.result import family_result

#: The component every tension setting produces.
TENSION_COMPONENT = "tension_supports"

#: How many opposing supports a tension setting builds.
#:
#: Two, and it is not a parameter. "Tension" names a pair of supports in
#: opposition; three supports in opposition is a different structure, and giving
#: this a count would let a document ask for one support — which would hold
#: nothing and would still be reported as a tension setting.
TENSION_SUPPORT_COUNT = 2


def generate_tension_setting(
    definition: SettingDefinition,
) -> tuple[dict[str, GeneratedComponent], SettingGeometryResult]:
    if definition.tension is None:
        raise SettingGenerationFailedError(
            "A tension setting was requested without tension parameters."
        )

    stone = definition.stone
    tension = definition.tension
    attachment = definition.attachment

    status = compatibility_status("tension", stone.shape)
    if status == "UNSUPPORTED":
        raise SettingStoneCombinationUnsupportedError(
            f"Tension setting is not supported for stone shape "
            f"{stone.shape!r}. This is an explicit refusal, never a silent "
            "substitution of another setting family."
        )

    axis = tension.gripAxisDeg
    half_extent = stone_extent_along(stone, axis) / 2.0
    if tension.padDepthMm >= half_extent:
        raise SettingGenerationFailedError(
            f"The tension supports' inward reach ({tension.padDepthMm} mm) is "
            f"not less than half the stone's extent along the grip axis "
            f"({half_extent:.4f} mm), so the two supports would meet through "
            "the middle of the stone. A geometric precondition, not a statement "
            "about how deeply a stone may be gripped."
        )

    bottom = base_z(attachment) + tension.offsetZMm
    top = stone.girdlePlaneZMm + tension.gripHeightMm + tension.offsetZMm
    center_x = stone.centerXMm + tension.offsetXMm
    center_y = stone.centerYMm + tension.offsetYMm
    dx, dy = axis_direction(axis)

    # Each support's INNER face sits `padDepthMm` inside the stone's edge, so
    # the support genuinely overlaps the stone's volume and the seat cut leaves a
    # groove rather than a tangent touch. Its centre is therefore half a
    # thickness further out than that face.
    center_offset = half_extent - tension.padDepthMm + tension.padThicknessMm / 2.0

    pieces = [
        oriented_prism(
            center_x + dx * sign * center_offset,
            center_y + dy * sign * center_offset,
            bottom,
            top,
            tension.padThicknessMm,
            tension.padWidthMm,
            axis,
        )
        for sign in (1.0, -1.0)
    ]

    shape = fuse_all(pieces, "Tension support construction")

    metadata = {
        "settingType": "tension",
        "settingModeId": definition.settingModeId,
        "stoneShape": stone.shape,
        "compatibilityStatus": status,
        "gripAxisDeg": axis,
        "supportCount": TENSION_SUPPORT_COUNT,
        "padWidthMm": tension.padWidthMm,
        "padThicknessMm": tension.padThicknessMm,
        "padDepthMm": tension.padDepthMm,
        "gripHeightMm": tension.gripHeightMm,
        "padCenterOffsetMm": center_offset,
        "stoneHalfExtentAlongGripAxisMm": half_extent,
        "supportBottomZMm": bottom,
        "supportTopZMm": top,
        "solidCount": len(shape.Solids()),
        "recessOperation": "CUT_STONE_FROM_METAL",
        "recessSource": "setting.seat",
        # THE HONEST CLAIM, carried on the component itself rather than only in
        # documentation. Nothing downstream may read this geometry as a
        # structural statement.
        "structuralBehaviourModelled": False,
        "professionalReviewRequirement": "REQUIRED",
    }

    component = GeneratedComponent(
        name=TENSION_COMPONENT,
        shape=shape,
        volume_mm3=shape.Volume(),
        bounding_box=BoundingBox.from_shape(shape),
        warnings=[
            "Tension setting geometry models the opposing supports only. The "
            "structural behaviour that makes a tension setting hold a stone is "
            "not modelled, and this geometry is not a statement that it would. "
            "Professional review is required."
        ],
        metadata=metadata,
    )

    result = family_result(
        definition,
        [component],
        status,
        diagnostics=list(component.warnings),
        professionalReviewRequirement="REQUIRED",
    )
    return {TENSION_COMPONENT: component}, result
