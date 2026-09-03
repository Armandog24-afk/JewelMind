"""Deterministic reference resolution.

Reuses Design Intent's own real target vocabulary (`TARGET_SYNONYMS`)
rather than duplicating a second word list — "the band"/"la fascia" must
resolve to the exact same `BAND` target Design Intent already knows about.
See docs/bible/14-conversation/379-reference-resolution.md and
380-pronoun-and-implicit-target-resolution.md.
"""

from __future__ import annotations

from jewelmind.design_intent.vocabulary import TARGET_SYNONYMS

# Phrases that mean "don't change this — keep it exactly as it is now".
# Deliberately literal and small — see 380's "safe vs. unsafe implicit
# resolution" distinction: a preserve phrase without an explicit target is
# NOT resolved to a guess, it is treated as ambiguous.
_PRESERVE_MARKERS: tuple[str, ...] = (
    "leave",
    "keep",
    "lascia",
    "lasciala",
    "lascialo",
    "lasciate",
)

# Bare pronouns that, on their own, never safely resolve to a target —
# see 380: a pronoun following an established topic may resolve via
# `session.lastReferencedTarget`, but never via guesswork from the pronoun
# text alone.
_BARE_PRONOUNS: tuple[str, ...] = ("it", "that", "quello", "quella", "lo", "la")

# Comparative/dimensional words are the specific case where a missing
# target genuinely matters — "make it wider" could mean the band, the
# stone, or the whole ring, and each implies a different numeric field.
# A bare pronoun WITHOUT one of these markers (e.g. "make it delicate",
# "make it more classic") is a legitimate whole-ring aesthetic statement
# with no missing information — Design Intent Model already defaults an
# unscoped aesthetic descriptor to RING (see docs/bible/13-design-intent/),
# so it is never treated as ambiguous here.
_COMPARATIVE_MARKERS: tuple[str, ...] = (
    "wider", "narrower", "bigger", "smaller", "larger", "thicker", "thinner",
    "più largo", "più larga", "più stretto", "più grande", "più piccolo",
    "più spesso", "più sottile", "wide", "narrow",
)

# Materials named directly are a safe, real exception: a color-of-gold or
# a metal name uniquely identifies MATERIAL_APPEARANCE regardless of
# pronoun wording, because no other target has a "material" sense — e.g.
# "make it rose gold" is safe even though "it" alone would not be.
_MATERIAL_WORDS: tuple[str, ...] = (
    "gold",
    "oro",
    "platinum",
    "platino",
    "silver",
    "argento",
    "rose gold",
    "oro rosa",
    "white gold",
    "oro bianco",
    "yellow gold",
    "oro giallo",
)


def mentions_gem_word(text: str) -> bool:
    """Whether `text` names a gem material, an origin, or a treatment.

    A gem name uniquely identifies the STONE, for the same reason a metal name
    uniquely identifies MATERIAL_APPEARANCE (see `_MATERIAL_WORDS` above): no
    other target in the vocabulary has a gem-material sense. So "make it a
    ruby" is a safe resolution even though "it" alone would not be.

    The terms come from `designer.gem_language`, which derives them from the
    live gem registry — never a second word list here. Its ambiguous cut/species
    terms ("emerald", "pearl") are already excluded from that index, so this
    cannot resolve a target off a word that might have meant the cut.
    """

    from jewelmind.designer.gem_language import (
        GEM_ORIGIN_SYNONYMS,
        GEM_TREATMENT_SYNONYMS,
        GEM_UNTREATED_TERMS,
        gem_alias_index,
    )

    lowered = f" {text.lower()} "
    terms = (
        set(gem_alias_index())
        | set(GEM_ORIGIN_SYNONYMS)
        | set(GEM_TREATMENT_SYNONYMS)
        | set(GEM_UNTREATED_TERMS)
    )
    # Whole-word matching: a bare substring test would fire on "corallo" inside
    # an unrelated word, and — worse — on the short registry IDs.
    return any(f" {term} " in lowered for term in terms)


def find_explicit_target(text: str) -> str | None:
    """Scans `text` for a known component word (band/stone/prongs/...).

    Returns the first canonical target found, or None. Longer phrases are
    checked before single words so "oro rosa" matches before a bare "oro"
    would.
    """

    lowered = text.lower()
    for phrase in sorted(TARGET_SYNONYMS.keys(), key=len, reverse=True):
        if phrase in lowered:
            return TARGET_SYNONYMS[phrase]
    return None


def find_preserve_target(text: str) -> str | None:
    """Returns the target of a "leave/keep X as is" phrase, or None if
    the text isn't a preserve phrase or names no explicit target."""

    lowered = text.lower()
    if not any(marker in lowered for marker in _PRESERVE_MARKERS):
        return None
    return find_explicit_target(text)


def mentions_material_word(text: str) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in _MATERIAL_WORDS)


def mentions_comparative_marker(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _COMPARATIVE_MARKERS)


def resolve_implicit_target(text: str, last_referenced_target: str | None) -> tuple[str | None, bool]:
    """Resolves a possibly-implicit target reference.

    Returns ``(target_or_None, is_ambiguous)``. A safe resolution (an
    explicit target word, or a bare pronoun immediately following an
    established topic, or a material word) never sets `is_ambiguous`. A
    bare pronoun with no established topic is reported as ambiguous
    (CONV-GOV-010: ambiguous references must trigger clarification, never
    an arbitrary guess) rather than silently resolved or silently
    dropped.
    """

    explicit = find_explicit_target(text)
    if explicit is not None:
        return explicit, False

    if mentions_material_word(text):
        return "MATERIAL_APPEARANCE", False

    # Sprint 21: a gem, origin or treatment word resolves to the STONE. Checked
    # after the metal words so a design whose text names both keeps the
    # pre-existing behaviour rather than silently changing which target an old
    # phrase resolves to.
    if mentions_gem_word(text):
        return "STONE", False

    lowered = text.lower()
    has_bare_pronoun = any(f" {p} " in f" {lowered} " for p in _BARE_PRONOUNS)
    if not has_bare_pronoun:
        return None, False

    if last_referenced_target is not None:
        return last_referenced_target, False

    # No established topic to resolve the pronoun against. Only a
    # comparative/dimensional request is genuinely ambiguous without a
    # target (which field would grow?) — a bare aesthetic statement
    # ("make it delicate") is not, see the comment on
    # `_COMPARATIVE_MARKERS` above.
    return (None, True) if mentions_comparative_marker(text) else (None, False)
