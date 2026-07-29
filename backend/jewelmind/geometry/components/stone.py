"""Simplified round-brilliant-style stone reference geometry.

This is a deliberately simplified geometric reference (a lofted
crown/girdle/pavilion approximation), not a gemological reproduction of a
real round brilliant cut. It exists so the assembly has a visually distinct,
correctly-sized placeholder for the stone that stays entirely separate from
the metal geometry (see docs/known-limitations.md).
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.constants import band_top_z
from jewelmind.geometry.model import BoundingBox, GeneratedComponent

# Rough round-brilliant proportions used only to split the user-provided
# total `depth` into a crown height and a pavilion height, and to size the
# table relative to the girdle. Not derived from any gemological standard.
_CROWN_FRACTION = 0.35
_PAVILION_FRACTION = 0.65
_TABLE_TO_GIRDLE_RATIO = 0.56
_CULET_RADIUS_MM = 0.05


def build_stone_reference(definition: JewelryDefinition) -> GeneratedComponent:
    """Build the stone reference solid, centered above the top of the band."""

    girdle_r = definition.stone.diameter / 2
    crown_h = definition.stone.depth * _CROWN_FRACTION
    pavilion_h = definition.stone.depth * _PAVILION_FRACTION
    table_r = girdle_r * _TABLE_TO_GIRDLE_RATIO

    girdle_z = band_top_z(definition) + definition.setting.basketHeight

    solid = (
        cq.Workplane("XY")
        .workplane(offset=girdle_z - pavilion_h)
        .circle(_CULET_RADIUS_MM)
        .workplane(offset=pavilion_h)
        .circle(girdle_r)
        .workplane(offset=crown_h)
        .circle(table_r)
        .loft(ruled=True)
    )

    shape = solid.val()
    metadata = {
        "girdleRadiusMm": girdle_r,
        "girdleZMm": girdle_z,
        "crownHeightMm": crown_h,
        "pavilionHeightMm": pavilion_h,
        "tableRadiusMm": table_r,
        "isGemologicalReproduction": False,
    }

    return GeneratedComponent(
        name="stone_reference",
        shape=shape,
        volume_mm3=shape.Volume(),
        bounding_box=BoundingBox.from_shape(shape),
        warnings=[],
        metadata=metadata,
    )
