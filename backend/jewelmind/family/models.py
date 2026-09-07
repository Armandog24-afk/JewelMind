"""Multi-stone family domain models (Sprint 24).

WHAT A FAMILY IS. The SEMANTIC structure of a multi-stone design: that this is a
three-stone ring rather than "a design that happens to contain three stones",
that this member is the centre and those two are its sides, and that the sides
are meant to be a mirrored pair. It answers *what the design means*.

WHAT A FAMILY IS NOT, and must never become:

- **Not a placement engine.** A family compiles INTO an
  `ArrangementDefinition`; the Stone Arrangement Engine remains the sole
  authority on positions, patterns and relations. `compile.py` produces
  arrangement primitives and nothing else, so there is exactly one place where
  a stone's position is decided.
- **Not a second stone or gem model.** A member REFERENCES a stone
  specification and may carry a `GemIdentity`; it never restates a shape, a
  dimension, a material or a visual profile. Three stones of different cuts is
  three references, not three copies.
- **Not a setting implementation.** A member may name the setting it wants; the
  Setting System decides what that setting is and builds it.
- **Not geometry.** No field holds a kernel object.
- **Not category-specific.** Nothing here imports a jewelry category. A
  toi-et-moi is the same family whether it is a ring or a pendant.

WHY A LAYER ABOVE THE ARRANGEMENT AT ALL. An arrangement can already express
three stones in a row — but it cannot say that the row IS a three-stone design,
which side is which, or that widening the design should move both sides
symmetrically. Those are semantic facts, and without them every consumer
(Studio, Designer, a future family-aware setting strategy) would have to
re-infer intent from coordinates. A family records the intent once.

IDENTITY IS BY ID, NEVER BY POSITION. Reordering `members` must not change what
a family means, its canonical JSON, or its fingerprint.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from jewelmind.arrangement.models import (
    ARRANGEMENT_ID_PATTERN,
    MAX_ARRANGEMENT_ID_LENGTH,
    InstanceTransform,
)
from jewelmind.gem.models import GemIdentity, StoneRole

#: Member ids share the arrangement's id shape, because a member becomes an
#: arrangement instance and its id becomes that instance's id. Reusing the
#: pattern means one validator covers the whole chain, and a member id can
#: never become a filesystem path or a shell argument.
FAMILY_ID_PATTERN = ARRANGEMENT_ID_PATTERN
MAX_FAMILY_ID_LENGTH = MAX_ARRANGEMENT_ID_LENGTH

#: Software bounds. A malformed or hostile document must not produce an
#: unbounded compilation. NOT jewelry limits: nothing here claims how many
#: stones a piece should carry.
MAX_FAMILY_MEMBERS = 60
MAX_CLUSTER_COUNT = 40

#: Families with a real compiler. Every member of this enum compiles to a real
#: arrangement; a family named here but unimplemented would be the silently
#: ignored field this project keeps refusing to add.
#:
#: Reserved names (halo, pave, eternity, bypass, ...) live in
#: `capability.py::RESERVED_FAMILY_TYPES` and are deliberately NOT members.
FamilyType = Literal[
    "THREE_STONE",
    "TOI_ET_MOI",
    "CLUSTER",
    "CENTER_WITH_ACCENTS",
]

#: How a family's members are laid out relative to each other.
#:
#: `SYMMETRIC` mirrors the secondary members about the design's YZ plane, which
#: is what makes a three-stone ring read as balanced. `ASYMMETRIC` places each
#: member from its own parameters, which is what makes a deliberately
#: unbalanced toi-et-moi expressible rather than approximated.
FamilySymmetry = Literal["SYMMETRIC", "ASYMMETRIC"]


class FamilyModel(BaseModel):
    """Strict, kernel-neutral, immutable base.

    `strict=True` matches `domain/schema.py::StrictModel` and
    `arrangement/models.py`: these models are carried DIRECTLY in JDL rather
    than through a hand-written `Jdl*` mirror, so they apply JDL's own
    untrusted-input policy. A JSON string `"2.4"` is not an acceptable spacing.

    `frozen=True` because a family is replaced, never mutated: compilation and
    normalization return new objects, so a shared reference cannot be edited out
    from under a computed fingerprint.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class FamilyMember(FamilyModel):
    """One participating stone, by role.

    THE ROLE IS THE POINT. A three-stone family holds a `CENTER` and two
    `SIDE`s, not three anonymous stones — which is what lets a consumer ask
    "what is the centre stone?" without guessing from size or position.

    Everything about what the stone IS lives elsewhere: `stoneRef` names the
    stone specification and `gem` names the material. Neither is copied here.
    """

    memberId: str = Field(pattern=FAMILY_ID_PATTERN, max_length=MAX_FAMILY_ID_LENGTH)
    role: StoneRole

    #: Which stone specification this member is an occurrence of. `"primary"`
    #: is the definition's own `stone`; any other value names a future named
    #: specification and is reported unresolved rather than silently treated as
    #: the primary one (the same contract `arrangement` already uses).
    stoneRef: str = Field(
        default="primary",
        pattern=FAMILY_ID_PATTERN,
        max_length=MAX_FAMILY_ID_LENGTH,
    )

    #: This member's own gem. `None` inherits the referenced stone's gem, which
    #: is what makes "all three the same material" one edit rather than three.
    #: Set it per member for a mixed-material design.
    gem: GemIdentity | None = None

    #: Uniform scale on the referenced stone's resolved dimensions, so a side
    #: stone can be smaller than the centre without a second stone
    #: specification. `None` means "as specified".
    scale: float | None = Field(default=None, gt=0.01, le=10.0, allow_inf_nan=False)

    #: This member's own rotation about its vertical axis, in degrees. What
    #: lets a toi-et-moi's two pears point in opposite directions.
    orientationDeg: float | None = Field(
        default=None, ge=-360.0, le=360.0, allow_inf_nan=False
    )

    #: An explicit placement, overriding whatever the family parameters would
    #: derive for this member.
    #:
    #: REUSES `InstanceTransform` rather than declaring a second transform
    #: model, because the value this carries IS an arrangement transform — it is
    #: handed to the arrangement unchanged. A parallel model would be two
    #: definitions of one concept, which is exactly what this sprint must not
    #: create.
    placementOverride: InstanceTransform | None = None

    #: The setting this member wants, by name (`"prong"`, `"bezel"`).
    #:
    #: A REQUEST, not an implementation. The Setting System decides what the
    #: name means and whether it can be built; the family neither knows nor
    #: stores setting geometry. `None` means the design's own `setting` block
    #: applies, which is the single-stone case.
    settingRef: str | None = Field(default=None, max_length=40)


class ThreeStoneParams(FamilyModel):
    """A centre with two flanking stones.

    `sideSpacingMm` is a centre-to-centre distance along the design's X axis. A
    POSITION parameter, never a clearance: this layer knows no stone's size, so
    it cannot claim two stones do not touch. Whether a spacing is settable is a
    geometric question for Inspection and a professional one nobody here can
    answer.
    """

    kind: Literal["THREE_STONE"] = "THREE_STONE"

    sideSpacingMm: float = Field(gt=0.0, le=200.0, allow_inf_nan=False)

    #: Default scale applied to both side stones when a member does not state
    #: its own. A CONSTRUCTION default, not a proportion rule.
    sideScale: float = Field(default=0.6, gt=0.01, le=10.0, allow_inf_nan=False)

    symmetry: FamilySymmetry = "SYMMETRIC"


class ToiEtMoiParams(FamilyModel):
    """Two stones set side by side as a deliberate pair.

    A DISTINCT FAMILY, not a two-element list. The pair is the design: the two
    stones face each other across the design axis, and the relationship between
    them is the thing a consumer needs to preserve when either one is edited.
    """

    kind: Literal["TOI_ET_MOI"] = "TOI_ET_MOI"

    #: Centre-to-centre distance between the two stones.
    separationMm: float = Field(gt=0.0, le=200.0, allow_inf_nan=False)

    #: Angle of the line joining them, degrees from +X. A classic toi-et-moi
    #: sets the pair on a diagonal, which this expresses without a second
    #: family type.
    axisAngleDeg: float = Field(default=0.0, ge=-360.0, le=360.0, allow_inf_nan=False)

    #: When `SYMMETRIC`, the second stone's own orientation mirrors the first's
    #: — the difference between a facing pair and two parallel stones.
    symmetry: FamilySymmetry = "SYMMETRIC"


class ClusterParams(FamilyModel):
    """Stones grouped around a common structure.

    NOT NECESSARILY CIRCULAR. `sweepDeg` under 360 lays the cluster on an arc,
    and `radiusYMm` makes it elliptical, so an oval or crescent cluster is a
    parameter change rather than a new family.
    """

    kind: Literal["CLUSTER"] = "CLUSTER"

    #: Number of surrounding stones, excluding any centre.
    count: int = Field(ge=1, le=MAX_CLUSTER_COUNT)

    radiusMm: float = Field(gt=0.0, le=200.0, allow_inf_nan=False)

    #: Second semi-axis, for an elliptical cluster. `None` means circular.
    radiusYMm: float | None = Field(default=None, gt=0.0, le=200.0, allow_inf_nan=False)

    startAngleDeg: float = Field(default=0.0, ge=-360.0, le=360.0, allow_inf_nan=False)
    sweepDeg: float = Field(default=360.0, gt=0.0, le=360.0, allow_inf_nan=False)

    #: Whether a centre stone participates. A cluster without one is a ring of
    #: stones, which is a real design rather than a degenerate case.
    includeCenter: bool = True

    #: Default scale for the surrounding stones.
    memberScale: float = Field(default=0.4, gt=0.01, le=10.0, allow_inf_nan=False)

    #: Whether each surrounding stone is rotated to face outward.
    alignToRadius: bool = True


class CenterWithAccentsParams(FamilyModel):
    """The general centre-plus-accents family.

    Deliberately the LEAST specialized of the four: it exists so a design that
    is neither a strict three-stone nor a cluster still has a semantic home,
    rather than forcing one of the others to stretch. Accents are placed on an
    arc by the same closed-form evaluation a cluster uses.
    """

    kind: Literal["CENTER_WITH_ACCENTS"] = "CENTER_WITH_ACCENTS"

    accentCount: int = Field(ge=1, le=MAX_CLUSTER_COUNT)
    accentRadiusMm: float = Field(gt=0.0, le=200.0, allow_inf_nan=False)
    accentStartAngleDeg: float = Field(
        default=0.0, ge=-360.0, le=360.0, allow_inf_nan=False
    )
    accentSweepDeg: float = Field(default=360.0, gt=0.0, le=360.0, allow_inf_nan=False)
    accentScale: float = Field(default=0.35, gt=0.01, le=10.0, allow_inf_nan=False)
    symmetry: FamilySymmetry = "SYMMETRIC"


FamilyParams = (
    ThreeStoneParams | ToiEtMoiParams | ClusterParams | CenterWithAccentsParams
)


class FamilyDefinition(FamilyModel):
    """A multi-stone design's semantic structure.

    `members` names the participating stones and their roles; `params` says how
    the family arranges them. Compilation turns both into a real
    `ArrangementDefinition`, which is where placement actually lives.

    ABSENT IS NOT EMPTY. A definition with no family is a single-stone design
    and behaves exactly as it did before this sprint. Reading a missing family
    as an implicit solitaire family would give every stored document a family it
    never declared, and its hash would change with it.
    """

    familyType: FamilyType
    params: FamilyParams = Field(discriminator="kind")

    #: The participating stones. Empty is legal and means "derive every member
    #: from the parameters", which is how a 12-stone cluster is expressed
    #: without typing twelve members.
    members: list[FamilyMember] = Field(
        default_factory=list, max_length=MAX_FAMILY_MEMBERS
    )

    #: A human label, carried through for Studio. Never used for identity.
    label: str | None = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def _params_match_the_family_type(self) -> FamilyDefinition:
        """The discriminator and the family type must agree.

        Two fields naming the same thing can disagree, and a family whose type
        says THREE_STONE while its parameters describe a cluster has no
        determinate meaning. Checked here rather than collapsing the two,
        because `familyType` is what consumers switch on and the discriminated
        union is what gives each family its own typed parameters.
        """

        if self.params.kind != self.familyType:
            raise ValueError(
                f"family.params.kind '{self.params.kind}' does not match "
                f"family.familyType '{self.familyType}'."
            )
        return self

    @model_validator(mode="after")
    def _member_ids_are_unique(self) -> FamilyDefinition:
        """Ids are the authoritative identity, so a duplicate makes every
        reference to it — a role query, a relation, a generated component —
        ambiguous."""

        seen: set[str] = set()
        for member in self.members:
            if member.memberId in seen:
                raise ValueError(
                    f"family.members contains duplicate memberId "
                    f"'{member.memberId}'."
                )
            seen.add(member.memberId)
        return self
