"""Bar setting generator (Sprint 27).

WHAT A BAR SETTING IS HERE. A set of transverse bars across a run, with the
stones sitting between adjacent bars. Real prisms, one per bar, fused into one
component.

THE SEPARATION THAT MATTERS. A bar setting has two halves that are easy to
conflate: the BARS (retention, this module's job) and WHERE THE STONES SIT
(placement, the Stone Arrangement Engine's job). Conflating them is how a
second placement engine appears — so this module places bars at a stated
spacing along a stated axis and records which arrangement instances they hold,
and it never derives a stone position from a bar position or the reverse.

WHY THE DEFAULT IS TWO BARS. One bar retains nothing on its own, and the
smallest configuration that holds a single stone is one bar on each side of it.
With `barSpacingMm` unset that is exactly what is built, derived from the
stone's own measured extent — the single-stone case, not a degenerate one.

NO INVENTED PROFESSIONAL THRESHOLD. No minimum bar width, no minimum spacing,
no judgment about whether the bars would hold. Every dimension is a
CONSTRUCTION PARAMETER from the document (SETTING-GOV-010).
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

#: The component every bar setting produces.
#:
#: ONE COMPONENT FOR EVERY BAR, not one per bar, for the reason
#: `retention.py::PAVE_RETENTION_COMPONENT` documents at length: forty
#: individually named bars would give Geometry Inspection an intersection matrix
#: that grows with the bar count, and would put forty entries in every manifest
#: for one structural role. Each bar's own position is carried in this
#: component's metadata instead (INSPECT-GOV-015).
BAR_COMPONENT = "bars"


def generate_bar_setting(
    definition: SettingDefinition,
) -> tuple[dict[str, GeneratedComponent], SettingGeometryResult]:
    if definition.bar is None:
        raise SettingGenerationFailedError(
            "A bar setting was requested without bar parameters."
        )

    stone = definition.stone
    bar = definition.bar
    attachment = definition.attachment

    status = compatibility_status("bar", stone.shape)
    if status == "UNSUPPORTED":
        raise SettingStoneCombinationUnsupportedError(
            f"Bar setting is not supported for stone shape {stone.shape!r}. "
            "This is an explicit refusal, never a silent substitution of "
            "another setting family."
        )

    axis = bar.axisDeg
    along_extent = stone_extent_along(stone, axis)
    spacing = (
        bar.barSpacingMm
        if bar.barSpacingMm is not None
        else along_extent + bar.barWidthMm
    )
    length = (
        bar.barLengthMm
        if bar.barLengthMm is not None
        else stone_extent_along(stone, axis + 90.0)
    )

    bottom = base_z(attachment) + bar.offsetZMm
    top = stone.girdlePlaneZMm + bar.barHeightMm + bar.offsetZMm
    center_x = stone.centerXMm + bar.offsetXMm
    center_y = stone.centerYMm + bar.offsetYMm
    dx, dy = axis_direction(axis)

    # Bars are distributed symmetrically about the run's centre, so an even
    # count straddles the stone and an odd count puts one bar over its middle.
    # Both are legitimate configurations; the symmetric distribution is what
    # makes the result independent of which end a reader counts from.
    count = bar.barCount
    if bar.symmetry == "SYMMETRIC":
        positions = [(index - (count - 1) / 2.0) * spacing for index in range(count)]
    else:
        # ASYMMETRIC puts the first bar ON the stone's centre and runs the rest
        # along the axis. A real geometric difference, which is what keeps
        # `symmetry` from being a label nothing reads.
        positions = [index * spacing for index in range(count)]

    pieces = [
        oriented_prism(
            center_x + dx * offset,
            center_y + dy * offset,
            bottom,
            top,
            bar.barWidthMm,
            length,
            axis,
        )
        for offset in positions
    ]

    shape = fuse_all(pieces, "Bar construction")

    metadata = {
        "settingType": "bar",
        "settingModeId": definition.settingModeId,
        "stoneShape": stone.shape,
        "compatibilityStatus": status,
        "axisDeg": axis,
        "requestedBarCount": count,
        "generatedBarCount": len(pieces),
        "barWidthMm": bar.barWidthMm,
        "barLengthMm": length,
        "barLengthSource": (
            "REQUESTED" if bar.barLengthMm is not None else "STONE_EXTENT"
        ),
        "barHeightMm": bar.barHeightMm,
        "barSpacingMm": spacing,
        "barSpacingSource": (
            "REQUESTED" if bar.barSpacingMm is not None else "STONE_EXTENT"
        ),
        # Every bar's own offset along the run, so a consumer never has to
        # re-derive the distribution to know where a bar is.
        "barOffsetsMm": positions,
        "symmetry": bar.symmetry,
        "barBottomZMm": bottom,
        "barTopZMm": top,
        "solidCount": len(shape.Solids()),
        "stoneInstanceIds": list(bar.stoneInstanceIds),
    }

    component = GeneratedComponent(
        name=BAR_COMPONENT,
        shape=shape,
        volume_mm3=shape.Volume(),
        bounding_box=BoundingBox.from_shape(shape),
        warnings=[],
        metadata=metadata,
    )

    result = family_result(
        definition,
        [component],
        status,
        stone_instance_ids=bar.stoneInstanceIds,
        requestedBarCount=count,
        generatedBarCount=len(pieces),
    )
    return {BAR_COMPONENT: component}, result
