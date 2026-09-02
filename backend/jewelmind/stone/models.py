"""Category-neutral Stone System v2 domain models (brief sections 3/34/35/36/43).

Every model here is KERNEL-NEUTRAL: no field holds a `cadquery.Shape`,
`Workplane`, or OCP object, so Forge, Studio, Designer, Setting and any future
jewelry category can depend on these contracts without importing CadQuery.
Real geometry objects live only on the `GeneratedComponent`s the Atlas-layer
builders return.

Nothing here imports `jewelmind.ring`, any other jewelry category, or
`JewelryDefinition` (STONEV2-GOV-001).

THE CENTRAL SEPARATION OF THIS SPRINT (brief section 36): a stone's OUTLINE
SHAPE and its 3D REFERENCE PROFILE are independent axes.

    outline = OVAL   + profile = FACETED_REFERENCE   -> a faceted-style oval
    outline = OVAL   + profile = CABOCHON_REFERENCE  -> an oval cabochon
    outline = CUSTOM + profile = CABOCHON_REFERENCE  -> a custom cabochon

Modelling those as two axes rather than as `OVAL_CABOCHON`-style compound enum
members is what keeps the shape list from exploding combinatorially, and is
why a cabochon is not "just another outline".
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Canonical vocabularies
# ---------------------------------------------------------------------------

#: Where a stone's geometry comes from (brief section 3).
#:
#: `SCANNED_MESH` is deliberately NOT a member. A scan arrives as a mesh or a
#: converted CAD file and is handled by `IMPORTED_CAD`'s normalization; adding
#: a separate mode would duplicate that pipeline without adding meaning
#: (brief sections 3/33). Scan-specific processing remains PLANNED and is
#: tracked as the `STONE_SCAN` capability.
StoneSourceMode = Literal[
    "PARAMETRIC_REFERENCE",
    "CUSTOM_OUTLINE",
    "MEASURED",
    "IMPORTED_CAD",
]

#: The 3D reference profile applied to an outline (brief sections 21/36).
#:
#: These are reference-geometry classes, never claims of a commercial cutting
#: style. `SPHERICAL_REFERENCE` ignores the outline entirely — it is the pearl
#: / bead case, where the silhouette is a consequence of the profile.
StoneReferenceProfile = Literal[
    "FACETED_REFERENCE",
    "CABOCHON_REFERENCE",
    "SPHERICAL_REFERENCE",
]

#: Geometry-reuse families (brief section 5). A family groups shapes that share
#: a construction strategy; it is NOT a jewelry-marketing taxonomy, and two
#: shapes in one family remain independently changeable canonical IDs.
StoneShapeFamily = Literal[
    "RADIAL",
    "ELLIPTICAL",
    "POINTED_ELONGATED",
    "ASYMMETRIC_POINTED",
    "RECTILINEAR",
    "CLIPPED_RECTILINEAR",
    "ROUNDED_RECTILINEAR",
    "SQUARE_ANGULAR",
    "TRIANGULAR",
    "TAPERED_QUADRILATERAL",
    "POLYGONAL",
    "SPECIAL_OUTLINE",
    "SPHERICAL",
    "CUSTOM",
    "IMPORTED",
]

#: How a stone's outline behaves under reflection. Drives whether a Setting may
#: assume symmetry it does not have (SETTING-GOV-008).
SymmetryClass = Literal[
    "RADIAL",
    "BILATERAL_BOTH_AXES",
    "BILATERAL_ONE_AXIS",
    "ASYMMETRIC",
    "UNKNOWN",
]

#: Deterministic named points on a stone outline (brief section 43).
#:
#: An anchor is a GEOMETRIC FACT — where a feature of the outline is. It is
#: explicitly NOT a prong position: the Setting System decides how (or whether)
#: to use an anchor (STONEV2-GOV-009).
StoneAnchorId = Literal[
    "CENTER",
    "TOP",
    "BOTTOM",
    "LEFT",
    "RIGHT",
    "TIP",
    "CLEFT",
    "LEFT_LOBE",
    "RIGHT_LOBE",
    "WIDE_END",
    "NARROW_END",
    "CORNER_NW",
    "CORNER_NE",
    "CORNER_SW",
    "CORNER_SE",
]

#: How an imported asset's geometry is represented. B-Rep supports richer
#: operations than a mesh, and the difference is never papered over
#: (brief section 32).
StoneRepresentation = Literal["BREP_SOLID", "MESH", "PARAMETRIC"]

#: Where a dimension value came from. Keeps a measurement the user supplied
#: distinct from a value JewelMind computed off its own generated reference
#: (brief section 46).
DimensionProvenance = Literal[
    "REQUESTED_PARAMETER",
    "INPUT_MEASUREMENT",
    "GENERATED_REFERENCE_MEASUREMENT",
    "IMPORTED_GEOMETRY_MEASUREMENT",
    "DERIVED_FROM_OUTLINE",
]

#: How a measured stone's reference geometry relates to the physical stone.
#:
#: `MEASURED_DIMENSION_REFERENCE` is the honest label for "we built an
#: approximation from length/width/depth" — it must never be presented as the
#: real surface of the physical stone (brief section 29).
MeasuredReferenceClass = Literal[
    "MEASURED_DIMENSION_REFERENCE",
    "MEASURED_OUTLINE_REFERENCE",
]

CapabilityStatus = Literal["CURRENT", "PARTIAL", "PLANNED", "BLOCKED", "OUT_OF_SCOPE"]

SettingCompatibilityStatus = Literal["SUPPORTED_SOFTWARE", "EXPERIMENTAL", "UNSUPPORTED"]

ProfessionalValidationStatus = Literal["NOT_REVIEWED", "IN_REVIEW", "VALIDATED"]

#: Units a caller may declare for an imported asset or a custom outline.
#: JewelMind's own internal unit is always the millimetre (LAW-007); these
#: exist only so an explicitly-declared foreign unit can be converted once, at
#: the boundary, and recorded in provenance.
DeclaredUnit = Literal["mm", "cm", "m", "in"]

#: Conversion factors to millimetres. Exact by definition, including the inch
#: (25.4mm is the international definition, not an approximation).
UNIT_TO_MM: dict[str, float] = {"mm": 1.0, "cm": 10.0, "m": 1000.0, "in": 25.4}


class StoneModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
# Outline and anchors
# ---------------------------------------------------------------------------


class OutlinePoint(StoneModel):
    """One 2D point in the stone's local XY frame, in millimetres."""

    x: float
    y: float


class CustomOutlineSpec(StoneModel):
    """A caller-supplied closed 2D outline (brief sections 23/25).

    Represented as ordered points rather than as curve segments: points are the
    one representation every accepted input form (JSON, a vector path, a future
    SVG adapter) can be reduced to without loss of determinism, and they carry
    no capacity to express executable geometry (JDL's no-executable-code rule
    applies here too).

    The outline is implicitly closed — the last point connects back to the
    first — and a caller must NOT repeat the first point at the end. Validation
    rejects a duplicated closing point rather than silently dropping it.
    """

    points: list[OutlinePoint] = Field(min_length=3)
    #: The unit the points are expressed in. Converted to millimetres exactly
    #: once, during normalization, and recorded in provenance.
    unit: DeclaredUnit = "mm"
    #: Optional caller label, carried through for traceability only.
    label: str | None = Field(default=None, max_length=200)


class StoneOutline(StoneModel):
    """A normalized, millimetre-space outline any consumer may read
    (brief section 44).

    This is the single contract that makes the Setting System shape-agnostic:
    a bezel consumes `points` and never needs to know whether they came from a
    native enum member, a custom outline, or a projected imported solid.
    """

    points: list[OutlinePoint] = Field(min_length=3)
    #: True when the outline is a closed polygon of straight segments. False
    #: when it is a sampled approximation of a curved outline, so a consumer
    #: can tell an exact polygon from a discretization.
    isPolygonal: bool
    #: How the outline was obtained, for honest reporting.
    derivation: Literal[
        "NATIVE_PRIMITIVE",
        "CUSTOM_INPUT",
        "SAMPLED_FROM_CURVE",
        "PROJECTED_FROM_GEOMETRY",
    ]


class StoneAnchor(StoneModel):
    """A deterministic named point on the stone outline, in local millimetres.

    A geometric fact only. Never a prong position (STONEV2-GOV-009).
    """

    anchor: StoneAnchorId
    x: float
    y: float


# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------


class StoneDimensions(StoneModel):
    """Resolved stone dimensions in millimetres (brief section 35).

    LENGTH is the major horizontal dimension (local Y), WIDTH the minor
    horizontal dimension (local X), DEPTH the vertical dimension (local Z) —
    unchanged from Sprint 18's contract in `domain/stone_dimensions.py`.

    `narrowWidthMm` is populated only for the tapered family, where the taper
    is a real dimension rather than a hidden ratio (brief section 13).
    """

    lengthMm: float
    widthMm: float
    depthMm: float
    narrowWidthMm: float | None = None
    provenance: DimensionProvenance


class DimensionComparison(StoneModel):
    """Requested versus measured dimensions for one stone (brief section 46).

    Both sides are always real numbers taken from real sources: `requested` is
    what the caller asked for, `measured` is what the generated or imported
    geometry actually is. They are never assumed equal, and `withinTolerance`
    is computed, not asserted.
    """

    requested: StoneDimensions | None
    measured: StoneDimensions
    lengthDeltaMm: float | None
    widthDeltaMm: float | None
    depthDeltaMm: float | None
    withinTolerance: bool | None


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


class StoneSourceProvenance(StoneModel):
    """Where a stone's geometry came from (brief section 34).

    Deliberately free of wall-clock timestamps: this record participates in
    `definitionHash` and in Golden snapshots, and a volatile field would make
    identical geometry hash differently on every run (ATLAS-GOV-003,
    brief section 34's own "do not include volatile metadata" instruction).
    A caller-supplied `measurementDate` is a stable data value, not a clock
    reading, so it is allowed.
    """

    sourceMode: StoneSourceMode
    #: Stable identity of an external asset — a content hash, never a
    #: filesystem path (FOUNDRY-GOV-011: no internal server path may leak).
    sourceAssetHash: str | None = None
    #: Caller-facing asset name, for traceability in a review package.
    sourceAssetName: str | None = Field(default=None, max_length=255)
    originalUnit: DeclaredUnit | None = None
    #: Every normalization actually applied, in order. An empty list means no
    #: normalization was needed, never that normalization was skipped.
    normalizationOperations: list[str] = Field(default_factory=list)
    generatorVersion: str | None = None
    importerVersion: str | None = None
    #: Free-text description of how a physical measurement was taken.
    measurementSource: str | None = Field(default=None, max_length=500)
    #: Caller-supplied date as an opaque string. Never generated from the clock.
    measurementDate: str | None = Field(default=None, max_length=64)
    operatorNote: str | None = Field(default=None, max_length=500)


# ---------------------------------------------------------------------------
# Source specifications
# ---------------------------------------------------------------------------


class ParametricStoneSource(StoneModel):
    """A stone built from a named canonical shape plus explicit dimensions."""

    mode: Literal["PARAMETRIC_REFERENCE"] = "PARAMETRIC_REFERENCE"
    shape: str
    profile: StoneReferenceProfile = "FACETED_REFERENCE"


class CustomOutlineStoneSource(StoneModel):
    """A stone built from a caller-supplied outline — the escape hatch that
    frees the Stone System from a finite built-in shape list
    (brief sections 23/76)."""

    mode: Literal["CUSTOM_OUTLINE"] = "CUSTOM_OUTLINE"
    outline: CustomOutlineSpec
    profile: StoneReferenceProfile = "FACETED_REFERENCE"
    depthMm: float


class MeasuredStoneSource(StoneModel):
    """A real physical stone the user has measured (brief sections 28/29).

    If only length/width/depth are supplied, JewelMind builds an approximation
    and labels it `MEASURED_DIMENSION_REFERENCE`. If a measured outline is also
    supplied it is used, and the result is `MEASURED_OUTLINE_REFERENCE`. A
    missing measurement is never invented (STONEV2-GOV-006).
    """

    mode: Literal["MEASURED"] = "MEASURED"
    lengthMm: float
    widthMm: float
    depthMm: float
    #: The named shape the operator judged this stone to be, if any. Optional
    #: on purpose: a measured stone may genuinely have no known cut, and
    #: `None` is the honest answer rather than a guess.
    shape: str | None = None
    profile: StoneReferenceProfile = "FACETED_REFERENCE"
    measuredOutline: CustomOutlineSpec | None = None
    measurementSource: str | None = Field(default=None, max_length=500)
    measurementDate: str | None = Field(default=None, max_length=64)
    operatorNote: str | None = Field(default=None, max_length=500)


class ImportedStoneSource(StoneModel):
    """Externally supplied stone geometry (brief sections 30/31/32).

    `declaredUnit` is required rather than inferred. No CAD or mesh format
    JewelMind reads carries a reliable, universally-populated unit, and
    guessing one silently rescales a real physical object — so the caller
    declares it and the declaration is recorded in provenance
    (FOUNDRY-GOV-012).
    """

    mode: Literal["IMPORTED_CAD"] = "IMPORTED_CAD"
    #: Content hash of the asset. The importer resolves this to real bytes; a
    #: filesystem path never travels in a domain model.
    assetHash: str
    assetName: str | None = Field(default=None, max_length=255)
    declaredUnit: DeclaredUnit
    #: Rotation about the local vertical axis applied after import, in degrees.
    orientationDeg: float = 0.0


StoneSource = (
    ParametricStoneSource
    | CustomOutlineStoneSource
    | MeasuredStoneSource
    | ImportedStoneSource
)


# ---------------------------------------------------------------------------
# The canonical normalized model
# ---------------------------------------------------------------------------


class NormalizedStoneDefinition(StoneModel):
    """The single internal stone model every downstream system consumes
    (brief section 54).

    Legacy Stone v1 input, an extended native shape, a custom outline, a
    measured stone and an imported asset all normalize into this one shape, so
    source-specific branching stays inside `jewelmind/stone/` instead of
    spreading across Atlas, Forge, Setting, Vision and Studio.

    `shape` is a string rather than a closed enum on purpose: a custom or
    imported stone genuinely has no canonical named cut, and this field carries
    `"custom"` or `"imported"` for those. Consumers that need to know whether a
    named cut is present must read `sourceMode`, never pattern-match `shape`.
    """

    stoneId: str = "stone_reference"
    sourceMode: StoneSourceMode
    shape: str
    family: StoneShapeFamily
    profile: StoneReferenceProfile
    dimensions: StoneDimensions
    orientationDeg: float = 0.0
    symmetry: SymmetryClass
    representation: StoneRepresentation
    provenance: StoneSourceProvenance
    #: Present when the outline is known in normalized millimetre space.
    #: `None` when it genuinely cannot be derived — never a fabricated
    #: silhouette (brief section 44).
    outline: StoneOutline | None = None
    #: Explicit reference class for a measured stone; `None` for every other
    #: source mode.
    measuredReferenceClass: MeasuredReferenceClass | None = None
