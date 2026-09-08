"""What the Pavé & Microsetting Engine can actually do (Sprint 26).

THE SINGLE SOURCE OF TRUTH for CURRENT vs PARTIAL vs PLANNED, mirrored —
never hand-copied — into `specs/pave/v1/pave-registry.json` and
`specs/capabilities/jewelmind-capabilities.json`.

FOUR INDEPENDENT AXES, carried over from Sprints 24-25 because the same
distinction decides the same question:

    representable  - the model expresses it, and it round-trips through JDL
    composable     - `compile.py` turns it into a real arrangement
    stoneGeometry  - Atlas builds a stone solid for every cell
    settingGeometry- Atlas builds real metal that holds those stones

THE FOURTH AXIS IS TRUE HERE FOR THE FIRST TIME IN THIS PROGRAMME. Sprints 24
and 25 built stones with no metal holding them, and said so. Sprint 26 builds
real retention: beads and micro-prongs are solids fused into the host, and a
recess is the stone's own volume cut out of it. That is why a pavé with a bead
retention is CURRENT rather than PARTIAL — and why the strategies that have
no builder are named PLANNED rather than quietly folded into one that does.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

#: JewelMind's established capability vocabulary, unchanged since Sprint 15.
#:
#: The Sprint 26 brief names "SUPPORTED" and "NOT_IMPLEMENTED" for the two ends
#: of this scale. They map to `CURRENT` and `PLANNED` respectively, and the
#: established words are used rather than a second vocabulary for one
#: subsystem: two status vocabularies in one registry is precisely the drift
#: the same brief asks the audit to hunt for.
CapabilityStatus = Literal["CURRENT", "PARTIAL", "PLANNED"]

#: Bumped whenever pavé COMPILATION changes — the lattice arithmetic, the seat
#: drop derivation, the retention anchor topology, or how a host surface is
#: parameterized. A purely additive capability entry does not bump it.
PAVE_COMPILER_VERSION = "1.0.0"

PAVE_REGISTRY_VERSION = "1.0.0"

#: Host surfaces named for architectural completeness but with NO resolver and
#: NO membership in `PaveHost`. The mapped value is the real reason, not a
#: roadmap slogan.
RESERVED_PAVE_HOSTS: dict[str, str] = {
    "SETTING_SURFACE": (
        "A basket wall or a prong flank is a swept or lofted surface with no "
        "closed-form parameterization the pavé layer could walk. Targeting it "
        "means picking faces out of a solid, and a face index is not "
        "reproducible across kernel versions or across a change to an "
        "unrelated parameter — a pavé whose stones moved because a fillet "
        "renumbered a face would be indefensible."
    ),
    "BAND_INNER": (
        "The shank's inner surface is the finger bore. Setting stones into it "
        "is not a technique this project has evidence for, and the geometry "
        "would be a recess into the only surface whose dimensions the ring "
        "size fixes."
    ),
    "BAND_SIDE": (
        "The shank's flat side faces are planar and executable in principle, "
        "but their extent depends on the band profile's own section — "
        "comfort-fit has no flat side at all. Supporting it needs a profile "
        "capability that reports a side surface, which `geometry/shank/` does "
        "not have."
    ),
    "CUSTOM_SURFACE": (
        "An arbitrary user-supplied surface would need a real surface import "
        "and a robust offset walk. Neither exists, and `EXPLICIT` placements "
        "already cover the case where a document knows exactly where its "
        "stones go."
    ),
    "HALO_PLANE": (
        "The plane a declared halo's rings sit in is trivially resolvable, and "
        "the pavé would still have nothing to hold it: a halo has NO METAL. "
        "Sprint 25 recorded halo retention as PLANNED, so beads in a halo's "
        "plane would fuse into nothing and ship as a disconnected production "
        "solid. Blocked on the same setting RFC, not on surface targeting."
    ),
    "PRONG_SURFACE": (
        "Stones set into the prongs themselves need per-prong surface "
        "targeting and shared retention across two curved bodies, which "
        "Sprint 23 recorded as absent."
    ),
}

#: Retention strategies named but with no builder, and deliberately NOT
#: `PaveRetentionStrategy` members.
RESERVED_RETENTION_STRATEGIES: dict[str, str] = {
    "SHARED_PRONG": (
        "One prong body gripping two adjacent stones needs the shared-prong "
        "geometry Sprint 23 explicitly recorded as PLANNED. A bead already "
        "shares between four cells; a shared PRONG is a different solid with "
        "a different contact topology, and substituting one for the other "
        "would report a technique the metal does not implement."
    ),
    "CHANNEL": (
        "A channel holds stones between two continuous rails. Sprint 23 "
        "recorded support rails as PLANNED, and approximating a channel as a "
        "row of beads would misdescribe both the metal and how the stones are "
        "retained."
    ),
    "GRAIN": (
        "Raised grain work is a cut-and-pushed surface treatment rather than "
        "a placed solid. Representing it as a sphere would be a bead with a "
        "different name."
    ),
    "THREAD_SET": (
        "Thread or bright-cut setting removes metal along a continuous line "
        "between stones. It needs a swept cut along the lattice, which the "
        "recess operation (a per-stone cut) does not express."
    ),
}


class PaveCapabilityEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    capability: str
    status: CapabilityStatus

    representable: bool
    composable: bool
    stoneGeometry: bool
    settingGeometry: bool

    note: str


def _entry(
    capability: str,
    status: CapabilityStatus,
    note: str,
    *,
    representable: bool = True,
    composable: bool = True,
    stone_geometry: bool = True,
    setting_geometry: bool = True,
) -> PaveCapabilityEntry:
    return PaveCapabilityEntry(
        capability=capability,
        status=status,
        representable=representable,
        composable=composable,
        stoneGeometry=stone_geometry,
        settingGeometry=setting_geometry,
        note=note,
    )


#: The two first-class field kinds.
PAVE_KIND_CAPABILITIES: dict[str, PaveCapabilityEntry] = {
    entry.capability: entry
    for entry in (
        _entry(
            "PAVE",
            "CURRENT",
            "Surface population: an angular span and a row count filled at a "
            "stated pitch, so the designer gives the area and the density and "
            "the stone count follows. Real stone solids and real retention "
            "metal.",
        ),
        _entry(
            "MICROSETTING",
            "CURRENT",
            "A stated retention topology: explicit rows and columns with "
            "explicit spacings, so the designer gives the structure and the "
            "area follows. The inverse specification of a PAVE, sharing its "
            "lattice, surface and retention primitives.",
        ),
    )
}


#: Which host surfaces have a real resolver AND real geometry.
PAVE_HOST_CAPABILITIES: dict[str, PaveCapabilityEntry] = {
    entry.capability: entry
    for entry in (
        _entry(
            "BAND_OUTER",
            "CURRENT",
            "The shank's outer surface, cylindrical about the finger axis — "
            "the classic shank pavé. Executable because Sprint 26 gave the "
            "arrangement a real axis tilt, so each stone follows the surface "
            "normal instead of standing upright through the metal. Retention "
            "beads fuse into the band and a recess is cut out of it.",
        ),
        _entry(
            "HEAD_PLANE",
            "CURRENT",
            "The horizontal plane at the top of the head. Planar, so no tilt "
            "is needed. The field is bounded away from the centre stone by the "
            "inner radius the Ring adapter reports, so a gallery pavé cannot "
            "land on top of the stone it surrounds.",
        ),
    )
}


PAVE_PATTERN_CAPABILITIES: dict[str, PaveCapabilityEntry] = {
    entry.capability: entry
    for entry in (
        _entry(
            "GRID",
            "CURRENT",
            "Rows and columns aligned. Every row starts at the same angular "
            "position.",
        ),
        _entry(
            "STAGGERED",
            "CURRENT",
            "Alternate rows shifted by half the column pitch — the fixed 0.5 "
            "case of ROW_OFFSET, kept separate because a half shift is the "
            "case a designer names.",
        ),
        _entry(
            "ROW_OFFSET",
            "CURRENT",
            "Every successive row shifted by a declared fraction of the column "
            "pitch, so a diagonal lattice is a parameter rather than a new "
            "pattern.",
        ),
        _entry(
            "RADIAL",
            "CURRENT",
            "Stones distributed about the host surface's own axis. On a full "
            "360-degree planar sweep the angular sequence comes from "
            "`arrangement/radial.py` — the same function the resolver uses for "
            "a RADIAL pattern — so a pavé ring and a hand-written one place "
            "their stones identically.",
        ),
        _entry(
            "EXPLICIT",
            "CURRENT",
            "The document states each placement, carrying an arrangement "
            "`InstanceTransform` verbatim. The escape hatch for a field no "
            "lattice derives; refused rather than silently replaced by a "
            "generated lattice when the list is empty.",
        ),
    )
}


PAVE_RETENTION_CAPABILITIES: dict[str, PaveCapabilityEntry] = {
    entry.capability: entry
    for entry in (
        _entry(
            "NONE",
            "CURRENT",
            "No retention metal, stated explicitly. An honest option rather "
            "than a missing capability: it produces the stone field alone, "
            "which is what a layout preview is. Reported in the compiled "
            "field's notes so it can never be mistaken for a failure to build "
            "metal.",
            setting_geometry=False,
        ),
        _entry(
            "BEAD",
            "CURRENT",
            "One bead per lattice corner of each stone, individually — four "
            "solids per stone. Each is a real sphere fused into the host, "
            "embedded below the surface so the boolean produces genuine 3D "
            "overlap rather than a tangent touch.",
        ),
        _entry(
            "SHARED_BEAD",
            "CURRENT",
            "One bead per lattice corner, shared by every stone touching it. "
            "Genuinely fewer solids, and each names the stones it serves, so "
            "'shared' is a checkable statement about the topology rather than "
            "a label.",
        ),
        _entry(
            "MICRO_PRONG",
            "CURRENT",
            "A small cylinder standing normal to the host surface at each "
            "corner. Normal to the SURFACE, not vertical, which is what makes "
            "it a prong on a curved shank rather than a pin through it.",
        ),
    )
}


#: Cross-cutting capabilities, kept beside the rest so a reader sees the whole
#: picture rather than inferring it from twelve notes.
PAVE_FEATURE_CAPABILITIES: dict[str, PaveCapabilityEntry] = {
    entry.capability: entry
    for entry in (
        _entry(
            "pave_over_family",
            "CURRENT",
            "A pavé composes onto a compiled family or an explicit "
            "arrangement rather than replacing it, so 'three-stone with a "
            "pavé shank' is one design. Same composition contract Sprint 25 "
            "established for the halo.",
        ),
        _entry(
            "pave_over_halo",
            "PARTIAL",
            "A pavé and a halo coexist in one design: both compose onto the "
            "same placement and both build real stones. PARTIAL because a pavé "
            "cannot target the HALO's own plane — a halo has no metal to hold "
            "beads — so the two are concentric neighbours rather than one "
            "structure. Nothing prevents a dense field and a halo ring from "
            "occupying the same radius; that overlap is reported as a geometric "
            "fact, not refused.",
        ),
        _entry(
            "reference_recess",
            "CURRENT",
            "The stones' own volumes cut out of the host, reusing "
            "`setting/seat.py` — the module whose source is asserted never to "
            "fuse a stone shape. Deliberately NOT called a seat: it has no "
            "bearing shoulder and makes no claim that a stone would sit "
            "correctly in it.",
        ),
        _entry(
            "containment_policy",
            "CURRENT",
            "A cell outside the host's declared extent is either clipped or "
            "the whole field is refused, by declared policy. A clipped field "
            "reports how many cells it lost, so a field that lost a third of "
            "its stones to an edge is visible rather than silently smaller.",
        ),
        _entry(
            "mixed_pave_gem_identities",
            "CURRENT",
            "The field carries its own GemIdentity and an explicit placement "
            "may override it, resolved through the real Sprint 21 registry. "
            "Semantic only, exactly as for a single stone: it never affects "
            "geometry.",
            setting_geometry=False,
        ),
        _entry(
            "mixed_pave_stone_specifications",
            "PARTIAL",
            "A field's `stoneRef` may name a stone specification other than "
            "'primary', and that reference is preserved and reported. It does "
            "not resolve, because JDL carries exactly one `stone` — so such a "
            "field produces no geometry and says so (JM-PAVE-004).",
            stone_geometry=False,
            setting_geometry=False,
        ),
        _entry(
            "multiple_pave_fields",
            "PLANNED",
            "One field per design. A shank pavé AND a gallery pavé in one "
            "document needs a list of fields, each with its own host and "
            "retention, plus a rule for what happens where two fields meet. "
            "The single field is `pave`, not `paves`, so the limitation is "
            "visible in the schema rather than implied.",
            representable=False,
            composable=False,
            stone_geometry=False,
            setting_geometry=False,
        ),
        _entry(
            "outline_following_pave",
            "PLANNED",
            "A field following a non-circular stone's own girdle outline needs "
            "the outline-offset walk Sprint 25 already recorded as absent for "
            "halos. The planar host offers concentric circles and says so.",
            representable=False,
            composable=False,
            stone_geometry=False,
            setting_geometry=False,
        ),
        _entry(
            "pave_collision_checking",
            "PARTIAL",
            "Whether two pavé stones, or a pavé stone and a halo stone, "
            "physically overlap is a GEOMETRIC fact Geometry Inspection "
            "reports for every named component pair. What does not exist is a "
            "rule interpreting that overlap as a defect — that requires a "
            "professional minimum this project has no evidence for.",
            setting_geometry=False,
        ),
        _entry(
            "professional_pave_rules",
            "PLANNED",
            "A minimum pavé spacing, a minimum bead diameter, a maximum stone "
            "density, a settable seat depth, or whether a field could be cut "
            "by a setter. Each needs sourced professional evidence this "
            "project does not have, so none exists — see the brief's own "
            "prohibition on inventing them.",
            representable=False,
            composable=False,
            stone_geometry=False,
            setting_geometry=False,
        ),
    )
}


#: Every capability, flattened, so a consumer can look one up without knowing
#: which family it belongs to.
PAVE_CAPABILITIES: dict[str, PaveCapabilityEntry] = {
    **PAVE_KIND_CAPABILITIES,
    **PAVE_HOST_CAPABILITIES,
    **PAVE_PATTERN_CAPABILITIES,
    **PAVE_RETENTION_CAPABILITIES,
    **PAVE_FEATURE_CAPABILITIES,
}


def get_pave_capability(capability: str) -> PaveCapabilityEntry | None:
    return PAVE_CAPABILITIES.get(capability)


def supported_pave_hosts() -> tuple[str, ...]:
    """Hosts whose geometry is fully executable. Derived, never restated."""

    return tuple(
        sorted(
            name
            for name, entry in PAVE_HOST_CAPABILITIES.items()
            if entry.status == "CURRENT"
        )
    )


def retention_strategies_with_geometry() -> tuple[str, ...]:
    """Retention strategies that build real metal.

    NOT empty, unlike the equivalent function in the Family and Halo
    registries — which is the one substantive difference between this sprint's
    claim and theirs.
    """

    return tuple(
        sorted(
            name
            for name, entry in PAVE_RETENTION_CAPABILITIES.items()
            if entry.settingGeometry
        )
    )
