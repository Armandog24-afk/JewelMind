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

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = "0.1.0"

BandProfile = Literal["comfort_fit", "flat"]
StoneShape = Literal["round", "oval", "pear", "emerald", "cushion", "princess", "marquise"]
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
    """Base model for the domain schema.

    - ``extra="forbid"``: reject unknown fields so client/server drift is
      caught early.
    - ``strict=True``: reject type-coerced input — e.g. a JSON string like
      ``"2.4"`` is NOT accepted for a numeric field, even though Pydantic's
      default ("lax") mode would silently parse it. Untrusted input must
      send real JSON numbers for numeric fields. Note that widening
      int -> float (e.g. ``16`` for a ``float`` field) is still allowed in
      strict mode, since that is lossless and is exactly what a JSON number
      without a decimal point parses to.
    """

    model_config = ConfigDict(extra="forbid", strict=True)


# Every plain `float` field in this schema also sets `allow_inf_nan=False`.
# Without it, `gt=0`-style constraints are not enough: `float('inf') > 0` is
# True, so an infinite mesh tolerance or band width would otherwise sail
# straight through validation and into CadQuery, which cannot construct
# geometry from a non-finite dimension. NaN comparisons are always False,
# so an unconstrained field (no gt/lt) would silently accept NaN too.


class ProjectInfo(StrictModel):
    name: str = Field(default="Solitaire Ring", min_length=1, max_length=200)
    units: Literal["mm"] = "mm"


class JewelryInfo(StrictModel):
    category: JewelryCategory = "ring"
    style: JewelryStyle = "solitaire"


class RingSpec(StrictModel):
    sizeSystem: RingSizeSystem = "EU"
    size: float = Field(default=16, allow_inf_nan=False)
    innerDiameter: float = Field(default=17.8, allow_inf_nan=False)


BandTaperMode = Literal["NONE", "TOWARD_BOTTOM"]


class BandTaperSpec(StrictModel):
    """A MINOR, additive Sprint 17 field (see
    docs/bible/05-jdl/081-schema-versioning-and-migrations.md's MINOR
    definition) — every existing document omitting this field gets the
    default below, which is bit-identical to pre-Sprint-17 geometry.

    `mode="NONE"` means no taper: the dimension is constant all the way
    around the ring, exactly as before this Sprint. `mode="TOWARD_BOTTOM"`
    anchors the full base dimension at the head (u=0) and linearly tapers
    it down to `bottomRatio * base` at the bottom (u=0.5), symmetric on
    both shoulders. `bottomRatio` is ignored when `mode="NONE"`.
    """

    mode: BandTaperMode = "NONE"
    bottomRatio: float = Field(default=1.0, gt=0, le=1, allow_inf_nan=False)


class BandSpec(StrictModel):
    width: float = Field(default=2.4, allow_inf_nan=False)
    thickness: float = Field(default=1.8, allow_inf_nan=False)
    profile: BandProfile = "comfort_fit"
    widthTaper: BandTaperSpec = Field(default_factory=BandTaperSpec)
    thicknessTaper: BandTaperSpec = Field(default_factory=BandTaperSpec)


class StoneSpec(StrictModel):
    """A MINOR, additive Sprint 18 field set (see
    docs/bible/05-jdl/081-schema-versioning-and-migrations.md's MINOR
    definition) — `shape` gains 6 new enum members and `length`/`width`/
    `orientation` are new optional fields, so every existing `round`
    document that only ever set `diameter`/`depth` keeps validating
    exactly as before.

    `diameter` is the round-only public dimension, unchanged since Sprint
    2. `length`/`width` are required only when `shape != "round"` — see
    docs/bible/20-stone/564-stone-dimension-model.md for the LENGTH
    (major horizontal dimension) / WIDTH (minor horizontal dimension) /
    DEPTH semantics and their exact local-axis mapping per shape.
    `orientation` is a rotation in degrees around the stone's local
    vertical axis, default 0 — see 565-stone-coordinate-and-orientation.md.
    """

    shape: StoneShape = "round"
    diameter: float | None = Field(default=6.5, allow_inf_nan=False)
    length: float | None = Field(default=None, allow_inf_nan=False)
    width: float | None = Field(default=None, allow_inf_nan=False)
    depth: float = Field(default=4.0, allow_inf_nan=False)
    orientation: float = Field(default=0.0, allow_inf_nan=False)

    @model_validator(mode="after")
    def _check_shape_dimensions(self) -> StoneSpec:
        if self.shape == "round":
            if self.diameter is None:
                raise ValueError("stone.diameter is required when stone.shape is 'round'")
        else:
            if self.length is None or self.width is None:
                raise ValueError(
                    f"stone.length and stone.width are both required when stone.shape is '{self.shape}'"
                )
        return self


class SettingSpec(StrictModel):
    type: SettingType = "prong"
    # Not a Literal[4, 6]: an out-of-set value must surface as a structured
    # JM-PRONG-001 validation result, not a raw pydantic parse error.
    prongCount: int = Field(default=6)
    prongDiameter: float = Field(default=1.1, allow_inf_nan=False)
    prongHeight: float = Field(default=4.8, allow_inf_nan=False)
    basketHeight: float = Field(default=3.5, allow_inf_nan=False)


class MaterialSpec(StrictModel):
    metal: MetalType = "yellow_gold_18k"


class ManufacturingSpec(StrictModel):
    method: ManufacturingMethod = "lost_wax_casting"


class PreviewSpec(StrictModel):
    meshTolerance: float = Field(default=0.1, gt=0, allow_inf_nan=False)
    angularTolerance: float = Field(default=0.2, gt=0, allow_inf_nan=False)


class JewelryDefinition(StrictModel):
    # Only the currently supported schema version is accepted. A definition
    # saved by a future/older incompatible version of JewelMind must fail
    # loudly here rather than being silently (mis)interpreted.
    schemaVersion: Literal["0.1.0"] = SCHEMA_VERSION
    project: ProjectInfo = Field(default_factory=ProjectInfo)
    jewelry: JewelryInfo = Field(default_factory=JewelryInfo)
    ring: RingSpec = Field(default_factory=RingSpec)
    band: BandSpec = Field(default_factory=BandSpec)
    stone: StoneSpec = Field(default_factory=StoneSpec)
    setting: SettingSpec = Field(default_factory=SettingSpec)
    material: MaterialSpec = Field(default_factory=MaterialSpec)
    manufacturing: ManufacturingSpec = Field(default_factory=ManufacturingSpec)
    preview: PreviewSpec = Field(default_factory=PreviewSpec)
