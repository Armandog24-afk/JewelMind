"""Shank architectures beyond the closed ring (Sprint 28).

Two real constructions, both reached only by a document that asks for them, so
the uniform fast path stays byte-for-byte unchanged (SHANK-GOV-003). See
[`ADR-014`](../../../../docs/bible/03-decisions/ADR-014-shank-architectures.md)
for why a new architecture needed a decision record at all.

## SPLIT — two rails, joined at the bottom

Two full rings of the band's own profile, offset along the width axis, plus a
BRIDGE over an angular span centred on the bottom that restores the full width
there. So the shank is genuinely two rails at the top and one band at the
bottom, which is what a split shank is.

THE RAILS SHARE THE BAND'S WIDTH. A wider separation makes each rail narrower
rather than making the ring wider, so `band.width` still means the ring's
overall width and a split shank does not silently grow past it.

## BYPASS — one open rail that passes itself

ONE rail lofted over `360 + overlap` degrees, its axial offset running from
`-separation/2` to `+separation/2` as it travels. Over the overlap span its
start and its end occupy the same angle at different axial positions, so they
PASS each other rather than meet.

Deliberately ONE rail and not two arcs, and this is the finding that shaped the
construction: two axially separated arcs come out as TWO DISCONNECTED SOLIDS.
A ring that is not one connected body is not a ring, and fusing them would
have needed a bridge that a bypass does not have.

## Two kernel findings this module is built around

- **`Workplane.translate()` before `.revolve()` does not move the revolved
  solid.** The axial offset was silently lost, and the two split rails came out
  coincident — their "fused" volume was exactly one rail's. Revolve FIRST and
  translate the SOLID after. The same class of mistake Sprint 20 recorded for a
  mesh that `Shape.scale()` did not move, and the reason every offset here is
  applied to a `Shape`.
- **An arc is built by INTERSECTION, not by a partial revolve.** A partial
  `revolve()` swept somewhere other than from the wire's own position; a full
  revolve intersected with a pie sector about the same axis is exact and
  predictable, and it is the machinery Sprint 27 already verified for bezel
  openings.

EVERY CONSTANT HERE IS A CONSTRUCTION PARAMETER. The sector oversize exists so a
boolean is never an exactly tangent cut, and the loft resolution is a
construction resolution. No dimension of a shank is asserted anywhere
(SHANK-GOV-012).
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.constants import inner_radius, outer_radius
from jewelmind.geometry.shank.profile import build_profile
from jewelmind.geometry.shank.taper import angle_deg_for_u, taper_ratio

#: How much larger than the ring a sector-cutting tool is made, as a multiple of
#: the outer radius. Only has to exceed 1; 2 clears the ring for any band
#: thickness without a per-design calculation.
_SECTOR_RADIUS_FACTOR = 2.0

#: How much wider than the band a sector tool is, as a multiple of the band's
#: width. A GEOMETRIC ROBUSTNESS value: a tool exactly as wide as the band would
#: produce coplanar faces at both edges, which is where OCCT is least reliable.
_SECTOR_WIDTH_FACTOR = 4.0

#: Sections lofted per 360 degrees of a bypass rail.
#:
#: Matches `builder.py::SECTION_COUNT`, deliberately: a bypass rail is the same
#: kind of loft the tapered shank already builds, and using the same resolution
#: means the two constructions cannot disagree about how finely a ring is
#: sampled. A bypass travels further than a full turn, so the actual section
#: count is scaled by its own span.
_BYPASS_SECTIONS_PER_TURN = 48

#: Sections lofted per full turn for a TAPERED rail.
#:
#: Matches `builder.py::SECTION_COUNT`, deliberately: a tapered rail is the same
#: kind of loft the tapered shank already builds, and using the same resolution
#: means the two cannot disagree about how finely a ring is sampled.
SECTION_COUNT = 48

#: The smallest rail half-width a split or bypass shank will build.
#:
#: A CONSTRUCTION FLOOR, not a minimum metal section: below it the profile wire
#: degenerates and the revolve produces nothing usable. A configuration that
#: would fall under it is REFUSED (`JM-RINGFAM-004` reports it first), never
#: silently clamped — a rail the author did not describe is worse than an error.
_MIN_RAIL_HALF_WIDTH_MM = 0.05


class ShankArchitectureError(Exception):
    """A requested shank architecture could not be constructed.

    Raised rather than silently falling back to a uniform ring, which would
    report a split or bypass shank and deliver a plain band (SHANK-GOV-007).
    """


def rail_half_width(definition: JewelryDefinition, separation_mm: float) -> float:
    """Half-width of ONE rail when two of them share the band's width.

    `band.width = 2 * rail + separation + 2 * rail`, so each rail is
    `(width - separation) / 4` wide in half-width terms. Stated as a function
    because both architectures and both Forge rules need the same arithmetic,
    and two copies of it is how a rule stops agreeing with the geometry.
    """

    return (definition.band.width - separation_mm) / 4.0


def _revolved_ring(
    definition: JewelryDefinition, half_width: float, y_offset: float
) -> cq.Shape:
    """A closed ring of the band's own profile, at an axial offset.

    REVOLVED FIRST, TRANSLATED AFTER — see the module docstring for the real
    bug this ordering fixes.
    """

    wire = build_profile(
        definition.band.profile,
        inner_radius(definition),
        outer_radius(definition),
        half_width,
    )
    solid = wire.revolve(360, (0, 0, 0), (0, 1, 0)).val()
    return solid.translate((0, y_offset, 0)) if y_offset else solid


def _tapered_ring(
    definition: JewelryDefinition, base_half_width: float, y_offset: float
) -> cq.Shape:
    """A closed ring whose width follows the band's own width taper.

    WHY THIS EXISTS. `SPLIT_SHANK_TAPERED` derives a width taper, and a derived
    value the builder ignored would be the silently ignored field this project
    keeps refusing to add — the defect this function was written to fix, found
    by measuring the two split variants and getting identical volumes.

    Uses `taper_ratio()` — the SAME function the tapered shank and both
    shoulders use — so a rail's narrowing can never disagree with the band's.
    Each section is offset axially BEFORE being rotated into place, for the
    reason `_revolved_ring` documents.
    """

    inner_r = inner_radius(definition)
    outer_r = outer_radius(definition)
    taper = definition.band.widthTaper
    wires: list[cq.Wire] = []
    for index in range(SECTION_COUNT + 1):  # +1 closes the loop
        u = index / SECTION_COUNT
        half = base_half_width * taper_ratio(u, taper)
        wire = build_profile(definition.band.profile, inner_r, outer_r, half).val()
        if y_offset:
            wire = wire.translate((0, y_offset, 0))
        wires.append(wire.rotate((0, 0, 0), (0, 1, 0), angle_deg_for_u(u)))

    try:
        return cq.Solid.makeLoft(wires, ruled=True)
    except Exception as exc:  # noqa: BLE001 - OCC loft failures vary widely
        raise ShankArchitectureError(
            f"Could not loft a tapered rail ({exc}). This is a real "
            "construction failure, never downgraded to an untapered rail."
        ) from exc


def _ring(
    definition: JewelryDefinition, half_width: float, y_offset: float
) -> cq.Shape:
    """A closed ring, tapered when the document asks for one.

    The untapered case keeps the exact revolve: it is cheaper AND exact, where a
    48-section loft only approximates a circle. A split shank with no taper
    therefore has no loft in it at all.
    """

    if definition.band.widthTaper.mode == "NONE":
        return _revolved_ring(definition, half_width, y_offset)
    return _tapered_ring(definition, half_width, y_offset)


def _sector(definition: JewelryDefinition, center_deg: float, span_deg: float) -> cq.Shape:
    """A pie sector about the ring's own axis of revolution.

    `center_deg` is measured the way `angle_deg_for_u` measures: 0 is the TOP of
    the ring, 180 the bottom. Verified empirically — a sector at 0 spans +Z, at
    90 spans +X, at 180 spans -Z.
    """

    radius = outer_radius(definition) * _SECTOR_RADIUS_FACTOR
    width = definition.band.width * _SECTOR_WIDTH_FACTOR
    sector = cq.Solid.makeCylinder(
        radius,
        width,
        pnt=cq.Vector(0, -width / 2.0, 0),
        dir=cq.Vector(0, 1, 0),
        angleDegrees=span_deg,
    )
    return sector.rotate(
        cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), center_deg - span_deg / 2.0
    )


def build_split_shank(definition: JewelryDefinition) -> tuple[cq.Shape, dict]:
    """Two rails joined into one band over the bottom span."""

    separation = definition.band.splitSeparation
    join_span = definition.band.splitJoinSpan
    half = rail_half_width(definition, separation)
    if half < _MIN_RAIL_HALF_WIDTH_MM:
        raise ShankArchitectureError(
            f"A split separation of {separation} mm leaves each rail "
            f"{half * 2:.4f} mm wide in a {definition.band.width} mm band, "
            f"below the {_MIN_RAIL_HALF_WIDTH_MM * 2} mm construction floor. "
            "The rails SHARE the band's width, so a wider separation narrows "
            "them. Refused rather than clamped: a rail you did not describe is "
            "worse than an error."
        )

    offset = separation / 2.0 + half
    rails = _ring(definition, half, +offset).fuse(_ring(definition, half, -offset))

    # THE BRIDGE, over a span centred on the BOTTOM. Cut from a full-width ring
    # rather than built separately, so the bridge's own section is exactly the
    # band's and the two cannot disagree about the profile.
    bridge = _ring(definition, definition.band.width / 2.0, 0.0).intersect(
        _sector(definition, 180.0, join_span)
    )

    try:
        shape = rails.fuse(bridge)
    except Exception as exc:  # noqa: BLE001 - OCC boolean failures vary widely
        raise ShankArchitectureError(
            f"Could not join the split shank's rails to its bridge ({exc}). "
            "This is a real construction failure, never downgraded to a "
            "uniform ring."
        ) from exc

    if not shape.Solids() or not shape.isValid():
        raise ShankArchitectureError(
            "The requested split shank produced no valid solid."
        )
    if len(shape.Solids()) != 1:
        raise ShankArchitectureError(
            f"The split shank produced {len(shape.Solids())} disconnected "
            "solids: the bridge does not reach both rails. A shank that is not "
            "one connected body is not a shank."
        )

    return shape, {
        "variation": "SPLIT",
        "architecture": "SPLIT",
        "railCount": 2,
        "railWidthMm": half * 2,
        "splitSeparationMm": separation,
        "splitJoinSpanDeg": join_span,
        "railAxialOffsetMm": offset,
        # An explicit statement of the property that makes this a split shank,
        # so a consumer never has to infer it from a volume.
        "separatedAtTheHead": True,
        "joinedAtTheBottom": True,
    }


def build_bypass_shank(definition: JewelryDefinition) -> tuple[cq.Shape, dict]:
    """One open rail travelling past a full turn, its ends passing each other."""

    separation = definition.band.bypassSeparation
    overlap = definition.band.bypassOverlap
    half = rail_half_width(definition, separation)
    if half < _MIN_RAIL_HALF_WIDTH_MM:
        raise ShankArchitectureError(
            f"A bypass separation of {separation} mm leaves the rail "
            f"{half * 2:.4f} mm wide in a {definition.band.width} mm band, "
            f"below the {_MIN_RAIL_HALF_WIDTH_MM * 2} mm construction floor."
        )

    total_deg = 360.0 + overlap
    sections = max(8, round(_BYPASS_SECTIONS_PER_TURN * total_deg / 360.0))
    inner_r = inner_radius(definition)
    outer_r = outer_radius(definition)

    wires: list[cq.Wire] = []
    for index in range(sections + 1):
        t = index / sections
        # Starting half the overlap BEFORE the top centres the crossing on it,
        # which is where a bypass ring's setting sits.
        u = -(overlap / 2.0) / 360.0 + t * (total_deg / 360.0)
        y = -separation / 2.0 + t * separation
        # The rail narrows with the band's own width taper, using the SAME
        # `taper_ratio()` every other shank construction uses. `u` is wrapped
        # into [0, 1) first, because a bypass travels past a full turn and the
        # taper is a function of angular distance from the head.
        section_half = half * taper_ratio(u % 1.0, definition.band.widthTaper)
        wire = build_profile(
            definition.band.profile, inner_r, outer_r, section_half
        ).val()
        wires.append(
            wire.translate((0, y, 0)).rotate((0, 0, 0), (0, 1, 0), angle_deg_for_u(u))
        )

    try:
        shape = cq.Solid.makeLoft(wires, ruled=True)
    except Exception as exc:  # noqa: BLE001 - OCC loft failures vary widely
        raise ShankArchitectureError(
            f"Could not construct the requested bypass shank ({exc}). This is a "
            "real construction failure, never downgraded to a uniform ring."
        ) from exc

    if not shape.Solids() or not shape.isValid():
        raise ShankArchitectureError(
            "The requested bypass shank produced no valid solid — the "
            "separation/overlap combination is not constructible with the "
            "current loft-based builder."
        )
    if len(shape.Solids()) != 1:
        raise ShankArchitectureError(
            f"The bypass shank produced {len(shape.Solids())} disconnected "
            "solids. A bypass is ONE open rail that passes itself, not two "
            "arcs."
        )

    return shape, {
        "variation": "BYPASS",
        "architecture": "BYPASS",
        "railCount": 1,
        "railWidthMm": half * 2,
        "bypassSeparationMm": separation,
        "bypassOverlapDeg": overlap,
        "sweptAngleDeg": total_deg,
        "sectionCount": sections,
        # The property that makes this a bypass: the two ends share an angular
        # range and are axially apart there.
        "endsPassRatherThanMeet": True,
    }


#: The architecture registry. A real builder per entry, and `UNIFORM` is
#: deliberately ABSENT rather than mapped: the uniform path is
#: `builder.py::_build_uniform_shank()`, whose byte-identity guarantee is the
#: reason it is not reached through a dispatch that could grow a wrapper.
SHANK_ARCHITECTURE_BUILDERS = {
    "SPLIT": build_split_shank,
    "BYPASS": build_bypass_shank,
}
