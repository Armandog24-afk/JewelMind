"""Canonical JewelryDefinition schema.

This module is the single source of truth for the shape of a JewelMind
jewelry definition on the backend. The frontend keeps a structurally
equivalent TypeScript type (see shared/types/jewelry-definition.ts), but the
backend is always the authoritative validator before generation or export.

All lengths are in millimeters. See docs/geometry-conventions.md for the
coordinate convention used when this definition is turned into geometry.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "0.1.0"

BandProfile = Literal["comfort_fit", "flat"]
StoneShape = Literal["round"]
SettingType = Literal["prong"]
MetalType = Literal[
    "yellow_gold_18k",
    "white_gold_18k",
    "rose_gold_18k",
    "platinum",
    "silver",
]
ManufacturingMethod = Literal["lost_wax_casting", "direct_resin_printing"]
RingSizeSystem = Literal["EU"]
JewelryCategory = Literal["ring"]
JewelryStyle = Literal["solitaire"]


class StrictModel(BaseModel):
    """Base model: reject unknown fields so client/server drift is caught early."""

    model_config = ConfigDict(extra="forbid")


class ProjectInfo(StrictModel):
    name: str = Field(default="Solitaire Ring", min_length=1, max_length=200)
    units: Literal["mm"] = "mm"


class JewelryInfo(StrictModel):
    category: JewelryCategory = "ring"
    style: JewelryStyle = "solitaire"


class RingSpec(StrictModel):
    sizeSystem: RingSizeSystem = "EU"
    size: float = Field(default=16)
    innerDiameter: float = Field(default=17.8)


class BandSpec(StrictModel):
    width: float = Field(default=2.4)
    thickness: float = Field(default=1.8)
    profile: BandProfile = "comfort_fit"


class StoneSpec(StrictModel):
    shape: StoneShape = "round"
    diameter: float = Field(default=6.5)
    depth: float = Field(default=4.0)


class SettingSpec(StrictModel):
    type: SettingType = "prong"
    # Not a Literal[4, 6]: an out-of-set value must surface as a structured
    # JM-PRONG-001 validation result, not a raw pydantic parse error.
    prongCount: int = Field(default=6)
    prongDiameter: float = Field(default=1.1)
    prongHeight: float = Field(default=4.8)
    basketHeight: float = Field(default=3.5)


class MaterialSpec(StrictModel):
    metal: MetalType = "yellow_gold_18k"


class ManufacturingSpec(StrictModel):
    method: ManufacturingMethod = "lost_wax_casting"


class PreviewSpec(StrictModel):
    meshTolerance: float = Field(default=0.1, gt=0)
    angularTolerance: float = Field(default=0.2, gt=0)


class JewelryDefinition(StrictModel):
    schemaVersion: str = SCHEMA_VERSION
    project: ProjectInfo = Field(default_factory=ProjectInfo)
    jewelry: JewelryInfo = Field(default_factory=JewelryInfo)
    ring: RingSpec = Field(default_factory=RingSpec)
    band: BandSpec = Field(default_factory=BandSpec)
    stone: StoneSpec = Field(default_factory=StoneSpec)
    setting: SettingSpec = Field(default_factory=SettingSpec)
    material: MaterialSpec = Field(default_factory=MaterialSpec)
    manufacturing: ManufacturingSpec = Field(default_factory=ManufacturingSpec)
    preview: PreviewSpec = Field(default_factory=PreviewSpec)
