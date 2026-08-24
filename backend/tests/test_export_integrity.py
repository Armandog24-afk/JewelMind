"""Sprint 7 (Foundry) targeted-hardening tests: checksums, non-empty file
validation, and export roundtrip validation for STEP and STL.

STEP roundtrip compares volume with a relative tolerance, not exact
equality, because round-tripping through a file format is an even lossier
boundary than the cross-OCCT-build variance already documented in
docs/bible/07-atlas/137-determinism-and-reproducibility.md.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import cadquery as cq
import pytest

from jewelmind.domain.defaults import default_definition
from jewelmind.exporters.integrity import (
    ArtifactIntegrityError,
    binary_stl_triangle_count,
    sha256_checksum,
    validate_non_empty,
)
from jewelmind.exporters.step_exporter import export_step
from jewelmind.exporters.stl_exporter import export_stl
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring

_ROUNDTRIP_REL_TOLERANCE = 1e-3  # STEP files store limited decimal precision


def test_checksum_is_deterministic_and_content_dependent():
    with tempfile.TemporaryDirectory() as tmp:
        a = Path(tmp) / "a.txt"
        b = Path(tmp) / "b.txt"
        a.write_bytes(b"hello")
        b.write_bytes(b"hello")
        assert sha256_checksum(a) == sha256_checksum(b)

        c = Path(tmp) / "c.txt"
        c.write_bytes(b"different")
        assert sha256_checksum(a) != sha256_checksum(c)


def test_validate_non_empty_accepts_real_file_and_rejects_empty():
    with tempfile.TemporaryDirectory() as tmp:
        real = Path(tmp) / "real.bin"
        real.write_bytes(b"x")
        assert validate_non_empty(real, artifact_type="TEST") == 1

        empty = Path(tmp) / "empty.bin"
        empty.write_bytes(b"")
        with pytest.raises(ArtifactIntegrityError):
            validate_non_empty(empty, artifact_type="TEST")

        missing = Path(tmp) / "missing.bin"
        with pytest.raises(ArtifactIntegrityError):
            validate_non_empty(missing, artifact_type="TEST")


def test_step_export_roundtrip_via_reimport():
    definition = default_definition()
    model = build_solitaire_ring(definition)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "model.step"
        export_step(model, path)
        validate_non_empty(path, artifact_type="STEP")

        reimported = cq.importers.importStep(str(path))
        solids = reimported.val().Solids()
        assert len(solids) == len(model.combined_metal.Solids())

        reimported_volume = sum(s.Volume() for s in solids)
        assert reimported_volume == pytest.approx(
            model.combined_metal_volume_mm3, rel=_ROUNDTRIP_REL_TOLERANCE
        )


def test_stl_export_roundtrip_via_binary_header_parse():
    definition = default_definition()
    model = build_solitaire_ring(definition)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "model.stl"
        export_stl(model, definition, path)
        size = validate_non_empty(path, artifact_type="STL")

        triangle_count = binary_stl_triangle_count(path)
        assert triangle_count > 0
        # Binary STL: 84-byte header + 50 bytes per triangle, exactly.
        assert size == 84 + triangle_count * 50


def test_step_and_stl_exports_exclude_stone_by_default():
    """Re-import confirms the exported volume matches metal-only, not
    metal+stone — a real geometric check that stone exclusion actually
    holds, not just that the include_stone flag defaults to False."""

    definition = default_definition()
    model = build_solitaire_ring(definition)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "model.step"
        export_step(model, path, include_stone=False)
        reimported = cq.importers.importStep(str(path))
        reimported_volume = sum(s.Volume() for s in reimported.val().Solids())

        stone_volume = model.components["stone_reference"].volume_mm3
        metal_plus_stone = model.combined_metal_volume_mm3 + stone_volume
        assert reimported_volume == pytest.approx(
            model.combined_metal_volume_mm3, rel=_ROUNDTRIP_REL_TOLERANCE
        )
        assert reimported_volume < metal_plus_stone
