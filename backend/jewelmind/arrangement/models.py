"""Category-neutral Stone Arrangement domain models (Sprint 22).

WHAT THIS LAYER IS. A declarative description of WHICH stones participate in a
design and WHERE they sit relative to a reference frame. It answers "there is a
6.5 mm round centre stone, and eight 1.3 mm accents evenly spaced around it at
radius 4.6 mm" — as data.

WHAT THIS LAYER IS NOT, and must never become:

- Not a geometry engine. No field holds a CadQuery/OCP object, and nothing here
  constructs a solid. `resolve.py` produces NUMBERS; Atlas turns numbers into
  geometry.
- Not a constraint solver. Every model resolves by direct evaluation in a fixed
  order — no iteration to convergence, no search, no solver state. A general
  solver would make the output depend on iteration order and starting values,
  which is exactly the determinism this layer has to guarantee.
- Not a jewelry-rule layer. No minimum spacing, no maximum stone count, no
  "accents should be 20% of the centre". Those are Forge's business if they are
  ever sourced, and inventing them here would hide a professional claim inside
  a data model.
- Not category-specific. Nothing imports `jewelmind.ring`,
  `jewelmind.jewelry_category`, `jewelmind.geometry`, or `JewelryDefinition`.
  A future earring arrangement uses these same models unchanged.

THE THREE-WAY SEPARATION THIS SPRINT ADDS. Sprint 20 separated a stone's
geometry from its cut; Sprint 21 separated its gem identity from its geometry.
This sprint separates a stone's OCCURRENCE from both:

    StoneSpec        - what a stone IS (shape, dimensions, source)
    GemIdentity      - what it is MADE OF
    StoneInstanceDef - THIS occurrence: which stone, which gem, where, what role

An occurrence carries no shape and no material of its own. It REFERENCES them,
because two accents cut from the same specification are two occurrences of one
stone, not two stones that happen to match.

IDENTITY IS BY ID, NEVER BY POSITION. Every instance, group and relation is
addressed by a stable string ID. Array order is a serialization artifact:
reordering the `instances` list must not change what the arrangement means, and
`normalize.py` sorts canonically so it cannot.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from jewelmind.gem.models import GemIdentity, StoneRole

# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

#: Instance, group, pattern and relation IDs: lowercase, dot-separated,
#: letters/digits/`_`/`-`, and never a path separator, a space or a shell
#: metacharacter. The same safety property gem IDs have
#: (`jewelmind/gem/models.py::GEM_ID_PATTERN`), so a user-authored ID can never
#: become a filesystem path, a shell argument or an arbitrary dictionary key.
#:
#: ONE DELIBERATE DIFFERENCE FROM THE GEM PATTERN: a segment after the first may
#: begin with a DIGIT, so `side.1` and `halo.0` are valid. A gem ID is a
#: registry key written by this project; an arrangement ID is a label written by
#: a user or derived from a pattern index, and numbered members are the natural
#: way to name them. Requiring a letter would have made
#: `resolve.py::_member_id`'s own derived IDs unrepresentable in JDL — a real
#: inconsistency found by round-tripping a resolved arrangement, not by reading
#: the pattern. The first character is still a letter, so an ID can never be
#: mistaken for a number.
ARRANGEMENT_ID_PATTERN = r"^[a-z][a-z0-9_-]*(\.[a-z0-9][a-z0-9_-]*)*$"
MAX_ARRANGEMENT_ID_LENGTH = 80

#: Bounds on structure size. Software limits that keep a malformed or hostile
#: document from producing an unbounded resolution, NOT jewelry limits — no
#: claim is made that 200 stones is a sensible ring.
MAX_INSTANCES = 200
MAX_GROUPS = 50
MAX_RELATIONS = 200
MAX_PATTERN_COUNT = 100

#: Coordinate bound, in millimetres. Wide enough for any jewelry article and
#: narrow enough that a mis-scaled import fails loudly.
MAX_COORDINATE_MM = 500.0


# ---------------------------------------------------------------------------
# Vocabularies
# ---------------------------------------------------------------------------

#: How an instance's placement is expressed.
#:
#: `EXPLICIT` is the only mode a placement can END in: every other mode is
#: RESOLVED to an explicit position by `resolve.py`. Downstream consumers
#: therefore only ever see coordinates, and never have to interpret a mode.
PlacementMode = Literal[
    "EXPLICIT",
    "PATTERN_MEMBER",
    "RELATIVE",
]

#: The reference frame a placement's coordinates are measured in.
#:
#: `DESIGN_ORIGIN` is the design's own origin — for a ring, the same origin
#: `geometry/constants.py` already defines. `PARENT_GROUP` is relative to the
#: group's own origin, which is itself placed in the design frame.
PlacementFrame = Literal["DESIGN_ORIGIN", "PARENT_GROUP"]

#: Pattern kinds. Each is a closed-form generator: given its parameters, the
#: member positions follow by direct evaluation, in a fixed order.
#:
#: Deliberately NOT a member: a free-form "PATH" pattern following an arbitrary
#: curve. That needs curve evaluation, which is Atlas's job, and would drag
#: geometry into this layer.
ArrangementPatternKind = Literal[
    "LINEAR",
    "RADIAL",
    "MIRROR",
]

#: The plane a `MIRROR` pattern reflects across, named by its normal axis.
MirrorPlane = Literal["YZ", "XZ"]

#: Relationship kinds between instances or groups.
#:
#: A relation is a DECLARATION OF INTENT that survives editing — "these two are
#: a mirrored pair", "this row is aligned" — not a constraint to be solved.
#: Recording it lets a later edit, a Studio grouped operation, or a future
#: setting system act on the relationship instead of re-deriving it from
#: coordinates that happen to look symmetric.
ArrangementRelationKind = Literal[
    "MIRRORED_PAIR",
    "ALIGNED_WITH",
    "EVENLY_SPACED_WITH",
    "CONCENTRIC_WITH",
    "SHARES_TRANSFORM_WITH",
]

#: Whether a resolved instance actually became geometry.
#:
#: The honest reporting channel for this sprint's execution boundary: the
#: arrangement RESOLVES completely (every instance gets a real placement), while
#: the current geometry pipeline emits one stone component. An instance the
#: pipeline did not build reports `NOT_GENERATED` with a reason, rather than
#: being silently dropped (ATLAS-GOV-006, restated for instances).
InstanceGenerationStatus = Literal["GENERATED", "NOT_GENERATED"]


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


class ArrangementModel(BaseModel):
    """Strict, kernel-neutral, immutable base.

    `strict=True` matches `domain/schema.py::StrictModel` rather than
    `StoneModel`/`GemModel`, and that is deliberate: these models are carried
    DIRECTLY in JDL rather than through a hand-written `Jdl*` mirror, so they
    must apply JDL's own untrusted-input policy — a JSON string `"4.6"` is not
    an acceptable radius. (int -> float widening still works, since that is
    lossless and is what a JSON number without a decimal point parses to.)

    NO JDL MIRROR EXISTS FOR THIS TREE, on purpose. Sprint 21 mirrored
    `GemIdentity` as `JdlGemIdentity` because that was two small models; this
    tree is eight nested ones, and a hand-maintained mirror of eight models is
    the drift Sprint 20 had to remove three times. One strict definition, used
    at both layers, cannot disagree with itself.

    `frozen=True` because an arrangement is replaced, never mutated in place:
    resolution and normalization return new objects, so a shared reference can
    never be edited out from under a computed fingerprint.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


# ---------------------------------------------------------------------------
# Placement and transform
# ---------------------------------------------------------------------------


class InstanceTransform(ArrangementModel):
    """An instance's rigid placement: a translation plus one rotation.

    ONE ROTATION, ABOUT THE VERTICAL AXIS ONLY, and that is a decision rather
    than an omission. `StoneSpec.orientation` already rotates a stone about its
    own vertical axis, and a full 3×3 orientation here would create a second,
    overlapping way to express the same thing plus five more ways to express
    something no current geometry builder can execute. Tilt and roll are
    recorded as PLANNED in the capability registry instead of being accepted
    and ignored.

    Millimetres and degrees, like every other length and angle in JewelMind
    (LAW-007). No unit field, no conversion.
    """

    xMm: float = Field(
        default=0.0, ge=-MAX_COORDINATE_MM, le=MAX_COORDINATE_MM, allow_inf_nan=False
    )
    yMm: float = Field(
        default=0.0, ge=-MAX_COORDINATE_MM, le=MAX_COORDINATE_MM, allow_inf_nan=False
    )
    zMm: float = Field(
        default=0.0, ge=-MAX_COORDINATE_MM, le=MAX_COORDINATE_MM, allow_inf_nan=False
    )

    #: Rotation about the vertical (Z) axis, degrees. Normalized into [0, 360)
    #: by `normalize.py`, so 370° and 10° are the same arrangement.
    rotationDeg: float = Field(default=0.0, ge=-3600.0, le=3600.0, allow_inf_nan=False)


class InstancePlacement(ArrangementModel):
    """Where an instance sits, and how that was expressed.

    `mode` records the ORIGIN of the placement so an editor can tell a position
    the user typed from one a pattern produced. Resolution rewrites every mode
    to `EXPLICIT`; before that, a `PATTERN_MEMBER` placement's transform is the
    pattern's own offset for that member and is not yet the final position.
    """

    mode: PlacementMode = "EXPLICIT"
    frame: PlacementFrame = "DESIGN_ORIGIN"
    transform: InstanceTransform = Field(default_factory=InstanceTransform)

    #: Set when this instance belongs to a group; `None` for a top-level one.
    groupId: str | None = Field(
        default=None, pattern=ARRANGEMENT_ID_PATTERN, max_length=MAX_ARRANGEMENT_ID_LENGTH
    )

    @model_validator(mode="after")
    def _parent_frame_requires_a_group(self) -> InstancePlacement:
        if self.frame == "PARENT_GROUP" and self.groupId is None:
            raise ValueError(
                "placement.frame 'PARENT_GROUP' requires a groupId naming the parent "
                "group; without one there is no parent frame to measure from."
            )
        return self


# ---------------------------------------------------------------------------
# Instance-level overrides
# ---------------------------------------------------------------------------


class InstanceOverrides(ArrangementModel):
    """The EXPLICITLY supported per-instance deviations from the referenced
    stone specification.

    A CLOSED SET, on purpose. Allowing an instance to override any stone field
    would make the reference meaningless — the instance would become a second
    stone definition, and "same stone, eight times" would stop being expressible.
    So an instance may scale a size and rotate itself, and nothing else. It can
    never override the shape, the source, the outline, or the profile: those are
    what make two occurrences occurrences OF something.

    A field left `None` means "inherit", which is different from "same value as
    the parent" — an inherited size follows a later edit to the stone
    specification, a copied one would not.
    """

    #: Uniform scale applied to the referenced stone's resolved dimensions.
    #: Bounded well away from zero: a zero or negative scale is a malformed
    #: instance, not a request for an invisible stone.
    scale: float | None = Field(default=None, gt=0.01, le=10.0, allow_inf_nan=False)

    #: Overrides `StoneSpec.orientation` for this occurrence only — the reason a
    #: mirrored pair of pear accents can point outward in opposite directions
    #: while referencing one stone specification.
    orientationDeg: float | None = Field(
        default=None, ge=-360.0, le=360.0, allow_inf_nan=False
    )


# ---------------------------------------------------------------------------
# Instances
# ---------------------------------------------------------------------------


class StoneInstanceDef(ArrangementModel):
    """One occurrence of a stone in a design.

    References the stone specification and the gem identity rather than
    restating them (see this module's docstring). `stoneRef` is a symbolic name
    resolved by the consumer — `"primary"` means the definition's own
    `stone` — which is what keeps this model free of a `StoneSpec` import and
    therefore free of the whole domain schema.

    Supersedes `jewelmind.gem.models.StoneInstance`, which carried identity and
    role but deliberately no placement (it predates this layer). That model
    remains for gem-only consumers; this one is what an arrangement holds.
    """

    instanceId: str = Field(
        pattern=ARRANGEMENT_ID_PATTERN, max_length=MAX_ARRANGEMENT_ID_LENGTH
    )

    #: Which stone specification this occurrence is an occurrence OF.
    #: `"primary"` is the definition's own `stone`; any other value names a
    #: future named stone specification and is reported unresolved today rather
    #: than silently treated as the primary one.
    stoneRef: str = Field(
        default="primary",
        pattern=ARRANGEMENT_ID_PATTERN,
        max_length=MAX_ARRANGEMENT_ID_LENGTH,
    )

    role: StoneRole = "CENTER"
    placement: InstancePlacement = Field(default_factory=InstancePlacement)
    overrides: InstanceOverrides = Field(default_factory=InstanceOverrides)

    #: Per-instance gem identity. `None` inherits the referenced stone's gem —
    #: which is what makes "eight identical accents" one edit rather than eight.
    gem: GemIdentity | None = None

    #: The pattern that produced this instance, when it was generated by one.
    #: Present on a resolved arrangement so an editor can tell a hand-placed
    #: stone from a pattern member, and so re-resolving a pattern replaces its
    #: own members rather than duplicating them.
    sourcePatternId: str | None = Field(
        default=None, pattern=ARRANGEMENT_ID_PATTERN, max_length=MAX_ARRANGEMENT_ID_LENGTH
    )


class ArrangementGroup(ArrangementModel):
    """A named set of instances that move and are edited together.

    Grouping is expressed by an instance naming its `groupId`, not by the group
    listing members. One direction only: two directions would need to agree, and
    a membership list that disagrees with its members is a malformed document
    that nothing can resolve correctly.
    """

    groupId: str = Field(
        pattern=ARRANGEMENT_ID_PATTERN, max_length=MAX_ARRANGEMENT_ID_LENGTH
    )
    label: str | None = Field(default=None, max_length=120)

    #: The group's own origin in the design frame. A member placed in
    #: `PARENT_GROUP` frame is offset from this.
    transform: InstanceTransform = Field(default_factory=InstanceTransform)


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------


class LinearPatternSpec(ArrangementModel):
    """`count` copies along a straight line, evenly spaced.

    `spacingMm` is centre-to-centre distance. It is a POSITION parameter, never
    a clearance: nothing here knows a stone's size, so nothing here can claim
    two stones do not collide. Whether a spacing is manufacturable is a
    geometric and professional question, asked downstream.
    """

    kind: Literal["LINEAR"] = "LINEAR"
    count: int = Field(ge=1, le=MAX_PATTERN_COUNT)
    spacingMm: float = Field(gt=0.0, le=MAX_COORDINATE_MM, allow_inf_nan=False)

    #: Direction of the line in the XY plane, degrees from +X.
    directionDeg: float = Field(default=0.0, ge=-360.0, le=360.0, allow_inf_nan=False)

    #: When true the run is centred on the anchor, so an odd count puts one
    #: member exactly on it and an even count straddles it. When false the
    #: anchor is the first member.
    centered: bool = True


class RadialPatternSpec(ArrangementModel):
    """`count` copies around a circle of radius `radiusMm`.

    `startAngleDeg` and `sweepDeg` make a partial arc expressible, so a halo
    that stops short of the shank is a first-class arrangement rather than a
    full circle with members deleted.
    """

    kind: Literal["RADIAL"] = "RADIAL"
    count: int = Field(ge=1, le=MAX_PATTERN_COUNT)
    radiusMm: float = Field(gt=0.0, le=MAX_COORDINATE_MM, allow_inf_nan=False)
    startAngleDeg: float = Field(default=0.0, ge=-360.0, le=360.0, allow_inf_nan=False)

    #: Angular extent. 360 distributes members over a full circle without
    #: doubling one at both ends; a smaller sweep spreads them across an arc,
    #: inclusive of both endpoints.
    sweepDeg: float = Field(default=360.0, gt=0.0, le=360.0, allow_inf_nan=False)

    #: When true each member is rotated to face outward from the centre, which
    #: is what makes a radial run of pear accents read as a halo rather than as
    #: parallel stones on a circle.
    alignToRadius: bool = True


class MirrorPatternSpec(ArrangementModel):
    """One reflected copy across a principal plane through the design origin.

    A pattern rather than a relation because it PRODUCES an instance. The
    `MIRRORED_PAIR` relation records that two existing instances are a pair;
    this creates the second one.
    """

    kind: Literal["MIRROR"] = "MIRROR"
    plane: MirrorPlane = "YZ"

    #: Mirroring a chiral stone (pear, marquise, half moon) must also flip its
    #: own orientation, or the reflection is not a reflection. Settable so a
    #: radially symmetric stone can skip a rotation that would change nothing.
    mirrorOrientation: bool = True


ArrangementPatternSpec = LinearPatternSpec | RadialPatternSpec | MirrorPatternSpec


class ArrangementPattern(ArrangementModel):
    """A pattern plus what it applies to.

    `sourceInstanceId` names the instance being repeated: a pattern is always
    "more of this one", never a free-floating count of nothing. That keeps every
    generated member's stone reference, gem and overrides traceable to a real
    instance the user can see and edit.
    """

    patternId: str = Field(
        pattern=ARRANGEMENT_ID_PATTERN, max_length=MAX_ARRANGEMENT_ID_LENGTH
    )
    sourceInstanceId: str = Field(
        pattern=ARRANGEMENT_ID_PATTERN, max_length=MAX_ARRANGEMENT_ID_LENGTH
    )
    spec: ArrangementPatternSpec = Field(discriminator="kind")

    #: The role every generated member takes. The source instance keeps its own,
    #: so a `CENTER` stone can seed a halo of `HALO` members.
    memberRole: StoneRole = "ACCENT"

    #: The group generated members join, if any.
    groupId: str | None = Field(
        default=None, pattern=ARRANGEMENT_ID_PATTERN, max_length=MAX_ARRANGEMENT_ID_LENGTH
    )


# ---------------------------------------------------------------------------
# Relations
# ---------------------------------------------------------------------------


class ArrangementRelation(ArrangementModel):
    """A declared relationship between two or more instances or groups.

    Relations are RECORDED AND VALIDATED, never solved. `resolve.py` checks that
    every referenced ID exists and that the relation's arity is respected, and
    passes them through untouched. Enforcing them — moving a stone because its
    mirror moved — is a future editing capability, marked PLANNED rather than
    implied.
    """

    relationId: str = Field(
        pattern=ARRANGEMENT_ID_PATTERN, max_length=MAX_ARRANGEMENT_ID_LENGTH
    )
    kind: ArrangementRelationKind

    #: The participants, by instance or group ID. Order is meaningful for
    #: `MIRRORED_PAIR` (first is the original) and not for the rest;
    #: `normalize.py` sorts only the order-insensitive kinds.
    members: list[str] = Field(min_length=2, max_length=MAX_INSTANCES)

    note: str | None = Field(default=None, max_length=500)


# ---------------------------------------------------------------------------
# The arrangement
# ---------------------------------------------------------------------------


class ArrangementDefinition(ArrangementModel):
    """The declarative arrangement: instances, groups, patterns, relations.

    ABSENT IS NOT EMPTY. A definition with no arrangement at all is a
    single-stone design and keeps behaving exactly as it did before this sprint;
    that is why JDL's field is nullable rather than defaulting to a
    one-instance arrangement. Reading a missing arrangement as an implicit
    single instance would make every pre-Sprint-22 document silently acquire an
    arrangement, and its hash change with it.
    """

    #: Empty is legal and means "no instances declared". `resolve.py` returns an
    #: empty resolution for it — an honest nothing, not an error and not an
    #: invented default stone.
    instances: list[StoneInstanceDef] = Field(
        default_factory=list, max_length=MAX_INSTANCES
    )
    groups: list[ArrangementGroup] = Field(default_factory=list, max_length=MAX_GROUPS)
    patterns: list[ArrangementPattern] = Field(
        default_factory=list, max_length=MAX_INSTANCES
    )
    relations: list[ArrangementRelation] = Field(
        default_factory=list, max_length=MAX_RELATIONS
    )


# ---------------------------------------------------------------------------
# Resolution output
# ---------------------------------------------------------------------------


class ResolvedInstance(ArrangementModel):
    """One instance after resolution: an explicit position in the design frame.

    Every placement is `EXPLICIT` and every frame is `DESIGN_ORIGIN` — group
    offsets are composed in, pattern members are expanded, and nothing is left
    for a downstream consumer to interpret. A consumer that had to re-derive a
    position would be a second implementation of this layer's arithmetic, and
    the two would eventually disagree.
    """

    instanceId: str
    stoneRef: str
    role: StoneRole
    transform: InstanceTransform
    overrides: InstanceOverrides
    gem: GemIdentity | None
    sourcePatternId: str | None
    groupId: str | None

    #: Whether geometry was actually built for this instance. Set by the
    #: compilation boundary, not by resolution — resolution has no opinion about
    #: what a geometry pipeline can execute.
    generationStatus: InstanceGenerationStatus = "NOT_GENERATED"

    #: Why, when `NOT_GENERATED`. Required in that case by
    #: `_reason_required_when_not_generated`, so an ungenerated instance can
    #: never be reported without saying why.
    generationNote: str | None = Field(default=None, max_length=300)

    #: The geometry component name this instance became, when it was built.
    #: Ties a resolved instance to a real `GeneratedComponent`, which is what
    #: keeps component identity stable and non-positional (INSPECT-GOV-015).
    componentName: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def _reason_required_when_not_generated(self) -> ResolvedInstance:
        if self.generationStatus == "NOT_GENERATED" and not (
            self.generationNote or ""
        ).strip():
            raise ValueError(
                "an instance reported NOT_GENERATED must carry a generationNote "
                "explaining why; silently omitting a stone is never acceptable."
            )
        if self.generationStatus == "GENERATED" and not (self.componentName or "").strip():
            raise ValueError(
                "an instance reported GENERATED must name the geometry component "
                "it became."
            )
        return self


class ResolvedArrangement(ArrangementModel):
    """The complete, deterministic resolution of an `ArrangementDefinition`.

    THE CONTRACT DOWNSTREAM CONSUMERS DEPEND ON. Atlas, Vision, Foundry and
    Forge read this and never the raw definition, so pattern expansion and frame
    composition happen exactly once, in one place.

    Kernel-neutral: not one field holds a shape. This is the boundary the brief
    requires between declarative data and CAD construction.
    """

    instances: list[ResolvedInstance]
    relations: list[ArrangementRelation]

    #: Deterministic fingerprint of the arrangement's own content, SEPARATE
    #: from `definitionHash` and from `geometryHash`. Two arrangements with the
    #: same fingerprint are the same arrangement; the same arrangement inside
    #: two different rings has two different definition hashes.
    arrangementFingerprint: str

    #: Version of the resolution algorithm. A change to the arithmetic changes
    #: this, so a stored resolution can be told apart from a fresh one.
    resolverVersion: str

    #: Structural facts about the resolution, for reporting. Counts only — no
    #: judgment about whether the arrangement is good, manufacturable, or
    #: sensible.
    instanceCount: int = Field(ge=0)
    generatedCount: int = Field(ge=0)
    patternExpandedCount: int = Field(ge=0)

    #: Non-fatal observations, e.g. an instance the current pipeline cannot
    #: build. Never a jewelry judgment.
    notes: list[str] = Field(default_factory=list)
