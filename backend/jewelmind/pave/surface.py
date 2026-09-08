"""The host surface contract (Sprint 26).

A DETERMINISTIC REFERENCE, NEVER AN ARBITRARY SELECTION. A pavé names its host
with a `PaveHost` value, and the jewelry category resolves that name to the
numbers below. Nothing here picks a face out of a solid: a face index is not
reproducible across kernel versions or across a change to an unrelated
parameter, and a pavé whose stones moved because a fillet changed a face
ordering would be indefensible.

WHY THE NEUTRAL LAYER GETS NUMBERS, NOT A SHAPE. `jewelmind.pave` must not
import a geometry module or a jewelry category, so it cannot measure a band. It
declares WHAT it needs to know about a surface, and `geometry/pave_adapter.py`
— the Ring-side translation point, the role `geometry/setting_adapter.py` plays
for the Setting System — supplies it. The pavé then does closed-form arithmetic
on plain floats.

TWO SURFACE KINDS, and only two, because only two are executable:

- `CYLINDRICAL` — a surface of revolution about a horizontal axis, at a fixed
  radius. The shank's outer surface. Its stones must follow the surface normal,
  which is why Sprint 26 gave the arrangement a real axis tilt.
- `PLANAR` — a horizontal plane at a fixed Z. The head's top, a halo's plane.
  Its normal is +Z everywhere, so no tilt is needed and the placements are the
  same closed-form ring/grid arithmetic the arrangement already does.

Anything else — a basket wall, a prong flank, a swept custom surface — has no
resolver and is listed in `capability.py::RESERVED_PAVE_HOSTS` with the reason.
"""

from __future__ import annotations

import math
from typing import Literal

from pydantic import Field

from jewelmind.pave.models import PaveModel

SurfaceKind = Literal["CYLINDRICAL", "PLANAR"]


class ResolvedHostSurface(PaveModel):
    """Everything the pavé layer needs to know about a surface, as numbers.

    Supplied by the jewelry category, never measured here. Every field is a
    plain float in millimetres or degrees, so this object is serializable,
    comparable, hashable and free of any kernel dependency.
    """

    #: Which target this resolves. Carried so a compiled field can be traced
    #: back to the host it was applied to (§13: no anonymous geometry).
    host: str = Field(max_length=40)

    kind: SurfaceKind

    #: The production component the field is applied to — `band`,
    #: `basket_support`. Retention metal fuses into it and, when a recess is
    #: requested, the stones are cut out of it.
    hostComponent: str = Field(max_length=80)

    #: CYLINDRICAL: distance from the surface axis to the surface.
    radiusMm: float | None = Field(default=None, gt=0.0, allow_inf_nan=False)

    #: CYLINDRICAL: azimuth of the surface's axis, in degrees from +X in the XY
    #: plane. The shank revolves about the global Y axis, so the Ring adapter
    #: supplies 90.0 — expressed as a number rather than as an axis name, which
    #: is what keeps this layer category-neutral.
    axisAzimuthDeg: float = Field(default=90.0, ge=-360.0, le=360.0, allow_inf_nan=False)

    #: CYLINDRICAL: usable extent along the axis (the band's width).
    axialExtentMm: float | None = Field(
        default=None, gt=0.0, allow_inf_nan=False
    )

    #: CYLINDRICAL: where the middle of the usable extent sits along the axis.
    axialCenterMm: float = Field(default=0.0, allow_inf_nan=False)

    #: PLANAR: the plane's height.
    planeZMm: float | None = Field(default=None, allow_inf_nan=False)

    #: PLANAR: the smallest radius from the design axis a stone may occupy, so a
    #: field on a gallery does not land on top of the centre stone.
    innerRadiusMm: float | None = Field(
        default=None, ge=0.0, allow_inf_nan=False
    )

    #: PLANAR: the largest radius from the design axis a stone may occupy.
    outerRadiusMm: float | None = Field(
        default=None, gt=0.0, allow_inf_nan=False
    )

    #: Where the as-built stone's girdle plane sits in the design frame.
    #:
    #: NEEDED BECAUSE AN ARRANGEMENT TRANSFORM IS A DELTA, not an absolute
    #: position: the stone is built once, centred on the design axis with its
    #: girdle here, and each instance's transform moves it from there. Without
    #: this the pavé could not turn a target point into a transform, and
    #: hard-coding it would make the pavé depend on how the assembly happens to
    #: build a stone today.
    stoneAnchorZMm: float = Field(allow_inf_nan=False)

    def surface_normal_azimuth_deg(self) -> float:
        """Azimuth of the direction a CYLINDRICAL surface's stones lean toward.

        Perpendicular to the axis and horizontal: a surface whose axis runs
        along Y bulges toward ±X, so its stones tip toward azimuth 0 or 180.
        """

        return self.axisAzimuthDeg + 90.0

    def cylindrical_point(self, angle_deg: float, axial_mm: float) -> tuple[float, float, float]:
        """A point on a CYLINDRICAL surface, in the design frame.

        `angle_deg` is measured from +Z about the surface axis, so 0 is the
        crest — the top of the band, which is where a shank pavé is described
        from. `axial_mm` runs along the axis.
        """

        radians = math.radians(angle_deg)
        perp = math.radians(self.surface_normal_azimuth_deg())
        axis = math.radians(self.axisAzimuthDeg)
        radius = self.radiusMm or 0.0

        # The surface offset decomposes into the horizontal perpendicular
        # direction and the vertical: radius * (sin(angle) * perp + cos(angle) * Z).
        lateral = radius * math.sin(radians)
        return (
            lateral * math.cos(perp) + axial_mm * math.cos(axis),
            lateral * math.sin(perp) + axial_mm * math.sin(axis),
            radius * math.cos(radians),
        )
