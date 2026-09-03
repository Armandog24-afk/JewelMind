"""Deterministic hashing of a canonical JewelryDefinition.

The hash is used as a stable model identity: the same input definition must
always produce the same hash, and (barring a generator version change) the
same geometry.
"""

from __future__ import annotations

import hashlib
import json

from jewelmind.domain.schema import JewelryDefinition


def canonical_json(definition: JewelryDefinition) -> str:
    """Serialize a definition to a canonical (sorted-key, stable) JSON string."""

    data = definition.model_dump(mode="json")
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def definition_hash(definition: JewelryDefinition) -> str:
    """Return a short deterministic hex digest identifying this definition."""

    payload = canonical_json(definition).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


#: Fields that provably do NOT drive Atlas geometry, and are therefore excluded
#: from `geometry_hash()`.
#:
#: Every entry here is an EMPIRICAL claim, not an assumption, and
#: `test_gem_identity.py::TestGeometryIdentitySeparation` verifies it by
#: actually generating geometry with each varied and requiring identical
#: volumes and bounding boxes. If a future change makes one of these drive
#: geometry, that test fails rather than the cache silently going stale.
#:
#: - `stone.gem`      Sprint 21 gem identity. A round stone's geometry is the
#:                    same whether it is a diamond or a sapphire.
#: - `material`       Documented metadata-only since Sprint 2 (CLAUDE.md's
#:                    jewelry-domain rules).
#: - `manufacturing`  Documented metadata-only since Sprint 2.
#: - `project`        A name and a unit label.
#: - `preview`        Mesh tolerances affect TESSELLATION, never the B-Rep the
#:                    exporters and Golden snapshots measure.
_NON_GEOMETRY_PATHS: tuple[tuple[str, ...], ...] = (
    ("stone", "gem"),
    ("material",),
    ("manufacturing",),
    ("project",),
    ("preview",),
)


def _without(data: dict, path: tuple[str, ...]) -> None:
    """Delete a nested key in place, tolerating an absent path."""

    cursor: object = data
    for key in path[:-1]:
        if not isinstance(cursor, dict) or key not in cursor:
            return
        cursor = cursor[key]
    if isinstance(cursor, dict):
        cursor.pop(path[-1], None)


def geometry_canonical_json(definition: JewelryDefinition) -> str:
    """Canonical JSON of only the geometry-driving part of a definition."""

    data = definition.model_dump(mode="json")
    for path in _NON_GEOMETRY_PATHS:
        _without(data, path)
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def geometry_hash(definition: JewelryDefinition) -> str:
    """Identity of a definition's GEOMETRY, independent of its semantics.

    WHY THIS EXISTS (Sprint 21, brief section 19). `definition_hash()` identifies
    the whole document, so changing Diamond -> Sapphire changes it — correctly,
    because the document did change. But the geometry did not, and regenerating
    Atlas geometry for a semantic edit is wasted work.

    `geometry_hash()` is the key under which built geometry may be REUSED. It
    deliberately does not replace `definition_hash()`, which remains the model's
    public identity: two designs differing only by gem are genuinely two
    designs, and collapsing them would lose the distinction Foundry, the
    technical specification and Vision all need.

    What a gem change MAY still invalidate: the visual material, the
    presentation render, technical metadata, and any output that contains gem
    identity. What it must not invalidate is the B-Rep.
    """

    payload = geometry_canonical_json(definition).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]
