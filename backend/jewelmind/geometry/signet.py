"""Signet body geometry — a solid mass with a table at the ring's top.

Sprint 28. A signet ring's defining feature is that its top is a solid body
rather than a setting rising above a band, so the body is built as its OWN
component: it has parametric identity, its own provenance and its own
inspection facts, rather than being an unnamed lump fused into the shank.

## What is built

One prism spanning the ring's own circumferential direction (`length`) and
across it (`width`), rising `height` above the band's top ridge and reaching
DOWN into the band so the fuse produces genuine 3D overlap rather than a
tangent touch — the same reasoning `constants.EMBED_MM` documents.

## What is deliberately NOT built

- **No engraving, relief or texture.** A signet's decoration is a cut driven by
  a 2D pattern, and no pattern representation exists anywhere in the pipeline.
  `SIGNET_ENGRAVED` is reserved with that as its recorded reason.
- **No non-rectangular table.** An oval or cushion table's outline would come
  from the same outline machinery the Stone System uses, and giving
  `stone/outline.py` a second caller for a metal table is a real change to that
  module's contract. `SIGNET_OVAL_TABLE` is reserved.
- **No stone-bearing table.** A signet variant that also carried a flush-set
  stone would need the table's own surface as a setting host, which is a pavé/
  setting host resolver rather than a body parameter.

Every dimension arrives as a parameter. No table proportion, minimum wall or
engraving depth is asserted anywhere (ATLAS-GOV-002).
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.connection import shank_connection_interface
from jewelmind.geometry.model import BoundingBox, GeneratedComponent

#: The component every signet body takes.
SIGNET_COMPONENT = "signet_body"

#: How far the body reaches DOWN past the band's top ridge, in millimetres.
#:
#: A GEOMETRIC ROBUSTNESS value in the same class as `constants.EMBED_MM`: a
#: body that merely touched the band's outer surface would leave OCCT two
#: solids instead of one fused body. It is not a seat depth and not a wall
#: thickness.
_BODY_EMBED_MM = 1.0


class SignetConstructionError(Exception):
    """A requested signet body could not be constructed.

    Raised rather than returning nothing, which would report a signet ring and
    deliver a plain band.
    """


def build_signet_body(
    definition: JewelryDefinition,
    table_length_mm: float,
    table_width_mm: float,
    table_height_mm: float,
) -> GeneratedComponent:
    """Build the signet body for one ring family variant.

    `table_length_mm` runs along the ring's own circumferential direction (the
    global X axis at the top of the ring) and `table_width_mm` across it (the
    global Y axis, which is the band's width direction) — the same axis
    convention every other component uses, so a reader never has to work out
    which way round the two are.
    """

    interface = shank_connection_interface(definition)
    base_z = interface.topZMm - _BODY_EMBED_MM
    top_z = interface.topZMm + table_height_mm
    height = top_z - base_z

    if height <= 0:  # pragma: no cover - the schema bounds the height above 0
        raise SignetConstructionError(
            f"The signet body's vertical extent is {height} mm."
        )

    try:
        shape = cq.Solid.makeBox(
            table_length_mm,
            table_width_mm,
            height,
            pnt=cq.Vector(-table_length_mm / 2.0, -table_width_mm / 2.0, base_z),
        )
    except Exception as exc:  # noqa: BLE001 - OCC construction failures vary
        raise SignetConstructionError(
            f"Could not construct the signet body "
            f"(length={table_length_mm}, width={table_width_mm}, "
            f"height={table_height_mm}): {exc}. A real construction failure, "
            "never downgraded to a plain band."
        ) from exc

    if not shape.Solids() or not shape.isValid():
        raise SignetConstructionError(
            "The signet body produced no valid solid."
        )

    metadata = {
        "bodyArchitecture": "SIGNET_TABLE",
        "tableLengthMm": table_length_mm,
        "tableWidthMm": table_width_mm,
        "tableHeightMm": table_height_mm,
        "tableTopZMm": top_z,
        "baseZMm": base_z,
        "embedMm": _BODY_EMBED_MM,
        "solidCount": len(shape.Solids()),
        # Explicit statements of what this body is NOT, carried on the
        # component so a consumer reads them from the geometry rather than from
        # documentation.
        "engraved": False,
        "tableOutline": "RECTANGULAR",
        "carriesStone": False,
    }

    return GeneratedComponent(
        name=SIGNET_COMPONENT,
        shape=shape,
        volume_mm3=shape.Volume(),
        bounding_box=BoundingBox.from_shape(shape),
        warnings=[],
        metadata=metadata,
    )


#: Body architectures with a real builder. `NONE` is deliberately absent rather
#: than mapped to a no-op, for the same reason `SHOULDER_ARCHITECTURES` omits it.
BODY_ARCHITECTURES: tuple[str, ...] = ("SIGNET_TABLE",)
