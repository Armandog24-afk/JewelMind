"""Category-neutral Gem Identity domain models (brief sections 3-10/13).

THE CENTRAL SEPARATION OF THIS SPRINT: a stone's geometry and a stone's gem
identity are different things, and neither implies the other.

    StoneSpec       what shape and size the stone is        (Sprint 18/20)
    GemDefinition   what KIND of gem this is                (registry, type-level)
    GemIdentity     what THIS stone actually is             (per-stone)
    GemVisualProfile how a gem is rendered                  (Vision input)
    StoneInstance   one stone occurrence in a design        (future arrangements)

A round stone is not automatically a diamond. An oval stone is not automatically
a sapphire. The same `StoneSpec` is reusable with any `GemIdentity`, and
changing the gem does not change the geometry.

THE TYPE / INSTANCE SPLIT, and why it is not optional.

A registry entry for "ruby" cannot know whether *this particular* ruby was
heated, or whether it is natural or lab-grown. Those are facts about a specific
stone, not about the species. So:

- `GemDefinition` (registry) carries taxonomy, material class, aliases, which
  origins are APPLICABLE, and a default visual profile.
- `GemIdentity` (per-stone, and what JDL stores) carries the ACTUAL origin, the
  actual treatments, and any override.

Cramming treatment state into the registry would mean either a separate entry
per treatment combination — a combinatorial explosion — or a registry that
silently asserts something about a stone it has never seen.

Every model here is kernel-neutral: no field holds a CadQuery or OCP object,
and nothing imports a jewelry category.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# ---------------------------------------------------------------------------
# Canonical vocabularies. Every value is language-independent (brief section 31).
# ---------------------------------------------------------------------------

#: What a gem material fundamentally IS.
#:
#: `ORGANIC` exists because the architecture must not assume every gem is a
#: mineral (brief section 8): a pearl, amber and coral have no crystal system,
#: no mineral species, and no meaningful variety — forcing mineralogical fields
#: onto them would be inventing facts.
GemMaterialClass = Literal[
    "MINERAL",
    "ORGANIC",
    "NON_MINERAL",
    "COMPOSITE",
    "UNKNOWN",
]

#: How the gem came to exist. INDEPENDENT of treatment (brief section 6).
#:
#: Deliberately NOT a boolean `isNatural`. A stone may be natural AND treated,
#: or synthetic AND untreated, and a single flag cannot express either without
#: losing the other. `SIMULANT` is its own value because a simulant must never
#: identify as the material it imitates: cubic zirconia is not diamond, however
#: diamond-like it looks (brief section 9).
GemOrigin = Literal[
    "NATURAL",
    "SYNTHETIC",
    "SIMULANT",
    "COMPOSITE",
    "UNKNOWN",
]

#: Treatment types. NOT an exhaustive list, and the model must never imply it
#: is (brief section 7). `OTHER` carries a free-text note; `UNKNOWN` records
#: that treatment status is genuinely not known, which is different from
#: recording that a stone is untreated.
GemTreatmentType = Literal[
    "HEAT",
    "IRRADIATION",
    "FRACTURE_FILLING",
    "GLASS_FILLING",
    "COATING",
    "DIFFUSION",
    "DYEING",
    "IMPREGNATION",
    "RESIN_IMPREGNATION",
    "BLEACHING",
    "LASER_DRILLING",
    "HPHT",
    "OTHER",
    "UNKNOWN",
]

#: Whether a treatment is asserted to be present, absent, or unknown.
#:
#: `NOT_PRESENT` is a real, useful state — an explicit "this stone was not
#: heated" is different information from "we do not know". Neither is a
#: disclosure guarantee; see `GemTreatment.disclosure`.
GemTreatmentStatus = Literal["PRESENT", "NOT_PRESENT", "SUSPECTED", "UNKNOWN"]

#: Where the claim about a treatment came from. JewelMind never invents a
#: professional disclosure requirement (brief section 7) — this only records
#: who said so.
GemTreatmentDisclosure = Literal[
    "USER_DECLARED",
    "VENDOR_DECLARED",
    "LAB_REPORT_CLAIMED",
    "UNDISCLOSED",
    "UNKNOWN",
]

#: Confidence in a recorded claim. A software confidence label, never a
#: gemological grading.
GemConfidence = Literal["HIGH", "MEDIUM", "LOW", "UNKNOWN"]

#: Registry entry lifecycle (brief section 29).
#:
#: A `DEPRECATED` entry must stay RESOLVABLE, because a saved project may
#: reference it. Entries are never deleted.
GemEntryStatus = Literal["CURRENT", "DEPRECATED", "CUSTOM", "UNKNOWN"]

#: Where a registry entry's data came from (brief section 27).
#:
#: `INTERNAL_TAXONOMY` is the honest label for JewelMind's own organizing
#: choices. Nothing in this system is `PROFESSIONALLY_VALIDATED`, and marking an
#: internal assumption as a professional fact is forbidden.
GemDataProvenance = Literal[
    "INTERNAL_TAXONOMY",
    "SOURCED",
    "USER_AUTHORED",
    "PRELIMINARY",
    "PROFESSIONALLY_VALIDATED",
    "UNKNOWN",
]

#: How Vision should render a gem. A rendering CATEGORY, not an optical claim.
GemRenderCategory = Literal[
    "TRANSPARENT_BRILLIANT",
    "TRANSPARENT_COLOURED",
    "TRANSLUCENT",
    "OPAQUE",
    "IRIDESCENT",
    "PEARLESCENT",
    "FALLBACK",
]

#: The role a stone plays in a design. Present so gem identity is addressable
#: PER OCCURRENCE (brief section 16); only `CENTER` is currently produced.
StoneRole = Literal["CENTER", "SIDE", "ACCENT", "HALO", "PAVE", "UNKNOWN"]

#: The two reserved identity IDs. Mandatory escape hatches (brief section 10).
CUSTOM_GEM_ID = "custom"
UNKNOWN_GEM_ID = "unknown"

#: The visual profile used when a gem has none of its own. Represented
#: explicitly AS a fallback so it can never be mistaken for a real gem's
#: appearance (brief section 22).
FALLBACK_VISUAL_PROFILE_ID = "fallback.generic"


class GemModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
# Identifier discipline
# ---------------------------------------------------------------------------

#: Canonical gem IDs are lowercase, dot-separated, and language-independent
#: (brief section 31). A localized display name must never be a stable
#: identifier, because renaming a translation would change identity.
#:
#: The pattern also makes an ID unusable as a filesystem path or a shell
#: argument: no slashes, no dots-only segments, no whitespace, no separators
#: beyond `.`, `_` and `-` (brief section 37).
GEM_ID_PATTERN = r"^[a-z][a-z0-9_-]*(\.[a-z][a-z0-9_-]*)*$"
MAX_GEM_ID_LENGTH = 80


class GemVisualProfile(GemModel):
    """How a gem is rendered (brief section 13).

    EVERY VALUE HERE IS A RENDERING PARAMETER, NOT A MEASUREMENT. `ior` is the
    number a renderer is given to make a stone look plausible on screen; it is
    not this gem's refractive index as a laboratory would report it, and it must
    never be presented as such. The same applies to `dispersion`, which drives a
    sparkle effect rather than describing real spectral separation.
    """

    profileId: str = Field(pattern=GEM_ID_PATTERN, max_length=MAX_GEM_ID_LENGTH)
    renderCategory: GemRenderCategory

    #: Base colour as a CSS hex string. Constrained rather than free text so a
    #: malformed value cannot reach the renderer (brief section 37).
    baseColor: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")

    #: PBR parameters. Bounded to their physically meaningful ranges;
    #: `allow_inf_nan=False` follows the schema-wide numeric policy, without
    #: which `float("inf") > 0` would sail through a `ge`/`le` constraint.
    metalness: float = Field(default=0.0, ge=0.0, le=1.0, allow_inf_nan=False)
    roughness: float = Field(default=0.05, ge=0.0, le=1.0, allow_inf_nan=False)
    opacity: float = Field(default=1.0, ge=0.0, le=1.0, allow_inf_nan=False)
    transmission: float = Field(default=0.0, ge=0.0, le=1.0, allow_inf_nan=False)

    #: A renderer input, NOT a measured refractive index. Bounded to the range
    #: real renderers accept.
    ior: float = Field(default=1.5, ge=1.0, le=3.0, allow_inf_nan=False)
    thickness: float = Field(default=0.0, ge=0.0, le=10.0, allow_inf_nan=False)
    clearcoat: float = Field(default=0.0, ge=0.0, le=1.0, allow_inf_nan=False)
    envMapIntensity: float = Field(default=1.0, ge=0.0, le=5.0, allow_inf_nan=False)

    #: Sparkle strength. A stylistic dial, not a dispersion measurement.
    dispersion: float = Field(default=0.0, ge=0.0, le=1.0, allow_inf_nan=False)

    #: True when the appearance varies across the stone in a way a single
    #: colour cannot express (opal's play-of-colour, a pearl's orient). Vision
    #: currently approximates these; the flag records that the approximation is
    #: known to be one.
    hasVariableColour: bool = False

    #: True only for `FALLBACK_VISUAL_PROFILE_ID`. Carried as a real field so a
    #: consumer can tell a deliberate generic look from a gem's own appearance.
    isFallback: bool = False

    description: str = Field(min_length=10, max_length=400)


class GemTreatment(GemModel):
    """One treatment claim about one stone (brief section 7).

    Treatments live on `GemIdentity`, never on a registry entry: whether a
    particular ruby was heated is a fact about that stone.

    JewelMind records the claim and its source. It does not decide whether a
    treatment must be disclosed, whether it is stable, or whether it affects
    durability — all of which require professional evidence
    (GEM-GOV-006).
    """

    treatment: GemTreatmentType
    status: GemTreatmentStatus = "PRESENT"
    disclosure: GemTreatmentDisclosure = "USER_DECLARED"
    confidence: GemConfidence = "UNKNOWN"
    note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def _other_requires_a_note(self) -> GemTreatment:
        """`OTHER` without a note records nothing.

        The whole point of the escape-hatch value is to carry information the
        enum cannot; accepting it empty would let a caller assert "some other
        treatment" and convey no fact at all.
        """

        if self.treatment == "OTHER" and not (self.note or "").strip():
            raise ValueError(
                "a treatment of type 'OTHER' requires a note describing it"
            )
        return self


class GemDefinition(GemModel):
    """A registry entry: one KIND of gem (brief sections 4/5/11).

    Type-level only. It says what a ruby is; it says nothing about any
    particular ruby's origin or treatment.

    TAXONOMY IS OPTIONAL AT EVERY LEVEL (brief section 5). `family`, `species`
    and `variety` are each nullable, because the hierarchy genuinely does not
    apply uniformly:

        diamond    species only, no meaningful family/variety split
        ruby       family=corundum, species=corundum, variety=ruby
        amethyst   family=quartz, species=quartz, variety=amethyst
        pearl      ORGANIC — none of the three apply
        custom     user-authored, no taxonomy at all

    Where a hierarchy is not reliable for an entry, the honest representation is
    a null level, never an invented one (GEM-GOV-004).
    """

    gemId: str = Field(pattern=GEM_ID_PATTERN, max_length=MAX_GEM_ID_LENGTH)

    #: The stable English canonical name. Not a display string — see
    #: `displayNames` — and not an identifier.
    canonicalName: str = Field(min_length=2, max_length=80)

    #: Localized display names, keyed by ISO 639-1 code. A display name may be
    #: retranslated freely; `gemId` may not (brief section 31).
    displayNames: dict[str, str] = Field(default_factory=dict)

    materialClass: GemMaterialClass

    family: str | None = Field(default=None, max_length=60)
    species: str | None = Field(default=None, max_length=60)
    variety: str | None = Field(default=None, max_length=60)

    #: Which origins are meaningful for this gem TYPE. A simulant entry such as
    #: cubic zirconia lists only `SIMULANT`; diamond lists NATURAL and
    #: SYNTHETIC. Used to validate a `GemIdentity`, never to guess one.
    applicableOrigins: list[GemOrigin] = Field(min_length=1)

    #: Alternative names that resolve TO this entry. An alias is never a
    #: separate identity (brief section 30).
    aliases: list[str] = Field(default_factory=list)

    defaultVisualProfileId: str = Field(
        pattern=GEM_ID_PATTERN, max_length=MAX_GEM_ID_LENGTH
    )

    status: GemEntryStatus = "CURRENT"
    provenance: GemDataProvenance = "INTERNAL_TAXONOMY"

    #: Set only when `status` is `DEPRECATED`: the entry that supersedes this
    #: one. The deprecated entry stays resolvable regardless (brief section 29).
    supersededBy: str | None = Field(
        default=None, pattern=GEM_ID_PATTERN, max_length=MAX_GEM_ID_LENGTH
    )

    description: str = Field(min_length=10, max_length=500)


class GemIdentity(GemModel):
    """What THIS stone actually is (brief sections 4/6/7/16).

    This is what JDL stores per stone, and it is deliberately separate from the
    registry entry it points at.

    `gemId` alone is not an identity: a natural untreated sapphire and a
    heat-treated lab-grown sapphire share a `gemId` and are different stones.
    """

    gemId: str = Field(pattern=GEM_ID_PATTERN, max_length=MAX_GEM_ID_LENGTH)

    #: The ACTUAL origin of this stone. Validated against the registry entry's
    #: `applicableOrigins`, never inferred from it.
    origin: GemOrigin = "UNKNOWN"

    #: Treatment claims about this stone. An EMPTY list means "no treatment is
    #: recorded" — which is NOT the same as "this stone is untreated". To assert
    #: the latter, record a treatment with `status: NOT_PRESENT`.
    treatments: list[GemTreatment] = Field(default_factory=list)

    #: Overrides the registry entry's default profile. Present so a user can
    #: change appearance without changing identity — a pale sapphire is still a
    #: sapphire (brief section 13).
    visualProfileId: str | None = Field(
        default=None, pattern=GEM_ID_PATTERN, max_length=MAX_GEM_ID_LENGTH
    )

    #: Free-text name for a `custom` gem. Meaningless for any other `gemId`,
    #: and validated as such: a custom gem with no name, or a named non-custom
    #: gem, are both rejected rather than silently accepted.
    customName: str | None = Field(default=None, max_length=120)

    note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def _custom_name_matches_custom_gem(self) -> GemIdentity:
        """`customName` is meaningful only for the `custom` gem.

        Both directions are rejected rather than silently tolerated. A custom
        gem with no name carries no identity at all, and a named `ruby` invites
        a reader to believe the name means something the system will honour —
        it will not, because resolution goes through `gemId`.
        """

        if self.gemId == CUSTOM_GEM_ID:
            if not (self.customName or "").strip():
                raise ValueError(
                    "a custom gem requires a customName describing the material"
                )
        elif self.customName is not None:
            raise ValueError(
                f"customName is only valid when gemId is {CUSTOM_GEM_ID!r}; "
                f"got gemId={self.gemId!r}"
            )
        return self


class ResolvedGem(GemModel):
    """A `GemIdentity` joined to its registry entry and visual profile.

    What every downstream consumer reads. Produced by
    `jewelmind/gem/resolution.py`, which is the only place the join happens —
    so Forge, Vision, Foundry and the technical specification cannot each
    resolve a gem slightly differently.
    """

    identity: GemIdentity
    definition: GemDefinition
    visualProfile: GemVisualProfile

    #: True when the identity pointed at an entry that no longer exists and was
    #: resolved to `unknown`. Surfaced rather than hidden: a design that
    #: references a removed gem must load, and the reader must be told
    #: (brief sections 10/29).
    wasUnresolved: bool = False

    #: True when the visual profile is the generic fallback rather than a gem's
    #: own appearance.
    usedFallbackVisualProfile: bool = False

    #: The registry version this resolution came from (brief section 28).
    registryVersion: str


class StoneInstance(GemModel):
    """One stone occurrence in a design (brief section 16).

    The contract that makes gem identity addressable PER STONE, so a future
    design can carry a diamond centre with sapphire sides without the whole
    project depending on one global gem.

    Deliberately does NOT include arrangement geometry — position, spacing,
    count. That belongs to a future arrangement milestone, and duplicating it
    here would create a second source of truth for stone placement. This model
    carries only what identifies an occurrence.
    """

    instanceId: str = Field(pattern=GEM_ID_PATTERN, max_length=MAX_GEM_ID_LENGTH)
    role: StoneRole = "CENTER"

    #: The gem identity for THIS occurrence.
    gem: GemIdentity
