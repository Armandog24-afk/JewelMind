"""Pavé and microsetting domain models (Sprint 26).

FIVE SEPARATE QUESTIONS, and this package answers exactly one of them:

    WHAT the stones are          Stone System v2      (`stone.shape`, dimensions)
    WHAT they are made of        Gem Identity v1      (`GemIdentity`)
    WHICH individual stones      Arrangement v1       (`StoneInstanceDef`)
    WHERE they sit               Arrangement v1       (`InstanceTransform`)
    HOW metal holds them         Setting System v2    (retention builders)
    ------------------------------------------------------------------
    WHICH FIELD they populate    THIS PACKAGE

A pavé is a RULE FOR POPULATING A SURFACE. It says "cover this region of this
host, at this pitch, in this pattern, held this way" — and then compiles into
arrangement primitives so the Stone Arrangement Engine does every piece of
placement arithmetic. Nothing here computes a position the arrangement layer
would compute differently.

PAVÉ AND MICROSETTING ARE TWO MODELS, not one with a flag, because they answer
different questions:

- `PaveSpec` populates a SURFACE REGION: an angular span and a width, filled at
  a pitch. The designer states the area and the density; the count follows.
- `MicrosettingSpec` builds a RETENTION TOPOLOGY for small stones: an explicit
  row and column count with explicit spacings. The designer states the
  structure; the area follows.

They share primitives — the same host surface, the same pattern layer, the same
retention model — because they are two ways of describing one lattice, not two
lattices.

WHAT THIS PACKAGE IS NOT:

- **Not a placement engine.** `compile.py` emits `StoneInstanceDef`s; the
  arrangement resolver resolves them.
- **Not a stone or gem model.** A pavé references a stone specification and may
  carry a gem identity. Nothing about the stone is copied.
- **Not a setting implementation.** Retention is named here and BUILT by the
  Setting System.
- **Not geometry.** No field holds a kernel object.
- **Not category-specific.** Nothing here imports a jewelry category; a host
  surface is named abstractly and resolved to numbers by the category adapter.

NO INVENTED PROFESSIONAL THRESHOLD. Every spacing, pitch, bead radius and seat
depth here is a CONSTRUCTION PARAMETER supplied by the document. This layer
knows no stone's size, so it cannot claim two stones do not touch — whether
they do is a GEOMETRIC fact for Geometry Inspection, and whether the result
could be cut by a setter is a professional question nobody here can answer.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from jewelmind.arrangement.models import (
    ARRANGEMENT_ID_PATTERN,
    MAX_ARRANGEMENT_ID_LENGTH,
    InstanceTransform,
)
from jewelmind.gem.models import GemIdentity

#: Pavé ids share the arrangement's id shape, because a pavé stone BECOMES an
#: arrangement instance and its derived id becomes that instance's id. Reusing
#: the pattern means one validator covers the whole chain, and a pavé id can
#: never become a filesystem path or a shell argument.
PAVE_ID_PATTERN = ARRANGEMENT_ID_PATTERN
MAX_PAVE_ID_LENGTH = MAX_ARRANGEMENT_ID_LENGTH

#: SOFTWARE SAFETY LIMITS, documented as such (Sprint 26 brief §33). A
#: malformed or hostile document must not be able to ask the kernel for an
#: unbounded number of solids: a pathological pitch on a wide span would
#: otherwise produce tens of thousands of stones and exhaust memory before any
#: validation reported it. NOT jewelry limits: nothing here claims how many
#: stones a pavé should carry or how densely they may sit.
MAX_PAVE_STONES = 120
MAX_PAVE_ROWS = 12
MAX_PAVE_COLUMNS = 60
MAX_EXPLICIT_PLACEMENTS = MAX_PAVE_STONES

#: The two first-class field kinds.
PaveKind = Literal["PAVE", "MICROSETTING"]

#: How the lattice is laid out over the host surface.
#:
#: `GRID`       - rows and columns aligned.
#: `STAGGERED`  - alternate rows shifted by half the column pitch.
#: `ROW_OFFSET` - every row shifted by a declared fraction of the column pitch,
#:                which is a superset of STAGGERED and is kept separate because
#:                a half shift is the case a designer names.
#: `RADIAL`     - stones distributed around the surface's own axis, for a host
#:                whose natural parameterization is angular.
#: `EXPLICIT`   - the document states each placement itself.
#:
#: A pattern named here but with no generator would be the silently ignored
#: field this project keeps refusing to add; `compile.py::pave_patterns()` is
#: the registry and a test asserts the two agree in both directions.
PavePattern = Literal["GRID", "STAGGERED", "ROW_OFFSET", "RADIAL", "EXPLICIT"]

#: Which surface a field is applied to.
#:
#: `BAND_OUTER` - the shank's outer surface: cylindrical, and the classic
#:                shank pavé. Executable because Sprint 26 gave the arrangement
#:                a real axis tilt, so a stone follows the surface normal.
#: `HEAD_PLANE` - the horizontal plane at the top of the head. Planar, so no
#:                tilt is needed.
#:
#: Reserved targets live in `capability.py::RESERVED_PAVE_HOSTS` and are
#: deliberately NOT members, because a target with no resolver cannot be
#: honoured and must not be accepted. `HALO_PLANE` is among them, and the
#: reason is worth stating here too: a halo has no metal (Sprint 25 recorded
#: halo retention as PLANNED), so a pavé in a halo's plane would have nothing
#: to fuse its beads into and would ship a disconnected production solid.
PaveHost = Literal["BAND_OUTER", "HEAD_PLANE"]

#: How metal holds the stones.
#:
#: `NONE`        - no retention metal. An honest option: it produces the stone
#:                 field alone, which is what a preview of a stone layout is.
#: `BEAD`        - one bead per lattice corner of each stone, individually.
#: `SHARED_BEAD` - one bead per lattice corner, shared by every stone touching
#:                 it. Genuinely fewer beads, which is the point of the
#:                 technique rather than a rendering shortcut.
#: `MICRO_PRONG` - a small cylinder normal to the surface at each corner.
#: `SHARED_PRONG` - a micro prong at each SHARED corner, serving every stone
#:                 touching it (Sprint 27). Sharing is a property of the ANCHOR
#:                 SET rather than of the solid, which is why this and
#:                 `MICRO_PRONG` reach the same builder — exactly as `BEAD` and
#:                 `SHARED_BEAD` already do.
#:
#: Reserved strategies (`CHANNEL`, `GRAIN`) live in
#: `capability.py::RESERVED_RETENTION_STRATEGIES`. A channel rail is
#: deliberately NOT a pavé retention strategy: these anchors are lattice
#: CORNERS, which is the right topology for a bead or a prong and the wrong one
#: for a rail running the whole row. Channel setting exists as its own Setting
#: System family instead (Sprint 27).
PaveRetentionStrategy = Literal[
    "NONE", "BEAD", "SHARED_BEAD", "MICRO_PRONG", "SHARED_PRONG"
]

#: Strategies whose anchors are SHARED between the stones that touch them.
#:
#: Stated once, here, because it is the property the anchor derivation actually
#: switches on: a shared strategy leaves its piece exactly on the corner where
#: cells meet, while an individual one draws it in toward its own stone. Two
#: copies of this membership test is how a new shared strategy silently becomes
#: an individual one.
SHARED_RETENTION_STRATEGIES: tuple[str, ...] = ("SHARED_BEAD", "SHARED_PRONG")

#: What happens to a lattice cell that falls outside the host's declared
#: extent.
#:
#: `CLIP`   - drop it. The field ends where the surface ends.
#: `REJECT` - refuse the whole pavé. For a caller who would rather fix the
#:            parameters than receive a quietly smaller field.
PaveContainmentPolicy = Literal["CLIP", "REJECT"]

#: How a row ends at the edge of its span.
#:
#: `FULL_STONES`  - only whole stones, so a row may stop short of the edge.
#: `CENTERED`     - the row is centred in its span, so both margins are equal.
#:
#: Neither is a professional statement about how a setter finishes an edge; both
#: are deterministic layout rules.
PaveTermination = Literal["FULL_STONES", "CENTERED"]

PaveSymmetry = Literal["SYMMETRIC", "ASYMMETRIC"]

#: The instance id the design's own centre stone takes when a pavé is declared
#: with no family, halo or explicit arrangement to supply one.
#:
#: THE SAME LITERAL the family compiler derives (`CENTER_MEMBER_ID`) and the
#: halo defaults to (`DEFAULT_CENTER_MEMBER_ID`), so the three layers name one
#: stone one way. Asserted equal across all three by `test_pave.py`, because
#: three copies of a string is exactly how they drift.
DESIGN_CENTER_INSTANCE_ID = "center"


class PaveModel(BaseModel):
    """Strict, kernel-neutral, immutable base.

    `strict=True` matches `domain/schema.py::StrictModel` and every sibling
    domain package: these models are carried DIRECTLY in JDL rather than through
    a hand-written `Jdl*` mirror, so they apply JDL's own untrusted-input
    policy. A JSON string `"0.15"` is not an acceptable pitch.

    `frozen=True` because a pavé is replaced, never mutated: compilation returns
    new objects, so a shared reference cannot be edited out from under a
    computed fingerprint.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class PaveRetention(PaveModel):
    """How metal holds the field's stones.

    A REQUEST plus its construction parameters. The Setting System owns what a
    bead IS and builds it; this states which strategy the field wants and at
    what size. Keeping the two apart is why there is no second prong model
    here.
    """

    strategy: PaveRetentionStrategy = "SHARED_BEAD"

    #: Radius of one bead, or of one micro-prong, in millimetres.
    #:
    #: A CONSTRUCTION PARAMETER with a software default, NOT a minimum bead
    #: size: no sourced professional evidence says how small a bead may be, so
    #: none is enforced. Forge checks only that the value is finite and
    #: positive, and that it is consistent with the geometry it must produce.
    beadRadiusMm: float = Field(
        default=0.18, gt=0.0, le=5.0, allow_inf_nan=False
    )

    #: How far a bead's centre sits BELOW the host surface, so the fuse into the
    #: host produces genuine 3D overlap rather than a tangent touch OCCT would
    #: leave as two solids. The same reasoning as `constants.EMBED_MM`; a
    #: geometric robustness value, not a setting depth.
    beadEmbedMm: float = Field(
        default=0.06, ge=0.0, le=5.0, allow_inf_nan=False
    )

    #: Height of a micro-prong above the host surface. Ignored by the bead
    #: strategies.
    prongHeightMm: float = Field(
        default=0.35, gt=0.0, le=10.0, allow_inf_nan=False
    )


class PaveSeat(PaveModel):
    """Whether the host metal is recessed for the stones.

    A CUT, NEVER A FUSE, enforced at the geometry layer by reusing
    `setting/seat.py` — the module whose own source is asserted never to call
    `.fuse()` on a stone shape (SETTINGV2-GOV-008, LAW-006).

    `REFERENCE_RECESS` is deliberately not called a seat: it has no bearing
    shoulder and makes no claim that a stone would sit correctly in it. It is
    the stone's own volume removed from the host, which is a real recess and
    nothing more.
    """

    mode: Literal["NONE", "REFERENCE_RECESS"] = "NONE"

    #: How much larger than the stone the cutting tool is, so the boolean is
    #: not an exactly tangent cut. A GEOMETRIC ROBUSTNESS value, carried
    #: straight through to the Setting System's own seat clearance.
    clearanceMm: float = Field(
        default=0.02, ge=0.0, le=1.0, allow_inf_nan=False
    )


class PaveExplicitPlacement(PaveModel):
    """One stone placed by the document rather than by the pattern.

    THE ESCAPE HATCH, and it reuses the arrangement's own `InstanceTransform`
    verbatim rather than declaring a parallel transform model — the value this
    carries IS an arrangement transform, and is handed to the arrangement
    unchanged.
    """

    placementId: str = Field(
        pattern=PAVE_ID_PATTERN, max_length=MAX_PAVE_ID_LENGTH
    )
    transform: InstanceTransform

    #: This stone's own gem and scale, for a field that is not uniform.
    gem: GemIdentity | None = None
    scale: float | None = Field(
        default=None, gt=0.01, le=10.0, allow_inf_nan=False
    )


class PaveSpec(PaveModel):
    """SURFACE POPULATION: cover a region at a pitch.

    The designer states the AREA and the DENSITY; the stone count follows. That
    is the difference from a microsetting, where the count is stated and the
    area follows — and it is why these are two models rather than one with a
    flag.

    `angularSpanDeg` and `axialSpanMm` describe the region in the host
    surface's OWN parameterization: an angle about the surface axis and a
    distance along it. For a planar host the angular span is read as a sweep
    about the surface's normal and the axial span as a radius extent, which is
    what makes one spec cover both a shank and a flat gallery.
    """

    kind: Literal["PAVE"] = "PAVE"

    #: Extent of the field around the host surface's axis.
    angularSpanDeg: float = Field(gt=0.0, le=360.0, allow_inf_nan=False)

    #: Where the field starts, in the same angular parameterization.
    startAngleDeg: float = Field(
        default=0.0, ge=-360.0, le=360.0, allow_inf_nan=False
    )

    #: Extent of the field along the host surface's axis. `None` means "the
    #: host's own full extent", resolved by the category adapter rather than
    #: guessed here.
    axialSpanMm: float | None = Field(
        default=None, gt=0.0, le=200.0, allow_inf_nan=False
    )

    #: Centre-to-centre pitch between adjacent stones along the surface, in
    #: millimetres. A POSITION parameter, never a clearance.
    pitchMm: float = Field(gt=0.0, le=50.0, allow_inf_nan=False)

    #: Centre-to-centre pitch between rows. `None` uses `pitchMm`, which is the
    #: square lattice a single number describes.
    rowPitchMm: float | None = Field(
        default=None, gt=0.0, le=50.0, allow_inf_nan=False
    )

    #: How many rows across the axial span.
    rowCount: int = Field(default=1, ge=1, le=MAX_PAVE_ROWS)

    pattern: PavePattern = "GRID"

    #: Fraction of the column pitch each successive row is shifted by. Only
    #: `ROW_OFFSET` reads it; `STAGGERED` is the fixed 0.5 case.
    rowOffsetFraction: float = Field(
        default=0.5, ge=-1.0, le=1.0, allow_inf_nan=False
    )

    termination: PaveTermination = "CENTERED"
    symmetry: PaveSymmetry = "SYMMETRIC"


class MicrosettingSpec(PaveModel):
    """SMALL-STONE RETENTION TOPOLOGY: a stated structure.

    The designer states the ROWS and COLUMNS and their spacings; the area
    follows. That is the inverse of a `PaveSpec`, and the reason both exist: a
    microsetting is specified as a structure to be cut, not as a region to be
    covered.
    """

    kind: Literal["MICROSETTING"] = "MICROSETTING"

    #: Stones per row.
    columnCount: int = Field(ge=1, le=MAX_PAVE_COLUMNS)

    #: Number of rows.
    rowCount: int = Field(default=1, ge=1, le=MAX_PAVE_ROWS)

    #: Centre-to-centre spacing between stones in a row.
    stoneSpacingMm: float = Field(gt=0.0, le=50.0, allow_inf_nan=False)

    #: Centre-to-centre spacing between rows. `None` uses `stoneSpacingMm`.
    rowSpacingMm: float | None = Field(
        default=None, gt=0.0, le=50.0, allow_inf_nan=False
    )

    #: Where the structure starts around the host surface's axis.
    startAngleDeg: float = Field(
        default=0.0, ge=-360.0, le=360.0, allow_inf_nan=False
    )

    #: Offset of the whole structure along the host surface's axis, so a
    #: microsetting need not be centred.
    axialOffsetMm: float = Field(
        default=0.0, ge=-100.0, le=100.0, allow_inf_nan=False
    )

    pattern: PavePattern = "STAGGERED"

    rowOffsetFraction: float = Field(
        default=0.5, ge=-1.0, le=1.0, allow_inf_nan=False
    )

    termination: PaveTermination = "CENTERED"
    symmetry: PaveSymmetry = "SYMMETRIC"


PaveFieldSpec = PaveSpec | MicrosettingSpec


class PaveDefinition(PaveModel):
    """A pavé or microsetting field.

    `spec` says how the lattice is described, `host` says which surface it is
    applied to, `retention` says how metal holds it, and `seat` says whether the
    host is recessed for it. Compilation turns the first two into a real
    `ArrangementDefinition`, which is where placement actually lives.

    ABSENT IS NOT EMPTY. A definition with no pavé behaves exactly as it did
    before this sprint. `enabled: false` keeps the parameters in the document
    and produces no stones — which is what lets a designer switch a field off
    without losing how it was configured, and is a different state from having
    no pavé at all.
    """

    paveId: str = Field(
        default="pave", pattern=PAVE_ID_PATTERN, max_length=MAX_PAVE_ID_LENGTH
    )

    #: Whether the field participates in geometry. `false` is carried through
    #: to every report, so a disabled pavé is visible as disabled rather than
    #: absent.
    enabled: bool = True

    #: Which of the two first-class field kinds this is. Checked against
    #: `spec.kind`, because two fields naming the same thing can disagree.
    kind: PaveKind
    spec: PaveFieldSpec = Field(discriminator="kind")

    host: PaveHost

    #: Which stone specification the field's stones are occurrences of.
    #: `"primary"` is the definition's own `stone`; any other value names a
    #: future named specification and is reported unresolved rather than
    #: silently treated as the primary one.
    stoneRef: str = Field(
        default="primary", pattern=PAVE_ID_PATTERN, max_length=MAX_PAVE_ID_LENGTH
    )

    #: Uniform scale applied to the referenced stone. A pavé stone is normally
    #: far smaller than a centre stone, and this is how that is expressed
    #: without a second stone specification.
    stoneScale: float = Field(
        default=0.12, gt=0.001, le=10.0, allow_inf_nan=False
    )

    #: Each stone's own spin about its axis, in degrees.
    stoneOrientationDeg: float = Field(
        default=0.0, ge=-360.0, le=360.0, allow_inf_nan=False
    )

    #: The field's gem. `None` inherits the referenced stone's, which is what
    #: makes "the whole pavé in the same material" one edit rather than sixty.
    gem: GemIdentity | None = None

    retention: PaveRetention = Field(default_factory=PaveRetention)
    seat: PaveSeat = Field(default_factory=PaveSeat)

    containment: PaveContainmentPolicy = "CLIP"

    #: Placements the document states itself, used by the `EXPLICIT` pattern.
    #: Ignored by every other pattern rather than silently merged, so a
    #: leftover list cannot change a generated field.
    explicitPlacements: list[PaveExplicitPlacement] = Field(
        default_factory=list, max_length=MAX_EXPLICIT_PLACEMENTS
    )

    #: A human label, carried through for Studio. Never used for identity.
    label: str | None = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def _spec_kind_matches_the_field_kind(self) -> PaveDefinition:
        """The discriminator and the declared kind must agree.

        A field whose `kind` says PAVE while its `spec` describes a
        microsetting has no determinate meaning. Checked here rather than
        collapsing the two, because `kind` is what consumers switch on and the
        discriminated union is what gives each field its own typed parameters.
        """

        if self.spec.kind != self.kind:
            raise ValueError(
                f"pave.spec.kind '{self.spec.kind}' does not match "
                f"pave.kind '{self.kind}'."
            )
        return self

    @model_validator(mode="after")
    def _explicit_pattern_needs_placements(self) -> PaveDefinition:
        """`EXPLICIT` with no placements raises rather than falling back.

        The same discipline SETTINGV2-GOV-012 applies to explicit prong
        layouts: silently producing a derived lattice for a document that asked
        for explicit placement would build a field nobody authored.
        """

        if self.spec.pattern == "EXPLICIT" and not self.explicitPlacements:
            raise ValueError(
                "pave.spec.pattern is 'EXPLICIT' but pave.explicitPlacements is "
                "empty. State the placements, or choose a generated pattern — a "
                "derived lattice here would be a field nobody authored."
            )
        return self

    @model_validator(mode="after")
    def _explicit_placement_ids_are_unique(self) -> PaveDefinition:
        """Ids are the authoritative identity, so a duplicate makes every
        reference to it — a relation, a generated component, an inspection
        fact — ambiguous."""

        seen: set[str] = set()
        for placement in self.explicitPlacements:
            if placement.placementId in seen:
                raise ValueError(
                    "pave.explicitPlacements contains duplicate placementId "
                    f"'{placement.placementId}'."
                )
            seen.add(placement.placementId)
        return self

    @model_validator(mode="after")
    def _declared_lattice_is_bounded(self) -> PaveDefinition:
        """A stated structure must fit the software bound BEFORE compilation.

        A microsetting states its own count, so an over-capacity field is
        knowable from the document alone and is refused at the schema layer
        rather than after the kernel has been asked for the solids. A
        `PaveSpec`'s count is derived, so `compile.py` bounds that one.
        """

        spec = self.spec
        if isinstance(spec, MicrosettingSpec):
            total = spec.columnCount * spec.rowCount
            if total > MAX_PAVE_STONES:
                raise ValueError(
                    f"this microsetting declares {total} stones "
                    f"({spec.columnCount} x {spec.rowCount}), above the software "
                    f"bound of {MAX_PAVE_STONES}. An implementation limit, not a "
                    "statement about how many stones a design should have."
                )
        return self


def default_pave_field(kind: PaveKind = "PAVE") -> PaveDefinition:
    """The field a caller gets when a pavé is switched on with no parameters.

    ONE DEFINITION OF "TURN THE PAVÉ ON", owned by the domain rather than by
    each interface. Designer materializes this before applying a `pave.*`
    patch, because a dotted-path patch cannot construct a discriminated union
    from nothing; the Studio panel offers the same field. Two copies of it
    would let a natural-language request and a UI toggle produce different
    designs from the same instruction.

    NOT A RECOMMENDATION. Every value is a construction default inside the
    schema's own range, immediately editable, and none of them is professionally
    validated: a single shank row at a 1mm pitch is the least surprising thing
    that builds, not a proportion anyone has reviewed.
    """

    spec: PaveFieldSpec = (
        MicrosettingSpec(columnCount=12, stoneSpacingMm=1.0, rowCount=1)
        if kind == "MICROSETTING"
        else PaveSpec(angularSpanDeg=90.0, pitchMm=1.0, rowCount=1)
    )
    return PaveDefinition(
        kind=kind, host="BAND_OUTER", spec=spec, stoneScale=0.1
    )
