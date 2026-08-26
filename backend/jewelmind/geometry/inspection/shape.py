"""Pure, read-only shape-level inspection primitives.

Every function here takes a real `cadquery.Shape`/`cq.Compound` and
returns a plain value or a kernel-neutral model — never mutates the
shape, never repairs it (INSPECT-GOV-013/014). All three underlying
operations (`Shape.isValid()`, topology counts, `BoundingBox.from_shape`)
are real CadQuery APIs verified against the installed cadquery==2.8.0 /
OCP build during this Sprint's investigation — see
docs/bible/16-geometry-inspection/466-shape-validity-inspection.md and
477-topology-inspection-model.md for what was actually tested.
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.geometry.inspection.models import BoundingBoxFact, TopologyCounts
from jewelmind.geometry.model import BoundingBox


def solid_count(shape: cq.Shape) -> int:
    return len(shape.Solids())


def shape_is_valid(shape: cq.Shape) -> bool:
    """Wraps `cadquery.Shape.isValid()`, itself a thin wrapper around
    OCP's `BRepCheck_Analyzer` — verified available and fast (single-digit
    milliseconds on every current solitaire component) during this
    Sprint's investigation. See 466-shape-validity-inspection.md."""

    return shape.isValid()


def topology_counts(shape: cq.Shape) -> TopologyCounts:
    return TopologyCounts(
        solids=len(shape.Solids()),
        shells=len(shape.Shells()),
        faces=len(shape.Faces()),
        edges=len(shape.Edges()),
        vertices=len(shape.Vertices()),
    )


def bounding_box_fact(shape: cq.Shape) -> BoundingBoxFact:
    bbox = BoundingBox.from_shape(shape)
    return bounding_box_fact_from_box(bbox)


def bounding_box_fact_from_box(bbox: BoundingBox) -> BoundingBoxFact:
    return BoundingBoxFact(
        xmin=bbox.xmin,
        ymin=bbox.ymin,
        zmin=bbox.zmin,
        xmax=bbox.xmax,
        ymax=bbox.ymax,
        zmax=bbox.zmax,
        sizeX=bbox.xmax - bbox.xmin,
        sizeY=bbox.ymax - bbox.ymin,
        sizeZ=bbox.zmax - bbox.zmin,
        centerX=(bbox.xmin + bbox.xmax) / 2,
        centerY=(bbox.ymin + bbox.ymax) / 2,
        centerZ=(bbox.zmin + bbox.zmax) / 2,
    )
