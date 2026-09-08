"""Structured pavé errors (Sprint 26).

Plain exceptions, deliberately not `AppError` subclasses: this package is
category- and transport-neutral, and importing `jewelmind.api.errors` would give
a domain model an opinion about HTTP status codes. The API layer maps these
where it needs to, exactly as it already does for Stone, Setting, Arrangement,
Family and Halo.

Every message names the offending field, host or count. A pavé failure the user
cannot locate is barely better than a silent one.
"""

from __future__ import annotations


class PaveError(Exception):
    """Base for every pavé failure."""


class PaveHostUnsupportedError(PaveError):
    """The requested host surface has no resolver.

    Refused rather than approximated onto another surface: a pavé on the wrong
    surface is worse than a pavé that fails loudly.
    """


class PaveHostUnresolvedError(PaveError):
    """The host surface exists as a target but this design cannot supply it.

    A halo-plane pavé on a design with no halo, for example. The target is real
    and the design does not have it, which is a different failure from an
    unsupported target and is reported differently.
    """


class PaveFieldEmptyError(PaveError):
    """The parameters describe no stones at all.

    Raised rather than returning an empty field, which would silently produce a
    design that declares a pavé and contains none.
    """


class PaveCapacityExceededError(PaveError):
    """The field would produce more stones than the software bound allows.

    A software safety limit, not a jewelry limit: no claim is made about how
    many stones a pavé should carry. It exists so a malformed or hostile
    document cannot ask the kernel for an unbounded number of solids.
    """


class PaveGeometryUnsupportedError(PaveError):
    """A requested retention strategy has no builder.

    Never substituted with another strategy: reporting shared beads while
    building individual ones would describe one design and build another.
    """


class PaveIdentityCollisionError(PaveError):
    """A pavé instance id already exists in the arrangement it composes onto."""


class PaveContainmentError(PaveError):
    """The field does not fit the host surface under a strict containment
    policy.

    A GEOMETRIC statement about the declared surface extent, not a professional
    judgment about whether the metal could carry the stones.
    """
