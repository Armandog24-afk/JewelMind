"""Stone -> Setting interface (brief section 20).

Builds the kernel-neutral `StoneSettingReference` a Setting is allowed to
consume, from a real generated stone component plus its `StoneSpec`. This
is the ONLY place Setting reads stone facts, which is what keeps
SETTING-GOV-003 enforceable: a Setting consumes these facts and never
redefines stone geometry.

Depends on the Stone System's public contracts (`domain/stone_dimensions.py`,
`geometry/stone/outline.py`) — never on Stone builder internals, and never
on `jewelmind.ring`.
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.domain.schema import StoneSpec
from jewelmind.domain.stone_dimensions import (
    resolved_depth_mm,
    resolved_length_mm,
    resolved_width_mm,
)
from jewelmind.geometry.model import GeneratedComponent
from jewelmind.geometry.stone import outline as stone_outline
from jewelmind.setting.errors import StoneOutlineUnavailableError
from jewelmind.setting.models import StoneSettingReference

#: Shapes with a distinguished tip, and the local-Y direction it points at
#: `orientation = 0`. Sourced from the real outline construction in
#: `geometry/stone/outline.py` (pear starts at `(0, +half_length)`).
_TIP_DIRECTION_Y: dict[str, float] = {"pear": +1.0}

#: Exact outline builders for every native cut, keyed by canonical shape.
#:
#: DERIVED from the Stone System's own registry rather than hand-listed, because
#: a second hand-maintained copy drifts: this table held only six shapes when
#: Stone v2 added fourteen, and a bezel over an `asscher` failed with "no
#: registered outline builder" even though the Stone System could build it.
#:
#: `round` is adapted because `round_outline` takes a radius rather than a
#: half-length/half-width pair; the tapered shapes are adapted because they need
#: the narrow width as a fourth argument.
def _native_outline_builders() -> dict:
    from jewelmind.stone.normalize import NATIVE_OUTLINE_BUILDERS

    builders: dict = dict(NATIVE_OUTLINE_BUILDERS)
    builders["round"] = lambda half_length, half_width, scale: stone_outline.round_outline(
        half_width, scale
    )
    return builders


_OUTLINE_BUILDERS = _native_outline_builders()

#: Shapes whose exact builder needs a narrow width the reference must carry.
_TAPERED_SHAPES: frozenset[str] = frozenset({"tapered_baguette", "trapezoid"})


def build_stone_setting_reference(
    stone: StoneSpec,
    component: GeneratedComponent,
    stone_id: str = "stone_reference",
) -> StoneSettingReference:
    """Extract the Setting-consumable facts from a real generated stone.

    DIMENSIONS COME FROM THE BUILT COMPONENT, NOT FROM THE REQUEST. Every stone
    builder records the dimensions it actually built into `component.metadata`,
    and reading those means the Setting System describes the stone that exists
    rather than the one that was asked for. It is also what lets a custom,
    measured or imported stone work here at all: those have no named-cut
    `length`/`width` fields to resolve, and the previous implementation raised a
    bare `AssertionError` deep inside `resolved_length_mm()` when handed one.

    The pre-Sprint-20 `resolved_*_mm()` helpers remain the fallback for any
    component whose metadata predates this contract, so nothing regresses.
    """

    bb = component.bounding_box
    metadata = component.metadata
    girdle_z = float(metadata["girdleZMm"])
    shape = str(metadata.get("shape", stone.shape))

    length = float(metadata["lengthMm"]) if "lengthMm" in metadata else resolved_length_mm(stone)
    width = float(metadata["widthMm"]) if "widthMm" in metadata else resolved_width_mm(stone)
    depth = float(metadata["depthMm"]) if "depthMm" in metadata else resolved_depth_mm(stone)

    outline_points: list[tuple[float, float]] | None = None
    anchors = metadata.get("outlinePointsMm")
    if anchors:
        outline_points = [(float(x), float(y)) for x, y in anchors]

    return StoneSettingReference(
        stoneId=stone_id,
        shape=shape,
        lengthMm=length,
        widthMm=width,
        depthMm=depth,
        orientationDeg=float(metadata.get("orientationDeg", stone.orientation)),
        girdlePlaneZMm=girdle_z,
        centerXMm=(bb.xmin + bb.xmax) / 2,
        centerYMm=(bb.ymin + bb.ymax) / 2,
        boundingBoxMinMm=(bb.xmin, bb.ymin, bb.zmin),
        boundingBoxMaxMm=(bb.xmax, bb.ymax, bb.zmax),
        isBilaterallySymmetric=_symmetry_class(metadata) == "BILATERAL_BOTH_AXES",
        isRadiallySymmetric=_symmetry_class(metadata) == "RADIAL",
        tipDirectionY=_TIP_DIRECTION_Y.get(shape),
        narrowWidthMm=(
            float(metadata["narrowWidthMm"])
            if metadata.get("narrowWidthMm") is not None
            else None
        ),
        outlinePoints=outline_points,
    )


def _symmetry_class(metadata: dict) -> str:
    """The stone's symmetry class, as the Stone System computed it.

    Every builder — including the byte-identical round fast path — records this,
    so there is no name-keyed fallback: a component that somehow lacks it is
    treated as UNKNOWN, which is the SAFE direction. Assuming symmetry a stone
    does not have mirrors prongs onto places the stone never reaches, whereas
    assuming less symmetry than it has only costs the outline-aware strategy.
    """

    return str(metadata.get("symmetry", "UNKNOWN"))


def girdle_outline_wire(reference: StoneSettingReference) -> cq.Wire:
    """The stone's own girdle outline, as a closed planar wire at Z=0.

    This is the authoritative bezel path (brief section 17) and the source
    of cardinal anchors for shape-aware prong placement. It calls the real
    Stone System outline primitives rather than re-deriving a silhouette,
    so a future custom outline flows through the same pipeline
    (brief section 19).

    The wire is returned in the stone's own unrotated local frame; callers
    apply `orientationDeg` themselves so a rotated stone and its setting
    rotate together.

    RESOLUTION ORDER MATTERS, AND THE EXACT BUILDER COMES FIRST.

    A native cut's real outline is an analytic curve — an ellipse for the oval,
    arcs for the cushion. The sampled `outlinePoints` the Stone System carries
    are a faithful but DISCRETE approximation of that curve, so building a bezel
    from them would silently replace a true elliptical offset with a 48-gon one.
    That was measured during Sprint 20: preferring the points made the oval
    bezel stop needing its documented STEP-safety repair (because a polyline has
    no ELLIPSE edge to offset into an OFFSET curve) and moved the oval's
    OUTLINE_CARDINAL prong by 6.3e-5 mm. Both are small; both are geometry
    changes nobody asked for.

    The carried points are therefore the path for a stone that has no analytic
    outline to rebuild — custom, imported, or measured-with-outline — which is
    exactly the case they were added for.
    """

    builder = _OUTLINE_BUILDERS.get(reference.shape)
    if builder is not None:
        half_length, half_width = reference.lengthMm / 2, reference.widthMm / 2
        if reference.shape in _TAPERED_SHAPES:
            if reference.narrowWidthMm is None:
                raise StoneOutlineUnavailableError(
                    f"Stone shape {reference.shape!r} is tapered but carries no "
                    "narrow width, so its outline cannot be rebuilt exactly."
                )
            return builder(half_length, half_width, 1.0, reference.narrowWidthMm / 2)
        return builder(half_length, half_width, 1.0)

    if reference.outlinePoints:
        return stone_outline.custom_outline(list(reference.outlinePoints), 1.0)

    raise StoneOutlineUnavailableError(
        f"Stone shape {reference.shape!r} has no registered outline builder and "
        "carries no outline points, so no setting path can be derived from it. "
        "This is reported rather than approximated with a circle."
    )
