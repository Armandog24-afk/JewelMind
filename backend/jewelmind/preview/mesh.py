"""Preview mesh generation: one binary STL per named component.

GLB packaging was evaluated and intentionally not used in this milestone —
see docs/known-limitations.md for why. Instead each component (band,
stone_reference, prongs, basket_support) is tessellated and written as its
own binary STL file, and a small JSON manifest ties them together with
vertex/triangle counts and per-component bounding boxes. The frontend loads
these STL files directly (three.js ships an STL loader), which keeps the
preview pipeline entirely dependent on real backend-generated geometry.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.model import GeneratedModel
from jewelmind.geometry.roles import geometry_role as _geometry_role
from jewelmind.geometry.roles import production_role as _production_role

# The role mapping itself now lives in jewelmind.geometry.roles (Sprint 14
# — Geometry Inspection v2 needed the same mapping and a second private
# copy here would have drifted). See docs/bible/07-atlas/130-component-contract.md.


def _component_filename(name: str) -> str:
    return f"{name}.stl"


def write_component_previews(
    model: GeneratedModel,
    definition: JewelryDefinition,
    out_dir: Path,
) -> dict[str, dict[str, Any]]:
    """Write one STL file per component into `out_dir` and return a manifest."""

    out_dir.mkdir(parents=True, exist_ok=True)
    tolerance = definition.preview.meshTolerance
    angular = definition.preview.angularTolerance

    manifest: dict[str, dict[str, Any]] = {}
    for name, component in model.components.items():
        filename = _component_filename(name)
        path = out_dir / filename

        has_geometry = bool(component.shape.Solids())
        if has_geometry:
            component.shape.exportStl(str(path), tolerance=tolerance, angularTolerance=angular)
            vertices, triangles = component.shape.tessellate(tolerance, angular)
            vertex_count = len(vertices)
            triangle_count = len(triangles)
        else:
            # Nothing to tessellate (e.g. zero generated prongs); still emit
            # a manifest entry so the frontend can show "no geometry"
            # instead of a missing/broken entry.
            vertex_count = 0
            triangle_count = 0

        manifest[name] = {
            "file": filename if has_geometry else None,
            "vertexCount": vertex_count,
            "triangleCount": triangle_count,
            "volumeMm3": component.volume_mm3,
            "boundingBox": component.bounding_box.as_dict(),
            "warnings": component.warnings,
            # Additive metadata for Vision (Sprint 8): explicit component
            # identity so the frontend never has to infer role from name
            # string-matching. See docs/bible/10-vision/223-atlas-to-vision-contract.md.
            # Sprint 22: resolved through the role FUNCTIONS rather than by a
            # dict lookup with a default, so an instance-suffixed stone
            # component (`stone_reference.<instanceId>`) is classified as a
            # stone reference instead of falling through to production metal.
            "geometryRole": _geometry_role(name),
            "productionRole": _production_role(name),
            "meshSource": "stl",
            "generationStatus": "SUCCEEDED" if has_geometry else "EMPTY",
        }

    return manifest
