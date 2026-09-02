"""Canonical stone normalization (brief section 54).

`canonicalize_stone()` is the one place that resolves ANY accepted stone input
— a legacy Stone v1 document, an extended native cut, a custom outline, a
measured stone, or an imported asset — into a single
`NormalizedStoneDefinition`.

WHY THIS EXISTS: without it, every downstream system (Atlas, Forge, Setting,
Vision, Studio, Foundry, the technical specification, the review package) would
each need its own `if source == ...` ladder. Sprint 19 showed how that goes:
five separate architectural leaks appeared the moment `prong` stopped being the
only setting, every one of them a hardcoded assumption in a different module.
Normalizing once, here, is what stops the same thing happening for stone
sources.

Consumers therefore read `NormalizedStoneDefinition` and must NOT pattern-match
`shape` to infer a source; `sourceMode` is the field that says where geometry
came from.
"""

from __future__ import annotations

from jewelmind.domain.schema import StoneSpec
from jewelmind.geometry.stone import outline as outline_primitives
from jewelmind.stone.anchors import derive_anchors
from jewelmind.stone.capability import (
    CUSTOM_SHAPE_ID,
    IMPORTED_SHAPE_ID,
    STONE_GEOMETRY_VERSION_V2,
    STONE_SHAPE_CAPABILITIES_V2,
)
from jewelmind.stone.errors import (
    MeasuredStoneInsufficientDataError,
    StoneShapeDimensionsInvalidError,
    StoneShapeProfileCombinationUnsupportedError,
    StoneShapeUnsupportedError,
)
from jewelmind.stone.importing import STONE_IMPORTER_VERSION, ImportedStoneGeometry
from jewelmind.stone.models import (
    CustomOutlineSpec,
    NormalizedStoneDefinition,
    OutlinePoint,
    StoneAnchor,
    StoneDimensions,
    StoneOutline,
    StoneSourceProvenance,
)
from jewelmind.stone.outline_validation import normalize_custom_outline

#: Shapes whose horizontal size is a single diameter.
_ROUND_LIKE = frozenset({"round", "pearl"})

#: Shapes whose outline builder needs the extra narrow-width argument.
_TAPERED = frozenset({"tapered_baguette", "trapezoid"})

#: The registry of outline builders, keyed by canonical shape. A registry
#: rather than an if/elif chain so a new shape is a registration
#: (brief section 67). `round` takes a radius; `pearl` has no outline at all
#: (its profile is spherical); the tapered shapes take a fourth argument and
#: are bound separately in `outline_builder_for()`.
NATIVE_OUTLINE_BUILDERS = {
    "oval": outline_primitives.oval_outline,
    "marquise": outline_primitives.marquise_outline,
    "pear": outline_primitives.pear_outline,
    "emerald": outline_primitives.emerald_outline,
    "princess": outline_primitives.princess_outline,
    "cushion": outline_primitives.cushion_outline,
    "heart": outline_primitives.heart_outline,
    "radiant": outline_primitives.radiant_outline,
    "asscher": outline_primitives.asscher_outline,
    "trillion": outline_primitives.trillion_outline,
    "baguette": outline_primitives.baguette_outline,
    "triangle": outline_primitives.triangle_outline,
    "lozenge": outline_primitives.lozenge_outline,
    "hexagon": outline_primitives.hexagon_outline,
    "kite": outline_primitives.kite_outline,
    "shield": outline_primitives.shield_outline,
    "half_moon": outline_primitives.half_moon_outline,
}


def outline_builder_for(normalized: NormalizedStoneDefinition):
    """Return a `(scale) -> cq.Wire` builder for this stone's outline.

    Binding the dimensions here means the profile builders in
    `geometry/stone/profile.py` never learn which shape they are building —
    which is what lets CABOCHON_REFERENCE apply to a native cut and a custom
    outline through exactly the same code path.
    """

    dimensions = normalized.dimensions
    half_length = dimensions.lengthMm / 2
    half_width = dimensions.widthMm / 2

    if normalized.sourceMode == "CUSTOM_OUTLINE" or normalized.shape == CUSTOM_SHAPE_ID:
        if normalized.outline is None:
            raise StoneShapeDimensionsInvalidError(
                "A custom-outline stone has no normalized outline to build from."
            )
        points = [(p.x, p.y) for p in normalized.outline.points]
        return lambda scale: outline_primitives.custom_outline(points, scale)

    if normalized.shape == "round":
        return lambda scale: outline_primitives.round_outline(half_width, scale)

    if normalized.shape in _TAPERED:
        narrow = normalized.dimensions.narrowWidthMm
        if narrow is None:
            raise StoneShapeDimensionsInvalidError(
                f"Shape {normalized.shape!r} requires a narrow width."
            )
        builder = (
            outline_primitives.tapered_baguette_outline
            if normalized.shape == "tapered_baguette"
            else outline_primitives.trapezoid_outline
        )
        return lambda scale: builder(half_length, half_width, scale, narrow / 2)

    builder = NATIVE_OUTLINE_BUILDERS.get(normalized.shape)
    if builder is None:
        raise StoneShapeUnsupportedError(
            f"No registered outline builder for stone shape {normalized.shape!r}."
        )
    return lambda scale: builder(half_length, half_width, scale)


def _outline_from_points(
    points: list[OutlinePoint], is_polygonal: bool, derivation: str
) -> StoneOutline:
    return StoneOutline(points=points, isPolygonal=is_polygonal, derivation=derivation)


def native_outline(normalized: NormalizedStoneDefinition) -> StoneOutline | None:
    """Sample a native shape's real girdle outline into explicit points.

    Returns `None` for a shape that genuinely has no planar outline — the
    spherical pearl reference — rather than inventing one (brief section 44).
    """

    if normalized.profile == "SPHERICAL_REFERENCE" or normalized.shape == "pearl":
        return None
    builder = outline_builder_for(normalized)
    points, is_polygonal = outline_primitives.sample_outline(builder(1.0))
    return _outline_from_points(
        [OutlinePoint(x=x, y=y) for x, y in points],
        is_polygonal,
        "NATIVE_PRIMITIVE" if is_polygonal else "SAMPLED_FROM_CURVE",
    )


def _dimensions_from_outline(
    points: list[OutlinePoint], depth_mm: float, provenance: str
) -> StoneDimensions:
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    return StoneDimensions(
        lengthMm=max(ys) - min(ys),
        widthMm=max(xs) - min(xs),
        depthMm=depth_mm,
        provenance=provenance,
    )


def _require_positive(name: str, value: float | None) -> float:
    if value is None:
        raise StoneShapeDimensionsInvalidError(f"stone.{name} is required.")
    if not (value > 0):
        raise StoneShapeDimensionsInvalidError(
            f"stone.{name} must be greater than zero, got {value!r}."
        )
    return value


def _parametric_dimensions(stone: StoneSpec) -> StoneDimensions:
    if stone.shape in _ROUND_LIKE:
        diameter = _require_positive("diameter", stone.diameter)
        return StoneDimensions(
            lengthMm=diameter,
            widthMm=diameter,
            # A sphere's depth IS its diameter; accepting a different `depth`
            # for a pearl and then ignoring it would be a silent lie, so the
            # spherical case reports the diameter it actually builds.
            depthMm=diameter if stone.shape == "pearl" else _require_positive("depth", stone.depth),
            provenance="REQUESTED_PARAMETER",
        )

    return StoneDimensions(
        lengthMm=_require_positive("length", stone.length),
        widthMm=_require_positive("width", stone.width),
        depthMm=_require_positive("depth", stone.depth),
        narrowWidthMm=(
            _require_positive("narrowWidth", stone.narrowWidth)
            if stone.shape in _TAPERED
            else None
        ),
        provenance="REQUESTED_PARAMETER",
    )


def _capability_facts(shape: str) -> tuple[str, str]:
    entry = STONE_SHAPE_CAPABILITIES_V2.get(shape)
    if entry is None:
        raise StoneShapeUnsupportedError(
            f"Stone shape {shape!r} is not in the Stone System capability registry."
        )
    return entry.family, entry.symmetryClass


def resolve_profile(stone: StoneSpec) -> tuple[str, list[str]]:
    """Decide which 3D reference profile to build, honestly.

    THE DISTINCTION THAT MATTERS: a profile the caller never set is a schema
    default, and resolving it to the shape's only supported profile is a
    deterministic default — recorded in provenance, not hidden. A profile the
    caller DID set and that the shape does not support is a real error, and is
    raised rather than quietly replaced (STONEV2-GOV-010: never silently
    substitute).

    Without this, `{"shape": "pearl", "diameter": 8}` failed deep inside the
    outline builder, because `profile` defaults to FACETED_REFERENCE while a
    sphere supports only SPHERICAL_REFERENCE.
    """

    entry = STONE_SHAPE_CAPABILITIES_V2.get(stone.shape)
    if entry is None:
        raise StoneShapeUnsupportedError(
            f"Stone shape {stone.shape!r} is not in the Stone System capability registry."
        )

    requested = stone.profile
    if requested in entry.supportedProfiles:
        return requested, []

    explicitly_set = "profile" in stone.model_fields_set
    if explicitly_set or len(entry.supportedProfiles) != 1:
        raise StoneShapeProfileCombinationUnsupportedError(
            f"Stone shape {stone.shape!r} does not support reference profile "
            f"{requested!r}. Supported for this shape: "
            f"{', '.join(entry.supportedProfiles)}."
        )

    resolved = entry.supportedProfiles[0]
    return resolved, [f"PROFILE_DEFAULTED:{requested}->{resolved}"]


def canonicalize_stone(
    stone: StoneSpec,
    imported: ImportedStoneGeometry | None = None,
    stone_id: str = "stone_reference",
) -> NormalizedStoneDefinition:
    """Resolve any accepted stone input into the one canonical internal model.

    `imported` must be supplied when `stone.source == "IMPORTED_CAD"`: the real
    geometry has to be read before its dimensions are known, and this function
    never reaches out to an asset store itself — that keeps normalization pure
    and testable, and keeps I/O at the orchestration layer.
    """

    if stone.source == "CUSTOM_OUTLINE":
        assert stone.customOutline is not None  # enforced by StoneSpec's validator
        spec = CustomOutlineSpec(
            points=[{"x": p.x, "y": p.y} for p in stone.customOutline.points],
            unit=stone.customOutline.unit,
            label=stone.customOutline.label,
        )
        points, operations = normalize_custom_outline(spec)
        outline = _outline_from_points(points, True, "CUSTOM_INPUT")
        dimensions = _dimensions_from_outline(
            points, _require_positive("depth", stone.depth), "DERIVED_FROM_OUTLINE"
        )
        return NormalizedStoneDefinition(
            stoneId=stone_id,
            sourceMode="CUSTOM_OUTLINE",
            shape=CUSTOM_SHAPE_ID,
            family="CUSTOM",
            profile=stone.profile,
            dimensions=dimensions,
            orientationDeg=stone.orientation,
            symmetry="UNKNOWN",
            representation="PARAMETRIC",
            outline=outline,
            provenance=StoneSourceProvenance(
                sourceMode="CUSTOM_OUTLINE",
                originalUnit=stone.customOutline.unit,
                normalizationOperations=operations,
                generatorVersion=STONE_GEOMETRY_VERSION_V2,
                sourceAssetName=stone.customOutline.label,
            ),
        )

    if stone.source == "IMPORTED_CAD":
        assert stone.importedAsset is not None  # enforced by StoneSpec's validator
        if imported is None:
            raise StoneShapeDimensionsInvalidError(
                "An imported stone cannot be canonicalized without its real "
                "imported geometry; dimensions come from the asset, never from "
                "the design document."
            )
        return NormalizedStoneDefinition(
            stoneId=stone_id,
            sourceMode="IMPORTED_CAD",
            shape=IMPORTED_SHAPE_ID,
            family="IMPORTED",
            profile=stone.profile,
            dimensions=StoneDimensions(
                lengthMm=imported.lengthMm,
                widthMm=imported.widthMm,
                depthMm=imported.depthMm,
                provenance="IMPORTED_GEOMETRY_MEASUREMENT",
            ),
            orientationDeg=stone.orientation,
            symmetry="UNKNOWN",
            representation=imported.representation,
            outline=None,
            provenance=StoneSourceProvenance(
                sourceMode="IMPORTED_CAD",
                sourceAssetHash=imported.assetHash,
                sourceAssetName=imported.assetName,
                originalUnit=stone.importedAsset.declaredUnit,
                normalizationOperations=imported.normalizationOperations,
                importerVersion=STONE_IMPORTER_VERSION,
            ),
        )

    # PARAMETRIC_REFERENCE and MEASURED share the named-cut dimension rules.
    family, symmetry = _capability_facts(stone.shape)
    profile, operations = resolve_profile(stone)
    dimensions = _parametric_dimensions(stone)

    measured_class = None
    outline: StoneOutline | None = None

    if stone.source == "MEASURED":
        if stone.shape in _ROUND_LIKE:
            if stone.diameter is None:
                raise MeasuredStoneInsufficientDataError(
                    "A measured round stone needs a real measured diameter."
                )
        elif stone.length is None or stone.width is None:
            raise MeasuredStoneInsufficientDataError(
                "A measured stone needs real measured length and width. "
                "JewelMind never infers a missing measurement."
            )
        dimensions = dimensions.model_copy(update={"provenance": "INPUT_MEASUREMENT"})
        measured_class = "MEASURED_DIMENSION_REFERENCE"

        if stone.customOutline is not None:
            spec = CustomOutlineSpec(
                points=[{"x": p.x, "y": p.y} for p in stone.customOutline.points],
                unit=stone.customOutline.unit,
                label=stone.customOutline.label,
            )
            points, operations = normalize_custom_outline(spec)
            outline = _outline_from_points(points, True, "CUSTOM_INPUT")
            dimensions = _dimensions_from_outline(
                points, dimensions.depthMm, "INPUT_MEASUREMENT"
            )
            measured_class = "MEASURED_OUTLINE_REFERENCE"

    normalized = NormalizedStoneDefinition(
        stoneId=stone_id,
        sourceMode=stone.source,
        shape=stone.shape,
        family=family,
        profile=profile,
        dimensions=dimensions,
        orientationDeg=stone.orientation,
        symmetry=symmetry,
        representation="PARAMETRIC",
        outline=outline,
        measuredReferenceClass=measured_class,
        provenance=StoneSourceProvenance(
            sourceMode=stone.source,
            normalizationOperations=operations,
            generatorVersion=STONE_GEOMETRY_VERSION_V2,
            measurementSource=stone.measurement.measurementSource if stone.measurement else None,
            measurementDate=stone.measurement.measurementDate if stone.measurement else None,
            operatorNote=stone.measurement.operatorNote if stone.measurement else None,
        ),
    )

    if normalized.outline is None:
        normalized = normalized.model_copy(update={"outline": native_outline(normalized)})
    return normalized


def stone_anchors(normalized: NormalizedStoneDefinition) -> list[StoneAnchor]:
    """Every deterministic anchor for this stone, or an empty list when the
    outline is unavailable. Never a fabricated anchor (STONEV2-GOV-009)."""

    if normalized.outline is None:
        return []
    return derive_anchors(normalized.shape, normalized.outline.points)
