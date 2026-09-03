"""Basket support: a thin re-export of the Setting System's head builder.

Sprint 23 moved head construction into `jewelmind/setting/head.py` so a head is
a CATEGORY-NEUTRAL Setting concern rather than a ring-specific one — a future
pendant or earring reaching the same structure gets it for free. This module
survives as the Ring-side entry point, the same pattern `band.py`, `stone.py`
and `prongs.py` already follow.

THE GEOMETRY IS UNCHANGED for a `BASKET` architecture, which is every
pre-Sprint-23 document: `head.py::_basket()` reproduces the previous
construction character-for-character, and the component is still named
`basket_support`. The radial dimensions are resolved by
`geometry/setting_adapter.py::head_definition_from_jdl()`, which restates the
same `centre ± prongR` arithmetic this module used to do inline.
"""

from __future__ import annotations

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.model import GeneratedComponent
from jewelmind.setting.head import build_head


def build_basket_support(definition: JewelryDefinition) -> GeneratedComponent:
    """Build the head component (named `basket_support`) for this ring."""

    from jewelmind.geometry.setting_adapter import (
        head_definition_from_jdl,
        setting_attachment_interface,
    )

    return build_head(
        head_definition_from_jdl(definition),
        setting_attachment_interface(definition),
    )
