"""The Shank builder (brief sections 19/24/25) — dispatches between two
real, deterministic construction paths:

- **uniform** (`widthTaper.mode == thicknessTaper.mode == "NONE"`): the
  exact pre-Sprint-17 `revolve()`-based construction, byte-for-byte
  unchanged, including the outer-rim fillet. This guarantees zero Golden
  regression for every existing case (SHANK-GOV-008/009).
- **tapered** (either taper mode is not "NONE"): a real multi-section
  loft around the full 360 degrees, sampling `SECTION_COUNT` profile
  wires (reusing the exact same `geometry.shank.profile` builders) at
  deterministic angular positions. See
  docs/bible/19-shank/551-shank-generation-pipeline.md for why loft was
  chosen over sweep after real experimentation.

The dispatch is based on whether taper is actually requested, never on
any implicit heuristic — SHANK-GOV-001 (deterministic), SHANK-GOV-007
(never silently repair/reinterpret input).
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.connection import shank_connection_interface
from jewelmind.geometry.constants import inner_radius, outer_radius
from jewelmind.geometry.model import BoundingBox, GeneratedComponent
from jewelmind.geometry.primitives.selectors import FlatCircleAtRadius
from jewelmind.geometry.shank.profile import build_profile
from jewelmind.geometry.shank.taper import angle_deg_for_u, taper_ratio

# Number of profile sections sampled around the full 360 degrees for a
# tapered loft. Chosen empirically by measuring real volume convergence
# vs section count (16/24/36/48/72 all tested): 48 sections is within
# 0.16% of the 72-section volume while costing ~22% less — see
# docs/bible/19-shank/551-shank-generation-pipeline.md for the real
# measured table this decision is based on.
SECTION_COUNT = 48

# Outer rim fillet radius is capped at 15% of the smallest relevant
# dimension so it never grows large enough to distort thin bands —
# unchanged from pre-Sprint-17 band.py, uniform path only.
_FILLET_FRACTION = 0.15
_FILLET_MAX_MM = 0.25


class ShankConstructionError(Exception):
    """A requested Shank configuration could not be constructed. Raised
    rather than silently falling back to uniform geometry (SHANK-GOV-007,
    brief section 48)."""


def _try_fillet_outer_rim(solid: cq.Workplane, outer_r: float, fillet_radius: float) -> cq.Workplane:
    selector = FlatCircleAtRadius(outer_r)
    return solid.edges(selector).fillet(fillet_radius)


def _build_uniform_shank(definition: JewelryDefinition) -> GeneratedComponent:
    """The exact pre-Sprint-17 construction — see git history for
    `geometry/components/band.py` before this Sprint. Never changed by
    this Sprint's taper work; this is what guarantees zero Golden
    regression for every existing case."""

    warnings: list[str] = []
    inner_r = inner_radius(definition)
    outer_r = outer_radius(definition)
    half_width = definition.band.width / 2

    wire = build_profile(definition.band.profile, inner_r, outer_r, half_width)
    solid = wire.revolve(360, (0, 0, 0), (0, 1, 0))

    fillet_radius = min(
        _FILLET_MAX_MM,
        definition.band.width * _FILLET_FRACTION,
        definition.band.thickness * _FILLET_FRACTION,
    )
    fallback_used = False
    if fillet_radius > 0.02:
        try:
            filleted = _try_fillet_outer_rim(solid, outer_r, fillet_radius)
            if not filleted.solids().vals():
                raise ValueError("fillet produced no solid")
            solid = filleted
        except Exception as exc:  # noqa: BLE001 - deliberately broad: OCC fillet failures vary
            fallback_used = True
            warnings.append(
                f"Outer rim fillet could not be applied ({exc}); falling back to sharp edges."
            )

    shape = solid.val()
    interface = shank_connection_interface(definition)
    metadata = {
        "profile": definition.band.profile,
        "innerRadiusMm": inner_r,
        "outerRadiusMm": outer_r,
        "filletApplied": not fallback_used,
        "variation": "UNIFORM",
        "widthTaperMode": "NONE",
        "thicknessTaperMode": "NONE",
        "sectionCount": 1,
        "connectionInterface": {
            "topZMm": interface.topZMm,
            "embedMm": interface.embedMm,
            "headCenterRadiusMm": interface.headCenterRadiusMm,
        },
    }

    return GeneratedComponent(
        name="band",
        shape=shape,
        volume_mm3=shape.Volume(),
        bounding_box=BoundingBox.from_shape(shape),
        warnings=warnings,
        metadata=metadata,
    )


def _section_wire(
    u: float,
    profile_type: str,
    inner_r: float,
    base_outer_r: float,
    base_half_width: float,
    width_taper,
    thickness_taper,
) -> cq.Wire:
    half_width = base_half_width * taper_ratio(u, width_taper)
    thickness = (base_outer_r - inner_r) * taper_ratio(u, thickness_taper)
    outer_r = inner_r + thickness
    wire = build_profile(profile_type, inner_r, outer_r, half_width)
    angle = angle_deg_for_u(u)
    return wire.rotate((0, 0, 0), (0, 1, 0), angle).val()


def _build_tapered_shank(definition: JewelryDefinition) -> GeneratedComponent:
    """A real multi-section loft — see module docstring. Fillet is not
    yet implemented for a tapered outer rim (there is no single "circle
    at radius X" to select once the radius varies by angle); this is a
    real, documented v1 limitation, not a silent omission
    (SHANK-GOV-014)."""

    inner_r = inner_radius(definition)
    base_outer_r = outer_radius(definition)
    base_half_width = definition.band.width / 2
    width_taper = definition.band.widthTaper
    thickness_taper = definition.band.thicknessTaper
    interface = shank_connection_interface(definition)

    wires = [
        _section_wire(
            i / SECTION_COUNT,
            definition.band.profile,
            inner_r,
            base_outer_r,
            base_half_width,
            width_taper,
            thickness_taper,
        )
        for i in range(SECTION_COUNT + 1)  # +1 closes the loop: wire[N] == wire[0]
    ]

    try:
        solid = cq.Solid.makeLoft(wires, ruled=True)
    except Exception as exc:  # noqa: BLE001 - OCC loft failures vary widely
        raise ShankConstructionError(
            f"Could not construct the requested tapered shank ({exc}). "
            "This is a real construction failure, not silently downgraded to a uniform shank."
        ) from exc

    if not solid.Solids() or not solid.isValid():
        raise ShankConstructionError(
            "The requested tapered shank produced no valid solid — the taper configuration "
            "is not constructible with the current loft-based builder."
        )

    metadata = {
        "profile": definition.band.profile,
        "innerRadiusMm": inner_r,
        "outerRadiusMm": base_outer_r,
        "filletApplied": False,
        "filletSkippedReason": "Outer-rim fillet is not yet implemented for a tapered shank (v1 limitation).",
        "variation": "TAPERED",
        "widthTaperMode": width_taper.mode,
        "widthTaperBottomRatio": width_taper.bottomRatio,
        "thicknessTaperMode": thickness_taper.mode,
        "thicknessTaperBottomRatio": thickness_taper.bottomRatio,
        "sectionCount": SECTION_COUNT,
        "widthSamplesMm": {
            "headMm": base_half_width * 2 * taper_ratio(0.0, width_taper),
            "bottomMm": base_half_width * 2 * taper_ratio(0.5, width_taper),
        },
        "thicknessSamplesMm": {
            "headMm": (base_outer_r - inner_r) * taper_ratio(0.0, thickness_taper),
            "bottomMm": (base_outer_r - inner_r) * taper_ratio(0.5, thickness_taper),
        },
        "connectionInterface": {
            "topZMm": interface.topZMm,
            "embedMm": interface.embedMm,
            "headCenterRadiusMm": interface.headCenterRadiusMm,
        },
    }

    return GeneratedComponent(
        name="band",
        shape=solid,
        volume_mm3=solid.Volume(),
        bounding_box=BoundingBox.from_shape(solid),
        warnings=[],
        metadata=metadata,
    )


def build_shank(definition: JewelryDefinition) -> GeneratedComponent:
    """Build the metal ring shank as a single closed solid, named "band"
    (the stable, unchanged component identity — brief section 30).

    Dispatches to the exact pre-Sprint-17 construction when no taper is
    requested, and a new loft-based construction otherwise.
    """

    width_taper = definition.band.widthTaper
    thickness_taper = definition.band.thicknessTaper
    if width_taper.mode == "NONE" and thickness_taper.mode == "NONE":
        return _build_uniform_shank(definition)
    return _build_tapered_shank(definition)
