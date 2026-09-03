"""Head geometry: the structure between the attachment plane and the stone.

Sprint 23. Before this, there was exactly one head — a hollow cylindrical wall
built ring-side in `geometry/components/basket.py` from `basketHeight` and the
shank connection interface. That worked, and it was category-specific: a
pendant or earring reaching the same structure would have had to reimplement
it.

This module makes the head a CATEGORY-NEUTRAL Setting concern, driven by
`HeadSettingDefinition` plus the generic attachment interface. It never learns
what a band is (SETTING-GOV-001/014).

THE BASKET IS PRESERVED BYTE-IDENTICALLY. `_basket()` reproduces the
pre-Sprint-23 construction exactly — same `Workplane`/`circle`/`extrude`/`cut`
sequence, same `_MIN_INNER_RADIUS_MM` floor, same metadata keys. The component
is still named `basket_support`. That is what keeps all 39 Golden baselines,
every preview manifest, every export component list and the whole inspection
required-component set unchanged. `geometry/components/basket.py` is now a thin
re-export, the same pattern band, stone and prongs already follow.

A REGISTRY, not a branch. `TRELLIS` is deliberately absent: it needs swept
curved rails the current pipeline cannot build robustly, and a "simplified
trellis" that was really four bent prongs would be a different structure
wearing the name. See `capability.py::RESERVED_HEAD_ARCHITECTURES`.

EVERY CONSTANT IS A CONSTRUCTION PARAMETER, not a jewelry threshold: the inner
radius floor exists so a cut cannot degenerate, and the taper ratios produce
robust solids of revolution (SETTING-GOV-010).
"""

from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache

import cadquery as cq

from jewelmind.geometry.model import BoundingBox, GeneratedComponent
from jewelmind.setting.errors import SettingGenerationFailedError
from jewelmind.setting.models import (
    HeadArchitecture,
    HeadSettingDefinition,
    SettingAttachmentInterface,
)

#: The component name a head takes, unchanged from every previous sprint.
#:
#: STILL `basket_support` EVEN FOR A MARTINI OR TULIP, and that is a deliberate
#: compatibility decision rather than sloppy naming. The name is a structural
#: role — "the support between the attachment plane and the stone" — and it is
#: wired into `geometry/roles.py`, the inspection required-component set, every
#: preview manifest, every export list and all 39 Golden baselines. Renaming it
#: per architecture would break all of those to express something the
#: `headArchitecture` field already reports.
HEAD_COMPONENT = "basket_support"

#: Floor on a head wall's inner radius. Inherited unchanged from the
#: pre-Sprint-23 basket so its geometry is preserved exactly; it exists because
#: a zero-radius inner cut degenerates.
_MIN_INNER_RADIUS_MM = 0.2

HeadBuilder = Callable[
    [HeadSettingDefinition, SettingAttachmentInterface], tuple[cq.Shape, dict]
]


def _resolved_inner_radius(head: HeadSettingDefinition) -> float:
    """The wall's inner radius: stated exactly, or derived from the thickness.

    See `HeadSettingDefinition.innerRadiusMm` for why an explicit value exists
    at all — it preserves the pre-Sprint-23 basket bore bit-for-bit rather than
    re-associating the same arithmetic.
    """

    if head.innerRadiusMm is not None:
        return head.innerRadiusMm
    return head.outerRadiusMm - head.wallThicknessMm


def _basket(
    head: HeadSettingDefinition, attachment: SettingAttachmentInterface
) -> tuple[cq.Shape, dict]:
    """The pre-Sprint-23 hollow cylindrical wall, unchanged.

    Kept character-for-character equivalent to
    `geometry/components/basket.py::build_basket_support()` as it stood before
    this sprint, including the outer-minus-inner `cut()` (rather than a single
    hollow revolve) and the metadata key names, so a default design's
    `basket_support` solid and metadata are identical.
    """

    outer_r = head.outerRadiusMm
    inner_r = max(_resolved_inner_radius(head), _MIN_INNER_RADIUS_MM)
    base_z = attachment.attachmentPlaneZMm - attachment.embedMm
    height = head.heightMm + attachment.embedMm

    outer = cq.Workplane("XY").workplane(offset=base_z).circle(outer_r).extrude(height)
    inner = cq.Workplane("XY").workplane(offset=base_z).circle(inner_r).extrude(height)
    shape = outer.cut(inner).val()

    return shape, {
        "outerRadiusMm": outer_r,
        "innerRadiusMm": inner_r,
        "baseZMm": base_z,
        "heightMm": height,
    }


def _conical_wall(
    outer_top_r: float,
    outer_base_r: float,
    wall: float,
    base_z: float,
    height: float,
) -> cq.Shape:
    """A hollow conical wall: an outer frustum minus an inner frustum.

    Shared by `MARTINI` and `TULIP`, which differ only in which end is wider
    and in how the inner surface is offset. Built from `makeCone` primitives
    rather than lofted sections for the reason Sprint 20 documented: a
    two-section loft over a large radius ratio can overshoot its own bounding
    box, while a cone frustum is exact.
    """

    outer = cq.Solid.makeCone(
        outer_base_r, outer_top_r, height, pnt=cq.Vector(0, 0, base_z)
    )
    inner = cq.Solid.makeCone(
        max(outer_base_r - wall, _MIN_INNER_RADIUS_MM),
        max(outer_top_r - wall, _MIN_INNER_RADIUS_MM),
        # Extended past both ends so the cut is a clean through-bore rather
        # than leaving a floor or a lid, which a same-height tool would.
        height + 2.0,
        pnt=cq.Vector(0, 0, base_z - 1.0),
    )
    try:
        return outer.cut(inner)
    except Exception as exc:  # noqa: BLE001 - OCC boolean failures vary widely
        raise SettingGenerationFailedError(
            f"Head wall construction failed while hollowing the cone: {exc}. "
            "Raised rather than returning the solid cone, which would report a "
            "hollow head and build a filled one."
        ) from exc


def _martini(
    head: HeadSettingDefinition, attachment: SettingAttachmentInterface
) -> tuple[cq.Shape, dict]:
    """A conical wall, wide at the girdle and narrow at the base."""

    outer_top_r = head.outerRadiusMm
    outer_base_r = max(
        head.outerRadiusMm * head.baseRadiusRatio,
        head.wallThicknessMm + _MIN_INNER_RADIUS_MM,
    )
    base_z = attachment.attachmentPlaneZMm - attachment.embedMm
    height = head.heightMm + attachment.embedMm

    shape = _conical_wall(
        outer_top_r, outer_base_r, head.wallThicknessMm, base_z, height
    )
    return shape, {
        "outerRadiusMm": outer_top_r,
        "baseRadiusMm": outer_base_r,
        "wallThicknessMm": head.wallThicknessMm,
        "baseZMm": base_z,
        "heightMm": height,
    }


def _tulip(
    head: HeadSettingDefinition, attachment: SettingAttachmentInterface
) -> tuple[cq.Shape, dict]:
    """A flared wall built as stacked frusta, opening toward the girdle.

    A tulip's silhouette is CONCAVE, not straight — that is what distinguishes
    it from a martini. Approximated by stacking `_TULIP_SECTIONS` frusta whose
    radii follow a quadratic, which keeps every piece an exact cone primitive
    instead of relying on a swept spline the kernel may or may not hollow
    cleanly.

    The section count and the quadratic are SOFTWARE REFERENCE CONSTRUCTION
    choices. This is a tulip-STYLE reference silhouette; no commercial tulip
    head proportion is claimed.
    """

    base_z = attachment.attachmentPlaneZMm - attachment.embedMm
    height = head.heightMm + attachment.embedMm
    outer_top_r = head.outerRadiusMm
    outer_base_r = max(
        head.outerRadiusMm * head.baseRadiusRatio,
        head.wallThicknessMm + _MIN_INNER_RADIUS_MM,
    )

    sections = _TULIP_SECTIONS
    step = height / sections
    pieces: list[cq.Shape] = []
    for index in range(sections):
        t0 = index / sections
        t1 = (index + 1) / sections
        # Quadratic in t: slow near the base, opening faster toward the girdle.
        r0 = outer_base_r + (outer_top_r - outer_base_r) * (t0**2)
        r1 = outer_base_r + (outer_top_r - outer_base_r) * (t1**2)
        pieces.append(
            _conical_wall(r1, r0, head.wallThicknessMm, base_z + index * step, step)
        )

    try:
        shape = pieces[0]
        for piece in pieces[1:]:
            shape = shape.fuse(piece)
    except Exception as exc:  # noqa: BLE001
        raise SettingGenerationFailedError(
            f"Tulip head construction failed while fusing its sections: {exc}. "
            "Raised rather than returning a partial stack, which would be a "
            "shorter head than the one requested."
        ) from exc

    return shape, {
        "outerRadiusMm": outer_top_r,
        "baseRadiusMm": outer_base_r,
        "wallThicknessMm": head.wallThicknessMm,
        "baseZMm": base_z,
        "heightMm": height,
        "sectionCount": sections,
        "profile": "QUADRATIC_FLARE",
    }


#: Frusta stacked to approximate the tulip's concave flare. A construction
#: resolution: more sections mean a smoother silhouette and more boolean work.
_TULIP_SECTIONS = 6

#: How much of a peg head's wall height the connecting flare occupies. A
#: construction parameter: large enough that the flare genuinely intersects the
#: wall's material rather than touching it tangentially, which is where OCCT
#: booleans are least reliable.
_PEG_FLARE_FRACTION = 0.45


def _peg_head(
    head: HeadSettingDefinition, attachment: SettingAttachmentInterface
) -> tuple[cq.Shape, dict]:
    """A basket wall on a narrower solid peg.

    The peg occupies the LOWER portion of the head's height and the basket the
    remainder, so the total height still matches the attachment interface's
    `supportHeightMm`. Growing the head instead would silently lift the stone
    above where the category integration placed it.
    """

    peg_diameter = head.pegDiameterMm
    peg_height = head.pegHeightMm
    if peg_diameter is None or peg_height is None:
        raise SettingGenerationFailedError(
            "A PEG_HEAD requires both pegDiameterMm and pegHeightMm. Raised "
            "rather than defaulting them, because an invented peg size would be "
            "a construction choice the caller never made."
        )
    if peg_height >= head.heightMm:
        raise SettingGenerationFailedError(
            f"PEG_HEAD peg height {peg_height} mm must be less than the head "
            f"height {head.heightMm} mm; otherwise no basket wall remains."
        )

    base_z = attachment.attachmentPlaneZMm - attachment.embedMm
    peg_total = peg_height + attachment.embedMm
    peg_r = peg_diameter / 2.0
    peg = cq.Solid.makeCylinder(peg_r, peg_total, pnt=cq.Vector(0, 0, base_z))

    wall_base_z = base_z + peg_total
    wall_height = head.heightMm - peg_height
    outer_r = head.outerRadiusMm
    inner_r = max(_resolved_inner_radius(head), _MIN_INNER_RADIUS_MM)
    outer = (
        cq.Workplane("XY").workplane(offset=wall_base_z).circle(outer_r).extrude(wall_height)
    )
    inner = (
        cq.Workplane("XY").workplane(offset=wall_base_z).circle(inner_r).extrude(wall_height)
    )
    wall = outer.cut(inner).val()

    # A FLARE, not a butt joint. A peg narrower than the wall's inner bore never
    # touches the wall: stacking them produced two disconnected solids, which
    # would have shipped as a floating basket above an unattached peg. The flare
    # is a cone from the peg's radius out to the wall's OUTER radius, occupying
    # the lowest `_PEG_FLARE_FRACTION` of the wall's height, so it genuinely
    # intersects the wall's material and the fuse yields one solid.
    flare_height = wall_height * _PEG_FLARE_FRACTION
    flare = cq.Solid.makeCone(
        peg_r, outer_r, flare_height, pnt=cq.Vector(0, 0, wall_base_z)
    )

    try:
        shape = wall.fuse(peg).fuse(flare)
    except Exception as exc:  # noqa: BLE001
        raise SettingGenerationFailedError(
            f"PEG_HEAD construction failed while fusing peg, flare and wall: "
            f"{exc}. Raised rather than returning the wall alone, which would "
            "leave the head unsupported."
        ) from exc

    if len(shape.Solids()) != 1:
        raise SettingGenerationFailedError(
            f"PEG_HEAD produced {len(shape.Solids())} disconnected solids; the "
            "peg does not reach the head wall. A head that is not one connected "
            "body is not a head."
        )

    return shape, {
        "outerRadiusMm": outer_r,
        "innerRadiusMm": inner_r,
        "baseZMm": base_z,
        "heightMm": head.heightMm + attachment.embedMm,
        "pegDiameterMm": peg_diameter,
        "pegHeightMm": peg_height,
        "flareHeightMm": flare_height,
    }


@lru_cache(maxsize=1)
def head_builders() -> dict[str, HeadBuilder]:
    """The architecture registry. Every entry builds a real solid."""

    return {
        "BASKET": _basket,
        "PEG_HEAD": _peg_head,
        "MARTINI": _martini,
        "TULIP": _tulip,
    }


def build_head(
    head: HeadSettingDefinition, attachment: SettingAttachmentInterface
) -> GeneratedComponent:
    """Build the head component for one setting.

    An unregistered architecture is an explicit error, never a substitution: a
    basket built for a requested martini would report one structure and deliver
    another (SETTING-GOV-013).
    """

    builder = head_builders().get(head.architecture)
    if builder is None:
        raise SettingGenerationFailedError(
            f"No head builder is registered for architecture "
            f"{head.architecture!r}. Registered: {sorted(head_builders())}."
        )

    shape, metadata = builder(head, attachment)
    if not shape.Solids():
        raise SettingGenerationFailedError(
            f"Head architecture {head.architecture!r} produced no solid."
        )

    metadata = {
        **metadata,
        "headArchitecture": head.architecture,
        # A fact about what was built, so a consumer never has to infer the
        # architecture from a volume or a bounding box.
        "solidCount": len(shape.Solids()),
    }

    return GeneratedComponent(
        name=HEAD_COMPONENT,
        shape=shape,
        volume_mm3=shape.Volume(),
        bounding_box=BoundingBox.from_shape(shape),
        warnings=[],
        metadata=metadata,
    )


def head_architectures() -> tuple[HeadArchitecture, ...]:
    """Architectures with a real builder. Derived, never restated."""

    return tuple(sorted(head_builders()))  # type: ignore[return-value]
