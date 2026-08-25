"""Deterministic descriptor/target/relation normalization.

None of this depends on an AI provider — it is plain, testable Python run
against whatever a provider (real or fake) reports as a raw statement's
`target`/`concept`/`value`. The provider (which sees full sentence
context) is responsible for picking which of the 6 concept categories a
word belongs to — see docs/bible/13-design-intent/356-designer-intent-extraction.md
— the normalizer only ever validates that choice deterministically against
the real controlled vocabulary; it never guesses a category on its own.
"""

from __future__ import annotations

from jewelmind.design_intent.vocabulary import CATEGORIES, TARGET_SYNONYMS

KNOWN_TARGETS: frozenset[str] = frozenset(
    {
        "JEWELRY_PRODUCT",
        "RING",
        "BAND",
        "STONE",
        "SETTING",
        "PRONGS",
        "BASKET",
        "MATERIAL_APPEARANCE",
        "OVERALL_PROPORTION",
        "VISUAL_HIERARCHY",
    }
)

KNOWN_CONCEPTS: frozenset[str] = frozenset(CATEGORIES.keys())

KNOWN_PREDICATES: frozenset[str] = frozenset(
    {
        "NARROWER_THAN",
        "BROADER_THAN",
        "DOMINANT_OVER",
        "SUBORDINATE_TO",
        "DISCREET_RELATIVE_TO",
        "BALANCED_WITH",
    }
)

# Free-text predicate phrasing a provider might use, normalized to the
# controlled set above. Deliberately small and literal — an unrecognized
# phrasing is dropped as an unresolved relation, never guessed.
PREDICATE_SYNONYMS: dict[str, str] = {
    "narrower_than": "NARROWER_THAN",
    "narrower than": "NARROWER_THAN",
    "broader_than": "BROADER_THAN",
    "broader than": "BROADER_THAN",
    "dominant_over": "DOMINANT_OVER",
    "dominant over": "DOMINANT_OVER",
    "should dominate": "DOMINANT_OVER",
    "subordinate_to": "SUBORDINATE_TO",
    "subordinate to": "SUBORDINATE_TO",
    "discreet_relative_to": "DISCREET_RELATIVE_TO",
    "discreet relative to": "DISCREET_RELATIVE_TO",
    "balanced_with": "BALANCED_WITH",
    "balanced with": "BALANCED_WITH",
}


def normalize_target(raw_target: str) -> str | None:
    token = raw_target.strip()
    if token.upper() in KNOWN_TARGETS:
        return token.upper()
    return TARGET_SYNONYMS.get(token.strip().lower())


def normalize_descriptor(concept: str, raw_value: str) -> tuple[str | None, bool]:
    """Normalize a raw descriptor word against one concept's real vocabulary.

    Returns ``(canonical_value_or_None, is_exact)``. `is_exact` is True
    when the raw text already equalled the canonical value (no synonym
    lookup needed) — used to distinguish `EXACT` from
    `HIGH_CONFIDENCE_NORMALIZATION` confidence.
    """

    category = CATEGORIES.get(concept)
    if category is None:
        return None, False
    token = raw_value.strip()
    if token.upper() in category.order:
        return token.upper(), True
    return category.synonyms.get(token.lower()), False


def normalize_predicate(raw_predicate: str) -> str | None:
    token = raw_predicate.strip()
    if token.upper() in KNOWN_PREDICATES:
        return token.upper()
    return PREDICATE_SYNONYMS.get(token.lower())
