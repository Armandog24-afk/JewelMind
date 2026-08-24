"""Shared production-shape selection for STEP/STL export.

Extracted from step_exporter.py and stl_exporter.py (Sprint 7), which
previously duplicated this exact logic. Behavior is unchanged — this is a
pure extraction, not a new policy. See docs/bible/09-foundry/196-production-geometry-selection.md.
"""

from __future__ import annotations

import cadquery as cq

from jewelmind.geometry.model import GeneratedModel


def select_export_shapes(model: GeneratedModel, *, include_stone: bool) -> cq.Shape:
    """Return the shape to export: combined production metal, optionally
    plus the stone reference as a non-fused compound member.

    `stone_reference` is never fused into `combined_metal` here or anywhere
    else — see LAW-006. This function only ever adds it as a separate
    member of an export-only compound when explicitly requested.
    """

    shapes = [model.combined_metal]
    if include_stone:
        shapes.append(model.components["stone_reference"].shape)

    return shapes[0] if len(shapes) == 1 else cq.Compound.makeCompound(shapes)
