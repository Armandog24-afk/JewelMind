"""The authoritative Stone System v2 shape and source registries
(brief sections 6/67; STONEV2-GOV-013).

This module is the SINGLE SOURCE OF TRUTH for what the Stone System can
actually do. `specs/stone/v2/shape-registry-v2.json` and
`stone-source-registry.json` are generated from it, never hand-maintained as a
second, driftable copy (JEWELRY-ARCH-GOV-015's discipline).

THREE INDEPENDENT AXES, never collapsed into one (STONEV2-GOV-007):

- `generationSupported` — a real registered generator produces real CAD.
- `settingCompatibility`  — whether a Setting can currently grip this shape.
- `professionalValidationStatus` — whether a qualified human reviewed it.

A shape that generates real geometry is not, by that fact, a shape whose
setting is valid, and neither implies professional validation. Every entry
below is `NOT_REVIEWED`, and must stay so until a real `ValidationRecord` with
real evidence exists (PROVAL-GOV-006).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from jewelmind.stone.models import (
    CapabilityStatus,
    ProfessionalValidationStatus,
    SettingCompatibilityStatus,
    StoneReferenceProfile,
    StoneRepresentation,
    StoneShapeFamily,
    StoneSourceMode,
    SymmetryClass,
)

#: Version of the Stone v2 reference-geometry construction algorithms.
#: Bumped on any MAJOR change to how an outline or profile is built.
STONE_GEOMETRY_VERSION_V2 = "2.0.0"

#: Version of the imported-stone normalization pipeline.
STONE_IMPORTER_VERSION = "1.0.0"

#: Pseudo-shape IDs used when a stone genuinely has no named canonical cut.
#: They are real registry entries so that every consumer can look up their
#: capabilities uniformly, but they are never offered as "cuts" to a user.
CUSTOM_SHAPE_ID = "custom"
IMPORTED_SHAPE_ID = "imported"

#: Shape names JewelMind deliberately does NOT implement, with the reason.
#: Listing them documents direction without implying capability
#: (SETTING-GOV-005's discipline applied to shapes). None has a generator, and
#: none is a member of the JDL `StoneShape` enum.
RESERVED_STONE_SHAPES: dict[str, str] = {
    "briolette": "Fully three-dimensional drop with no single girdle plane; "
    "the current outline-plus-profile pipeline cannot express it.",
    "rose_cut": "Defined by its facet arrangement (flat back, domed faceted "
    "crown) rather than by its outline; needs a real facet model.",
    "old_mine": "A historical proportion set, not a distinct outline. Would "
    "require sourced proportions JewelMind does not have.",
    "star": "Concave polygonal outline is expressible, but no sourced "
    "proportions exist; a caller wanting one today should use CUSTOM_OUTLINE.",
    "cross": "As above — reachable through CUSTOM_OUTLINE without a new enum.",
}


class StoneShapeCapabilityV2(BaseModel):
    """One canonical shape's real, current capabilities (brief section 6)."""

    model_config = ConfigDict(extra="forbid")

    shape: str
    aliases: list[str] = Field(default_factory=list)
    family: StoneShapeFamily
    status: CapabilityStatus
    generationSupported: bool
    inspectionSupported: bool
    visionSupported: bool
    jdlSupported: bool
    requiredDimensions: list[str]
    optionalDimensions: list[str] = Field(default_factory=list)
    symmetryClass: SymmetryClass
    #: Profiles this outline may be combined with (brief section 36).
    supportedProfiles: list[StoneReferenceProfile]
    #: Source modes this shape can be produced through.
    availableSourceModes: list[StoneSourceMode]
    anchors: list[str] = Field(default_factory=list)
    referenceGeometryVersion: str
    prongCompatibility: SettingCompatibilityStatus
    bezelCompatibility: SettingCompatibilityStatus
    professionalValidationStatus: ProfessionalValidationStatus
    #: True when this shape existed and generated real geometry before Sprint
    #: 20. Those must remain byte-identical (brief section 70).
    introducedInStoneV1: bool
    description: str


class StoneSourceCapability(BaseModel):
    """One source mode's real, current capabilities (brief section 3)."""

    model_config = ConfigDict(extra="forbid")

    sourceMode: StoneSourceMode
    status: CapabilityStatus
    generatesRealGeometry: bool
    representation: StoneRepresentation
    outlineAvailable: bool
    anchorsAvailable: bool
    settingCompatible: bool
    professionalValidationStatus: ProfessionalValidationStatus
    description: str
    knownLimitations: list[str] = Field(default_factory=list)


_FACETED: list[StoneReferenceProfile] = ["FACETED_REFERENCE"]
_FACETED_AND_CAB: list[StoneReferenceProfile] = ["FACETED_REFERENCE", "CABOCHON_REFERENCE"]
_NATIVE_SOURCES: list[StoneSourceMode] = ["PARAMETRIC_REFERENCE", "MEASURED"]
_LWD = ["length", "width", "depth"]
_CARDINAL = ["CENTER", "TOP", "BOTTOM", "LEFT", "RIGHT"]


def _entry(**kwargs) -> StoneShapeCapabilityV2:
    kwargs.setdefault("status", "CURRENT")
    kwargs.setdefault("generationSupported", True)
    kwargs.setdefault("inspectionSupported", True)
    kwargs.setdefault("visionSupported", True)
    kwargs.setdefault("jdlSupported", True)
    kwargs.setdefault("requiredDimensions", _LWD)
    kwargs.setdefault("supportedProfiles", _FACETED)
    kwargs.setdefault("availableSourceModes", _NATIVE_SOURCES)
    kwargs.setdefault("anchors", _CARDINAL)
    kwargs.setdefault("referenceGeometryVersion", STONE_GEOMETRY_VERSION_V2)
    kwargs.setdefault("professionalValidationStatus", "NOT_REVIEWED")
    kwargs.setdefault("introducedInStoneV1", False)
    return StoneShapeCapabilityV2(**kwargs)


_ENTRIES: list[StoneShapeCapabilityV2] = [
    # ---------------------------------------------------- Stone v1 (unchanged)
    _entry(
        shape="round", aliases=["brilliant", "round brilliant", "rotondo", "tondo"],
        family="RADIAL", requiredDimensions=["diameter", "depth"],
        symmetryClass="RADIAL", supportedProfiles=_FACETED_AND_CAB,
        prongCompatibility="SUPPORTED_SOFTWARE", bezelCompatibility="SUPPORTED_SOFTWARE",
        introducedInStoneV1=True, referenceGeometryVersion="1.0.0",
        description="Pre-Sprint-18 lofted round reference, byte-identical since Sprint 18.",
    ),
    _entry(
        shape="oval", aliases=["ovale"], family="ELLIPTICAL",
        symmetryClass="BILATERAL_BOTH_AXES", supportedProfiles=_FACETED_AND_CAB,
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="SUPPORTED_SOFTWARE",
        introducedInStoneV1=True, referenceGeometryVersion="1.0.0",
        description="Elliptical outline. Bezel requires STEP-safety resampling (Sprint 19).",
    ),
    _entry(
        shape="pear", aliases=["pera", "goccia", "teardrop", "drop"],
        family="ASYMMETRIC_POINTED", symmetryClass="BILATERAL_ONE_AXIS",
        anchors=[*_CARDINAL, "TIP"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        introducedInStoneV1=True, referenceGeometryVersion="1.0.0",
        description="One pointed tip at +Y, one rounded end. Placement is not tip-aware.",
    ),
    _entry(
        shape="emerald", aliases=["smeraldo", "taglio smeraldo", "emerald cut"],
        family="CLIPPED_RECTILINEAR", symmetryClass="BILATERAL_BOTH_AXES",
        anchors=[*_CARDINAL, "CORNER_NW", "CORNER_NE", "CORNER_SW", "CORNER_SE"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        introducedInStoneV1=True, referenceGeometryVersion="1.0.0",
        description=(
            "Clipped-corner rectangle. NOTE: this is a SHAPE named emerald, never the "
            "gem species emerald — see STONEV2-GOV-008."
        ),
    ),
    _entry(
        shape="cushion", aliases=["cuscino"], family="ROUNDED_RECTILINEAR",
        symmetryClass="BILATERAL_BOTH_AXES",
        anchors=[*_CARDINAL, "CORNER_NW", "CORNER_NE", "CORNER_SW", "CORNER_SE"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        introducedInStoneV1=True, referenceGeometryVersion="1.0.0",
        description="Rounded-rectangle outline.",
    ),
    _entry(
        shape="princess", aliases=["principessa", "quadrato", "square"],
        family="SQUARE_ANGULAR", symmetryClass="BILATERAL_BOTH_AXES",
        anchors=[*_CARDINAL, "CORNER_NW", "CORNER_NE", "CORNER_SW", "CORNER_SE"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        introducedInStoneV1=True, referenceGeometryVersion="1.0.0",
        description="Plain rectangle; square only when length equals width.",
    ),
    _entry(
        shape="marquise", aliases=["navette", "marchesa"], family="POINTED_ELONGATED",
        symmetryClass="BILATERAL_BOTH_AXES", anchors=[*_CARDINAL, "TIP"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        introducedInStoneV1=True, referenceGeometryVersion="1.0.0",
        description="Two-arc pointed lens. Prongs are not clustered at the tips.",
    ),
    # ------------------------------------------------- Sprint 20 extended cuts
    _entry(
        shape="heart", aliases=["cuore", "heart cut"], family="SPECIAL_OUTLINE",
        symmetryClass="BILATERAL_ONE_AXIS",
        anchors=[*_CARDINAL, "TIP", "CLEFT", "LEFT_LOBE", "RIGHT_LOBE"],
        supportedProfiles=_FACETED_AND_CAB,
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        description=(
            "Point at -Y, cleft at +Y. Construction half-extents are normalized so the "
            "real bounding box equals the request; no commercial heart proportion is claimed."
        ),
    ),
    _entry(
        shape="radiant", aliases=["radiante", "radiant cut"], family="CLIPPED_RECTILINEAR",
        symmetryClass="BILATERAL_BOTH_AXES",
        anchors=[*_CARDINAL, "CORNER_NW", "CORNER_NE", "CORNER_SW", "CORNER_SE"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        description="Clipped-corner rectangle, shallower clip than emerald. Silhouette only.",
    ),
    _entry(
        shape="asscher", aliases=["asscher cut"], family="CLIPPED_RECTILINEAR",
        symmetryClass="BILATERAL_BOTH_AXES",
        anchors=[*_CARDINAL, "CORNER_NW", "CORNER_NE", "CORNER_SW", "CORNER_SE"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        description="Clipped-corner rectangle, deeper clip than emerald or radiant.",
    ),
    _entry(
        shape="trillion", aliases=["trilliant", "trillian", "trilliante", "triangolo brillante"],
        family="TRIANGULAR", symmetryClass="BILATERAL_ONE_AXIS",
        anchors=[*_CARDINAL, "TIP", "CORNER_SW", "CORNER_SE"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        description=(
            "Triangle with outward-bowed sides. TRILLIANT is an ALIAS, not a second "
            "canonical shape: no distinct geometry semantics were defined for it "
            "(brief section 11)."
        ),
    ),
    _entry(
        shape="baguette", aliases=["baguette cut", "rettangolo"], family="RECTILINEAR",
        symmetryClass="BILATERAL_BOTH_AXES",
        anchors=[*_CARDINAL, "CORNER_NW", "CORNER_NE", "CORNER_SW", "CORNER_SE"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        description=(
            "Plain rectangle. Distinct from EMERALD (which has clipped corners) and from "
            "PRINCESS (same geometry, different canonical identity and proportions)."
        ),
    ),
    _entry(
        shape="tapered_baguette",
        aliases=["tapered baguette", "baguette rastremata", "baguette conica"],
        family="TAPERED_QUADRILATERAL", symmetryClass="BILATERAL_ONE_AXIS",
        requiredDimensions=["length", "width", "narrowWidth", "depth"],
        anchors=[*_CARDINAL, "WIDE_END", "NARROW_END"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        description=(
            "Explicitly tapered rectangle: WIDE end at -Y, NARROW end at +Y. The taper is a "
            "required dimension, never an invented default ratio."
        ),
    ),
    _entry(
        shape="triangle", aliases=["triangolo", "triangolare", "triangular"],
        family="TRIANGULAR", symmetryClass="BILATERAL_ONE_AXIS",
        anchors=[*_CARDINAL, "TIP", "CORNER_SW", "CORNER_SE"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        description="Isosceles triangle with STRAIGHT sides — deliberately not TRILLION.",
    ),
    _entry(
        shape="trapezoid", aliases=["trapezio", "trapeze", "trapezium"],
        family="TAPERED_QUADRILATERAL", symmetryClass="BILATERAL_ONE_AXIS",
        requiredDimensions=["length", "width", "narrowWidth", "depth"],
        anchors=[*_CARDINAL, "WIDE_END", "NARROW_END"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        description=(
            "Same primitive as TAPERED_BAGUETTE, separate canonical identity: a trapezoid "
            "is typically a short accent stone rather than an elongated one."
        ),
    ),
    _entry(
        shape="lozenge", aliases=["losanga", "rombo", "rhombus"], family="POLYGONAL",
        symmetryClass="BILATERAL_BOTH_AXES", anchors=[*_CARDINAL, "TIP"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        description=(
            "Rhombus. Named LOZENGE and never 'diamond', because in JewelMind 'diamond' is "
            "a gem species and a shape ID must never collide with gem identity."
        ),
    ),
    _entry(
        shape="hexagon", aliases=["esagono", "esagonale", "hexagonal"], family="POLYGONAL",
        symmetryClass="BILATERAL_BOTH_AXES", anchors=[*_CARDINAL, "TIP"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        description=(
            "ELONGATED hexagon: regular only when the caller supplies a matching "
            "length/width ratio. Regularity is not forced."
        ),
    ),
    _entry(
        shape="kite", aliases=["aquilone", "cervo volante"], family="POLYGONAL",
        symmetryClass="BILATERAL_ONE_AXIS", anchors=[*_CARDINAL, "TIP"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        description="Kite with its widest span above center — longitudinally asymmetric.",
    ),
    _entry(
        shape="shield", aliases=["scudo", "shield cut"], family="POLYGONAL",
        symmetryClass="BILATERAL_ONE_AXIS", anchors=[*_CARDINAL, "TIP"],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        description=(
            "Flat-topped shield tapering to a point at -Y. Fully polygonal: an arc-based "
            "lower boundary overshot the requested width during prototyping. No subtypes."
        ),
    ),
    _entry(
        shape="half_moon", aliases=["half moon", "mezzaluna", "demi lune", "halfmoon"],
        family="SPECIAL_OUTLINE", symmetryClass="BILATERAL_ONE_AXIS",
        supportedProfiles=_FACETED_AND_CAB, anchors=[*_CARDINAL],
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="EXPERIMENTAL",
        description=(
            "Straight chord at -X closed by an ELLIPTICAL arc. Half of an ellipse rather "
            "than half of a circle, so the bounding box is exact at any aspect ratio."
        ),
    ),
    _entry(
        shape="pearl", aliases=["perla", "sphere", "sfera", "bead"], family="SPHERICAL",
        requiredDimensions=["diameter"], symmetryClass="RADIAL",
        supportedProfiles=["SPHERICAL_REFERENCE"],
        # Deliberately EMPTY. A sphere has no planar girdle outline, so it has
        # no outline-derived anchors, and `stone_anchors()` correctly returns
        # none. Declaring cardinal anchors here would make the registry claim a
        # fact the code cannot produce.
        anchors=[],
        prongCompatibility="UNSUPPORTED", bezelCompatibility="UNSUPPORTED",
        description=(
            "Spherical reference solid. This is GEOMETRY only: whether the stone is an "
            "actual pearl is gem identity, which arrives in Sprint 21. Near-round, drop "
            "and button pearls remain PLANNED. Settings are UNSUPPORTED because a sphere "
            "has no girdle plane for the current prong/bezel contracts to grip."
        ),
    ),
    # ------------------------------------------------------------ pseudo-shapes
    _entry(
        shape=CUSTOM_SHAPE_ID, aliases=["custom outline", "pietra personalizzata"],
        family="CUSTOM", symmetryClass="UNKNOWN",
        requiredDimensions=["outline", "depth"],
        supportedProfiles=_FACETED_AND_CAB,
        availableSourceModes=["CUSTOM_OUTLINE"], anchors=_CARDINAL,
        prongCompatibility="EXPERIMENTAL", bezelCompatibility="SUPPORTED_SOFTWARE",
        description=(
            "A stone defined by a caller-supplied outline. The escape hatch that frees the "
            "Stone System from a finite built-in shape list. Bezel is SUPPORTED_SOFTWARE "
            "because the bezel consumes the normalized outline contract directly, with no "
            "per-shape branch."
        ),
    ),
    _entry(
        shape=IMPORTED_SHAPE_ID, aliases=[], family="IMPORTED", symmetryClass="UNKNOWN",
        requiredDimensions=[], optionalDimensions=_LWD,
        supportedProfiles=_FACETED, availableSourceModes=["IMPORTED_CAD"],
        anchors=_CARDINAL, status="PARTIAL", inspectionSupported=True,
        prongCompatibility="UNSUPPORTED", bezelCompatibility="UNSUPPORTED",
        description=(
            "Externally supplied geometry. PARTIAL: B-Rep import, unit normalization, "
            "inspection and Vision all work, but setting compatibility is decided per "
            "asset from real geometry rather than granted by this registry entry."
        ),
    ),
]

STONE_SHAPE_CAPABILITIES_V2: dict[str, StoneShapeCapabilityV2] = {
    entry.shape: entry for entry in _ENTRIES
}

STONE_SOURCE_CAPABILITIES: dict[str, StoneSourceCapability] = {
    entry.sourceMode: entry
    for entry in [
        StoneSourceCapability(
            sourceMode="PARAMETRIC_REFERENCE", status="CURRENT",
            generatesRealGeometry=True, representation="PARAMETRIC",
            outlineAvailable=True, anchorsAvailable=True, settingCompatible=True,
            professionalValidationStatus="NOT_REVIEWED",
            description="A named canonical shape plus explicit dimensions.",
            knownLimitations=[
                "Reference silhouettes only — no shape models a real facet arrangement.",
            ],
        ),
        StoneSourceCapability(
            sourceMode="CUSTOM_OUTLINE", status="CURRENT",
            generatesRealGeometry=True, representation="PARAMETRIC",
            outlineAvailable=True, anchorsAvailable=True, settingCompatible=True,
            professionalValidationStatus="NOT_REVIEWED",
            description=(
                "A validated caller-supplied closed outline, extruded through the same "
                "reference-profile pipeline every native shape uses."
            ),
            knownLimitations=[
                "Concave outlines generate valid geometry but are not bezel-verified "
                "for every concavity; the Golden case covers a convex outline.",
                "Only ordered points are accepted; curve segments and SVG import are PLANNED.",
                "Anchors are limited to the five cardinal points — a custom outline has no "
                "deterministic TIP or CLEFT.",
            ],
        ),
        StoneSourceCapability(
            sourceMode="MEASURED", status="CURRENT",
            generatesRealGeometry=True, representation="PARAMETRIC",
            outlineAvailable=True, anchorsAvailable=True, settingCompatible=True,
            professionalValidationStatus="NOT_REVIEWED",
            description=(
                "A real physical stone's measurements. With dimensions only, JewelMind "
                "builds an approximation labelled MEASURED_DIMENSION_REFERENCE; with a "
                "measured outline it builds MEASURED_OUTLINE_REFERENCE."
            ),
            knownLimitations=[
                "A dimension-only reference is an approximation of the physical stone, "
                "never a model of its real surface.",
                "No measurement is ever inferred when absent.",
            ],
        ),
        StoneSourceCapability(
            sourceMode="IMPORTED_CAD", status="PARTIAL",
            generatesRealGeometry=True, representation="BREP_SOLID",
            outlineAvailable=True, anchorsAvailable=True, settingCompatible=False,
            professionalValidationStatus="NOT_REVIEWED",
            description=(
                "Externally supplied CAD or mesh geometry, normalized into the canonical "
                "stone frame with explicit declared units and recorded provenance."
            ),
            knownLimitations=[
                "PARTIAL: STEP/BREP B-Rep import is CURRENT; STL mesh import is CURRENT "
                "for inspection and Vision but exposes no B-Rep operations.",
                "Setting compatibility is decided per asset from real geometry, never "
                "granted automatically.",
                "Scan-specific processing (point clouds, decimation, hole filling) is PLANNED.",
            ],
        ),
    ]
}


def get_shape_capability(shape: str) -> StoneShapeCapabilityV2 | None:
    return STONE_SHAPE_CAPABILITIES_V2.get(shape)


def get_source_capability(mode: str) -> StoneSourceCapability | None:
    return STONE_SOURCE_CAPABILITIES.get(mode)


def current_shapes() -> list[str]:
    """Every shape with a real generator, in registry order."""

    return [
        s for s, e in STONE_SHAPE_CAPABILITIES_V2.items()
        if e.generationSupported and e.status in ("CURRENT", "PARTIAL")
    ]


def native_shapes() -> list[str]:
    """Every real named cut — excludes the `custom`/`imported` pseudo-shapes."""

    return [
        s for s in current_shapes()
        if s not in (CUSTOM_SHAPE_ID, IMPORTED_SHAPE_ID)
    ]


def alias_lookup() -> dict[str, str]:
    """Every alias mapped to its canonical shape ID (brief section 38).

    Aliases are lowercase and never duplicated across shapes; the registry
    tests assert both, so Designer can rely on an unambiguous resolution.
    """

    table: dict[str, str] = {}
    for shape, entry in STONE_SHAPE_CAPABILITIES_V2.items():
        table[shape] = shape
        for alias in entry.aliases:
            table[alias.lower()] = shape
    return table


def supports_profile(shape: str, profile: StoneReferenceProfile) -> bool:
    entry = STONE_SHAPE_CAPABILITIES_V2.get(shape)
    return bool(entry and profile in entry.supportedProfiles)


def setting_compatibility(shape: str, family: Literal["prong", "bezel"]) -> str:
    """This shape's compatibility with a Setting family (brief section 40)."""

    entry = STONE_SHAPE_CAPABILITIES_V2.get(shape)
    if entry is None:
        return "UNSUPPORTED"
    return entry.prongCompatibility if family == "prong" else entry.bezelCompatibility


def compatibility_matrix_v2() -> list[dict[str, str]]:
    """The full Stone x Setting matrix, generated from the live entries."""

    return [
        {
            "stoneShape": shape,
            "settingFamily": family,
            "status": setting_compatibility(shape, family),
        }
        for shape in STONE_SHAPE_CAPABILITIES_V2
        for family in ("prong", "bezel")
    ]
