"""The canonical gem registry (brief sections 11/12/29/30).

THE SINGLE SOURCE OF TRUTH for gem identity. `specs/gem/v1/gem-registry.json`
is generated from this module, never hand-maintained as a second copy — the
lesson Sprint 20 learned three times over, when hand-copied capability lists in
Setting and Designer had each drifted into misreporting a real capability.

WHAT THIS REGISTRY IS: an extensible foundation for identifying and rendering
gems. Every entry's `provenance` is `INTERNAL_TAXONOMY` — JewelMind's own
organizing choice, informed by ordinary mineralogical grouping but not cited
from a source and not professionally reviewed.

WHAT THIS REGISTRY IS NOT: a gemological database, a certification source, or
a completeness claim. Having many entries does not make it authoritative
(brief section 41). No entry carries hardness, durability, heat sensitivity, a
setting recommendation, or a treatment safety rule, because every one of those
would require evidence this project does not have (GEM-GOV-006).

ENTRIES ARE NEVER DELETED (brief section 29). A saved project may reference any
ID that has ever existed, so an obsolete entry becomes `DEPRECATED` — still
resolvable, with `supersededBy` pointing at its replacement.
"""

from __future__ import annotations

from jewelmind.gem.models import (
    CUSTOM_GEM_ID,
    FALLBACK_VISUAL_PROFILE_ID,
    UNKNOWN_GEM_ID,
    GemDefinition,
    GemOrigin,
)

#: Version of this registry's CONTENT. Bumped whenever an entry is added,
#: changed or deprecated, so a generated artifact can identify which registry
#: produced it (brief section 28).
GEM_REGISTRY_VERSION = "1.0.0"

_NATURAL: list[GemOrigin] = ["NATURAL"]
_NATURAL_OR_SYNTHETIC: list[GemOrigin] = ["NATURAL", "SYNTHETIC"]
_ANY_ORIGIN: list[GemOrigin] = [
    "NATURAL", "SYNTHETIC", "SIMULANT", "COMPOSITE", "UNKNOWN",
]


def _gem(**kwargs) -> GemDefinition:
    return GemDefinition(**kwargs)


_ENTRIES: list[GemDefinition] = [
    # =====================================================================
    # Escape hatches. Listed FIRST because they are what make the registry
    # extensible rather than limiting (brief section 10).
    # =====================================================================
    _gem(
        gemId=UNKNOWN_GEM_ID,
        canonicalName="Unknown gem",
        displayNames={"en": "Unknown gem", "it": "Gemma non specificata"},
        materialClass="UNKNOWN",
        applicableOrigins=["UNKNOWN"],
        defaultVisualProfileId=FALLBACK_VISUAL_PROFILE_ID,
        status="UNKNOWN",
        provenance="UNKNOWN",
        description=(
            "No gem identity has been specified. This is the state a legacy "
            "design normalizes to, and it is deliberately NOT diamond: the MVP "
            "having used a diamond-like stone is not evidence about any "
            "particular design's intent."
        ),
    ),
    _gem(
        gemId=CUSTOM_GEM_ID,
        canonicalName="Custom material",
        displayNames={"en": "Custom material", "it": "Materiale personalizzato"},
        materialClass="UNKNOWN",
        applicableOrigins=_ANY_ORIGIN,
        defaultVisualProfileId=FALLBACK_VISUAL_PROFILE_ID,
        status="CUSTOM",
        provenance="USER_AUTHORED",
        description=(
            "A user-described material with no registry entry. Requires a "
            "customName on the identity, so a custom gem always carries the "
            "user's own description rather than an empty label."
        ),
    ),
    # =====================================================================
    # Diamond. No meaningful family/variety split — species only.
    # =====================================================================
    _gem(
        gemId="diamond",
        canonicalName="Diamond",
        displayNames={"en": "Diamond", "it": "Diamante"},
        materialClass="MINERAL",
        species="diamond",
        applicableOrigins=_NATURAL_OR_SYNTHETIC,
        aliases=["diamante", "brilliant", "brillante"],
        defaultVisualProfileId="colourless.brilliant",
        description=(
            "Carbon mineral. Natural and laboratory-grown diamond share this "
            "identity and are distinguished by GemIdentity.origin, not by "
            "separate registry entries — a lab-grown diamond IS diamond."
        ),
    ),
    # =====================================================================
    # Corundum family
    # =====================================================================
    _gem(
        gemId="corundum",
        canonicalName="Corundum",
        displayNames={"en": "Corundum", "it": "Corindone"},
        materialClass="MINERAL",
        family="corundum",
        species="corundum",
        applicableOrigins=_NATURAL_OR_SYNTHETIC,
        aliases=["corindone"],
        defaultVisualProfileId="colourless.moderate",
        description=(
            "The corundum species itself, for a stone identified no further "
            "than its species. Ruby and sapphire are varieties of it."
        ),
    ),
    _gem(
        gemId="corundum.ruby",
        canonicalName="Ruby",
        displayNames={"en": "Ruby", "it": "Rubino"},
        materialClass="MINERAL",
        family="corundum", species="corundum", variety="ruby",
        applicableOrigins=_NATURAL_OR_SYNTHETIC,
        aliases=["ruby", "rubino", "rubis"],
        defaultVisualProfileId="red.deep",
        description="Red variety of corundum. Natural and synthetic share this identity.",
    ),
    _gem(
        gemId="corundum.sapphire",
        canonicalName="Sapphire",
        displayNames={"en": "Sapphire", "it": "Zaffiro"},
        materialClass="MINERAL",
        family="corundum", species="corundum", variety="sapphire",
        applicableOrigins=_NATURAL_OR_SYNTHETIC,
        aliases=["sapphire", "zaffiro", "saphir"],
        defaultVisualProfileId="blue.deep",
        description=(
            "Non-red variety of corundum. Blue is the default appearance; other "
            "sapphire colours are expressed with a visualProfileId override, "
            "since colour is appearance rather than identity."
        ),
    ),
    # =====================================================================
    # Beryl family
    # =====================================================================
    _gem(
        gemId="beryl",
        canonicalName="Beryl",
        displayNames={"en": "Beryl", "it": "Berillo"},
        materialClass="MINERAL",
        family="beryl", species="beryl",
        applicableOrigins=_NATURAL_OR_SYNTHETIC,
        aliases=["berillo"],
        defaultVisualProfileId="colourless.moderate",
        description="The beryl species itself, for a stone identified no further.",
    ),
    _gem(
        gemId="beryl.emerald",
        canonicalName="Emerald",
        displayNames={"en": "Emerald", "it": "Smeraldo"},
        materialClass="MINERAL",
        family="beryl", species="beryl", variety="emerald",
        applicableOrigins=_NATURAL_OR_SYNTHETIC,
        aliases=["emerald", "smeraldo", "emeraude"],
        defaultVisualProfileId="green.deep",
        description=(
            "Green variety of beryl. NOTE the distinction this whole sprint "
            "exists for: this is the GEM SPECIES emerald, entirely separate "
            "from stone.shape = 'emerald', which is a clipped-corner outline."
        ),
    ),
    _gem(
        gemId="beryl.aquamarine",
        canonicalName="Aquamarine",
        displayNames={"en": "Aquamarine", "it": "Acquamarina"},
        materialClass="MINERAL",
        family="beryl", species="beryl", variety="aquamarine",
        applicableOrigins=_NATURAL_OR_SYNTHETIC,
        aliases=["aquamarine", "acquamarina", "aquamarina"],
        defaultVisualProfileId="blue.pale",
        description="Blue to blue-green variety of beryl.",
    ),
    _gem(
        gemId="beryl.morganite",
        canonicalName="Morganite",
        displayNames={"en": "Morganite", "it": "Morganite"},
        materialClass="MINERAL",
        family="beryl", species="beryl", variety="morganite",
        applicableOrigins=_NATURAL,
        aliases=["morganite"],
        defaultVisualProfileId="pink.medium",
        description="Pink to peach variety of beryl.",
    ),
    # =====================================================================
    # Quartz family
    # =====================================================================
    _gem(
        gemId="quartz",
        canonicalName="Quartz",
        displayNames={"en": "Quartz", "it": "Quarzo"},
        materialClass="MINERAL",
        family="quartz", species="quartz",
        applicableOrigins=_NATURAL_OR_SYNTHETIC,
        aliases=["quarzo", "rock crystal", "cristallo di rocca"],
        defaultVisualProfileId="colourless.moderate",
        description="The quartz species itself, for a stone identified no further.",
    ),
    _gem(
        gemId="quartz.amethyst",
        canonicalName="Amethyst",
        displayNames={"en": "Amethyst", "it": "Ametista"},
        materialClass="MINERAL",
        family="quartz", species="quartz", variety="amethyst",
        applicableOrigins=_NATURAL_OR_SYNTHETIC,
        aliases=["amethyst", "ametista"],
        defaultVisualProfileId="violet.medium",
        description="Violet variety of quartz.",
    ),
    _gem(
        gemId="quartz.citrine",
        canonicalName="Citrine",
        displayNames={"en": "Citrine", "it": "Citrino"},
        materialClass="MINERAL",
        family="quartz", species="quartz", variety="citrine",
        applicableOrigins=_NATURAL_OR_SYNTHETIC,
        aliases=["citrine", "citrino"],
        defaultVisualProfileId="yellow.warm",
        description="Yellow to orange variety of quartz.",
    ),
    _gem(
        gemId="quartz.rose",
        canonicalName="Rose quartz",
        displayNames={"en": "Rose quartz", "it": "Quarzo rosa"},
        materialClass="MINERAL",
        family="quartz", species="quartz", variety="rose_quartz",
        applicableOrigins=_NATURAL,
        aliases=["rose quartz", "quarzo rosa"],
        defaultVisualProfileId="pink.medium",
        description="Pink variety of quartz.",
    ),
    # =====================================================================
    # Species with no widely-used variety split in this registry
    # =====================================================================
    _gem(
        gemId="spinel",
        canonicalName="Spinel",
        displayNames={"en": "Spinel", "it": "Spinello"},
        materialClass="MINERAL",
        species="spinel",
        applicableOrigins=_NATURAL_OR_SYNTHETIC,
        aliases=["spinello"],
        defaultVisualProfileId="red.deep",
        description=(
            "Spinel. Recorded at species level: its colour varieties are not "
            "given separate entries, because a reliable variety taxonomy for "
            "them is not something this registry can assert."
        ),
    ),
    _gem(
        gemId="topaz",
        canonicalName="Topaz",
        displayNames={"en": "Topaz", "it": "Topazio"},
        materialClass="MINERAL",
        species="topaz",
        applicableOrigins=_NATURAL,
        aliases=["topazio"],
        defaultVisualProfileId="brown.warm",
        description="Topaz, recorded at species level.",
    ),
    _gem(
        gemId="zircon",
        canonicalName="Zircon",
        displayNames={"en": "Zircon", "it": "Zircone"},
        materialClass="MINERAL",
        species="zircon",
        applicableOrigins=_NATURAL,
        aliases=["zircone"],
        defaultVisualProfileId="brown.warm",
        description=(
            "Zircon, a natural mineral. NOT to be confused with cubic "
            "zirconia, which is a separate synthetic simulant entry — the two "
            "are different materials with confusingly similar names."
        ),
    ),
    _gem(
        gemId="peridot",
        canonicalName="Peridot",
        displayNames={"en": "Peridot", "it": "Peridoto"},
        materialClass="MINERAL",
        species="forsterite_olivine", variety="peridot",
        applicableOrigins=_NATURAL,
        aliases=["peridoto", "olivine", "olivina"],
        defaultVisualProfileId="green.light",
        description="Gem-quality variety of the olivine mineral series.",
    ),
    _gem(
        gemId="opal",
        canonicalName="Opal",
        displayNames={"en": "Opal", "it": "Opale"},
        materialClass="MINERAL",
        species="opal",
        applicableOrigins=_NATURAL_OR_SYNTHETIC,
        aliases=["opale"],
        defaultVisualProfileId="iridescent.opal",
        description=(
            "Opal. Its play-of-colour is not simulated; the visual profile "
            "records that its appearance is a known approximation."
        ),
    ),
    _gem(
        gemId="moonstone",
        canonicalName="Moonstone",
        displayNames={"en": "Moonstone", "it": "Pietra di luna"},
        materialClass="MINERAL",
        family="feldspar", species="orthoclase", variety="moonstone",
        applicableOrigins=_NATURAL,
        aliases=["moonstone", "pietra di luna", "adularia"],
        defaultVisualProfileId="translucent.moonstone",
        description=(
            "Adularescent variety within the feldspar group. Adularescence is "
            "not simulated."
        ),
    ),
    _gem(
        gemId="turquoise",
        canonicalName="Turquoise",
        displayNames={"en": "Turquoise", "it": "Turchese"},
        materialClass="MINERAL",
        species="turquoise",
        applicableOrigins=["NATURAL", "SYNTHETIC", "COMPOSITE"],
        aliases=["turchese"],
        defaultVisualProfileId="opaque.turquoise",
        description=(
            "Opaque phosphate mineral. Frequently stabilized or reconstituted, "
            "which is why COMPOSITE is an applicable origin here."
        ),
    ),
    # =====================================================================
    # Groups where the variety level is the useful one
    # =====================================================================
    _gem(
        gemId="garnet",
        canonicalName="Garnet",
        displayNames={"en": "Garnet", "it": "Granato"},
        materialClass="MINERAL",
        family="garnet",
        applicableOrigins=_NATURAL,
        aliases=["granato"],
        defaultVisualProfileId="red.deep",
        description=(
            "The garnet group. Recorded with a family but NO species, which is "
            "the honest representation: garnet is a mineral group of several "
            "species rather than a single one."
        ),
    ),
    _gem(
        gemId="garnet.almandine",
        canonicalName="Almandine garnet",
        displayNames={"en": "Almandine garnet", "it": "Granato almandino"},
        materialClass="MINERAL",
        family="garnet", species="almandine",
        applicableOrigins=_NATURAL,
        aliases=["almandine", "almandino"],
        defaultVisualProfileId="red.deep",
        description="Iron-aluminium species within the garnet group.",
    ),
    _gem(
        gemId="garnet.spessartine",
        canonicalName="Spessartine garnet",
        displayNames={"en": "Spessartine garnet", "it": "Granato spessartite"},
        materialClass="MINERAL",
        family="garnet", species="spessartine",
        applicableOrigins=_NATURAL,
        aliases=["spessartine", "spessartite"],
        defaultVisualProfileId="orange.warm",
        description="Manganese-aluminium species within the garnet group.",
    ),
    _gem(
        gemId="garnet.tsavorite",
        canonicalName="Tsavorite garnet",
        displayNames={"en": "Tsavorite garnet", "it": "Granato tsavorite"},
        materialClass="MINERAL",
        family="garnet", species="grossular", variety="tsavorite",
        applicableOrigins=_NATURAL,
        aliases=["tsavorite", "tsavorite garnet"],
        defaultVisualProfileId="green.deep",
        description="Green variety of grossular garnet.",
    ),
    _gem(
        gemId="tourmaline",
        canonicalName="Tourmaline",
        displayNames={"en": "Tourmaline", "it": "Tormalina"},
        materialClass="MINERAL",
        family="tourmaline",
        applicableOrigins=_NATURAL,
        aliases=["tormalina"],
        defaultVisualProfileId="pink.medium",
        description=(
            "The tourmaline group. Family only, for the same reason as garnet: "
            "it is a group rather than a single species."
        ),
    ),
    _gem(
        gemId="tourmaline.rubellite",
        canonicalName="Rubellite tourmaline",
        displayNames={"en": "Rubellite tourmaline", "it": "Tormalina rubellite"},
        materialClass="MINERAL",
        family="tourmaline", species="elbaite", variety="rubellite",
        applicableOrigins=_NATURAL,
        aliases=["rubellite"],
        defaultVisualProfileId="pink.medium",
        description="Pink to red variety of elbaite tourmaline.",
    ),
    _gem(
        gemId="tourmaline.verdelite",
        canonicalName="Green tourmaline",
        displayNames={"en": "Green tourmaline", "it": "Tormalina verde"},
        materialClass="MINERAL",
        family="tourmaline", species="elbaite", variety="verdelite",
        applicableOrigins=_NATURAL,
        aliases=["verdelite", "green tourmaline"],
        defaultVisualProfileId="green.deep",
        description="Green variety of elbaite tourmaline.",
    ),
    _gem(
        gemId="jade.jadeite",
        canonicalName="Jadeite jade",
        displayNames={"en": "Jadeite jade", "it": "Giada giadeite"},
        materialClass="MINERAL",
        family="jade", species="jadeite",
        applicableOrigins=["NATURAL", "COMPOSITE"],
        aliases=["jadeite", "giadeite", "jade", "giada"],
        defaultVisualProfileId="translucent.green",
        description=(
            "Jadeite, one of the two distinct minerals sold as jade. Given its "
            "own entry rather than a generic 'jade' precisely because jadeite "
            "and nephrite are different minerals."
        ),
    ),
    _gem(
        gemId="jade.nephrite",
        canonicalName="Nephrite jade",
        displayNames={"en": "Nephrite jade", "it": "Giada nefrite"},
        materialClass="MINERAL",
        family="jade", species="nephrite",
        applicableOrigins=["NATURAL", "COMPOSITE"],
        aliases=["nephrite", "nefrite"],
        defaultVisualProfileId="translucent.green",
        description="Nephrite, the other mineral sold as jade.",
    ),
    # =====================================================================
    # ORGANIC materials. No family/species/variety — forcing mineralogical
    # fields onto these would be inventing facts (brief section 8).
    # =====================================================================
    _gem(
        gemId="pearl",
        canonicalName="Pearl",
        displayNames={"en": "Pearl", "it": "Perla"},
        materialClass="ORGANIC",
        applicableOrigins=["NATURAL", "SYNTHETIC", "SIMULANT"],
        aliases=["pearl", "perla"],
        defaultVisualProfileId="pearlescent.white",
        description=(
            "Organic gem material formed within a mollusc. No mineral species "
            "or variety applies. `SYNTHETIC` here covers cultured pearls and "
            "`SIMULANT` covers imitation pearls — genuinely different things "
            "that a single boolean could not distinguish."
        ),
    ),
    _gem(
        gemId="amber",
        canonicalName="Amber",
        displayNames={"en": "Amber", "it": "Ambra"},
        materialClass="ORGANIC",
        applicableOrigins=["NATURAL", "COMPOSITE", "SIMULANT"],
        aliases=["amber", "ambra"],
        defaultVisualProfileId="translucent.warm",
        description=(
            "Fossilized tree resin. `COMPOSITE` covers pressed or reconstituted "
            "amber, which is real amber that has been reformed."
        ),
    ),
    _gem(
        gemId="coral",
        canonicalName="Coral",
        displayNames={"en": "Coral", "it": "Corallo"},
        materialClass="ORGANIC",
        applicableOrigins=["NATURAL", "SIMULANT"],
        aliases=["coral", "corallo"],
        defaultVisualProfileId="opaque.coral",
        description="Organic material formed by marine coral polyps.",
    ),
    _gem(
        gemId="shell.mother_of_pearl",
        canonicalName="Mother of pearl",
        displayNames={"en": "Mother of pearl", "it": "Madreperla"},
        materialClass="ORGANIC",
        applicableOrigins=["NATURAL"],
        aliases=["mother of pearl", "madreperla", "nacre", "nacre shell"],
        defaultVisualProfileId="pearlescent.white",
        description="Nacreous shell lining used as a gem material.",
    ),
    _gem(
        gemId="jet",
        canonicalName="Jet",
        displayNames={"en": "Jet", "it": "Giaietto"},
        materialClass="ORGANIC",
        applicableOrigins=["NATURAL"],
        aliases=["jet", "giaietto"],
        defaultVisualProfileId="opaque.coral",
        description=(
            "Fossilized wood used as an opaque black gem material. Its visual "
            "profile is a placeholder shared with coral and is a recorded "
            "limitation, not a claim that jet looks like coral."
        ),
    ),
    # =====================================================================
    # SIMULANTS. A simulant NEVER identifies as the material it imitates
    # (brief section 9).
    # =====================================================================
    _gem(
        gemId="simulant.cubic_zirconia",
        canonicalName="Cubic zirconia",
        displayNames={"en": "Cubic zirconia", "it": "Zirconia cubica"},
        materialClass="MINERAL",
        species="cubic_zirconia",
        applicableOrigins=["SIMULANT"],
        aliases=["cubic zirconia", "zirconia cubica", "cz", "zirconia"],
        defaultVisualProfileId="colourless.brilliant",
        description=(
            "Synthetic cubic zirconium dioxide, most often used as a diamond "
            "simulant. It is NOT diamond and must never resolve to diamond, "
            "however diamond-like the intended appearance. Sharing a visual "
            "profile with diamond is a rendering choice, not an identity claim."
        ),
    ),
    _gem(
        gemId="simulant.moissanite",
        canonicalName="Moissanite",
        displayNames={"en": "Moissanite", "it": "Moissanite"},
        materialClass="MINERAL",
        species="silicon_carbide",
        applicableOrigins=["SIMULANT", "SYNTHETIC"],
        aliases=["moissanite"],
        defaultVisualProfileId="colourless.brilliant",
        description=(
            "Silicon carbide, essentially always laboratory-grown and commonly "
            "used as a diamond simulant. A distinct material with its own "
            "identity."
        ),
    ),
    _gem(
        gemId="simulant.glass",
        canonicalName="Glass",
        displayNames={"en": "Glass", "it": "Vetro"},
        materialClass="NON_MINERAL",
        applicableOrigins=["SIMULANT"],
        aliases=["glass", "vetro", "paste", "strass"],
        defaultVisualProfileId="colourless.moderate",
        description=(
            "Glass used as a gem simulant. `NON_MINERAL` because glass is "
            "amorphous and has no mineral species — a case where the "
            "mineralogical fields correctly stay empty."
        ),
    ),
    # =====================================================================
    # COMPOSITES
    # =====================================================================
    _gem(
        gemId="composite.doublet",
        canonicalName="Composite doublet",
        displayNames={"en": "Composite doublet", "it": "Doppietta composita"},
        materialClass="COMPOSITE",
        applicableOrigins=["COMPOSITE"],
        aliases=["doublet", "doppietta"],
        defaultVisualProfileId=FALLBACK_VISUAL_PROFILE_ID,
        description=(
            "A stone assembled from two bonded layers of different materials. "
            "Uses the generic profile because its appearance depends entirely "
            "on which materials were combined, which the registry cannot know."
        ),
    ),
    _gem(
        gemId="composite.triplet",
        canonicalName="Composite triplet",
        displayNames={"en": "Composite triplet", "it": "Tripletta composita"},
        materialClass="COMPOSITE",
        applicableOrigins=["COMPOSITE"],
        aliases=["triplet", "tripletta"],
        defaultVisualProfileId=FALLBACK_VISUAL_PROFILE_ID,
        description="A stone assembled from three bonded layers.",
    ),
]

GEM_REGISTRY: dict[str, GemDefinition] = {entry.gemId: entry for entry in _ENTRIES}


def get_gem(gem_id: str) -> GemDefinition | None:
    """Look an entry up by exact canonical ID. Never falls back."""

    return GEM_REGISTRY.get(gem_id)


def all_gem_ids() -> list[str]:
    return list(GEM_REGISTRY)


def current_gem_ids() -> list[str]:
    """Entries a user should be offered — excludes DEPRECATED ones.

    `custom` and `unknown` ARE included: both are legitimate things to choose.
    """

    return [
        gem_id for gem_id, entry in GEM_REGISTRY.items()
        if entry.status != "DEPRECATED"
    ]


def alias_lookup() -> dict[str, str]:
    """Every alias and canonical ID mapped to its canonical gem ID.

    An alias is never a separate identity (brief section 30). Two aliases must
    never resolve to two different IDs, and the registry tests assert exactly
    that — a duplicate alias is a hard failure, not a last-one-wins.

    Keys are lowercased, and the canonical ID plus the canonical name both map
    to themselves, so a caller can hand this table anything reasonable.
    """

    table: dict[str, str] = {}
    for gem_id, entry in GEM_REGISTRY.items():
        table[gem_id.lower()] = gem_id
        table[entry.canonicalName.lower()] = gem_id
        for alias in entry.aliases:
            table[alias.lower()] = gem_id
        for name in entry.displayNames.values():
            table[name.lower()] = gem_id
    return table


def registry_families() -> dict[str, list[str]]:
    """Gem IDs grouped by family, for entries that declare one.

    Entries with no family are absent rather than grouped under a placeholder:
    diamond has no family, and inventing one would be inventing taxonomy
    (GEM-GOV-004).
    """

    families: dict[str, list[str]] = {}
    for gem_id, entry in GEM_REGISTRY.items():
        if entry.family is None:
            continue
        families.setdefault(entry.family, []).append(gem_id)
    return families
