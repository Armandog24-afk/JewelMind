"""Centralized section-profile generation (SHANK-GOV-015, brief section 24)
— the single place flat and comfort-fit cross-sections are built, reused by
both the uniform (revolve) and tapered (loft) shank construction paths so
profile logic is never duplicated.

A profile is a real, closed 2D wire drawn in the local XY plane (local
x = radial distance from the ring axis, local y = position along the
shank's axial/width direction) — the exact plane `cq.Workplane("XY")`
already used before Sprint 17, unchanged. See
docs/bible/19-shank/545-section-profile-contract.md.
"""

from __future__ import annotations

import cadquery as cq

# Comfort-fit inner edge flare, in mm, at the profile's Y edges relative to
# its center. Conservative and fixed rather than user-configurable — moved
# here unchanged from the pre-Sprint-17 band.py.
COMFORT_FLARE_MM = 0.3


def flat_profile_wire(inner_r: float, outer_r: float, half_width: float) -> cq.Workplane:
    """A rectangular cross-section: a plain flat-topped/bottomed shank."""

    pts = [
        (inner_r, -half_width),
        (inner_r, half_width),
        (outer_r, half_width),
        (outer_r, -half_width),
    ]
    return cq.Workplane("XY").polyline(pts).close()


def comfort_fit_profile_wire(inner_r: float, outer_r: float, half_width: float) -> cq.Workplane:
    """The inner edge is a shallow outward-bulging arc instead of a
    straight line. The minimum inner radius (at the profile's center) is
    exactly `inner_r`, flaring slightly outward toward the edges — the
    requested finger opening is never reduced."""

    edge_r = inner_r + COMFORT_FLARE_MM
    return (
        cq.Workplane("XY")
        .moveTo(edge_r, -half_width)
        .threePointArc((inner_r, 0.0), (edge_r, half_width))
        .lineTo(outer_r, half_width)
        .lineTo(outer_r, -half_width)
        .close()
    )


def build_profile(profile_type: str, inner_r: float, outer_r: float, half_width: float) -> cq.Workplane:
    """Dispatch to the real profile builder for `profile_type` ("flat" or
    "comfort_fit"). Longitudinal taper is never mixed into this function —
    it only ever sees the already-resolved width/thickness for one
    section (SHANK-GOV-004)."""

    if profile_type == "flat":
        return flat_profile_wire(inner_r, outer_r, half_width)
    return comfort_fit_profile_wire(inner_r, outer_r, half_width)
