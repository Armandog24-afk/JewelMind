"""Artifact regression checks — STEP/STL, but never byte-for-byte
(QUALITY-GOV-007/008). See
docs/bible/17-geometry-quality/509-artifact-regression-model.md.

STEP is validated by export -> re-import -> inspect -> compare geometric
facts, never a checksum, because CadQuery's STEP writer embeds variable
OpenCascade metadata (a generation timestamp/GUID/product-definition
counters) that makes two exports of identical geometry byte-different.
STL, in contrast, is a pure triangulation with no such metadata, so a
checksum is recorded as *supplemental* evidence alongside the primary
structural check — never the other way around.
"""

from __future__ import annotations

import struct
import tempfile
from pathlib import Path

import cadquery as cq

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.exporters.integrity import binary_stl_triangle_count
from jewelmind.exporters.step_exporter import export_step
from jewelmind.exporters.stl_exporter import export_stl
from jewelmind.geometry.inspection.shape import bounding_box_fact
from jewelmind.geometry.model import GeneratedModel
from jewelmind.geometry_quality.models import ArtifactChange
from jewelmind.geometry_quality.version import (
    ABSOLUTE_COMPARISON_TOLERANCE_MM,
    RELATIVE_COMPARISON_TOLERANCE,
)


def _numeric_close(expected: float, actual: float) -> bool:
    delta = abs(actual - expected)
    if delta <= ABSOLUTE_COMPARISON_TOLERANCE_MM:
        return True
    return expected != 0 and delta / abs(expected) <= RELATIVE_COMPARISON_TOLERANCE


def step_roundtrip_check(model: GeneratedModel) -> list[ArtifactChange]:
    """Export STEP (production metal only), re-import, and compare solid
    count / volume / bounding box against the source shape that was
    exported — never against raw bytes."""

    changes: list[ArtifactChange] = []
    with tempfile.TemporaryDirectory() as tmp:
        destination = Path(tmp) / "roundtrip.step"
        export_step(model, destination, include_stone=False)

        reimported = cq.importers.importStep(str(destination))
        shape = reimported.val()
        solids = shape.Solids()
        if not solids:
            changes.append(
                ArtifactChange(artifactType="STEP", description="Re-imported STEP contains no solids.")
            )
            return changes

        source_solid_count = len(model.combined_metal.Solids())
        reimported_solid_count = len(solids)
        if source_solid_count != reimported_solid_count:
            changes.append(
                ArtifactChange(
                    artifactType="STEP",
                    description=(
                        f"Solid count changed on roundtrip: source={source_solid_count}, "
                        f"reimported={reimported_solid_count}."
                    ),
                )
            )

        source_volume = model.combined_metal_volume_mm3
        reimported_volume = shape.Volume()
        if not _numeric_close(source_volume, reimported_volume):
            changes.append(
                ArtifactChange(
                    artifactType="STEP",
                    description=(
                        f"Volume changed on roundtrip beyond tolerance: source={source_volume}, "
                        f"reimported={reimported_volume}."
                    ),
                )
            )

        source_bbox = bounding_box_fact(model.combined_metal)
        reimported_bbox = bounding_box_fact(shape)
        for field in ("sizeX", "sizeY", "sizeZ"):
            e, a = getattr(source_bbox, field), getattr(reimported_bbox, field)
            if not _numeric_close(e, a):
                changes.append(
                    ArtifactChange(
                        artifactType="STEP",
                        description=f"Bounding box {field} changed on roundtrip: source={e}, reimported={a}.",
                    )
                )
    return changes


def _binary_stl_bounding_box(path: Path) -> tuple[float, float, float, float, float, float]:
    """Full parse of a binary STL's triangle vertices for an approximate
    bounding box — no new dependency, mirrors
    exporters/integrity.py::binary_stl_triangle_count's header-only read."""

    with open(path, "rb") as f:
        header = f.read(84)
        (triangle_count,) = struct.unpack("<I", header[80:84])
        xs: list[float] = []
        ys: list[float] = []
        zs: list[float] = []
        for _ in range(triangle_count):
            record = f.read(50)
            if len(record) < 50:
                break
            # normal (3 floats) + 3 vertices (3 floats each) = 12 floats.
            floats = struct.unpack("<12f", record[:48])
            for i in range(3, 12, 3):
                xs.append(floats[i])
                ys.append(floats[i + 1])
                zs.append(floats[i + 2])
    if not xs:
        return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def stl_structure_check(model: GeneratedModel, definition: JewelryDefinition) -> list[ArtifactChange]:
    """Export STL (production metal only) and validate structural facts —
    never mesh volume, which no reliable tooling in this repo computes."""

    changes: list[ArtifactChange] = []
    with tempfile.TemporaryDirectory() as tmp:
        destination = Path(tmp) / "structure.stl"
        export_stl(model, definition, destination, include_stone=False)

        size = destination.stat().st_size
        if size == 0:
            changes.append(
                ArtifactChange(artifactType="STL", description="STL export produced an empty file.")
            )
            return changes

        triangle_count = binary_stl_triangle_count(destination)
        if triangle_count <= 0:
            changes.append(
                ArtifactChange(artifactType="STL", description="STL export contains zero triangles.")
            )
            return changes

        xmin, xmax, ymin, ymax, zmin, zmax = _binary_stl_bounding_box(destination)
        source_bbox = model.bounding_box
        # Mesh tessellation can slightly under/overshoot the exact B-Rep
        # bounding box; allow one order of magnitude more slack than the
        # standard numeric tolerance for this comparison only.
        loose_tolerance_mm = ABSOLUTE_COMPARISON_TOLERANCE_MM * 100
        for label, mesh_val, brep_min, brep_max in (
            ("x", (xmin, xmax), source_bbox.xmin, source_bbox.xmax),
            ("y", (ymin, ymax), source_bbox.ymin, source_bbox.ymax),
            ("z", (zmin, zmax), source_bbox.zmin, source_bbox.zmax),
        ):
            lower_bound = brep_min - loose_tolerance_mm - 1.0
            upper_bound = brep_max + loose_tolerance_mm + 1.0
            if mesh_val[0] < lower_bound or mesh_val[1] > upper_bound:
                changes.append(
                    ArtifactChange(
                        artifactType="STL",
                        description=(
                            f"Mesh {label} extent {mesh_val} is inconsistent with source bounding box "
                            f"[{brep_min}, {brep_max}]."
                        ),
                    )
                )
    return changes
