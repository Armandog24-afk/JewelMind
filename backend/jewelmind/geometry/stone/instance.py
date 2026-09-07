"""Per-instance stone placement (Sprint 24).

THE ONE PIECE SPRINT 22 IDENTIFIED AS MISSING. The Stone System builds a stone
centred on the design axis at a girdle plane; an arrangement resolves each
instance to an explicit position, a scale and a rotation. This module applies
the second to the first, which is what turns a resolved multi-stone arrangement
into real multi-stone geometry.

DELIBERATELY THIN, and deliberately here rather than inside the stone builder.
The builder's job is "what does this stone look like"; placement is "where does
this occurrence sit". Keeping them apart is why the byte-identical single-stone
fast path survives: a lone instance at the origin with no scale and no rotation
takes the identity path and the solid is returned untouched.

ORDER OF OPERATIONS IS FIXED AND MATTERS: scale about the stone's own centre,
then rotate about its own vertical axis, then translate into place. Scaling
after translating would move the stone; rotating after translating would swing
it around the design axis instead of spinning it in place.

KERNEL-ADJACENT BY DESIGN. This is an Atlas-layer module and does touch
CadQuery. It takes an already-resolved instance (plain numbers) and a built
component — it never reads an arrangement, a family, or a jewelry category.
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.geometry.model import BoundingBox, GeneratedComponent

#: Below this, a scale or rotation is treated as absent.
#:
#: Not a tolerance on anything physical: it exists so a resolved value that is
#: 1.0 or 0.0 to within float noise takes the identity path and returns the
#: solid untouched, preserving the single-stone geometry exactly.
_IDENTITY_EPSILON = 1e-12


def _scaled_about_center(shape: cq.Shape, factor: float) -> cq.Shape:
    """Scale a solid about its own bounding-box centre.

    `Shape.scale()` scales about the GLOBAL ORIGIN, which for a stone sitting
    at a girdle plane several millimetres up would also move it vertically —
    a smaller side stone would sink. Translating to the origin, scaling, and
    translating back keeps the stone where it was; the same correction
    `setting/seat.py` applies when it grows a cutting tool.
    """

    box = shape.BoundingBox()
    center = cq.Vector(
        (box.xmin + box.xmax) / 2.0,
        (box.ymin + box.ymax) / 2.0,
        (box.zmin + box.zmax) / 2.0,
    )
    return shape.translate(center * -1.0).scale(factor).translate(center)


def _rotated_about_own_axis(shape: cq.Shape, degrees: float) -> cq.Shape:
    """Rotate a solid about the vertical axis through its own centre.

    Rotating about the DESIGN axis would swing an off-centre stone around the
    ring instead of spinning it in place — which is the difference between a
    side stone turned to follow the band and a side stone that has moved.
    """

    box = shape.BoundingBox()
    cx = (box.xmin + box.xmax) / 2.0
    cy = (box.ymin + box.ymax) / 2.0
    return shape.rotate(
        cq.Vector(cx, cy, 0.0), cq.Vector(cx, cy, 1.0), degrees
    )


def place_stone_instance(
    component: GeneratedComponent,
    component_name: str,
    *,
    x_mm: float,
    y_mm: float,
    z_mm: float,
    rotation_deg: float,
    scale: float | None,
    orientation_deg: float | None,
    instance_id: str,
    role: str,
) -> GeneratedComponent:
    """One stone occurrence, placed.

    Returns a component carrying the instance's own identity in its name and
    metadata, so every downstream consumer — inspection, preview, export,
    Vision — can tell which occurrence a solid is without inferring it from a
    position (INSPECT-GOV-015).

    An instance at the origin with no scale and no rotation returns the input
    shape unchanged, which is what preserves the single-stone geometry
    byte-for-byte.
    """

    shape = component.shape
    applied: list[str] = []

    if scale is not None and abs(scale - 1.0) > _IDENTITY_EPSILON:
        shape = _scaled_about_center(shape, scale)
        applied.append("SCALE")

    # The instance's own `orientationDeg` override and the placement's
    # `rotationDeg` are BOTH spins about the stone's own axis — the first comes
    # from the member, the second from the pattern that placed it (a radial run
    # facing its stones outward). They compose additively, and applying only one
    # would silently drop whichever the caller happened not to set.
    spin = (orientation_deg or 0.0) + (rotation_deg or 0.0)
    if abs(spin) > _IDENTITY_EPSILON:
        shape = _rotated_about_own_axis(shape, spin)
        applied.append("ROTATE")

    if (
        abs(x_mm) > _IDENTITY_EPSILON
        or abs(y_mm) > _IDENTITY_EPSILON
        or abs(z_mm) > _IDENTITY_EPSILON
    ):
        shape = shape.translate(cq.Vector(x_mm, y_mm, z_mm))
        applied.append("TRANSLATE")

    metadata = {
        **component.metadata,
        "stoneInstanceId": instance_id,
        "stoneInstanceRole": role,
        # What was ACTUALLY applied, not what was requested — the same honesty
        # `stone/normalize.py`'s `normalizationOperations` keeps for imports.
        "instanceTransformOperations": applied,
        "instanceTranslationMm": {"x": x_mm, "y": y_mm, "z": z_mm},
        "instanceRotationDeg": spin,
        "instanceScale": scale,
    }

    if not applied:
        # Identity placement: the same shape object, so the single-stone path is
        # provably untouched rather than merely equal.
        return GeneratedComponent(
            name=component_name,
            shape=component.shape,
            volume_mm3=component.volume_mm3,
            bounding_box=component.bounding_box,
            warnings=list(component.warnings),
            metadata=metadata,
        )

    return GeneratedComponent(
        name=component_name,
        shape=shape,
        volume_mm3=shape.Volume(),
        bounding_box=BoundingBox.from_shape(shape),
        warnings=list(component.warnings),
        metadata=metadata,
    )
