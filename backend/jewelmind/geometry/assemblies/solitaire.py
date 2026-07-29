"""Full solitaire ring assembly: band + stone reference + prongs + basket."""

from __future__ import annotations

import time

import cadquery as cq

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.components.band import build_ring_band
from jewelmind.geometry.components.basket import build_basket_support
from jewelmind.geometry.components.prongs import build_prongs
from jewelmind.geometry.components.stone import build_stone_reference
from jewelmind.geometry.constants import GENERATOR_VERSION
from jewelmind.geometry.model import BoundingBox, GeneratedComponent, GeneratedModel
from jewelmind.utils.hashing import definition_hash


def _fuse_metal(band: GeneratedComponent, prongs: GeneratedComponent, basket: GeneratedComponent):
    """Fuse band + prongs + basket into one solid metal body.

    Falls back to an unfused compound (with a warning) if the boolean fuse
    fails for any reason — the individual solids are still valid and
    exportable even if OpenCascade cannot merge them into a single solid.
    """

    warnings: list[str] = []
    try:
        fused = band.shape.fuse(basket.shape)
        fused = fused.fuse(prongs.shape)
        if not fused.Solids():
            raise ValueError("fuse produced no solids")
        return fused, warnings
    except Exception as exc:  # noqa: BLE001 - OCC boolean failures vary widely
        warnings.append(
            f"Combined metal union failed ({exc}); exporting band, prongs, and "
            "basket as a multi-solid compound instead of a single fused solid."
        )
        compound = cq.Compound.makeCompound([band.shape, basket.shape, prongs.shape])
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
    prongs = build_prongs(definition)
    basket = build_basket_support(definition)

    combined_metal, fuse_warnings = _fuse_metal(band, prongs, basket)
    combined_metal_volume = combined_metal.Volume()

    metal_bbox = BoundingBox.from_shape(combined_metal)
    full_bbox = metal_bbox.union(stone.bounding_box)

    warnings = [
        *band.warnings,
        *stone.warnings,
        *prongs.warnings,
        *basket.warnings,
        *fuse_warnings,
    ]

    duration = time.perf_counter() - start

    return GeneratedModel(
        definition_hash=definition_hash(definition),
        generator_version=GENERATOR_VERSION,
        generation_duration_s=duration,
        components={
            "band": band,
            "stone_reference": stone,
            "prongs": prongs,
            "basket_support": basket,
        },
        combined_metal=combined_metal,
        combined_metal_volume_mm3=combined_metal_volume,
        bounding_box=full_bbox,
        warnings=warnings,
    )
