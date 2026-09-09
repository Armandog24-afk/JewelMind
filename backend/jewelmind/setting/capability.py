"""The real Setting capability registry and Stone×Setting compatibility
matrix (brief sections 8/43; SETTING-GOV-005/006/011/015).

Two things are kept rigorously separate here:

- **generatable** — a real registered generator produces real CAD geometry.
- **professionalValidationStatus** — whether a qualified human reviewed it.

A generatable setting is never, by that fact, professionally validated
(SETTING-GOV-007). Every entry below is `NOT_REVIEWED`, and must stay so
until a real `ValidationRecord` with real evidence exists.

Mirrored — never hand-duplicated — at specs/setting/v1/setting-registry.json.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, ConfigDict

from jewelmind.setting.models import CompatibilityStatus, SettingFamily

CapabilityStatus = Literal["CURRENT", "PARTIAL", "PLANNED", "BLOCKED", "OUT_OF_SCOPE"]
ProfessionalValidationStatus = Literal["NOT_REVIEWED", "IN_REVIEW", "VALIDATED"]

#: Version of the setting-construction algorithms. Bumped on any MAJOR
#: change to how a setting family's geometry is built.
#:
#: 1.1.0 (Sprint 23): prong style and head architecture dispatch were added.
#: MINOR rather than MAJOR because every default-path solid is byte-identical —
#: `ROUND_PRONG` and `BASKET` reproduce the previous construction exactly, which
#: is what left all 39 Golden baselines untouched.
#:
#: 1.2.0 (Sprint 27): four new setting families (channel, bar, flush, tension),
#: the PARTIAL bezel variant, the OPEN_GALLERY head architecture and the
#: SHARED_PRONG retention strategy. MINOR for the same reason: every addition is
#: reached only by a document that asks for it, `BEZEL_FULL` and `BASKET` still
#: reproduce their previous constructions exactly, and no existing Golden
#: baseline moves.
SETTING_GEOMETRY_VERSION = "1.2.0"

#: Setting families named for architectural completeness but with NO
#: generator and NO enum membership in `SettingFamily`. Listing them here
#: documents the direction without implying capability (SETTING-GOV-005).
#:
#: Sprint 27 REMOVED `channel`, `flush`, `bar` and `tension` from this tuple
#: because each now has a real registered generator. `bead` and `pave` are
#: deliberately still here and will stay: repeated small-stone retention is not
#: a setting family of its own, it is `setting/retention.py`'s builders driven
#: by a pavé field, and adding a second route to it would be the duplicate
#: engine Sprint 26 refused.
RESERVED_SETTING_FAMILIES: tuple[str, ...] = (
    "bead",
    "pave",
    "custom",
)

#: Head architectures named for completeness but with NO builder and NO
#: membership in `HeadArchitecture` (Sprint 23).
#:
#: `trellis` is the one that matters: it needs swept curved rails the current
#: pipeline cannot build robustly, and a "simplified trellis" that was really
#: four bent prongs would be a different structure wearing the name. The
#: mapped value is the real reason, not a roadmap slogan.
RESERVED_HEAD_ARCHITECTURES: dict[str, str] = {
    "trellis": (
        "Interwoven curved rails require a swept solid along a 3D spline. The "
        "current pipeline builds solids of revolution and lofts reliably; a swept "
        "trellis is not yet verifiable, so no builder exists."
    ),
    "cathedral": (
        "A cathedral head is defined by how the SHANK rises to meet it, which is "
        "shank geometry rather than head geometry. It belongs to a Shank "
        "milestone, not to this registry."
    ),
    "compass_point": (
        "Compass-point heads position prongs at the stone's own anchors. The "
        "anchors exist (Stone v2); anchor-driven placement does not."
    ),
    "double_gallery": (
        "Two stacked galleries need a second head instance per setting, which the "
        "one-head-per-setting contract does not express."
    ),
}

#: Support elements named for completeness with NO builder: rails between
#: heads, and the cutter/bearing tooling a setter would actually use.
RESERVED_SUPPORT_ELEMENTS: dict[str, str] = {
    "rail": (
        "A rail joins two or more heads, so it requires multi-head geometry. One "
        "setting builds one head today."
    ),
    "bearing": (
        "A bearing is a cut shoulder inside a seat, sized by a setter. No sourced "
        "professional geometry exists for one, so none is invented."
    ),
    "cutter": (
        "Cutter geometry is manufacturing tooling, not part of the jewelry model. "
        "It would belong to a manufacturing-preparation milestone."
    ),
}

#: Which existing Stone-registry compatibility axis each setting family's
#: support is read from (Sprint 27).
#:
#: STATED RATHER THAN GUESSED, and each choice follows from what the family's
#: geometry actually consumes:
#:
#: - `flush` offsets the stone's own GIRDLE OUTLINE, exactly as the bezel does,
#:   so it inherits the bezel axis. A shape with no usable planar outline
#:   genuinely cannot be flush set.
#: - `channel`, `bar` and `tension` consume only the stone's MEASURED BOUNDING
#:   BOX, which is a weaker requirement than either existing axis. They are
#:   nevertheless read from the prong axis rather than declared supported for
#:   every shape: claiming support for 21 shapes on the strength of a weaker
#:   requirement would be marking capability CURRENT without tests behind it,
#:   which STONEV2-GOV-007 forbids. The wider compatibility is a real,
#:   documented headroom, not a claim.
#:
#: The Stone System stays the authority on what a shape IS; this table only
#: says which of its verdicts a family reads.
_FAMILY_COMPATIBILITY_BASIS: dict[str, str] = {
    "prong": "prong",
    "bezel": "bezel",
    "flush": "bezel",
    "channel": "prong",
    "bar": "prong",
    "tension": "prong",
}


def _stone_shapes_by_compatibility(family: str) -> tuple[list[str], list[str], list[str]]:
    """Split every known stone shape into supported / experimental / unsupported.

    DERIVED from the Stone System's own registry rather than hand-listed here.
    Sprint 19 hard-coded the seven Stone v1 shapes in this module, and Sprint 20
    immediately proved why that is a drift hazard: fourteen new shapes plus the
    `custom` pseudo-shape appeared, and a bezel over a custom outline was
    refused as "not supported" even though the geometry pipeline built it
    correctly. Deriving the split means a new shape cannot be forgotten here.

    Stone remains the authority on what a shape IS; Setting remains the
    authority on what it can DO with one. This function only reads the former.
    """

    from jewelmind.stone.capability import STONE_SHAPE_CAPABILITIES_V2

    basis = _FAMILY_COMPATIBILITY_BASIS.get(family, "bezel")
    supported: list[str] = []
    experimental: list[str] = []
    unsupported: list[str] = []
    for shape, entry in STONE_SHAPE_CAPABILITIES_V2.items():
        status = entry.prongCompatibility if basis == "prong" else entry.bezelCompatibility
        if status == "SUPPORTED_SOFTWARE":
            supported.append(shape)
        elif status == "EXPERIMENTAL":
            experimental.append(shape)
        else:
            unsupported.append(shape)
    return supported, experimental, unsupported


ALL_STONE_SHAPES: tuple[str, ...] = (
    "round",
    "oval",
    "pear",
    "emerald",
    "cushion",
    "princess",
    "marquise",
)


class SettingCapability(BaseModel):
    model_config = ConfigDict(extra="forbid")

    settingType: SettingFamily
    status: CapabilityStatus
    generatable: bool
    inspectable: bool
    categoryNeutral: bool
    stoneShapesSupported: list[str]
    stoneShapesExperimental: list[str]
    stoneShapesUnsupported: list[str]
    stoneSourceModesSupported: list[str]
    seatSupport: CapabilityStatus
    bearingSupport: CapabilityStatus
    cutterSupport: CapabilityStatus
    professionalValidationStatus: ProfessionalValidationStatus
    settingGeometryVersion: str
    description: str


SETTING_CAPABILITIES: dict[str, SettingCapability] = {
    entry.settingType: entry
    for entry in [
        SettingCapability(
            settingType="prong",
            status="CURRENT",
            generatable=True,
            inspectable=True,
            categoryNeutral=True,
            # Only round's placement was designed for its shape. Every
            # non-round shape generates, but via a provisional strategy.
            stoneShapesSupported=_stone_shapes_by_compatibility("prong")[0],
            stoneShapesExperimental=_stone_shapes_by_compatibility("prong")[1],
            stoneShapesUnsupported=_stone_shapes_by_compatibility("prong")[2],
            stoneSourceModesSupported=[
                "PARAMETRIC_REFERENCE", "CUSTOM_OUTLINE", "MEASURED",
            ],
            seatSupport="PARTIAL",
            bearingSupport="PLANNED",
            cutterSupport="PLANNED",
            professionalValidationStatus="NOT_REVIEWED",
            settingGeometryVersion=SETTING_GEOMETRY_VERSION,
            description=(
                "Cylindrical reference prongs. RADIAL placement for round (byte-identical to "
                "pre-Sprint-19); OUTLINE_CARDINAL placement for every other outline, including "
                "custom ones. Placement is not tip-, corner- or anchor-aware. No seat, "
                "bearing, or cutter geometry exists. Sprint 23: opt-in "
                "REFERENCE_SEAT relief cuts the stone volume out of the metal; "
                "that is relief, not a cut seat with a bearing shoulder."
            ),
        ),
        SettingCapability(
            settingType="bezel",
            status="CURRENT",
            generatable=True,
            inspectable=True,
            categoryNeutral=True,
            # round and oval are the two proven cases required by the brief.
            stoneShapesSupported=_stone_shapes_by_compatibility("bezel")[0],
            stoneShapesExperimental=_stone_shapes_by_compatibility("bezel")[1],
            stoneShapesUnsupported=_stone_shapes_by_compatibility("bezel")[2],
            stoneSourceModesSupported=[
                "PARAMETRIC_REFERENCE", "CUSTOM_OUTLINE", "MEASURED",
            ],
            seatSupport="PARTIAL",
            bearingSupport="PLANNED",
            cutterSupport="PLANNED",
            professionalValidationStatus="NOT_REVIEWED",
            settingGeometryVersion=SETTING_GEOMETRY_VERSION,
            description=(
                "Parametric wall built by offsetting the stone's own girdle outline, so the "
                "pipeline is outline-agnostic rather than per-shape — which is why a custom "
                "outline needs no bezel code of its own. Wall thickness/height are preliminary "
                "software values, not professional recommendations. Sprint 23: opt-in "
                "REFERENCE_SEAT relief is available; no bearing or cutter geometry "
                "exists."
            ),
        ),
        SettingCapability(
            settingType="channel",
            status="CURRENT",
            generatable=True,
            inspectable=True,
            categoryNeutral=True,
            stoneShapesSupported=_stone_shapes_by_compatibility("channel")[0],
            stoneShapesExperimental=_stone_shapes_by_compatibility("channel")[1],
            stoneShapesUnsupported=_stone_shapes_by_compatibility("channel")[2],
            stoneSourceModesSupported=[
                "PARAMETRIC_REFERENCE", "CUSTOM_OUTLINE", "MEASURED",
            ],
            seatSupport="PARTIAL",
            bearingSupport="PLANNED",
            cutterSupport="PLANNED",
            professionalValidationStatus="NOT_REVIEWED",
            settingGeometryVersion=SETTING_GEOMETRY_VERSION,
            description=(
                "Two parallel walls with the stones between them, running along a "
                "stated axis in the stone's own horizontal frame. Real prisms, with "
                "optional end caps. The run's length and clear width default to the "
                "stone's own measured extents, so a channel-set solitaire needs no "
                "parameters; a longer run is stated, because only the document knows "
                "how many stones the row carries. The stones themselves come from the "
                "Stone Arrangement Engine — this family builds the walls and records "
                "which instances they hold, never where those instances are. Wall "
                "thickness and height are construction parameters; no minimum is "
                "enforced because no sourced professional minimum exists."
            ),
        ),
        SettingCapability(
            settingType="bar",
            status="CURRENT",
            generatable=True,
            inspectable=True,
            categoryNeutral=True,
            stoneShapesSupported=_stone_shapes_by_compatibility("bar")[0],
            stoneShapesExperimental=_stone_shapes_by_compatibility("bar")[1],
            stoneShapesUnsupported=_stone_shapes_by_compatibility("bar")[2],
            stoneSourceModesSupported=[
                "PARAMETRIC_REFERENCE", "CUSTOM_OUTLINE", "MEASURED",
            ],
            seatSupport="PARTIAL",
            bearingSupport="PLANNED",
            cutterSupport="PLANNED",
            professionalValidationStatus="NOT_REVIEWED",
            settingGeometryVersion=SETTING_GEOMETRY_VERSION,
            description=(
                "Transverse bars across a run, with the stones between adjacent bars. "
                "One component carrying every bar, each bar's own offset reported in "
                "its metadata. Bar spacing and length default to the stone's own "
                "measured extents, which places one bar on each side of a single "
                "stone. Retention only: the stones are the arrangement's, and no bar "
                "position is ever derived from a stone position or the reverse."
            ),
        ),
        SettingCapability(
            settingType="flush",
            status="CURRENT",
            generatable=True,
            inspectable=True,
            categoryNeutral=True,
            stoneShapesSupported=_stone_shapes_by_compatibility("flush")[0],
            stoneShapesExperimental=_stone_shapes_by_compatibility("flush")[1],
            stoneShapesUnsupported=_stone_shapes_by_compatibility("flush")[2],
            stoneSourceModesSupported=[
                "PARAMETRIC_REFERENCE", "CUSTOM_OUTLINE", "MEASURED",
            ],
            # The recess IS the seat relief for this family, which is why seat
            # support is CURRENT here and PARTIAL elsewhere: for a flush setting
            # the cut is not an optional extra, it is half the geometry.
            seatSupport="CURRENT",
            bearingSupport="PLANNED",
            cutterSupport="PLANNED",
            professionalValidationStatus="NOT_REVIEWED",
            settingGeometryVersion=SETTING_GEOMETRY_VERSION,
            description=(
                "A solid collar built by offsetting the stone's own girdle outline — "
                "the bezel's verified offset pipeline, reused rather than "
                "reimplemented — extruded from the attachment plane to a rim above "
                "the girdle, with the stone's own solid then cut out of it. The cut "
                "is the existing REFERENCE_SEAT relief, so the stone is a cutting "
                "tool and never becomes production metal. Relief is a PRECONDITION "
                "of this family rather than an option: without it the collar buries "
                "the stone, so the generator refuses and JM-SETTING-010 reports it. "
                "The rim height must stay below the stone's measured crown height, "
                "which is a geometric precondition and not a setting depth."
            ),
        ),
        SettingCapability(
            settingType="tension",
            # PARTIAL, NOT CURRENT, and the reason is not a missing solid: the
            # geometry is complete and real. A tension setting's entire FUNCTION
            # is structural, this project models none of that behaviour, and
            # marking the family CURRENT would read as a claim that it does.
            status="PARTIAL",
            generatable=True,
            inspectable=True,
            categoryNeutral=True,
            stoneShapesSupported=_stone_shapes_by_compatibility("tension")[0],
            stoneShapesExperimental=_stone_shapes_by_compatibility("tension")[1],
            stoneShapesUnsupported=_stone_shapes_by_compatibility("tension")[2],
            stoneSourceModesSupported=[
                "PARAMETRIC_REFERENCE", "CUSTOM_OUTLINE", "MEASURED",
            ],
            seatSupport="PARTIAL",
            bearingSupport="PLANNED",
            cutterSupport="PLANNED",
            professionalValidationStatus="NOT_REVIEWED",
            settingGeometryVersion=SETTING_GEOMETRY_VERSION,
            description=(
                "Two opposing supports, one on each side of the stone along a stated "
                "grip axis, each reaching inward past the stone's edge so the seat "
                "relief leaves a real groove. Real solids. WHAT IS NOT MODELLED: the "
                "elastic response of the metal, the force the supports apply, whether "
                "the stone would be held, and whether the configuration survives "
                "load or wear. Those require material properties and a validated "
                "engineering model that do not exist here, so no threshold is "
                "invented and professional review is REQUIRED before this geometry "
                "means anything structural."
            ),
        ),
    ]
}

#: Setting families whose geometry depends on a judgment this project has no
#: evidence for, mapped to what specifically is unmodelled.
#:
#: SEPARATE FROM `professionalValidationStatus`, which every family shares
#: (`NOT_REVIEWED` — nobody has reviewed anything). This says a qualified human
#: MUST look before the geometry can be read as a functional claim, which is a
#: different statement from "no one has looked yet".
PROFESSIONAL_REVIEW_REQUIRED: dict[str, str] = {
    "tension": (
        "A tension setting holds its stone by the elastic force two opposing "
        "shoulders apply to it. Nothing here computes that force, the metal's "
        "spring-back, or whether the stone would be retained under load, wear "
        "or impact. The generated supports are geometry, not a structural "
        "statement."
    ),
}


class ProngStyleCapability(BaseModel):
    """One prong body style and what is true about it (Sprint 23)."""

    model_config = ConfigDict(extra="forbid")

    style: str
    status: CapabilityStatus
    generatable: bool
    #: True only for the style that reproduces the pre-Sprint-23 cylinder.
    preservesLegacyGeometry: bool
    professionalValidationStatus: ProfessionalValidationStatus
    description: str


PRONG_STYLE_CAPABILITIES: dict[str, ProngStyleCapability] = {
    entry.style: entry
    for entry in [
        ProngStyleCapability(
            style="ROUND_PRONG",
            status="CURRENT",
            generatable=True,
            preservesLegacyGeometry=True,
            professionalValidationStatus="NOT_REVIEWED",
            description=(
                "The pre-Sprint-23 straight cylinder, unchanged and still the "
                "default. `tipRatio` is accepted and ignored, because honouring it "
                "would silently change every existing design's geometry."
            ),
        ),
        ProngStyleCapability(
            style="TAPERED_PRONG",
            status="CURRENT",
            generatable=True,
            preservesLegacyGeometry=False,
            professionalValidationStatus="NOT_REVIEWED",
            description=(
                "A cone frustum: full radius at the base, `tipRatio` of it at the "
                "tip. A software reference taper, not a measured claw profile."
            ),
        ),
        ProngStyleCapability(
            style="CLAW_PRONG",
            status="CURRENT",
            generatable=True,
            preservesLegacyGeometry=False,
            professionalValidationStatus="NOT_REVIEWED",
            description=(
                "A cylindrical shaft fused to a tapered head, so the taper is "
                "concentrated near the tip. Distinct from TAPERED_PRONG, which "
                "tapers over its whole length."
            ),
        ),
        ProngStyleCapability(
            style="V_PRONG",
            status="CURRENT",
            generatable=True,
            preservesLegacyGeometry=False,
            professionalValidationStatus="NOT_REVIEWED",
            description=(
                "A cylinder with a V notch cut into its tip, the notch opening "
                "outward along the prong's own radial direction. The notch angle "
                "and depth are construction parameters; no claim is made that a "
                "stone tip would seat correctly in one."
            ),
        ),
    ]
}

#: Prong-level capabilities that are representable but not generatable, or not
#: representable at all. Kept beside the styles so a reader sees both halves.
RESERVED_PRONG_CAPABILITIES: dict[str, str] = {
    "anchor_driven_placement": (
        "Placing prongs at a stone's own anchors (tip, cleft, corners). The "
        "anchors exist in Stone v2; consuming them needs a placement strategy "
        "that does not yet exist, so OUTLINE_CARDINAL remains the non-round "
        "default."
    ),
    "custom_prong_profile": (
        "An arbitrary swept prong cross-section. EXPLICIT positions are the "
        "escape hatch for layout; an arbitrary profile is not expressible."
    ),
}


class HeadArchitectureCapability(BaseModel):
    """One head architecture and what is true about it (Sprint 23)."""

    model_config = ConfigDict(extra="forbid")

    architecture: str
    status: CapabilityStatus
    generatable: bool
    preservesLegacyGeometry: bool
    #: Whether the built solid is one connected body. Every current
    #: architecture is, and a builder that produced more raises rather than
    #: shipping a floating head.
    singleSolid: bool
    requiredParameters: list[str]
    professionalValidationStatus: ProfessionalValidationStatus
    description: str


HEAD_ARCHITECTURE_CAPABILITIES: dict[str, HeadArchitectureCapability] = {
    entry.architecture: entry
    for entry in [
        HeadArchitectureCapability(
            architecture="BASKET",
            status="CURRENT",
            generatable=True,
            preservesLegacyGeometry=True,
            singleSolid=True,
            requiredParameters=[],
            professionalValidationStatus="NOT_REVIEWED",
            description=(
                "The pre-Sprint-23 hollow cylindrical wall, reproduced "
                "character-for-character and still the default. The Ring adapter "
                "passes the original bore expression so the solid is bit-identical."
            ),
        ),
        HeadArchitectureCapability(
            architecture="PEG_HEAD",
            status="CURRENT",
            generatable=True,
            preservesLegacyGeometry=False,
            singleSolid=True,
            requiredParameters=["pegDiameterMm", "pegHeightMm"],
            professionalValidationStatus="NOT_REVIEWED",
            description=(
                "A basket wall on a narrower solid peg, joined by a conical flare. "
                "The flare is not decoration: a peg narrower than the wall's bore "
                "never touches it, and stacking the two produced two disconnected "
                "solids until the flare was added."
            ),
        ),
        HeadArchitectureCapability(
            architecture="MARTINI",
            status="CURRENT",
            generatable=True,
            preservesLegacyGeometry=False,
            singleSolid=True,
            requiredParameters=[],
            professionalValidationStatus="NOT_REVIEWED",
            description=(
                "A hollow conical wall, wide at the girdle and narrow at the base. "
                "A software reference silhouette; no commercial martini proportion "
                "is claimed."
            ),
        ),
        HeadArchitectureCapability(
            architecture="TULIP",
            status="CURRENT",
            generatable=True,
            preservesLegacyGeometry=False,
            singleSolid=True,
            requiredParameters=[],
            professionalValidationStatus="NOT_REVIEWED",
            description=(
                "A concave flare approximated by stacked cone frusta following a "
                "quadratic. Section count and curve are construction choices; no "
                "commercial tulip proportion is claimed."
            ),
        ),
        HeadArchitectureCapability(
            architecture="OPEN_GALLERY",
            status="CURRENT",
            generatable=True,
            preservesLegacyGeometry=False,
            singleSolid=True,
            requiredParameters=[],
            professionalValidationStatus="NOT_REVIEWED",
            description=(
                "The basket wall with evenly spaced windows pierced through it, cut "
                "from the basket's own solid rather than built separately. The "
                "windows span only the middle fraction of the wall's height so a "
                "continuous rim survives at the top and the bottom — a construction "
                "correctness requirement, since a full-height window would sever the "
                "wall into disconnected pillars and a head must be one connected "
                "body. Deliberately NOT called azure: azure work is arbitrary "
                "decorative piercing, and this is the parametric subset of it."
            ),
        ),
    ]
}


class SeatCapability(BaseModel):
    """Stone-seat relief support (Sprint 23)."""

    model_config = ConfigDict(extra="forbid")

    mode: str
    status: CapabilityStatus
    generatable: bool
    #: The kernel operation performed. Load-bearing: a CUT is why relief can
    #: exist at all without breaking the stone/metal separation contract.
    operation: str
    professionalValidationStatus: ProfessionalValidationStatus
    description: str


SEAT_CAPABILITIES: dict[str, SeatCapability] = {
    entry.mode: entry
    for entry in [
        SeatCapability(
            mode="NONE",
            status="CURRENT",
            generatable=True,
            operation="NONE",
            professionalValidationStatus="NOT_REVIEWED",
            description=(
                "No relief, and the default. Stone and metal overlap exactly as "
                "they did before Sprint 23."
            ),
        ),
        SeatCapability(
            mode="REFERENCE_SEAT",
            status="CURRENT",
            generatable=True,
            operation="CUT_STONE_FROM_METAL",
            professionalValidationStatus="NOT_REVIEWED",
            description=(
                "The stone solid is used as a CUTTING TOOL against production "
                "metal, so metal no longer occupies the stone's volume. Never a "
                "fuse, so LAW-006 holds. REFERENCE relief only: it is not a cut "
                "seat with a bearing shoulder and no claim is made that a stone "
                "would sit correctly in it."
            ),
        ),
    ]
}


def prong_styles() -> tuple[str, ...]:
    """Styles with a real builder. Derived from the registry, never restated."""

    return tuple(
        sorted(
            name
            for name, entry in PRONG_STYLE_CAPABILITIES.items()
            if entry.generatable
        )
    )


def head_architecture_names() -> tuple[str, ...]:
    return tuple(
        sorted(
            name
            for name, entry in HEAD_ARCHITECTURE_CAPABILITIES.items()
            if entry.generatable
        )
    )


def get_setting_capability(setting_type: str) -> SettingCapability | None:
    return SETTING_CAPABILITIES.get(setting_type)


def compatibility_status(setting_type: str, stone_shape: str) -> CompatibilityStatus:
    """The real Stone x Setting compatibility status (brief section 43).

    Raises nothing — an unknown combination reports `UNSUPPORTED` rather
    than guessing, and the generator turns that into an explicit error
    (SETTING-GOV-012).
    """

    capability = SETTING_CAPABILITIES.get(setting_type)
    if capability is None:
        return "UNSUPPORTED"
    if stone_shape in capability.stoneShapesSupported:
        return "SUPPORTED_SOFTWARE"
    if stone_shape in capability.stoneShapesExperimental:
        return "EXPERIMENTAL"
    return "UNSUPPORTED"


#: The pipeline stages every setting mode declares a status for (brief §32).
#:
#: THE POINT OF ENUMERATING THEM is that "supported" is not one question. A mode
#: can be expressible in JDL, resolvable by the compiler, buildable by Atlas and
#: still absent from Studio — and a registry that answered only "SUPPORTED"
#: would hide which. Sprint 22 established the same discipline with
#: representable/resolvable/generatable; this extends it across the whole
#: pipeline so capability drift has nowhere to hide.
SETTING_MODE_PIPELINE_STAGES: tuple[str, ...] = (
    "schema",
    "parser",
    "validator",
    "compiler",
    "geometry",
    "inspection",
    "export",
    "vision",
    "studio",
    "designer",
    "conversation",
)


class SettingModeCapability(BaseModel):
    """One setting mode and everything true about it (Sprint 27).

    THE SINGLE SOURCE OF TRUTH for the extended taxonomy, and deliberately not a
    fifth registry beside the four that already exist: `setting_modes()` DERIVES
    each row's `settingGeometry` from the live builder registries rather than
    declaring it, and a bidirectional test asserts every builder has a row and
    every geometry-claiming row has a builder. A mode cannot claim a solid that
    is not built, and a builder cannot exist unnamed.

    FOUR INDEPENDENT AXES, kept apart for the reason FAMILY-GOV and PAVE-GOV
    already record: collapsing `stoneGeometry` and `settingGeometry` would turn
    "the stones exist" into "the design is complete".
    """

    model_config = ConfigDict(extra="forbid")

    settingModeId: str
    name: str
    axis: str
    family: str

    #: The `setting.type` value that selects this mode, for PRIMARY modes.
    #: `None` for HEAD and RETENTION modes, which are selected by their own
    #: fields — stating `None` is how the registry says "not chosen by type".
    settingType: str | None

    modeVersion: str

    representable: bool
    compilable: bool
    stoneGeometry: bool
    settingGeometry: bool

    status: CapabilityStatus
    pipelineCoverage: dict[str, CapabilityStatus]

    requiredParameters: list[str]

    #: Whether this mode can hold more than the design's own stone.
    multiStone: bool

    professionalValidationStatus: ProfessionalValidationStatus

    #: Whether a qualified human must review before this geometry can be read as
    #: a functional claim. Distinct from `professionalValidationStatus`: that
    #: says whether anyone HAS looked, this says whether anyone MUST.
    professionalReviewRequirement: Literal["NOT_REQUIRED", "REQUIRED"]

    #: Terms Designer and Conversation recognise for this mode. Read BY those
    #: layers rather than restated in them, so a spoken request and the registry
    #: cannot name different things.
    designerTerms: list[str]

    description: str


def _all_current() -> dict[str, CapabilityStatus]:
    """Full pipeline coverage, for a mode that traverses every stage."""

    return {stage: "CURRENT" for stage in SETTING_MODE_PIPELINE_STAGES}


def _coverage(**overrides: CapabilityStatus) -> dict[str, CapabilityStatus]:
    """Full coverage with named exceptions.

    Written as overrides rather than eleven values per row so a reader's eye
    goes straight to what is NOT current, which is the only part that carries
    information.
    """

    coverage = _all_current()
    for stage, status in overrides.items():
        if stage not in coverage:
            raise KeyError(
                f"{stage!r} is not a setting-mode pipeline stage. Known stages: "
                f"{list(SETTING_MODE_PIPELINE_STAGES)}."
            )
        coverage[stage] = status
    return coverage


def _mode_has_builder(mode_id: str) -> bool:
    """Whether a real builder exists for a mode, read from the LIVE registries.

    THE ANTI-DRIFT MECHANISM of this whole registry. Every other field below is
    a declaration; this one is a measurement, taken from the same dictionaries
    the generators dispatch through. A mode whose builder is deleted stops
    claiming geometry on the next import rather than on the next code review.

    Imported inside the function, not at module scope: `prong_styles.py`,
    `head.py`, `retention.py` and every family generator import THIS module, so
    a module-level import would be circular — the discipline
    `jewelry_category/dispatch.py` adopted after a real package-init cycle.
    """

    from jewelmind.setting.dispatch import setting_generators
    from jewelmind.setting.head import head_builders
    from jewelmind.setting.modes import (
        head_architecture_for_mode,
        mode_axis,
        prong_style_for_mode,
        retention_strategy_for_mode,
    )
    from jewelmind.setting.prong_styles import prong_solid_builders
    from jewelmind.setting.retention import retention_builders

    axis = mode_axis(mode_id)
    if axis == "HEAD":
        return head_architecture_for_mode(mode_id) in head_builders()
    if axis == "RETENTION":
        return retention_strategy_for_mode(mode_id) in retention_builders()

    from jewelmind.setting.modes import PRIMARY_FAMILY_SETTING_TYPE, mode_family

    setting_type = PRIMARY_FAMILY_SETTING_TYPE[mode_family(mode_id)]
    if setting_type not in setting_generators():
        return False
    style = prong_style_for_mode(mode_id)
    if style is not None:
        # A prong mode additionally needs its BODY builder, not only the family
        # generator: the family could dispatch while the style it names had no
        # solid, which would silently build a round prong for a claw request.
        return style in prong_solid_builders()
    return True


#: Everything a mode row declares, minus the derived `settingGeometry`.
#:
#: Kept as plain data rather than as constructed models so the derivation in
#: `setting_modes()` is the ONLY place a `SettingModeCapability` is built, and a
#: row cannot be added that skips it.
_MODE_ROWS: tuple[dict[str, object], ...] = (
    {
        "settingModeId": "PRONG_ROUND",
        "name": "Round prong",
        "requiredParameters": [],
        "multiStone": False,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["prong", "prongs", "griffe", "griffa", "claw prong set"],
        "description": (
            "The pre-Sprint-23 straight cylinder and still the default for every "
            "prong setting. Count, diameter and height are parameters, so a four- "
            "and a six-prong setting are one mode rather than two."
        ),
    },
    {
        "settingModeId": "PRONG_TAPERED",
        "name": "Tapered prong",
        "requiredParameters": [],
        "multiStone": False,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["tapered prong", "griffe rastremate"],
        "description": (
            "A cone frustum: full radius at the base, `prongTipRatio` of it at the "
            "tip. A software reference taper, not a measured claw profile."
        ),
    },
    {
        "settingModeId": "PRONG_CLAW",
        "name": "Claw prong",
        "requiredParameters": [],
        "multiStone": False,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["claw prong", "claw", "griffe artiglio"],
        "description": (
            "A cylindrical shaft fused to a tapered head, so the taper is "
            "concentrated near the tip."
        ),
    },
    {
        "settingModeId": "PRONG_V",
        "name": "V prong",
        "requiredParameters": [],
        "multiStone": False,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["v prong", "v-prong", "griffe a v"],
        "description": (
            "A cylinder with a V notch cut into its tip. The notch angle and depth "
            "are construction parameters; no claim is made that a stone tip would "
            "seat correctly in one."
        ),
    },
    {
        "settingModeId": "PRONG_SHARED",
        "name": "Shared prong",
        "requiredParameters": ["positions"],
        "multiStone": True,
        # PARTIAL: the metal is real and the association is recorded, but the
        # POSITION is stated by the document rather than derived from the two
        # stones' geometry. Nothing verifies that a shared prong actually
        # reaches both stones it names — that is a geometric fact, and Geometry
        # Inspection reports distances rather than this registry asserting them.
        "status": "PARTIAL",
        "coverage": _coverage(studio="PLANNED", designer="PLANNED", conversation="PLANNED"),
        "review": "NOT_REQUIRED",
        "terms": ["shared prong", "shared prongs", "griffe condivise"],
        "description": (
            "A prong serving two or more stones, expressed through EXPLICIT prong "
            "positions carrying `servesStoneInstanceIds`. The prongs are real solids "
            "and the assignment is reported per component. What is NOT provided: "
            "derivation of the shared position from the two stones' own geometry, so "
            "whether a shared prong reaches both stones it names is a geometric fact "
            "for inspection rather than a guarantee. No interface authors explicit "
            "positions yet, which is why Studio, Designer and Conversation are "
            "PLANNED for this mode."
        ),
    },
    {
        "settingModeId": "BEZEL_FULL",
        "name": "Full bezel",
        "requiredParameters": [],
        "multiStone": False,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["bezel", "full bezel", "castone", "montatura a castone"],
        "description": (
            "The continuous wall built by offsetting the stone's own girdle outline. "
            "Unchanged from Sprint 19 and preserved byte-identically, which is why it "
            "remains the bezel default."
        ),
    },
    {
        "settingModeId": "BEZEL_PARTIAL",
        "name": "Partial bezel",
        "requiredParameters": [],
        "multiStone": False,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["partial bezel", "half bezel", "castone parziale"],
        "description": (
            "The full bezel's own wall with evenly spaced angular openings cut "
            "through it, so a partial bezel can never be a different wall from the "
            "full one it derives from. Legitimately several solids — n openings leave "
            "n arcs, joined through the head below — and that solid count is reported "
            "rather than repaired."
        ),
    },
    {
        "settingModeId": "CHANNEL_LINEAR",
        "name": "Linear channel",
        "requiredParameters": ["channelWallThickness", "channelWallHeight"],
        "multiStone": True,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["channel", "channel setting", "incastonatura a canale", "canale"],
        "description": (
            "Two parallel walls with the stones between them, with optional end caps. "
            "Extents default to the stone's own measured box, so the single-stone "
            "case needs no parameters. Multi-stone by declaration: a longer run holds "
            "the arrangement's instances and records their ids, without computing a "
            "single placement."
        ),
    },
    {
        "settingModeId": "BAR_TRANSVERSE",
        "name": "Transverse bar",
        "requiredParameters": ["barCount", "barWidth", "barHeight"],
        "multiStone": True,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["bar setting", "bar", "incastonatura a barrette", "barrette"],
        "description": (
            "Transverse bars across a run, with the stones between adjacent bars. One "
            "component carrying every bar, with each bar's own offset reported. "
            "Spacing and length default to the stone's own measured extents."
        ),
    },
    {
        "settingModeId": "FLUSH_GYPSY",
        "name": "Flush / gypsy",
        "requiredParameters": ["flushCollarWidth", "flushRimHeight", "seatMode"],
        "multiStone": False,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["flush setting", "flush", "gypsy", "gypsy setting", "incastonatura a filo"],
        "description": (
            "A solid collar offset from the stone's girdle outline with the stone's "
            "own solid cut out of it. Requires REFERENCE_SEAT relief, because without "
            "the cut the collar buries the stone — a geometric precondition, refused "
            "by the generator and reported by JM-SETTING-010. The rim must stay below "
            "the stone's measured crown height."
        ),
    },
    {
        "settingModeId": "TENSION_OPPOSED",
        "name": "Opposed tension",
        "requiredParameters": [
            "tensionPadWidth",
            "tensionPadThickness",
            "tensionPadDepth",
            "tensionGripHeight",
        ],
        "multiStone": False,
        # PARTIAL with complete geometry: see the family capability row and
        # `tension.py`'s docstring. The solids are real; the structural claim
        # that makes a tension setting a tension setting is absent.
        "status": "PARTIAL",
        "coverage": _all_current(),
        "review": "REQUIRED",
        "terms": ["tension setting", "tension", "incastonatura a tensione"],
        "description": (
            "Two opposing supports with the stone between them, each reaching inward "
            "past the stone's edge so the seat relief leaves a real groove. The "
            "geometry is complete and the structural behaviour is NOT MODELLED: no "
            "force, no spring-back, no retention claim. Professional review is "
            "required before this geometry means anything functional."
        ),
    },
    {
        "settingModeId": "HEAD_BASKET",
        "name": "Basket head",
        "requiredParameters": [],
        "multiStone": False,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["basket", "basket head", "cestello"],
        "description": (
            "The pre-Sprint-23 hollow cylindrical wall, reproduced "
            "character-for-character and still the default."
        ),
    },
    {
        "settingModeId": "HEAD_PEG",
        "name": "Peg head",
        "requiredParameters": ["pegDiameter", "pegHeight"],
        "multiStone": False,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["peg head", "peg", "testa a perno"],
        "description": (
            "A basket wall on a narrower solid peg, joined by a conical flare. The "
            "flare is structural, not decorative: without it the peg never touches "
            "the bore and the head is two disconnected solids."
        ),
    },
    {
        "settingModeId": "HEAD_MARTINI",
        "name": "Martini head",
        "requiredParameters": [],
        "multiStone": False,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["martini", "martini head", "testa martini"],
        "description": (
            "A hollow conical wall, wide at the girdle and narrow at the base. A "
            "software reference silhouette; no commercial martini proportion is "
            "claimed."
        ),
    },
    {
        "settingModeId": "HEAD_TULIP",
        "name": "Tulip head",
        "requiredParameters": [],
        "multiStone": False,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["tulip", "tulip head", "testa tulipano", "tulipano"],
        "description": (
            "A concave flare approximated by stacked cone frusta following a "
            "quadratic. Section count and curve are construction choices."
        ),
    },
    {
        "settingModeId": "HEAD_OPEN_GALLERY",
        "name": "Open gallery head",
        "requiredParameters": [],
        "multiStone": False,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["open gallery", "gallery", "open head", "galleria aperta"],
        "description": (
            "The basket wall with evenly spaced windows pierced through it, cut from "
            "the basket's own solid. Windows span only the middle of the height so a "
            "continuous rim survives and the head stays one connected body. "
            "Deliberately not called azure."
        ),
    },
    {
        "settingModeId": "RETENTION_BEAD",
        "name": "Bead",
        "requiredParameters": ["beadRadiusMm"],
        "multiStone": True,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["bead", "beads", "grain setting", "granatura"],
        "description": (
            "One bead per lattice corner of each stone, individually. A hemisphere "
            "raised at the corner — named honestly as a sphere, because a real bead's "
            "shape depends on the graining tool and the hand."
        ),
    },
    {
        "settingModeId": "RETENTION_SHARED_BEAD",
        "name": "Shared bead",
        "requiredParameters": ["beadRadiusMm"],
        "multiStone": True,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["shared bead", "shared beads", "pave condiviso", "grani condivisi"],
        "description": (
            "One bead per lattice corner, shared by every stone touching it — "
            "genuinely fewer beads, which is the point of the technique. Anchors are "
            "derived in the surface's own parameters so neighbouring stones agree "
            "about where a corner is."
        ),
    },
    {
        "settingModeId": "RETENTION_MICRO_PRONG",
        "name": "Micro prong",
        "requiredParameters": ["prongHeightMm"],
        "multiStone": True,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["micro prong", "micro prongs", "micro griffe"],
        "description": (
            "A small cylinder normal to the host surface at each corner, capped with "
            "a hemisphere, built individually per stone."
        ),
    },
    {
        "settingModeId": "RETENTION_SHARED_PRONG",
        "name": "Shared micro prong",
        "requiredParameters": ["prongHeightMm"],
        "multiStone": True,
        "status": "CURRENT",
        "coverage": _all_current(),
        "review": "NOT_REQUIRED",
        "terms": ["shared micro prong", "shared prong retention", "micro griffe condivise"],
        "description": (
            "A micro prong at each shared lattice corner, serving every stone that "
            "touches it. Sharing is a property of the ANCHOR SET, not of the solid, "
            "which is why this maps to the same builder as MICRO_PRONG — exactly as "
            "BEAD and SHARED_BEAD already do."
        ),
    },
)


@lru_cache(maxsize=1)
def setting_modes() -> dict[str, SettingModeCapability]:
    """The extended setting-mode registry.

    CACHED AND BUILT LAZILY rather than declared as a module constant, because
    `settingGeometry` is measured from the live builder registries and those
    modules import this one. The same discipline `head_builders()` and
    `setting_generators()` already follow.
    """

    from jewelmind.setting.modes import (
        PRIMARY_FAMILY_SETTING_TYPE,
        SETTING_MODE_TAXONOMY_VERSION,
        mode_axis,
        mode_family,
    )

    modes: dict[str, SettingModeCapability] = {}
    for row in _MODE_ROWS:
        mode_id = str(row["settingModeId"])
        axis = mode_axis(mode_id)
        family = mode_family(mode_id)
        has_builder = _mode_has_builder(mode_id)
        modes[mode_id] = SettingModeCapability(
            settingModeId=mode_id,
            name=str(row["name"]),
            axis=axis,
            family=family,
            settingType=(
                PRIMARY_FAMILY_SETTING_TYPE[family] if axis == "PRIMARY" else None
            ),
            modeVersion=SETTING_MODE_TAXONOMY_VERSION,
            # A mode in this registry is expressible and compilable by
            # construction: it is a member of the closed `SettingModeId`
            # literal, so a document can state it and the resolver accepts it.
            representable=True,
            compilable=True,
            # Stones exist for every mode: a PRIMARY or HEAD mode is built for
            # the design's own stone, and a RETENTION mode for a pavé field
            # whose stones the arrangement resolves.
            stoneGeometry=True,
            # THE DERIVED AXIS. Measured, never declared.
            settingGeometry=has_builder,
            status=row["status"],  # type: ignore[arg-type]
            pipelineCoverage=row["coverage"],  # type: ignore[arg-type]
            requiredParameters=list(row["requiredParameters"]),  # type: ignore[arg-type]
            multiStone=bool(row["multiStone"]),
            professionalValidationStatus="NOT_REVIEWED",
            professionalReviewRequirement=row["review"],  # type: ignore[arg-type]
            designerTerms=list(row["terms"]),  # type: ignore[arg-type]
            description=str(row["description"]),
        )
    return modes


def get_setting_mode(mode_id: str) -> SettingModeCapability | None:
    return setting_modes().get(mode_id)


def setting_mode_ids(axis: str | None = None) -> tuple[str, ...]:
    """Every registered mode id, optionally filtered to one axis. Sorted."""

    return tuple(
        sorted(
            mode_id
            for mode_id, entry in setting_modes().items()
            if axis is None or entry.axis == axis
        )
    )


def designer_mode_terms() -> dict[str, str]:
    """Every recognised term mapped to its mode id.

    DERIVED FROM THE REGISTRY so Designer and Conversation cannot recognise a
    term for a mode that does not exist, or miss one that does. A duplicate term
    across two modes raises: an ambiguous term must be resolved in the registry,
    not silently resolved to whichever row was built last.
    """

    terms: dict[str, str] = {}
    for mode_id, entry in setting_modes().items():
        for term in entry.designerTerms:
            key = term.lower()
            if key in terms and terms[key] != mode_id:
                raise ValueError(
                    f"Designer term {term!r} is claimed by both {terms[key]!r} "
                    f"and {mode_id!r}. An ambiguous term must be resolved here, "
                    "never by whichever registry row happened to be built last."
                )
            terms[key] = mode_id
    return terms


def compatibility_matrix() -> list[dict[str, object]]:
    """The full cross-product, generated rather than hand-maintained, so it
    cannot drift from `SETTING_CAPABILITIES`."""

    rows: list[dict[str, object]] = []
    for setting_type in sorted(SETTING_CAPABILITIES):
        for shape in ALL_STONE_SHAPES:
            rows.append(
                {
                    "settingType": setting_type,
                    "stoneShape": shape,
                    "compatibility": compatibility_status(setting_type, shape),
                    "professionalValidation": SETTING_CAPABILITIES[
                        setting_type
                    ].professionalValidationStatus,
                }
            )
    return rows
