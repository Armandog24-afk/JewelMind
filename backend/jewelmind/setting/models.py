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

#: Prong body styles with a real generator (Sprint 23).
#:
#: `ROUND_PRONG` is the pre-Sprint-23 cylinder and remains the default, so every
#: existing design keeps byte-identical geometry. The other three are real
#: solids built by `prong.py`'s style registry:
#:
#: - `CLAW_PRONG` — a tapered body, narrower at the tip.
#: - `V_PRONG` — a body with a V notch cut into its tip, the shape used at a
#:   pointed stone's apex.
#: - `TAPERED_PRONG` — a straight taper with no notch; a claw without the
#:   pronounced tip reduction.
#:
#: `SHARED_PRONG` is deliberately NOT a member. Sharing is a question of WHICH
#: STONES a prong serves, not of what the prong's body looks like, so it lives
#: on `ProngGroupSpec` instead — a shared prong may be round, claw or V.
ProngStyle = Literal["ROUND_PRONG", "CLAW_PRONG", "V_PRONG", "TAPERED_PRONG"]

#: How prong positions are supplied.
#:
#: `DERIVED` runs a `ProngPlacementStrategy` against the stone's own geometry —
#: the pre-Sprint-23 behaviour and the default. `EXPLICIT` takes positions from
#: the caller, which is the escape hatch for a configuration no strategy
#: produces (a shared prong between two stones, an asymmetric claw layout).
#:
#: The same discipline Stone v2 established with `CUSTOM_OUTLINE`: a named
#: strategy for the common cases, and an explicit route so an unusual
#: configuration is expressible rather than unsupported.
ProngPositionSource = Literal["DERIVED", "EXPLICIT"]

#: Head architectures with a real generator (Sprint 23).
#:
#: The head is the structure BETWEEN the attachment plane and the stone — what
#: the prongs rise from. Before this sprint there was exactly one, built
#: ring-side as a hollow cylinder; these are category-neutral and built by
#: `head.py`'s registry.
#:
#: - `BASKET` — the pre-Sprint-23 hollow cylindrical wall, preserved
#:   byte-identically and still the default.
#: - `PEG_HEAD` — a basket on a narrower solid peg, the shape used where a head
#:   meets a shank at a single point.
#: - `MARTINI` — a conical wall, wide at the girdle and narrow at the base.
#: - `TULIP` — a concave-flared wall, narrow at the base and opening toward the
#:   girdle.
#:
#: `TRELLIS` is deliberately NOT a member: it needs swept curved rails that the
#: current pipeline cannot build robustly. See `capability.py`'s
#: `RESERVED_HEAD_ARCHITECTURES` and
#: docs/bible/25-setting-v2/head-execution-boundary.md.
HeadArchitecture = Literal["BASKET", "PEG_HEAD", "MARTINI", "TULIP"]

#: Whether metal is relieved where the stone sits.
#:
#: `NONE` is the default and the pre-Sprint-23 behaviour: no seat, and the
#: stone/metal overlap is exactly what it always was. `REFERENCE_SEAT` cuts the
#: real generated stone solid out of the head and prongs, so metal no longer
#: occupies the stone's volume.
#:
#: A CUT, never a fuse. The stone shape is used as a cutting TOOL and is never
#: unioned into the metal body, so LAW-006 holds unchanged — see
#: `seat.py`'s module docstring for why that distinction is load-bearing.
#:
#: This is REFERENCE geometry: it is not a cut seat with a bearing shoulder, and
#: no claim is made that a setter could use it as one.
SeatMode = Literal["NONE", "REFERENCE_SEAT"]

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

    #: True when the stone's outline is the same in every direction from its
    #: centre — a circle, or a sphere's equator.
    #:
    #: This is the property RADIAL prong placement actually depends on. Sprint
    #: 19 approximated it as `shape == "round"`, which was true then because
    #: round was the only radially symmetric shape. Stating the geometric fact
    #: instead means a future radially symmetric stone — including a custom
    #: outline that happens to be circular — is handled correctly without
    #: another name added to a branch.
    isRadiallySymmetric: bool = False
    #: Signed local-Y direction the stone's tip points, for pointed
    #: asymmetric shapes. `None` when the shape has no distinguished tip.
    tipDirectionY: float | None = None

    #: The stone's real girdle outline as ordered (x, y) millimetre points in
    #: the stone's own unrotated local frame.
    #:
    #: THIS IS WHAT MAKES SETTING SHAPE-AGNOSTIC (Sprint 20, brief sections
    #: 27/41/72). Before it existed, `girdle_outline_wire()` looked the outline
    #: up in a table keyed by shape NAME, so a custom or imported stone — which
    #: has no named cut — could not be set at all. Carrying the points means a
    #: bezel consumes the same contract whatever the stone's source, with no
    #: `if shape == "custom"` branch anywhere in the Setting System.
    #:
    #: `None` only when the stone genuinely has no planar outline (the
    #: spherical pearl reference), which a Setting must treat as "cannot set",
    #: never as "assume a circle".
    outlinePoints: list[tuple[float, float]] | None = None

    #: Narrow-end width of a tapered stone, needed to rebuild its exact outline.
    #: `None` for every non-tapered shape.
    narrowWidthMm: float | None = None


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

    #: Where positions come from (Sprint 23). `DERIVED` is the default and runs
    #: `placementStrategy`; `EXPLICIT` uses `positions` verbatim.
    positionSource: ProngPositionSource = "DERIVED"

    #: Explicit positions, required when `positionSource == "EXPLICIT"` and
    #: ignored otherwise. Never silently mixed with derived ones: a caller
    #: either states every position or none of them, because a half-derived
    #: layout has no determinate meaning.
    positions: list[ProngPositionSpec] = Field(default_factory=list, max_length=100)

    #: Named subsets carrying a per-group style override.
    groups: list[ProngGroupSpec] = Field(default_factory=list, max_length=20)

    #: Tip radius as a fraction of the prong radius, for the tapered styles.
    #: Ignored by `ROUND_PRONG`, which is a straight cylinder.
    tipRatio: float = Field(default=0.6, gt=0.05, le=1.0, allow_inf_nan=False)


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


class ProngPositionSpec(SettingModel):
    """One explicitly placed prong, in the stone's own local millimetre frame.

    Exists so a configuration no strategy derives is still expressible. The
    `servesStoneInstanceIds` field is what makes a SHARED prong a real concept
    rather than a coincidence of position: a prong between two stones declares
    both, and that declaration survives into the geometry metadata where
    inspection and Vision can read it.
    """

    xMm: float = Field(ge=-100.0, le=100.0, allow_inf_nan=False)
    yMm: float = Field(ge=-100.0, le=100.0, allow_inf_nan=False)

    #: Which stone instances this prong grips. Empty means "the setting's own
    #: stone", which is the single-stone case. Two or more ids make it shared.
    #:
    #: IDs reference `arrangement.instances[].instanceId`. Stored as opaque
    #: strings on purpose: the Setting System must not import the arrangement
    #: layer, so it carries the reference and never resolves it
    #: (SETTING-GOV-001).
    servesStoneInstanceIds: list[str] = Field(default_factory=list, max_length=20)


class ProngGroupSpec(SettingModel):
    """A named subset of prongs that share a style or a stone assignment.

    Grouping is how "these two prongs are the shared pair between the centre
    and the left side stone" is stated. It carries no geometry of its own — a
    group is a label over positions, so removing one changes nothing built.
    """

    groupId: str = Field(min_length=1, max_length=80)
    style: ProngStyle | None = None
    positionIndices: list[int] = Field(default_factory=list, max_length=100)


class HeadSettingDefinition(SettingModel):
    """Head-family parameters: the structure between the attachment plane and
    the stone (Sprint 23).

    Every dimension here is a CONSTRUCTION PARAMETER. `wallThicknessMm` and
    the taper ratios are deliberate software choices chosen to produce robust
    geometry, exactly like the bezel's wall dimensions — never professional
    recommendations, and no minimum is enforced because no sourced professional
    minimum exists (SETTING-GOV-010).
    """

    architecture: HeadArchitecture = "BASKET"

    #: Radius of the head wall's centreline at the girdle. Supplied by the
    #: category integration via the attachment interface, so the Setting never
    #: derives it from a band or a ring size.
    outerRadiusMm: float = Field(gt=0.0, le=100.0, allow_inf_nan=False)

    #: Radial thickness of the wall.
    wallThicknessMm: float = Field(gt=0.0, le=20.0, allow_inf_nan=False)

    #: The wall's inner radius, when the caller needs to state it exactly.
    #:
    #: EXISTS FOR FLOATING-POINT EXACTNESS, not for expressiveness. The
    #: pre-Sprint-23 basket computed its bore as `centre - prongRadius`, while
    #: deriving it here as `outerRadius - wallThickness` re-associates the same
    #: arithmetic as `(c + p) - 2p` and lands about 1e-11 mm away. That is
    #: harmless numerically and still a real, avoidable change to shipped
    #: geometry, so the Ring adapter passes the original expression and the
    #: basket's volume stays bit-for-bit what it was.
    #:
    #: `None` means "derive it", which is correct for every architecture that
    #: has no pre-existing geometry to preserve.
    innerRadiusMm: float | None = Field(
        default=None, gt=0.0, le=100.0, allow_inf_nan=False
    )

    #: Vertical extent from the attachment plane up to the girdle plane.
    heightMm: float = Field(gt=0.0, le=100.0, allow_inf_nan=False)

    #: Base radius as a fraction of `outerRadiusMm`, for the tapered
    #: architectures. Ignored by `BASKET`, which is a straight wall.
    baseRadiusRatio: float = Field(default=0.55, gt=0.05, le=1.0, allow_inf_nan=False)

    #: Diameter of the peg below the head, for `PEG_HEAD` only.
    pegDiameterMm: float | None = Field(
        default=None, gt=0.0, le=20.0, allow_inf_nan=False
    )

    #: Height of that peg.
    pegHeightMm: float | None = Field(
        default=None, gt=0.0, le=50.0, allow_inf_nan=False
    )


class SeatSettingDefinition(SettingModel):
    """Whether and how metal is relieved where the stone sits (Sprint 23)."""

    mode: SeatMode = "NONE"

    #: Extra radial clearance added to the cutting tool, in millimetres.
    #:
    #: A GEOMETRIC ROBUSTNESS value, not a manufacturing allowance: a boolean
    #: cut of two exactly-tangent solids is where OCCT is least reliable, so the
    #: tool is grown slightly. It is not a stone-setting tolerance and must
    #: never be described as one.
    clearanceMm: float = Field(default=0.02, ge=0.0, le=1.0, allow_inf_nan=False)


class SettingDefinition(SettingModel):
    """What setting to build, for which stone, attached how."""

    settingId: str
    settingType: SettingFamily
    stone: StoneSettingReference
    attachment: SettingAttachmentInterface
    prong: ProngSettingDefinition | None = None
    bezel: BezelSettingDefinition | None = None

    #: The head structure this setting rises from (Sprint 23). `None` means the
    #: category integration builds its own support, which is what every
    #: pre-Sprint-23 caller did — so the field being absent keeps the old
    #: behaviour rather than silently producing a second head.
    head: HeadSettingDefinition | None = None

    #: Whether metal is relieved where the stone sits. `None` is equivalent to
    #: `mode="NONE"`, i.e. the pre-Sprint-23 geometry.
    seat: SeatSettingDefinition | None = None


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

    #: The prong style actually built, for the prong family only (Sprint 23).
    prongStyle: ProngStyle | None = None

    #: The head architecture actually built, when this setting built one.
    headArchitecture: HeadArchitecture | None = None

    #: The seat mode actually applied.
    seatMode: SeatMode | None = None

    #: Which stone instances each generated component serves, by component name.
    #:
    #: THE DETERMINISTIC SETTING -> STONE MAPPING this sprint adds. A downstream
    #: consumer can ask "which stones does this prong grip?" without inferring
    #: it from coordinates, and a shared prong reports both.
    stoneInstanceAssignments: dict[str, list[str]] = Field(default_factory=dict)
