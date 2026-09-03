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
SETTING_GEOMETRY_VERSION = "1.1.0"

#: Setting families named for architectural completeness but with NO
#: generator and NO enum membership in `SettingFamily`. Listing them here
#: documents the direction without implying capability (SETTING-GOV-005).
RESERVED_SETTING_FAMILIES: tuple[str, ...] = (
    "channel",
    "flush",
    "bar",
    "tension",
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

    supported: list[str] = []
    experimental: list[str] = []
    unsupported: list[str] = []
    for shape, entry in STONE_SHAPE_CAPABILITIES_V2.items():
        status = entry.prongCompatibility if family == "prong" else entry.bezelCompatibility
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
    ]
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
    "shared_prong_geometry": (
        "A prong serving two stones is REPRESENTABLE today — explicit positions "
        "carry `servesStoneInstanceIds`, and the assignment is reported in the "
        "result. It is not GENERATABLE against two stones, because one stone "
        "component is built per model (see the Stone Arrangement execution "
        "boundary)."
    ),
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
