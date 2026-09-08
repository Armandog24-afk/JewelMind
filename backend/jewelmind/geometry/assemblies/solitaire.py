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

from jewelmind.arrangement.compile import compile_arrangement
from jewelmind.domain.schema import JewelryDefinition
from jewelmind.family.effective import effective_arrangement
from jewelmind.geometry.components.band import build_ring_band
from jewelmind.geometry.components.basket import build_basket_support
from jewelmind.geometry.components.stone import build_stone_reference
from jewelmind.geometry.constants import GENERATOR_VERSION
from jewelmind.geometry.model import BoundingBox, GeneratedComponent, GeneratedModel
from jewelmind.geometry.pave_adapter import (
    apply_pave_recess,
    resolve_pave_surface,
    retention_component,
)
from jewelmind.geometry.setting_adapter import setting_definition_from_jdl
from jewelmind.geometry.stone.placement import stone_components
from jewelmind.pave.compile import compose_pave
from jewelmind.setting.dispatch import generate_setting
from jewelmind.setting.head import HEAD_COMPONENT
from jewelmind.setting.retention import PAVE_RETENTION_COMPONENT
from jewelmind.utils.hashing import definition_hash, geometry_hash


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

    # THE EFFECTIVE ARRANGEMENT (Sprint 24). A family compiles into one; a
    # document may also declare one directly. Both routes end here, so there is
    # exactly one placement authority and a family can never disagree with it.
    # THE EFFECTIVE PLACEMENT, in one place (Sprint 26). A family or an
    # explicit arrangement, plus a halo, plus a pavé field — all composed
    # before anything is resolved, so there is exactly one placement authority.
    #
    # The pavé is composed HERE rather than inside `effective_arrangement()`
    # because it needs a resolved host surface, and resolving one means
    # measuring a band. `jewelmind.family` must not import a geometry module,
    # so the category-aware half of the composition belongs on this side of the
    # boundary.
    placement = effective_arrangement(definition)
    pave = definition.pave
    pave_surface = (
        resolve_pave_surface(definition, pave) if pave is not None else None
    )
    placement, pave_field = compose_pave(placement, pave, pave_surface)
    arrangement_result = compile_arrangement(placement)

    setting_definition = setting_definition_from_jdl(definition, stone)
    # The stone SHAPE is passed as an argument, never stored on the setting
    # contract, and only so seat relief can cut against the real generated
    # stone. `SettingDefinition` stays kernel-neutral (Sprint 23).
    setting_components, setting_result = generate_setting(
        setting_definition, stone_shape=stone.shape
    )

    # The head comes from the Setting System when the setting built one, and
    # from the Ring-side re-export otherwise. Both call the same builder; this
    # avoids constructing it twice for the same design.
    basket = setting_components.pop(HEAD_COMPONENT, None) or build_basket_support(
        definition
    )

    # PAVÉ METAL (Sprint 26). Real solids: beads or micro-prongs, each fused
    # into the production body. Built before the fuse so it participates in it,
    # which is what makes retention part of the metal rather than a separate
    # object resting on it.
    pave_retention = retention_component(pave, pave_field) if pave else None

    # Fuse order preserved from pre-Sprint-19: band, basket, then setting.
    setting_metal = [
        setting_components[name]
        for name in setting_result.productionComponents
        if name in setting_components
    ]
    # THE PAVÉ RECESS, applied to the host BEFORE the fuse and before the
    # retention is added, so the cut removes host metal rather than bead metal.
    # A cut, never a fuse: it routes through `setting/seat.py` (LAW-006).
    pave_recess_warnings: list[str] = []
    if pave is not None and pave_field is not None and pave_field.enabled:
        stone_shapes = [
            component.shape
            for name, component in stone_components(
                stone, arrangement_result
            ).items()
            if name != "stone_reference"
        ]
        hosts = {"band": band, "basket_support": basket}
        host = hosts.get(pave_field.hostComponent)
        if host is not None:
            relieved, pave_recess_warnings = apply_pave_recess(
                host, pave, stone_shapes
            )
            if pave_field.hostComponent == "band":
                band = relieved
            else:
                basket = relieved

    metal_parts = [band, basket, *setting_metal]
    if pave_retention is not None:
        metal_parts.append(pave_retention)
    combined_metal, fuse_warnings = _fuse_metal(metal_parts)
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
    warnings.extend(pave_recess_warnings)
    if pave_retention is not None:
        warnings.extend(pave_retention.warnings)

    components: dict[str, GeneratedComponent] = {"band": band}

    # STONE COMPONENTS, one per generated instance (Sprint 24).
    #
    # With no arrangement there is exactly one: the historical
    # `stone_reference`, returned by the identity placement path so its solid is
    # the same object the builder produced. With an arrangement or a family,
    # each generated instance gets its own placed copy, named for the instance
    # it came from.
    for name, component in stone_components(stone, arrangement_result).items():
        components[name] = component

    components.update(setting_components)
    components["basket_support"] = basket

    # ONE COMPONENT FOR THE WHOLE RETENTION FIELD, never one per bead: sixty
    # named components would give Geometry Inspection an intersection matrix
    # that grows with the stone count, and every anchor's own id and the stones
    # it serves are carried in this component's metadata instead.
    if pave_retention is not None:
        components[PAVE_RETENTION_COMPONENT] = pave_retention

    duration = time.perf_counter() - start

    return GeneratedModel(
        definition_hash=definition_hash(definition),
        geometry_hash=geometry_hash(definition),
        generator_version=GENERATOR_VERSION,
        generation_duration_s=duration,
        components=components,
        combined_metal=combined_metal,
        combined_metal_volume_mm3=combined_metal_volume,
        bounding_box=full_bbox,
        warnings=warnings,
        setting_result=setting_result,
        # Sprint 22, extended in Sprint 24 to cover a compiled family. Carried
        # on the model so the arrangement outcome travels with the geometry it
        # describes, exactly like `setting_result`. `None` in, `None` out: a
        # design with neither a family nor an arrangement is unchanged.
        arrangement_result=arrangement_result,
        # Sprint 26. Carried on the model beside the setting and arrangement
        # results, so the pavé outcome — its stone count, its retention
        # topology, its clipped cells and what it did NOT build — travels with
        # the geometry it describes.
        pave_result=pave_field,
    )
