"""Halo domain models (Sprint 25).

WHAT A HALO IS. A STRUCTURAL RELATIONSHIP between a centre and one or more rings
of stones surrounding it. Not a stone, not a gem, not a setting, not a placement
engine: it says *that these stones surround that one*, and compiles into the
arrangement primitives that put them there.

WHY IT IS NOT JUST ANOTHER FAMILY, which is a real question because Sprint 24
reserved the name `halo` on exactly that ground ("a halo is a
CENTER_WITH_ACCENTS whose accents sit against the centre"). That reasoning holds
for a single flat halo and fails for the rest of the concept:

- a HIDDEN halo sits BELOW the centre stone's girdle plane. `CENTER_WITH_ACCENTS`
  has no vertical axis at all, so a hidden halo is not expressible by it —
  approximating one as a flat accent ring would place the stones where they are
  visibly wrong.
- a DOUBLE halo is TWO concentric rings with independent counts, radii, scales
  and start angles. One `accentCount`/`accentRadiusMm` pair cannot carry two.
- a halo COMPOSES with a family rather than replacing it. "Three-stone with a
  halo around the centre" needs both structures at once; a fifth family type
  would force a choice between them.

So a halo is a composable LAYER over whatever placement the design already
declares — a family, an explicit arrangement, or nothing — and
`docs/bible/27-halo/halo-rfc.md` records that supersession of the Sprint 24
reservation rather than editing quietly around it.

WHAT A HALO IS NOT, and must never become:

- **Not a placement engine.** `compile.py` emits `StoneInstanceDef`s and
  `ArrangementRelation`s; the Stone Arrangement Engine resolves them, using the
  same shared ring arithmetic (`arrangement/radial.py`) a hand-written `RADIAL`
  pattern uses.
- **Not a second stone or gem model.** A ring names a stone specification and
  may carry a `GemIdentity`; nothing about the stone is copied. A halo stone
  need not share the centre's gem, shape, size or material.
- **Not a setting implementation.** A ring may REQUEST a setting by name; the
  Setting System decides what that means, and today builds one only for the
  primary stone.
- **Not geometry.** No field holds a kernel object.
- **Not category-specific.** Nothing here imports a jewelry category. The same
  halo is a halo on a ring, a pendant or an earring.

IDENTITY IS BY ID, NEVER BY POSITION. Reordering `rings`, or a ring's `members`,
must not change what the halo means, its compiled arrangement, its canonical
JSON or its fingerprint.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from jewelmind.arrangement.models import (
    ARRANGEMENT_ID_PATTERN,
    MAX_ARRANGEMENT_ID_LENGTH,
)
from jewelmind.family.models import FamilyMember
from jewelmind.gem.models import GemIdentity

#: Halo ids share the arrangement's id shape, because a halo ring's members
#: BECOME arrangement instances and their ids become those instances' ids.
#: Reusing the pattern means one validator covers the whole chain, and a halo id
#: can never become a filesystem path or a shell argument.
HALO_ID_PATTERN = ARRANGEMENT_ID_PATTERN
MAX_HALO_ID_LENGTH = MAX_ARRANGEMENT_ID_LENGTH

#: Software bounds. A malformed or hostile document must not produce an
#: unbounded composition. NOT jewelry limits: nothing here claims how many
#: stones a halo should carry, how tightly they may sit, or whether a given
#: count is settable.
MAX_HALO_RINGS = 2
MAX_HALO_STONES_PER_RING = 60
MAX_HALO_STONES = 120

#: Halo variants with a real compiler.
#:
#: `SINGLE`  - one ring around the centre.
#: `DOUBLE`  - two concentric rings, each with its own count, radius and scale.
#: `HIDDEN`  - one ring below the centre stone's girdle plane, which is what
#:             "hidden" means structurally: not visible from above the crown.
#:
#: A variant named here but unimplemented would be the silently ignored field
#: this project keeps refusing to add. Reserved variants live in
#: `capability.py::RESERVED_HALO_VARIANTS` and are deliberately NOT members.
HaloVariant = Literal["SINGLE", "DOUBLE", "HIDDEN"]

#: How many rings each variant describes. Stated as DATA rather than as checks
#: inside a validator so the rule is inspectable, testable and reportable —
#: Forge and the spec registry read this same table.
HALO_RING_CARDINALITY: dict[str, int] = {
    "SINGLE": 1,
    "DOUBLE": 2,
    "HIDDEN": 1,
}

#: Canonical ring ids a document need not name. DERIVED, never random:
#: re-compiling the same halo must reproduce them exactly, or a stored
#: compilation could not be compared with a fresh one.
DEFAULT_RING_IDS: tuple[str, ...] = ("halo.inner", "halo.outer")

#: The centre a halo surrounds when the document does not name one. Matches
#: `family/compile.py::CENTER_MEMBER_ID`, because that is the member every
#: centred family derives.
DEFAULT_CENTER_MEMBER_ID = "center"


class HaloModel(BaseModel):
    """Strict, kernel-neutral, immutable base.

    `strict=True` matches `domain/schema.py::StrictModel`, `arrangement/models.py`
    and `family/models.py`: these models are carried DIRECTLY in JDL rather than
    through a hand-written `Jdl*` mirror, so they apply JDL's own untrusted-input
    policy. A JSON string `"2.4"` is not an acceptable radius.

    `frozen=True` because a halo is replaced, never mutated: composition returns
    new objects, so a shared reference cannot be edited out from under a computed
    fingerprint.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class HaloRing(HaloModel):
    """One concentric ring of stones.

    THE RING IS THE UNIT, not the individual stone, because that is what a
    designer actually specifies: "sixteen stones at 3.2mm, a third the size of
    the centre". Individual stones remain separately identifiable — each becomes
    its own arrangement instance with its own id — and `members` exists for the
    cases where one of them differs.
    """

    ringId: str = Field(pattern=HALO_ID_PATTERN, max_length=MAX_HALO_ID_LENGTH)

    #: How many stones this ring carries. Every one becomes a distinct instance.
    count: int = Field(ge=1, le=MAX_HALO_STONES_PER_RING)

    #: Centre-to-centre distance from the halo's centre to each stone.
    #:
    #: A POSITION parameter, never a clearance. This layer knows no stone's
    #: size, so it cannot claim two stones do not touch — whether they do is a
    #: GEOMETRIC fact for Geometry Inspection, and whether the result is
    #: settable is a professional question nobody here can answer.
    radiusMm: float = Field(gt=0.0, le=200.0, allow_inf_nan=False)

    #: Second semi-axis, for an elliptical halo around an oval or marquise
    #: centre. `None` means circular.
    radiusYMm: float | None = Field(
        default=None, gt=0.0, le=200.0, allow_inf_nan=False
    )

    startAngleDeg: float = Field(
        default=0.0, ge=-360.0, le=360.0, allow_inf_nan=False
    )

    #: Under 360 lays the ring on an arc — a partial halo, which is a real
    #: design rather than a degenerate case.
    sweepDeg: float = Field(default=360.0, gt=0.0, le=360.0, allow_inf_nan=False)

    #: Vertical offset from the halo's centre plane.
    #:
    #: WHAT MAKES A HIDDEN HALO REAL rather than a label. A hidden halo sits
    #: below the centre stone's girdle, under the crown, and this is the field
    #: that puts it there — it reaches the stone solid through the arrangement's
    #: own `InstanceTransform.zMm`. A `SINGLE` halo leaves it at zero.
    zOffsetMm: float = Field(
        default=0.0, ge=-200.0, le=200.0, allow_inf_nan=False
    )

    #: Default scale for this ring's stones, applied to the referenced stone's
    #: real resolved dimensions. A CONSTRUCTION default, not a proportion rule:
    #: no sourced professional evidence says a halo stone should be any
    #: particular fraction of its centre.
    memberScale: float = Field(
        default=0.25, gt=0.01, le=10.0, allow_inf_nan=False
    )

    #: Whether each stone is rotated to face outward along its own radius.
    alignToRadius: bool = True

    #: Which stone specification this ring's stones are occurrences of.
    #: `"primary"` is the definition's own `stone`; any other value names a
    #: future named specification and is reported unresolved rather than
    #: silently treated as the primary one.
    stoneRef: str = Field(
        default="primary", pattern=HALO_ID_PATTERN, max_length=MAX_HALO_ID_LENGTH
    )

    #: This ring's gem. `None` inherits the referenced stone's, which is what
    #: makes "the whole halo in sapphire" one edit rather than sixteen.
    gem: GemIdentity | None = None

    #: The setting this ring wants, by name. A REQUEST, not an implementation:
    #: the Setting System decides what the name means and whether it can be
    #: built, and today builds one only for the primary stone.
    settingRef: str | None = Field(default=None, max_length=40)

    #: Per-stone overrides, for the stones in this ring that differ.
    #:
    #: REUSES `FamilyMember` rather than declaring a parallel member model,
    #: because the value this carries IS a family member: a role, a stone
    #: reference, an optional gem, a scale, an orientation, a placement override
    #: and a setting request. A second model with the same seven fields would be
    #: two definitions of one concept — exactly what this sprint must not
    #: create.
    #:
    #: Members are matched to positions by SORTED ID, never by array order, so
    #: reordering this list cannot move a stone.
    members: list[FamilyMember] = Field(
        default_factory=list, max_length=MAX_HALO_STONES_PER_RING
    )

    @model_validator(mode="after")
    def _member_ids_are_unique(self) -> HaloRing:
        seen: set[str] = set()
        for member in self.members:
            if member.memberId in seen:
                raise ValueError(
                    f"halo ring '{self.ringId}' contains duplicate memberId "
                    f"'{member.memberId}'."
                )
            seen.add(member.memberId)
        return self

    @model_validator(mode="after")
    def _members_do_not_exceed_the_ring(self) -> HaloRing:
        """A ring cannot carry more named stones than stones.

        Refused rather than truncated: a member the compilation would drop is a
        stone the document declared and the design does not contain.
        """

        if len(self.members) > self.count:
            raise ValueError(
                f"halo ring '{self.ringId}' declares {len(self.members)} members "
                f"but only {self.count} stone(s). Raise `count`, or remove the "
                "extra members — a member with no position would be silently "
                "dropped."
            )
        return self


class HaloDefinition(HaloModel):
    """A halo around a centre.

    `rings` are the stones; `centerMemberId` says what they surround.

    ABSENT IS NOT EMPTY. A definition with no halo behaves exactly as it did
    before this sprint. Reading a missing halo as an implicit one would give
    every stored document a halo it never declared, and its hash would change
    with it.
    """

    variant: HaloVariant

    #: Ordered by radius in the sense that matters — `DEFAULT_RING_IDS` names
    #: the inner ring first — but identity is the `ringId`, and reordering this
    #: list produces the same compiled arrangement.
    rings: list[HaloRing] = Field(min_length=1, max_length=MAX_HALO_RINGS)

    #: The arrangement instance this halo surrounds.
    #:
    #: `None` anchors the halo on the DESIGN ORIGIN, which is how a halo
    #: surrounds a multi-stone centre: a toi-et-moi pair straddles the origin,
    #: so a ring centred there encircles both stones rather than one of them.
    #: A named value must exist in the arrangement the halo composes onto, and
    #: is refused rather than defaulted if it does not — a halo whose centre
    #: silently moved would surround something nobody nominated.
    centerMemberId: str | None = Field(
        default=DEFAULT_CENTER_MEMBER_ID,
        pattern=HALO_ID_PATTERN,
        max_length=MAX_HALO_ID_LENGTH,
    )

    #: A human label, carried through for Studio. Never used for identity.
    label: str | None = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def _rings_match_the_variant(self) -> HaloDefinition:
        """The variant and the ring count must agree.

        Two fields describing one structure can disagree, and a `DOUBLE` halo
        carrying one ring has no determinate meaning. Checked against
        `HALO_RING_CARDINALITY` rather than inline, so Forge reports the same
        failure from the same table without compiling.
        """

        expected = HALO_RING_CARDINALITY.get(self.variant)
        if expected is not None and len(self.rings) != expected:
            raise ValueError(
                f"a {self.variant} halo describes exactly {expected} ring(s), "
                f"but {len(self.rings)} were declared."
            )
        return self

    @model_validator(mode="after")
    def _ring_ids_are_unique(self) -> HaloDefinition:
        """Ids are the authoritative identity, so a duplicate makes every
        reference to a ring — a relation, a generated component, an inspection
        fact — ambiguous."""

        seen: set[str] = set()
        for ring in self.rings:
            if ring.ringId in seen:
                raise ValueError(
                    f"halo.rings contains duplicate ringId '{ring.ringId}'."
                )
            seen.add(ring.ringId)
        return self

    @model_validator(mode="after")
    def _member_ids_are_unique_across_rings(self) -> HaloDefinition:
        """A member id is an ARRANGEMENT instance id once compiled, so it must
        be unique across the whole halo, not merely within one ring."""

        seen: set[str] = set()
        for ring in self.rings:
            for member in ring.members:
                if member.memberId in seen:
                    raise ValueError(
                        f"halo declares memberId '{member.memberId}' in more "
                        "than one ring; a member id becomes an arrangement "
                        "instance id and must be unique across the halo."
                    )
                seen.add(member.memberId)
        return self

    @model_validator(mode="after")
    def _hidden_halo_sits_below_the_centre(self) -> HaloDefinition:
        """A `HIDDEN` halo must actually be offset below the centre plane.

        STRUCTURAL, NOT A PROFESSIONAL THRESHOLD. No minimum offset is
        prescribed and none could be without sourced evidence; what is checked
        is only that the offset is negative, because a hidden halo sitting at or
        above the centre plane is a `SINGLE` halo mislabelled, and the label is
        what every downstream consumer reads.
        """

        if self.variant != "HIDDEN":
            return self
        for ring in self.rings:
            if ring.zOffsetMm >= 0.0:
                raise ValueError(
                    f"a HIDDEN halo must sit below the centre plane, but ring "
                    f"'{ring.ringId}' declares zOffsetMm={ring.zOffsetMm}. Use "
                    "variant 'SINGLE' for a halo level with the centre stone."
                )
        return self

    @model_validator(mode="after")
    def _total_stone_count_is_bounded(self) -> HaloDefinition:
        total = sum(ring.count for ring in self.rings)
        if total > MAX_HALO_STONES:
            raise ValueError(
                f"this halo declares {total} stones, above the software bound "
                f"of {MAX_HALO_STONES}. An implementation limit, not a "
                "statement about how many stones a design should have."
            )
        return self
