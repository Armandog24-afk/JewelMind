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


# ---------------------------------------------------------------------------
# Sprint 20 (Stone System v2) extended outline primitives.
#
# Every constant below is a fixed SOFTWARE REFERENCE CONSTRUCTION parameter
# (STONE-GOV-011 / STONEV2-GOV-004), verified only to produce robust,
# deterministic CAD geometry. None is a sourced gemological proportion, and
# none may ever be described as an industry-standard cut ratio.
#
# DIMENSION CONTRACT: every outline below is built so that its real bounding
# box is exactly `2 * half_width` (X) by `2 * half_length` (Y) at `scale=1`.
# That is what lets Geometry Inspection compare REQUESTED against MEASURED
# dimensions and expect equality (brief section 46). Where a naive arc
# construction would overshoot that box, the overshoot is removed
# analytically (`trillion`) or by choosing a curve that is exact by
# construction (`half_moon`) -- never by silently reporting the nominal
# value while building something larger.
# ---------------------------------------------------------------------------

#: Radiant/Asscher corner clips, as a fraction of the smaller half-extent.
#: Deliberately different from each other and from `_EMERALD_CORNER_CLIP_RATIO`
#: so the three clipped-rectilinear shapes stay visually distinguishable --
#: a software choice, not a cut specification (STONEV2-GOV-004).
_RADIANT_CORNER_CLIP_RATIO = 0.14
_ASSCHER_CORNER_CLIP_RATIO = 0.22

#: Trillion: how far each side bows outward, as a fraction of half-length.
_TRILLION_BULGE_RATIO = 0.18

#: Heart: how deep the cleft cuts down from the top edge, as a fraction of
#: half-length.
_HEART_CLEFT_RATIO = 0.22

#: Shield: where the straight flanks end and the point begins.
_SHIELD_SHOULDER_RATIO = 0.2
_SHIELD_WAIST_RATIO = 0.75
_SHIELD_WAIST_WIDTH_RATIO = 0.45

#: Kite: how far above the vertical center the widest points sit.
_KITE_SHOULDER_RATIO = 0.25

#: Hexagon: where the two horizontal flanks sit, as a fraction of half-length.
_HEXAGON_SHOULDER_RATIO = 0.5

# THE CANONICAL FRAME INVARIANT: every outline below is centred on the local
# origin, because that is the frame `_apply_orientation()` rotates about and the
# frame `StoneSettingReference.centerXMm/centerYMm` reports. An off-centre
# outline silently displaces the stone and every setting built around it. Two
# constructions violated it during Sprint 20 and were fixed at the source rather
# than patched with a post-hoc translation: `half_moon` (whose elliptical arc
# centres on the current point) and `heart` (rebuilt to be exact by
# construction). `test_stone_v2.py` asserts the invariant for every shape.


def _polyline_outline(points: list[tuple[float, float]]) -> cq.Wire:
    return cq.Workplane("XY").polyline(points).close().val()


def _clipped_rectangle(
    half_length: float, half_width: float, scale: float, clip_ratio: float
) -> cq.Wire:
    """A rectangle with all four corners clipped diagonally.

    Shared by emerald (through its own ratio), radiant and asscher: the same
    primitive with deliberately different clip ratios and three distinct
    canonical shape IDs. Shared geometry never merges two shape identities
    (STONEV2-GOV-005).
    """

    hl, hw = half_length * scale, half_width * scale
    clip = clip_ratio * min(hw, hl)
    return _polyline_outline([
        (hw - clip, hl), (hw, hl - clip), (hw, -hl + clip), (hw - clip, -hl),
        (-hw + clip, -hl), (-hw, -hl + clip), (-hw, hl - clip), (-hw + clip, hl),
    ])


def radiant_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """Clipped-corner rectangle -- RADIANT's reference SILHOUETTE only.

    Explicitly not a model of the radiant brilliant facet pattern
    (STONEV2-GOV-003).
    """

    return _clipped_rectangle(half_length, half_width, scale, _RADIANT_CORNER_CLIP_RATIO)


def asscher_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """Clipped-corner rectangle with a deeper clip than radiant or emerald.

    Square only when length equals width; a non-square request is a real,
    supported configuration. Not a model of the Asscher step-cut facet
    pattern (STONEV2-GOV-003).
    """

    return _clipped_rectangle(half_length, half_width, scale, _ASSCHER_CORNER_CLIP_RATIO)


def baguette_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """A plain rectangle.

    Geometrically identical to `princess_outline`, kept as its own named
    primitive because BAGUETTE and PRINCESS are distinct canonical shapes
    with distinct expected proportions: a future change to either must not
    silently move the other.
    """

    return cq.Workplane("XY").rect(2 * half_width * scale, 2 * half_length * scale).val()


def _tapered_quadrilateral(
    half_length: float, half_wide: float, half_narrow: float, scale: float
) -> cq.Wire:
    """A trapezoid with its WIDE end at -Y and its NARROW end at +Y.

    A fixed convention, not an arbitrary one: it makes `narrowWidth` shrink
    toward +Y for both TAPERED_BAGUETTE and TRAPEZOID, so the WIDE_END and
    NARROW_END anchors mean the same thing for both shapes. See
    docs/bible/22-stone-v2/extended-native-shapes.md.
    """

    hl = half_length * scale
    wide, narrow = half_wide * scale, half_narrow * scale
    return _polyline_outline([(-narrow, hl), (narrow, hl), (wide, -hl), (-wide, -hl)])


def tapered_baguette_outline(
    half_length: float, half_width: float, scale: float, half_narrow_width: float
) -> cq.Wire:
    """An explicitly tapered rectangle.

    The taper is never hidden inside a ratio constant: `narrowWidth` is a
    real, required JDL dimension (brief section 13).
    """

    return _tapered_quadrilateral(half_length, half_width, half_narrow_width, scale)


def trapezoid_outline(
    half_length: float, half_width: float, scale: float, half_narrow_width: float
) -> cq.Wire:
    """Geometrically the same primitive as `tapered_baguette_outline`.

    They stay separate canonical shapes: a trapezoid is typically a side or
    accent stone with a much shorter length-to-width ratio, and the two IDs
    must remain independently changeable.
    """

    return _tapered_quadrilateral(half_length, half_width, half_narrow_width, scale)


def triangle_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """An isosceles triangle, apex at +Y and base at -Y.

    Straight sides throughout -- deliberately not the same shape as
    `trillion_outline`, whose sides bow outward.
    """

    hl, hw = half_length * scale, half_width * scale
    return _polyline_outline([(0.0, hl), (hw, -hl), (-hw, -hl)])


def lozenge_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """A rhombus with its four vertices on the two axes.

    Canonically LOZENGE, never "diamond": in JewelMind "diamond" is a gem
    species, and a shape enum must never collide with gem identity
    (STONEV2-GOV-008; brief sections 16 and 37).
    """

    hl, hw = half_length * scale, half_width * scale
    return _polyline_outline([(0.0, hl), (hw, 0.0), (0.0, -hl), (-hw, 0.0)])


def hexagon_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """An ELONGATED hexagon: two points on the Y axis, four shoulder vertices.

    Regular only when the caller supplies the matching length/width ratio.
    Regularity is deliberately not forced, so an elongated hexagon is a
    first-class configuration (brief section 17).
    """

    hl, hw = half_length * scale, half_width * scale
    shoulder = hl * _HEXAGON_SHOULDER_RATIO
    return _polyline_outline([
        (0.0, hl), (hw, shoulder), (hw, -shoulder),
        (0.0, -hl), (-hw, -shoulder), (-hw, shoulder),
    ])


def kite_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """A kite: points at +Y and -Y, widest span ABOVE the vertical center.

    Longitudinally asymmetric -- a real ASYMMETRIC-class shape, like pear.
    """

    hl, hw = half_length * scale, half_width * scale
    shoulder = hl * _KITE_SHOULDER_RATIO
    return _polyline_outline([(0.0, hl), (hw, shoulder), (0.0, -hl), (-hw, shoulder)])


def shield_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """A flat-topped shield tapering to a point at -Y.

    Fully polygonal by design. An arc-based lower boundary bulges past the
    requested width -- measured at 6.05mm for a 6.00mm request during Sprint
    20 prototyping -- which would break the requested-equals-measured
    dimension contract. No shield subtypes are modeled (brief section 19).
    """

    hl, hw = half_length * scale, half_width * scale
    return _polyline_outline([
        (-hw, hl), (hw, hl),
        (hw, -hl * _SHIELD_SHOULDER_RATIO),
        (hw * _SHIELD_WAIST_WIDTH_RATIO, -hl * _SHIELD_WAIST_RATIO),
        (0.0, -hl),
        (-hw * _SHIELD_WAIST_WIDTH_RATIO, -hl * _SHIELD_WAIST_RATIO),
        (-hw, -hl * _SHIELD_SHOULDER_RATIO),
    ])


def trillion_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """A triangle with outward-bowed (convex) sides.

    The base vertices are pre-inset by exactly the bulge amount so the bowed
    bottom edge lands on -half_length rather than beyond it. Without that
    inset the real bounding box overshot the request by the full bulge --
    measured 7.63mm for a 7.00mm request during prototyping.
    """

    hl, hw = half_length * scale, half_width * scale
    bulge = _TRILLION_BULGE_RATIO * hl
    base_y = -(hl - bulge)
    tip = (0.0, hl)
    right = (hw, base_y)
    left = (-hw, base_y)
    centroid_y = (hl + base_y + base_y) / 3.0

    def bowed_midpoint(p: tuple[float, float], q: tuple[float, float]) -> tuple[float, float]:
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        dx, dy = mx, my - centroid_y
        norm = math.hypot(dx, dy) or 1.0
        return (mx + dx / norm * bulge, my + dy / norm * bulge)

    return (
        cq.Workplane("XY")
        .moveTo(*tip)
        .threePointArc(bowed_midpoint(tip, right), right)
        .threePointArc(bowed_midpoint(right, left), left)
        .threePointArc(bowed_midpoint(left, tip), tip)
        .close()
        .val()
    )


def half_moon_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """A straight chord at -X closed by an ELLIPTICAL arc bulging toward +X.

    Half of an ellipse rather than half of a circle: a circular arc through
    the two chord endpoints necessarily has a radius larger than the
    half-length, so its bounding box always overshoots the requested length
    -- measured 7.50mm for a 6.00mm request during prototyping. The
    half-ellipse is exact for every aspect ratio.
    """

    hl, hw = half_length * scale, half_width * scale
    # `ellipseArc(..., startAtCurrent=False)` centres the ellipse on the CURRENT
    # point, not on the arc's start. Moving to the chord endpoint first (the
    # obvious reading) therefore produced an outline centred at (-hw, -hl)
    # instead of the origin — a real off-centre bug caught by asserting that
    # every outline's bounding-box centre is the local origin. Move to the
    # ellipse's centre instead.
    return (
        cq.Workplane("XY")
        .moveTo(-hw, 0.0)
        .ellipseArc(2 * hw, hl, angle1=-90, angle2=90, startAtCurrent=False)
        .close()
        .val()
    )


#: Heart: the lobe circle radius, as a fraction of half-width. Must stay above
#: 0.5 so the lobe circle reaches the centre line and the cleft is a real point
#: on it; a fixed SOFTWARE REFERENCE CONSTRUCTION parameter.
_HEART_LOBE_RADIUS_RATIO = 0.55


def heart_outline(half_length: float, half_width: float, scale: float) -> cq.Wire:
    """A heart with its point at -Y and its cleft at +Y.

    EXACT BY CONSTRUCTION. Each lobe is a real circular arc whose own extreme
    points ARE the requested bounds: the lobe circle of radius `r` centred at
    `(-(hw - r), hl - r)` touches `y = hl` at its top and `x = -hw` at its left,
    so the bounding box equals the request at every aspect ratio with zero
    residual, and the outline is already centred on the local origin.

    This replaced an earlier control-point construction whose arcs bulged past
    their control box and had to be corrected by a fixed-point iteration. That
    iteration converged linearly at roughly 0.34 per step and did NOT reach
    tolerance for elongated hearts — a 10x6 heart was still 8e-6 mm too wide
    after forty steps. Solving the geometry exactly removed both the residual
    error and the iteration.

    The cleft is where the two lobe circles meet the centre line, at
    `y = hl - r + sqrt(r^2 - a^2)`; it is a consequence of the lobe geometry
    rather than an independent tunable, which is what keeps the outline closed
    and smooth at the cleft for every aspect ratio. No commercial heart-cut
    proportion is claimed (STONEV2-GOV-003).
    """

    hl, hw = half_length * scale, half_width * scale
    radius = _HEART_LOBE_RADIUS_RATIO * hw
    offset = hw - radius
    cleft_y = hl - radius + math.sqrt(max(radius * radius - offset * offset, 0.0))

    return (
        cq.Workplane("XY")
        .moveTo(0.0, cleft_y)
        .threePointArc((-offset, hl), (-hw, hl - radius))
        .lineTo(0.0, -hl)
        .lineTo(hw, hl - radius)
        .threePointArc((offset, hl), (0.0, cleft_y))
        .close()
        .val()
    )


def custom_outline(points: list[tuple[float, float]], scale: float) -> cq.Wire:
    """A closed polyline through caller-supplied 2D points.

    This is the Stone System's escape hatch (brief section 23): it is what
    lets JewelMind build a real StoneReference for a cut that has no built-in
    enum member. The points must already have been validated and normalized
    by `jewelmind/stone/outline_validation.py`; this function performs no
    repair of its own, so a malformed outline fails loudly upstream rather
    than being silently fixed here (brief section 24).
    """

    return _polyline_outline([(x * scale, y * scale) for x, y in points])


#: How many points each curved edge contributes when an outline is sampled
#: into explicit points. High enough that a bezel offset built from the sampled
#: outline is visually indistinguishable from one built on the real curve, and
#: low enough to keep manifests and Golden snapshots readable.
OUTLINE_CURVE_SAMPLES = 48

#: Tolerance for deciding two outline endpoints are the same vertex when
#: ordering edges. A kernel-level geometric tolerance, never a jewelry one.
_ENDPOINT_MATCH_MM = 1e-7


def _ordered_edges(wire: cq.Wire) -> list[tuple[cq.Edge, bool]]:
    """Walk a wire's edges in connected order, with each edge's direction.

    `Wire.Edges()` does NOT reliably return edges in traversal order: the heart
    outline returns its four arcs in the order 1, 4, 2, 3 with mixed
    orientations. Concatenating them naively produces a scrambled outline that
    still looks plausible in aggregate statistics (its bounding box is
    correct!) but is wrong point-by-point, which would silently corrupt anchor
    derivation and any bezel built from sampled points.

    Returns `(edge, reversed)` pairs so the caller can sample each edge in the
    direction the traversal actually needs.
    """

    edges = list(wire.Edges())
    if len(edges) <= 1:
        return [(e, False) for e in edges]

    def near(a, b) -> bool:
        return abs(a.x - b.x) <= _ENDPOINT_MATCH_MM and abs(a.y - b.y) <= _ENDPOINT_MATCH_MM

    remaining = edges[1:]
    ordered: list[tuple[cq.Edge, bool]] = [(edges[0], False)]
    current = edges[0].endPoint()

    while remaining:
        for index, candidate in enumerate(remaining):
            if near(candidate.startPoint(), current):
                ordered.append((candidate, False))
                current = candidate.endPoint()
                remaining.pop(index)
                break
            if near(candidate.endPoint(), current):
                ordered.append((candidate, True))
                current = candidate.startPoint()
                remaining.pop(index)
                break
        else:
            # No edge continues the chain. Rather than guess, stop and report
            # what was actually connected: a caller that gets fewer edges than
            # the wire has knows the outline is not a simple connected ring.
            break

    return ordered


def sample_outline(
    wire: cq.Wire, curve_samples: int = OUTLINE_CURVE_SAMPLES
) -> tuple[list[tuple[float, float]], bool]:
    """Discretize an outline into ordered points.

    Returns `(points, is_polygonal)`. A straight edge contributes only its
    start vertex, so a polygon samples to exactly its own vertices and stays
    EXACT; a curved edge contributes `curve_samples` evenly-parameterized
    points and is therefore an approximation, which `is_polygonal=False`
    reports honestly (see `StoneOutline.isPolygonal`).
    """

    points: list[tuple[float, float]] = []
    is_polygonal = True

    for edge, is_reversed in _ordered_edges(wire):
        if edge.geomType() == "LINE":
            start = edge.endPoint() if is_reversed else edge.startPoint()
            points.append((start.x, start.y))
            continue

        is_polygonal = False
        for i in range(curve_samples):
            t = i / curve_samples
            position = edge.positionAt(1.0 - t if is_reversed else t)
            points.append((position.x, position.y))

    # Drop a duplicated closing point if the traversal produced one: the
    # outline contract is that the ring is closed implicitly.
    if len(points) > 1:
        first, last = points[0], points[-1]
        if (
            abs(first[0] - last[0]) <= _ENDPOINT_MATCH_MM
            and abs(first[1] - last[1]) <= _ENDPOINT_MATCH_MM
        ):
            points.pop()

    return points, is_polygonal
