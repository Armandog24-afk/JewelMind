"""The effective arrangement: family-compiled, or declared directly (Sprint 24).

ONE PLACEMENT AUTHORITY, REACHED ONE WAY. A design may declare a `family` (which
compiles into an arrangement) or an `arrangement` (which is one already), and
every consumer resolves placements from whichever this function returns. Without
that single resolution point, the assembly, Forge and any future consumer would
each decide how a family and an arrangement relate, and they would eventually
decide differently.

DECLARING BOTH IS REFUSED, never merged. A family IS an arrangement expressed
semantically, so accepting both would leave two authorities over one set of
placements with no determinate rule for which wins. Forge reports the same
conflict as `JM-FAMILY-001` before generation is ever attempted.

This module takes a `JewelryDefinition`, so it deliberately sits at the edge of
the family package rather than inside its core: `models.py` and `compile.py`
know nothing about a jewelry document, and this is the one place the two meet —
the same role `geometry/setting_adapter.py` plays for the Setting System.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from jewelmind.arrangement.models import ArrangementDefinition
from jewelmind.family.compile import compile_family
from jewelmind.family.errors import FamilyConflictError

if TYPE_CHECKING:  # pragma: no cover - import cycle guard, typing only
    from jewelmind.domain.schema import JewelryDefinition


def effective_arrangement(
    definition: JewelryDefinition,
) -> ArrangementDefinition | None:
    """The arrangement this design actually has.

    - a family              -> the arrangement it compiles to
    - an arrangement        -> itself, unchanged
    - neither               -> `None`, and the design behaves exactly as it did
                               before families and arrangements existed
    - both                  -> `FamilyConflictError`
    """

    family = definition.family
    arrangement = definition.arrangement

    if family is not None and arrangement is not None:
        raise FamilyConflictError(
            "This design declares both a family and an explicit arrangement. A "
            "family compiles into an arrangement, so accepting both would leave "
            "two authorities over one set of stone placements. Remove one: the "
            "family for full manual control, or the arrangement to keep the "
            "family's semantics."
        )

    if family is not None:
        return compile_family(family)
    return arrangement
