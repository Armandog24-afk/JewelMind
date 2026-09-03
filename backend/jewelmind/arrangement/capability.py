"""What the Stone Arrangement Engine can actually do (Sprint 22).

THE SINGLE SOURCE OF TRUTH for CURRENT vs PARTIAL vs PLANNED, mirrored — never
hand-copied — into `specs/arrangement/v1/arrangement-registry.json` and
`specs/capabilities/jewelmind-capabilities.json`. Sprint 20 removed three
hand-maintained capability lists that had already drifted and made Designer and
Setting misreport real capabilities; this registry exists so that cannot happen
here.

THE DISTINCTION THIS REGISTRY EXISTS TO KEEP HONEST. Three independent axes,
and a capability may sit anywhere in the grid:

    representable  - the model can express it, and it round-trips through JDL
    resolvable     - `resolve.py` turns it into explicit numbers
    generatable    - the geometry pipeline builds a solid for it

A pattern can be fully representable and fully resolvable while remaining
ungeneratable, and reporting that as "supported" would be the exact
misstatement the brief forbids. Today every listed pattern and relation is
representable and resolvable; STONE GEOMETRY IS EMITTED FOR ONE INSTANCE, so
multi-stone generation is PARTIAL.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

CapabilityStatus = Literal["CURRENT", "PARTIAL", "PLANNED"]

#: Bumped whenever the resolution ARITHMETIC changes — a different member
#: ordering, a different centring convention, a changed composition order. A
#: purely additive capability entry does not bump it, because a stored
#: resolution stays valid.
RESOLVER_VERSION = "1.0.0"

ARRANGEMENT_REGISTRY_VERSION = "1.0.0"


class ArrangementCapabilityEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    capability: str
    status: CapabilityStatus

    #: Can the domain model express it and JDL carry it?
    representable: bool

    #: Does `resolve.py` produce explicit placements for it?
    resolvable: bool

    #: Does the geometry pipeline build a solid for it TODAY? `False` for
    #: everything that depends on emitting more than one stone component.
    generatable: bool

    note: str


def _entry(
    capability: str,
    status: CapabilityStatus,
    representable: bool,
    resolvable: bool,
    generatable: bool,
    note: str,
) -> ArrangementCapabilityEntry:
    return ArrangementCapabilityEntry(
        capability=capability,
        status=status,
        representable=representable,
        resolvable=resolvable,
        generatable=generatable,
        note=note,
    )


ARRANGEMENT_CAPABILITIES: dict[str, ArrangementCapabilityEntry] = {
    entry.capability: entry
    for entry in (
        _entry(
            "stone_instance",
            "CURRENT",
            True,
            True,
            True,
            "A first-class occurrence with a stable ID, a stone reference, a role, a "
            "placement and a gem. One instance is generated as the existing "
            "stone_reference component.",
        ),
        _entry(
            "explicit_placement",
            "CURRENT",
            True,
            True,
            False,
            "An instance placed by explicit XYZ plus a vertical-axis rotation. "
            "Resolved exactly; a non-zero XY offset is not yet built, because the "
            "current stone builder places one stone on the design axis.",
        ),
        _entry(
            "group",
            "CURRENT",
            True,
            True,
            False,
            "Named groups with their own origin; a member's placement composes with "
            "the group transform during resolution.",
        ),
        _entry(
            "linear_pattern",
            "CURRENT",
            True,
            True,
            False,
            "count/spacing/direction, optionally centred on the anchor. Expanded to "
            "explicit member placements by closed-form evaluation.",
        ),
        _entry(
            "radial_pattern",
            "CURRENT",
            True,
            True,
            False,
            "count/radius/startAngle/sweep, optionally aligning each member to its "
            "radius. Expanded by closed-form evaluation.",
        ),
        _entry(
            "mirror_pattern",
            "CURRENT",
            True,
            True,
            False,
            "One reflected copy across the YZ or XZ plane, flipping a chiral stone's "
            "own orientation.",
        ),
        _entry(
            "relative_placement",
            "PARTIAL",
            True,
            True,
            False,
            "A RELATIVE placement mode resolves against the parent group's frame. "
            "Placement relative to ANOTHER INSTANCE is PLANNED: it needs a dependency "
            "order, and a cyclic reference has no determinate resolution.",
        ),
        _entry(
            "relationships",
            "PARTIAL",
            True,
            True,
            False,
            "Five relation kinds are representable, reference-checked and preserved "
            "through resolution. They are DECLARATIONS, not constraints: nothing moves "
            "an instance to satisfy one. Enforcement is PLANNED.",
        ),
        _entry(
            "multi_stone_geometry",
            "PARTIAL",
            True,
            True,
            False,
            "The arrangement resolves every instance, and the compilation boundary "
            "reports each one's generation status. The current pipeline emits ONE stone "
            "component, so additional instances are reported NOT_GENERATED with a "
            "reason. See docs/bible/24-arrangement/execution-boundary.md.",
        ),
        _entry(
            "instance_overrides",
            "PARTIAL",
            True,
            True,
            False,
            "scale and orientationDeg are representable and carried through resolution. "
            "Neither is applied to geometry yet, because doing so requires the "
            "multi-stone emission path.",
        ),
        _entry(
            "per_instance_gem",
            "CURRENT",
            True,
            True,
            False,
            "Each instance may carry its own GemIdentity, resolved through the real "
            "Sprint 21 registry. Semantic only — it never affects geometry, exactly as "
            "for the single-stone case.",
        ),
        _entry(
            "full_3d_instance_orientation",
            "PLANNED",
            False,
            False,
            False,
            "Tilt and roll. Deliberately not representable: accepting a rotation no "
            "builder can execute would be a silently ignored field.",
        ),
        _entry(
            "path_pattern",
            "PLANNED",
            False,
            False,
            False,
            "Members distributed along an arbitrary curve. Needs curve evaluation, "
            "which belongs to Atlas, not to a declarative arrangement.",
        ),
        _entry(
            "constraint_solving",
            "PLANNED",
            False,
            False,
            False,
            "Iterative satisfaction of relations. Explicitly out of scope: a solver's "
            "output depends on iteration order and starting values, which this layer's "
            "determinism guarantee forbids.",
        ),
        _entry(
            "arrangement_collision_checking",
            "PLANNED",
            False,
            False,
            False,
            "Whether two placed stones overlap is a GEOMETRIC fact, answerable only by "
            "Geometry Inspection once multi-stone geometry exists. No spacing rule is "
            "invented here.",
        ),
        _entry(
            "professional_arrangement_rules",
            "PLANNED",
            False,
            False,
            False,
            "Minimum spacing, accent-to-centre proportion, pave density. Each needs "
            "sourced professional evidence this project does not have, so none exists.",
        ),
    )
}


def get_capability(capability: str) -> ArrangementCapabilityEntry | None:
    return ARRANGEMENT_CAPABILITIES.get(capability)


def current_capabilities() -> list[str]:
    return sorted(
        name
        for name, entry in ARRANGEMENT_CAPABILITIES.items()
        if entry.status == "CURRENT"
    )


def generatable_capabilities() -> list[str]:
    """Capabilities that produce real geometry today.

    Separate from `current_capabilities()` on purpose: CURRENT means the layer
    executes its own job completely, which for a declarative layer means
    resolution — not that a solid comes out the far end.
    """

    return sorted(
        name for name, entry in ARRANGEMENT_CAPABILITIES.items() if entry.generatable
    )


#: Pattern kinds with a real closed-form expander in `resolve.py`. Derived from
#: the registry so the two cannot disagree.
def resolvable_pattern_kinds() -> tuple[str, ...]:
    mapping = {
        "linear_pattern": "LINEAR",
        "radial_pattern": "RADIAL",
        "mirror_pattern": "MIRROR",
    }
    return tuple(
        kind
        for capability, kind in sorted(mapping.items())
        if ARRANGEMENT_CAPABILITIES[capability].resolvable
    )
