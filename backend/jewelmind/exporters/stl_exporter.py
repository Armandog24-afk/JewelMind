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

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.exporters.selection import select_export_shapes
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

    shape = select_export_shapes(model, include_stone=include_stone)
    shape.exportStl(str(destination), tolerance=tolerance, angularTolerance=angular)
    return destination
