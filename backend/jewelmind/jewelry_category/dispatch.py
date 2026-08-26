"""The generic category dispatch boundary (JEWELRY-ARCH-GOV — see
docs/bible/18-ring-architecture/520-jewelry-category-architecture.md).

`generate_for_category()` knows nothing about ring/earring/pendant
fields — it takes a plain category string, an arbitrary payload, and a
registry mapping category -> generator callable. This is what
`backend/tests/test_jewelry_category_extension.py`'s test-only dummy
category proves is genuinely generic, not ring-shaped. Production code
should use `generate_jewelry()`, the one real JewelryDefinition-aware
entry point.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from jewelmind.jewelry_category.errors import (
    JewelryCategoryNotGeneratableError,
    JewelryCategoryUnsupportedError,
)
from jewelmind.jewelry_category.models import CategoryCapability
from jewelmind.jewelry_category.registry import get_capability

if TYPE_CHECKING:
    from jewelmind.domain.schema import JewelryDefinition
    from jewelmind.geometry.model import GeneratedModel


def generate_for_category(
    category: str,
    payload: Any,
    *,
    registry: dict[str, Callable[[Any], Any]],
    capabilities: dict[str, CategoryCapability] | None = None,
) -> Any:
    """`capabilities` defaults to the real production registry — tests
    pass a test-local dict here to prove this function is genuinely
    generic without ever touching `CATEGORY_CAPABILITIES` (see
    `backend/tests/test_jewelry_category_extension.py`)."""

    capability = capabilities.get(category) if capabilities is not None else get_capability(category)
    if capability is None:
        raise JewelryCategoryUnsupportedError(f"Unknown jewelry category '{category}'.")
    if not capability.generationSupported:
        raise JewelryCategoryNotGeneratableError(
            f"'{category}' is a recognized jewelry category but generation is not yet supported."
        )
    generator = registry.get(category)
    if generator is None:
        raise JewelryCategoryNotGeneratableError(f"No generator registered for category '{category}'.")
    return generator(payload)


_category_generators_cache: dict[str, Callable[[Any], Any]] | None = None


def _category_generators() -> dict[str, Callable[[Any], Any]]:
    """Built lazily, on first real dispatch rather than at module-import
    time: `jewelmind.ring` imports `jewelmind.jewelry_category.errors`,
    so importing `jewelmind.ring.families` here eagerly (at this
    module's own import time) is a genuine circular import whenever
    `jewelmind.ring` is the first of the two packages to be imported.
    Deferring the import until this function is actually called (well
    after both packages have finished loading) avoids it entirely."""

    global _category_generators_cache
    if _category_generators_cache is None:
        from jewelmind.ring.families import generate_ring

        _category_generators_cache = {"ring": generate_ring}
    return _category_generators_cache


def generate_jewelry(definition: JewelryDefinition) -> GeneratedModel:
    """The one real production entry point: dispatch a real
    `JewelryDefinition` by its own `jewelry.category` field."""

    return generate_for_category(definition.jewelry.category, definition, registry=_category_generators())
