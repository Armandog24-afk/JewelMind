"""STEP export.

Exports real CadQuery/OpenCascade solids to a STEP file in millimeters.
The stone reference is excluded by default (it is a simplified geometric
reference, not metal geometry) and may be included via `include_stone`.
"""

from __future__ import annotations

from pathlib import Path

import cadquery as cq

from jewelmind.geometry.model import GeneratedModel


def export_step(model: GeneratedModel, destination: Path, *, include_stone: bool = False) -> Path:
    shapes = [model.combined_metal]
    if include_stone:
        shapes.append(model.components["stone_reference"].shape)

    shape = shapes[0] if len(shapes) == 1 else cq.Compound.makeCompound(shapes)
    shape.exportStep(str(destination))
    return destination
