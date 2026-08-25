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
