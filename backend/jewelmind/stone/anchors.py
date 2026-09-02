"""Deterministic stone anchors (brief section 43; STONEV2-GOV-009).

An anchor is a GEOMETRIC FACT: a named point on the stone's outline, in the
stone's own local millimetre frame. It is explicitly NOT a prong position. The
Stone System reports where a stone's tip, cleft, corners or wide end are; the
Setting System decides whether to put metal there. Keeping that boundary is
what stops shape knowledge from leaking back into Setting as per-shape
special cases.

Every anchor is derived from the REAL normalized outline points, never from
the nominal dimensions. That matters for a shape whose extreme is not at a
vertex (`half_moon`'s elliptical arc) and for custom outlines, where nominal
dimensions do not exist at all.

Anchors a shape genuinely does not have are absent, never approximated: a
custom outline has no deterministic TIP, and reporting one would be a
fabricated fact.
"""

from __future__ import annotations

from jewelmind.stone.capability import STONE_SHAPE_CAPABILITIES_V2
from jewelmind.stone.models import OutlinePoint, StoneAnchor, StoneAnchorId

#: Which local-Y direction each pointed shape's TIP faces at orientation 0.
#: Read off the real outline constructions in `geometry/stone/outline.py`.
_TIP_DIRECTION_Y: dict[str, float] = {
    "pear": +1.0,
    "marquise": +1.0,
    "triangle": +1.0,
    "trillion": +1.0,
    "kite": +1.0,
    "lozenge": +1.0,
    "hexagon": +1.0,
    "heart": -1.0,
    "shield": -1.0,
}

#: Which local-Y direction the WIDE end of a tapered shape faces. The narrow
#: end is always the opposite. Matches `_tapered_quadrilateral`'s convention.
_WIDE_END_DIRECTION_Y: dict[str, float] = {
    "tapered_baguette": -1.0,
    "trapezoid": -1.0,
}


def _extreme(points: list[OutlinePoint], key, reverse: bool) -> OutlinePoint:
    """The extreme point under `key`, tie-broken deterministically.

    A tie is real: a rectangle has two points at maximum Y. Sorting on a full
    (primary, secondary) key rather than using `max()` makes the choice stable
    for a given outline instead of depending on input order.
    """

    return sorted(points, key=key, reverse=reverse)[0]


def derive_anchors(shape: str, points: list[OutlinePoint]) -> list[StoneAnchor]:
    """Every anchor this shape declares, derived from its real outline.

    The set of anchors is driven by the shape's registry entry, so the registry
    and the derivation can never disagree about which anchors exist.
    """

    entry = STONE_SHAPE_CAPABILITIES_V2.get(shape)
    declared: set[str] = set(entry.anchors) if entry else {"CENTER", "TOP", "BOTTOM", "LEFT", "RIGHT"}

    xs = [p.x for p in points]
    ys = [p.y for p in points]
    cx = (min(xs) + max(xs)) / 2.0
    cy = (min(ys) + max(ys)) / 2.0

    found: dict[StoneAnchorId, tuple[float, float]] = {}

    if "CENTER" in declared:
        found["CENTER"] = (cx, cy)
    if "TOP" in declared:
        p = _extreme(points, lambda q: (q.y, abs(q.x)), reverse=True)
        found["TOP"] = (p.x, p.y)
    if "BOTTOM" in declared:
        p = _extreme(points, lambda q: (-q.y, abs(q.x)), reverse=True)
        found["BOTTOM"] = (p.x, p.y)
    if "LEFT" in declared:
        p = _extreme(points, lambda q: (-q.x, abs(q.y)), reverse=True)
        found["LEFT"] = (p.x, p.y)
    if "RIGHT" in declared:
        p = _extreme(points, lambda q: (q.x, abs(q.y)), reverse=True)
        found["RIGHT"] = (p.x, p.y)

    if "TIP" in declared:
        direction = _TIP_DIRECTION_Y.get(shape)
        if direction is not None:
            # The tip is the extreme point along the tip direction that also
            # sits nearest the centre line — which distinguishes a true point
            # from the two corners of a flat end.
            p = _extreme(points, lambda q: (direction * q.y, -abs(q.x - cx)), reverse=True)
            found["TIP"] = (p.x, p.y)

    if "CLEFT" in declared and shape == "heart":
        # The heart outline crosses its own centre line exactly twice: at the
        # TIP (lowest) and at the CLEFT (highest). Taking the highest on-axis
        # point therefore identifies the cleft without needing to detect a
        # local minimum, which would be fragile on a sampled outline.
        #
        # The tolerance is proportional to the stone's width rather than
        # absolute, so it behaves identically for a 4mm and a 40mm stone. It is
        # a sampling tolerance for finding a point, never a jewelry tolerance.
        half_width = (max(xs) - min(xs)) / 2.0
        axis_tolerance = max(half_width * 0.02, 1e-9)
        on_axis = [p for p in points if abs(p.x - cx) <= axis_tolerance]
        if on_axis:
            found["CLEFT"] = max(((p.x, p.y) for p in on_axis), key=lambda t: t[1])

    if "LEFT_LOBE" in declared and shape == "heart":
        p = _extreme(points, lambda q: (-q.x, q.y), reverse=True)
        found["LEFT_LOBE"] = (p.x, p.y)
    if "RIGHT_LOBE" in declared and shape == "heart":
        p = _extreme(points, lambda q: (q.x, q.y), reverse=True)
        found["RIGHT_LOBE"] = (p.x, p.y)

    if "WIDE_END" in declared or "NARROW_END" in declared:
        direction = _WIDE_END_DIRECTION_Y.get(shape)
        if direction is not None:
            wide_side = [p for p in points if (p.y - cy) * direction > 0]
            narrow_side = [p for p in points if (p.y - cy) * direction < 0]
            if wide_side and "WIDE_END" in declared:
                found["WIDE_END"] = (cx, sum(p.y for p in wide_side) / len(wide_side))
            if narrow_side and "NARROW_END" in declared:
                found["NARROW_END"] = (cx, sum(p.y for p in narrow_side) / len(narrow_side))

    corner_ids: dict[StoneAnchorId, tuple[float, float]] = {
        "CORNER_NE": (+1.0, +1.0),
        "CORNER_NW": (-1.0, +1.0),
        "CORNER_SE": (+1.0, -1.0),
        "CORNER_SW": (-1.0, -1.0),
    }
    for anchor_id, (sx, sy) in corner_ids.items():
        if anchor_id not in declared:
            continue
        # The point furthest along the corner's diagonal direction. For a
        # clipped-corner shape this is the clip's own vertex, which is the
        # honest answer: the corner was cut off, and the anchor reports where
        # the real outline actually turns.
        p = _extreme(points, lambda q, sx=sx, sy=sy: (sx * q.x + sy * q.y), reverse=True)
        found[anchor_id] = (p.x, p.y)

    order: list[StoneAnchorId] = [
        "CENTER", "TOP", "BOTTOM", "LEFT", "RIGHT", "TIP", "CLEFT",
        "LEFT_LOBE", "RIGHT_LOBE", "WIDE_END", "NARROW_END",
        "CORNER_NW", "CORNER_NE", "CORNER_SW", "CORNER_SE",
    ]
    return [
        StoneAnchor(anchor=a, x=found[a][0], y=found[a][1])
        for a in order
        if a in found
    ]
