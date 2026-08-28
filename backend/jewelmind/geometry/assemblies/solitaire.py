"""Full solitaire ring assembly: band + stone reference + setting + basket.

Sprint 19: the setting component is produced by the category-neutral
Setting System (`jewelmind.setting`) via `geometry/setting_adapter.py`.
This module is the RingHead integration point — it owns the band, the
basket support, and the decision to fuse them with whatever the Setting
produced. The Setting itself knows nothing about any of that
(SETTING-GOV-014).
"""

from __future__ import annotations

import time

import cadquery as cq

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.components.band import build_ring_band
from jewelmind.geometry.components.basket import build_basket_support
from jewelmind.geometry.components.stone import build_stone_reference
from jewelmind.geometry.constants import GENERATOR_VERSION
from jewelmind.geometry.model import BoundingBox, GeneratedComponent, GeneratedModel
from jewelmind.geometry.setting_adapter import setting_definition_from_jdl
from jewelmind.setting.dispatch import generate_setting
from jewelmind.utils.hashing import definition_hash


def _fuse_metal(metal_components: list[GeneratedComponent]):
    """Fuse every production-metal component into one solid body.

    Falls back to an unfused compound (with a warning) if the boolean fuse
    fails for any reason — the individual solids are still valid and
    exportable even if OpenCascade cannot merge them into a single solid.

    The fuse order is preserved from the pre-Sprint-19 implementation
    (band, basket, then the setting component) so a prong model's fused
    result is byte-identical.
    """

    warnings: list[str] = []
    shapes = [c.shape for c in metal_components]
    try:
        fused = shapes[0]
        for shape in shapes[1:]:
            fused = fused.fuse(shape)
        if not fused.Solids():
            raise ValueError("fuse produced no solids")
        return fused, warnings
    except Exception as exc:  # noqa: BLE001 - OCC boolean failures vary widely
        names = ", ".join(c.name for c in metal_components)
        warnings.append(
            f"Combined metal union failed ({exc}); exporting {names} "
            "as a multi-solid compound instead of a single fused solid."
        )
        compound = cq.Compound.makeCompound(shapes)
        return compound, warnings


def build_solitaire_ring(definition: JewelryDefinition) -> GeneratedModel:
    """Build the complete solitaire ring model from a validated definition.

    Callers are expected to have already run validation and confirmed there
    are no errors — this function does not re-validate; it deterministically
    turns parameters into geometry.
    """

    start = time.perf_counter()

    band = build_ring_band(definition)
    stone = build_stone_reference(definition)
    basket = build_basket_support(definition)

    setting_definition = setting_definition_from_jdl(definition, stone)
    setting_components, setting_result = generate_setting(setting_definition)

    # Fuse order preserved from pre-Sprint-19: band, basket, then setting.
    setting_metal = [
        setting_components[name]
        for name in setting_result.productionComponents
        if name in setting_components
    ]
    combined_metal, fuse_warnings = _fuse_metal([band, basket, *setting_metal])
    combined_metal_volume = combined_metal.Volume()

    metal_bbox = BoundingBox.from_shape(combined_metal)
    full_bbox = metal_bbox.union(stone.bounding_box)

    warnings = [
        *band.warnings,
        *stone.warnings,
        *basket.warnings,
    ]
    for component in setting_components.values():
        warnings.extend(component.warnings)
    warnings.extend(fuse_warnings)

    components: dict[str, GeneratedComponent] = {
        "band": band,
        "stone_reference": stone,
    }
    components.update(setting_components)
    components["basket_support"] = basket

    duration = time.perf_counter() - start

    return GeneratedModel(
        definition_hash=definition_hash(definition),
        generator_version=GENERATOR_VERSION,
        generation_duration_s=duration,
        components=components,
        combined_metal=combined_metal,
        combined_metal_volume_mm3=combined_metal_volume,
        bounding_box=full_bbox,
        warnings=warnings,
        setting_result=setting_result,
    )
