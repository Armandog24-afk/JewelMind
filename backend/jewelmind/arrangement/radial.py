"""The one place a ring of stones becomes a list of angles (Sprint 25).

WHY THIS MODULE EXISTS. The resolver expands a `RADIAL` pattern, Sprint 24's
family compiler places a cluster's ring explicitly, and Sprint 25's halo places
its rings explicitly — three callers computing the same angular sequence. Two of
those copies already existed and `family/compile.py` documented the duplication
in prose; a third would have made a drift between them a matter of time, and the
symptom would be a halo whose stones sit at angles a hand-written radial pattern
would not reproduce.

A FULL SWEEP AND A PARTIAL ARC DISTRIBUTE DIFFERENTLY, and the difference is the
whole reason this is a function rather than one expression. At 360 degrees the
last member would land on the first, so the step is `sweep / count`. On a partial
arc both endpoints are wanted, so the step is `sweep / (count - 1)`. Using one
formula for both would either double a stone at the start angle or leave an arc
short of its stated end.

ARITHMETIC-PRESERVING. The expressions are character-for-character the ones
`resolve.py::_radial_offsets` used before this extraction, in the same order, so
no existing resolution moves: float addition is not associative and rewriting
`start + step * i` as an accumulation would drift by ~1e-14 per member. That is
the same discipline Sprint 23 applied to the basket bore.

KERNEL-FREE. Angles in degrees, like every other angle in JewelMind.
"""

from __future__ import annotations


def ring_angles_deg(count: int, start_angle_deg: float, sweep_deg: float) -> list[float]:
    """The angular positions of `count` members, in increasing-angle order.

    `count` is assumed positive — every caller reaches this through a model
    field bounded at `ge=1`, so validating again here would be a second,
    weaker copy of a constraint the schema already enforces.
    """

    if count == 1:
        # A single member sits at the start angle; neither divisor applies.
        return [start_angle_deg]
    if sweep_deg >= 360.0:
        step = sweep_deg / count
        return [start_angle_deg + step * i for i in range(count)]
    step = sweep_deg / (count - 1)
    return [start_angle_deg + step * i for i in range(count)]
