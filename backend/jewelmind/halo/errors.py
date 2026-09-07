"""Structured halo errors (Sprint 25).

Plain exceptions, deliberately not `AppError` subclasses: this package is
category- and transport-neutral, and importing `jewelmind.api.errors` would give
a domain model an opinion about HTTP status codes. The API layer maps these where
it needs to, exactly as it already does for Stone, Setting, Arrangement and
Family.

Every message names the offending ring, member or centre reference. A halo
failure the user cannot locate is barely better than a silent one.
"""

from __future__ import annotations


class HaloError(Exception):
    """Base for every halo failure."""


class HaloCenterUnresolvedError(HaloError):
    """The halo names a centre the design does not contain.

    Refused rather than defaulted to the design origin. A halo whose centre
    silently moved would surround something the document never nominated, and
    the geometry would not match the declaration.
    """


class HaloVariantMismatchError(HaloError):
    """The variant and the declared rings disagree.

    A `DOUBLE` halo with one ring is not a small mistake: the document claims a
    structure it does not describe, and no ring can be invented for it without
    inventing radii and counts nobody authored.
    """


class HaloIdentityCollisionError(HaloError):
    """A halo instance id already exists in the arrangement it composes onto.

    Ids are the authoritative identity, so a collision would make every
    reference to it — a relation, a generated component, an inspection fact —
    ambiguous.
    """


class HaloCompositionUnsupportedError(HaloError):
    """This family/halo combination is not supported.

    Stated explicitly against a real support table rather than approximated:
    silently anchoring a halo somewhere plausible would produce a design nobody
    asked for.
    """


class HaloCapacityExceededError(HaloError):
    """Composition would produce more instances than the software bound allows.

    A software limit, not a jewelry limit: no claim is made about how many
    stones a halo should carry.
    """
