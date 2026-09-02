"""Prong placement strategies (brief section 10; SETTING-GOV-008).

Placement consumes real Stone System geometry — the resolved dimensions and
the stone's own girdle outline — rather than hardcoding
`angle = 360 / prongCount` for every shape.

Two strategies exist, and which one runs is decided by the stone's real
symmetry class, never by a shape-name branch in a caller:

- **RADIAL** — evenly spaced angles on a circle inset from the girdle.
  Correct for a radially symmetric stone, and byte-identical to the
  pre-Sprint-19 behaviour, which is what preserves round's Goldens.
- **OUTLINE_CARDINAL** — positions sampled from the stone's actual outline
  at evenly spaced angular directions, each pulled inward from the real
  outline point. Genuinely shape-aware: an oval's prongs sit near its own
  perimeter, not on a circle derived from its narrow axis.

Neither strategy claims to be a professionally correct setting position
(SETTING-GOV-007/010). Compatibility for every non-round shape is
`EXPERIMENTAL` precisely because these are provisional software placements.
"""

from __future__ import annotations

import math

from jewelmind.setting.errors import SettingPlacementFailedError
from jewelmind.setting.models import ProngPlacementStrategy, StoneSettingReference
from jewelmind.setting.stone_interface import girdle_outline_wire

#: How far a prong's axis is pulled inside the girdle so its body overlaps
#: the girdle edge and reads as a grip rather than a tangent touch. A
#: fraction of the prong's own radius, inherited unchanged from the
#: pre-Sprint-19 `geometry/constants.py::prong_center_radius()` so round's
#: geometry is preserved exactly. A construction parameter, not a jewelry
#: threshold (SETTING-GOV-010).
GIRDLE_INSET_PRONG_RADIUS_FRACTION = 0.3

#: Angular samples used to find where a direction ray leaves the outline.
#: Purely a numerical search resolution.
_OUTLINE_SAMPLES = 720


def resolve_strategy(reference: StoneSettingReference) -> ProngPlacementStrategy:
    """Pick the placement strategy from the stone's real geometry.

    RADIAL is geometrically faithful exactly when the outline is the same in
    every direction from its centre; every other stone gets the outline-aware
    strategy, including `pear`, whose asymmetry the outline itself carries.

    Selected on the GEOMETRIC PROPERTY, not on the shape's name. Sprint 19 wrote
    this as `shape == "round"`, which was equivalent at the time because round
    was the only radially symmetric shape — but it made the Setting System a
    list of known names again, which is exactly what Stone v2 set out to end.
    Round still resolves to RADIAL, so generated geometry is unchanged.
    """

    return "RADIAL" if reference.isRadiallySymmetric else "OUTLINE_CARDINAL"


def radial_positions(
    reference: StoneSettingReference, prong_count: int, prong_radius_mm: float
) -> list[tuple[float, float]]:
    """The exact pre-Sprint-19 placement: evenly spaced angles on a circle
    of radius `girdle_r - prong_r * 0.3`.

    Kept character-for-character equivalent to the original
    `prongs.py::_prong_positions()` + `constants.py::prong_center_radius()`
    pair, including the `cos`/`sin` order and the `2*pi*i/count` phase, so
    round's generated geometry is byte-identical.
    """

    girdle_r = reference.widthMm / 2
    center_r = girdle_r - prong_radius_mm * GIRDLE_INSET_PRONG_RADIUS_FRACTION
    return [
        (
            center_r * math.cos(2 * math.pi * i / prong_count),
            center_r * math.sin(2 * math.pi * i / prong_count),
        )
        for i in range(prong_count)
    ]


def _outline_points(reference: StoneSettingReference) -> list[tuple[float, float]]:
    """Sample the stone's real girdle outline into (x, y) points, with the
    stone's own orientation applied so a rotated stone's prongs rotate with
    it."""

    wire = girdle_outline_wire(reference)
    if reference.orientationDeg:
        wire = wire.rotate((0, 0, 0), (0, 0, 1), reference.orientationDeg)
    points: list[tuple[float, float]] = []
    for k in range(_OUTLINE_SAMPLES):
        p = wire.positionAt(k / _OUTLINE_SAMPLES)
        points.append((p.x, p.y))
    return points


def outline_cardinal_positions(
    reference: StoneSettingReference, prong_count: int, prong_radius_mm: float
) -> list[tuple[float, float]]:
    """Shape-aware placement.

    For each of `prong_count` evenly spaced *directions*, find the point
    where the stone's own outline extends furthest along that direction,
    then pull it inward by the same girdle inset the radial strategy uses.
    The result follows the real silhouette: an oval's prongs sit near its
    own perimeter on both axes, and an emerald's sit on its flats rather
    than on a circle that ignores its corners.

    Directions start at +X and advance counter-clockwise, matching the
    radial strategy's phase so a round stone would produce the same
    ordering.
    """

    points = _outline_points(reference)
    if not points:  # pragma: no cover - a valid wire always samples
        raise SettingPlacementFailedError(
            f"Could not sample the girdle outline for stone shape {reference.shape!r}."
        )

    inset = prong_radius_mm * GIRDLE_INSET_PRONG_RADIUS_FRACTION
    positions: list[tuple[float, float]] = []

    for i in range(prong_count):
        angle = 2 * math.pi * i / prong_count
        ux, uy = math.cos(angle), math.sin(angle)
        # The outline point furthest along this direction.
        best = max(points, key=lambda p: p[0] * ux + p[1] * uy)
        distance = best[0] * ux + best[1] * uy
        pulled = max(distance - inset, 0.0)
        positions.append((pulled * ux, pulled * uy))

    return positions


def prong_positions(
    reference: StoneSettingReference,
    prong_count: int,
    prong_radius_mm: float,
    strategy: ProngPlacementStrategy | None = None,
) -> tuple[list[tuple[float, float]], ProngPlacementStrategy]:
    """Resolve and run the placement strategy.

    Returns the positions and the strategy actually used, so the caller can
    report it as a real fact rather than assuming.
    """

    if prong_count <= 0:
        return [], strategy or resolve_strategy(reference)

    resolved = strategy or resolve_strategy(reference)
    if resolved == "RADIAL":
        return radial_positions(reference, prong_count, prong_radius_mm), resolved
    return outline_cardinal_positions(reference, prong_count, prong_radius_mm), resolved
