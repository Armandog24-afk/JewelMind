"""Pavé metal: retention and recess (Sprint 26).

The kernel half of the Ring-side pavé translation. Surface resolution is in
`geometry/pave_surface.py`, split out so Forge can import it without importing
CadQuery.

WHAT THIS MODULE DOES NOT DO. It does not lay out a lattice —
`pave/compile.py` owns that. It does not decide what a bead is —
`setting/retention.py` owns that. It calls both and applies the results to the
ring's real components.
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.geometry.model import GeneratedComponent
from jewelmind.geometry.pave_surface import (
    resolve_pave_surface,
    stone_anchor_z_mm,
)
from jewelmind.pave.models import PaveDefinition
from jewelmind.setting.retention import (
    RetentionAnchorFrame,
    RetentionBuildSpec,
    build_pave_retention,
)

__all__ = [
    "apply_pave_recess",
    "resolve_pave_surface",
    "retention_component",
    "stone_anchor_z_mm",
]


def retention_component(
    pave: PaveDefinition, field
) -> GeneratedComponent | None:
    """The field's retention metal, or `None` when it builds none.

    `field` is a `CompiledPaveField`, typed loosely for the same reason
    `GeneratedModel` types its result objects loosely: this module is in the
    geometry layer and the pavé package must stay importable without it.
    """

    if field is None or not field.enabled:
        return None
    if pave.retention.strategy == "NONE":
        return None

    frames = [
        RetentionAnchorFrame(
            anchorId=anchor.anchorId,
            xMm=anchor.xMm,
            yMm=anchor.yMm,
            zMm=anchor.zMm,
            tiltDeg=anchor.tiltDeg,
            tiltAzimuthDeg=anchor.tiltAzimuthDeg,
            servesPlacementIds=list(anchor.servesPlacementIds),
        )
        for anchor in field.retentionAnchors
    ]
    return build_pave_retention(
        frames,
        RetentionBuildSpec(
            strategy=pave.retention.strategy,
            radiusMm=pave.retention.beadRadiusMm,
            embedMm=pave.retention.beadEmbedMm,
            prongHeightMm=pave.retention.prongHeightMm,
        ),
    )


def apply_pave_recess(
    host: GeneratedComponent,
    pave: PaveDefinition,
    stone_shapes: list[cq.Shape],
) -> tuple[GeneratedComponent, list[str]]:
    """Cut the field's stones out of the host component.

    REUSES `setting/seat.py`, deliberately and not by coincidence: that module
    is the one whose own source is asserted never to call `.fuse()` on a stone
    shape (SETTINGV2-GOV-008), so routing the pavé's recess through it means
    the pavé inherits that guarantee instead of restating it.

    Called a RECESS and not a seat: it has no bearing shoulder and makes no
    claim that a stone would sit correctly in it.
    """

    if pave.seat.mode == "NONE" or not stone_shapes:
        return host, []

    from jewelmind.setting.models import SeatSettingDefinition
    from jewelmind.setting.seat import apply_seat_relief

    seat = SeatSettingDefinition(
        mode="REFERENCE_SEAT", clearanceMm=pave.seat.clearanceMm
    )

    current = host
    diagnostics: list[str] = []
    for shape in stone_shapes:
        current, notes = apply_seat_relief(current, shape, seat)
        diagnostics.extend(notes)

    metadata = {
        **current.metadata,
        "paveRecessMode": pave.seat.mode,
        "paveRecessStoneCount": len(stone_shapes),
        "paveRecessOperation": "CUT_STONE_FROM_METAL",
    }
    return (
        GeneratedComponent(
            name=current.name,
            shape=current.shape,
            volume_mm3=current.volume_mm3,
            bounding_box=current.bounding_box,
            warnings=list(current.warnings),
            metadata=metadata,
        ),
        diagnostics,
    )
