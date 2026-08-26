"""Pairwise minimum-distance inspection.

Uses `cadquery.Shape.distance()` (a thin wrapper around OCP's
`BRepExtrema_DistShapeShape`, multi-threaded) — verified real and cheap
(single-digit-to-tens of milliseconds per pair on every current solitaire
component pair) during this Sprint's investigation. See
docs/bible/16-geometry-inspection/472-component-distance-model.md. Never
defines an "acceptable" jewelry distance — only measures a real one.
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.geometry.inspection.models import DistanceResult
from jewelmind.geometry.inspection.version import CONTACT_TOLERANCE_MM


def inspect_distance(name_a: str, shape_a: cq.Shape, name_b: str, shape_b: cq.Shape) -> DistanceResult:
    try:
        value = shape_a.distance(shape_b)
    except Exception:  # noqa: BLE001 - a kernel distance failure must not crash the pipeline
        return DistanceResult(
            componentA=name_a,
            componentB=name_b,
            minDistanceMm=None,
            status="ERROR",
            tolerance=CONTACT_TOLERANCE_MM,
        )

    return DistanceResult(
        componentA=name_a,
        componentB=name_b,
        minDistanceMm=value,
        status="PASS",
        tolerance=CONTACT_TOLERANCE_MM,
    )
