"""Ring band geometry.

The band is a solid of revolution around the global Y axis (see
jewelmind.geometry.constants). Two profiles are supported:

- flat: a rectangular cross-section, with an optional conservative fillet on
  the two outer rim edges.
- comfort_fit: the inner edge is a shallow outward-bulging arc instead of a
  straight line. The minimum inner radius (at the center of the band width)
  is exactly the requested inner radius, and it flares slightly outward
  toward the edges — so the requested finger opening is never reduced.

Fillets on OpenCascade revolved solids are not always robust. If the fillet
operation fails for any reason, the builder falls back to the unfilleted
solid and records a warning rather than failing generation outright.
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.constants import inner_radius, outer_radius
from jewelmind.geometry.model import BoundingBox, GeneratedComponent
from jewelmind.geometry.primitives.selectors import FlatCircleAtRadius

# Comfort-fit inner edge flare, in mm, at the band's Y edges relative to its
# center. Conservative and fixed rather than user-configurable in this
# milestone.
_COMFORT_FLARE_MM = 0.3

# Outer rim fillet radius is capped at 15% of the smallest relevant
# dimension so it never grows large enough to distort thin bands.
_FILLET_FRACTION = 0.15
_FILLET_MAX_MM = 0.25


def _flat_profile_points(inner_r: float, outer_r: float, half_width: float):
    return [
        (inner_r, -half_width),
        (inner_r, half_width),
        (outer_r, half_width),
        (outer_r, -half_width),
    ]


def _build_flat_wire(inner_r: float, outer_r: float, half_width: float) -> cq.Workplane:
    pts = _flat_profile_points(inner_r, outer_r, half_width)
    return cq.Workplane("XY").polyline(pts).close()


def _build_comfort_fit_wire(inner_r: float, outer_r: float, half_width: float) -> cq.Workplane:
    edge_r = inner_r + _COMFORT_FLARE_MM
    return (
        cq.Workplane("XY")
        .moveTo(edge_r, -half_width)
        .threePointArc((inner_r, 0.0), (edge_r, half_width))
        .lineTo(outer_r, half_width)
        .lineTo(outer_r, -half_width)
        .close()
    )


def _try_fillet_outer_rim(solid: cq.Workplane, outer_r: float, fillet_radius: float) -> cq.Workplane:
    selector = FlatCircleAtRadius(outer_r)
    return solid.edges(selector).fillet(fillet_radius)


def build_ring_band(definition: JewelryDefinition) -> GeneratedComponent:
    """Build the metal ring band as a single closed solid.

    Returns a GeneratedComponent named "band". Any fallback taken (e.g. a
    fillet that could not be applied) is recorded in `warnings`.
    """

    warnings: list[str] = []
    inner_r = inner_radius(definition)
    outer_r = outer_radius(definition)
    half_width = definition.band.width / 2

    if definition.band.profile == "flat":
        wire = _build_flat_wire(inner_r, outer_r, half_width)
    else:
        wire = _build_comfort_fit_wire(inner_r, outer_r, half_width)

    solid = wire.revolve(360, (0, 0, 0), (0, 1, 0))

    fillet_radius = min(
        _FILLET_MAX_MM,
        definition.band.width * _FILLET_FRACTION,
        definition.band.thickness * _FILLET_FRACTION,
    )
    fallback_used = False
    if fillet_radius > 0.02:
        try:
            filleted = _try_fillet_outer_rim(solid, outer_r, fillet_radius)
            if not filleted.solids().vals():
                raise ValueError("fillet produced no solid")
            solid = filleted
        except Exception as exc:  # noqa: BLE001 - deliberately broad: OCC fillet failures vary
            fallback_used = True
            warnings.append(
                f"Outer rim fillet could not be applied ({exc}); falling back to sharp edges."
            )

    shape = solid.val()
    volume = shape.Volume()
    metadata = {
        "profile": definition.band.profile,
        "innerRadiusMm": inner_r,
        "outerRadiusMm": outer_r,
        "filletApplied": not fallback_used,
    }

    return GeneratedComponent(
        name="band",
        shape=shape,
        volume_mm3=volume,
        bounding_box=BoundingBox.from_shape(shape),
        warnings=warnings,
        metadata=metadata,
    )
