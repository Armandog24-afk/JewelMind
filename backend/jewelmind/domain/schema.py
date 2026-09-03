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

from jewelmind.arrangement.models import ArrangementDefinition

# The Stone and Gem systems own their canonical vocabularies; importing them
# here keeps one source of truth instead of hand-maintained duplicates. Safe
# against circular imports because both packages' `__init__.py` deliberately
# import nothing, and both `models` modules depend on no other JewelMind
# module — see each package's `__init__.py` for why that is load-bearing.
from jewelmind.gem.models import (
    GEM_ID_PATTERN,
    MAX_GEM_ID_LENGTH,
    GemConfidence,
    GemOrigin,
    GemTreatmentDisclosure,
    GemTreatmentStatus,
    GemTreatmentType,
)
from jewelmind.stone.models import (
    DeclaredUnit,
    StoneReferenceProfile,
    StoneSourceMode,
)

SCHEMA_VERSION = "0.1.0"

BandProfile = Literal["comfort_fit", "flat"]
#: Canonical stone CUT identities (never gem species — STONEV2-GOV-008).
#:
#: The first seven are Sprint 18's set and are unchanged. The rest are Sprint
#: 20's extended cuts. `custom` and `imported` are pseudo-shapes used when a
#: stone genuinely has no named cut; they are real members so that every
#: consumer can look a stone's capabilities up uniformly, and they are never
#: offered to a user as cuts to choose from.
StoneShape = Literal[
    # Stone v1 (Sprint 18)
    "round", "oval", "pear", "emerald", "cushion", "princess", "marquise",
    # Stone v2 (Sprint 20) extended cuts
    "heart", "radiant", "asscher", "trillion", "baguette", "tapered_baguette",
    "triangle", "trapezoid", "lozenge", "hexagon", "kite", "shield",
    "half_moon", "pearl",
    # Pseudo-shapes for non-native sources
    "custom", "imported",
]

#: Shapes whose single horizontal dimension is a diameter rather than a
#: length/width pair. `pearl` joins `round` here because a sphere has one
#: horizontal size, not two.
_ROUND_LIKE_SHAPES: frozenset[str] = frozenset({"round", "pearl"})

#: Shapes that require an explicit `narrowWidth`.
_TAPERED_SHAPES: frozenset[str] = frozenset({"tapered_baguette", "trapezoid"})

SettingType = Literal["prong", "bezel"]
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


class JdlGemTreatment(StrictModel):
    """One treatment claim about this stone (brief section 7).

    JewelMind records the claim and who made it. It never decides whether a
    treatment must be disclosed, whether it is stable, or whether it affects
    durability — all of which need professional evidence this project does not
    have.
    """

    treatment: GemTreatmentType
    status: GemTreatmentStatus = "PRESENT"
    disclosure: GemTreatmentDisclosure = "USER_DECLARED"
    confidence: GemConfidence = "UNKNOWN"
    note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def _other_requires_a_note(self) -> JdlGemTreatment:
        if self.treatment == "OTHER" and not (self.note or "").strip():
            raise ValueError(
                "stone.gem.treatments[].note is required when treatment is 'OTHER'"
            )
        return self


class JdlGemIdentity(StrictModel):
    """What gem THIS stone is (brief sections 3/4/17).

    Deliberately separate from every geometry field. A round stone is not
    automatically a diamond, and the same `StoneSpec` is reusable with any gem —
    which is why this is its own object rather than a `stone.material` string.

    `gemId` references the canonical registry
    (`backend/jewelmind/gem/registry.py`). IDs are language-independent and
    constrained so one can never become a filesystem path or a shell argument.

    Absent entirely on a legacy document, which normalizes to `unknown` — never
    to diamond (brief section 18).
    """

    gemId: str = Field(pattern=GEM_ID_PATTERN, max_length=MAX_GEM_ID_LENGTH)

    #: The ACTUAL origin of this stone, independent of treatment. Not a boolean:
    #: a stone may be natural AND treated, or synthetic AND untreated.
    origin: GemOrigin = "UNKNOWN"

    #: An EMPTY list means no treatment is RECORDED — not that the stone is
    #: untreated. To assert that, record a treatment with `status: NOT_PRESENT`.
    treatments: list[JdlGemTreatment] = Field(default_factory=list, max_length=20)

    #: Overrides the registry entry's default appearance, so a pale sapphire can
    #: look pale while still being a sapphire.
    visualProfileId: str | None = Field(
        default=None, pattern=GEM_ID_PATTERN, max_length=MAX_GEM_ID_LENGTH
    )

    #: Required for, and only valid for, `gemId == "custom"`.
    customName: str | None = Field(default=None, max_length=120)

    note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def _custom_name_matches_custom_gem(self) -> JdlGemIdentity:
        if self.gemId == "custom":
            if not (self.customName or "").strip():
                raise ValueError(
                    "stone.gem.customName is required when gemId is 'custom'"
                )
        elif self.customName is not None:
            raise ValueError(
                "stone.gem.customName is only valid when gemId is 'custom'"
            )
        return self


class JdlOutlinePoint(StrictModel):
    """One 2D point of a custom stone outline, in the stone's local frame."""

    x: float = Field(allow_inf_nan=False)
    y: float = Field(allow_inf_nan=False)


class JdlCustomOutline(StrictModel):
    """A caller-supplied closed stone outline (brief section 23).

    Ordered points only. No JDL representation may ever carry an expression,
    script or function body (JDL's no-executable-code rule), and a point list
    is the representation that cannot.

    The outline is closed implicitly; the first point must not be repeated at
    the end. Semantic validation (self-intersection, zero area, degenerate
    segments) lives in `jewelmind/stone/outline_validation.py`, not here —
    structural and semantic validation stay separate layers.
    """

    points: list[JdlOutlinePoint] = Field(min_length=3, max_length=10_000)
    unit: DeclaredUnit = "mm"
    label: str | None = Field(default=None, max_length=200)


class JdlStoneMeasurement(StrictModel):
    """Provenance for a physically measured stone (brief section 28).

    Every field is optional and caller-supplied. JewelMind never fills one in:
    an absent measurement source is an honest absence, not a value to invent
    (STONEV2-GOV-006).
    """

    measurementSource: str | None = Field(default=None, max_length=500)
    measurementDate: str | None = Field(default=None, max_length=64)
    operatorNote: str | None = Field(default=None, max_length=500)


class JdlImportedStoneAsset(StrictModel):
    """Reference to externally supplied stone geometry (brief sections 30/31).

    `assetHash` is a content hash, never a filesystem path: a path in a design
    document would leak an internal server location into every export and
    review package (FOUNDRY-GOV-011).

    `declaredUnit` is required rather than inferred, because no format
    JewelMind reads carries a reliable, universally-populated unit, and
    guessing one silently rescales a real physical object.
    """

    assetHash: str = Field(min_length=8, max_length=128)
    assetName: str | None = Field(default=None, max_length=255)
    declaredUnit: DeclaredUnit


class StoneSpec(StrictModel):
    """A MINOR, additive Sprint 20 field set, on top of Sprint 18's.

    Sprint 18 added 6 shape enum members plus `length`/`width`/`orientation`.
    Sprint 20 adds 14 further shape members and the `source`/`profile`/
    `narrowWidth`/`customOutline`/`measurement`/`importedAsset` fields. Every
    new field is optional with a default that reproduces pre-Sprint-20
    behaviour exactly, so an existing document — whether it set only
    `diameter`/`depth` or a Sprint 18 `length`/`width` pair — keeps validating
    AND keeps generating identical geometry (brief sections 53/70).

    `diameter` is the round-only public dimension, unchanged since Sprint 2.
    `length`/`width` are required for a named non-round cut. See
    docs/bible/20-stone/564-stone-dimension-model.md for the LENGTH (major
    horizontal dimension) / WIDTH (minor horizontal dimension) / DEPTH
    semantics, and docs/bible/22-stone-v2/stone-source-architecture.md for how
    `source` selects which of those dimension rules applies.

    IMPORTANT — `shape` is a CUT, never a GEM SPECIES (STONEV2-GOV-008). The
    member `emerald` is the clipped-corner rectangular outline; the gem species
    emerald is an entirely separate concept arriving in Sprint 21. That is also
    why the rhombus member is named `lozenge` and not `diamond`.
    """

    shape: StoneShape = "round"
    diameter: float | None = Field(default=6.5, allow_inf_nan=False)
    length: float | None = Field(default=None, allow_inf_nan=False)
    width: float | None = Field(default=None, allow_inf_nan=False)
    depth: float = Field(default=4.0, allow_inf_nan=False)
    orientation: float = Field(default=0.0, allow_inf_nan=False)

    #: The narrow-end width of a tapered shape. A real required dimension for
    #: `tapered_baguette`/`trapezoid` rather than an invented default ratio
    #: (brief section 13).
    narrowWidth: float | None = Field(default=None, allow_inf_nan=False)

    #: Where this stone's geometry comes from (brief section 3).
    source: StoneSourceMode = "PARAMETRIC_REFERENCE"

    #: The 3D reference profile applied to the outline (brief section 36).
    #: Independent of `shape`, which is what avoids `OVAL_CABOCHON`-style
    #: compound enum members.
    profile: StoneReferenceProfile = "FACETED_REFERENCE"

    customOutline: JdlCustomOutline | None = None
    measurement: JdlStoneMeasurement | None = None
    importedAsset: JdlImportedStoneAsset | None = None

    #: The gem this stone is made of (Sprint 21). Absent on every document
    #: written before Sprint 21, which normalizes to `unknown` — never to
    #: diamond, because the MVP having used a diamond-like stone is not
    #: evidence about any particular design's intent (brief section 18).
    #:
    #: Deliberately NOT a geometry field: `geometry_hash()` excludes it, so
    #: changing Diamond -> Sapphire does not invalidate the stone's geometry.
    gem: JdlGemIdentity | None = None

    @model_validator(mode="after")
    def _check_shape_dimensions(self) -> StoneSpec:
        # Source-specific structural requirements. Semantic checks (outline
        # geometry, importable asset) belong to the Stone System and Forge.
        if self.source == "CUSTOM_OUTLINE":
            if self.customOutline is None:
                raise ValueError(
                    "stone.customOutline is required when stone.source is 'CUSTOM_OUTLINE'"
                )
            return self

        if self.source == "IMPORTED_CAD":
            if self.importedAsset is None:
                raise ValueError(
                    "stone.importedAsset is required when stone.source is 'IMPORTED_CAD'"
                )
            return self

        # PARAMETRIC_REFERENCE and MEASURED both describe a named cut with
        # explicit dimensions, so they share the same dimension rules.
        if self.shape in _ROUND_LIKE_SHAPES:
            if self.diameter is None:
                raise ValueError(
                    f"stone.diameter is required when stone.shape is '{self.shape}'"
                )
        else:
            if self.length is None or self.width is None:
                raise ValueError(
                    f"stone.length and stone.width are both required when stone.shape is '{self.shape}'"
                )

        if self.shape in _TAPERED_SHAPES:
            if self.narrowWidth is None:
                raise ValueError(
                    f"stone.narrowWidth is required when stone.shape is '{self.shape}'"
                )
            if self.width is not None and self.narrowWidth > self.width:
                raise ValueError(
                    f"stone.narrowWidth ({self.narrowWidth}) cannot exceed stone.width "
                    f"({self.width}) — width is the WIDE end of a tapered shape"
                )

        return self


class SettingSpec(StrictModel):
    """A MINOR, additive Sprint 19 change (see
    docs/bible/05-jdl/081-schema-versioning-and-migrations.md's MINOR
    definition) — `type` gains the `bezel` enum member and two optional
    bezel fields are added, so every existing prong document keeps
    validating and generating exactly as before.

    The prong fields keep their defaults and are therefore never *required*
    for a bezel setting; they are simply unread. Likewise the bezel fields
    are unread for a prong setting. Sprint 19 deliberately did NOT split
    this into a discriminated union at the JDL layer: that would be a
    breaking change to a published schema for no capability gain. The
    discriminated model exists one layer in, as
    `setting/models.py::ProngSettingDefinition` / `BezelSettingDefinition`,
    with `ring/setting_adapter.py` as the compatibility adapter (brief
    section 30).

    `bezelWallThickness`/`bezelWallHeight` defaults are **PRELIMINARY
    SOFTWARE VALUES**, in the same class as `band.width = 2.4` — deliberate,
    configurable software choices chosen to produce robust geometry. They
    are NOT professional recommendations and must never be described as
    such (SETTING-GOV-010).
    """

    type: SettingType = "prong"
    # Not a Literal[4, 6]: an out-of-set value must surface as a structured
    # JM-PRONG-001 validation result, not a raw pydantic parse error.
    prongCount: int = Field(default=6)
    prongDiameter: float = Field(default=1.1, allow_inf_nan=False)
    prongHeight: float = Field(default=4.8, allow_inf_nan=False)
    basketHeight: float = Field(default=3.5, allow_inf_nan=False)
    bezelWallThickness: float = Field(default=0.6, allow_inf_nan=False)
    bezelWallHeight: float = Field(default=2.5, allow_inf_nan=False)


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

    #: Multiple stone occurrences and their relationships (Sprint 22).
    #:
    #: NULLABLE AND ABSENT BY DEFAULT, which is a compatibility decision rather
    #: than an oversight. Every pre-Sprint-22 document has no arrangement, and
    #: defaulting this to a one-instance arrangement would give all of them an
    #: arrangement they never declared — changing their canonical JSON and
    #: therefore their `definitionHash`, and breaking every stored hash, Golden
    #: baseline and test vector in the repository. `None` means "single-stone
    #: design", and behaves exactly as before.
    #:
    #: Carried as the real `ArrangementDefinition` rather than a `Jdl*` mirror;
    #: see that model's docstring for why. `schemaVersion` stays `0.1.0`: an
    #: optional additive field is backward compatible, the same judgment
    #: Sprint 21 made for `stone.gem`.
    arrangement: ArrangementDefinition | None = None
