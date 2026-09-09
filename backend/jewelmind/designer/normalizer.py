"""Deterministic language normalization, diffing, and input screening.

None of this depends on an AI provider — it is plain, testable Python, run
against whatever a provider (real or fake) returns, or directly against
the request text for security screening. See
docs/bible/12-designer/297-supported-language-scope.md and
313-designer-security-model.md.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from jewelmind.designer import gem_language
from jewelmind.designer.schemas import FieldDiff
from jewelmind.domain.schema import JewelryDefinition
from jewelmind.stone.capability import native_shapes as _native_shapes

# Only mappings for values that actually exist in the current schema are
# implemented here — see 298-defaulting-policy.md: Designer may normalize a
# spoken synonym to a real enum value, but must never invent a mapping for
# a concept the schema doesn't define (e.g. "delicate" -> a thickness).
METAL_SYNONYMS: dict[str, str] = {
    "yellow_gold_18k": "yellow_gold_18k",
    "yellow gold": "yellow_gold_18k",
    "yellow gold 18k": "yellow_gold_18k",
    "oro giallo": "yellow_gold_18k",
    "giallo": "yellow_gold_18k",
    "white_gold_18k": "white_gold_18k",
    "white gold": "white_gold_18k",
    "white gold 18k": "white_gold_18k",
    "oro bianco": "white_gold_18k",
    "bianco": "white_gold_18k",
    "rose_gold_18k": "rose_gold_18k",
    "rose gold": "rose_gold_18k",
    "rose gold 18k": "rose_gold_18k",
    "pink gold": "rose_gold_18k",
    "oro rosa": "rose_gold_18k",
    "rosa": "rose_gold_18k",
    "platinum": "platinum",
    "platino": "platinum",
    "silver": "silver",
    "argento": "silver",
}

# Present in the table with a None target: the word alone is a real,
# recognized metal reference but does not map to exactly one supported
# metal, so it must trigger clarification rather than a silent guess.
AMBIGUOUS_METAL_TERMS: frozenset[str] = frozenset({"gold", "oro"})

BAND_PROFILE_SYNONYMS: dict[str, str] = {
    "comfort_fit": "comfort_fit",
    "comfort fit": "comfort_fit",
    "comfort": "comfort_fit",
    "comfortevole": "comfort_fit",
    "confort": "comfort_fit",
    "fascia comfort fit": "comfort_fit",
    "flat": "flat",
    "piatta": "flat",
    "fascia piatta": "flat",
}

#: Natural-language names for stone CUTS, in Italian and English
#: (brief section 38). Every value must be a real member of the JDL `StoneShape`
#: enum; `test_designer_corpus.py` asserts that, so a synonym can never point at
#: a shape the system cannot build.
#:
#: `custom` and `imported` are deliberately ABSENT. A user asking for "a custom
#: stone" is describing a SOURCE, not naming a cut, and Designer must route that
#: to a clarification rather than silently producing a stone with no outline
#: behind it (brief section 60).
#: Every shape with a real generator, read from the Stone System registry.
_NATIVE_SHAPES: tuple[str, ...] = tuple(_native_shapes())

STONE_SHAPE_SYNONYMS: dict[str, str] = {
    # --- Stone v1 (Sprint 18) ---
    "round": "round",
    "rotondo": "round",
    "rotonda": "round",
    "tondo": "round",
    "tonda": "round",
    "brillante": "round",
    "round brilliant": "round",
    "oval": "oval",
    "ovale": "oval",
    "pear": "pear",
    "pera": "pear",
    "goccia": "pear",
    "teardrop": "pear",
    "emerald": "emerald",
    "smeraldo": "emerald",
    "taglio smeraldo": "emerald",
    "emerald cut": "emerald",
    "cushion": "cushion",
    "cuscino": "cushion",
    "princess": "princess",
    "principessa": "princess",
    "marquise": "marquise",
    "navette": "marquise",
    # --- Stone v2 (Sprint 20) extended cuts ---
    "heart": "heart",
    "cuore": "heart",
    "a cuore": "heart",
    "heart cut": "heart",
    "radiant": "radiant",
    "radiante": "radiant",
    "radiant cut": "radiant",
    "asscher": "asscher",
    "asscher cut": "asscher",
    # TRILLIANT is an alias, not a second canonical shape: no distinct geometry
    # semantics were defined for it (brief section 11).
    "trillion": "trillion",
    "trilliant": "trillion",
    "trilliante": "trillion",
    "baguette": "baguette",
    "baguette cut": "baguette",
    "tapered baguette": "tapered_baguette",
    "baguette rastremata": "tapered_baguette",
    "baguette conica": "tapered_baguette",
    "triangle": "triangle",
    "triangolo": "triangle",
    "triangolare": "triangle",
    "triangular": "triangle",
    "trapezoid": "trapezoid",
    "trapezio": "trapezoid",
    "trapezium": "trapezoid",
    # LOZENGE, never "diamond": in JewelMind "diamond" is a gem species, and a
    # shape synonym must never resolve a species name to a cut
    # (STONEV2-GOV-008, brief section 37).
    "lozenge": "lozenge",
    "losanga": "lozenge",
    "rombo": "lozenge",
    "rhombus": "lozenge",
    "hexagon": "hexagon",
    "esagono": "hexagon",
    "esagonale": "hexagon",
    "hexagonal": "hexagon",
    "kite": "kite",
    "aquilone": "kite",
    "shield": "shield",
    "scudo": "shield",
    "shield cut": "shield",
    "half moon": "half_moon",
    "halfmoon": "half_moon",
    "mezzaluna": "half_moon",
    "demi lune": "half_moon",
    "pearl": "pearl",
    "perla": "pearl",
    "sfera": "pearl",
    "sphere": "pearl",
}

# Every canonical shape ID must resolve to itself. Two real shapes —
# `tapered_baguette` and `half_moon` — were reported as UNSUPPORTED by Designer
# because the table above lists only their spaced human spellings ("tapered
# baguette", "half moon") and nothing mapped the underscored canonical ID. That
# is exactly the misreport Sprint 18 had to correct for its six new shapes, so
# the identity mapping is derived from the registry rather than typed out.
for _shape in _NATIVE_SHAPES:
    STONE_SHAPE_SYNONYMS.setdefault(_shape, _shape)
    STONE_SHAPE_SYNONYMS.setdefault(_shape.replace("_", " "), _shape)


#: Natural-language names for the 3D REFERENCE PROFILE, which is a separate axis
#: from the cut (brief section 36). "cabochon oval" therefore resolves to
#: `shape=oval` plus `profile=CABOCHON_REFERENCE`, never to a compound
#: `OVAL_CABOCHON` shape.
STONE_PROFILE_SYNONYMS: dict[str, str] = {
    "faceted": "FACETED_REFERENCE",
    "sfaccettata": "FACETED_REFERENCE",
    "sfaccettato": "FACETED_REFERENCE",
    "brilliant": "FACETED_REFERENCE",
    "cabochon": "CABOCHON_REFERENCE",
    "cabochon cut": "CABOCHON_REFERENCE",
    "cabochon reference": "CABOCHON_REFERENCE",
    "liscia": "CABOCHON_REFERENCE",
    "bombata": "CABOCHON_REFERENCE",
    "sphere": "SPHERICAL_REFERENCE",
    "spherical": "SPHERICAL_REFERENCE",
    "sferica": "SPHERICAL_REFERENCE",
}

#: Natural-language names for the stone SOURCE MODE (brief section 60).
#:
#: Recognizing these is what lets Designer respond honestly to "use this exact
#: stone": the phrase names a source, and if no asset or measurement was
#: supplied the correct response is a structured clarification, never a
#: fabricated import (STONEV2-GOV-006).
STONE_SOURCE_SYNONYMS: dict[str, str] = {
    "parametric": "PARAMETRIC_REFERENCE",
    "parametrica": "PARAMETRIC_REFERENCE",
    "custom": "CUSTOM_OUTLINE",
    "custom stone": "CUSTOM_OUTLINE",
    "custom outline": "CUSTOM_OUTLINE",
    "pietra personalizzata": "CUSTOM_OUTLINE",
    "profilo personalizzato": "CUSTOM_OUTLINE",
    "sagoma personalizzata": "CUSTOM_OUTLINE",
    "measured": "MEASURED",
    "measured stone": "MEASURED",
    "pietra misurata": "MEASURED",
    "pietra reale": "MEASURED",
    "misurata": "MEASURED",
    "imported": "IMPORTED_CAD",
    "stone from cad": "IMPORTED_CAD",
    "imported stone": "IMPORTED_CAD",
    "pietra importata": "IMPORTED_CAD",
    "pietra da cad": "IMPORTED_CAD",
    "stone scan": "IMPORTED_CAD",
    "scansione": "IMPORTED_CAD",
    "scan della pietra": "IMPORTED_CAD",
}

SETTING_TYPE_SYNONYMS: dict[str, str] = {
    "prong": "prong",
    "prong setting": "prong",
    "griffe": "prong",
    "griffes": "prong",
    "a griffe": "prong",
    "incastonatura a griffe": "prong",
    "bezel": "bezel",
    "bezel setting": "bezel",
    "castone": "bezel",
    "castone pieno": "bezel",
    "incastonatura a castone": "bezel",
    # Sprint 27: the four new families, each with a real registered generator.
    # A term here reaches a `setting.type` value the backend can build; a
    # reserved technique (trellis, azure, shared-wall channel) is absent from
    # the enum and is reported as an unsupported feature by
    # `capability.py::KNOWN_UNSUPPORTED_CONCEPTS`, which derives its own list
    # from `RESERVED_SETTING_MODES`.
    "channel": "channel",
    "channel setting": "channel",
    "canale": "channel",
    "a canale": "channel",
    "incastonatura a canale": "channel",
    "binario": "channel",
    "bar": "bar",
    "bar setting": "bar",
    "barrette": "bar",
    "a barrette": "bar",
    "incastonatura a barrette": "bar",
    "flush": "flush",
    "flush setting": "flush",
    "gypsy": "flush",
    "gypsy setting": "flush",
    "a filo": "flush",
    "incastonatura a filo": "flush",
    "incassata": "flush",
    "tension": "tension",
    "tension setting": "tension",
    "a tensione": "tension",
    "incastonatura a tensione": "tension",
}

#: Sprint 27. Natural-language names for a setting MODE — the variant within a
#: family, the head architecture, or the field retention.
#:
#: DERIVED FROM THE LIVE REGISTRY rather than restated here, so a term can never
#: name a mode that does not exist and a mode cannot be unreachable by name.
#: `designer_mode_terms()` refuses an ambiguous term at the registry, which is
#: where an ambiguity has to be resolved — not by whichever table was read last.
def setting_mode_synonyms() -> dict[str, str]:
    from jewelmind.setting.capability import designer_mode_terms

    return designer_mode_terms()


#: Sprint 27. Relative descriptions of a setting's SUBSTANCE.
#:
#: Recognized precisely so such a request becomes a QUESTION rather than an
#: invented dimension. "A heavier channel" names a weight, and turning one into
#: a wall thickness in millimetres requires professional judgment this project
#: has no evidence for — the same discipline `PAVE_DENSITY_TERMS` established
#: for "denser".
SETTING_WEIGHT_TERMS: frozenset[str] = frozenset(
    {
        "heavier",
        "lighter",
        "chunkier",
        "daintier",
        "more delicate",
        "sturdier",
        "stronger",
        "thinner walls",
        "thicker walls",
        "piu robusto",
        "più robusto",
        "piu leggero",
        "più leggero",
        "piu delicato",
        "più delicato",
        "piu massiccio",
        "più massiccio",
    }
)


def is_setting_weight_term(token: str) -> bool:
    """Whether a token names a setting's substance rather than a dimension."""

    return token.strip().lower() in SETTING_WEIGHT_TERMS

MANUFACTURING_SYNONYMS: dict[str, str] = {
    "lost_wax_casting": "lost_wax_casting",
    "lost wax casting": "lost_wax_casting",
    "casting": "lost_wax_casting",
    "fusione a cera persa": "lost_wax_casting",
    "direct_resin_printing": "direct_resin_printing",
    "direct resin printing": "direct_resin_printing",
    "resin printing": "direct_resin_printing",
    "stampa in resina": "direct_resin_printing",
}

#: Sprint 26. Natural-language pavé vocabulary, EN and IT, mapping to the
#: live model's own members. Kept beside the other synonym tables rather than
#: in a new module, because it is the same kind of thing they are: a token to
#: a canonical value, with no geometry and no threshold anywhere in it.
PAVE_KIND_SYNONYMS: dict[str, str] = {
    "pave": "PAVE",
    "pavé": "PAVE",
    "pave setting": "PAVE",
    "pavimentazione": "PAVE",
    "microsetting": "MICROSETTING",
    "micro setting": "MICROSETTING",
    "micro-setting": "MICROSETTING",
    "micropave": "MICROSETTING",
    "micro pave": "MICROSETTING",
    "micro pavé": "MICROSETTING",
    "micro-pavé": "MICROSETTING",
    "microincassatura": "MICROSETTING",
}

PAVE_HOST_SYNONYMS: dict[str, str] = {
    "band": "BAND_OUTER",
    "shank": "BAND_OUTER",
    "gambo": "BAND_OUTER",
    "fascia": "BAND_OUTER",
    "band outer": "BAND_OUTER",
    "shoulder": "BAND_OUTER",
    "shoulders": "BAND_OUTER",
    "spalla": "BAND_OUTER",
    "spalle": "BAND_OUTER",
    "head": "HEAD_PLANE",
    "gallery": "HEAD_PLANE",
    "galleria": "HEAD_PLANE",
    "testa": "HEAD_PLANE",
    "head plane": "HEAD_PLANE",
}

PAVE_PATTERN_SYNONYMS: dict[str, str] = {
    "grid": "GRID",
    "griglia": "GRID",
    "aligned": "GRID",
    "allineato": "GRID",
    "staggered": "STAGGERED",
    "sfalsato": "STAGGERED",
    "offset": "ROW_OFFSET",
    "row offset": "ROW_OFFSET",
    "diagonal": "ROW_OFFSET",
    "diagonale": "ROW_OFFSET",
    "radial": "RADIAL",
    "radiale": "RADIAL",
    "explicit": "EXPLICIT",
    "esplicito": "EXPLICIT",
}

PAVE_RETENTION_SYNONYMS: dict[str, str] = {
    "none": "NONE",
    "nessuna": "NONE",
    "bead": "BEAD",
    "beads": "BEAD",
    "grano": "BEAD",
    "grani": "BEAD",
    "shared bead": "SHARED_BEAD",
    "shared beads": "SHARED_BEAD",
    "grani condivisi": "SHARED_BEAD",
    "micro prong": "MICRO_PRONG",
    "micro prongs": "MICRO_PRONG",
    "microgriffe": "MICRO_PRONG",
    "micro griffe": "MICRO_PRONG",
    # Sprint 27.
    "shared prong": "SHARED_PRONG",
    "shared prongs": "SHARED_PRONG",
    "shared micro prong": "SHARED_PRONG",
    "shared micro prongs": "SHARED_PRONG",
    "micro griffe condivise": "SHARED_PRONG",
    "griffe condivise": "SHARED_PRONG",
}

PAVE_SEAT_SYNONYMS: dict[str, str] = {
    "none": "NONE",
    "nessuno": "NONE",
    "recess": "REFERENCE_RECESS",
    "recessed": "REFERENCE_RECESS",
    "incasso": "REFERENCE_RECESS",
    "reference recess": "REFERENCE_RECESS",
}

PAVE_CONTAINMENT_SYNONYMS: dict[str, str] = {
    "clip": "CLIP",
    "taglia": "CLIP",
    "reject": "REJECT",
    "rifiuta": "REJECT",
}

#: Terms that name a pavé DENSITY rather than a value.
#:
#: DELIBERATELY NOT MAPPED TO A NUMBER. "Denser" is a relative instruction, and
#: turning it into a pitch would require knowing what pitch is appropriate —
#: which is exactly the professional judgment this project has no evidence for.
#: Recognized so a request can be understood and clarified, never resolved to a
#: millimetre value on the user's behalf.
PAVE_DENSITY_TERMS: frozenset[str] = frozenset(
    {
        "dense",
        "denser",
        "denso",
        "più fitto",
        "piu fitto",
        "fitto",
        "fitte",
        "tight",
        "tighter",
        "sparse",
        "sparser",
        "rado",
        "spaziato",
        "loose",
    }
)


#: Sprint 27. Whether metal is relieved where the stone sits.
#:
#: A small static table rather than a registry-derived one, because relief is
#: not a setting MODE — it is an orthogonal axis with its own two-member enum,
#: recorded in `setting/capability.py::SEAT_CAPABILITIES`.
SEAT_MODE_SYNONYMS: dict[str, str] = {
    "none": "NONE",
    "nessuno": "NONE",
    "no relief": "NONE",
    "reference_seat": "REFERENCE_SEAT",
    "reference seat": "REFERENCE_SEAT",
    "relief": "REFERENCE_SEAT",
    "relieved": "REFERENCE_SEAT",
    "seat": "REFERENCE_SEAT",
    "sede": "REFERENCE_SEAT",
    "incasso": "REFERENCE_SEAT",
}


@lru_cache(maxsize=1)
def _setting_mode_tables() -> dict[str, dict[str, str]]:
    """Synonym tables for the setting-mode axes, DERIVED from the registry.

    Three tables, one per axis, and the split is what keeps each axis a single
    authority: a head term must not resolve into `setting.mode.modeId`, which
    declares the PRIMARY mode, and a primary term must not resolve into
    `setting.headArchitecture`.

    Built lazily and cached because the registry's own `settingGeometry` axis is
    measured from the live builder registries, which import this package's
    siblings — the discipline `setting/capability.py::setting_modes()` documents
    for the same reason.
    """

    from jewelmind.setting.capability import setting_modes
    from jewelmind.setting.modes import (
        head_architecture_for_mode,
        mode_axis,
        prong_style_for_mode,
    )

    primary: dict[str, str] = {}
    heads: dict[str, str] = {}
    prongs: dict[str, str] = {}

    for mode_id, entry in setting_modes().items():
        axis = mode_axis(mode_id)
        if axis == "PRIMARY":
            primary[mode_id.lower()] = mode_id
            for term in entry.designerTerms:
                primary.setdefault(term.lower(), mode_id)
            # A prong mode also names a BODY STYLE, which is a separate field.
            # `PRONG_SHARED` is excluded: it maps to the round body, so a style
            # alone can never imply sharing.
            style = prong_style_for_mode(mode_id)
            if style is not None and mode_id != "PRONG_SHARED":
                prongs[style.lower()] = style
                for term in entry.designerTerms:
                    prongs.setdefault(term.lower(), style)
        elif axis == "HEAD":
            architecture = head_architecture_for_mode(mode_id)
            if architecture is None:  # pragma: no cover - registry guarantees one
                continue
            heads[architecture.lower()] = architecture
            heads[mode_id.lower()] = architecture
            for term in entry.designerTerms:
                heads.setdefault(term.lower(), architecture)

    return {
        "setting.mode.modeId": primary,
        "setting.headArchitecture": heads,
        "setting.prongStyle": prongs,
    }


@lru_cache(maxsize=1)
def _ring_family_tables() -> dict[str, dict[str, str]]:
    """Synonym tables for the two ring-family axes, DERIVED from the registry.

    TWO TABLES, and the split keeps each axis a single authority — the same
    reason `_setting_mode_tables()` splits three ways. `jewelry.style` declares
    the FAMILY; `ringFamily.variant` declares which variant of it. A term
    resolves in both, to different values, because both statements are true of
    it: "cathedral" names the solitaire family AND the cathedral variant, so a
    request naming it produces a coherent pair rather than a family with a
    variant from somewhere else.

    Built lazily and cached because the registry MEASURES its rows by running
    the real resolver, which imports this package's siblings.
    """

    from jewelmind.ring_family.capability import designer_family_terms
    from jewelmind.ring_family.models import family_for_variant, implemented_families

    styles: dict[str, str] = {family: family for family in implemented_families()}
    variants: dict[str, str] = {}

    for term, variant in designer_family_terms().items():
        variants.setdefault(term, variant)
        # A family name already maps to itself and must not be displaced: a
        # request for "a halo" names the family, and the DEFAULT variant is what
        # an undeclared `ringFamily` already resolves to.
        styles.setdefault(term, family_for_variant(variant))

    for variant in designer_family_terms().values():
        variants.setdefault(variant.lower(), variant)
        # The spaced form of the id, because a request writes words.
        variants.setdefault(variant.lower().replace("_", " "), variant)

    return {"jewelry.style": styles, "ringFamily.variant": variants}


_ENUM_SYNONYM_TABLES: dict[str, dict[str, str]] = {
    "material.metal": METAL_SYNONYMS,
    "band.profile": BAND_PROFILE_SYNONYMS,
    "stone.shape": STONE_SHAPE_SYNONYMS,
    "setting.type": SETTING_TYPE_SYNONYMS,
    "manufacturing.method": MANUFACTURING_SYNONYMS,
    # Sprint 26.
    "pave.kind": PAVE_KIND_SYNONYMS,
    "pave.host": PAVE_HOST_SYNONYMS,
    "pave.spec.pattern": PAVE_PATTERN_SYNONYMS,
    "pave.retention.strategy": PAVE_RETENTION_SYNONYMS,
    "pave.seat.mode": PAVE_SEAT_SYNONYMS,
    "pave.containment": PAVE_CONTAINMENT_SYNONYMS,
    # Sprint 27.
    "setting.seatMode": SEAT_MODE_SYNONYMS,
}

# Prong count is numeric in the schema, but requests name it in words —
# only the two currently-supported counts are recognized (see
# capability.py::SUPPORTED_PRONG_COUNTS). A number outside this map is
# left to fail capability checking rather than being silently accepted.
PRONG_COUNT_WORDS: dict[str, int] = {
    "4": 4,
    "four": 4,
    "quattro": 4,
    "6": 6,
    "six": 6,
    "sei": 6,
}


def normalize_enum_token(field: str, raw_value: str) -> tuple[str | None, bool]:
    """Normalize a raw token for an enum field.

    Returns ``(canonical_value, is_ambiguous)``. `canonical_value` is
    `None` when the token doesn't map to anything known. `is_ambiguous` is
    True when the token is a recognized-but-incomplete reference (e.g.
    bare "gold") that must trigger clarification rather than a guess.
    """

    token = str(raw_value).strip().lower()

    if field == "material.metal" and token in AMBIGUOUS_METAL_TERMS:
        return None, True

    # Sprint 21. Gem terms live in `gem_language.py` and are derived from the
    # live registry, so this function stays a router rather than gaining a
    # 40-entry copy of the registry that could drift from it.
    if field == "stone.gem.gemId":
        return gem_language.normalize_gem_term(token)
    if field == "stone.gem.origin":
        origin = gem_language.normalize_origin_term(token)
        return origin, False

    if field == "setting.prongCount":
        mapped = PRONG_COUNT_WORDS.get(token)
        return (str(mapped) if mapped is not None else None), False

    # Sprint 27. The setting-mode axes are DERIVED from the live registry, so
    # they are looked up through a cached builder rather than a module-level
    # constant — see `_setting_mode_tables()`.
    derived = _setting_mode_tables().get(field)
    if derived is not None:
        return derived.get(token), False

    # Sprint 28. Derived from the live ring-family registry for the same reason.
    family_table = _ring_family_tables().get(field)
    if family_table is not None:
        return family_table.get(token), False

    table = _ENUM_SYNONYM_TABLES.get(field)
    if table is None:
        return None, False
    return table.get(token), False


_NUMERIC_FIELDS: frozenset[str] = frozenset(
    {
        "ring.size",
        "ring.innerDiameter",
        "band.width",
        "band.thickness",
        "stone.diameter",
        "stone.length",
        "stone.width",
        "stone.depth",
        "stone.orientation",
        "setting.prongDiameter",
        "setting.prongHeight",
        "setting.basketHeight",
        "setting.bezelWallThickness",
        "setting.bezelWallHeight",
        # Sprint 26.
        "pave.stoneScale",
        "pave.stoneOrientationDeg",
        "pave.retention.beadRadiusMm",
        "pave.spec.pitchMm",
        "pave.spec.rowPitchMm",
        "pave.spec.rowCount",
        "pave.spec.angularSpanDeg",
        "pave.spec.stoneSpacingMm",
        "pave.spec.rowSpacingMm",
        "pave.spec.columnCount",
    }
)


def is_pave_density_term(token: str) -> bool:
    """Whether a token names a pavé density rather than a value.

    Used to turn "make the stones denser" into a CLARIFICATION rather than a
    silently invented pitch.
    """

    return token.strip().lower() in PAVE_DENSITY_TERMS


def is_numeric_field(field: str) -> bool:
    return field in _NUMERIC_FIELDS


def flatten_definition(definition: JewelryDefinition) -> dict[str, Any]:
    """Dotted-path -> value for every leaf field in a JewelryDefinition,
    recursing into nested objects (e.g. `band.widthTaper.mode`, added
    Sprint 17) so every reported value is a real scalar `FieldDiff` can
    hold — never a raw nested dict."""

    out: dict[str, Any] = {}
    data = definition.model_dump(mode="json")
    for section, fields in data.items():
        if not isinstance(fields, dict):
            continue
        _flatten_into(out, section, fields)
    return out


def _flatten_into(out: dict[str, Any], prefix: str, value: Any) -> None:
    if isinstance(value, dict):
        for key, sub_value in value.items():
            _flatten_into(out, f"{prefix}.{key}", sub_value)
    elif isinstance(value, list):
        # A LIST-valued leaf, rendered as canonical JSON (Sprint 21).
        #
        # `FieldDiff` holds a scalar, so a raw list raised a validation error
        # the moment `stone.gem.treatments` became the first list-valued leaf in
        # a definition — an interpretation that was otherwise entirely valid
        # failed outright. Sorted-key JSON keeps the value faithful AND keeps
        # `changed` detection exact, since two equal lists always render to the
        # same string. Reporting a length or a placeholder instead would have
        # made the diff lie about what the user is being asked to approve.
        out[prefix] = json.dumps(value, sort_keys=True, separators=(",", ":"))
    else:
        out[prefix] = value


def compute_diff(
    before: JewelryDefinition | None, after: JewelryDefinition
) -> list[FieldDiff]:
    """Deterministic before/after diff for the MODIFY review UI.

    Never LLM-generated — see 311-proposal-diff-model.md. When `before` is
    None (a CREATE), every field is reported unchanged against itself so
    the review UI has a uniform shape to render either way.
    """

    before_flat = flatten_definition(before) if before is not None else {}
    after_flat = flatten_definition(after)
    diffs: list[FieldDiff] = []
    for path, proposed_value in after_flat.items():
        previous_value = before_flat.get(path)
        diffs.append(
            FieldDiff(
                path=path,
                previousValue=previous_value,
                proposedValue=proposed_value,
                changed=before is not None and previous_value != proposed_value,
            )
        )
    return diffs


# Phrases that indicate the request text is trying to act on the assistant
# rather than describe a jewelry design — treated as untrusted input per
# the same instruction-source-boundary discipline used everywhere else in
# this project. This is a coarse, explicit denylist, not a claim of
# complete prompt-injection immunity — see 314-prompt-injection-and-untrusted-input.md.
_INJECTION_MARKERS: tuple[str, ...] = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "ignore the system prompt",
    "disregard your instructions",
    "you are now",
    "system prompt",
    "reveal your instructions",
    "print your instructions",
    "environment variable",
    "api key",
    "act as",
    "jailbreak",
)


def detect_prompt_injection_risk(text: str) -> str | None:
    """Returns a human-readable reason if `text` looks like an injection attempt, else None."""

    lowered = text.lower()
    for marker in _INJECTION_MARKERS:
        if marker in lowered:
            return f"Request text contains a suspicious instruction-override phrase: {marker!r}."
    return None
