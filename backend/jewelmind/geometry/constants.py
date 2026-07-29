"""Coordinate convention shared by every geometry builder.

See docs/geometry-conventions.md for the full write-up. Summary:

- All dimensions are millimeters.
- The world origin is the center of the ring (center of the finger hole).
- The band revolves around the global Y axis (the finger/hole axis is
  horizontal). The band's cross-section is drawn with local x = radial
  distance and local y = position along the band width, then revolved
  360 degrees around Y.
- Consequently the band lies in the X/Z plane when viewed down the Y axis,
  and its topmost point sits at (x=0, z=+outer_radius).
- The stone, prongs, and basket support are all built concentric around the
  vertical line x=0, y=0 (parallel to global Z), starting at
  `band_top_z = outer_radius` and rising in +Z. This is the "top of the
  ring": the stone is centered directly above it.
- The generator version below is stamped onto every generated model so a
  fixed input always maps to a fixed geometry-producing code path.
"""

from __future__ import annotations

from jewelmind.domain.schema import JewelryDefinition

GENERATOR_VERSION = "0.1.0"

# Bases are embedded this far into whatever they attach to (band or basket)
# so that unions produce genuine 3D overlap rather than a zero-volume
# tangent touch, which OpenCascade would otherwise leave as separate solids
# in a compound instead of fusing into one.
EMBED_MM = 0.4


def inner_radius(definition: JewelryDefinition) -> float:
    return definition.ring.innerDiameter / 2


def outer_radius(definition: JewelryDefinition) -> float:
    return inner_radius(definition) + definition.band.thickness


def band_top_z(definition: JewelryDefinition) -> float:
    """Z height of the topmost ridge of the band — the assembly anchor point."""

    return outer_radius(definition)


def prong_center_radius(definition: JewelryDefinition) -> float:
    """Radial distance (in the local XY plane) of each prong's central axis.

    Slightly inside the stone's girdle radius so the prong body overlaps the
    girdle edge, approximating a grip. Shared by the prong and basket
    builders so their footprints stay consistent with each other.
    """

    girdle_r = definition.stone.diameter / 2
    prong_r = definition.setting.prongDiameter / 2
    return girdle_r - prong_r * 0.3
