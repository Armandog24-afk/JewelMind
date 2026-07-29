"""STL export.

Exports a real triangulated mesh of the combined metal geometry (band +
prongs + basket, fused when possible). The stone reference is excluded by
default, matching the STEP exporter. Mesh tolerance is configurable; it
defaults to the definition's own `preview.meshTolerance` /
`preview.angularTolerance` so the exported mesh matches what was previewed.

If the combined metal geometry could not be fused into a single solid (see
jewelmind.geometry.assemblies.solitaire), this still works: exportStl
accepts multi-solid compounds and writes every solid into one STL file, so
no component is silently dropped.
"""

from __future__ import annotations

from pathlib import Path

import cadquery as cq

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.model import GeneratedModel


def export_stl(
    model: GeneratedModel,
    definition: JewelryDefinition,
    destination: Path,
    *,
    include_stone: bool = False,
    mesh_tolerance: float | None = None,
    angular_tolerance: float | None = None,
) -> Path:
    tolerance = mesh_tolerance if mesh_tolerance is not None else definition.preview.meshTolerance
    angular = angular_tolerance if angular_tolerance is not None else definition.preview.angularTolerance

    shapes = [model.combined_metal]
    if include_stone:
        shapes.append(model.components["stone_reference"].shape)

    shape = shapes[0] if len(shapes) == 1 else cq.Compound.makeCompound(shapes)
    shape.exportStl(str(destination), tolerance=tolerance, angularTolerance=angular)
    return destination
