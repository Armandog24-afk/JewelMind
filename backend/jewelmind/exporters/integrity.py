"""Artifact integrity helpers: checksums and minimum file-validity checks.

Added in Sprint 7 (Foundry Export System v1) as targeted hardening — see
docs/bible/09-foundry/202-artifact-integrity-model.md. Every exporter
already only ever writes a real, complete file in one shot (no streaming/
partial-write path exists), so `validate_non_empty` is expected to always
pass; it exists to make FOUNDRY-GOV-008 an enforced invariant rather than
an unverified assumption, and to fail loudly (not silently return an
empty/corrupt file as a success) if that ever stops being true.
"""

from __future__ import annotations

import hashlib
import struct
from pathlib import Path

from jewelmind.api.errors import AppError


class ArtifactIntegrityError(AppError):
    """Raised when a generated artifact file fails a basic integrity check."""

    status_code = 500
    code = "FOUNDRY_INTEGRITY_FAILED"


def sha256_checksum(path: Path) -> str:
    """Return the hex-encoded SHA-256 checksum of the file at `path`."""

    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_non_empty(path: Path, *, artifact_type: str) -> int:
    """Raise ArtifactIntegrityError if `path` does not exist or is empty.

    Returns the file's byte size on success.
    """

    if not path.exists():
        raise ArtifactIntegrityError(f"{artifact_type} export produced no file at {path.name}.")
    size = path.stat().st_size
    if size == 0:
        raise ArtifactIntegrityError(f"{artifact_type} export produced an empty file ({path.name}).")
    return size


def binary_stl_triangle_count(path: Path) -> int:
    """Read a binary STL file's declared triangle count without a full parse.

    Binary STL layout: an 80-byte header, then a little-endian uint32
    triangle count, then 50 bytes per triangle (12 floats + a 2-byte
    attribute count). This reads only the first 84 bytes — no full-file
    parse and no new dependency (CadQuery's own STL export is always
    binary, confirmed by inspection during Sprint 7).
    """

    with open(path, "rb") as f:
        header = f.read(84)
    if len(header) < 84:
        raise ArtifactIntegrityError(f"STL file too small to contain a valid header: {path.name}.")
    (triangle_count,) = struct.unpack("<I", header[80:84])
    return triangle_count
