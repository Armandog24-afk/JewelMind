"""Repeated small-stone retention metal (Sprint 26).

WHY THIS LIVES IN THE SETTING SYSTEM. Setting System v2 is authoritative for
how metal holds a stone, and a bead is metal holding a stone. Putting the bead
builder inside `jewelmind/pave/` would create a second retention
implementation, which is exactly what the brief forbids — and it would put
kernel code inside a domain package that is asserted to contain none.

WHAT THE SPLIT IS. The pavé layer owns WHERE retention goes: it owns the
lattice, so it knows where four cells meet. This module owns WHAT a piece of
retention IS and builds the solid. The pavé passes explicit points and surface
normals; this module never reads a pavé, an arrangement or a jewelry category.

A REGISTRY, NOT A BRANCH CHAIN, for the reason `dispatch.py` and `head.py` are
registries: a strategy with no builder must be unreachable rather than silently
substituted, and a reserved strategy must be refused rather than approximated
with the nearest solid that happens to exist (SETTING-GOV-013).

NO INVENTED PROFESSIONAL THRESHOLD. Every radius, height and embed depth here
arrives as a parameter. The one constant is the minimum solid count check,
which is a construction correctness check rather than a dimension.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from functools import lru_cache

import cadquery as cq
from pydantic import ConfigDict, Field

from jewelmind.geometry.model import BoundingBox, GeneratedComponent
from jewelmind.setting.errors import SettingGenerationFailedError
from jewelmind.setting.models import SettingModel

#: The component name every retention field takes.
#:
#: ONE NAME FOR THE WHOLE FIELD, not one per bead, and that is a deliberate
#: decision rather than a shortcut. Sixty individually named beads would give
#: Geometry Inspection sixty components to pair off against every other
#: component — an O(n²) intersection matrix that grows with the stone count —
#: and would give every preview manifest and export list sixty entries for one
#: structural role. The field is one component whose metadata carries every
#: anchor's own id and the stones it serves, so identity is preserved without
#: inflating the component set (INSPECT-GOV-015).
PAVE_RETENTION_COMPONENT = "pave_retention"


class RetentionAnchorFrame(SettingModel):
    """One point where a piece of retention metal goes, and how it stands.

    Plain numbers, deliberately: this contract must stay kernel-neutral so the
    pavé layer can produce it without importing CadQuery.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    anchorId: str = Field(max_length=200)
    xMm: float = Field(allow_inf_nan=False)
    yMm: float = Field(allow_inf_nan=False)
    zMm: float = Field(allow_inf_nan=False)

    #: The surface normal at this point, in the same tilt/azimuth
    #: parameterization the arrangement uses for a stone's axis, so a prong
    #: stands normal to a curved surface rather than vertically through it.
    tiltDeg: float = Field(default=0.0, allow_inf_nan=False)
    tiltAzimuthDeg: float = Field(default=0.0, allow_inf_nan=False)

    #: The stone instances this piece touches. Carried into the component
    #: metadata so a shared bead's topology is inspectable.
    servesPlacementIds: list[str] = Field(default_factory=list)


class RetentionBuildSpec(SettingModel):
    """The construction parameters for one retention field."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    strategy: str = Field(max_length=40)

    #: Radius of a bead, or of a micro-prong's shaft.
    radiusMm: float = Field(gt=0.0, le=5.0, allow_inf_nan=False)

    #: How far a piece's base sits below the host surface, so the fuse into the
    #: host produces genuine 3D overlap rather than a tangent touch OCCT would
    #: leave as two solids. A GEOMETRIC ROBUSTNESS value, the same reasoning as
    #: `constants.EMBED_MM`.
    embedMm: float = Field(ge=0.0, le=5.0, allow_inf_nan=False)

    #: Height of a micro-prong above the surface. Ignored by the bead builders.
    prongHeightMm: float = Field(default=0.35, gt=0.0, le=10.0, allow_inf_nan=False)


def _normal_vector(frame: RetentionAnchorFrame) -> cq.Vector:
    """The outward unit normal at an anchor."""

    tilt = math.radians(frame.tiltDeg)
    azimuth = math.radians(frame.tiltAzimuthDeg)
    return cq.Vector(
        math.sin(tilt) * math.cos(azimuth),
        math.sin(tilt) * math.sin(azimuth),
        math.cos(tilt),
    )


def _bead_solid(frame: RetentionAnchorFrame, spec: RetentionBuildSpec) -> cq.Shape:
    """One bead: a sphere centred `embedMm` below the surface.

    A SPHERE, and named honestly as one. A real bead is metal raised with a
    graining tool and its shape depends on the tool and the hand; this is a
    deterministic CAD reference solid that occupies the place a bead occupies.
    Nothing here claims it reproduces a bench-raised grain.
    """

    normal = _normal_vector(frame)
    center = cq.Vector(frame.xMm, frame.yMm, frame.zMm) - normal * spec.embedMm
    return cq.Solid.makeSphere(spec.radiusMm, center, angleDegrees1=-90.0)


def _micro_prong_solid(
    frame: RetentionAnchorFrame, spec: RetentionBuildSpec
) -> cq.Shape:
    """One micro-prong: a cylinder standing along the surface normal.

    Started `embedMm` below the surface so it genuinely intersects the host,
    and capped with a hemisphere so the tip is not a sharp annulus — the same
    shape a set prong tip approximates, built as a real solid rather than
    implied.
    """

    normal = _normal_vector(frame)
    base = cq.Vector(frame.xMm, frame.yMm, frame.zMm) - normal * spec.embedMm
    height = spec.prongHeightMm + spec.embedMm
    shaft = cq.Solid.makeCylinder(spec.radiusMm, height, base, normal)
    tip = cq.Solid.makeSphere(
        spec.radiusMm, base + normal * height, angleDegrees1=-90.0
    )
    return shaft.fuse(tip)


RetentionBuilder = Callable[[RetentionAnchorFrame, RetentionBuildSpec], cq.Shape]


@lru_cache(maxsize=1)
def retention_builders() -> dict[str, RetentionBuilder]:
    """The retention registry. Every entry builds a real solid.

    `NONE` is deliberately absent rather than mapped to a no-op: a caller
    asking for no retention should not reach a builder at all, and an entry
    here would make "no metal" look like a kind of metal.
    """

    return {
        "BEAD": _bead_solid,
        "SHARED_BEAD": _bead_solid,
        "MICRO_PRONG": _micro_prong_solid,
    }


def build_pave_retention(
    frames: Sequence[RetentionAnchorFrame], spec: RetentionBuildSpec
) -> GeneratedComponent | None:
    """One component carrying every piece of retention metal for a field.

    Returns `None` for an empty field or an unbuilt strategy — never an empty
    component, which would be a production component with no geometry claiming
    to hold stones.

    RAISES on a real construction failure rather than returning fewer pieces
    than requested: reporting a shared-bead field while delivering half its
    beads would be the silent substitution SETTING-GOV-013 forbids.
    """

    builder = retention_builders().get(spec.strategy)
    if builder is None or not frames:
        return None

    solids: list[cq.Shape] = []
    for frame in frames:
        try:
            solid = builder(frame, spec)
        except Exception as exc:  # noqa: BLE001 - OCC failures vary widely
            raise SettingGenerationFailedError(
                f"Retention piece {frame.anchorId!r} could not be built: {exc}. "
                "Raised rather than returning a field with a missing piece, "
                "which would report retention that is not there."
            ) from exc
        if not solid.Solids():
            raise SettingGenerationFailedError(
                f"Retention piece {frame.anchorId!r} produced no solid."
            )
        solids.append(solid)

    fused = solids[0]
    for solid in solids[1:]:
        fused = fused.fuse(solid)

    if not fused.Solids():  # pragma: no cover - defensive
        raise SettingGenerationFailedError(
            "The retention field fused to no solids."
        )

    # A field of separate beads is legitimately MANY solids until it is fused
    # into the host; recording the count makes that a reported fact rather than
    # a surprise for Geometry Inspection.
    return GeneratedComponent(
        name=PAVE_RETENTION_COMPONENT,
        shape=fused,
        volume_mm3=fused.Volume(),
        bounding_box=BoundingBox.from_shape(fused),
        warnings=[],
        metadata={
            "retentionStrategy": spec.strategy,
            "retentionPieceCount": len(frames),
            "retentionSolidCount": len(fused.Solids()),
            "retentionRadiusMm": spec.radiusMm,
            "retentionEmbedMm": spec.embedMm,
            # Every piece's own identity and what it serves, so a shared bead's
            # topology is inspectable without re-deriving the lattice.
            "retentionAnchors": [
                {
                    "anchorId": frame.anchorId,
                    "servesPlacementIds": list(frame.servesPlacementIds),
                }
                for frame in frames
            ],
            # An explicit, checkable statement of the operation performed.
            "retentionOperation": "FUSED_INTO_PRODUCTION_METAL",
        },
    )
