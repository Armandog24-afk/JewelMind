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

#: Setting families with a real, registered generator.
#:
#: Sprint 27 added `channel`, `bar`, `flush` and `tension`, each with a real
#: generator registered in `dispatch.py::setting_generators()` — the literal is
#: still a closed enum whose every member is implemented, per
#: SETTING-GOV-005/006. `bead` and `pave` remain deliberately ABSENT: repeated
#: small-stone retention is not a family of its own here, it is
#: `setting/retention.py`'s builders driven by a pavé field, and giving it a
#: second route would be the duplicate engine Sprint 26 already refused. See
#: `capability.py::RESERVED_SETTING_FAMILIES` and
#: `modes.py::RESERVED_SETTING_MODES` for every reserved name and its real
#: reason.
SettingFamily = Literal["prong", "bezel", "channel", "bar", "flush", "tension"]

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
#: - `OPEN_GALLERY` — a basket wall with evenly spaced windows pierced through
#:   it (Sprint 27). Deliberately NOT called azure: azure/ajouré work is
#:   arbitrary decorative piercing, and this is the parametric subset of it.
#:
#: `TRELLIS` is deliberately NOT a member: it needs swept curved rails that the
#: current pipeline cannot build robustly. See `capability.py`'s
#: `RESERVED_HEAD_ARCHITECTURES` and
#: docs/bible/25-setting-v2/head-execution-boundary.md.
HeadArchitecture = Literal[
    "BASKET", "PEG_HEAD", "MARTINI", "TULIP", "OPEN_GALLERY"
]

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

#: Which bezel variant is built (Sprint 27).
#:
#: `FULL` is the pre-Sprint-27 continuous wall and remains the default, so
#: every existing bezel design keeps byte-identical geometry. `PARTIAL` cuts
#: evenly spaced angular openings through that same wall — the SAME offset
#: outline, the same extrusion, then a boolean cut, so a partial bezel can never
#: be a different wall from the full one it is derived from.
#:
#: `OPEN_BACK` is deliberately NOT a member: the generated wall is already open
#: at both ends, so it would name no distinct solid. See
#: `modes.py::RESERVED_SETTING_MODES`.
BezelVariant = Literal["FULL", "PARTIAL"]

#: Where a bezel wall's vertical extent is anchored.
BezelVerticalReference = Literal["GIRDLE"]

#: How the bezel path is derived from the stone outline.
BezelOutlineOffsetMode = Literal["CONSTANT_OFFSET"]

CompatibilityStatus = Literal["SUPPORTED_SOFTWARE", "EXPERIMENTAL", "UNSUPPORTED"]

#: How a channel or a bar run ends (Sprint 27).
#:
#: `OPEN`        - the walls simply stop, so the run is visible from the end.
#: `CLOSED_ENDS` - an end cap closes each end of the run.
#:
#: Neither is a professional statement about how a setter finishes an edge; both
#: are deterministic construction rules, the same discipline the pavé's own
#: `PaveTermination` follows.
SettingTerminationMode = Literal["OPEN", "CLOSED_ENDS"]

#: Whether a mode's geometry is mirrored about the host's own axes.
SettingModeSymmetry = Literal["SYMMETRIC", "ASYMMETRIC"]


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

    #: Which variant to build (Sprint 27). `FULL` reproduces the pre-Sprint-27
    #: wall exactly, so the field being defaulted keeps every existing bezel's
    #: solid identical.
    variant: BezelVariant = "FULL"

    #: How many openings a `PARTIAL` bezel cuts, their angular width, and where
    #: the first one is centred. Read only by `PARTIAL`; a `FULL` bezel ignores
    #: them, and the unread values are reported as INFORMATION by
    #: `JM-SETTING-009` rather than silently dropped.
    openingCount: int = Field(default=2, ge=1, le=24)
    openingSweepDeg: float = Field(
        default=40.0, gt=0.0, le=180.0, allow_inf_nan=False
    )
    openingStartAngleDeg: float = Field(
        default=90.0, ge=-360.0, le=360.0, allow_inf_nan=False
    )


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

    #: How many windows an `OPEN_GALLERY` pierces through its wall, how wide
    #: each is, and how much of the wall's height they span (Sprint 27).
    #:
    #: `windowHeightFraction` is strictly below 1.0 so a continuous rim survives
    #: at the top and the bottom of the wall. Without it the wall becomes
    #: disconnected pillars, and `build_head()` refuses a head that is not one
    #: connected body (SETTINGV2-GOV-006) — so the fraction is a CONSTRUCTION
    #: CORRECTNESS bound, not a proportion anyone reviewed.
    windowCount: int = Field(default=4, ge=1, le=24)
    windowSweepDeg: float = Field(
        default=45.0, gt=0.0, le=180.0, allow_inf_nan=False
    )
    windowHeightFraction: float = Field(
        default=0.6, gt=0.0, lt=1.0, allow_inf_nan=False
    )


class ChannelSettingDefinition(SettingModel):
    """Channel-family parameters (Sprint 27).

    A channel is TWO PARALLEL WALLS with the stones between them. This model
    describes the walls; it never describes where the stones are — a channel
    spanning a row consumes placements the Stone Arrangement Engine resolved and
    records their ids, and computing a position here would be the second
    placement engine ARRANGE-GOV-006 forbids.

    Every dimension is a CONSTRUCTION PARAMETER. No minimum wall thickness is
    enforced, because no sourced professional minimum exists — the same
    documented gap the bezel already carries (SETTING-GOV-010).
    """

    #: Direction the run takes in the stone's own horizontal frame.
    axisDeg: float = Field(default=0.0, ge=-360.0, le=360.0, allow_inf_nan=False)

    #: Length of the run. `None` means "the stone's own extent along the axis",
    #: resolved from the stone reference by the generator — reading a stone fact,
    #: which is exactly what SETTING-GOV-003 sanctions.
    spanMm: float | None = Field(
        default=None, gt=0.0, le=200.0, allow_inf_nan=False
    )

    #: Clear distance between the walls. `None` resolves to the stone's own
    #: extent across the axis.
    innerWidthMm: float | None = Field(
        default=None, gt=0.0, le=100.0, allow_inf_nan=False
    )

    wallThicknessMm: float = Field(gt=0.0, le=20.0, allow_inf_nan=False)

    #: How far each wall rises above the stone's girdle plane.
    wallHeightMm: float = Field(gt=0.0, le=50.0, allow_inf_nan=False)

    termination: SettingTerminationMode = "OPEN"

    #: `SYMMETRIC` centres the run on the stone; `ASYMMETRIC` starts it AT the
    #: stone's centre and extends along `axisDeg`, which is how a channel
    #: running off to one side of a centre stone is expressed.
    symmetry: SettingModeSymmetry = "SYMMETRIC"

    offsetXMm: float = Field(default=0.0, ge=-50.0, le=50.0, allow_inf_nan=False)
    offsetYMm: float = Field(default=0.0, ge=-50.0, le=50.0, allow_inf_nan=False)
    offsetZMm: float = Field(default=0.0, ge=-50.0, le=50.0, allow_inf_nan=False)

    #: Which arrangement instances this channel spans. Opaque ids, carried and
    #: never resolved (SETTINGV2-GOV-011).
    stoneInstanceIds: list[str] = Field(default_factory=list, max_length=120)


class BarSettingDefinition(SettingModel):
    """Bar-family parameters (Sprint 27).

    A bar setting is a set of TRANSVERSE BARS across a run, with the stones
    between adjacent bars. The bars are the retention; the stones are the
    arrangement's. That separation is why this model carries a bar count and a
    spacing but no stone position.
    """

    axisDeg: float = Field(default=0.0, ge=-360.0, le=360.0, allow_inf_nan=False)

    barCount: int = Field(ge=1, le=40)

    #: Centre-to-centre spacing between adjacent bars along the axis. `None`
    #: resolves to the stone's own extent along the axis plus one bar width, so
    #: a two-bar setting places one bar on each side of a single stone.
    barSpacingMm: float | None = Field(
        default=None, gt=0.0, le=100.0, allow_inf_nan=False
    )

    #: Thickness of each bar along the axis.
    barWidthMm: float = Field(gt=0.0, le=20.0, allow_inf_nan=False)

    #: Length of each bar across the axis. `None` resolves to the stone's own
    #: extent across the axis.
    barLengthMm: float | None = Field(
        default=None, gt=0.0, le=100.0, allow_inf_nan=False
    )

    #: How far each bar rises above the stone's girdle plane.
    barHeightMm: float = Field(gt=0.0, le=50.0, allow_inf_nan=False)

    #: `SYMMETRIC` distributes the bars about the stone's centre, so an even
    #: count straddles it. `ASYMMETRIC` puts the first bar ON that centre and
    #: runs the rest along `axisDeg`.
    symmetry: SettingModeSymmetry = "SYMMETRIC"

    offsetXMm: float = Field(default=0.0, ge=-50.0, le=50.0, allow_inf_nan=False)
    offsetYMm: float = Field(default=0.0, ge=-50.0, le=50.0, allow_inf_nan=False)
    offsetZMm: float = Field(default=0.0, ge=-50.0, le=50.0, allow_inf_nan=False)

    stoneInstanceIds: list[str] = Field(default_factory=list, max_length=120)


class FlushSettingDefinition(SettingModel):
    """Flush/gypsy-family parameters (Sprint 27).

    A flush setting sinks the stone INTO a mass of metal whose top surface is
    level with part of its crown. So the geometry is a solid collar plus a
    RECESS — and the recess is the existing `REFERENCE_SEAT` cut, not a new
    operation: the stone's own solid is used as a cutting tool against the
    collar, so the stone never becomes production metal (LAW-006,
    SETTINGV2-GOV-008).

    That makes seat relief a GEOMETRIC PRECONDITION of this family rather than
    an option: without it the collar occupies the stone's whole volume and the
    result is a lump of metal with a stone inside it. `JM-SETTING-010` reports
    the missing relief; the generator refuses.
    """

    #: How far the collar extends outward from the stone's girdle outline.
    collarWidthMm: float = Field(gt=0.0, le=20.0, allow_inf_nan=False)

    #: How far the collar's top sits above the stone's girdle plane.
    #:
    #: Must stay BELOW the stone's own crown height, or the stone is entirely
    #: buried and the recess leaves a closed cavity instead of an opening. A
    #: geometric precondition checked against the real generated stone, never a
    #: professional setting depth.
    rimHeightMm: float = Field(gt=0.0, le=20.0, allow_inf_nan=False)

    offsetXMm: float = Field(default=0.0, ge=-50.0, le=50.0, allow_inf_nan=False)
    offsetYMm: float = Field(default=0.0, ge=-50.0, le=50.0, allow_inf_nan=False)
    offsetZMm: float = Field(default=0.0, ge=-50.0, le=50.0, allow_inf_nan=False)


class TensionSettingDefinition(SettingModel):
    """Tension-family parameters (Sprint 27).

    TWO OPPOSING SUPPORTS and the stone between them. The supports are real
    solids and the stone's volume is relieved out of each, so the grooves the
    stone would sit in are genuine geometry rather than an implication.

    WHAT IS DELIBERATELY NOT MODELLED, and this is the substantive honesty of
    this family: nothing here computes the elastic response of the metal, the
    force the supports apply, or whether the stone would be held. A real tension
    ring's whole function is a structural one, and asserting anything about it
    would require material properties and a validated engineering model that do
    not exist in this project. The capability registry records
    `professionalReviewRequirement: REQUIRED` for exactly this reason, and the
    mode's status is PARTIAL rather than CURRENT — the geometry is complete, the
    engineering claim is absent (SETTING-GOV-010, LAW-010).
    """

    #: Direction the supports oppose each other along, in the stone's own
    #: horizontal frame.
    gripAxisDeg: float = Field(
        default=0.0, ge=-360.0, le=360.0, allow_inf_nan=False
    )

    #: Width of each support across the grip axis.
    padWidthMm: float = Field(gt=0.0, le=50.0, allow_inf_nan=False)

    #: Extent of each support ALONG the grip axis — the shoulder's thickness.
    padThicknessMm: float = Field(gt=0.0, le=50.0, allow_inf_nan=False)

    #: How far each support's inner face reaches INWARD past the stone's edge,
    #: so the seat cut leaves a real groove rather than a tangent touch. A
    #: GEOMETRIC ROBUSTNESS value in the class of `constants.EMBED_MM`, never a
    #: grip depth: nothing here models how hard the metal presses.
    padDepthMm: float = Field(gt=0.0, le=10.0, allow_inf_nan=False)

    #: How far each support rises above the stone's girdle plane.
    gripHeightMm: float = Field(gt=0.0, le=50.0, allow_inf_nan=False)

    offsetXMm: float = Field(default=0.0, ge=-50.0, le=50.0, allow_inf_nan=False)
    offsetYMm: float = Field(default=0.0, ge=-50.0, le=50.0, allow_inf_nan=False)
    offsetZMm: float = Field(default=0.0, ge=-50.0, le=50.0, allow_inf_nan=False)


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

    #: The Sprint 27 families. Each is `None` unless `settingType` names it, for
    #: the same reason `prong` and `bezel` already are: a family's parameters
    #: are meaningless to another family's generator, and carrying them all
    #: would make the unread ones look like inputs.
    channel: ChannelSettingDefinition | None = None
    bar: BarSettingDefinition | None = None
    flush: FlushSettingDefinition | None = None
    tension: TensionSettingDefinition | None = None

    #: The resolved PRIMARY setting mode's stable id, and its deterministic
    #: fingerprint (Sprint 27).
    #:
    #: RESOLVED BY THE CALLER, carried here. The Setting System does not read
    #: `setting.type` from a JDL document — the adapter does — so the mode
    #: arrives already resolved, exactly as the attachment interface does. `None`
    #: means the caller predates setting modes, which every pre-Sprint-27 test
    #: fixture does; the generators fall back to the family's own default
    #: variant, so the geometry is unchanged.
    settingModeId: str | None = None
    settingModeFingerprint: str | None = None

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


class SettingComponentProvenance(SettingModel):
    """Why one generated setting component exists (Sprint 27, brief §19).

    THE PROVENANCE RECORD, and it deliberately lives on the setting result
    rather than on a `GeometryPlan`. `GeometryPlan` is still not materialized —
    `docs/bible/08-alchemist/` records it as PLANNED, and materializing it is an
    explicit ADR condition (ALCHEMIST-GOV, "materializing GeometryPlan"). This
    sprint's requirement was that every setting component be traceable to the
    mode, the stone and the placements it came from, and that is a fact about the
    component, so it is recorded where the component's other facts already live.
    Inventing an unrequested compiler stage to hold it would have been a
    speculative abstraction with an ADR attached.

    ANONYMOUS COMPONENTS ARE THE FAILURE MODE THIS PREVENTS: without it, a
    reader looking at `bars` in a manifest can tell what it measures and not
    what asked for it.
    """

    componentId: str

    #: The stable mode id that built this component. `None` only for a caller
    #: that predates setting modes.
    settingModeId: str | None = None

    #: Which stone specification this component holds.
    sourceStoneId: str

    #: Which arrangement instances it holds, by id. Empty for a component that
    #: holds only the design's own stone.
    sourceStoneInstanceIds: list[str] = Field(default_factory=list)

    #: Production metal, or reference geometry. Stated rather than inferred from
    #: the name, so a consumer never has to know the naming convention.
    classification: Literal["PRODUCTION", "REFERENCE"]


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

    # ---- Sprint 27 -----------------------------------------------------------

    #: The resolved PRIMARY mode this setting was built as, and its identity.
    settingModeId: str | None = None
    settingModeFingerprint: str | None = None

    #: Why each generated component exists. One entry per component in
    #: `generatedComponents`, asserted by test in both directions so a component
    #: cannot ship without provenance.
    componentProvenance: list[SettingComponentProvenance] = Field(
        default_factory=list
    )

    #: The bezel variant actually built, for the bezel family only.
    bezelVariant: BezelVariant | None = None

    #: Requested-vs-generated counts for the counted families, reported the same
    #: way the prong family already reports its own. A requested count that
    #: could not be honoured must be VISIBLE, never quietly smaller
    #: (ATLAS-GOV-006).
    requestedOpeningCount: int | None = None
    generatedOpeningCount: int | None = None
    requestedBarCount: int | None = None
    generatedBarCount: int | None = None
    requestedWindowCount: int | None = None
    generatedWindowCount: int | None = None

    #: Whether this family's geometry depends on a professional judgment the
    #: project has no evidence for. `REQUIRED` for `tension` and nothing else
    #: today; it is not a validation verdict and never becomes one — it says a
    #: qualified human must look, not that anyone has.
    professionalReviewRequirement: Literal["NOT_REQUIRED", "REQUIRED"] = (
        "NOT_REQUIRED"
    )
