"""Custom outline validation and normalization (brief sections 24/25).

Two responsibilities, kept deliberately separate:

- **validate** — reject a materially malformed outline. Nothing here repairs
  geometry. A self-intersecting outline is an error, never a silently-fixed
  one (brief section 24's "do not silently repair materially malformed
  outlines").
- **normalize** — apply the small set of well-defined, reversible, RECORDED
  transformations that put a valid outline into JewelMind's canonical frame:
  unit conversion, winding direction, and origin. Every operation applied is
  appended to `StoneSourceProvenance.normalizationOperations`, so a reader can
  always see what was changed.

The distinction matters: normalization changes the outline's coordinates but
never its shape. Anything that would change the shape is a validation failure
instead.

CANONICAL LOCAL FRAME (brief section 25, matching Sprint 18's convention in
docs/bible/20-stone/565-stone-coordinate-and-orientation.md):

- the outline lies in the local XY plane; depth runs along +Z;
- LENGTH is the Y extent, WIDTH the X extent;
- the origin is the outline's BOUNDING-BOX CENTER, not its centroid.

Bounding-box center is chosen because that is what Sprint 18's native shapes
already use (`_apply_orientation()` rotates about the bounding-box center) and
what `StoneSettingReference.centerXMm/centerYMm` already reports. Using a
centroid here would put a custom stone in a different frame from every native
stone and silently misplace every setting built around it.
"""

from __future__ import annotations

import math

from jewelmind.stone.errors import (
    CustomOutlineInvalidError,
    CustomOutlineSelfIntersectionError,
)
from jewelmind.stone.models import UNIT_TO_MM, CustomOutlineSpec, OutlinePoint

#: Minimum number of distinct points that can bound a real area.
MIN_OUTLINE_POINTS = 3

#: Upper bound on outline complexity. A resource safeguard for untrusted input
#: (brief section 50), not a geometric judgment: a legitimate hand-authored or
#: vector-imported stone outline is orders of magnitude below this.
MAX_OUTLINE_POINTS = 10_000

#: Two consecutive points closer than this are treated as a degenerate segment.
#: A pure numerical-robustness threshold for the kernel, never a manufacturing
#: tolerance (INSPECT-GOV-012's discipline).
DEGENERATE_SEGMENT_MM = 1e-9

#: An outline enclosing less than this signed area is treated as zero-area.
MIN_OUTLINE_AREA_MM2 = 1e-9

#: Largest coordinate magnitude accepted, in millimetres. Guards against an
#: absurd scale reaching the kernel; a gemstone outline is never near this.
MAX_COORDINATE_MM = 10_000.0


def _signed_area(points: list[tuple[float, float]]) -> float:
    """Twice the signed area (the shoelace sum), positive counter-clockwise."""

    total = 0.0
    for i, (x1, y1) in enumerate(points):
        x2, y2 = points[(i + 1) % len(points)]
        total += x1 * y2 - x2 * y1
    return total / 2.0


def _segments_properly_intersect(
    a1: tuple[float, float], a2: tuple[float, float],
    b1: tuple[float, float], b2: tuple[float, float],
) -> bool:
    """True when segments a1-a2 and b1-b2 cross at an interior point.

    Uses exact orientation signs rather than computing an intersection point,
    which avoids the division-by-near-zero instability a point-based test has
    on nearly-parallel segments. Shared endpoints (which adjacent outline
    segments always have) are excluded by the caller, and collinear overlap is
    reported through the degenerate-segment and zero-area checks instead.
    """

    def orient(p, q, r) -> float:
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    d1, d2 = orient(b1, b2, a1), orient(b1, b2, a2)
    d3, d4 = orient(a1, a2, b1), orient(a1, a2, b2)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


def _point_on_segment(
    p: tuple[float, float], a: tuple[float, float], b: tuple[float, float]
) -> bool:
    """True when `p` lies on segment a-b, within `DEGENERATE_SEGMENT_MM`.

    Distance from the point to the segment, not to the infinite line: a vertex
    beyond an endpoint is not touching the segment.
    """

    abx, aby = b[0] - a[0], b[1] - a[1]
    length_sq = abx * abx + aby * aby
    if length_sq <= 0.0:
        return math.dist(p, a) <= DEGENERATE_SEGMENT_MM
    t = ((p[0] - a[0]) * abx + (p[1] - a[1]) * aby) / length_sq
    t = max(0.0, min(1.0, t))
    closest = (a[0] + t * abx, a[1] + t * aby)
    return math.dist(p, closest) <= DEGENERATE_SEGMENT_MM


def _find_vertex_touching_edge(
    points: list[tuple[float, float]],
) -> tuple[int, int] | None:
    """Return the first (vertex index, non-adjacent segment index) where the
    vertex lies ON the segment, or None.

    A proper-crossing test alone is not enough to prove an outline is a simple
    closed curve. A polygon whose vertex merely TOUCHES a distant edge has no
    strict orientation-sign change, so `_find_self_intersection` correctly
    reports nothing — yet the outline is still non-simple, and offsetting it
    (which is exactly what a bezel does) is unreliable. Found during Sprint 20
    validation with a Z-shaped outline that passed every other check.
    """

    n = len(points)
    for vi in range(n):
        v = points[vi]
        for si in range(n):
            # The vertex legitimately lies on its own two incident segments.
            if si == vi or (si + 1) % n == vi:
                continue
            if _point_on_segment(v, points[si], points[(si + 1) % n]):
                return vi, si
    return None


def _find_self_intersection(points: list[tuple[float, float]]) -> tuple[int, int] | None:
    """Return the first crossing pair of segment indices, or None.

    O(n^2) by design: `MAX_OUTLINE_POINTS` bounds the work, and a sweep-line
    implementation would add real complexity for input sizes that never occur
    in practice. If a future sprint raises that bound materially, this is the
    function to revisit.
    """

    n = len(points)
    for i in range(n):
        a1, a2 = points[i], points[(i + 1) % n]
        for j in range(i + 1, n):
            # Skip adjacent segments (and the wrap-around pair), which legally
            # share an endpoint.
            if j == i or (j + 1) % n == i or (i + 1) % n == j:
                continue
            b1, b2 = points[j], points[(j + 1) % n]
            if _segments_properly_intersect(a1, a2, b1, b2):
                return i, j
    return None


def validate_custom_outline(spec: CustomOutlineSpec) -> list[tuple[float, float]]:
    """Validate an outline and return its points converted to millimetres.

    Raises `CustomOutlineInvalidError` (or its
    `CustomOutlineSelfIntersectionError` subclass) with a specific, actionable
    message. Never returns a repaired outline.
    """

    raw = [(p.x, p.y) for p in spec.points]

    if len(raw) > MAX_OUTLINE_POINTS:
        raise CustomOutlineInvalidError(
            f"Outline has {len(raw)} points, above the {MAX_OUTLINE_POINTS} limit."
        )

    for x, y in raw:
        if not (math.isfinite(x) and math.isfinite(y)):
            raise CustomOutlineInvalidError(
                "Outline contains a non-finite coordinate (NaN or infinity)."
            )

    factor = UNIT_TO_MM[spec.unit]
    points = [(x * factor, y * factor) for x, y in raw]

    for x, y in points:
        if abs(x) > MAX_COORDINATE_MM or abs(y) > MAX_COORDINATE_MM:
            raise CustomOutlineInvalidError(
                f"Outline coordinate exceeds the {MAX_COORDINATE_MM}mm limit "
                f"after unit conversion from {spec.unit!r}."
            )

    # A caller must not repeat the first point to close the ring. Detect it
    # explicitly instead of trimming it, so the input contract stays one thing
    # rather than two accepted spellings.
    if len(points) >= 2 and math.dist(points[0], points[-1]) <= DEGENERATE_SEGMENT_MM:
        raise CustomOutlineInvalidError(
            "Outline repeats its first point at the end. The outline is closed "
            "implicitly; supply each vertex exactly once."
        )

    for i in range(len(points)):
        a, b = points[i], points[(i + 1) % len(points)]
        if math.dist(a, b) <= DEGENERATE_SEGMENT_MM:
            raise CustomOutlineInvalidError(
                f"Outline segment {i} is degenerate: points {a} and {b} coincide."
            )

    if len(points) < MIN_OUTLINE_POINTS:
        raise CustomOutlineInvalidError(
            f"Outline needs at least {MIN_OUTLINE_POINTS} distinct points, got {len(points)}."
        )

    area = _signed_area(points)
    if abs(area) < MIN_OUTLINE_AREA_MM2:
        raise CustomOutlineInvalidError(
            f"Outline encloses no area (computed {area:.3e} mm^2). The points are "
            "collinear or the outline collapses on itself."
        )

    crossing = _find_self_intersection(points)
    if crossing is not None:
        i, j = crossing
        raise CustomOutlineSelfIntersectionError(
            f"Outline self-intersects: segment {i} crosses segment {j}. "
            "A stone outline must be a simple closed curve."
        )

    touching = _find_vertex_touching_edge(points)
    if touching is not None:
        vertex_index, segment_index = touching
        raise CustomOutlineSelfIntersectionError(
            f"Outline is not simple: vertex {vertex_index} lies on segment "
            f"{segment_index}. The boundary touches itself, which makes an "
            "offset (and therefore a bezel) ambiguous."
        )

    return points


def normalize_custom_outline(
    spec: CustomOutlineSpec,
) -> tuple[list[OutlinePoint], list[str]]:
    """Validate, then place the outline in JewelMind's canonical local frame.

    Returns the normalized points and the list of operations actually applied,
    for `StoneSourceProvenance.normalizationOperations`.
    """

    points = validate_custom_outline(spec)
    operations: list[str] = []

    if spec.unit != "mm":
        operations.append(f"UNIT_CONVERSION:{spec.unit}->mm")

    # Canonical winding is counter-clockwise (positive signed area), matching
    # the direction CadQuery's own `polyline().close()` produces for the native
    # primitives. A consistent winding is what lets a bezel offset outward
    # rather than inward without inspecting each outline.
    if _signed_area(points) < 0:
        points = list(reversed(points))
        operations.append("WINDING_REVERSED:CW->CCW")

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    cx = (min(xs) + max(xs)) / 2.0
    cy = (min(ys) + max(ys)) / 2.0
    if abs(cx) > DEGENERATE_SEGMENT_MM or abs(cy) > DEGENERATE_SEGMENT_MM:
        points = [(x - cx, y - cy) for x, y in points]
        operations.append(f"ORIGIN_RECENTERED:bbox_center({cx:.9f},{cy:.9f})")

    return [OutlinePoint(x=x, y=y) for x, y in points], operations
