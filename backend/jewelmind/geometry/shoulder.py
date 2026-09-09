"""Shoulder geometry — the structural transition from the shank to the head.

Sprint 28. Before this, the shoulder was the one part of `RingDefinition` v2
with no geometry at all: `ring/models.py::ShoulderDefinition` has recorded
`modeled: False` since Sprint 16, because the shank flowed directly into the
head with no distinct transition component. This module gives it real solids
and, with them, a real parametric identity (brief §12: a shoulder must not be
"simply a fused part of the shank with no parametric identity").

## What is built

- **`CATHEDRAL`** — two arches, one on each side of the head, each lofted from
  a section ON the band's own profile at a stated angular distance from the top
  up to a section at the head's own height. They meet at the ring's centre
  plane, which is what makes the pair one continuous arch under the setting and
  guarantees both are connected to the head.
- **`SPLIT_RAILS`** — four arches: one per rail per side. A split shank's rails
  converge on the head, and this is that convergence as real metal rather than
  as an implication.

## Why a loft

The base section IS the band's own profile wire, from the same
`shank/profile.py` builders the shank uses, so a shoulder can never disagree
with the band about its cross-section. A loft between two real sections is the
primitive the tapered shank already uses, verified in this codebase since
Sprint 17.

It also brings the primitive's own limit, which is real and is enforced:
`MAX_ARCH_SPAN_DEG`. Past a quarter turn the two end sections have rotated
past each other and the ruled loft self-intersects — silently, because OCC's
validity check passes the individual solid and only the ring's combined metal
reports invalid. The span is therefore refused before construction.

## Every constant is a construction parameter

The section factors narrow the arch as it rises, which is what distinguishes a
shoulder from a thickened band. No shoulder dimension, proportion or minimum
section is asserted: nothing here says how large a shoulder should be
(SHANK-GOV-012, ATLAS-GOV-002).
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.connection import shank_connection_interface
from jewelmind.geometry.constants import inner_radius, outer_radius
from jewelmind.geometry.model import BoundingBox, GeneratedComponent
from jewelmind.geometry.shank.architecture import rail_half_width
from jewelmind.geometry.shank.profile import build_profile
from jewelmind.geometry.shank.taper import angle_deg_for_u

#: The largest angular span a ruled-loft arch can be built over, in degrees.
#:
#: A CONSTRUCTION LIMIT, MEASURED, not a professional threshold and not a
#: statement about how far down a shoulder should reach. Nothing here says
#: anything about how large a shoulder ought to be (SHANK-GOV-012,
#: ATLAS-GOV-002).
#:
#: WHY EXACTLY 90, and why it is arithmetic rather than a guess. The arch is a
#: ruled loft from the band's own section at `u = span/360` up to a section at
#: the head's height at `u = 0`. Section rotation is
#: `angle_deg_for_u(u) = -90 + u * 360`, so the base section's rotation is
#: `-90 + span`: at `span = 90` it reaches 0 degrees, the same orientation as
#: the head's section, and past that it rotates BEYOND it. A ruled loft between
#: two sections that have crossed each other turns back on itself.
#:
#: FOUND BY MEASURING, and the cliff is sharp: at 90 degrees the fused arches
#: are 84.651 mm³ and the ring's metal is valid; at 92 degrees they collapse to
#: 19.577 mm³ and the ring's combined metal reports `isValid() == False`. The
#: individual arch still reports valid — OCC's own check does not catch the
#: self-intersection — which is why this is a PRECONDITION checked before
#: construction rather than a validity check after it.
MAX_ARCH_SPAN_DEG = 90.0

#: The component every shoulder architecture takes.
#:
#: ONE NAME FOR BOTH ARCHITECTURES, and one component for every arch rather
#: than one per arch — the reason `retention.py` and `bar.py` both document:
#: four individually named arches would give Geometry Inspection an
#: intersection matrix that grows with the arch count, and four entries in
#: every manifest for one structural role. The architecture and the arch count
#: are reported in the metadata instead (INSPECT-GOV-015).
SHOULDER_COMPONENT = "shoulders"


class ShoulderConstructionError(Exception):
    """A requested shoulder could not be constructed.

    Raised rather than returning fewer arches than the architecture describes,
    which would report a cathedral and deliver half of one.
    """


def _band_section(
    definition: JewelryDefinition, u: float, half_width: float, y_offset: float
) -> cq.Wire:
    """The band's OWN profile wire, placed at longitudinal position `u`.

    Built from `shank/profile.py`, so a shoulder's base is exactly the band's
    cross-section there and the two cannot disagree.
    """

    wire = build_profile(
        definition.band.profile,
        inner_radius(definition),
        outer_radius(definition),
        half_width,
    ).val()
    if y_offset:
        wire = wire.translate((0, y_offset, 0))
    return wire.rotate((0, 0, 0), (0, 1, 0), angle_deg_for_u(u))


def _head_section(
    top_z: float, thickness: float, half_width: float, y_offset: float
) -> cq.Wire:
    """A section at the head's own height, oriented like the band's section at
    the top of the ring.

    Drawn with the same local convention every shank profile uses — local x is
    radial, local y is axial — and rotated by `angle_deg_for_u(0)`, which is
    the rotation that puts a radial coordinate onto +Z. Using the same rotation
    as the base section is what keeps the loft's two ends compatible.
    """

    wire = build_profile("flat", top_z - thickness, top_z, half_width).val()
    if y_offset:
        wire = wire.translate((0, y_offset, 0))
    return wire.rotate((0, 0, 0), (0, 1, 0), angle_deg_for_u(0.0))


def _arch(
    definition: JewelryDefinition,
    sign: float,
    span_deg: float,
    head_z: float,
    base_half_width: float,
    top_half_width: float,
    top_thickness: float,
    y_offset: float,
) -> cq.Shape:
    base = _band_section(definition, sign * (span_deg / 360.0), base_half_width, y_offset)
    top = _head_section(head_z, top_thickness, top_half_width, y_offset)
    try:
        return cq.Solid.makeLoft([base, top], ruled=True)
    except Exception as exc:  # noqa: BLE001 - OCC loft failures vary widely
        raise ShoulderConstructionError(
            f"Could not loft a shoulder arch at span {span_deg} degrees "
            f"({exc}). This is a real construction failure, never downgraded to "
            "no shoulder at all."
        ) from exc


def build_shoulders(
    definition: JewelryDefinition,
    architecture: str,
    span_deg: float,
    top_width_factor: float,
    top_thickness_factor: float,
) -> GeneratedComponent:
    """Build the shoulder component for one ring family variant.

    An unregistered architecture is an explicit error, never a substitution: a
    cathedral built for a requested split would report one structure and deliver
    another (SETTING-GOV-013's discipline, restated for ring structure).
    """

    if span_deg > MAX_ARCH_SPAN_DEG:
        # REFUSED, NEVER CLAMPED. Reducing the span to fit would build a
        # shoulder the author never described, and building it anyway would ship
        # a self-intersecting solid that OCC's own validity check passes.
        raise ShoulderConstructionError(
            f"A shoulder span of {span_deg} degrees is past the "
            f"{MAX_ARCH_SPAN_DEG}-degree construction limit of a ruled-loft "
            "arch: the base section's rotation is `-90 + span`, so beyond 90 "
            "degrees it has rotated past the head's own section and the loft "
            "turns back on itself. A construction limit, not a statement about "
            "how far down a shoulder should reach."
        )

    interface = shank_connection_interface(definition)
    # The arches rise to the head's own top — the girdle plane the setting
    # attaches at — so a taller head grows taller arches. That is the parametric
    # relation: `setting.basketHeight` is read, never restated.
    head_z = interface.topZMm + definition.setting.basketHeight

    band_half = definition.band.width / 2.0
    top_half = band_half * top_width_factor
    top_thickness = definition.band.thickness * top_thickness_factor

    if architecture == "CATHEDRAL":
        offsets = ((band_half, 0.0),)
        arch_count = 2
    elif architecture == "SPLIT_RAILS":
        # One arch per rail per side. The rails' own half-width and offset come
        # from the SAME function the split shank builds them with, so the
        # shoulders land exactly on the rails rather than beside them.
        separation = definition.band.splitSeparation
        half = rail_half_width(definition, separation)
        offset = separation / 2.0 + half
        offsets = ((half, +offset), (half, -offset))
        arch_count = 4
    else:
        raise ShoulderConstructionError(
            f"No shoulder builder is registered for architecture "
            f"{architecture!r}. Registered: ['CATHEDRAL', 'SPLIT_RAILS']."
        )

    solids: list[cq.Shape] = []
    for base_half, y_offset in offsets:
        for sign in (1.0, -1.0):
            solids.append(
                _arch(
                    definition,
                    sign,
                    span_deg,
                    head_z,
                    base_half,
                    min(top_half, base_half),
                    top_thickness,
                    y_offset,
                )
            )

    shape = solids[0]
    for solid in solids[1:]:
        try:
            shape = shape.fuse(solid)
        except Exception as exc:  # noqa: BLE001
            raise ShoulderConstructionError(
                f"Could not fuse the shoulder arches ({exc}). Raised rather "
                "than returning a partial set, which would report an "
                "architecture and deliver less of it."
            ) from exc

    if not shape.Solids():
        raise ShoulderConstructionError(
            f"The {architecture} shoulders produced no solid."
        )

    metadata = {
        "shoulderArchitecture": architecture,
        "archCount": arch_count,
        "spanDeg": span_deg,
        "topWidthFactor": top_width_factor,
        "topThicknessFactor": top_thickness_factor,
        "baseZMm": interface.topZMm,
        "headZMm": head_z,
        "riseMm": head_z - interface.topZMm,
        "solidCount": len(shape.Solids()),
        # Stated so a reader never has to infer where the arches came from: the
        # base section IS the band's own profile at that angle.
        "baseSectionSource": "shank_profile",
    }

    return GeneratedComponent(
        name=SHOULDER_COMPONENT,
        shape=shape,
        volume_mm3=shape.Volume(),
        bounding_box=BoundingBox.from_shape(shape),
        warnings=[],
        metadata=metadata,
    )


#: The shoulder architectures with a real builder. `NONE` is deliberately
#: absent rather than mapped to a no-op: a variant asking for no shoulder should
#: not reach a builder at all, and an entry here would make "no shoulder" look
#: like a kind of shoulder.
SHOULDER_ARCHITECTURES: tuple[str, ...] = ("CATHEDRAL", "SPLIT_RAILS")
