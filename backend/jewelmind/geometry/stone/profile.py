"""3D reference profiles for stone geometry (brief sections 21/26/36).

This module owns the SECOND axis of Stone v2: given an outline builder, it
produces the stone's three-dimensional reference body. Separating it from
`outline.py` is what lets `OVAL + CABOCHON_REFERENCE` exist without an
`OVAL_CABOCHON` enum member, and what lets a CUSTOM outline reuse the exact
same profile pipeline every native shape uses (brief section 26).

An outline builder here is any callable `(scale: float) -> cq.Wire` that
returns the same silhouette scaled about the local origin. Callers bind the
shape's dimensions before handing it over, so this module never needs to know
which shape it is building.

Every profile produces a real, deterministic B-Rep solid. None of them models
a real facet arrangement, and none may ever be described as one
(STONEV2-GOV-003).
"""

from __future__ import annotations

import math
from collections.abc import Callable

import cadquery as cq

from jewelmind.stone.errors import (
    StoneProfileUnsupportedError,
    StoneShapeGenerationFailedError,
)

OutlineAtScale = Callable[[float], cq.Wire]

# Shared faceted proportions — unchanged from Sprint 18 so every existing shape
# keeps producing byte-identical geometry (brief section 70).
CROWN_FRACTION = 0.35
PAVILION_FRACTION = 0.65
TABLE_TO_GIRDLE_RATIO = 0.56
CULET_SCALE_RATIO = 0.05

#: Cabochon: how tall the dome is above the girdle, and how far the base sits
#: below it, both as fractions of total depth. Fixed SOFTWARE REFERENCE
#: CONSTRUCTION parameters — no commercial cabochon proportion is claimed
#: (STONEV2-GOV-003).
CABOCHON_DOME_FRACTION = 0.75
CABOCHON_BASE_FRACTION = 0.25
CABOCHON_BASE_SCALE = 0.55
CABOCHON_APEX_SCALE = 0.04

#: Number of horizontal sections used to approximate the cabochon dome.
#:
#: Chosen from a real measured convergence run during Sprint 20 prototyping
#: (round cabochon, 6.5mm x 3.0mm): 8 sections -> 64.4884 mm^3, 12 -> 64.7957,
#: 16 -> 64.9082. The 12->16 step moves the result by 0.17% against 0.48% for
#: 8->12, so 16 sits on the flat part of the curve. Same empirical approach as
#: `geometry/shank/builder.py::SECTION_COUNT`.
CABOCHON_DOME_SECTIONS = 16


def _loft(wires: list[cq.Wire], what: str) -> cq.Solid:
    """Loft with `ruled=True` and verify the result is a real solid.

    `ruled=True` is not a style preference. A smooth (`ruled=False`) loft over
    these sections bulges between them, so the finished solid's bounding box
    exceeds the requested dimensions — measured at 6.5088mm for a 6.5mm
    request during Sprint 20 prototyping — which would break the
    requested-equals-measured dimension contract. Worse, a smooth loft over
    ELLIPSE sections produced a body that did not survive STEP export at all
    (re-imported with zero solids), the same failure class Sprint 19 hit with
    `offset2D` on an ellipse.
    """

    try:
        solid = cq.Solid.makeLoft(wires, ruled=True)
    except Exception as exc:  # noqa: BLE001 - OCC loft failures vary widely
        raise StoneShapeGenerationFailedError(
            f"Could not construct {what}: {exc}. This is a real construction "
            "failure, never silently downgraded to another shape or profile."
        ) from exc

    if not solid.Solids() or not solid.isValid():
        raise StoneShapeGenerationFailedError(
            f"Constructing {what} produced no valid solid. This configuration is "
            "not constructible with the current builder."
        )
    return solid


def build_faceted_reference(
    outline_at: OutlineAtScale, depth_mm: float, girdle_z_mm: float
) -> cq.Solid:
    """The Sprint 18 three-level culet/girdle/table reference body.

    Unchanged in construction so every Stone v1 shape keeps generating
    byte-identical geometry.
    """

    crown_h = depth_mm * CROWN_FRACTION
    pavilion_h = depth_mm * PAVILION_FRACTION
    return _loft(
        [
            outline_at(CULET_SCALE_RATIO).translate((0, 0, girdle_z_mm - pavilion_h)),
            outline_at(1.0).translate((0, 0, girdle_z_mm)),
            outline_at(TABLE_TO_GIRDLE_RATIO).translate((0, 0, girdle_z_mm + crown_h)),
        ],
        "a faceted reference body",
    )


def build_cabochon_reference(
    outline_at: OutlineAtScale, depth_mm: float, girdle_z_mm: float
) -> cq.Solid:
    """A domed cabochon body: a shallow base below the girdle, a smooth-ish
    dome above it (brief section 21).

    A cabochon is genuinely a different 3D class, not a different outline: the
    same OVAL outline yields an oval cabochon here and a faceted oval in
    `build_faceted_reference`. The dome follows an ellipsoidal profile,
    `scale = sqrt(1 - t^2)`, sampled at `CABOCHON_DOME_SECTIONS` levels.
    """

    dome_h = depth_mm * CABOCHON_DOME_FRACTION
    base_h = depth_mm * CABOCHON_BASE_FRACTION

    wires = [
        outline_at(CABOCHON_BASE_SCALE).translate((0, 0, girdle_z_mm - base_h)),
        outline_at(1.0).translate((0, 0, girdle_z_mm)),
    ]
    for i in range(1, CABOCHON_DOME_SECTIONS + 1):
        t = i / CABOCHON_DOME_SECTIONS
        scale = (
            CABOCHON_APEX_SCALE
            if i == CABOCHON_DOME_SECTIONS
            else math.sqrt(max(1.0 - t * t, 1e-6))
        )
        wires.append(outline_at(scale).translate((0, 0, girdle_z_mm + dome_h * t)))

    return _loft(wires, "a cabochon reference body")


def build_spherical_reference(diameter_mm: float, girdle_z_mm: float) -> cq.Solid:
    """A sphere — the pearl / bead reference (brief section 22).

    The only profile that ignores its outline entirely: for a sphere the
    silhouette is a consequence of the body, not an input to it. Its "girdle"
    is the equator, which is what `girdle_z_mm` positions.
    """

    if not math.isfinite(diameter_mm) or diameter_mm <= 0:
        raise StoneShapeGenerationFailedError(
            f"A spherical reference needs a positive finite diameter, got {diameter_mm!r}."
        )
    try:
        solid = cq.Solid.makeSphere(
            diameter_mm / 2, angleDegrees1=-90, angleDegrees2=90
        ).translate((0, 0, girdle_z_mm))
    except Exception as exc:  # noqa: BLE001
        raise StoneShapeGenerationFailedError(
            f"Could not construct a spherical reference of diameter {diameter_mm}: {exc}."
        ) from exc

    if not solid.Solids() or not solid.isValid():
        raise StoneShapeGenerationFailedError(
            "Constructing a spherical reference produced no valid solid."
        )
    return solid


#: Registry of real, implemented profile builders (brief section 67). A
#: registry rather than an if/elif chain, so a future profile is a registration
#: rather than an edit to a growing conditional. `SPHERICAL_REFERENCE` is absent
#: because it does not consume an outline and is dispatched separately.
PROFILE_BUILDERS: dict[str, Callable[[OutlineAtScale, float, float], cq.Solid]] = {
    "FACETED_REFERENCE": build_faceted_reference,
    "CABOCHON_REFERENCE": build_cabochon_reference,
}


def build_profile(
    profile: str, outline_at: OutlineAtScale, depth_mm: float, girdle_z_mm: float
) -> cq.Solid:
    """Build an outline-consuming reference body for the requested profile."""

    builder = PROFILE_BUILDERS.get(profile)
    if builder is None:
        raise StoneProfileUnsupportedError(
            f"No registered builder for stone reference profile {profile!r}."
        )
    return builder(outline_at, depth_mm, girdle_z_mm)
