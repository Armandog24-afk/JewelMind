"""JewelryDefinition -> pavé host surface (Sprint 26).

THE RING-SIDE TRANSLATION POINT for surface targeting, and it lives
deliberately outside `jewelmind/pave/` — the role
`geometry/setting_adapter.py` plays for the Setting System. The pavé layer is
category-neutral and cannot measure a band; this module measures one and hands
over plain numbers.

DELIBERATELY KERNEL-FREE, and that is what makes it importable by Forge. A
pavé rule has to answer "does this field compile against this design's real
surface?", and it has to answer it with the SAME code generation will use or
the two will eventually disagree — the discipline `_family_rules` and
`_halo_rules` already follow by running the real compiler. Forge may not import
CadQuery, so the surface resolution is split out here and the kernel work stays
in `pave_adapter.py`.

WHY A SURFACE IS RESOLVED FROM PARAMETERS, NEVER PICKED OUT OF A SOLID. A face
index is not reproducible: it can change when the kernel version changes, or
when an unrelated parameter alters how a solid was built. A pavé whose stones
moved because a fillet renumbered a face would be indefensible, so every
supported host is derived from the same `constants.py` expressions the rest of
the assembly uses.
"""

from __future__ import annotations

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.domain.stone_dimensions import resolved_width_mm
from jewelmind.geometry.constants import (
    band_top_z,
    outer_radius,
    prong_center_radius,
)
from jewelmind.pave.errors import PaveHostUnsupportedError
from jewelmind.pave.models import PaveDefinition
from jewelmind.pave.surface import ResolvedHostSurface

#: Azimuth of the shank's axis of revolution.
#:
#: The band revolves about the global Y axis (`geometry/constants.py`), and +Y
#: is at azimuth 90 degrees in the XY plane. Stated here rather than inside the
#: pave layer because it is a CATEGORY fact: an earring's pave surface would
#: have a different axis, and the neutral layer must not assume this one.
_SHANK_AXIS_AZIMUTH_DEG = 90.0


def stone_anchor_z_mm(definition: JewelryDefinition) -> float:
    """Where the as-built stone's girdle plane sits in the design frame.

    Reproduces `geometry/stone/builder.py`'s own expression rather than
    re-deriving it: an arrangement transform is a DELTA from the as-built
    position, so a pavé that computed this differently would place every stone
    off by the difference. The same discipline Sprint 23 applied when the Ring
    adapter passed the ORIGINAL basket bore expression instead of recomputing
    it.
    """

    return band_top_z(definition) + definition.setting.basketHeight


def _band_outer_surface(definition: JewelryDefinition) -> ResolvedHostSurface:
    """The shank's outer surface: cylindrical about the finger axis."""

    return ResolvedHostSurface(
        host="BAND_OUTER",
        kind="CYLINDRICAL",
        hostComponent="band",
        radiusMm=outer_radius(definition),
        axisAzimuthDeg=_SHANK_AXIS_AZIMUTH_DEG,
        # The band's own width is the usable extent along the axis, so a field
        # cannot run off the edge of the metal it is set into.
        axialExtentMm=definition.band.width,
        axialCenterMm=0.0,
        stoneAnchorZMm=stone_anchor_z_mm(definition),
    )


def _head_plane_surface(definition: JewelryDefinition) -> ResolvedHostSurface:
    """The horizontal plane at the top of the head.

    Bounded INWARD by the centre stone's own footprint, so a gallery field
    cannot land on top of the stone it surrounds, and OUTWARD by the head's own
    outer radius — which is the metal actually present in this plane. A wider
    field would have nothing to fuse its beads into, and reporting it as
    supported would ship a disconnected production solid.
    """

    girdle_radius = resolved_width_mm(definition.stone) / 2.0
    prong_radius = definition.setting.prongDiameter / 2.0
    return ResolvedHostSurface(
        host="HEAD_PLANE",
        kind="PLANAR",
        hostComponent="basket_support",
        planeZMm=stone_anchor_z_mm(definition),
        innerRadiusMm=girdle_radius,
        outerRadiusMm=prong_center_radius(definition) + prong_radius,
        stoneAnchorZMm=stone_anchor_z_mm(definition),
    )


_HOST_RESOLVERS = {
    "BAND_OUTER": _band_outer_surface,
    "HEAD_PLANE": _head_plane_surface,
}


def resolve_pave_surface(
    definition: JewelryDefinition, pave: PaveDefinition
) -> ResolvedHostSurface:
    """The host surface this pavé is applied to, as numbers.

    A registry rather than a branch chain, so a host with no resolver is
    unreachable rather than silently substituted with the nearest surface that
    happens to exist.
    """

    resolver = _HOST_RESOLVERS.get(pave.host)
    if resolver is None:
        raise PaveHostUnsupportedError(
            f"No surface resolver is registered for pavé host {pave.host!r}. "
            f"Resolvable hosts: {sorted(_HOST_RESOLVERS)}."
        )
    return resolver(definition)


