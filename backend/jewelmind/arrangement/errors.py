"""Structured Stone Arrangement errors (Sprint 22).

Plain exceptions, deliberately not `AppError` subclasses: this package is
category- AND transport-neutral, and importing `jewelmind.api.errors` would
give a domain model an opinion about HTTP status codes. The API layer maps
these where it needs to, exactly as it does for Stone and Setting errors.

Every message names the offending ID. An arrangement failure the user cannot
locate is barely better than a silent one.
"""

from __future__ import annotations


class ArrangementError(Exception):
    """Base for every Stone Arrangement failure."""


class ArrangementIdInvalidError(ArrangementError):
    """A malformed instance, group, pattern or relation ID.

    Raised before any lookup, so a user-authored ID never reaches a path, a
    command, or a dictionary key.
    """


class DuplicateInstanceIdError(ArrangementError):
    """Two instances claim the same ID.

    Fatal rather than deduplicated: IDs are the authoritative identity, so two
    stones sharing one means the document cannot say which stone a relation,
    an override or a generated component refers to.
    """


class UnresolvedInstanceReferenceError(ArrangementError):
    """A pattern, relation or placement names an instance that does not exist."""


class UnresolvedGroupReferenceError(ArrangementError):
    """A placement or pattern names a group that does not exist."""


class UnresolvedStoneReferenceError(ArrangementError):
    """An instance references a stone specification that cannot be resolved.

    Distinct from an unresolved INSTANCE reference: the instance exists, but
    the stone it claims to be an occurrence of does not.
    """


class ArrangementPatternInvalidError(ArrangementError):
    """A pattern's parameters cannot produce a determinate set of members."""


class ArrangementRelationInvalidError(ArrangementError):
    """A relation's arity or membership is inconsistent with its kind."""


class ArrangementCapacityExceededError(ArrangementError):
    """Resolution would produce more instances than the software bound allows.

    A software limit, not a jewelry limit: no claim is made about how many
    stones a piece should carry.
    """
