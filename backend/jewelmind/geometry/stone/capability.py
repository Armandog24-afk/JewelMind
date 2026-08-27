"""The real Stone System capability registry (STONE-GOV-014, brief
sections 11/54) — distinguishes stone-generation capability from Setting
compatibility (STONE-GOV-009/brief section 27: a shape can be
`generatable` while its `settingCompatibility` stays `EXPERIMENTAL`), so
documentation, Designer, and Studio can never advertise a capability the
code doesn't actually have. Mirrored, not hand-duplicated, at
specs/stone/v1/shape-registry.json.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from jewelmind.domain.schema import StoneShape

SettingCompatibility = Literal["SUPPORTED", "EXPERIMENTAL", "UNSUPPORTED"]
SymmetryClass = Literal[
    "RADIAL",
    "ELONGATED_SMOOTH",
    "RECTILINEAR_ANGULAR",
    "ROUNDED_RECTILINEAR",
    "ASYMMETRIC",
]

#: Version of the reference-geometry construction algorithm — bumped on any
#: MAJOR change to how a shape's outline/loft is built (mirrors
#: `geometry/shank/builder.py::SECTION_COUNT`'s versioning discipline).
REFERENCE_GEOMETRY_VERSION = "1.0.0"


class StoneShapeCapability(BaseModel):
    model_config = ConfigDict(extra="forbid")

    shape: StoneShape
    status: Literal["current", "planned"]
    generationSupported: bool
    jdlSupported: bool
    inspectionSupported: bool
    visionSupported: bool
    currentSettingCompatibility: SettingCompatibility
    requiredDimensions: list[str]
    symmetryClass: SymmetryClass
    referenceGeometryVersion: str
    description: str


STONE_SHAPE_CAPABILITIES: dict[str, StoneShapeCapability] = {
    entry.shape: entry
    for entry in [
        StoneShapeCapability(
            shape="round",
            status="current",
            generationSupported=True,
            jdlSupported=True,
            inspectionSupported=True,
            visionSupported=True,
            currentSettingCompatibility="SUPPORTED",
            requiredDimensions=["diameter", "depth"],
            symmetryClass="RADIAL",
            referenceGeometryVersion=REFERENCE_GEOMETRY_VERSION,
            description="Byte-identical pre-Sprint-18 lofted round-brilliant-style reference.",
        ),
        StoneShapeCapability(
            shape="oval",
            status="current",
            generationSupported=True,
            jdlSupported=True,
            inspectionSupported=True,
            visionSupported=True,
            currentSettingCompatibility="EXPERIMENTAL",
            requiredDimensions=["length", "width", "depth"],
            symmetryClass="ELONGATED_SMOOTH",
            referenceGeometryVersion=REFERENCE_GEOMETRY_VERSION,
            description=(
                "Elliptical outline, real CAD loft. Current prong placement is generic/circular, "
                "not shape-optimized."
            ),
        ),
        StoneShapeCapability(
            shape="marquise",
            status="current",
            generationSupported=True,
            jdlSupported=True,
            inspectionSupported=True,
            visionSupported=True,
            currentSettingCompatibility="EXPERIMENTAL",
            requiredDimensions=["length", "width", "depth"],
            symmetryClass="ELONGATED_SMOOTH",
            referenceGeometryVersion=REFERENCE_GEOMETRY_VERSION,
            description=(
                "Two-arc pointed lens outline. Current prong placement does not cluster prongs at the tips."
            ),
        ),
        StoneShapeCapability(
            shape="pear",
            status="current",
            generationSupported=True,
            jdlSupported=True,
            inspectionSupported=True,
            visionSupported=True,
            currentSettingCompatibility="EXPERIMENTAL",
            requiredDimensions=["length", "width", "depth"],
            symmetryClass="ASYMMETRIC",
            referenceGeometryVersion=REFERENCE_GEOMETRY_VERSION,
            description=(
                "One pointed tip, one rounded end. Current prong placement is generic/circular, "
                "not tip-aware."
            ),
        ),
        StoneShapeCapability(
            shape="emerald",
            status="current",
            generationSupported=True,
            jdlSupported=True,
            inspectionSupported=True,
            visionSupported=True,
            currentSettingCompatibility="EXPERIMENTAL",
            requiredDimensions=["length", "width", "depth"],
            symmetryClass="RECTILINEAR_ANGULAR",
            referenceGeometryVersion=REFERENCE_GEOMETRY_VERSION,
            description=(
                "Clipped-corner rectangular outline. Current prong placement is generic/circular, "
                "not corner-aware."
            ),
        ),
        StoneShapeCapability(
            shape="princess",
            status="current",
            generationSupported=True,
            jdlSupported=True,
            inspectionSupported=True,
            visionSupported=True,
            currentSettingCompatibility="EXPERIMENTAL",
            requiredDimensions=["length", "width", "depth"],
            symmetryClass="RECTILINEAR_ANGULAR",
            referenceGeometryVersion=REFERENCE_GEOMETRY_VERSION,
            description=(
                "Plain rectangular outline. Current prong placement is generic/circular, "
                "not corner-aware."
            ),
        ),
        StoneShapeCapability(
            shape="cushion",
            status="current",
            generationSupported=True,
            jdlSupported=True,
            inspectionSupported=True,
            visionSupported=True,
            currentSettingCompatibility="EXPERIMENTAL",
            requiredDimensions=["length", "width", "depth"],
            symmetryClass="ROUNDED_RECTILINEAR",
            referenceGeometryVersion=REFERENCE_GEOMETRY_VERSION,
            description=(
                "Rounded-rectangle outline. Current prong placement is generic/circular, "
                "not corner-aware."
            ),
        ),
    ]
}


def get_stone_shape_capability(shape: str) -> StoneShapeCapability | None:
    return STONE_SHAPE_CAPABILITIES.get(shape)
