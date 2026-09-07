"""The effective arrangement: family-compiled, declared directly, or haloed.

ONE PLACEMENT AUTHORITY, REACHED ONE WAY. A design may declare a `family` (which
compiles into an arrangement) or an `arrangement` (which is one already), and
either may additionally carry a `halo` (Sprint 25) whose rings are COMPOSED onto
whichever of the two is present. Every consumer resolves placements from
whatever this function returns. Without that single resolution point, the
assembly, Forge and any future consumer would each decide how a family, an
arrangement and a halo relate, and they would eventually decide differently.

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
from jewelmind.halo.compile import compose_halo

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

    A `halo`, if present, is then COMPOSED onto that result (Sprint 25) — added
    to it rather than replacing it, which is what makes a halo orthogonal to a
    family instead of a fifth family type. A halo declared on its own composes
    onto `None` and supplies its own centre instance, because a halo with no
    centre is not a halo.

    NO HALO STILL MEANS NO CHANGE. `compose_halo(base, None)` returns `base`
    untouched, so every pre-Sprint-25 design reaches the geometry pipeline
    through exactly the arrangement it reached it through before.
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

    base = compile_family(family) if family is not None else arrangement
    return compose_halo(base, definition.halo)
