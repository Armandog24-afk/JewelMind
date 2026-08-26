"""Topology inspection: solid/shell/face/edge/vertex counts and kernel
validity for one shape.

Topology counts are primarily useful for regression detection and
debugging, not professional interpretation — see
docs/bible/16-geometry-inspection/477-topology-inspection-model.md. This
Sprint's investigation confirmed a reliable kernel-validity check exists
(`cadquery.Shape.isValid()`) and is fast; there is no separate
"NOT_IMPLEMENTED" path for validity itself, but a genuinely unavailable
future check should still report NOT_IMPLEMENTED rather than fabricate a
result (INSPECT-GOV-006/007).
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.geometry.inspection.models import InspectionStatus, TopologyCounts
from jewelmind.geometry.inspection.shape import shape_is_valid, topology_counts


def inspect_topology(shape: cq.Shape) -> tuple[TopologyCounts | None, bool | None, InspectionStatus]:
    """Returns `(counts, is_valid, status)`. `counts`/`is_valid` are `None`
    only if the underlying kernel call itself raised."""

    try:
        counts = topology_counts(shape)
    except Exception:  # noqa: BLE001 - a kernel topology query failure must not crash the pipeline
        return None, None, "ERROR"

    try:
        valid = shape_is_valid(shape)
    except Exception:  # noqa: BLE001 - a kernel validity check failure must not crash the pipeline
        return counts, None, "ERROR"

    return counts, valid, ("PASS" if valid else "FAIL")
