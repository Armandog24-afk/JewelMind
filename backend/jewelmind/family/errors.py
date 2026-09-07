"""Structured multi-stone family errors (Sprint 24).

Plain exceptions, deliberately not `AppError` subclasses: this package is
category- and transport-neutral, and importing `jewelmind.api.errors` would
give a domain model an opinion about HTTP status codes. The API layer maps
these where it needs to, as it already does for Stone, Setting and Arrangement.

Every message names the offending member or role. A family failure the user
cannot locate is barely better than a silent one.
"""

from __future__ import annotations


class FamilyError(Exception):
    """Base for every multi-stone family failure."""


class FamilyTypeUnsupportedError(FamilyError):
    """No compiler is registered for the requested family type.

    An explicit refusal, never a substitution: compiling a cluster for a
    requested three-stone would report one design and build another.
    """


class FamilyRoleInvalidError(FamilyError):
    """A member's role is not one this family accepts.

    A `HALO` member in a toi-et-moi is not a small mistake — it means the
    document describes something the family cannot represent.
    """


class FamilyRoleCardinalityError(FamilyError):
    """A family has the wrong number of members in a role.

    Two centres in a three-stone design, or one side instead of two: the
    structure is expressible in JSON and not as the family it claims to be.
    """


class FamilyMemberMissingError(FamilyError):
    """A required role has no member and none can be derived."""


class FamilyReferenceUnresolvedError(FamilyError):
    """A member references a stone specification or setting that cannot be
    resolved."""


class FamilyParamsInvalidError(FamilyError):
    """Family parameters cannot produce a determinate arrangement."""


class FamilyCapacityExceededError(FamilyError):
    """Compilation would produce more members than the software bound allows.

    A software limit, not a jewelry limit: no claim is made about how many
    stones a design should have.
    """


class FamilyConflictError(FamilyError):
    """A document declares both a family and an explicit arrangement.

    Refused rather than merged. A family COMPILES to an arrangement, so
    accepting both would leave two authorities over one set of placements and
    no determinate rule for which wins.
    """
