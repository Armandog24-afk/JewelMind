"""Family semantics -> arrangement primitives (Sprint 24).

THE ONLY TRANSFORMATION IN THIS LAYER, and it deliberately produces an
`ArrangementDefinition` rather than positions of its own. Stone Arrangement
Engine v1 remains the sole authority on placement: this module chooses which
arrangement primitives express a family, and the arrangement resolver then does
the arithmetic exactly as it does for a hand-written arrangement.

That indirection is the point. A three-stone family compiles to a source
instance plus a `MIRROR` pattern, so the mirroring is performed by the same code
that mirrors anything else — and a family can never disagree with an
arrangement about where a mirrored stone goes.

A REGISTRY, not an `if familyType == ...` chain. A new family is a new entry.

REJECTS, NEVER REPAIRS. A missing role, a wrong cardinality or an unresolvable
reference raises. Filling in a plausible member would produce a design nobody
authored — the discipline Sprint 20 set for outlines and Sprint 22 for
arrangements.

KERNEL-FREE. Nothing here imports CadQuery, any geometry module, or any jewelry
category. The output is arrangement data.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from functools import lru_cache

from jewelmind.arrangement.models import (
    MAX_INSTANCES,
    ArrangementDefinition,
    ArrangementPattern,
    ArrangementRelation,
    InstanceOverrides,
    InstancePlacement,
    InstanceTransform,
    MirrorPatternSpec,
    StoneInstanceDef,
)
from jewelmind.family.errors import (
    FamilyCapacityExceededError,
    FamilyMemberMissingError,
    FamilyRoleCardinalityError,
    FamilyRoleInvalidError,
    FamilyTypeUnsupportedError,
)
from jewelmind.family.models import (
    MAX_FAMILY_MEMBERS,
    CenterWithAccentsParams,
    ClusterParams,
    FamilyDefinition,
    FamilyMember,
    ThreeStoneParams,
    ToiEtMoiParams,
)
from jewelmind.gem.models import StoneRole

#: Which roles each family accepts, and how many of each it requires.
#:
#: `None` as a count means "any number, including zero". Stated as data rather
#: than as checks inside each compiler so the rules are inspectable, testable
#: and reportable — Forge reads this same table.
FAMILY_ROLE_RULES: dict[str, dict[str, int | None]] = {
    "THREE_STONE": {"CENTER": 1, "SIDE": 2},
    "TOI_ET_MOI": {"SIDE": 2},
    "CLUSTER": {"CENTER": None, "ACCENT": None},
    "CENTER_WITH_ACCENTS": {"CENTER": 1, "ACCENT": None},
}

#: Canonical member ids a compiler derives when a document does not name them.
#: DERIVED, never random: re-compiling the same family must produce the same
#: ids, or a stored compilation could not be compared with a fresh one.
CENTER_MEMBER_ID = "center"
LEFT_MEMBER_ID = "side.left"
RIGHT_MEMBER_ID = "side.right"
ACCENT_MEMBER_PREFIX = "accent"

FamilyCompiler = Callable[[FamilyDefinition], ArrangementDefinition]


def _members_by_role(family: FamilyDefinition) -> dict[str, list[FamilyMember]]:
    grouped: dict[str, list[FamilyMember]] = {}
    for member in family.members:
        grouped.setdefault(member.role, []).append(member)
    # Sorted by id inside each role, so compilation never depends on the order
    # members happen to appear in the document.
    for role in grouped:
        grouped[role].sort(key=lambda m: m.memberId)
    return grouped


def validate_roles(family: FamilyDefinition) -> None:
    """Check the family's roles against `FAMILY_ROLE_RULES`.

    Raised here rather than inside each compiler so every family is checked the
    same way, and so Forge can report the same failure without compiling.

    A family with NO members is legal and skips cardinality: that is how a
    twelve-stone cluster is expressed without typing twelve members, and the
    compiler derives them from the parameters.
    """

    rules = FAMILY_ROLE_RULES.get(family.familyType)
    if rules is None:
        raise FamilyTypeUnsupportedError(
            f"No role rules are registered for family type "
            f"{family.familyType!r}. Registered: {sorted(FAMILY_ROLE_RULES)}."
        )

    if not family.members:
        return

    grouped = _members_by_role(family)

    for role in grouped:
        if role not in rules:
            raise FamilyRoleInvalidError(
                f"Role {role!r} is not part of a {family.familyType} family. "
                f"Accepted roles: {', '.join(sorted(rules))}."
            )

    for role, expected in rules.items():
        if expected is None:
            continue
        actual = len(grouped.get(role, []))
        if actual != expected:
            raise FamilyRoleCardinalityError(
                f"A {family.familyType} family requires exactly {expected} "
                f"member(s) with role {role!r}, found {actual}."
            )


def _instance(
    member: FamilyMember,
    transform: InstanceTransform,
    *,
    default_scale: float | None = None,
) -> StoneInstanceDef:
    """One arrangement instance for one family member.

    The member's own `scale`/`orientationDeg` win over the family default, so a
    single unusual side stone does not require abandoning the family's
    parameters. `placementOverride` wins over the derived transform for the same
    reason.
    """

    scale = member.scale if member.scale is not None else default_scale
    return StoneInstanceDef(
        instanceId=member.memberId,
        stoneRef=member.stoneRef,
        role=member.role,
        gem=member.gem,
        overrides=InstanceOverrides(
            scale=scale, orientationDeg=member.orientationDeg
        ),
        placement=InstancePlacement(
            transform=member.placementOverride or transform
        ),
    )


def _derived_member(member_id: str, role: StoneRole) -> FamilyMember:
    """A member the document did not name.

    Real, minimal and deterministic: it references the primary stone and states
    no scale of its own, so the family's parameter supplies it.
    """

    return FamilyMember(memberId=member_id, role=role)


def _three_stone(family: FamilyDefinition) -> ArrangementDefinition:
    """A centre plus two sides.

    SYMMETRIC compiles to ONE side instance plus a `MIRROR` pattern, so the
    mirroring is performed by the arrangement engine rather than by arithmetic
    here — which is what guarantees a family's mirrored stone lands exactly
    where a hand-written mirrored arrangement's would. ASYMMETRIC places both
    sides explicitly, because there is nothing to mirror.
    """

    params = family.params
    assert isinstance(params, ThreeStoneParams)  # guaranteed by the discriminator

    grouped = _members_by_role(family)
    center = (grouped.get("CENTER") or [_derived_member(CENTER_MEMBER_ID, "CENTER")])[0]
    sides = grouped.get("SIDE") or [
        _derived_member(LEFT_MEMBER_ID, "SIDE"),
        _derived_member(RIGHT_MEMBER_ID, "SIDE"),
    ]
    if len(sides) != 2:
        raise FamilyRoleCardinalityError(
            f"A THREE_STONE family needs exactly 2 SIDE members, found {len(sides)}."
        )

    offset = params.sideSpacingMm
    instances = [_instance(center, InstanceTransform())]
    relations: list[ArrangementRelation] = []
    patterns: list[ArrangementPattern] = []

    if params.symmetry == "SYMMETRIC":
        # The first side by sorted id is placed; the second is its mirror.
        placed, mirrored = sides[0], sides[1]
        instances.append(
            _instance(
                placed,
                InstanceTransform(xMm=offset),
                default_scale=params.sideScale,
            )
        )
        patterns.append(
            ArrangementPattern(
                patternId=f"{placed.memberId}.mirror",
                sourceInstanceId=placed.memberId,
                spec=MirrorPatternSpec(plane="YZ"),
                memberRole="SIDE",
            )
        )
        # The mirror pattern generates the second side, so the document's own
        # second member is recorded as the pair's other half rather than
        # instantiated twice.
        relations.append(
            ArrangementRelation(
                relationId="three-stone.sides",
                kind="MIRRORED_PAIR",
                members=[placed.memberId, f"{placed.memberId}.mirror.1"],
                note=(
                    f"Symmetric three-stone sides. The document's second SIDE "
                    f"member ({mirrored.memberId!r}) is realized as this "
                    "mirror's generated member."
                ),
            )
        )
    else:
        left, right = sides
        instances.append(
            _instance(
                left,
                InstanceTransform(xMm=-offset),
                default_scale=params.sideScale,
            )
        )
        instances.append(
            _instance(
                right,
                InstanceTransform(xMm=offset),
                default_scale=params.sideScale,
            )
        )
        relations.append(
            ArrangementRelation(
                relationId="three-stone.sides",
                kind="ALIGNED_WITH",
                members=[left.memberId, right.memberId],
                note="Asymmetric three-stone sides: aligned, not mirrored.",
            )
        )

    return ArrangementDefinition(
        instances=instances, patterns=patterns, relations=relations
    )


def _toi_et_moi(family: FamilyDefinition) -> ArrangementDefinition:
    """Two stones set as a deliberate pair.

    Placed along `axisAngleDeg` at ±half the separation, so the pair straddles
    the design axis rather than sitting off to one side — which is what makes it
    a toi-et-moi rather than two stones that happen to be adjacent.

    BOTH STONES ARE PLACED EXPLICITLY, even when symmetric, and that is a
    correctness decision rather than a shortcut. The arrangement's `MIRROR`
    pattern reflects across a PRINCIPAL PLANE: mirroring a pair whose axis runs
    along Y across the YZ plane maps each stone onto itself, so a symmetric
    toi-et-moi at `axisAngleDeg = 90` collapsed both stones onto one point.
    Choosing the plane from the angle would only move the failure to the
    diagonal. What "symmetric" means here is a point reflection through the
    design centre, which no pattern expresses — so the pair is placed directly
    and the second stone's own orientation is flipped, which is what makes the
    two face each other rather than sit parallel.

    The `MIRRORED_PAIR` relation still records the intent, so a later edit or a
    future setting strategy can act on the relationship.
    """

    params = family.params
    assert isinstance(params, ToiEtMoiParams)

    grouped = _members_by_role(family)
    pair = grouped.get("SIDE") or [
        _derived_member(LEFT_MEMBER_ID, "SIDE"),
        _derived_member(RIGHT_MEMBER_ID, "SIDE"),
    ]
    if len(pair) != 2:
        raise FamilyRoleCardinalityError(
            f"A TOI_ET_MOI family needs exactly 2 SIDE members, found {len(pair)}."
        )

    half = params.separationMm / 2.0
    theta = math.radians(params.axisAngleDeg)
    dx = half * math.cos(theta)
    dy = half * math.sin(theta)

    first, second = pair
    instances = [_instance(first, InstanceTransform(xMm=-dx, yMm=-dy))]

    if params.symmetry == "SYMMETRIC":
        # The facing half of the pair: the same position reflected through the
        # centre, with its own orientation turned 180 degrees so a chiral stone
        # points back toward its partner instead of parallel to it.
        flipped = second.model_copy(
            update={
                "orientationDeg": _normalized_angle(
                    (second.orientationDeg or first.orientationDeg or 0.0) + 180.0
                )
            }
        )
        instances.append(_instance(flipped, InstanceTransform(xMm=dx, yMm=dy)))
        kind = "MIRRORED_PAIR"
        note = (
            "Symmetric toi-et-moi: the pair is a point reflection through the "
            "design centre, with the second stone's orientation flipped so the "
            "two face each other."
        )
    else:
        instances.append(_instance(second, InstanceTransform(xMm=dx, yMm=dy)))
        kind = "ALIGNED_WITH"
        note = "Asymmetric toi-et-moi: both stones placed from their own values."

    relations = [
        ArrangementRelation(
            relationId="toi-et-moi.pair",
            kind=kind,
            members=[first.memberId, second.memberId],
            note=note,
        )
    ]

    return ArrangementDefinition(instances=instances, patterns=[], relations=relations)


def _normalized_angle(degrees: float) -> float:
    """Fold an angle into [0, 360).

    Kept here rather than reusing the arrangement's own normalizer because this
    value is written into a MEMBER override, which the arrangement will
    normalize again on its own terms. Folding it now keeps it inside the
    model's own bounds.
    """

    return degrees % 360.0


def _radial_members(
    family: FamilyDefinition,
    role: StoneRole,
    count: int,
    radius: float,
    radius_y: float | None,
    start_angle: float,
    sweep: float,
    scale: float,
    align: bool,
) -> list[StoneInstanceDef]:
    """Ring members, placed explicitly.

    WHY NOT THE ARRANGEMENT'S RADIAL PATTERN. A pattern's generated members
    inherit their SOURCE instance's overrides, and the only instance sitting at
    the ring's centre is the centre STONE — whose scale is its own. Routing
    accents through a pattern therefore silently dropped their `memberScale`
    and produced full-size accents. Anchoring on a ring member instead
    reintroduces a duplicate stone at the start angle, because the pattern
    keeps its source and generates `count` more.

    So the ring is placed directly, using the SAME closed-form arithmetic the
    arrangement resolver applies to a radial pattern — a full sweep steps by
    `sweep / count` (at 360 degrees the last member would land on the first)
    and an arc by `sweep / (count - 1)` so both endpoints are included. These
    are still arrangement primitives: explicit instances, resolved and
    fingerprinted by the arrangement engine exactly like any others.

    Placing directly also lets a document name its own ring members and lets a
    ring be elliptical, neither of which a circular pattern can express.
    """

    grouped = _members_by_role(family)
    named = grouped.get(role, [])

    if count == 1:
        angles = [start_angle]
    elif sweep >= 360.0:
        angles = [start_angle + (sweep / count) * i for i in range(count)]
    else:
        angles = [start_angle + (sweep / (count - 1)) * i for i in range(count)]

    semi_y = radius if radius_y is None else radius_y
    instances: list[StoneInstanceDef] = []
    for index, angle in enumerate(angles):
        radians = math.radians(angle)
        member = (
            named[index]
            if index < len(named)
            else _derived_member(f"{ACCENT_MEMBER_PREFIX}.{index}", role)
        )
        instances.append(
            _instance(
                member,
                InstanceTransform(
                    xMm=radius * math.cos(radians),
                    yMm=semi_y * math.sin(radians),
                    rotationDeg=angle if align else 0.0,
                ),
                default_scale=scale,
            )
        )
    return instances


def _cluster(family: FamilyDefinition) -> ArrangementDefinition:
    """Stones grouped around an optional centre.

    Not necessarily circular and not necessarily centred: `radiusYMm` makes it
    elliptical, `sweepDeg` makes it an arc, and `includeCenter=False` makes it a
    ring of stones — each a real design rather than a degenerate case.
    """

    params = family.params
    assert isinstance(params, ClusterParams)

    instances: list[StoneInstanceDef] = []
    grouped = _members_by_role(family)

    center_id: str | None = None
    if params.includeCenter:
        center = (
            grouped.get("CENTER") or [_derived_member(CENTER_MEMBER_ID, "CENTER")]
        )[0]
        center_id = center.memberId
        instances.append(_instance(center, InstanceTransform()))

    ring = _radial_members(
        family,
        "ACCENT",
        params.count,
        params.radiusMm,
        params.radiusYMm,
        params.startAngleDeg,
        params.sweepDeg,
        params.memberScale,
        params.alignToRadius,
    )
    instances.extend(ring)

    relations: list[ArrangementRelation] = []
    if center_id is not None and ring:
        relations.append(
            ArrangementRelation(
                relationId="cluster.concentric",
                kind="CONCENTRIC_WITH",
                members=[center_id, ring[0].instanceId],
                note="The ring is concentric with the cluster's centre stone.",
            )
        )

    return ArrangementDefinition(
        instances=instances, patterns=[], relations=relations
    )


def _center_with_accents(family: FamilyDefinition) -> ArrangementDefinition:
    """A centre plus accents on an arc.

    The least specialized family: it exists so a design that is neither a
    strict three-stone nor a cluster still has a semantic home, instead of
    forcing one of the others to stretch.
    """

    params = family.params
    assert isinstance(params, CenterWithAccentsParams)

    grouped = _members_by_role(family)
    center = (grouped.get("CENTER") or [_derived_member(CENTER_MEMBER_ID, "CENTER")])[0]
    instances = [_instance(center, InstanceTransform())]

    accents = _radial_members(
        family,
        "ACCENT",
        params.accentCount,
        params.accentRadiusMm,
        None,
        params.accentStartAngleDeg,
        params.accentSweepDeg,
        params.accentScale,
        params.symmetry == "SYMMETRIC",
    )
    instances.extend(accents)

    relations = [
        ArrangementRelation(
            relationId="accents.concentric",
            kind="CONCENTRIC_WITH",
            members=[center.memberId, accents[0].instanceId],
            note="Accents are concentric with the centre stone.",
        )
    ]

    return ArrangementDefinition(
        instances=instances, patterns=[], relations=relations
    )


@lru_cache(maxsize=1)
def family_compilers() -> dict[str, FamilyCompiler]:
    """The family registry. Every entry compiles to a real arrangement."""

    return {
        "THREE_STONE": _three_stone,
        "TOI_ET_MOI": _toi_et_moi,
        "CLUSTER": _cluster,
        "CENTER_WITH_ACCENTS": _center_with_accents,
    }


def compile_family(family: FamilyDefinition | None) -> ArrangementDefinition | None:
    """Compile a family into the arrangement that expresses it.

    Returns `None` for `None`, which is the whole backward-compatibility story
    in one line: a design with no family compiles to no arrangement and behaves
    exactly as it did before this sprint. Nothing synthesizes a solitaire
    family for a single-stone design, because that would invent a declaration
    the document never made.
    """

    if family is None:
        return None

    compiler = family_compilers().get(family.familyType)
    if compiler is None:
        raise FamilyTypeUnsupportedError(
            f"No compiler is registered for family type {family.familyType!r}. "
            f"Registered: {sorted(family_compilers())}."
        )

    validate_roles(family)
    arrangement = compiler(family)

    if not arrangement.instances:
        raise FamilyMemberMissingError(
            f"A {family.familyType} family compiled to no stone instances. "
            "Raised rather than returning an empty arrangement, which would "
            "silently produce a design with no stones."
        )
    if len(arrangement.instances) > MAX_FAMILY_MEMBERS:
        raise FamilyCapacityExceededError(
            f"Compiling this family produced {len(arrangement.instances)} "
            f"instances, above the software bound of {MAX_FAMILY_MEMBERS}. An "
            "implementation limit, not a statement about how many stones a "
            "design should have."
        )
    if len(arrangement.instances) > MAX_INSTANCES:  # pragma: no cover - defence
        raise FamilyCapacityExceededError(
            "Compiling this family exceeded the arrangement instance bound."
        )

    return arrangement


def family_types() -> tuple[str, ...]:
    """Family types with a real compiler. Derived, never restated."""

    return tuple(sorted(family_compilers()))
