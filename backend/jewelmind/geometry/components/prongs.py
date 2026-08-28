"""Thin adapter — the real prong generator lives in `jewelmind.setting.prong`
(Sprint 19). Kept for import-path stability; see
docs/bible/21-setting/current-prong-migration.md.

Round + 4/6 prongs is byte-identical to the pre-Sprint-19 construction: the
Setting System's RADIAL placement strategy reproduces the original
`_prong_positions()` + `prong_center_radius()` pair exactly.
"""

from __future__ import annotations

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.components.stone import build_stone_reference
from jewelmind.geometry.model import GeneratedComponent
from jewelmind.geometry.setting_adapter import setting_definition_from_jdl
from jewelmind.setting.dispatch import generate_setting

__all__ = ["build_prongs"]


def build_prongs(definition: JewelryDefinition) -> GeneratedComponent:
    """Build the prong solids as one compound component.

    Rebuilds the stone reference to derive the Setting's stone facts. The
    assembly path (`assemblies/solitaire.py`) avoids this duplicate build by
    calling the Setting System directly with the stone it already made; this
    convenience wrapper exists for callers and tests that want prongs alone.
    """

    stone_component = build_stone_reference(definition)
    setting_definition = setting_definition_from_jdl(definition, stone_component)
    components, _result = generate_setting(setting_definition)
    return components["prongs"]
