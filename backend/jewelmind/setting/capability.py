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
SETTING_GEOMETRY_VERSION = "1.0.0"

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
            stoneShapesSupported=["round"],
            stoneShapesExperimental=["oval", "emerald", "cushion", "princess", "marquise", "pear"],
            stoneShapesUnsupported=[],
            stoneSourceModesSupported=["PARAMETRIC_REFERENCE_STONE"],
            seatSupport="PLANNED",
            bearingSupport="PLANNED",
            cutterSupport="PLANNED",
            professionalValidationStatus="NOT_REVIEWED",
            settingGeometryVersion=SETTING_GEOMETRY_VERSION,
            description=(
                "Cylindrical reference prongs. RADIAL placement for round (byte-identical to "
                "pre-Sprint-19); OUTLINE_CARDINAL placement for non-round shapes. No seat, "
                "bearing, or cutter geometry exists."
            ),
        ),
        SettingCapability(
            settingType="bezel",
            status="CURRENT",
            generatable=True,
            inspectable=True,
            categoryNeutral=True,
            # round and oval are the two proven cases required by the brief.
            stoneShapesSupported=["round", "oval"],
            stoneShapesExperimental=["emerald", "cushion", "princess", "marquise", "pear"],
            stoneShapesUnsupported=[],
            stoneSourceModesSupported=["PARAMETRIC_REFERENCE_STONE"],
            seatSupport="PLANNED",
            bearingSupport="PLANNED",
            cutterSupport="PLANNED",
            professionalValidationStatus="NOT_REVIEWED",
            settingGeometryVersion=SETTING_GEOMETRY_VERSION,
            description=(
                "Parametric wall built by offsetting the stone's own girdle outline, so the "
                "pipeline is outline-agnostic rather than per-shape. Wall thickness/height are "
                "preliminary software values, not professional recommendations. No seat, "
                "bearing, or cutter geometry exists."
            ),
        ),
    ]
}


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
