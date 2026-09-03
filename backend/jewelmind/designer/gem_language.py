"""Deterministic gem-term recognition for Designer (Sprint 21, brief section 20).

Plain Python, no provider involvement, exactly like `normalizer.py`: a term
either resolves to a real registry entry or it does not, and "does not" is
reported rather than guessed.

THREE DELIBERATE DESIGN POINTS.

1. GEM NAMES COME FROM THE REGISTRY, NOT FROM A SECOND TABLE HERE. Sprint 20
   removed three hand-copied capability lists that had already drifted and made
   Designer misreport real capabilities. `gem_alias_index()` is built from
   `jewelmind.gem.registry`'s own `aliases`/`displayNames`, so a gem added there
   is recognized here in the same change, with no second list to forget.

2. A WORD THAT NAMES BOTH A CUT AND A SPECIES IS AMBIGUOUS, NOT A GEM.
   "smeraldo" is both the emerald CUT (`stone.shape = "emerald"`, an outline
   with clipped corners) and the gem species emerald. "perla" is both the
   `pearl` SHAPE and the gem pearl. Sprint 20's STONEV2-GOV-008 forbids
   resolving a species name to a cut; the mirror obligation is that Designer
   must not silently resolve a cut name to a species either. Those terms are
   reported as ambiguous so the caller asks, which is the same treatment bare
   "gold" already gets in `normalizer.AMBIGUOUS_METAL_TERMS`.

3. "TRATTATO" MEANS A TREATMENT IS CLAIMED, NOT WHICH ONE. "smeraldo trattato"
   resolves to a treatment record of `UNKNOWN`/`PRESENT`/`USER_DECLARED`. That
   is the honest reading: the user asserted a treatment exists and did not say
   what it was. Mapping it to `FRACTURE_FILLING` because emeralds are commonly
   oiled would be inventing a gemological claim the user never made, which the
   brief forbids outright.

NOTHING HERE MAY EVER INFER A GEM FROM GEOMETRY. A round stone is not a
diamond, a red stone is not a ruby, and an 8x6 oval is not a sapphire.
"""

from __future__ import annotations

from functools import lru_cache

from jewelmind.gem.models import (
    CUSTOM_GEM_ID,
    UNKNOWN_GEM_ID,
    GemOrigin,
    GemTreatmentType,
)
from jewelmind.gem.registry import GEM_REGISTRY, alias_lookup, current_gem_ids

#: Terms that name a stone CUT in `normalizer.STONE_SHAPE_SYNONYMS` *and* a gem
#: species in the registry. Recognized, never auto-resolved (point 2 above).
AMBIGUOUS_GEM_TERMS: frozenset[str] = frozenset(
    {
        "emerald",
        "smeraldo",
        "pearl",
        "perla",
    }
)

#: Extra spoken forms the registry's own aliases do not carry, because they are
#: phrasings rather than names. Every value must be a real registry ID —
#: `test_gem_designer_language.py` asserts that.
_EXTRA_GEM_TERMS: dict[str, str] = {
    "lab grown diamond": "diamond",
    "lab-grown diamond": "diamond",
    "diamante sintetico": "diamond",
    "diamante da laboratorio": "diamond",
    "zaffiro blu": "corundum.sapphire",
    "blue sapphire": "corundum.sapphire",
    "pietra sconosciuta": UNKNOWN_GEM_ID,
    "unknown stone": UNKNOWN_GEM_ID,
    "materiale personalizzato": CUSTOM_GEM_ID,
    "custom material": CUSTOM_GEM_ID,
    "altro materiale": CUSTOM_GEM_ID,
}

#: Words naming the ORIGIN / NATURE axis, which is independent of the gem ID:
#: a synthetic ruby is still `corundum.ruby` (brief section 8).
GEM_ORIGIN_SYNONYMS: dict[str, GemOrigin] = {
    "natural": "NATURAL",
    "naturale": "NATURAL",
    "mined": "NATURAL",
    "di miniera": "NATURAL",
    "synthetic": "SYNTHETIC",
    "sintetico": "SYNTHETIC",
    "sintetica": "SYNTHETIC",
    "lab grown": "SYNTHETIC",
    "lab-grown": "SYNTHETIC",
    "laboratory grown": "SYNTHETIC",
    "da laboratorio": "SYNTHETIC",
    "di laboratorio": "SYNTHETIC",
    "coltivato": "SYNTHETIC",
    "coltivata": "SYNTHETIC",
    "cultured": "SYNTHETIC",
    "simulant": "SIMULANT",
    "simulante": "SIMULANT",
    "imitation": "SIMULANT",
    "imitazione": "SIMULANT",
    "composite": "COMPOSITE",
    "composito": "COMPOSITE",
    "doublet": "COMPOSITE",
    "triplet": "COMPOSITE",
}

#: Words naming a TREATMENT. `UNKNOWN` is a real, honest target here: it records
#: that a treatment was declared without naming it (point 3 above).
GEM_TREATMENT_SYNONYMS: dict[str, GemTreatmentType] = {
    "treated": "UNKNOWN",
    "trattato": "UNKNOWN",
    "trattata": "UNKNOWN",
    "heated": "HEAT",
    "riscaldato": "HEAT",
    "riscaldata": "HEAT",
    "heat treated": "HEAT",
    "trattamento termico": "HEAT",
    "irradiated": "IRRADIATION",
    "irradiato": "IRRADIATION",
    "fracture filled": "FRACTURE_FILLING",
    "oiled": "FRACTURE_FILLING",
    "oliato": "FRACTURE_FILLING",
    "glass filled": "GLASS_FILLING",
    "dyed": "DYEING",
    "tinto": "DYEING",
    "coated": "COATING",
    "impregnated": "IMPREGNATION",
    "impregnato": "IMPREGNATION",
    "stabilized": "IMPREGNATION",
    "stabilizzato": "IMPREGNATION",
    "bleached": "BLEACHING",
    "laser drilled": "LASER_DRILLING",
    "hpht": "HPHT",
}

#: Words asserting the ABSENCE of treatment. Kept separate from the table above
#: because "untreated" is not a treatment — it produces a `NOT_PRESENT` record,
#: which is a different state from "nothing recorded" (brief section 9).
GEM_UNTREATED_TERMS: frozenset[str] = frozenset(
    {
        "untreated",
        "non trattato",
        "non trattata",
        "no treatment",
        "nessun trattamento",
        "natural colour",
        "colore naturale",
    }
)


@lru_cache(maxsize=1)
def gem_alias_index() -> dict[str, str]:
    """Lowercased term -> canonical gem ID, derived from the live registry.

    Ambiguous cut/species terms are EXCLUDED, so a lookup here can never
    silently resolve one.
    """

    index: dict[str, str] = dict(alias_lookup())
    for gem_id, entry in GEM_REGISTRY.items():
        index.setdefault(gem_id.lower(), gem_id)
        index.setdefault(entry.canonicalName.lower(), gem_id)
        for name in entry.displayNames.values():
            index.setdefault(name.lower(), gem_id)
    index.update(_EXTRA_GEM_TERMS)
    for term in AMBIGUOUS_GEM_TERMS:
        index.pop(term, None)
    return index


def normalize_gem_term(term: str) -> tuple[str | None, bool]:
    """Resolve a spoken gem term.

    Returns ``(gem_id, is_ambiguous)``, mirroring
    `normalizer.normalize_enum_token()`'s contract exactly. `gem_id` is `None`
    when the term is unrecognized; `is_ambiguous` is True for a term that names
    both a cut and a species.
    """

    token = str(term).strip().lower()
    if not token:
        return None, False
    if token in AMBIGUOUS_GEM_TERMS:
        return None, True
    return gem_alias_index().get(token), False


def normalize_origin_term(term: str) -> GemOrigin | None:
    """Resolve a spoken origin term, or `None` if unrecognized."""

    return GEM_ORIGIN_SYNONYMS.get(str(term).strip().lower())


def normalize_treatment_term(term: str) -> tuple[GemTreatmentType | None, bool]:
    """Resolve a spoken treatment term.

    Returns ``(treatment, asserts_absence)``. When `asserts_absence` is True the
    caller should record a `NOT_PRESENT` treatment rather than a present one —
    "untreated" is a claim, and it is not the same claim as silence.
    """

    token = str(term).strip().lower()
    if token in GEM_UNTREATED_TERMS:
        return None, True
    return GEM_TREATMENT_SYNONYMS.get(token), False


def ambiguity_reason(term: str) -> str:
    """Why a cut/species term cannot be resolved without asking."""

    token = str(term).strip().lower()
    return (
        f"{token!r} names both a stone cut and a gem material in JewelMind. "
        "Specify whether you mean the cut (stone.shape) or the gem "
        "(stone.gem.gemId)."
    )


def unresolved_gem_reason(term: str) -> str:
    """Why an unrecognized gem term is not silently approximated.

    Offers the two real escape hatches instead of the nearest-looking entry —
    the same discipline `resolve_gem()` follows at the domain layer.
    """

    return (
        f"{str(term).strip()!r} does not match any gem JewelMind currently "
        f"knows ({len(current_gem_ids())} entries). It can be recorded as "
        f"{CUSTOM_GEM_ID!r} with the material named explicitly, or left as "
        f"{UNKNOWN_GEM_ID!r}."
    )
