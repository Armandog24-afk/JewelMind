"""Imported stone geometry: asset store, format detection, normalization
(brief sections 30/31/32/50/51).

IMPORTED ASSETS ARE UNTRUSTED INPUT. Every safeguard here exists because a
stone file arrives from outside JewelMind:

- assets are addressed by CONTENT HASH, never by caller-supplied path, so no
  input can traverse the filesystem;
- the hash is validated as hexadecimal before it ever touches a path;
- file size, triangle count and face count are bounded before and after
  parsing;
- every parser exception is caught and re-raised as a structured JewelMind
  error whose message contains no stack trace, no library output and no
  server path (FOUNDRY-GOV-011);
- nothing in a stone file is ever executed. Only geometry is read.

FORMATS ARE DECLARED FROM WHAT THE INSTALLED KERNEL ACTUALLY DOES, verified by
running it rather than by reading documentation (brief section 30's "do not
claim support for formats the current importer cannot actually parse"):

    STEP  -> B-Rep solid   via cadquery.importers.importStep      CURRENT
    BREP  -> B-Rep solid   via cadquery.importers.importBrep      CURRENT
    STL   -> mesh          via OCP.RWStl                          CURRENT
    OBJ   -> unavailable: OCP.RWObj is not present in this build
    GLTF  -> unavailable: needs an XCAF document pipeline not wired here
    IGES  -> unavailable: no reader in this build

B-REP VERSUS MESH (brief section 32) is never papered over. A STEP import
yields a real solid with volume and usable boolean/section operations; an STL
import yields a triangulated face with no solid, no reliable volume, and no
B-Rep operations. `StoneRepresentation` records which one a caller got, and
`ImportedStoneGeometry.supportsBrepOperations` says plainly what it can do.
"""

from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from typing import Protocol

import cadquery as cq
from pydantic import BaseModel, ConfigDict

from jewelmind.stone.errors import (
    StoneImportEmptyError,
    StoneImportFailedError,
    StoneImportFormatUnsupportedError,
    StoneImportGeometryInvalidError,
    StoneImportTooComplexError,
)
from jewelmind.stone.models import UNIT_TO_MM, StoneRepresentation

#: Version of this normalization pipeline, recorded in provenance.
STONE_IMPORTER_VERSION = "1.0.0"

#: Largest asset accepted, in bytes. A resource safeguard for untrusted input,
#: not a geometric judgment — a single gemstone's CAD file is far below this.
MAX_ASSET_BYTES = 32 * 1024 * 1024

#: Upper bounds on parsed geometry complexity, enforced AFTER parsing because
#: a small compressed file can expand into a very large mesh.
MAX_MESH_TRIANGLES = 2_000_000
MAX_BREP_FACES = 100_000

#: Formats this build can genuinely read, and what each yields.
SUPPORTED_IMPORT_FORMATS: dict[str, StoneRepresentation] = {
    ".step": "BREP_SOLID",
    ".stp": "BREP_SOLID",
    ".brep": "BREP_SOLID",
    ".stl": "MESH",
}

#: Formats deliberately NOT claimed, with the real reason. Listed so a caller
#: gets an honest answer instead of a bare "unsupported".
UNSUPPORTED_IMPORT_FORMATS: dict[str, str] = {
    ".obj": "OCP.RWObj is not available in this build.",
    ".gltf": "No XCAF document pipeline is wired up to read it.",
    ".glb": "No XCAF document pipeline is wired up to read it.",
    ".iges": "No IGES reader is available in this build.",
    ".igs": "No IGES reader is available in this build.",
    ".3dm": "Rhino format; JewelMind never requires Rhino (LAW).",
}

_HEX_RE = re.compile(r"\A[0-9a-f]{8,128}\Z")


class ImportedStoneGeometry(BaseModel):
    """The kernel-neutral facts about one imported asset.

    `shape` deliberately holds the real `cadquery.Shape`, which is why this
    model lives in the Atlas-facing part of the Stone System and never crosses
    into a Forge contract (INSPECT-GOV-016/017).
    """

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    shape: object
    representation: StoneRepresentation
    supportsBrepOperations: bool
    solidCount: int
    faceCount: int
    triangleCount: int | None
    lengthMm: float
    widthMm: float
    depthMm: float
    volumeMm3: float | None
    assetHash: str
    assetName: str | None
    originalUnit: str
    normalizationOperations: list[str]
    importerVersion: str = STONE_IMPORTER_VERSION


class StoneAssetStore(Protocol):
    """Resolves a content hash to real bytes on disk.

    A protocol rather than a concrete class so tests, the API layer and a
    future object-storage backend can each supply their own, without the Stone
    System ever learning about filesystem layout.
    """

    def resolve(self, asset_hash: str) -> Path:  # pragma: no cover - protocol
        ...


class FilesystemStoneAssetStore:
    """Content-addressed asset store rooted at a single directory.

    The stored filename is `<hash><ext>`, so resolving never uses any
    caller-supplied string other than the validated hexadecimal hash. That is
    what makes path traversal structurally impossible rather than merely
    filtered.
    """

    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def store(self, data: bytes, suffix: str) -> str:
        """Write bytes under their own SHA-256 and return the hash."""

        # Rejected at STORE time, not only at import time. Accepting an asset
        # this build cannot read would let a caller believe an unsupported
        # format had been accepted, and would only fail later, further from the
        # cause. `detect_format` gives the honest per-format reason.
        suffix = suffix.lower()
        detect_format(Path(f"probe{suffix}"))
        if len(data) > MAX_ASSET_BYTES:
            raise StoneImportTooComplexError(
                f"Stone asset is {len(data)} bytes, above the "
                f"{MAX_ASSET_BYTES} byte limit."
            )
        digest = hashlib.sha256(data).hexdigest()
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / f"{digest}{suffix}").write_bytes(data)
        return digest

    def resolve(self, asset_hash: str) -> Path:
        if not _HEX_RE.match(asset_hash):
            raise StoneImportFailedError(
                "Stone asset identifier is not a valid content hash."
            )
        matches = sorted(self.root.glob(f"{asset_hash}.*"))
        if not matches:
            raise StoneImportFailedError(
                f"No stored stone asset matches identifier {asset_hash[:12]}..."
            )
        return matches[0]


def detect_format(path: Path) -> tuple[str, StoneRepresentation]:
    """Return `(suffix, representation)` for a supported asset."""

    suffix = path.suffix.lower()
    representation = SUPPORTED_IMPORT_FORMATS.get(suffix)
    if representation is not None:
        return suffix, representation

    reason = UNSUPPORTED_IMPORT_FORMATS.get(suffix)
    detail = f" {reason}" if reason else ""
    raise StoneImportFormatUnsupportedError(
        f"Stone asset format {suffix!r} is not supported.{detail} "
        f"Supported formats: {', '.join(sorted(SUPPORTED_IMPORT_FORMATS))}."
    )


def _read_brep(path: Path, suffix: str) -> cq.Shape:
    try:
        if suffix == ".brep":
            workplane = cq.importers.importBrep(str(path))
        else:
            workplane = cq.importers.importStep(str(path))
        return workplane.val()
    except Exception as exc:  # noqa: BLE001 - importer failures vary widely
        # Deliberately does not include `exc` in the message: importer output
        # can contain absolute server paths and library internals.
        raise StoneImportFailedError(
            "The stone asset could not be read as B-Rep geometry. It may be "
            "corrupt, truncated, or not the format its extension claims."
        ) from exc


def _read_mesh_triangulation(path: Path):
    """Read a triangulated mesh, returning the raw OCP triangulation.

    Imported through OCP's `RWStl` directly because CadQuery's own importer
    registry (`ImportTypes`: BIN, BREP, DXF, STEP) has no STL entry.
    """

    from OCP.RWStl import RWStl

    try:
        triangulation = RWStl.ReadFile_s(str(path))
    except Exception as exc:  # noqa: BLE001
        raise StoneImportFailedError(
            "The stone asset could not be read as a mesh. It may be corrupt, "
            "truncated, or not the format its extension claims."
        ) from exc

    if triangulation is None or triangulation.NbTriangles() == 0:
        raise StoneImportEmptyError("The stone mesh asset contains no triangles.")

    triangle_count = triangulation.NbTriangles()
    if triangle_count > MAX_MESH_TRIANGLES:
        raise StoneImportTooComplexError(
            f"Stone mesh has {triangle_count} triangles, above the "
            f"{MAX_MESH_TRIANGLES} limit."
        )
    return triangulation, triangle_count


def _transform_triangulation(
    triangulation,
    scale: float = 1.0,
    translate: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotate_deg: float = 0.0,
):
    """Apply scale, then rotation about Z, then translation to a mesh's NODES.

    A MESH MUST BE TRANSFORMED NODE BY NODE. This is not a stylistic choice:
    neither `cadquery.Shape.scale()` nor `BRepBuilderAPI_Transform` moves a
    triangulation attached to an otherwise-empty face. Measured during Sprint 20
    on a real 6x8x4mm STL: both returned a bounding box of exactly 6x8x4 after a
    requested 10x scale, while node-level scaling correctly produced 60x80x40.

    That made the bug worse than a wrong size. `normalizationOperations` recorded
    UNIT_CONVERSION:cm->mm for an STL whose geometry had not moved at all, so the
    provenance record asserted a conversion that never happened — and a false
    provenance entry is more damaging than a missing one.
    """

    from OCP.gp import gp_Pnt

    angle = math.radians(rotate_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)

    for index in range(1, triangulation.NbNodes() + 1):
        node = triangulation.Node(index)
        x, y, z = node.X() * scale, node.Y() * scale, node.Z() * scale
        if rotate_deg:
            x, y = x * cos_a - y * sin_a, x * sin_a + y * cos_a
        triangulation.SetNode(
            index, gp_Pnt(x + translate[0], y + translate[1], z + translate[2])
        )
    return triangulation


def _face_from_triangulation(triangulation) -> cq.Shape:
    """Wrap a triangulation in a `Face` that carries it.

    The result has real bounds and a real triangle count, and genuinely zero
    solids — which is exactly the honest representation of a mesh.
    """

    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Face

    face = TopoDS_Face()
    BRep_Builder().MakeFace(face, triangulation)
    return cq.Shape.cast(face)


def _mesh_bounds(triangulation):
    """Min/max corner of a triangulation, computed from its own nodes."""

    xs, ys, zs = [], [], []
    for index in range(1, triangulation.NbNodes() + 1):
        node = triangulation.Node(index)
        xs.append(node.X())
        ys.append(node.Y())
        zs.append(node.Z())
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def import_stone_asset(
    store: StoneAssetStore,
    asset_hash: str,
    declared_unit: str,
    asset_name: str | None = None,
    orientation_deg: float = 0.0,
) -> ImportedStoneGeometry:
    """Import, scale, recentre and inspect one stone asset.

    Normalization is explicit and recorded, never silent (brief section 31):
    the declared unit is converted to millimetres, the geometry is recentred on
    its own bounding-box centre so it lands in the canonical stone frame, and
    any requested orientation is applied. Each operation actually performed is
    appended to `normalizationOperations`.
    """

    if declared_unit not in UNIT_TO_MM:
        raise StoneImportFailedError(
            f"Declared unit {declared_unit!r} is not one of "
            f"{', '.join(sorted(UNIT_TO_MM))}."
        )

    path = store.resolve(asset_hash)
    size = path.stat().st_size
    if size == 0:
        raise StoneImportEmptyError("The stone asset file is empty.")
    if size > MAX_ASSET_BYTES:
        raise StoneImportTooComplexError(
            f"Stone asset is {size} bytes, above the {MAX_ASSET_BYTES} byte limit."
        )

    suffix, representation = detect_format(path)
    operations: list[str] = []
    triangle_count: int | None = None
    factor = UNIT_TO_MM[declared_unit]

    if representation == "MESH":
        triangulation, triangle_count = _read_mesh_triangulation(path)

        low, high = _mesh_bounds(triangulation)
        if not all(
            value == value and abs(value) != float("inf") for value in (*low, *high)
        ):
            raise StoneImportGeometryInvalidError(
                "The imported stone has non-finite bounds."
            )
        if min(high[i] - low[i] for i in range(3)) <= 0.0:
            raise StoneImportGeometryInvalidError(
                "The imported stone is degenerate: at least one dimension is zero."
            )

        # Scale, rotate and recentre in ONE node pass. The centre is measured in
        # the scaled frame and rotated with the geometry, so subtracting the
        # rotated centre lands the mesh on the origin.
        centre = tuple((low[i] + high[i]) / 2 * factor for i in range(3))
        if factor != 1.0:
            operations.append(f"UNIT_CONVERSION:{declared_unit}->mm")
        if orientation_deg:
            operations.append(f"ORIENTATION_APPLIED:{orientation_deg}deg")
        if any(abs(value) > 1e-9 for value in centre):
            operations.append(
                f"ORIGIN_RECENTERED:bbox_center"
                f"({centre[0]:.6f},{centre[1]:.6f},{centre[2]:.6f})"
            )

        angle = math.radians(orientation_deg)
        rotated_centre = (
            centre[0] * math.cos(angle) - centre[1] * math.sin(angle),
            centre[0] * math.sin(angle) + centre[1] * math.cos(angle),
            centre[2],
        )
        _transform_triangulation(
            triangulation,
            scale=factor,
            rotate_deg=orientation_deg,
            translate=(-rotated_centre[0], -rotated_centre[1], -rotated_centre[2]),
        )
        shape = _face_from_triangulation(triangulation)
        faces = shape.Faces()
    else:
        shape = _read_brep(path, suffix)
        faces = shape.Faces()
        if not faces:
            raise StoneImportEmptyError("The stone asset contains no geometry.")
        if len(faces) > MAX_BREP_FACES:
            raise StoneImportTooComplexError(
                f"Stone asset has {len(faces)} faces, above the "
                f"{MAX_BREP_FACES} limit."
            )

        if factor != 1.0:
            shape = shape.scale(factor)
            operations.append(f"UNIT_CONVERSION:{declared_unit}->mm")

        box = shape.BoundingBox()
        if not all(
            value == value and abs(value) != float("inf")
            for value in (box.xmin, box.xmax, box.ymin, box.ymax, box.zmin, box.zmax)
        ):
            raise StoneImportGeometryInvalidError(
                "The imported stone has non-finite bounds."
            )
        if min(box.xlen, box.ylen, box.zlen) <= 0.0:
            raise StoneImportGeometryInvalidError(
                "The imported stone is degenerate: at least one dimension is zero."
            )

        centre = (
            (box.xmin + box.xmax) / 2,
            (box.ymin + box.ymax) / 2,
            (box.zmin + box.zmax) / 2,
        )
        if any(abs(value) > 1e-9 for value in centre):
            shape = shape.translate((-centre[0], -centre[1], -centre[2]))
            operations.append(
                f"ORIGIN_RECENTERED:bbox_center"
                f"({centre[0]:.6f},{centre[1]:.6f},{centre[2]:.6f})"
            )

        if orientation_deg:
            shape = shape.rotate((0, 0, 0), (0, 0, 1), orientation_deg)
            operations.append(f"ORIENTATION_APPLIED:{orientation_deg}deg")

    if not faces:
        raise StoneImportEmptyError("The stone asset contains no geometry.")

    solids = shape.Solids()
    volume: float | None = None
    if solids:
        try:
            volume = shape.Volume()
        except Exception:  # noqa: BLE001 - a malformed solid may refuse to measure
            volume = None

    final_box = shape.BoundingBox()
    return ImportedStoneGeometry(
        shape=shape,
        representation=representation,
        # A mesh genuinely cannot support the B-Rep operations a setting needs.
        # Reported from the real parsed result, never from the file extension.
        supportsBrepOperations=representation == "BREP_SOLID" and bool(solids),
        solidCount=len(solids),
        faceCount=len(faces),
        triangleCount=triangle_count,
        lengthMm=final_box.ylen,
        widthMm=final_box.xlen,
        depthMm=final_box.zlen,
        volumeMm3=volume,
        assetHash=asset_hash,
        assetName=asset_name,
        originalUnit=declared_unit,
        normalizationOperations=operations,
    )
