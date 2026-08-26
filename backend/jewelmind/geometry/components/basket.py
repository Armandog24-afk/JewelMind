"""Basket support geometry: a simplified structural ring connecting the
prongs down to the band.

Implemented as a hollow cylindrical wall (outer radius minus inner radius)
rather than a tapered or decorative structure — a robust first
implementation, per the product spec, rather than a highly decorative one.
The wall's radial thickness is sized to fully embed the prong footprint so
prongs, basket, and band all genuinely overlap in 3D rather than merely
touching at a surface.
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.connection import shank_connection_interface
from jewelmind.geometry.model import BoundingBox, GeneratedComponent

_MIN_INNER_RADIUS_MM = 0.2


def build_basket_support(definition: JewelryDefinition) -> GeneratedComponent:
    interface = shank_connection_interface(definition)
    prong_r = definition.setting.prongDiameter / 2
    center_r = interface.headCenterRadiusMm

    outer_r = center_r + prong_r
    inner_r = max(center_r - prong_r, _MIN_INNER_RADIUS_MM)

    base_z = interface.topZMm - interface.embedMm
    height = definition.setting.basketHeight + interface.embedMm

    outer = cq.Workplane("XY").workplane(offset=base_z).circle(outer_r).extrude(height)
    inner = cq.Workplane("XY").workplane(offset=base_z).circle(inner_r).extrude(height)
    solid = outer.cut(inner)

    shape = solid.val()
    metadata = {
        "outerRadiusMm": outer_r,
        "innerRadiusMm": inner_r,
        "baseZMm": base_z,
        "heightMm": height,
    }

    return GeneratedComponent(
        name="basket_support",
        shape=shape,
        volume_mm3=shape.Volume(),
        bounding_box=BoundingBox.from_shape(shape),
        warnings=[],
        metadata=metadata,
    )
