"""Deterministic 2D outline primitives for every Stone System shape
(STONE-GOV-002, brief section 13/25) — category-neutral, pure geometry,
reused by both the outline-only contract and the real 3D reference
builder in `builder.py`.

Every function returns a closed `cq.Wire` in the local XY plane at Z=0,
scaled by `scale` (used by the builder to sample culet/girdle/table
levels of the same outline — see 572-shank-generation-pipeline.md's
Shank precedent, mirrored here). `half_length` is the half-extent along
local Y (the major horizontal dimension); `half_width` is the half-extent
along local X (the minor horizontal dimension) — see
docs/bible/20-stone/565-stone-coordinate-and-orientation.md.

Every shape-specific constant below (corner clip ratios, corner radius
ratios) is a deliberate, fixed SOFTWARE REFERENCE CONSTRUCTION parameter,
verified only to produce robust, deterministic CAD geometry — never a
sourced gemological/industry-standard proportion (STONE-GOV-011; see
brief sections 18/20's explicit prohibition on "industry standard corner
ratio").
"""

from __future__ import annotations

import math

import cadquery as cq

# Emerald: how far each corner is clipped diagonally, as a fraction of the
# smaller half-extent. A fixed software constant (see module docstring).
_EMERALD_CORNER_CLIP_RATIO = 0.18

# Cushion: rounded-corner radius, as a fraction of the smaller half-extent.
_CUSHION_CORNER_RATIO = 0.25

_COS_45 = math.cos(math.radians(45))


def round_outline(radius: float, scale: float) -> cq.Wire:
    return cq.Workplane("XY").circle(radius * scale).val()


def oval_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    return cq.Workplane("XY").ellipse(half_width * scale, half_length * scale).val()


def marquise_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """A symmetric lens: two arcs meeting at a point on each end of the
    major axis (STONE-GOV classification: ELONGATED_SMOOTH)."""

    hl, hw = half_length * scale, half_width * scale
    return (
        cq.Workplane("XY")
        .moveTo(0, hl)
        .threePointArc((hw, 0), (0, -hl))
        .threePointArc((-hw, 0), (0, hl))
        .close()
        .val()
    )


def pear_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """One pointed end (the tip, at +Y) and one rounded end (a
    semicircle-like arc at -Y) — the deliberate asymmetric case
    (STONE-GOV classification: ASYMMETRIC). This is a simplified,
    non-tangent silhouette (two straight sides meeting a rounded end) —
    robust and deterministic, not a smooth commercial pear outline; see
    docs/bible/20-stone/571-asymmetric-stone-contract.md."""

    hl, hw = half_length * scale, half_width * scale
    return (
        cq.Workplane("XY")
        .moveTo(0, hl)
        .lineTo(hw, -hl + hw)
        .threePointArc((0, -hl), (-hw, -hl + hw))
        .close()
        .val()
    )


def emerald_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """A rectangle with diagonally clipped corners (STONE-GOV
    classification: RECTILINEAR/ANGULAR)."""

    hl, hw = half_length * scale, half_width * scale
    clip = _EMERALD_CORNER_CLIP_RATIO * min(hw, hl)
    points = [
        (hw - clip, hl), (hw, hl - clip), (hw, -hl + clip), (hw - clip, -hl),
        (-hw + clip, -hl), (-hw, -hl + clip), (-hw, hl - clip), (-hw + clip, hl),
    ]
    return cq.Workplane("XY").polyline(points).close().val()


def princess_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """A plain rectangle — square only when `half_length == half_width`;
    a non-square rectangle is a supported, real configuration, not an
    error (brief section 19; STONE-GOV classification: RECTILINEAR/
    ANGULAR)."""

    return cq.Workplane("XY").rect(2 * half_width * scale, 2 * half_length * scale).val()


def cushion_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """A rounded rectangle, built from 4 lines and 4 quarter-circle arcs
    (STONE-GOV classification: ROUNDED_RECTILINEAR)."""

    hl, hw = half_length * scale, half_width * scale
    cr = _CUSHION_CORNER_RATIO * min(hw, hl)
    k = cr * _COS_45
    return (
        cq.Workplane("XY")
        .moveTo(hw - cr, hl)
        .lineTo(-hw + cr, hl)
        .threePointArc((-hw + cr - k, hl - cr + k), (-hw, hl - cr))
        .lineTo(-hw, -hl + cr)
        .threePointArc((-hw + cr - k, -hl + cr - k), (-hw + cr, -hl))
        .lineTo(hw - cr, -hl)
        .threePointArc((hw - cr + k, -hl + cr - k), (hw, -hl + cr))
        .lineTo(hw, hl - cr)
        .threePointArc((hw - cr + k, hl - cr + k), (hw - cr, hl))
        .close()
        .val()
    )
