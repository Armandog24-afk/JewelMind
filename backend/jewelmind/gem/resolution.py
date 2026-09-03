"""Gem resolution: identity + registry + visual profile -> `ResolvedGem`.

THE ONLY PLACE THE JOIN HAPPENS. Forge, Vision, Foundry, the technical
specification and the API all read `ResolvedGem`, so none of them can resolve a
gem slightly differently from the others — the failure mode Sprint 20 saw three
times when Setting and Designer each kept their own copy of a capability set.

RESOLUTION NEVER RAISES AND NEVER SUBSTITUTES.

A saved project may reference a gem ID that has since been removed. That design
must still load (brief section 10), so resolution degrades to `unknown` and sets
`wasUnresolved` — an observable fact, not a silent swap. What it must never do
is pick a *different real gem* that looks similar, or infer a gem from the
stone's shape.

Validation is separate: `validate_gem_identity()` reports problems for Forge to
turn into rule results.
"""

from __future__ import annotations

import re

from jewelmind.gem.errors import (
    GemIdInvalidError,
    GemNotFoundError,
    GemOriginInvalidError,
)
from jewelmind.gem.models import (
    GEM_ID_PATTERN,
    MAX_GEM_ID_LENGTH,
    UNKNOWN_GEM_ID,
    GemDefinition,
    GemIdentity,
    ResolvedGem,
)
from jewelmind.gem.registry import GEM_REGISTRY, GEM_REGISTRY_VERSION, alias_lookup
from jewelmind.gem.visual import (
    FALLBACK_PROFILE,
    VISUAL_PROFILE_SET_VERSION,
    get_visual_profile,
)

_ID_RE = re.compile(GEM_ID_PATTERN)

#: The version string a generated artifact records, identifying both the
#: registry content and the visual profile set it was produced with
#: (brief section 28).
GEM_SYSTEM_VERSION = f"registry-{GEM_REGISTRY_VERSION}+visual-{VISUAL_PROFILE_SET_VERSION}"


def is_valid_gem_id(gem_id: str) -> bool:
    """Whether a string is a structurally valid gem ID.

    Checked before any lookup so a malformed value never reaches a path, a
    command, or a dictionary key (brief section 37).
    """

    return bool(
        isinstance(gem_id, str)
        and len(gem_id) <= MAX_GEM_ID_LENGTH
        and _ID_RE.match(gem_id)
    )


def require_gem_id(gem_id: str) -> str:
    """Validate an ID's shape, raising `GemIdInvalidError` if malformed."""

    if not is_valid_gem_id(gem_id):
        raise GemIdInvalidError(
            f"{gem_id!r} is not a valid gem identifier. IDs are lowercase, "
            "dot-separated, and limited to letters, digits, '_' and '-'."
        )
    return gem_id


def resolve_alias(term: str) -> str | None:
    """Resolve a name, alias or canonical ID to a canonical gem ID.

    Case-insensitive and whitespace-tolerant, because the input is a human
    term. Returns `None` when nothing matches — never a guess.

    An alias is never a separate identity (brief section 30): the alias table is
    built from the registry and the registry tests assert no string resolves to
    two different IDs.
    """

    if not isinstance(term, str):
        return None
    return alias_lookup().get(term.strip().lower())


def get_gem_or_raise(gem_id: str) -> GemDefinition:
    """Look a gem up, raising if it does not exist.

    For callers that genuinely need a real entry — an explicit API lookup, or
    validation. Normal resolution degrades instead; see `resolve_gem`.
    """

    require_gem_id(gem_id)
    entry = GEM_REGISTRY.get(gem_id)
    if entry is None:
        raise GemNotFoundError(f"No gem registry entry with id {gem_id!r}.")
    return entry


def resolve_gem(identity: GemIdentity | None) -> ResolvedGem:
    """Join an identity to its registry entry and visual profile.

    Never raises. `None` — a legacy design with no gem at all — resolves to
    `unknown`, which is deliberately NOT diamond: the MVP having used a
    diamond-like stone is not evidence about any design's intent
    (brief section 18).
    """

    if identity is None:
        identity = GemIdentity(gemId=UNKNOWN_GEM_ID)

    was_unresolved = False
    entry = GEM_REGISTRY.get(identity.gemId) if is_valid_gem_id(identity.gemId) else None

    if entry is None:
        # A removed or malformed reference. The design still loads, and the
        # reader is told — rather than being handed a plausible-looking gem
        # nobody chose.
        was_unresolved = True
        entry = GEM_REGISTRY[UNKNOWN_GEM_ID]

    profile_id = identity.visualProfileId or entry.defaultVisualProfileId
    profile = get_visual_profile(profile_id)

    return ResolvedGem(
        identity=identity,
        definition=entry,
        visualProfile=profile,
        wasUnresolved=was_unresolved,
        usedFallbackVisualProfile=profile.profileId == FALLBACK_PROFILE.profileId,
        registryVersion=GEM_SYSTEM_VERSION,
    )


def require_origin_applicable(identity: GemIdentity) -> None:
    """Raise when a declared origin is not applicable to the gem type.

    Refused rather than corrected: a cubic zirconia declared `NATURAL` is a
    contradiction, and resolving it would mean deciding whether the user meant
    the material or the origin.

    `UNKNOWN` is always accepted — not knowing an origin is a legitimate state,
    and every entry's `applicableOrigins` is about what the gem CAN be, not
    about what must be recorded.
    """

    entry = GEM_REGISTRY.get(identity.gemId)
    if entry is None:
        return
    if identity.origin == "UNKNOWN":
        return
    if identity.origin not in entry.applicableOrigins:
        raise GemOriginInvalidError(
            f"origin {identity.origin!r} is not applicable to gem "
            f"{identity.gemId!r}. Applicable: "
            f"{', '.join(entry.applicableOrigins)}."
        )


def effective_display_name(resolved: ResolvedGem, language: str = "en") -> str:
    """The name to show a user, in the requested language.

    A custom gem shows the user's own `customName`, because that is the only
    description of it that exists. Otherwise a localized display name is
    preferred, falling back to the canonical English name — never to the ID,
    which is an identifier rather than a label (brief section 31).
    """

    if resolved.identity.customName:
        return resolved.identity.customName
    return resolved.definition.displayNames.get(
        language, resolved.definition.canonicalName
    )


def treatment_summary(identity: GemIdentity) -> str:
    """A short human-readable treatment state.

    Distinguishes the three genuinely different states an empty-looking
    treatment list can mean:

        no records                 -> "not recorded"
        every record NOT_PRESENT   -> "declared untreated"
        at least one PRESENT       -> the treatments themselves

    "Not recorded" is never rendered as "untreated". That conflation is exactly
    what the `NOT_PRESENT` status exists to prevent.
    """

    if not identity.treatments:
        return "not recorded"

    present = [t for t in identity.treatments if t.status in ("PRESENT", "SUSPECTED")]
    if not present:
        if all(t.status == "NOT_PRESENT" for t in identity.treatments):
            return "declared untreated"
        return "not recorded"

    parts = []
    for treatment in present:
        label = treatment.treatment.lower().replace("_", " ")
        if treatment.status == "SUSPECTED":
            label = f"{label} (suspected)"
        parts.append(label)
    return ", ".join(parts)
