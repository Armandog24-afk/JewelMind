"""Pavé semantics -> arrangement primitives (Sprint 26).

THE ONLY TRANSFORMATION IN THIS LAYER, and it deliberately produces an
`ArrangementDefinition` rather than positions of its own. Stone Arrangement
Engine v1 remains the sole authority on placement: this module chooses which
arrangement primitives express a field, and the arrangement resolver then does
the arithmetic exactly as it does for a hand-written arrangement.

A PAVÉ COMPOSES, it does not replace — the same contract Sprint 25 established
for the halo. `compose_pave()` takes whatever placement the design already
declares and returns that same structure with the field's stones added, so
"solitaire with a pavé shank" and "three-stone with a pavé shank" are one design
each rather than a choice between two.

WHY THE LATTICE IS PLACED EXPLICITLY rather than through a pattern. A pattern's
generated members inherit their SOURCE instance's overrides, and the only
instance at a field's origin is the centre stone, whose scale is its own —
Sprint 24 shipped that defect once and Sprint 25 documented it. A pavé stone is
one to two orders of magnitude smaller than a centre stone, so inheriting its
scale would produce a field of full-size stones. The angular sequence still
comes from `arrangement/radial.py`, the same function the resolver uses to
expand a `RADIAL` pattern, so a pavé ring and a hand-written one agree.

REJECTS, NEVER REPAIRS. An unsupported host, an unresolvable host, an empty
field, an over-capacity field, an id collision or a field that does not fit
under a strict containment policy raises. Inventing a plausible lattice would
produce a design nobody authored.

KERNEL-FREE. Nothing here imports CadQuery, any geometry module, or any jewelry
category. The output is arrangement data plus plain numbers.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from functools import lru_cache

from pydantic import Field

from jewelmind.arrangement.models import (
    MAX_INSTANCES,
    ArrangementDefinition,
    ArrangementRelation,
    InstanceOverrides,
    InstancePlacement,
    InstanceTransform,
    StoneInstanceDef,
)
from jewelmind.arrangement.radial import ring_angles_deg
from jewelmind.gem.models import GemIdentity
from jewelmind.pave.errors import (
    PaveCapacityExceededError,
    PaveContainmentError,
    PaveFieldEmptyError,
    PaveIdentityCollisionError,
)
from jewelmind.pave.models import (
    DESIGN_CENTER_INSTANCE_ID,
    MAX_PAVE_STONES,
    SHARED_RETENTION_STRATEGIES,
    MicrosettingSpec,
    PaveDefinition,
    PaveModel,
    PaveSpec,
)
from jewelmind.pave.surface import ResolvedHostSurface

#: The role every pavé stone carries. `PAVE` is distinct from `ACCENT` and
#: `HALO` for the reason those are distinct from each other: it lets a consumer
#: ask "what is set into this surface?" without inspecting coordinates.
#: `StoneRole` has carried `PAVE` since Sprint 21.
PAVE_ROLE = "PAVE"

#: Below this a lattice cell is treated as coincident with another. Not a
#: jewelry clearance: it exists so a shared bead lattice does not emit two
#: beads at what is arithmetically one point.
_COINCIDENT_EPSILON_MM = 1e-9

#: How far an INDIVIDUAL bead sits from its stone's centre, as a fraction of
#: the half-pitch.
#:
#: A CONSTRUCTION PARAMETER, and it exists because of a real finding rather
#: than a preference. Placed at the full half-pitch, an individual bead lands
#: exactly on the lattice corner its neighbours also use — so four coincident
#: spheres fuse into one and `BEAD` produced metal identical to
#: `SHARED_BEAD` while reporting four times the pieces. Reporting a technique
#: the metal does not implement is precisely what this project refuses, so an
#: individual bead is drawn IN toward its own stone and is genuinely its own
#: solid. Nothing here claims 0.75 is a setter's proportion; it is a
#: deterministic construction choice, verified only to produce distinct solids.
_INDIVIDUAL_BEAD_INSET_FRACTION = 0.75


class PaveStonePlacement(PaveModel):
    """One stone of the field, with its lattice provenance.

    `rowIndex`/`columnIndex` are carried rather than recomputed so every
    generated solid is traceable to the cell that produced it (§11, §13). They
    are provenance, never identity: `placementId` is the identity.
    """

    placementId: str
    rowIndex: int
    columnIndex: int
    transform: InstanceTransform
    scale: float
    gem: GemIdentity | None = None


class PaveRetentionAnchor(PaveModel):
    """One point where retention metal is placed, and what it serves.

    `servesPlacementIds` is what makes a SHARED bead honest: a shared bead
    names every stone it touches, so "shared" is a checkable statement about
    the topology rather than a label on a smaller number of beads.
    """

    anchorId: str
    xMm: float
    yMm: float
    zMm: float

    #: The surface normal at this point, in the arrangement's own tilt/azimuth
    #: parameterization, so a micro-prong stands normal to the surface rather
    #: than vertically out of a curved shank.
    tiltDeg: float
    tiltAzimuthDeg: float

    servesPlacementIds: list[str] = Field(default_factory=list)


class CompiledPaveField(PaveModel):
    """The field, compiled: where its stones go and where its metal goes.

    Carried on the generated model beside `setting_result` and
    `arrangement_result`, so the pavé outcome travels with the geometry it
    describes rather than being recomputed by every consumer.
    """

    paveId: str
    kind: str
    host: str
    hostComponent: str
    pattern: str
    retentionStrategy: str
    enabled: bool

    placements: list[PaveStonePlacement] = Field(default_factory=list)
    retentionAnchors: list[PaveRetentionAnchor] = Field(default_factory=list)

    #: Cells dropped by a `CLIP` containment policy. Reported rather than
    #: silently absorbed: a field that lost a third of its stones to the edge
    #: of the surface is a fact the caller needs.
    clippedCells: int = 0

    #: What was NOT built and why, in the caller's own result object.
    notes: list[str] = Field(default_factory=list)

    def stone_count(self) -> int:
        return len(self.placements)

    def retention_count(self) -> int:
        return len(self.retentionAnchors)


# ---------------------------------------------------------------- lattice


def lattice_pitches(pave: PaveDefinition) -> tuple[float, float]:
    """The field's column and row pitch, in millimetres.

    ONE resolution point, read by both the lattice builders and the retention
    anchor derivation. Deriving them twice is how a bead would end up half a
    pitch from where four cells actually meet.
    """

    spec = pave.spec
    if isinstance(spec, PaveSpec):
        pitch = spec.pitchMm
        row_pitch = spec.rowPitchMm if spec.rowPitchMm is not None else pitch
    else:
        pitch = spec.stoneSpacingMm
        row_pitch = spec.rowSpacingMm if spec.rowSpacingMm is not None else pitch
    return pitch, row_pitch


def _row_offsets(pattern: str, offset_fraction: float, row_index: int) -> float:
    """How far row `row_index` is shifted along the column direction, in
    fractions of the column pitch.

    Stated as data-driven arithmetic rather than an `if` chain per pattern so a
    new pattern is one entry, and so `GRID`/`STAGGERED`/`ROW_OFFSET` provably
    differ only in this number.
    """

    if pattern == "STAGGERED":
        return 0.5 * (row_index % 2)
    if pattern == "ROW_OFFSET":
        return offset_fraction * row_index
    return 0.0


def _centered_positions(count: int, pitch: float) -> list[float]:
    """`count` positions of pitch `pitch`, centred on zero.

    An odd count puts one position exactly at the centre and an even count
    straddles it, which is the difference between a row with a middle stone and
    a row with a middle gap — a visible design decision, not a rounding
    artifact.
    """

    span = pitch * (count - 1)
    return [-span / 2.0 + pitch * i for i in range(count)]


def _column_count_for_span(span_deg: float, radius: float, pitch: float) -> int:
    """How many stones of pitch `pitch` fit in `span_deg` at `radius`.

    Closed form, and deliberately conservative: the arc length is
    `radius * span`, and a row of `n` stones spans `pitch * (n - 1)` centre to
    centre, so `n = floor(arc / pitch) + 1`. Using `arc / pitch` would claim
    room for one more stone than the span holds.
    """

    arc = radius * math.radians(span_deg)
    return max(1, int(arc // pitch) + 1)


# --------------------------------------------------------------- patterns

LatticeBuilder = Callable[
    [PaveDefinition, ResolvedHostSurface], list[tuple[int, int, float, float]]
]


def _cylindrical_lattice(
    pave: PaveDefinition, surface: ResolvedHostSurface
) -> list[tuple[int, int, float, float]]:
    """Cells on a cylindrical surface, as (row, column, angleDeg, axialMm).

    Columns run around the surface, rows along its axis — which for a shank is
    a field that wraps the finger and is several stones wide across the band.
    """

    radius = surface.radiusMm or 0.0
    extent = surface.axialExtentMm or 0.0
    spec = pave.spec

    pitch, row_pitch = lattice_pitches(pave)

    if isinstance(spec, PaveSpec):
        rows = spec.rowCount
        span = spec.angularSpanDeg
        start = spec.startAngleDeg
        columns = _column_count_for_span(span, radius, pitch)
        axial_center = surface.axialCenterMm
    else:
        assert isinstance(spec, MicrosettingSpec)
        rows = spec.rowCount
        columns = spec.columnCount
        start = spec.startAngleDeg
        # A stated structure defines its own span; the angular pitch follows
        # from the arc a stone spacing subtends at this radius.
        span = math.degrees(pitch * (columns - 1) / radius) if radius else 0.0
        axial_center = surface.axialCenterMm + spec.axialOffsetMm

    angular_pitch = math.degrees(pitch / radius) if radius else 0.0
    axial_positions = _centered_positions(rows, row_pitch)

    cells: list[tuple[int, int, float, float]] = []
    for row in range(rows):
        shift = _row_offsets(spec.pattern, spec.rowOffsetFraction, row)
        if spec.termination == "CENTERED":
            angles = [
                start + angular_pitch * (i - (columns - 1) / 2.0 + shift)
                for i in range(columns)
            ]
        else:
            angles = [start + angular_pitch * (i + shift) for i in range(columns)]
        axial = axial_center + axial_positions[row]
        for column, angle in enumerate(angles):
            cells.append((row, column, angle, axial))

    # An angular span wider than the pitch allows is caught by the caller's
    # containment policy, not silently truncated here.
    del extent, span
    return cells


def _planar_lattice(
    pave: PaveDefinition, surface: ResolvedHostSurface
) -> list[tuple[int, int, float, float]]:
    """Cells on a horizontal plane, as (row, column, angleDeg, radiusMm).

    Rows are concentric radii and columns are angular positions on each, which
    is what a gallery or halo-plane field actually is. The angular sequence
    comes from `arrangement/radial.py` for a full sweep, so a single-row planar
    pavé and a hand-written `RADIAL` pattern place their stones identically.
    """

    inner = surface.innerRadiusMm or 0.0
    spec = pave.spec

    pitch, row_pitch = lattice_pitches(pave)

    if isinstance(spec, PaveSpec):
        rows = spec.rowCount
        span = spec.angularSpanDeg
        start = spec.startAngleDeg
        base_radius = inner + (spec.axialSpanMm or 0.0)
    else:
        assert isinstance(spec, MicrosettingSpec)
        rows = spec.rowCount
        start = spec.startAngleDeg
        base_radius = inner + spec.axialOffsetMm
        span = 0.0

    cells: list[tuple[int, int, float, float]] = []
    for row in range(rows):
        radius = base_radius + row_pitch * row
        if radius <= 0.0:
            continue
        if isinstance(spec, PaveSpec):
            columns = _column_count_for_span(span, radius, pitch)
            angular_pitch = math.degrees(pitch / radius)
            if span >= 360.0:
                # A closed ring: reuse the resolver's own full-sweep spacing so
                # the last stone does not land on the first.
                count = max(1, int((radius * math.tau) // pitch))
                angles = ring_angles_deg(count, start, 360.0)
                columns = count
            else:
                shift = _row_offsets(
                    spec.pattern, spec.rowOffsetFraction, row
                )
                angles = [
                    start + angular_pitch * (i - (columns - 1) / 2.0 + shift)
                    for i in range(columns)
                ]
        else:
            columns = spec.columnCount
            angular_pitch = math.degrees(pitch / radius)
            shift = _row_offsets(spec.pattern, spec.rowOffsetFraction, row)
            angles = [
                start + angular_pitch * (i - (columns - 1) / 2.0 + shift)
                for i in range(columns)
            ]
        for column, angle in enumerate(angles):
            cells.append((row, column, angle, radius))
    return cells


@lru_cache(maxsize=1)
def surface_lattices() -> dict[str, LatticeBuilder]:
    """The surface registry. Every entry produces a real lattice.

    A registry rather than a branch chain, so a new surface kind is a new entry
    — the discipline `setting/dispatch.py` and `family/compile.py` already
    follow.
    """

    return {
        "CYLINDRICAL": _cylindrical_lattice,
        "PLANAR": _planar_lattice,
    }


@lru_cache(maxsize=1)
def pave_patterns() -> tuple[str, ...]:
    """Patterns with a real generator, derived from what the lattice honours."""

    return ("GRID", "STAGGERED", "ROW_OFFSET", "RADIAL", "EXPLICIT")


# ------------------------------------------------------------ compilation


def _placement_id(pave_id: str, row: int, column: int) -> str:
    """A stone's id: derived, deterministic, and never a UUID (§11).

    Reproducible from the field's own id and the cell's lattice coordinates, so
    re-compiling the same pavé reproduces the same ids and a stored compilation
    can be compared with a fresh one.
    """

    return f"{pave_id}.r{row}.c{column}"


def _cylindrical_point_and_tilt(
    surface: ResolvedHostSurface, angle_deg: float, axial_mm: float, seat_drop_mm: float
) -> tuple[tuple[float, float, float], float, float]:
    """Where a stone's girdle sits on a cylindrical surface, and how it leans.

    The stone is seated `seat_drop_mm` BELOW the surface along the local normal,
    so its girdle sits inside the metal and its crown stands proud — which is
    what makes a recess cut meaningful and a bead have something to hold. A
    stone centred exactly on the surface would be half outside the solid.

    The lean is the surface normal itself: `tiltDeg` is the angle from the
    crest and the azimuth flips by 180° on the far side, because leaning -30°
    toward +X and +30° toward -X are the same placement and only one of them is
    representable with a non-negative tilt.
    """

    radius = (surface.radiusMm or 0.0) - seat_drop_mm
    radians = math.radians(angle_deg)
    perp = math.radians(surface.surface_normal_azimuth_deg())
    axis = math.radians(surface.axisAzimuthDeg)
    lateral = radius * math.sin(radians)

    point = (
        lateral * math.cos(perp) + axial_mm * math.cos(axis),
        lateral * math.sin(perp) + axial_mm * math.sin(axis),
        radius * math.cos(radians),
    )

    normalized = ((angle_deg + 180.0) % 360.0) - 180.0
    if normalized >= 0.0:
        return point, normalized, surface.surface_normal_azimuth_deg()
    return point, -normalized, surface.surface_normal_azimuth_deg() + 180.0


def _planar_point(
    surface: ResolvedHostSurface, angle_deg: float, radius_mm: float, seat_drop_mm: float
) -> tuple[float, float, float]:
    """Where a stone's girdle sits on a horizontal plane.

    Seated `seat_drop_mm` below the plane, for the same reason a cylindrical
    stone is seated below its surface.
    """

    radians = math.radians(angle_deg)
    return (
        radius_mm * math.cos(radians),
        radius_mm * math.sin(radians),
        (surface.planeZMm or 0.0) - seat_drop_mm,
    )


def _contains(
    surface: ResolvedHostSurface, angle_deg: float, second_mm: float
) -> bool:
    """Whether a cell lies within the host's declared extent.

    A GEOMETRIC statement about the surface the category reported, not a
    professional judgment about whether the metal could carry the stone.
    """

    if surface.kind == "CYLINDRICAL":
        extent = surface.axialExtentMm
        if extent is None:
            return True
        half = extent / 2.0
        return abs(second_mm - surface.axialCenterMm) <= half + _COINCIDENT_EPSILON_MM

    inner = surface.innerRadiusMm
    outer = surface.outerRadiusMm
    if inner is not None and second_mm < inner - _COINCIDENT_EPSILON_MM:
        return False
    if outer is not None and second_mm > outer + _COINCIDENT_EPSILON_MM:
        return False
    return True


def _seat_drop_mm(pave: PaveDefinition) -> float:
    """How far below the host surface a stone's girdle sits.

    Derived from the retention's own bead radius rather than declared
    separately, because the two describe one relationship: a bead of radius r
    can only hold a stone whose girdle sits within reach of it. A CONSTRUCTION
    PARAMETER, not a professional seat depth — no sourced evidence says how
    deep a pavé stone should sit, so none is claimed.
    """

    return pave.retention.beadRadiusMm


def _explicit_placements(pave: PaveDefinition) -> list[PaveStonePlacement]:
    """Placements the document stated itself.

    Sorted by id, never by array order, so reordering the list cannot move a
    stone. Row and column are recorded as -1: these cells have no lattice
    provenance, and reporting a fabricated one would be worse than reporting
    none.
    """

    return [
        PaveStonePlacement(
            placementId=placement.placementId,
            rowIndex=-1,
            columnIndex=-1,
            transform=placement.transform,
            scale=(
                placement.scale if placement.scale is not None else pave.stoneScale
            ),
            gem=placement.gem if placement.gem is not None else pave.gem,
        )
        for placement in sorted(
            pave.explicitPlacements, key=lambda p: p.placementId
        )
    ]


def compile_pave_field(
    pave: PaveDefinition, surface: ResolvedHostSurface
) -> CompiledPaveField:
    """Turn a pavé and its resolved surface into placements and anchors.

    The lattice arithmetic lives here; the PLACEMENT is then handed to the
    arrangement engine by `compose_pave()`. Splitting the two keeps this
    function pure and testable against plain numbers.
    """

    if not pave.enabled:
        return CompiledPaveField(
            paveId=pave.paveId,
            kind=pave.kind,
            host=pave.host,
            hostComponent=surface.hostComponent,
            pattern=pave.spec.pattern,
            retentionStrategy=pave.retention.strategy,
            enabled=False,
            notes=[
                "This pavé is declared and disabled, so no stones and no "
                "retention metal were built. The parameters are preserved."
            ],
        )

    seat_drop = _seat_drop_mm(pave)
    notes: list[str] = []

    cells: list[tuple[int, int, float, float]] = []
    if pave.spec.pattern == "EXPLICIT":
        placements = _explicit_placements(pave)
        clipped = 0
        notes.append(
            "This field's placements are stated by the document, so its "
            "retention anchors are offset in the tangent frame at each stone "
            "rather than shared across a lattice: an explicit field has no "
            "lattice to share."
        )
    else:
        builder = surface_lattices()[surface.kind]
        cells = builder(pave, surface)

        placements = []
        clipped = 0
        for row, column, angle, second in cells:
            if not _contains(surface, angle, second):
                if pave.containment == "REJECT":
                    raise PaveContainmentError(
                        f"Pavé {pave.paveId!r} places a stone at row {row}, "
                        f"column {column} outside the {pave.host} surface's "
                        "declared extent, and the containment policy is "
                        "'REJECT'. Reduce the span, the row count or the pitch, "
                        "or set containment to 'CLIP' to end the field at the "
                        "surface edge."
                    )
                clipped += 1
                continue

            if surface.kind == "CYLINDRICAL":
                point, tilt, azimuth = _cylindrical_point_and_tilt(
                    surface, angle, second, seat_drop
                )
            else:
                point = _planar_point(surface, angle, second, seat_drop)
                tilt, azimuth = 0.0, 0.0

            # The transform is a DELTA from the as-built stone position, which
            # sits on the design axis with its girdle at `stoneAnchorZMm`.
            placements.append(
                PaveStonePlacement(
                    placementId=_placement_id(pave.paveId, row, column),
                    rowIndex=row,
                    columnIndex=column,
                    transform=InstanceTransform(
                        xMm=point[0],
                        yMm=point[1],
                        zMm=point[2] - surface.stoneAnchorZMm,
                        rotationDeg=pave.stoneOrientationDeg,
                        tiltDeg=tilt,
                        tiltAzimuthDeg=azimuth,
                    ),
                    scale=pave.stoneScale,
                    gem=pave.gem,
                )
            )

        if clipped:
            notes.append(
                f"{clipped} lattice cell(s) fell outside the {pave.host} "
                "surface's declared extent and were clipped."
            )

    if not placements:
        raise PaveFieldEmptyError(
            f"Pavé {pave.paveId!r} compiled to no stones. Raised rather than "
            "returning an empty field, which would silently produce a design "
            "that declares a pavé and contains none."
        )

    if len(placements) > MAX_PAVE_STONES:
        raise PaveCapacityExceededError(
            f"Pavé {pave.paveId!r} compiled to {len(placements)} stones, above "
            f"the software bound of {MAX_PAVE_STONES}. An implementation safety "
            "limit, not a statement about how many stones a design should have: "
            "increase the pitch or reduce the span."
        )

    anchors = (
        _explicit_anchors(pave, surface)
        if pave.spec.pattern == "EXPLICIT"
        else _lattice_anchors(pave, surface, cells)
    )
    if pave.retention.strategy == "NONE":
        notes.append(
            "Retention is 'NONE', so the field's stones were built with no "
            "metal holding them. An explicit choice, not a missing capability."
        )

    return CompiledPaveField(
        paveId=pave.paveId,
        kind=pave.kind,
        host=pave.host,
        hostComponent=surface.hostComponent,
        pattern=pave.spec.pattern,
        retentionStrategy=pave.retention.strategy,
        enabled=True,
        placements=placements,
        retentionAnchors=anchors,
        clippedCells=clipped,
        notes=notes,
    )


def _lattice_anchors(
    pave: PaveDefinition,
    surface: ResolvedHostSurface,
    cells: list[tuple[int, int, float, float]],
) -> list[PaveRetentionAnchor]:
    """Retention anchors derived in the SURFACE'S OWN PARAMETERS.

    WHY NOT IN 3D. A corner computed in the tangent plane at each stone lands
    on the chord rather than on the surface, so two adjacent stones' shared
    corner comes out at two slightly different points — and a `SHARED_BEAD`
    field silently degrades into an individual-bead field with four times the
    solids. Working in (angle, axial) and mapping to 3D once means adjacent
    cells share a corner EXACTLY, which is what makes the shared topology real.

    Corners sit at half a pitch in each direction, which is arithmetically
    where four cells meet — the gap a setter raises a bead into.
    """

    if pave.retention.strategy == "NONE" or not cells:
        return []

    pitch, row_pitch = lattice_pitches(pave)
    shared = pave.retention.strategy in SHARED_RETENTION_STRATEGIES
    # An individual bead belongs to ONE stone, so it is drawn in toward that
    # stone rather than left on the corner its neighbours share.
    inset = 1.0 if shared else _INDIVIDUAL_BEAD_INSET_FRACTION

    buckets: dict[tuple[int, int], list[str]] = {}
    ordered: list[tuple[tuple[int, int], float, float]] = []

    for row, column, angle, second in cells:
        if not _contains(surface, angle, second):
            continue
        placement_id = _placement_id(pave.paveId, row, column)

        # Half-pitch offsets in the surface's own parameters. On a cylinder the
        # angular half-pitch is the arc half-pitch converted at the surface
        # radius; on a plane it is converted at this row's own radius, because a
        # concentric row's angular pitch depends on how far out it sits.
        radius = surface.radiusMm if surface.kind == "CYLINDRICAL" else second
        half_angle = (
            math.degrees(pitch / 2.0 * inset / radius) if radius else 0.0
        )
        half_second = row_pitch / 2.0 * inset

        for sign_a in (-1.0, 1.0):
            for sign_b in (-1.0, 1.0):
                corner_angle = angle + sign_a * half_angle
                corner_second = second + sign_b * half_second
                key = (
                    int(round(corner_angle / 1e-6)),
                    int(round(corner_second / 1e-6)),
                )
                if shared and key in buckets:
                    buckets[key].append(placement_id)
                    continue
                buckets.setdefault(key, []).append(placement_id)
                ordered.append((key, corner_angle, corner_second))

    anchors: list[PaveRetentionAnchor] = []
    for index, (key, corner_angle, corner_second) in enumerate(ordered):
        if surface.kind == "CYLINDRICAL":
            # Anchors sit ON the surface, not dropped into it: the piece's own
            # embed depth is applied by the builder, so applying one here too
            # would sink every bead twice.
            point, tilt, azimuth = _cylindrical_point_and_tilt(
                surface, corner_angle, corner_second, 0.0
            )
        else:
            point = _planar_point(surface, corner_angle, corner_second, 0.0)
            tilt, azimuth = 0.0, 0.0
        anchors.append(
            PaveRetentionAnchor(
                anchorId=f"{pave.paveId}.bead.{index}",
                xMm=point[0],
                yMm=point[1],
                zMm=point[2],
                tiltDeg=tilt,
                tiltAzimuthDeg=azimuth,
                servesPlacementIds=sorted(set(buckets[key])),
            )
        )
    return anchors


def _explicit_anchors(
    pave: PaveDefinition, surface: ResolvedHostSurface
) -> list[PaveRetentionAnchor]:
    """Retention anchors for an EXPLICIT field.

    An explicit field has no lattice, so there is no shared corner to compute:
    each placement gets its own anchors, offset in the tangent frame at that
    stone by half the declared pitch. Reported in the field's notes rather than
    presented as a derived lattice, because it is not one.
    """

    if pave.retention.strategy == "NONE":
        return []

    pitch, row_pitch = lattice_pitches(pave)
    anchors: list[PaveRetentionAnchor] = []
    index = 0
    for placement in _explicit_placements(pave):
        transform = placement.transform
        tilt = math.radians(transform.tiltDeg)
        azimuth = math.radians(transform.tiltAzimuthDeg)
        normal = (
            math.sin(tilt) * math.cos(azimuth),
            math.sin(tilt) * math.sin(azimuth),
            math.cos(tilt),
        )
        tangent_a = (-math.sin(azimuth), math.cos(azimuth), 0.0)
        tangent_b = (
            normal[1] * tangent_a[2] - normal[2] * tangent_a[1],
            normal[2] * tangent_a[0] - normal[0] * tangent_a[2],
            normal[0] * tangent_a[1] - normal[1] * tangent_a[0],
        )
        base = (
            transform.xMm,
            transform.yMm,
            transform.zMm + surface.stoneAnchorZMm,
        )
        for sign_a in (-1.0, 1.0):
            for sign_b in (-1.0, 1.0):
                anchors.append(
                    PaveRetentionAnchor(
                        anchorId=f"{pave.paveId}.bead.{index}",
                        xMm=base[0]
                        + pitch / 2.0 * sign_a * tangent_a[0]
                        + row_pitch / 2.0 * sign_b * tangent_b[0],
                        yMm=base[1]
                        + pitch / 2.0 * sign_a * tangent_a[1]
                        + row_pitch / 2.0 * sign_b * tangent_b[1],
                        zMm=base[2]
                        + pitch / 2.0 * sign_a * tangent_a[2]
                        + row_pitch / 2.0 * sign_b * tangent_b[2],
                        tiltDeg=transform.tiltDeg,
                        tiltAzimuthDeg=transform.tiltAzimuthDeg,
                        servesPlacementIds=[placement.placementId],
                    )
                )
                index += 1
    return anchors


def compose_pave(
    base: ArrangementDefinition | None,
    pave: PaveDefinition | None,
    surface: ResolvedHostSurface | None,
) -> tuple[ArrangementDefinition | None, CompiledPaveField | None]:
    """Add a pavé field's stones to the arrangement a design already declares.

    Returns `(base, None)` for `None`, which is the whole
    backward-compatibility story in one line: a design with no pavé composes to
    exactly the arrangement it had before this sprint.
    """

    if pave is None:
        return base, None
    if surface is None:  # pragma: no cover - the adapter raises first
        return base, None

    field = compile_pave_field(pave, surface)
    if not field.enabled:
        return base, field

    existing = {i.instanceId for i in base.instances} if base is not None else set()
    instances: list[StoneInstanceDef] = list(base.instances) if base is not None else []
    relations: list[ArrangementRelation] = (
        list(base.relations) if base is not None else []
    )

    # THE DESIGN'S OWN CENTRE STONE, when nothing else supplied it.
    #
    # A pavé is a field set INTO a surface, not a replacement for the design it
    # decorates: a solitaire with a pavé shank still has its solitaire. Without
    # this, composing onto `None` would produce an arrangement containing only
    # pavé stones, the deterministic primary selection would pick the
    # lowest-id pavé stone, and the centre stone would silently BECOME a pavé
    # stone — inheriting the bare `stone_reference` component name while sitting
    # on the band. That is not an inferred design: the centre stone is already
    # in the document as `stone`, and this instance is how it keeps its place
    # once an arrangement exists at all.
    if base is None:
        instances.append(
            StoneInstanceDef(
                instanceId=DESIGN_CENTER_INSTANCE_ID,
                stoneRef="primary",
                role="CENTER",
                placement=InstancePlacement(transform=InstanceTransform()),
            )
        )
        existing.add(DESIGN_CENTER_INSTANCE_ID)

    for placement in field.placements:
        if placement.placementId in existing:
            raise PaveIdentityCollisionError(
                f"Pavé {pave.paveId!r} would create instance "
                f"{placement.placementId!r}, which this design's arrangement "
                "already declares. Ids are the authoritative identity, so a "
                "collision would make every reference to it ambiguous — rename "
                "the pavé or the existing instance."
            )
        existing.add(placement.placementId)
        instances.append(
            StoneInstanceDef(
                instanceId=placement.placementId,
                stoneRef=pave.stoneRef,
                role=PAVE_ROLE,
                gem=placement.gem,
                overrides=InstanceOverrides(scale=placement.scale),
                placement=InstancePlacement(transform=placement.transform),
            )
        )

    if len(instances) > MAX_INSTANCES:
        raise PaveCapacityExceededError(
            f"Composing this pavé produced {len(instances)} instances, above "
            f"the arrangement bound of {MAX_INSTANCES}. A software limit, not a "
            "statement about how many stones a design should have."
        )

    # RELATIONS RECORD THE INTENT so a later edit, a Studio grouped operation or
    # a future pavé-aware setting strategy can act on the field rather than
    # re-deriving it from coordinates that happen to look regular.
    if len(field.placements) >= 2:
        relations.append(
            ArrangementRelation(
                relationId=f"{pave.paveId}.field",
                kind="EVENLY_SPACED_WITH",
                members=[p.placementId for p in field.placements],
                note=(
                    f"{pave.kind} field {pave.paveId!r} on the {pave.host} "
                    f"surface, {field.stone_count()} stones in a "
                    f"{pave.spec.pattern} lattice."
                ),
            )
        )

    if base is None:
        composed = ArrangementDefinition(instances=instances, relations=relations)
    else:
        composed = base.model_copy(
            update={"instances": instances, "relations": relations}
        )
    return composed, field
