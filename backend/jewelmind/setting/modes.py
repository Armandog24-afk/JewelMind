"""Extended Setting Modes: the first-class retention/support taxonomy (Sprint 27).

WHAT A SETTING MODE IS, AND WHAT IT IS NOT. A setting mode is a named
STRATEGY FOR HOLDING OR SUPPORTING A STONE. It is not the stone (Stone System
v2 owns that), not the material (Gem Identity owns that), not where the stones
sit (the Stone Arrangement Engine owns that), and not the resulting solids
(Atlas owns those). Those four boundaries are why this module contains no
dimension of a stone, no gem field, no coordinate of a placement and no kernel
object.

WHY A MODE EXISTS AT ALL, GIVEN `SettingSpec.type` ALREADY SELECTS A FAMILY.
Before this sprint the Setting System carried four independent axes —
`settingType`, `prongStyle`, `headArchitecture` and the pavé's
`PaveRetentionStrategy` — each with its own registry, each honest about itself,
and no single place that could answer "which setting techniques does JewelMind
actually build?". A reader had to consult four registries and know that a
`SHARED_BEAD` and a `V_PRONG` are the same KIND of thing (a way metal holds a
stone) expressed at different points in the pipeline.

THIS MODULE ADDS THE MISSING NOUN, NOT A FIFTH REGISTRY. `SettingModeId` names
one strategy per member, and `capability.py::setting_modes()` DERIVES each
mode's geometry capability from the live builder registries — `setting_generators()`,
`prong_solid_builders()`, `head_builders()`, `retention_builders()` — rather
than restating it. A mode cannot claim geometry a builder does not provide, and
a builder cannot exist without a mode row, because the test asserts both
directions. That is the anti-drift discipline Sprint 20 established after three
hand-copied registries had already drifted.

THE THREE AXES ARE PRESERVED, NOT COLLAPSED. `SettingModeAxis` records which
one a mode belongs to:

    PRIMARY    - how the design's own stone is held (prong, bezel, channel,
                 bar, flush, tension). Selected by `setting.type`.
    HEAD       - what the setting rises from (basket, peg, martini, tulip,
                 open gallery). Selected by `setting.headArchitecture`.
    RETENTION  - how a FIELD of small stones is held (bead, shared bead,
                 micro-prong, shared prong). Selected by the pavé's own
                 `retention.strategy`.

A primary mode and a head mode are both present in one design at the same
time; they are not alternatives. Collapsing them into one enum would make
"a bezel on a martini" inexpressible.

RESERVED IDS ARE NOT MEMBERS. `SettingModeId` is a closed literal whose every
member has a real builder, and `RESERVED_SETTING_MODES` carries the rest with
the real technical reason each is absent — the discipline SETTING-GOV-005 and
SETTINGV2-GOV-005 already apply to setting families and head architectures. An
unimplemented technique must be refused by the model, never silently
substituted with the nearest solid that happens to exist.

NO INVENTED PROFESSIONAL THRESHOLD. Every dimension in `SettingModeParameters`
is a CONSTRUCTION PARAMETER supplied by the document, and every default is a
deliberate software choice inside the schema's own range chosen to produce
robust geometry. Nothing here states a minimum wall, a minimum bead, a settable
depth, a grip pressure or whether any configuration would hold — each of those
needs sourced professional evidence this project does not have
(SETTING-GOV-010, SETTINGV2-GOV-010).

Nothing here imports `jewelmind.ring`, a jewelry category, a geometry module or
the CAD kernel (SETTING-GOV-001).
"""

from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from jewelmind.setting.models import SettingModeSymmetry, SettingTerminationMode

#: Version of the mode TAXONOMY — the id set, the axis assignment and the
#: parameter contract. Distinct from `SETTING_GEOMETRY_VERSION`, which versions
#: how the solids are built: a mode can be renamed in documentation or gain a
#: reserved sibling without any geometry changing, and a construction can change
#: without the taxonomy moving.
SETTING_MODE_TAXONOMY_VERSION = "1.0.0"

#: Which pipeline axis a mode belongs to. See the module docstring for why
#: three axes are preserved rather than collapsed into one enum.
SettingModeAxis = Literal["PRIMARY", "HEAD", "RETENTION"]

#: The setting-technique families this taxonomy spans.
#:
#: Deliberately UPPER CASE while `SettingFamily` (the generator key, and the
#: public `setting.type` value) stays lower case. They are not the same thing: a
#: family here groups techniques for a reader, while `SettingFamily` names a
#: registered generator. `RETENTION` and `HEAD` have no `setting.type` at all.
SettingModeFamily = Literal[
    "PRONG",
    "BEZEL",
    "CHANNEL",
    "BAR",
    "FLUSH",
    "TENSION",
    "HEAD",
    "RETENTION",
]

#: Every setting mode with a real builder behind it.
#:
#: ONE MEMBER PER DISTINGUISHABLE STRATEGY, and "distinguishable" means the
#: solid differs. `PRONG_ROUND` and `PRONG_CLAW` are two members because the
#: bodies genuinely differ; a four-prong and a six-prong setting are ONE member
#: because the count is a parameter and duplicating it as a mode id would put
#: the same number in two places.
#:
#: `PRONG_SHARED` is the exception that earns its own id: sharing is not a body
#: shape but a question of WHICH STONES a prong serves, it is expressed through
#: a different route (explicit positions carrying `servesStoneInstanceIds`), and
#: its honest status differs from the other prong modes.
SettingModeId = Literal[
    # PRIMARY — how the design's own stone is held.
    "PRONG_ROUND",
    "PRONG_TAPERED",
    "PRONG_CLAW",
    "PRONG_V",
    "PRONG_SHARED",
    "BEZEL_FULL",
    "BEZEL_PARTIAL",
    "CHANNEL_LINEAR",
    "BAR_TRANSVERSE",
    "FLUSH_GYPSY",
    "TENSION_OPPOSED",
    # HEAD — what the setting rises from.
    "HEAD_BASKET",
    "HEAD_PEG",
    "HEAD_MARTINI",
    "HEAD_TULIP",
    "HEAD_OPEN_GALLERY",
    # RETENTION — how a field of small stones is held.
    "RETENTION_BEAD",
    "RETENTION_SHARED_BEAD",
    "RETENTION_MICRO_PRONG",
    "RETENTION_SHARED_PRONG",
]

#: Setting techniques named for architectural completeness, with NO builder and
#: NO membership in `SettingModeId`.
#:
#: Each value is the REAL TECHNICAL REASON the mode is absent, never a roadmap
#: slogan. A reader should be able to tell from this table what would have to
#: exist first — which is the whole point of writing the reason down rather than
#: the word "planned".
RESERVED_SETTING_MODES: dict[str, str] = {
    "PRONG_COMPASS_POINT": (
        "Prongs placed at the stone's own named anchors (tip, cleft, corners). "
        "The anchors exist in Stone System v2; a placement strategy that "
        "consumes them does not, so OUTLINE_CARDINAL remains the non-round "
        "default and a compass-point request would silently be an "
        "outline-cardinal layout."
    ),
    "PRONG_CUSTOM_PROFILE": (
        "An arbitrary swept prong cross-section. EXPLICIT positions are the "
        "escape hatch for LAYOUT; an arbitrary profile is a different escape "
        "hatch and no builder accepts one."
    ),
    "BEZEL_OPEN_BACK": (
        "The generated bezel wall is already open at both ends, so an "
        "'open-back' bezel is not a distinct solid here. A genuine open-back "
        "bezel differs by carrying a pierced seat rail the stone rests on, and "
        "no seat with a bearing shoulder exists (SETTINGV2-GOV-009)."
    ),
    "BEZEL_MILLGRAIN": (
        "A milled decorative edge. It is a surface texture applied along the "
        "wall's rim, and no texturing or knurling operation exists in the "
        "pipeline; approximating it with beads would be a different structure "
        "wearing the name."
    ),
    "CHANNEL_SHARED_WALL": (
        "One wall shared between two adjacent channel rows. It requires two "
        "hosted rows resolved together, and one setting builds one channel."
    ),
    "CHANNEL_TAPERED": (
        "A channel whose clear width narrows along its run, for a graduated "
        "row. It needs a lofted wall pair rather than a pair of prisms, and a "
        "loft over a long shallow taper is not yet verifiable here."
    ),
    "BAR_TAPERED": (
        "A bar with a varying cross-section. Same construction gap as "
        "CHANNEL_TAPERED: it needs a swept or lofted profile per bar."
    ),
    "FLUSH_MILLGRAIN": (
        "A milled rim around a flush-set stone. Same texturing gap as "
        "BEZEL_MILLGRAIN."
    ),
    "TENSION_COMPRESSION_MODELLED": (
        "A tension setting whose grip is derived from the metal's actual "
        "elastic response. That is an engineering calculation requiring "
        "material properties and a validated model, neither of which exists "
        "here. TENSION_OPPOSED builds the opposing supports and makes no "
        "structural claim (see its own capability row)."
    ),
    "HEAD_TRELLIS": (
        "Interwoven curved rails require a swept solid along a 3D spline. The "
        "current pipeline builds solids of revolution and lofts reliably; a "
        "swept trellis is not yet verifiable, so no builder exists."
    ),
    "HEAD_CATHEDRAL": (
        "A cathedral head is defined by how the SHANK rises to meet it, which "
        "is shank geometry rather than head geometry. It belongs to a Shank "
        "milestone, not to this taxonomy."
    ),
    "HEAD_DOUBLE_GALLERY": (
        "Two stacked galleries need a second head instance per setting, which "
        "the one-head-per-setting contract does not express."
    ),
    "HEAD_AZURE": (
        "Azure/ajouré work is arbitrary decorative piercing, whose pattern is "
        "not expressible as parameters. HEAD_OPEN_GALLERY is the parametric "
        "subset that is — evenly spaced windows through the wall — and it is "
        "deliberately not called azure."
    ),
    "UNDER_GALLERY_SUPPORT": (
        "Decorative structure below the gallery, joining a head to a shank or "
        "to a second head. It needs multi-head or rail geometry, and "
        "RESERVED_SUPPORT_ELEMENTS already records that a rail joins two heads "
        "while one setting builds one."
    ),
    "HALO_HIDDEN_SETTING": (
        "Retention metal for a hidden halo's own stones. Sprint 25 recorded "
        "halo settingGeometry as false and it still is: the halo layer composes "
        "placements, and no builder holds a halo member. A mode here would have "
        "nothing to build."
    ),
    "RETENTION_CHANNEL": (
        "A continuous rail holding a pavé row. The pavé's retention anchors are "
        "LATTICE CORNERS — the points where cells meet — which is the right "
        "topology for a bead and the wrong one for a rail that runs the whole "
        "row. Channel setting exists as its own PRIMARY family instead, which "
        "is where a rail's extent is actually stated."
    ),
    "RETENTION_BAR": (
        "Bars between adjacent pavé stones. Same topology reason as "
        "RETENTION_CHANNEL: a bar sits at a cell MIDPOINT, not at a corner. "
        "BAR_TRANSVERSE is the PRIMARY family that builds bars."
    ),
    "RETENTION_GRAIN": (
        "A raised grain, as distinct from a bead. Its shape depends on the "
        "graining tool and the setter's hand; RETENTION_BEAD's sphere is the "
        "deterministic CAD reference for the volume a grain occupies, and a "
        "second id mapped to the same solid would imply a difference that is "
        "not there."
    ),
}

#: Modes selectable through `setting.type`, i.e. the PRIMARY axis.
#:
#: Derived by `mode_axis()` rather than restated, so a new PRIMARY mode cannot
#: be added without appearing here.
_PRIMARY_MODES: tuple[str, ...] = (
    "PRONG_ROUND",
    "PRONG_TAPERED",
    "PRONG_CLAW",
    "PRONG_V",
    "PRONG_SHARED",
    "BEZEL_FULL",
    "BEZEL_PARTIAL",
    "CHANNEL_LINEAR",
    "BAR_TRANSVERSE",
    "FLUSH_GYPSY",
    "TENSION_OPPOSED",
)

_HEAD_MODES: tuple[str, ...] = (
    "HEAD_BASKET",
    "HEAD_PEG",
    "HEAD_MARTINI",
    "HEAD_TULIP",
    "HEAD_OPEN_GALLERY",
)

_RETENTION_MODES: tuple[str, ...] = (
    "RETENTION_BEAD",
    "RETENTION_SHARED_BEAD",
    "RETENTION_MICRO_PRONG",
    "RETENTION_SHARED_PRONG",
)

#: Which `setting.type` value selects each PRIMARY family.
#:
#: The mapping is stated ONE WAY — mode id to family — and inverted where the
#: other direction is needed, because two hand-written tables are how a mapping
#: drifts.
_MODE_FAMILY: dict[str, str] = {
    "PRONG_ROUND": "PRONG",
    "PRONG_TAPERED": "PRONG",
    "PRONG_CLAW": "PRONG",
    "PRONG_V": "PRONG",
    "PRONG_SHARED": "PRONG",
    "BEZEL_FULL": "BEZEL",
    "BEZEL_PARTIAL": "BEZEL",
    "CHANNEL_LINEAR": "CHANNEL",
    "BAR_TRANSVERSE": "BAR",
    "FLUSH_GYPSY": "FLUSH",
    "TENSION_OPPOSED": "TENSION",
    "HEAD_BASKET": "HEAD",
    "HEAD_PEG": "HEAD",
    "HEAD_MARTINI": "HEAD",
    "HEAD_TULIP": "HEAD",
    "HEAD_OPEN_GALLERY": "HEAD",
    "RETENTION_BEAD": "RETENTION",
    "RETENTION_SHARED_BEAD": "RETENTION",
    "RETENTION_MICRO_PRONG": "RETENTION",
    "RETENTION_SHARED_PRONG": "RETENTION",
}

#: The `setting.type` value each PRIMARY family is selected by.
#:
#: The one place the UPPER CASE taxonomy family meets the lower case public
#: `SettingType` enum. Kept here rather than in the adapter so a consumer that
#: never touches JDL — Studio's capability display, a Forge rule — can still
#: answer "which type do I set to get this mode?".
PRIMARY_FAMILY_SETTING_TYPE: dict[str, str] = {
    "PRONG": "prong",
    "BEZEL": "bezel",
    "CHANNEL": "channel",
    "BAR": "bar",
    "FLUSH": "flush",
    "TENSION": "tension",
}

#: Which structure a mode attaches to.
#:
#: `HEAD` is the attachment plane the category integration supplies — the only
#: host the current primary families use, and the one every pre-Sprint-27
#: setting already attached to. Surface hosts are named by the pavé's own
#: `PaveHost` and are deliberately NOT duplicated here: a field on a band is a
#: pavé concern, and a second host enum would be the parallel registry §40
#: forbids.
SettingModeHost = Literal["HEAD"]

#: SOFTWARE SAFETY LIMITS, documented as such. A malformed or hostile document
#: must not be able to ask the kernel for an unbounded number of solids: a
#: pathological bar count or window count would otherwise exhaust memory before
#: any validation reported it. NOT jewelry limits — nothing here claims how
#: many bars a channel should have or how many windows a gallery may carry.
MAX_BAR_COUNT = 40
MAX_OPENING_COUNT = 24

#: Which `SettingModeParameters` fields each mode actually READS.
#:
#: THE AUTHORITY FOR "IS THIS PARAMETER APPLICABLE?", consumed by
#: `JM-SETTING-009` so an unread value is reported to its author rather than
#: silently dropped — the mechanism `JM-SETTING-006` already uses for
#: `prongStyle` on a bezel.
#:
#: A mode with an EMPTY tuple reads none of them, which is correct and not a
#: gap: the prong and bezel families' dimensions are the pre-existing flat
#: `setting.*` fields, and duplicating them into this model would put one
#: quantity in two places.
#:
#: A field that appears in NO tuple would be a parameter nothing reads, i.e.
#: the silently ignored field ARRANGE-GOV-011 forbids —
#: `test_extended_setting_modes.py` asserts every field of
#: `SettingModeParameters` is read by at least one mode.
MODE_PARAMETER_FIELDS: dict[str, tuple[str, ...]] = {
    "PRONG_ROUND": (),
    "PRONG_TAPERED": (),
    "PRONG_CLAW": (),
    "PRONG_V": (),
    "PRONG_SHARED": (),
    "BEZEL_FULL": (),
    "BEZEL_PARTIAL": (
        "openingCount",
        "openingSweepDeg",
        "openingStartAngleDeg",
    ),
    "CHANNEL_LINEAR": (
        "axisDeg",
        "spanMm",
        "innerWidthMm",
        "wallThicknessMm",
        "wallHeightMm",
        "termination",
        "symmetry",
        "offsetXMm",
        "offsetYMm",
        "offsetZMm",
    ),
    "BAR_TRANSVERSE": (
        "axisDeg",
        "barCount",
        "barSpacingMm",
        "barLengthMm",
        "barHeightMm",
        "wallThicknessMm",
        "symmetry",
        "offsetXMm",
        "offsetYMm",
        "offsetZMm",
    ),
    "FLUSH_GYPSY": (
        "collarWidthMm",
        "rimHeightMm",
        "offsetXMm",
        "offsetYMm",
        "offsetZMm",
    ),
    "TENSION_OPPOSED": (
        "gripAxisDeg",
        "padWidthMm",
        "padThicknessMm",
        "padDepthMm",
        "gripHeightMm",
        "offsetXMm",
        "offsetYMm",
        "offsetZMm",
    ),
    "HEAD_BASKET": (),
    "HEAD_PEG": (),
    "HEAD_MARTINI": (),
    "HEAD_TULIP": (),
    "HEAD_OPEN_GALLERY": (),
    "RETENTION_BEAD": (),
    "RETENTION_SHARED_BEAD": (),
    "RETENTION_MICRO_PRONG": (),
    "RETENTION_SHARED_PRONG": (),
}


class SettingModeParameters(BaseModel):
    """Construction parameters for a setting mode.

    ONE FLAT MODEL, NOT A DISCRIMINATED UNION, and that is a deliberate repeat
    of the judgment `SettingSpec` already documents: a discriminated union at
    the JDL layer cannot be reached by a dotted-path patch, which is exactly the
    defect Sprint 26 hit when Designer could not create a pavé. A flat model
    with per-mode fields keeps every route — a UI control, a natural-language
    request, a hand-written document — able to set one value.

    THE COST IS PAID EXPLICITLY. A field a mode does not read is reported as an
    INFORMATION result by `JM-SETTING-009` rather than silently ignored, the
    same mechanism `JM-SETTING-006` already uses for `prongStyle` on a bezel. An
    unread field is a fact the author deserves to be told, not a bug to hide.

    EVERY DEFAULT IS A CONSTRUCTION PARAMETER. None of them is a professional
    recommendation, a minimum, or a manufacturing tolerance; each was chosen to
    produce robust geometry inside the schema's own range
    (SETTING-GOV-010).
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    # ---- BEZEL_PARTIAL ------------------------------------------------------

    #: How many openings are cut through a partial bezel's wall.
    openingCount: int = Field(default=2, ge=1, le=MAX_OPENING_COUNT)

    #: Angular width of each opening, about the stone's own vertical axis.
    #:
    #: The openings are distributed evenly, so `openingCount * openingSweepDeg`
    #: must stay below 360 or nothing of the wall would remain — checked by the
    #: model validator below rather than clamped, because a clamp would build a
    #: wall the author did not describe.
    openingSweepDeg: float = Field(
        default=40.0, gt=0.0, le=180.0, allow_inf_nan=False
    )

    #: Where the first opening's centre sits, measured the same way.
    openingStartAngleDeg: float = Field(
        default=90.0, ge=-360.0, le=360.0, allow_inf_nan=False
    )

    # NOTE ON THE HEAD AXIS. An open gallery's window parameters are
    # deliberately NOT here. `mode` declares the PRIMARY mode, the head is a
    # separate axis already selected by `setting.headArchitecture`, and a field
    # in this model that only a head reads would be a field this mode never
    # applies — the silently ignored parameter ARRANGE-GOV-011 forbids. They
    # live beside the other flat head fields as `setting.galleryWindow*`.

    # ---- FLUSH_GYPSY --------------------------------------------------------

    #: How far the collar extends outward from the stone's own girdle outline.
    collarWidthMm: float = Field(
        default=1.0, gt=0.0, le=20.0, allow_inf_nan=False
    )

    #: How far the collar's top surface sits ABOVE the stone's girdle plane.
    #:
    #: This is what makes a flush setting flush: the stone is sunk into a metal
    #: mass whose top is level with part of its crown. It must stay BELOW the
    #: stone's own crown height or the stone would be entirely buried and the
    #: seat cut would leave a closed cavity rather than an opening — a GEOMETRIC
    #: precondition checked by `JM-SETTING-010` against the real generated
    #: stone, never a professional setting depth.
    rimHeightMm: float = Field(
        default=0.4, gt=0.0, le=20.0, allow_inf_nan=False
    )

    # ---- TENSION_OPPOSED ----------------------------------------------------

    #: Direction the two supports oppose each other along, in the stone's own
    #: horizontal frame. 0 places them on the +X/-X sides.
    gripAxisDeg: float = Field(
        default=0.0, ge=-360.0, le=360.0, allow_inf_nan=False
    )

    #: Width of each support, across the grip axis.
    padWidthMm: float = Field(default=2.0, gt=0.0, le=50.0, allow_inf_nan=False)

    #: Extent of each support along the grip axis — the shoulder's thickness.
    padThicknessMm: float = Field(
        default=1.6, gt=0.0, le=50.0, allow_inf_nan=False
    )

    #: How far each support reaches INWARD past the stone's own edge, so the
    #: support genuinely overlaps the stone's volume and the seat cut leaves a
    #: real groove rather than a tangent touch. A GEOMETRIC ROBUSTNESS value in
    #: the same class as `constants.EMBED_MM`, never a grip depth: nothing here
    #: models how hard the metal presses.
    padDepthMm: float = Field(default=0.6, gt=0.0, le=10.0, allow_inf_nan=False)

    #: How far each support rises above the stone's girdle plane.
    gripHeightMm: float = Field(
        default=1.2, gt=0.0, le=50.0, allow_inf_nan=False
    )

    # ---- CHANNEL_LINEAR and BAR_TRANSVERSE ----------------------------------

    #: Direction the channel or bar row runs, in the stone's own horizontal
    #: frame. 0 runs along +X.
    axisDeg: float = Field(default=0.0, ge=-360.0, le=360.0, allow_inf_nan=False)

    #: Length of the run along `axisDeg`.
    #:
    #: `None` means "as long as the stone it is built for", resolved from the
    #: stone reference by the generator. A channel around one stone is the
    #: single-stone case; a longer span is how a channel spans a row the
    #: arrangement placed, and stating it here is the only way the extent can
    #: exceed one stone without this layer computing placements
    #: (ARRANGE-GOV-006).
    spanMm: float | None = Field(
        default=None, gt=0.0, le=200.0, allow_inf_nan=False
    )

    #: Clear distance between the two channel walls, across the run.
    #:
    #: `None` means "the stone's own extent across the run", resolved from the
    #: stone reference. Stated explicitly when a row's stones are narrower or
    #: wider than the design's own stone.
    innerWidthMm: float | None = Field(
        default=None, gt=0.0, le=100.0, allow_inf_nan=False
    )

    #: Radial thickness of each channel wall, or of a bar.
    wallThicknessMm: float = Field(
        default=0.7, gt=0.0, le=20.0, allow_inf_nan=False
    )

    #: How far a channel wall rises above the stone's girdle plane.
    wallHeightMm: float = Field(
        default=0.8, gt=0.0, le=50.0, allow_inf_nan=False
    )

    #: How many bars a `BAR_TRANSVERSE` setting builds.
    barCount: int = Field(default=2, ge=1, le=MAX_BAR_COUNT)

    #: Centre-to-centre spacing between adjacent bars, along `axisDeg`.
    #:
    #: `None` means "the stone's own extent along the run plus one wall
    #: thickness", which places one bar on each side of a single stone. A POSITION
    #: parameter, never a clearance.
    barSpacingMm: float | None = Field(
        default=None, gt=0.0, le=100.0, allow_inf_nan=False
    )

    #: How far each bar rises above the stone's girdle plane.
    barHeightMm: float = Field(
        default=0.8, gt=0.0, le=50.0, allow_inf_nan=False
    )

    #: Length of each bar, across the run. `None` resolves to the channel's own
    #: `innerWidthMm` plus a wall thickness at each end, so a bar spans the run
    #: it crosses.
    barLengthMm: float | None = Field(
        default=None, gt=0.0, le=100.0, allow_inf_nan=False
    )

    termination: SettingTerminationMode = "OPEN"

    # ---- shared -------------------------------------------------------------

    #: Whether a run is centred on the stone or starts at it.
    #:
    #: A REAL GEOMETRIC DIFFERENCE, not a label. `SYMMETRIC` distributes a
    #: channel's span and a bar row about the stone's own centre; `ASYMMETRIC`
    #: starts the run AT that centre and extends along `axisDeg`, which is how a
    #: channel that runs off to one side of a centre stone is expressed. Read
    #: only by the CHANNEL and BAR modes; a mode that reads it not at all would
    #: be the silently ignored field ARRANGE-GOV-011 forbids, which is why the
    #: head's window parameters are not in this model.
    symmetry: SettingModeSymmetry = "SYMMETRIC"

    #: Offset of the mode's whole geometry from the stone's own centre, in the
    #: design frame. Exists so an asymmetric configuration is expressible
    #: without a second setting, and defaults to no offset so every existing
    #: construction is unchanged.
    offsetXMm: float = Field(default=0.0, ge=-50.0, le=50.0, allow_inf_nan=False)
    offsetYMm: float = Field(default=0.0, ge=-50.0, le=50.0, allow_inf_nan=False)
    offsetZMm: float = Field(default=0.0, ge=-50.0, le=50.0, allow_inf_nan=False)

    @model_validator(mode="after")
    def _openings_leave_wall(self) -> SettingModeParameters:
        """A partial bezel's openings must leave some wall behind.

        REFUSED, NOT CLAMPED. Reducing the sweep to fit would build a wall the
        author never described, which is the silent substitution
        SETTING-GOV-013 forbids.
        """

        total = self.openingCount * self.openingSweepDeg
        if total >= 360.0:
            raise ValueError(
                f"openingCount ({self.openingCount}) x openingSweepDeg "
                f"({self.openingSweepDeg}) is {total} degrees, which leaves no "
                "bezel wall. State a narrower opening or fewer of them — the "
                "values are not reduced for you, because a wall you did not "
                "describe is worse than a refusal."
            )
        return self



class SettingModeSpec(BaseModel):
    """A setting mode as a document declares it (Sprint 27).

    THE FIRST-CLASS DECLARATION, carried directly in JDL as
    `setting.mode`. Absent by default: a document that declares no mode gets
    the mode `resolve_primary_mode()` derives from its existing
    `type`/`prongStyle` fields, which is what keeps every pre-Sprint-27
    document generating exactly the geometry it did.

    IT REFINES `setting.type`, IT DOES NOT COMPETE WITH IT. `type` names the
    family and selects the generator; a mode names the variant within that
    family and carries its parameters. A mode whose family disagrees with
    `type` is refused by `JM-SETTING-008` rather than resolved by precedence —
    two authorities over one setting have no determinate resolution, the same
    reason `JM-FAMILY-001` refuses a family and an arrangement together.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    modeId: SettingModeId

    #: Whether the mode participates in geometry. `false` keeps the parameters
    #: in the document and falls back to the family's own default variant, which
    #: is what lets an author switch a variant off without losing how it was
    #: configured — a different state from having declared no mode at all.
    enabled: bool = True

    #: Which stone specification this mode holds. `"primary"` is the
    #: definition's own `stone`; any other value names a future named
    #: specification and is reported unresolved rather than silently treated as
    #: the primary one (the discipline `PaveDefinition.stoneRef` established).
    stoneRef: str = Field(default="primary", min_length=1, max_length=80)

    #: Which arrangement instances this mode holds, when it holds more than the
    #: design's own stone — a channel spanning a row, a bar between two stones.
    #:
    #: OPAQUE IDS, CARRIED AND NEVER RESOLVED: nothing under
    #: `jewelmind/setting/` may import the arrangement layer
    #: (SETTINGV2-GOV-011), so this records the association and the arrangement
    #: remains the authority on where those instances are.
    arrangementInstanceIds: list[str] = Field(
        default_factory=list, max_length=120
    )

    host: SettingModeHost = "HEAD"

    parameters: SettingModeParameters = Field(
        default_factory=SettingModeParameters
    )

    #: A human label, carried through for Studio. Never used for identity.
    label: str | None = Field(default=None, max_length=120)


def mode_axis(mode_id: str) -> SettingModeAxis:
    """Which pipeline axis a mode belongs to.

    Derived from the id tables rather than declared per row, so a new mode
    cannot be added to `SettingModeId` without being placed on an axis.
    """

    if mode_id in _PRIMARY_MODES:
        return "PRIMARY"
    if mode_id in _HEAD_MODES:
        return "HEAD"
    if mode_id in _RETENTION_MODES:
        return "RETENTION"
    raise KeyError(
        f"Setting mode {mode_id!r} is on no known axis. Every member of "
        "SettingModeId must appear in exactly one axis tuple."
    )


def mode_family(mode_id: str) -> SettingModeFamily:
    """The technique family a mode belongs to."""

    family = _MODE_FAMILY.get(mode_id)
    if family is None:
        raise KeyError(f"Setting mode {mode_id!r} has no family.")
    return family  # type: ignore[return-value]


def modes_on_axis(axis: SettingModeAxis) -> tuple[str, ...]:
    """Every implemented mode on one axis, sorted."""

    return tuple(
        sorted(
            mode_id
            for mode_id in _MODE_FAMILY
            if mode_axis(mode_id) == axis
        )
    )


#: The prong body style each PRONG mode builds.
#:
#: `PRONG_SHARED` maps to the round body because sharing is orthogonal to the
#: body shape — a shared prong may be round, claw or V — and the round cylinder
#: is the default every other axis already uses.
_PRONG_MODE_STYLE: dict[str, str] = {
    "PRONG_ROUND": "ROUND_PRONG",
    "PRONG_TAPERED": "TAPERED_PRONG",
    "PRONG_CLAW": "CLAW_PRONG",
    "PRONG_V": "V_PRONG",
    "PRONG_SHARED": "ROUND_PRONG",
}

#: The head architecture each HEAD mode builds. A plain inversion, stated once.
_HEAD_MODE_ARCHITECTURE: dict[str, str] = {
    "HEAD_BASKET": "BASKET",
    "HEAD_PEG": "PEG_HEAD",
    "HEAD_MARTINI": "MARTINI",
    "HEAD_TULIP": "TULIP",
    "HEAD_OPEN_GALLERY": "OPEN_GALLERY",
}

#: The pavé retention strategy each RETENTION mode builds.
_RETENTION_MODE_STRATEGY: dict[str, str] = {
    "RETENTION_BEAD": "BEAD",
    "RETENTION_SHARED_BEAD": "SHARED_BEAD",
    "RETENTION_MICRO_PRONG": "MICRO_PRONG",
    "RETENTION_SHARED_PRONG": "SHARED_PRONG",
}


def prong_style_for_mode(mode_id: str) -> str | None:
    return _PRONG_MODE_STYLE.get(mode_id)


def head_architecture_for_mode(mode_id: str) -> str | None:
    return _HEAD_MODE_ARCHITECTURE.get(mode_id)


def retention_strategy_for_mode(mode_id: str) -> str | None:
    return _RETENTION_MODE_STRATEGY.get(mode_id)


def mode_for_prong_style(style: str) -> str:
    """The PRONG mode a body style corresponds to.

    Inverted from `_PRONG_MODE_STYLE` rather than written out again, and
    `PRONG_SHARED` is excluded from the inversion because it shares the round
    body — a style alone can never imply sharing.
    """

    for mode_id, mapped in _PRONG_MODE_STYLE.items():
        if mapped == style and mode_id != "PRONG_SHARED":
            return mode_id
    raise KeyError(f"No prong mode builds style {style!r}.")


def mode_for_head_architecture(architecture: str) -> str:
    for mode_id, mapped in _HEAD_MODE_ARCHITECTURE.items():
        if mapped == architecture:
            return mode_id
    raise KeyError(f"No head mode builds architecture {architecture!r}.")


def mode_for_retention_strategy(strategy: str) -> str:
    for mode_id, mapped in _RETENTION_MODE_STRATEGY.items():
        if mapped == strategy:
            return mode_id
    raise KeyError(f"No retention mode builds strategy {strategy!r}.")


#: The variant each PRIMARY family falls back to when a document declares no
#: mode. Every one of them reproduces the pre-Sprint-27 construction for that
#: family, which is what makes the fallback a compatibility guarantee rather
#: than a preference.
_DEFAULT_PRIMARY_MODE: dict[str, str] = {
    "prong": "PRONG_ROUND",
    "bezel": "BEZEL_FULL",
    "channel": "CHANNEL_LINEAR",
    "bar": "BAR_TRANSVERSE",
    "flush": "FLUSH_GYPSY",
    "tension": "TENSION_OPPOSED",
}


def default_primary_mode(setting_type: str, prong_style: str = "ROUND_PRONG") -> str:
    """The PRIMARY mode a document with no `setting.mode` resolves to.

    For a prong setting the answer comes from `prongStyle`, which already
    carried the variant before this sprint; for every other family there is one
    default variant. Stated as a function rather than a table lookup at the call
    site so there is exactly one definition of "what did this document mean
    before setting modes existed".
    """

    if setting_type == "prong":
        return mode_for_prong_style(prong_style)
    mode = _DEFAULT_PRIMARY_MODE.get(setting_type)
    if mode is None:
        raise KeyError(
            f"No default setting mode is defined for setting type "
            f"{setting_type!r}. Every member of SettingType must have one, or a "
            "document choosing it would resolve to nothing."
        )
    return mode


def default_mode_parameters() -> SettingModeParameters:
    """The parameters a mode gets when it is switched on with no values.

    ONE DEFINITION OF "TURN THIS MODE ON", owned by the domain rather than by
    each interface — the discipline `default_pave_field()` established after
    Designer and Studio could otherwise have produced different designs from
    the same instruction.
    """

    return SettingModeParameters()


class ResolvedSettingMode(BaseModel):
    """The mode a design actually uses, after resolution.

    THE SINGLE RESOLUTION POINT every consumer must read, the role
    `family/effective.py::effective_arrangement()` plays for placement. A second
    consumer deriving the mode from `type`/`prongStyle` itself would eventually
    disagree, and the disagreement would surface as geometry that does not match
    what Studio displayed.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    modeId: SettingModeId
    axis: SettingModeAxis
    family: SettingModeFamily
    settingType: str
    parameters: SettingModeParameters

    #: True when the mode was derived from the pre-Sprint-27 fields rather than
    #: declared. Carried so a report can say which, instead of a consumer
    #: having to guess whether a document opted in.
    derived: bool

    stoneRef: str = "primary"
    arrangementInstanceIds: list[str] = Field(default_factory=list)


def resolve_primary_mode(
    setting_type: str,
    prong_style: str = "ROUND_PRONG",
    mode: SettingModeSpec | None = None,
) -> ResolvedSettingMode:
    """The PRIMARY setting mode this design uses.

    Three cases, and the first two are the compatibility path:

    1. No mode declared -> derived from `type` (+ `prongStyle` for a prong).
    2. A mode declared but disabled -> the same derived default, with the
       declared parameters DISCARDED. A disabled mode contributes nothing, and
       honouring half of it would be neither state.
    3. A mode declared and enabled -> that mode, with its parameters.

    Raises on a family mismatch rather than choosing a winner. See
    `SettingModeSpec` for why precedence is refused.
    """

    if mode is None or not mode.enabled:
        return ResolvedSettingMode(
            modeId=default_primary_mode(setting_type, prong_style),  # type: ignore[arg-type]
            axis="PRIMARY",
            family=mode_family(default_primary_mode(setting_type, prong_style)),
            settingType=setting_type,
            parameters=default_mode_parameters(),
            derived=True,
        )

    axis = mode_axis(mode.modeId)
    if axis != "PRIMARY":
        raise ValueError(
            f"setting.mode '{mode.modeId}' is a {axis} mode, not a PRIMARY one. "
            "The head architecture is chosen by setting.headArchitecture and "
            "field retention by the pave's own retention strategy; declaring "
            "one here would be a second authority over an axis that already "
            "has one."
        )

    family = mode_family(mode.modeId)
    expected_type = PRIMARY_FAMILY_SETTING_TYPE[family]
    if expected_type != setting_type:
        raise ValueError(
            f"setting.mode '{mode.modeId}' belongs to the {family} family, "
            f"which is selected by setting.type '{expected_type}', but "
            f"setting.type is '{setting_type}'. Refused rather than resolved by "
            "precedence: two authorities over one setting have no determinate "
            "resolution."
        )

    return ResolvedSettingMode(
        modeId=mode.modeId,
        axis="PRIMARY",
        family=family,
        settingType=setting_type,
        parameters=mode.parameters,
        derived=False,
        stoneRef=mode.stoneRef,
        arrangementInstanceIds=list(mode.arrangementInstanceIds),
    )


#: Length of a setting-mode fingerprint, matching every other identity in the
#: project (`definitionHash`, `arrangementFingerprint`, `compilationHash`).
MODE_FINGERPRINT_LENGTH = 16


def setting_mode_fingerprint(resolved: ResolvedSettingMode) -> str:
    """Deterministic identity of a resolved setting mode.

    THE MODE'S OWN CONTENT AND NOTHING ELSE — no wall-clock time, no random
    value, no process id, no memory address and no iteration order
    (ARRANGE-GOV-004's discipline, restated here because this is a new
    identity).

    NOT A REPLACEMENT FOR ANY EXISTING IDENTITY. `definitionHash` still
    identifies the whole document and `geometryHash` the geometry-driving part
    of it; this identifies one mode, so a report can say which mode built a
    component without re-deriving it (ARRANGE-GOV-007's separation).

    `derived` is deliberately EXCLUDED: a document that declares
    `PRONG_ROUND` explicitly and one that reaches it through `prongStyle`
    describe the same setting and must fingerprint the same, or the identity
    would encode how the author typed it rather than what they meant.
    """

    payload = {
        "modeId": resolved.modeId,
        "axis": resolved.axis,
        "family": resolved.family,
        "settingType": resolved.settingType,
        "stoneRef": resolved.stoneRef,
        # Sorted: an id set has no order, so two documents listing the same
        # instances differently describe one setting.
        "arrangementInstanceIds": sorted(resolved.arrangementInstanceIds),
        "parameters": resolved.parameters.model_dump(mode="json"),
        "taxonomyVersion": SETTING_MODE_TAXONOMY_VERSION,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[
        :MODE_FINGERPRINT_LENGTH
    ]
