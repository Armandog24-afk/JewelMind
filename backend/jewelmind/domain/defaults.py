"""The canonical default JewelryDefinition, matching the product spec exactly."""

from __future__ import annotations

from jewelmind.domain.schema import JewelryDefinition


def default_definition() -> JewelryDefinition:
    """Return a fresh instance of the default solitaire ring definition."""

    return JewelryDefinition()
