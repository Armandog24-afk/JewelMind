"""Pairwise intersection inspection.

Uses `cadquery.Shape.intersect()` (a thin wrapper around OCP's
`BRepAlgoAPI_Common`) — verified real during this Sprint's investigation,
but noticeably more expensive than distance (tens to roughly a thousand
milliseconds per pair on current solitaire components, depending on
solid complexity — see docs/bible/16-geometry-inspection/484-inspection-performance-model.md).

Zero intersection volume does not by itself mean "no geometric
relationship" — two shapes that merely touch at a surface can report a
positive `distance()` of exactly 0 with a near-zero or zero boolean
common volume. Callers that already know two shapes are separated by a
real positive distance should skip calling this at all (broad-phase
elimination) — see `should_skip_intersection()`.
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.geometry.inspection.models import IntersectionResult
from jewelmind.geometry.inspection.version import CONTACT_TOLERANCE_MM

_NOTE = (
    "Positive intersection volume confirms real 3D overlap. A NO_INTERSECTION "
    "result with a distance of exactly 0 can still mean the shapes touch at a "
    "surface with zero enclosed volume — see 471-component-intersection-model.md."
)


def should_skip_intersection(min_distance_mm: float | None, tolerance: float = CONTACT_TOLERANCE_MM) -> bool:
    """True when a prior distance measurement already proves the pair is
    separated by more than a kernel contact tolerance — broad-phase
    elimination so the more expensive boolean-common operation is only
    run for pairs that are actually touching or overlapping."""

    return min_distance_mm is not None and min_distance_mm > tolerance


def inspect_intersection(
    name_a: str, shape_a: cq.Shape, name_b: str, shape_b: cq.Shape, *, known_separated: bool = False
) -> IntersectionResult:
    if known_separated:
        return IntersectionResult(
            componentA=name_a,
            componentB=name_b,
            status="NO_INTERSECTION",
            intersectionVolumeMm3=0.0,
            intersectionSolidCount=0,
            tolerance=CONTACT_TOLERANCE_MM,
            note="Skipped the boolean-common operation: a prior distance measurement "
            "already proved this pair is separated beyond the contact tolerance.",
        )

    try:
        result = shape_a.intersect(shape_b)
    except Exception:  # noqa: BLE001 - a kernel boolean failure must not crash the pipeline
        return IntersectionResult(
            componentA=name_a,
            componentB=name_b,
            status="UNKNOWN",
            tolerance=CONTACT_TOLERANCE_MM,
            note="The boolean-common operation itself failed; see diagnostics.",
        )

    solids = result.Solids()
    volume = result.Volume() if solids else 0.0

    if not solids or volume <= CONTACT_TOLERANCE_MM:
        status = "NO_INTERSECTION" if not solids else "TOUCHES"
    else:
        status = "INTERSECTS"

    return IntersectionResult(
        componentA=name_a,
        componentB=name_b,
        status=status,
        intersectionVolumeMm3=volume,
        intersectionSolidCount=len(solids),
        tolerance=CONTACT_TOLERANCE_MM,
        note=_NOTE,
    )
