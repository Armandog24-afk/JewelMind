"""Prong body geometry, one builder per style (Sprint 23).

A REGISTRY, not an `if style == ...` chain — the same discipline
`dispatch.py` applies to setting families, for the same reason: a new style is
a new entry, not an edit to a branch every existing style flows through.

THE ROUND PRONG IS PRESERVED EXACTLY. `_round_prong()` is the pre-Sprint-23
construction character-for-character: same `Workplane("XY")`, same
`workplane(offset=...)`, `center()`, `circle()`, `extrude()` sequence. That is
what keeps every prong volume, every preview mesh and all 39 Golden baselines
byte-identical for the designs that had no style to choose from. A "unified"
builder that produced round as a degenerate taper would have been tidier and
would have moved the geometry.

EVERY CONSTANT HERE IS A CONSTRUCTION PARAMETER. The V notch's angular width
and depth fractions are software choices that produce a robust boolean; they
are not setter geometry and no claim is made that a stone would sit in one
correctly (SETTING-GOV-010).
"""

from __future__ import annotations

import math
from collections.abc import Callable
from functools import lru_cache

import cadquery as cq

from jewelmind.setting.errors import SettingGenerationFailedError
from jewelmind.setting.models import ProngStyle

#: The V notch's opening angle, degrees. Wide enough that the cut tool is not
#: a sliver — a near-zero-angle wedge is where OCCT booleans are least
#: reliable — and narrow enough to leave a recognisable V.
V_NOTCH_ANGLE_DEG = 90.0

#: How far down the prong the CLAW's taper reaches, as a fraction of its
#: height. Used by the claw's shaft/head split, not by the V notch — the notch
#: is sized from the prong's radius, for the reason `_v_prong()` documents.
V_NOTCH_DEPTH_FRACTION = 0.35

#: The notch's half-width as a multiple of the prong radius.
#:
#: STRICTLY LESS THAN 1, and that is the whole difference between a V prong and
#: a shortened cylinder. The groove runs across the prong, so material survives
#: only where |x| exceeds this half-width — those two surviving horns are what
#: make the tip a V. At 1.05 the wedge spanned wider than the prong and shaved
#: the entire top face away, leaving a 0.025 mm rim and a solid that reported
#: `V_PRONG` while looking like a truncated round one.
V_NOTCH_WIDTH_FACTOR = 0.6

#: A claw's tip radius floor, as a fraction of the prong radius. Prevents a
#: degenerate zero-radius loft, which OCCT can build and then fail to fuse.
MIN_TIP_RATIO = 0.1

ProngSolidBuilder = Callable[[float, float, float, float, float, float], cq.Shape]


def _round_prong(
    x: float, y: float, base_z: float, height: float, radius: float, tip_ratio: float
) -> cq.Shape:
    """The pre-Sprint-23 cylinder, unchanged.

    `tip_ratio` is accepted and deliberately ignored: a round prong is a
    straight cylinder by definition, and honouring the ratio here would
    silently change the geometry of every existing design.
    """

    return (
        cq.Workplane("XY")
        .workplane(offset=base_z)
        .center(x, y)
        .circle(radius)
        .extrude(height)
        .val()
    )


def _tapered_prong(
    x: float, y: float, base_z: float, height: float, radius: float, tip_ratio: float
) -> cq.Shape:
    """A straight taper: full radius at the base, `tip_ratio * radius` at the top.

    Built as a cone frustum rather than a loft. `makeCone` is a single OCCT
    primitive with no section-matching to get wrong, which matters because a
    two-circle loft over a large radius ratio is exactly where Sprint 20 found
    lofts overshooting their bounding box.
    """

    tip_radius = max(radius * tip_ratio, radius * MIN_TIP_RATIO)
    return cq.Solid.makeCone(
        radius, tip_radius, height, pnt=cq.Vector(x, y, base_z), dir=cq.Vector(0, 0, 1)
    )


def _claw_prong(
    x: float, y: float, base_z: float, height: float, radius: float, tip_ratio: float
) -> cq.Shape:
    """A claw: a cylindrical shaft with a tapered head.

    Two stacked primitives fused, rather than one long taper. A claw's
    distinguishing feature is that the taper is CONCENTRATED near the tip — a
    single frustum over the full height is a `TAPERED_PRONG`, which is why both
    styles exist rather than one with a parameter.
    """

    shaft_height = height * (1.0 - V_NOTCH_DEPTH_FRACTION)
    head_height = height - shaft_height
    tip_radius = max(radius * tip_ratio, radius * MIN_TIP_RATIO)

    shaft = cq.Solid.makeCylinder(
        radius, shaft_height, pnt=cq.Vector(x, y, base_z), dir=cq.Vector(0, 0, 1)
    )
    head = cq.Solid.makeCone(
        radius,
        tip_radius,
        head_height,
        pnt=cq.Vector(x, y, base_z + shaft_height),
        dir=cq.Vector(0, 0, 1),
    )
    try:
        return shaft.fuse(head)
    except Exception as exc:  # noqa: BLE001 - OCC boolean failures vary widely
        raise SettingGenerationFailedError(
            f"Claw prong construction failed while fusing shaft and head: {exc}. "
            "Raised rather than falling back to a plain cylinder, which would "
            "silently build a different style than the one requested."
        ) from exc


def _v_prong(
    x: float, y: float, base_z: float, height: float, radius: float, tip_ratio: float
) -> cq.Shape:
    """A prong with a V notch cut into its tip.

    The notch is cut with a wedge oriented along the prong's own radial
    direction from the design axis, so the V opens outward — which is the only
    orientation that makes sense at a pointed stone's apex. A prong exactly on
    the axis has no radial direction, so the notch falls back to +X and says so
    in no uncertain terms rather than producing an arbitrary rotation.
    """

    body = cq.Solid.makeCylinder(
        radius, height, pnt=cq.Vector(x, y, base_z), dir=cq.Vector(0, 0, 1)
    )

    # THE NOTCH IS SIZED FROM THE PRONG, NOT FROM ITS HEIGHT.
    #
    # The first implementation derived the half-width from a fraction of the
    # prong's HEIGHT, which made the wedge several times wider than the prong
    # itself: the cut then removed the entire tip across the full diameter and
    # produced a shortened cylinder, not a V. A prong reporting `V_PRONG` and
    # delivering a truncated round one is exactly the silent substitution
    # SETTING-GOV-013 forbids, so the geometry is derived from the radius and
    # the notch's own opening angle instead.
    half_angle = math.radians(V_NOTCH_ANGLE_DEG / 2.0)
    half_width = radius * V_NOTCH_WIDTH_FACTOR
    notch_depth = half_width / math.tan(half_angle)
    # Wide enough to clear the prong body in every direction, so the cut is a
    # clean through-notch rather than leaving a shell.
    reach = radius * 2.0

    radial = math.degrees(math.atan2(y, x)) if (x or y) else 0.0

    notch_profile = (
        cq.Workplane("XZ")
        .polyline(
            [
                (-half_width, base_z + height),
                (half_width, base_z + height),
                (0.0, base_z + height - notch_depth),
            ]
        )
        .close()
        .extrude(reach, both=True)
    )
    notch = notch_profile.val().rotate(
        cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), radial
    ).translate(cq.Vector(x, y, 0))

    try:
        cut = body.cut(notch)
    except Exception as exc:  # noqa: BLE001
        raise SettingGenerationFailedError(
            f"V prong construction failed while cutting the notch: {exc}. Raised "
            "rather than returning the uncut cylinder, which would report a V "
            "prong and build a round one."
        ) from exc

    if not cut.Solids():
        raise SettingGenerationFailedError(
            "V prong notch cut produced no solid; the notch would consume the "
            "whole prong body."
        )
    return cut


@lru_cache(maxsize=1)
def prong_solid_builders() -> dict[str, ProngSolidBuilder]:
    """The style registry. Every entry builds a real solid."""

    return {
        "ROUND_PRONG": _round_prong,
        "TAPERED_PRONG": _tapered_prong,
        "CLAW_PRONG": _claw_prong,
        "V_PRONG": _v_prong,
    }


def build_prong_solid(
    style: ProngStyle,
    x: float,
    y: float,
    base_z: float,
    height: float,
    radius: float,
    tip_ratio: float,
) -> cq.Shape:
    """One prong solid in the requested style.

    An unregistered style is an explicit error, never a substitution: building
    a round prong for a requested claw would report one style and deliver
    another (SETTING-GOV-013).
    """

    builder = prong_solid_builders().get(style)
    if builder is None:
        raise SettingGenerationFailedError(
            f"No prong solid builder is registered for style {style!r}. "
            f"Registered: {sorted(prong_solid_builders())}."
        )
    solid = builder(x, y, base_z, height, radius, tip_ratio)
    if not solid.Solids():
        raise SettingGenerationFailedError(
            f"Prong style {style!r} produced no solid at ({x}, {y})."
        )
    return solid
