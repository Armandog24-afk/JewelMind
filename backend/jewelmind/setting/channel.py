"""Channel setting generator (Sprint 27).

WHAT A CHANNEL IS HERE. Two parallel walls with the stones between them,
running along a direction in the stone's own horizontal frame. The walls are
real prisms: a channel is never a groove drawn on a surface, never a line in a
preview, and never a bezel renamed.

WHAT IT DELIBERATELY IS NOT. It is not a placement engine. A channel spanning a
row of stones takes its LENGTH from `spanMm` and records which arrangement
instances it holds; it never computes where those stones are. The Stone
Arrangement Engine resolved them, and a second opinion about a stone's position
would surface as geometry that does not match the preview (ARRANGE-GOV-006).
That is why `stoneInstanceIds` is a list of opaque strings and why this module
does not import `jewelmind.arrangement` (SETTINGV2-GOV-011).

THE SINGLE-STONE CASE IS THE DEFAULT, NOT A DEGENERATE ONE. With `spanMm` and
`innerWidthMm` unset, the run is exactly as long and as wide as the design's own
stone — a channel-set solitaire, which is a real configuration and the one a
document that says nothing more means. Longer runs are stated, because only the
document knows how many stones the row carries.

NO INVENTED PROFESSIONAL THRESHOLD. No minimum wall thickness, no minimum
clearance between a wall and a stone, and no judgment about whether a setter
could close the channel. Each of those needs sourced professional evidence this
project does not have, so none is asserted (SETTING-GOV-010). Whether a wall
actually touches a stone is a GEOMETRIC fact, reported by Geometry Inspection.
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

#: The component every channel setting produces.
CHANNEL_COMPONENT = "channel_walls"


def generate_channel_setting(
    definition: SettingDefinition,
) -> tuple[dict[str, GeneratedComponent], SettingGeometryResult]:
    if definition.channel is None:
        raise SettingGenerationFailedError(
            "A channel setting was requested without channel parameters."
        )

    stone = definition.stone
    channel = definition.channel
    attachment = definition.attachment

    status = compatibility_status("channel", stone.shape)
    if status == "UNSUPPORTED":
        raise SettingStoneCombinationUnsupportedError(
            f"Channel setting is not supported for stone shape {stone.shape!r}. "
            "This is an explicit refusal, never a silent substitution of "
            "another setting family."
        )

    axis = channel.axisDeg
    # The run's own extents, resolved from the stone when the document left them
    # unstated. Reading the stone's measured box is exactly what
    # SETTING-GOV-003 sanctions; inventing a millimetre default would be a
    # construction choice the author never made.
    span = channel.spanMm if channel.spanMm is not None else stone_extent_along(stone, axis)
    inner_width = (
        channel.innerWidthMm
        if channel.innerWidthMm is not None
        else stone_extent_along(stone, axis + 90.0)
    )

    wall = channel.wallThicknessMm
    bottom = base_z(attachment) + channel.offsetZMm
    top = stone.girdlePlaneZMm + channel.wallHeightMm + channel.offsetZMm

    # SYMMETRY (Sprint 27). A symmetric run is centred on the stone; an
    # asymmetric one STARTS at the stone's centre and extends along the axis, so
    # its own centre sits half a span further out. A real geometric difference,
    # which is what keeps `symmetry` from being a label nothing reads.
    along_dx, along_dy = axis_direction(axis)
    run_shift = 0.0 if channel.symmetry == "SYMMETRIC" else span / 2.0
    center_x = stone.centerXMm + channel.offsetXMm + along_dx * run_shift
    center_y = stone.centerYMm + channel.offsetYMm + along_dy * run_shift

    # Each wall's centre sits half a clear width plus half a wall thickness away
    # from the run's centreline, so the CLEAR distance between the walls is
    # exactly `innerWidthMm` — the quantity a document states, rather than a
    # centre-to-centre distance a reader would have to convert.
    across_offset = inner_width / 2.0 + wall / 2.0
    dx, dy = axis_direction(axis + 90.0)

    pieces = [
        oriented_prism(
            center_x + dx * sign * across_offset,
            center_y + dy * sign * across_offset,
            bottom,
            top,
            span,
            wall,
            axis,
        )
        for sign in (1.0, -1.0)
    ]

    end_caps = 0
    if channel.termination == "CLOSED_ENDS":
        # A cap spans the full outer width so it genuinely meets both walls'
        # material. A cap only as wide as the clear span would touch each wall
        # along a face, which is where OCCT booleans are least reliable.
        cap_across = inner_width + 2.0 * wall
        along_offset = span / 2.0 - wall / 2.0
        for sign in (1.0, -1.0):
            pieces.append(
                oriented_prism(
                    center_x + along_dx * sign * along_offset,
                    center_y + along_dy * sign * along_offset,
                    bottom,
                    top,
                    wall,
                    cap_across,
                    axis,
                )
            )
            end_caps += 1

    shape = fuse_all(pieces, "Channel wall construction")

    metadata = {
        "settingType": "channel",
        "settingModeId": definition.settingModeId,
        "stoneShape": stone.shape,
        "compatibilityStatus": status,
        "axisDeg": axis,
        "spanMm": span,
        "spanSource": "REQUESTED" if channel.spanMm is not None else "STONE_EXTENT",
        "innerWidthMm": inner_width,
        "innerWidthSource": (
            "REQUESTED" if channel.innerWidthMm is not None else "STONE_EXTENT"
        ),
        "wallThicknessMm": wall,
        "wallHeightMm": channel.wallHeightMm,
        "wallCount": 2,
        "endCapCount": end_caps,
        "termination": channel.termination,
        "symmetry": channel.symmetry,
        "runShiftMm": run_shift,
        "wallBottomZMm": bottom,
        "wallTopZMm": top,
        "solidCount": len(shape.Solids()),
        "stoneInstanceIds": list(channel.stoneInstanceIds),
    }

    component = GeneratedComponent(
        name=CHANNEL_COMPONENT,
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
        stone_instance_ids=channel.stoneInstanceIds,
    )
    return {CHANNEL_COMPONENT: component}, result
