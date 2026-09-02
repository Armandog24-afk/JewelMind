"""The Stone System builder (brief sections 21-24) — dispatches between
two real, deterministic construction paths:

- **round**: the exact pre-Sprint-18 lofted culet/girdle/table
  construction, byte-for-byte unchanged (STONE-GOV-016). This guarantees
  zero Golden regression for every existing round case.
- **every other shape** (oval/pear/emerald/cushion/princess/marquise): a
  new, real 3-level loft (culet → girdle → table) built from the shared
  outline primitives in `outline.py`, using the SAME crown/pavilion/table
  ratios as round for a visually consistent reference silhouette.

Both paths produce a `StoneReference` — a deterministic CAD reference
solid, never a claim of gemological or optical accuracy (STONE-GOV-011).
"""

from __future__ import annotations

from collections.abc import Callable

import cadquery as cq

from jewelmind.domain.schema import JewelryDefinition, StoneSpec
from jewelmind.domain.stone_dimensions import (
    resolved_depth_mm,
    resolved_length_mm,
    resolved_width_mm,
)
from jewelmind.geometry.constants import band_top_z
from jewelmind.geometry.model import BoundingBox, GeneratedComponent
from jewelmind.geometry.stone import outline as O
from jewelmind.geometry.stone.errors import StoneGenerationError, StoneShapeUnsupportedError

# Shared reference proportions (STONE-GOV-011: a documented software
# reference construction, never a sourced gemological standard) — the
# non-round shapes reuse the exact same ratios round already used, for a
# visually consistent crown/pavilion silhouette across every shape.
_CROWN_FRACTION = 0.35
_PAVILION_FRACTION = 0.65
_TABLE_TO_GIRDLE_RATIO = 0.56
_CULET_RADIUS_MM = 0.05  # round only, unchanged pre-Sprint-18 constant
_CULET_SCALE_RATIO = 0.05  # non-round shapes: a proportional, self-similar culet


def _round_anchors(points: list[tuple[float, float]]):
    """Cardinal anchors for the round fast path.

    Imported lazily so the byte-identical round path keeps its minimal import
    graph, and so `geometry/stone/builder.py` does not import the Stone System
    core at module level (`domain/schema.py` already imports
    `jewelmind.stone.models`, and eager imports here would tighten that loop).
    """

    from jewelmind.stone.anchors import derive_anchors
    from jewelmind.stone.models import OutlinePoint

    return derive_anchors("round", [OutlinePoint(x=x, y=y) for x, y in points])


def _build_round_stone(definition: JewelryDefinition) -> GeneratedComponent:
    """The exact pre-Sprint-18 construction — see git history for
    `geometry/components/stone.py` before this Sprint. Never changed by
    this Sprint's shape work; this is what guarantees zero Golden
    regression for round (STONE-GOV-016)."""

    girdle_r = definition.stone.diameter / 2
    crown_h = definition.stone.depth * _CROWN_FRACTION
    pavilion_h = definition.stone.depth * _PAVILION_FRACTION
    table_r = girdle_r * _TABLE_TO_GIRDLE_RATIO

    girdle_z = band_top_z(definition) + definition.setting.basketHeight

    solid = (
        cq.Workplane("XY")
        .workplane(offset=girdle_z - pavilion_h)
        .circle(_CULET_RADIUS_MM)
        .workplane(offset=pavilion_h)
        .circle(girdle_r)
        .workplane(offset=crown_h)
        .circle(table_r)
        .loft(ruled=True)
    )

    shape = solid.val()
    shape = _apply_orientation(shape, definition.stone.orientation)
    metadata = {
        "shape": "round",
        "girdleRadiusMm": girdle_r,
        "girdleZMm": girdle_z,
        "crownHeightMm": crown_h,
        "pavilionHeightMm": pavilion_h,
        "tableRadiusMm": table_r,
        "lengthMm": girdle_r * 2,
        "widthMm": girdle_r * 2,
        "depthMm": definition.stone.depth,
        "orientationDeg": definition.stone.orientation,
        # ADDITIVE METADATA ONLY — the geometry above is untouched.
        #
        # Round is the DEFAULT stone, and while this fast path exists to keep its
        # geometry byte-identical, that is no reason for it to be the least
        # inspectable stone in the system: before Sprint 20 filled these in, the
        # default solitaire reported NOT_APPLICABLE for its own shape family,
        # symmetry, outline and anchors while every other stone reported them.
        #
        # `symmetry` in particular is load-bearing: it is what lets the Setting
        # System choose RADIAL placement from a geometric property rather than
        # from the shape's name.
        "sourceMode": "PARAMETRIC_REFERENCE",
        "profile": "FACETED_REFERENCE",
        "family": "RADIAL",
        "symmetry": "RADIAL",
        "representation": "PARAMETRIC",
        "dimensionProvenance": "REQUESTED_PARAMETER",
        "narrowWidthMm": None,
        "measuredReferenceClass": None,
        "provenance": {
            "sourceMode": "PARAMETRIC_REFERENCE",
            "normalizationOperations": [],
            "generatorVersion": "1.0.0",
        },
        "isGemologicalReproduction": False,
        "referenceGeometryVersion": "1.0.0",
    }

    outline_points, outline_is_polygonal = O.sample_outline(O.round_outline(girdle_r, 1.0))
    metadata["outlineAvailable"] = True
    metadata["outlineIsPolygonal"] = outline_is_polygonal
    metadata["outlinePointCount"] = len(outline_points)
    metadata["outlinePointsMm"] = [[x, y] for x, y in outline_points]
    metadata["anchors"] = [
        {"anchor": a.anchor, "x": a.x, "y": a.y}
        for a in _round_anchors(outline_points)
    ]

    return GeneratedComponent(
        name="stone_reference",
        shape=shape,
        volume_mm3=shape.Volume(),
        bounding_box=BoundingBox.from_shape(shape),
        warnings=[],
        metadata=metadata,
    )


_OutlineFn = Callable[[float, float, float], cq.Wire]

_NON_ROUND_OUTLINE_BUILDERS: dict[str, _OutlineFn] = {
    "oval": O.oval_outline,
    "marquise": O.marquise_outline,
    "pear": O.pear_outline,
    "emerald": O.emerald_outline,
    "princess": O.princess_outline,
    "cushion": O.cushion_outline,
}


def _apply_orientation(shape: cq.Shape, orientation_deg: float) -> cq.Shape:
    """Rotate the finished solid around its own local vertical (Z) axis,
    at its own center — deterministic, explicit orientation
    (STONE-GOV-008). A no-op in practice for `round` (radially
    symmetric), applied uniformly for every shape rather than special-
    cased away."""

    if orientation_deg == 0.0:
        return shape
    bb = shape.BoundingBox()
    center = ((bb.xmin + bb.xmax) / 2, (bb.ymin + bb.ymax) / 2, (bb.zmin + bb.zmax) / 2)
    return shape.rotate(center, (center[0], center[1], center[2] + 1), orientation_deg)


def _build_non_round_stone(definition: JewelryDefinition) -> GeneratedComponent:
    """A real 3-level loft (culet → girdle → table) built from the shape's
    own outline primitive — see `outline.py`. Uses the exact same crown/
    pavilion/table ratios round already used, for a consistent reference
    silhouette across shapes (STONE-GOV-011)."""

    stone: StoneSpec = definition.stone
    outline_fn = _NON_ROUND_OUTLINE_BUILDERS.get(stone.shape)
    if outline_fn is None:
        raise StoneShapeUnsupportedError(f"No registered generator for stone.shape={stone.shape!r}")

    half_length = resolved_length_mm(stone) / 2
    half_width = resolved_width_mm(stone) / 2
    depth = resolved_depth_mm(stone)
    crown_h = depth * _CROWN_FRACTION
    pavilion_h = depth * _PAVILION_FRACTION

    girdle_z = band_top_z(definition) + definition.setting.basketHeight

    try:
        culet_wire = outline_fn(half_length, half_width, _CULET_SCALE_RATIO)
        girdle_wire = outline_fn(half_length, half_width, 1.0)
        table_wire = outline_fn(half_length, half_width, _TABLE_TO_GIRDLE_RATIO)

        culet_wire = culet_wire.translate((0, 0, girdle_z - pavilion_h))
        girdle_wire = girdle_wire.translate((0, 0, girdle_z))
        table_wire = table_wire.translate((0, 0, girdle_z + crown_h))

        solid = cq.Solid.makeLoft([culet_wire, girdle_wire, table_wire], ruled=True)
    except Exception as exc:  # noqa: BLE001 - OCC loft failures vary widely
        raise StoneGenerationError(
            f"Could not construct a stone reference for shape={stone.shape!r} "
            f"(length={half_length * 2}, width={half_width * 2}, depth={depth}): {exc}. "
            "This is a real construction failure, never silently downgraded to another shape."
        ) from exc

    if not solid.Solids() or not solid.isValid():
        raise StoneGenerationError(
            f"The requested stone shape={stone.shape!r} produced no valid solid — this "
            "configuration is not constructible with the current loft-based builder."
        )

    solid = _apply_orientation(solid, stone.orientation)

    metadata = {
        "shape": stone.shape,
        "girdleZMm": girdle_z,
        "crownHeightMm": crown_h,
        "pavilionHeightMm": pavilion_h,
        "lengthMm": half_length * 2,
        "widthMm": half_width * 2,
        "depthMm": depth,
        "orientationDeg": stone.orientation,
        "isGemologicalReproduction": False,
        "referenceGeometryVersion": "1.0.0",
    }

    return GeneratedComponent(
        name="stone_reference",
        shape=solid,
        volume_mm3=solid.Volume(),
        bounding_box=BoundingBox.from_shape(solid),
        warnings=[],
        metadata=metadata,
    )


def build_stone_geometry(
    stone: StoneSpec,
    girdle_z_mm: float,
    imported: object | None = None,
) -> GeneratedComponent:
    """The Stone v2 path: normalize the stone, then build outline x profile.

    Everything that is not the byte-identical `round` fast path flows through
    here — extended native cuts, cabochons, pearls, custom outlines, measured
    stones and imported assets alike. That is the point: one pipeline, so a new
    source or profile does not add a branch to every downstream consumer
    (brief section 54).
    """

    from jewelmind.geometry.stone.profile import (
        build_profile,
        build_spherical_reference,
    )
    from jewelmind.stone.dispatch import resolve_stone
    from jewelmind.stone.normalize import outline_builder_for, stone_anchors

    normalized = resolve_stone(stone, imported=imported)
    girdle_z = girdle_z_mm
    dimensions = normalized.dimensions

    if normalized.sourceMode == "IMPORTED_CAD":
        if imported is None:  # pragma: no cover - guarded by resolve_stone
            raise StoneGenerationError(
                "An imported stone requires real imported geometry."
            )
        # The imported asset IS the stone. It is placed, never rebuilt: silently
        # replacing it with a native approximation would discard the exact
        # geometry the user supplied (STONEV2-GOV-010).
        shape = imported.shape.translate((0, 0, girdle_z))
    elif normalized.profile == "SPHERICAL_REFERENCE":
        shape = build_spherical_reference(dimensions.depthMm, girdle_z)
    else:
        shape = build_profile(
            normalized.profile,
            outline_builder_for(normalized),
            dimensions.depthMm,
            girdle_z,
        )

    shape = _apply_orientation(shape, normalized.orientationDeg)

    solids = shape.Solids()
    anchors = stone_anchors(normalized)
    metadata = {
        "shape": normalized.shape,
        "sourceMode": normalized.sourceMode,
        "profile": normalized.profile,
        "family": normalized.family,
        "symmetry": normalized.symmetry,
        "representation": normalized.representation,
        "girdleZMm": girdle_z,
        "lengthMm": dimensions.lengthMm,
        "widthMm": dimensions.widthMm,
        "depthMm": dimensions.depthMm,
        "narrowWidthMm": dimensions.narrowWidthMm,
        "dimensionProvenance": dimensions.provenance,
        "orientationDeg": normalized.orientationDeg,
        "measuredReferenceClass": normalized.measuredReferenceClass,
        "anchors": [{"anchor": a.anchor, "x": a.x, "y": a.y} for a in anchors],
        "outlineAvailable": normalized.outline is not None,
        "outlineIsPolygonal": normalized.outline.isPolygonal if normalized.outline else None,
        "outlinePointCount": len(normalized.outline.points) if normalized.outline else 0,
        # The real outline points, carried so the Setting System can build a
        # bezel path for ANY stone without looking the shape up by name. This
        # is what makes a custom or imported stone settable at all. Golden
        # snapshots record specific geometric facts rather than raw metadata,
        # so carrying them here does not enlarge any baseline.
        "outlinePointsMm": (
            [[p.x, p.y] for p in normalized.outline.points] if normalized.outline else None
        ),
        "provenance": normalized.provenance.model_dump(),
        "isGemologicalReproduction": False,
        "referenceGeometryVersion": "2.0.0",
    }
    if normalized.profile != "SPHERICAL_REFERENCE" and normalized.sourceMode != "IMPORTED_CAD":
        crown_h = dimensions.depthMm * _CROWN_FRACTION
        metadata["crownHeightMm"] = crown_h
        metadata["pavilionHeightMm"] = dimensions.depthMm * _PAVILION_FRACTION

    # A mesh import legitimately has no solids and no volume. Reporting 0.0
    # rather than crashing is the honest answer, and `representation` already
    # tells a consumer why (brief section 32).
    volume = shape.Volume() if solids else 0.0

    return GeneratedComponent(
        name="stone_reference",
        shape=shape,
        volume_mm3=volume,
        bounding_box=BoundingBox.from_shape(shape),
        warnings=[],
        metadata=metadata,
    )


def build_stone(
    definition: JewelryDefinition,
    imported: object | None = None,
) -> GeneratedComponent:
    """Build the stone reference solid, named "stone_reference" (the
    stable, unchanged component identity).

    DISPATCH ORDER MATTERS AND IS DELIBERATE. A plain parametric `round`
    faceted stone — which is what every pre-Sprint-20 document is — takes the
    exact pre-Sprint-18 construction, untouched, which is what guarantees zero
    Golden baseline updates (brief section 70). Sprint 18 made the same choice
    for the same reason, and it is why Stone v1's twelve Golden cases survived
    that sprint unchanged.

    Everything else goes through the Stone v2 pipeline.
    """

    stone = definition.stone
    if (
        stone.shape == "round"
        and stone.source == "PARAMETRIC_REFERENCE"
        and stone.profile == "FACETED_REFERENCE"
    ):
        return _build_round_stone(definition)

    girdle_z = band_top_z(definition) + definition.setting.basketHeight
    return build_stone_geometry(stone, girdle_z, imported=imported)
