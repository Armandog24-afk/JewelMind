"""Ring Family domain models (Sprint 28).

WHAT A RING FAMILY IS. A parametric RELATION between a ring's finger size, its
structure, the stones it carries and how they are held. Changing one family
parameter regenerates every part of the design that depends on it.

WHAT IT IS NOT, and this is the whole point of the sprint:

- **Not a preset.** A preset stores a finished set of values. A family stores a
  RELATION, so `ring.size` and `stone.diameter` still drive the geometry and the
  family's own parameters modulate what they produce.
- **Not a second engine.** A family DERIVES the existing blocks it owns — the
  band's architecture and taper, the head's height, the stone family, the halo,
  the pavé field — and every one of those is then executed by the system that
  already owns it. `resolve.py` writes derivations; it builds nothing.
- **Not a catalogue.** A new combination is a new set of parameter values, never
  a new class: "cathedral + oval diamond + four prongs + pavé shoulders" is one
  variant with four parameters, not a hardcoded family.

WHERE THE FAMILY COMES FROM. `jewelry.style` has meant "ring family" since
Sprint 16 (`ring/families.py` dispatches on it), so it stays the ONE authority
for which family a document declares. `ringFamily` carries the VARIANT and the
parameters — the family/variant separation §15 asks for, with one authority for
each half rather than two fields that can disagree.

NOTHING HERE IS A PROFESSIONAL MEASUREMENT. Every ratio and dimension is a
software CONSTRUCTION PARAMETER, and every default was chosen to produce robust
geometry inside the schema's own range. No minimum shank section, no shoulder
proportion, no table size and no finger-size formula beyond the one
`validation/sizing.py` already owns is asserted anywhere.

Nothing here imports a geometry module, the CAD kernel or `JewelryDefinition`.
"""

from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# `errors.py` imports nothing from this module, so this direction is acyclic —
# and it is what lets `default_variant_for()` raise a DOMAIN error rather than a
# bare `KeyError` a caller guarding on `RingFamilyError` cannot catch.
from jewelmind.ring_family.errors import RingFamilyUnsupportedVariantError

#: Version of the family TAXONOMY — the variant id set, the family mapping and
#: the parameter contract. Distinct from the geometry versions, which record how
#: solids are built: a variant can be documented or reserved without any
#: geometry changing.
RING_FAMILY_TAXONOMY_VERSION = "1.0.0"

#: Every ring-family variant with a real, executable derivation behind it.
#:
#: FAMILY-PREFIXED, deliberately. Sprint 27 established that a prefixed id set
#: (`PRONG_ROUND`, `BEZEL_PARTIAL`) stays unambiguous as it grows, and it lets
#: the family be recovered from the variant without a second table.
#:
#: A variant is a member here only if it derives something REAL. `SOLITAIRE_LOW_PROFILE`
#: qualifies because it genuinely changes the head's height and therefore the
#: stone's position; a variant that only changed a label would not.
RingFamilyVariantId = Literal[
    # SOLITAIRE — one centre stone. The four variants differ structurally.
    "SOLITAIRE_CLASSIC",
    "SOLITAIRE_CATHEDRAL",
    "SOLITAIRE_LOW_PROFILE",
    "SOLITAIRE_ELEVATED",
    # THREE_STONE — a centre plus two sides, composed onto the stone family.
    "THREE_STONE_SYMMETRIC",
    "THREE_STONE_GRADUATED",
    # HALO — a centre surrounded, composed onto the Halo System.
    "HALO_SINGLE",
    "HALO_DOUBLE",
    "HALO_HIDDEN",
    # SPLIT_SHANK — the shank genuinely divides toward the head.
    "SPLIT_SHANK_PARALLEL",
    "SPLIT_SHANK_TAPERED",
    # BYPASS — one open rail whose ends pass each other at the top.
    "BYPASS_CROSSOVER",
    # SIGNET — a solid body with a table at the ring's top.
    "SIGNET_FLAT_TABLE",
]

#: Which family each variant belongs to, stated ONCE and inverted where the
#: other direction is needed. `jewelry.style` is the family authority; this is
#: what lets a declared variant be checked against it.
VARIANT_FAMILY: dict[str, str] = {
    "SOLITAIRE_CLASSIC": "solitaire",
    "SOLITAIRE_CATHEDRAL": "solitaire",
    "SOLITAIRE_LOW_PROFILE": "solitaire",
    "SOLITAIRE_ELEVATED": "solitaire",
    "THREE_STONE_SYMMETRIC": "three_stone",
    "THREE_STONE_GRADUATED": "three_stone",
    "HALO_SINGLE": "halo",
    "HALO_DOUBLE": "halo",
    "HALO_HIDDEN": "halo",
    "SPLIT_SHANK_PARALLEL": "split_shank",
    "SPLIT_SHANK_TAPERED": "split_shank",
    "BYPASS_CROSSOVER": "bypass",
    "SIGNET_FLAT_TABLE": "signet",
}

#: The variant a family falls back to when a document declares no `ringFamily`.
#:
#: Every one of them reproduces what the family means with nothing else stated,
#: and `solitaire`'s default reproduces the PRE-SPRINT-28 solitaire exactly —
#: which is what makes the fallback a compatibility guarantee rather than a
#: preference.
DEFAULT_VARIANT: dict[str, str] = {
    "solitaire": "SOLITAIRE_CLASSIC",
    "three_stone": "THREE_STONE_SYMMETRIC",
    "halo": "HALO_SINGLE",
    "split_shank": "SPLIT_SHANK_PARALLEL",
    "bypass": "BYPASS_CROSSOVER",
    "signet": "SIGNET_FLAT_TABLE",
}

#: Ring families and variants named for architectural completeness, with NO
#: derivation and NO membership in the literals above.
#:
#: Each value is the REAL TECHNICAL REASON the capability is absent. A reader
#: should be able to tell what would have to exist first — which is why the
#: reason is written down instead of the word "planned".
RESERVED_RING_FAMILIES: dict[str, str] = {
    "eternity": (
        "A full eternity band sets stones around the entire circumference, which "
        "needs a pavé field whose host is the band's own outer surface over 360 "
        "degrees AND a channel or bead retention that follows it. The pavé "
        "engine's containment policy clips a field at the host's declared extent "
        "rather than wrapping it, so a 360-degree field is not expressible yet."
    ),
    "toi_et_moi": (
        "Two equal stones side by side is already expressible as the "
        "TOI_ET_MOI stone family (Sprint 24). A RING family of the same name "
        "would be a second authority over the same placement, which is what "
        "JM-FAMILY-001 refuses. It stays reserved so the name cannot be taken "
        "for something else."
    ),
    "cluster": (
        "A cluster ring's stones are already the CLUSTER stone family "
        "(Sprint 24), composed onto any ring family. A separate ring family "
        "would duplicate it for no capability gain."
    ),
    "plain_band": (
        "A band with no stone at all requires the assembly to build no stone, no "
        "setting and no head. Every current component contract treats "
        "`stone_reference` and `basket_support` as required, so a stone-less ring "
        "is a change to the required-component set — an ADR condition — rather "
        "than a family parameter."
    ),
    "SOLITAIRE_TRELLIS": (
        "A trellis solitaire's arches are the reserved TRELLIS head "
        "architecture (Sprint 27), which needs a verifiable swept solid along a "
        "3D spline. No builder exists."
    ),
    "SPLIT_SHANK_SCULPTED": (
        "A split shank whose rails follow a sculpted 3D path rather than the "
        "ring's own circle. It needs a swept solid along a spline for the same "
        "reason the trellis head does."
    ),
    "BYPASS_TWIST": (
        "A bypass whose rails twist about their own axis as they travel. The "
        "current construction lofts sections that translate axially; adding a "
        "per-section rotation about the rail's tangent is a different sweep and "
        "is not yet verifiable."
    ),
    "SIGNET_ENGRAVED": (
        "An engraved signet table needs a surface-decoration system: a relief or "
        "an engraving is a cut driven by a 2D pattern, and no pattern "
        "representation exists anywhere in the pipeline. Sprint 29's specialty "
        "work is where that belongs."
    ),
    "SIGNET_OVAL_TABLE": (
        "An oval or cushion signet table needs the table's outline to come from "
        "the same outline machinery the Stone System uses. Reusing it would be "
        "correct and is not wired: `stone/outline.py` builds a STONE's girdle, "
        "and giving it a second caller for a metal table is a real change to "
        "that module's contract."
    ),
}

#: How each variant scales the head's height, before the author's own
#: `headHeightFactor` is applied.
#:
#: THIS IS WHAT MAKES A VARIANT A VARIANT rather than a name. A low-profile
#: solitaire sits the stone closer to the finger and an elevated one raises it,
#: and both are real changes to `setting.basketHeight` and therefore to where
#: the stone sits, how tall the shoulder arches are, and how much metal the head
#: contains.
#:
#: EVERY VALUE IS A SOFTWARE CONSTRUCTION PARAMETER. No professional proportion
#: is claimed: nothing here says how high a stone should sit, only how this
#: variant differs from the family's baseline. `1.0` means the variant does not
#: change the height, which is the honest value for every family whose
#: distinction lies elsewhere.
VARIANT_HEAD_HEIGHT_FACTOR: dict[str, float] = {
    "SOLITAIRE_CLASSIC": 1.0,
    "SOLITAIRE_CATHEDRAL": 1.0,
    "SOLITAIRE_LOW_PROFILE": 0.6,
    "SOLITAIRE_ELEVATED": 1.45,
    "THREE_STONE_SYMMETRIC": 1.0,
    "THREE_STONE_GRADUATED": 1.0,
    "HALO_SINGLE": 1.0,
    "HALO_DOUBLE": 1.0,
    "HALO_HIDDEN": 1.15,
    "SPLIT_SHANK_PARALLEL": 1.0,
    "SPLIT_SHANK_TAPERED": 1.0,
    "BYPASS_CROSSOVER": 1.0,
    "SIGNET_FLAT_TABLE": 1.0,
}

#: Which shank architecture each variant needs. `UNIFORM` is the pre-Sprint-28
#: full ring, and the value every solitaire, three-stone, halo and signet
#: variant keeps — so those families change nothing about the band.
VARIANT_SHANK_ARCHITECTURE: dict[str, str] = {
    "SOLITAIRE_CLASSIC": "UNIFORM",
    "SOLITAIRE_CATHEDRAL": "UNIFORM",
    "SOLITAIRE_LOW_PROFILE": "UNIFORM",
    "SOLITAIRE_ELEVATED": "UNIFORM",
    "THREE_STONE_SYMMETRIC": "UNIFORM",
    "THREE_STONE_GRADUATED": "UNIFORM",
    "HALO_SINGLE": "UNIFORM",
    "HALO_DOUBLE": "UNIFORM",
    "HALO_HIDDEN": "UNIFORM",
    "SPLIT_SHANK_PARALLEL": "SPLIT",
    "SPLIT_SHANK_TAPERED": "SPLIT",
    "BYPASS_CROSSOVER": "BYPASS",
    "SIGNET_FLAT_TABLE": "UNIFORM",
}

#: Which shoulder architecture each variant builds.
#:
#: `NONE` is the pre-Sprint-28 state and is honest rather than empty: before
#: this sprint the shank flowed directly into the head with no distinct
#: transition component, which `ring/models.py::ShoulderDefinition` has recorded
#: as unmodelled since Sprint 16.
VARIANT_SHOULDER_ARCHITECTURE: dict[str, str] = {
    "SOLITAIRE_CLASSIC": "NONE",
    "SOLITAIRE_CATHEDRAL": "CATHEDRAL",
    "SOLITAIRE_LOW_PROFILE": "NONE",
    "SOLITAIRE_ELEVATED": "CATHEDRAL",
    "THREE_STONE_SYMMETRIC": "NONE",
    "THREE_STONE_GRADUATED": "NONE",
    "HALO_SINGLE": "NONE",
    "HALO_DOUBLE": "NONE",
    "HALO_HIDDEN": "NONE",
    "SPLIT_SHANK_PARALLEL": "SPLIT_RAILS",
    "SPLIT_SHANK_TAPERED": "SPLIT_RAILS",
    "BYPASS_CROSSOVER": "NONE",
    "SIGNET_FLAT_TABLE": "NONE",
}

#: Which body architecture each variant builds. `NONE` for every family but the
#: signet, whose defining feature is a solid body at the ring's top.
VARIANT_BODY_ARCHITECTURE: dict[str, str] = {
    variant: ("SIGNET_TABLE" if variant.startswith("SIGNET_") else "NONE")
    for variant in VARIANT_FAMILY
}

#: SOFTWARE SAFETY LIMITS, documented as such. A malformed or hostile document
#: must not be able to ask the kernel for an unbounded amount of work: a
#: pathological halo count or side-stone spacing would otherwise exhaust memory
#: before any validation reported it. NOT jewelry limits — nothing here claims
#: how many stones a ring should carry.
MAX_HALO_STONES_PER_FAMILY = 96
MAX_SIDE_SPACING_MM = 40.0

RingFamilySymmetry = Literal["SYMMETRIC", "ASYMMETRIC"]


class RingFamilyModel(BaseModel):
    """Strict, kernel-neutral, immutable base.

    `strict=True` matches `domain/schema.py::StrictModel` and every sibling
    domain package: these models are carried DIRECTLY in JDL rather than through
    a hand-written mirror, so they apply JDL's own untrusted-input policy.
    `frozen=True` because a family is replaced, never mutated — resolution
    returns new objects, so a shared reference cannot be edited out from under a
    computed fingerprint.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class RingFamilyParams(RingFamilyModel):
    """The family's parametric knobs.

    ONE FLAT MODEL, NOT A DISCRIMINATED UNION, and for the reason Sprint 26 and
    Sprint 27 both recorded: a discriminated union at the JDL layer cannot be
    reached by a dotted-path patch, which is exactly the defect that stopped
    Designer creating a pavé. A flat model keeps every route — a UI control, a
    spoken request, a hand-written document — able to set one value.

    EVERY PARAMETER IS A MODULATION OR A DIMENSION, never a replacement. A
    factor multiplies what the document already states, so `ring.size`,
    `band.width` and `stone.diameter` keep driving the geometry and the family
    modulates what they produce. That is what makes the system parametric rather
    than a set of stored values.

    A parameter a variant does not read is reported as INFORMATION by
    `JM-RINGFAM-003` rather than silently ignored, and a test asserts every
    field here is read by at least one variant — a field nothing reads would be
    the silently ignored parameter ARRANGE-GOV-011 forbids.
    """

    # ---- head / profile -----------------------------------------------------

    #: Multiplies `setting.basketHeight`, which is what raises or lowers the
    #: stone. A MODULATION: the document's own basket height still sets the
    #: scale, and this says how the variant changes it.
    headHeightFactor: float = Field(
        default=1.0, gt=0.05, le=5.0, allow_inf_nan=False
    )

    # ---- cathedral / split shoulders ---------------------------------------

    #: Angular distance from the top of the ring, in degrees, at which each
    #: shoulder meets the band. A larger span starts the arch further down.
    #:
    #: BOUNDED AT 90 BY THE CONSTRUCTION, and the bound is a mirror rather than
    #: a second authority: `geometry/shoulder.py::MAX_ARCH_SPAN_DEG` is the
    #: measured limit of a ruled-loft arch, and this field refuses at the schema
    #: layer what the builder refuses at the geometry layer. Sprint 28 shipped
    #: `le=170.0` first, which accepted spans that built a self-intersecting
    #: solid OCC's own validity check passed — an accepted value that produces
    #: invalid geometry is worse than a refused one.
    #:
    #: NOT A PROFESSIONAL THRESHOLD. It says nothing about how far down a
    #: shoulder should reach; it is the angle past which this construction
    #: cannot be built at all.
    shoulderSpanDeg: float = Field(
        default=50.0, gt=1.0, le=90.0, allow_inf_nan=False
    )

    #: The shoulder's section at the head, as a fraction of the band's own width
    #: and thickness. Below 1.0 so the arch narrows as it rises, which is what
    #: distinguishes a shoulder from a thickened band.
    shoulderTopWidthFactor: float = Field(
        default=0.85, gt=0.05, le=1.0, allow_inf_nan=False
    )
    shoulderTopThicknessFactor: float = Field(
        default=0.85, gt=0.05, le=1.0, allow_inf_nan=False
    )

    # ---- split shank --------------------------------------------------------

    #: Clear axial distance between the two rails. The rails share the band's
    #: own width, so a wider separation makes each rail narrower — which is why
    #: the schema bounds it and `JM-RINGFAM-004` refuses a separation that would
    #: leave no rail at all.
    splitSeparationMm: float = Field(
        default=1.2, gt=0.0, le=20.0, allow_inf_nan=False
    )

    #: Angular span, centred on the BOTTOM of the ring, over which the rails are
    #: joined into one band. Outside it the shank is genuinely two rails.
    splitJoinSpanDeg: float = Field(
        default=200.0, gt=10.0, le=350.0, allow_inf_nan=False
    )

    # ---- bypass -------------------------------------------------------------

    #: Clear axial distance between the rail's two ends where they pass each
    #: other. Same width-sharing relation as `splitSeparationMm`.
    bypassSeparationMm: float = Field(
        default=1.0, gt=0.0, le=20.0, allow_inf_nan=False
    )

    #: How far past a full turn the rail travels, in degrees. This is what makes
    #: the two ends PASS each other rather than meet: over this span both ends
    #: occupy the same angle at different axial positions.
    bypassOverlapDeg: float = Field(
        default=60.0, gt=5.0, le=180.0, allow_inf_nan=False
    )

    # ---- signet -------------------------------------------------------------

    #: The table's extent along the ring's own circumferential direction, across
    #: it, and how far it rises above the band's top.
    signetTableLengthMm: float = Field(
        default=11.0, gt=0.1, le=60.0, allow_inf_nan=False
    )
    signetTableWidthMm: float = Field(
        default=9.0, gt=0.1, le=60.0, allow_inf_nan=False
    )
    signetTableHeightMm: float = Field(
        default=2.0, gt=0.1, le=30.0, allow_inf_nan=False
    )

    # ---- side stones (delegated to the stone family) ------------------------

    #: Uniform scale of each side stone relative to the centre. Handed to the
    #: Multi-Stone Family layer, which owns what a side stone IS.
    sideStoneScale: float = Field(
        default=0.55, gt=0.01, le=10.0, allow_inf_nan=False
    )

    #: Centre-to-centre distance from the centre stone to each side stone.
    sideSpacingMm: float = Field(
        default=5.0, gt=0.0, le=MAX_SIDE_SPACING_MM, allow_inf_nan=False
    )

    #: For `THREE_STONE_GRADUATED`: each successive side stone's scale relative
    #: to the previous one. 1.0 would make the variant identical to the
    #: symmetric one, so the schema keeps it strictly below.
    sideGraduationFactor: float = Field(
        default=0.8, gt=0.05, lt=1.0, allow_inf_nan=False
    )

    # ---- halo (delegated to the Halo System) --------------------------------

    haloStoneCount: int = Field(default=16, ge=3, le=MAX_HALO_STONES_PER_FAMILY)

    #: The halo ring's radius as a multiple of the centre stone's own half
    #: width. A RELATION rather than a millimetre value, which is what makes the
    #: halo follow the stone when the stone changes.
    haloRadiusFactor: float = Field(
        default=1.05, gt=0.1, le=10.0, allow_inf_nan=False
    )
    haloStoneScale: float = Field(
        default=0.22, gt=0.01, le=10.0, allow_inf_nan=False
    )

    # ---- pavé shoulders (delegated to the Pavé Engine) ---------------------

    #: Whether the family composes a pavé field onto the shank's shoulders.
    #: Composition, not a new capability: the Pavé Engine does every piece of it.
    paveShoulders: bool = False
    paveSpanDeg: float = Field(
        default=90.0, gt=1.0, le=360.0, allow_inf_nan=False
    )
    paveStoneScale: float = Field(
        default=0.1, gt=0.001, le=10.0, allow_inf_nan=False
    )

    # ---- shared -------------------------------------------------------------

    #: Whether the family's derived placements are mirrored about the ring's own
    #: midplane. Read by the multi-stone variants, where it decides whether the
    #: two side stones are placed symmetrically or graduated in one direction.
    symmetry: RingFamilySymmetry = "SYMMETRIC"


class RingFamilySpec(RingFamilyModel):
    """A ring family as a document declares it.

    ONLY THE VARIANT AND THE PARAMETERS. The FAMILY comes from
    `jewelry.style`, which has meant "ring family" since Sprint 16 and is
    already the value `ring/families.py` dispatches on — so there is exactly one
    authority for the family and one for the variant, rather than two fields
    that can disagree. A variant that does not belong to the declared family is
    refused by `JM-RINGFAM-001` rather than resolved by precedence.

    ABSENT IS NOT EMPTY. A document with no `ringFamily` resolves to its
    family's default variant with default parameters, which for `solitaire`
    reproduces the pre-Sprint-28 design exactly.
    """

    variant: RingFamilyVariantId

    #: Whether the variant participates. `false` keeps the parameters in the
    #: document and falls back to the family's DEFAULT variant — a different
    #: state from declaring no family block at all, and reported as such.
    enabled: bool = True

    params: RingFamilyParams = Field(default_factory=RingFamilyParams)

    #: A human label, carried through for Studio. Never used for identity.
    label: str | None = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def _variant_is_known(self) -> RingFamilySpec:
        """Belt and braces over the closed literal.

        The literal already refuses an unknown variant; this refuses one that is
        a literal member but has no family mapping, which would otherwise
        resolve to nothing at all.
        """

        if self.variant not in VARIANT_FAMILY:
            raise ValueError(
                f"ring family variant '{self.variant}' has no family mapping. "
                "Every member of RingFamilyVariantId must appear in "
                "VARIANT_FAMILY, or a document choosing it would resolve to "
                "nothing."
            )
        return self


def variants_for_family(family: str) -> tuple[str, ...]:
    """Every implemented variant of one family, sorted.

    Derived by inverting `VARIANT_FAMILY` rather than restated, because two
    hand-written tables is how a mapping drifts.
    """

    return tuple(
        sorted(
            variant
            for variant, mapped in VARIANT_FAMILY.items()
            if mapped == family
        )
    )


def implemented_families() -> tuple[str, ...]:
    """Every family with at least one implemented variant, sorted."""

    return tuple(sorted(set(VARIANT_FAMILY.values())))


def family_for_variant(variant: str) -> str:
    family = VARIANT_FAMILY.get(variant)
    if family is None:
        raise KeyError(f"ring family variant {variant!r} has no family.")
    return family


def default_variant_for(family: str) -> str:
    """The variant a document with no `ringFamily` resolves to.

    RAISES A DOMAIN ERROR, not a `KeyError`. It shipped as a bare `KeyError`
    first, and `test_ring_architecture.py` caught what that costs: a caller
    guarding on `RingFamilyError` — as `ring/adapter.py` does — cannot catch a
    `KeyError`, so a family with no generator escaped the guard and surfaced as
    an untyped exception from three frames down instead of the clean dispatch
    refusal the boundary is supposed to produce.

    A reserved family reaches here only when a caller has bypassed schema
    validation, which is exactly what that test does deliberately.
    """

    variant = DEFAULT_VARIANT.get(family)
    if variant is None:
        raise RingFamilyUnsupportedVariantError(
            f"No default ring-family variant is defined for family {family!r}. "
            "Every implemented family must have one, or a document choosing it "
            f"would resolve to nothing. Implemented: {list(implemented_families())}."
        )
    return variant


def default_params() -> RingFamilyParams:
    """The parameters a family gets when it is chosen with no values.

    ONE DEFINITION OF "PICK THIS FAMILY", owned by the domain rather than by
    each interface — the discipline `default_pave_field()` and
    `default_mode_parameters()` both established, after Designer and Studio
    could otherwise have produced different designs from the same instruction.
    """

    return RingFamilyParams()


#: Length of a ring-family fingerprint, matching every other identity in the
#: project (`definitionHash`, `arrangementFingerprint`, `compilationHash`,
#: `settingModeFingerprint`).
RING_FAMILY_FINGERPRINT_LENGTH = 16


def ring_family_fingerprint(family: str, variant: str, params: RingFamilyParams) -> str:
    """Deterministic identity of a resolved ring family.

    THE FAMILY'S OWN CONTENT AND NOTHING ELSE — no wall-clock time, no random
    value, no process id, no memory address and no iteration order.

    NOT A REPLACEMENT FOR ANY EXISTING IDENTITY. `definitionHash` still
    identifies the whole document and `compilationHash` the environment that
    built it; this identifies one family resolution, so a report can name it
    without re-deriving it.

    The LABEL is deliberately excluded: renaming a family does not change what
    it builds, and an identity that moved when a label changed would make every
    derived report churn for a rename.
    """

    payload = {
        "family": family,
        "variant": variant,
        "params": params.model_dump(mode="json"),
        "taxonomyVersion": RING_FAMILY_TAXONOMY_VERSION,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[
        :RING_FAMILY_FINGERPRINT_LENGTH
    ]
