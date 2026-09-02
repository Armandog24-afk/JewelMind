"""Stone source dispatch (brief section 67).

A registry, never an `if/elif` chain. Two reasons, both learned rather than
assumed:

- Sprint 19's Setting System proved that a registry keeps an escape hatch
  reachable: a future stone source is a registration, not an edit to a growing
  conditional scattered across modules.
- Sprint 19 also proved the failure mode of the alternative — five separate
  modules had hardcoded `prongs`, and the subtlest leak produced *missing
  facts* rather than an error.

`STONE_SOURCE_HANDLERS` contains only handlers that really exist. A source mode
with no implementation is absent from this registry AND absent from
`StoneSourceMode`; nothing here is registered as a placeholder
(SETTING-GOV-005's "no fake handlers", restated for stone sources).
"""

from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache

from jewelmind.domain.schema import StoneSpec
from jewelmind.stone.errors import StoneSourceUnsupportedError
from jewelmind.stone.importing import ImportedStoneGeometry
from jewelmind.stone.models import NormalizedStoneDefinition, StoneSourceMode

StoneSourceHandler = Callable[
    [StoneSpec, ImportedStoneGeometry | None, str], NormalizedStoneDefinition
]


@lru_cache(maxsize=1)
def stone_source_handlers() -> dict[str, StoneSourceHandler]:
    """The real, registered source handlers.

    Built lazily inside a cached function rather than as a module-level
    constant, for the same reason `jewelry_category/dispatch.py` does it: the
    handler lives in `normalize.py`, which imports from this package's other
    modules, and a module-level constant here would force that import at
    package-init time. Deferring it keeps the import graph acyclic.
    """

    from jewelmind.stone.normalize import canonicalize_stone

    def handler(
        stone: StoneSpec,
        imported: ImportedStoneGeometry | None,
        stone_id: str,
    ) -> NormalizedStoneDefinition:
        return canonicalize_stone(stone, imported=imported, stone_id=stone_id)

    # Every mode currently routes through the same canonicalizer, which
    # branches internally. They are registered separately anyway so that a
    # future mode needing genuinely different handling is a new registration
    # rather than another branch inside one function.
    return {
        "PARAMETRIC_REFERENCE": handler,
        "CUSTOM_OUTLINE": handler,
        "MEASURED": handler,
        "IMPORTED_CAD": handler,
    }


def resolve_stone(
    stone: StoneSpec,
    imported: ImportedStoneGeometry | None = None,
    stone_id: str = "stone_reference",
) -> NormalizedStoneDefinition:
    """Normalize a stone through its registered source handler."""

    handler = stone_source_handlers().get(stone.source)
    if handler is None:
        raise StoneSourceUnsupportedError(
            f"No registered handler for stone source mode {stone.source!r}. "
            f"Supported: {', '.join(sorted(stone_source_handlers()))}."
        )
    return handler(stone, imported, stone_id)


def supported_source_modes() -> list[StoneSourceMode]:
    return sorted(stone_source_handlers())  # type: ignore[return-value]
