"""Prong geometry: exactly 4 or 6 separate cylindrical solids.

Prongs are distributed evenly around the stone's girdle, rising from just
below the top of the band (embedded slightly into the band/basket so unions
produce genuine solid contact) up past the girdle to grip the stone crown.
"""

from __future__ import annotations

import math

import cadquery as cq

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.constants import EMBED_MM, band_top_z, prong_center_radius
from jewelmind.geometry.model import BoundingBox, GeneratedComponent


def _prong_positions(count: int, radius: float) -> list[tuple[float, float]]:
    return [
        (radius * math.cos(2 * math.pi * i / count), radius * math.sin(2 * math.pi * i / count))
        for i in range(count)
    ]


def build_prongs(definition: JewelryDefinition) -> GeneratedComponent:
    """Build the prong solids as one compound component.

    `metadata["requestedCount"]` and `metadata["generatedCount"]` always
    report the actual counts, even if validation would flag the requested
    count as unsupported — geometry generation is expected to be blocked
    upstream by validation errors in that case, but this function stays
    honest about what it was asked to build.
    """

    requested_count = definition.setting.prongCount
    generated_count = requested_count if requested_count in (4, 6) else max(requested_count, 0)

    prong_r = definition.setting.prongDiameter / 2
    center_r = prong_center_radius(definition)
    base_z = band_top_z(definition) - EMBED_MM
    height = definition.setting.prongHeight + EMBED_MM

    positions = _prong_positions(generated_count, center_r) if generated_count > 0 else []

    solids = []
    for x, y in positions:
        prong = (
            cq.Workplane("XY")
            .workplane(offset=base_z)
            .center(x, y)
            .circle(prong_r)
            .extrude(height)
        )
        solids.append(prong.val())

    compound = cq.Compound.makeCompound(solids) if solids else cq.Compound.makeCompound([])
    total_volume = sum(s.Volume() for s in solids)

    warnings: list[str] = []
    if requested_count != generated_count:
        warnings.append(
            f"Requested prong count {requested_count} is unsupported; generated {generated_count} instead."
        )

    metadata = {
        "requestedCount": requested_count,
        "generatedCount": generated_count,
        "prongRadiusMm": prong_r,
        "centerRadiusMm": center_r,
        "positions": [{"x": x, "y": y} for x, y in positions],
    }

    bbox = BoundingBox.from_shape(compound) if solids else BoundingBox(0, 0, 0, 0, 0, 0)

    return GeneratedComponent(
        name="prongs",
        shape=compound,
        volume_mm3=total_volume,
        bounding_box=bbox,
        warnings=warnings,
        metadata=metadata,
    )
