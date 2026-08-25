"""The controlled Design Intent vocabulary — v1.

Every concept category is an ORDERED semantic continuum (a list of
canonical values), never a millimeter value and never an invented 0-100
score — see docs/bible/13-design-intent/338-style-continuum-model.md.
Synonym tables map raw IT/EN text to canonical values, deliberately
excluding genuinely ambiguous words (e.g. Italian "importante", which can
mean either "substantial" or "eye-catching" depending on context) — an
excluded word simply becomes an unresolved descriptor rather than a
guessed classification. See 333-intent-vocabulary.md and
335-aesthetic-descriptor-model.md.
"""

from __future__ import annotations

from typing import NamedTuple


class ConceptCategory(NamedTuple):
    order: tuple[str, ...]
    synonyms: dict[str, str]


VISUAL_WEIGHT = ConceptCategory(
    order=("DELICATE", "LIGHT", "BALANCED", "SUBSTANTIAL", "BOLD"),
    synonyms={
        "delicate": "DELICATE",
        "delicato": "DELICATE",
        "delicata": "DELICATE",
        "fine": "DELICATE",
        "light": "LIGHT",
        "leggero": "LIGHT",
        "leggera": "LIGHT",
        "lightweight-looking": "LIGHT",
        "balanced": "BALANCED",
        "bilanciato": "BALANCED",
        "bilanciata": "BALANCED",
        "substantial": "SUBSTANTIAL",
        "sostanzioso": "SUBSTANTIAL",
        "sostanziosa": "SUBSTANTIAL",
        "bold": "BOLD",
        "audace": "BOLD",
    },
)

SIMPLICITY = ConceptCategory(
    order=("MINIMAL", "CLEAN", "BALANCED", "DETAILED", "ORNATE"),
    synonyms={
        "minimal": "MINIMAL",
        "minimalista": "MINIMAL",
        "clean": "CLEAN",
        "pulito": "CLEAN",
        "pulita": "CLEAN",
        "simple": "CLEAN",
        "semplice": "CLEAN",
        "balanced": "BALANCED",
        "bilanciato": "BALANCED",
        "bilanciata": "BALANCED",
        "detailed": "DETAILED",
        "dettagliato": "DETAILED",
        "dettagliata": "DETAILED",
        "ornate": "ORNATE",
        "elaborato": "ORNATE",
        "elaborata": "ORNATE",
    },
)

STYLE_TEMPORALITY = ConceptCategory(
    order=("CLASSIC", "TIMELESS", "CONTEMPORARY", "MODERN"),
    synonyms={
        "classic": "CLASSIC",
        "classico": "CLASSIC",
        "classica": "CLASSIC",
        "timeless": "TIMELESS",
        "contemporary": "CONTEMPORARY",
        "contemporaneo": "CONTEMPORARY",
        "contemporanea": "CONTEMPORARY",
        "modern": "MODERN",
        "moderno": "MODERN",
        "moderna": "MODERN",
    },
)

VISUAL_EMPHASIS = ConceptCategory(
    order=("UNDERSTATED", "BALANCED", "CENTER_FOCUSED", "STATEMENT"),
    synonyms={
        "understated": "UNDERSTATED",
        "discreto": "UNDERSTATED",
        "discreta": "UNDERSTATED",
        "sobrio": "UNDERSTATED",
        "sobria": "UNDERSTATED",
        "balanced": "BALANCED",
        "statement": "STATEMENT",
        "vistoso": "STATEMENT",
        "vistosa": "STATEMENT",
    },
)

PROPORTIONAL_CHARACTER = ConceptCategory(
    order=("SLIM", "BALANCED", "BROAD"),
    synonyms={
        "slim": "SLIM",
        "sottile": "SLIM",
        "snella": "SLIM",
        "narrow": "SLIM",
        "balanced": "BALANCED",
        "broad": "BROAD",
        "largo": "BROAD",
        "larga": "BROAD",
        "ampio": "BROAD",
        "ampia": "BROAD",
    },
)

STRUCTURAL_CHARACTER = ConceptCategory(
    order=("SOFT", "CLEAN", "STRONG"),
    synonyms={
        "soft": "SOFT",
        "morbido": "SOFT",
        "morbida": "SOFT",
        "clean": "CLEAN",
        "pulito": "CLEAN",
        "pulita": "CLEAN",
        "strong": "STRONG",
        "robusto": "STRONG",
        "robusta": "STRONG",
        "solido": "STRONG",
        "solida": "STRONG",
    },
)

CATEGORIES: dict[str, ConceptCategory] = {
    "VISUAL_WEIGHT": VISUAL_WEIGHT,
    "SIMPLICITY": SIMPLICITY,
    "STYLE_TEMPORALITY": STYLE_TEMPORALITY,
    "VISUAL_EMPHASIS": VISUAL_EMPHASIS,
    "PROPORTIONAL_CHARACTER": PROPORTIONAL_CHARACTER,
    "STRUCTURAL_CHARACTER": STRUCTURAL_CHARACTER,
}

# A word may belong to more than one category's synonym table (e.g. "clean"
# is both a SIMPLICITY and a STRUCTURAL_CHARACTER term); the caller decides
# which category a given raw statement targets — see normalizer.py.

TARGET_SYNONYMS: dict[str, str] = {
    "ring": "RING",
    "anello": "RING",
    "whole ring": "RING",
    "overall": "RING",
    "band": "BAND",
    "fascia": "BAND",
    "stone": "STONE",
    "pietra": "STONE",
    "diamond": "STONE",
    "diamante": "STONE",
    "setting": "SETTING",
    "castone": "SETTING",
    "prongs": "PRONGS",
    "griffe": "PRONGS",
    "basket": "BASKET",
    "jewelry": "JEWELRY_PRODUCT",
    "gioiello": "JEWELRY_PRODUCT",
    "product": "JEWELRY_PRODUCT",
}


def concept_values(concept: str) -> tuple[str, ...]:
    category = CATEGORIES.get(concept)
    return category.order if category is not None else ()


def continuum_distance(concept: str, value_a: str, value_b: str) -> int | None:
    """Distance between two values on a concept's ordered continuum.

    Returns None if either value isn't in the continuum (should not
    normally happen for two already-normalized values).
    """

    order = concept_values(concept)
    if value_a not in order or value_b not in order:
        return None
    return abs(order.index(value_a) - order.index(value_b))
