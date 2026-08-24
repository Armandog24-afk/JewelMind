"""STEP export.

Exports real CadQuery/OpenCascade solids to a STEP file in millimeters.
The stone reference is excluded by default (it is a simplified geometric
reference, not metal geometry) and may be included via `include_stone`.
"""

from __future__ import annotations

from pathlib import Path

from jewelmind.exporters.selection import select_export_shapes
from jewelmind.geometry.model import GeneratedModel


def export_step(model: GeneratedModel, destination: Path, *, include_stone: bool = False) -> Path:
    shape = select_export_shapes(model, include_stone=include_stone)
    shape.exportStep(str(destination))
    return destination
