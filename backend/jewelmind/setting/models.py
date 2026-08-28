"""Category-neutral Setting System domain models (brief sections 7/20/21).

Every model here is kernel-neutral: no field holds a `cadquery.Shape`,
`Workplane`, or OCP object, so Forge, Studio, Designer, and any future
jewelry category can depend on these contracts without importing CadQuery.
Actual geometry objects live only inside the Atlas-layer generators
(`prong.py`, `bezel.py`) and on the `GeneratedComponent`s they return.

Nothing here imports `jewelmind.ring` (SETTING-GOV-001).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

#: Setting families with a real, registered generator. Future/reserved
#: families (CHANNEL, FLUSH, BAR, TENSION, BEAD, PAVE, CUSTOM) are
#: deliberately NOT members of this literal — a closed enum whose every
#: member is implemented, per SETTING-GOV-005/006. See
#: `capability.py::RESERVED_SETTING_FAMILIES` for the reserved names.
SettingFamily = Literal["prong", "bezel"]

#: How prong positions are derived from the stone. `RADIAL` is the
#: pre-Sprint-19 behaviour (evenly spaced angles on a circle) and remains
#: correct for a radially symmetric stone. `OUTLINE_CARDINAL` places
#: prongs at the stone outline's cardinal extremes, which is what makes
#: placement genuinely shape-aware (SETTING-GOV-008).
ProngPlacementStrategy = Literal["RADIAL", "OUTLINE_CARDINAL"]

#: Only the cylindrical reference prong is implemented. CLAW, V_PRONG,
#: SHARED_PRONG and CUSTOM_PRONG are reserved names (Sprint 23 territory),
#: not members here.
ProngStyle = Literal["ROUND_PRONG"]

#: Where a bezel wall's vertical extent is anchored.
BezelVerticalReference = Literal["GIRDLE"]

#: How the bezel path is derived from the stone outline.
BezelOutlineOffsetMode = Literal["CONSTANT_OFFSET"]

CompatibilityStatus = Literal["SUPPORTED_SOFTWARE", "EXPERIMENTAL", "UNSUPPORTED"]


class SettingModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class StoneSettingReference(SettingModel):
    """The kernel-neutral facts a Setting is allowed to consume about one
    stone (brief section 20). Built by `stone_interface.py` from a real
    generated stone component — never by reaching into Stone builder
    internals.

    A Setting may read these; it may never redefine stone geometry
    (SETTING-GOV-003).
    """

    stoneId: str
    shape: str
    lengthMm: float
    widthMm: float
    depthMm: float
    orientationDeg: float
    #: Z of the stone's girdle plane — the reference plane a setting grips at.
    girdlePlaneZMm: float
    centerXMm: float
    centerYMm: float
    #: Real axis-aligned bounding box of the generated stone solid.
    boundingBoxMinMm: tuple[float, float, float]
    boundingBoxMaxMm: tuple[float, float, float]
    #: True when the stone is bilaterally symmetric about BOTH horizontal
    #: midplanes. False for `pear`. Lets a placement strategy refuse to
    #: assume symmetry it does not have (SETTING-GOV-008).
    isBilaterallySymmetric: bool
    #: Signed local-Y direction the stone's tip points, for pointed
    #: asymmetric shapes. `None` when the shape has no distinguished tip.
    tipDirectionY: float | None = None


class SettingAttachmentInterface(SettingModel):
    """The generic, category-neutral handoff between a Setting and whatever
    structure incorporates it (brief section 21).

    A RingHead consumes this today; a future PendantBody or EarringBody
    consumes the same contract. The Setting never learns which one it is
    (SETTING-GOV-014).
    """

    #: Z of the plane the setting attaches down onto (for a ring, the top
    #: of the band). Supplied BY the category integration, never computed
    #: from ring fields inside Setting.
    attachmentPlaneZMm: float
    #: How far setting geometry sinks past the attachment plane so a
    #: boolean union produces genuine 3D overlap rather than a tangent
    #: touch. A kernel/boolean-robustness value, not a jewelry threshold.
    embedMm: float
    #: Vertical distance from the attachment plane up to the stone's
    #: girdle plane, i.e. how much support structure sits between them.
    supportHeightMm: float


class ProngSettingDefinition(SettingModel):
    """Prong-family parameters (brief section 9). Mirrors the real public
    JDL fields; `placementStrategy` and `style` are Setting-internal and
    are resolved from the stone rather than requested via JDL."""

    prongCount: int
    prongDiameterMm: float
    prongHeightMm: float
    placementStrategy: ProngPlacementStrategy
    style: ProngStyle = "ROUND_PRONG"


class BezelSettingDefinition(SettingModel):
    """Bezel-family parameters (brief section 17).

    `wallThicknessMm` and `wallHeightMm` are PRELIMINARY SOFTWARE VALUES
    when defaulted — deliberate, configurable software choices, never
    professional recommendations (SETTING-GOV-010). See
    docs/bible/21-setting/bezel-setting-contract.md.
    """

    wallThicknessMm: float
    wallHeightMm: float
    verticalReference: BezelVerticalReference = "GIRDLE"
    outlineOffsetMode: BezelOutlineOffsetMode = "CONSTANT_OFFSET"


class SettingDefinition(SettingModel):
    """What setting to build, for which stone, attached how."""

    settingId: str
    settingType: SettingFamily
    stone: StoneSettingReference
    attachment: SettingAttachmentInterface
    prong: ProngSettingDefinition | None = None
    bezel: BezelSettingDefinition | None = None


class SettingComponentFact(SettingModel):
    """One kernel-neutral geometric fact about a generated setting
    component. Facts only — no quality judgement (SETTING-GOV-016)."""

    componentId: str
    solidCount: int
    volumeMm3: float
    boundingBoxMinMm: tuple[float, float, float]
    boundingBoxMaxMm: tuple[float, float, float]


class SettingFallbackEvent(SettingModel):
    """An observable record that a documented geometric fallback was taken
    (SETTING-GOV-013 — a fallback must never be silent)."""

    stage: str
    reason: str


class SettingGeometryResult(SettingModel):
    """The structured outcome of generating one setting (brief section 7).

    Component *shapes* are returned separately by the generator; this model
    carries only kernel-neutral structure so it can cross layer boundaries.
    """

    settingId: str
    settingType: SettingFamily
    generatedComponents: list[str]
    productionComponents: list[str]
    referenceComponents: list[str]
    attachmentInterfaces: list[SettingAttachmentInterface]
    geometryFacts: list[SettingComponentFact]
    fallbackEvents: list[SettingFallbackEvent] = Field(default_factory=list)
    diagnostics: list[str] = Field(default_factory=list)
    compatibilityStatus: CompatibilityStatus
    #: Real requested-vs-generated prong count, for the prong family only.
    requestedProngCount: int | None = None
    generatedProngCount: int | None = None
    placementStrategy: ProngPlacementStrategy | None = None
