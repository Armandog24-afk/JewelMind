"""Halo semantics -> arrangement primitives (Sprint 25).

THE ONLY TRANSFORMATION IN THIS LAYER, and it deliberately produces an
`ArrangementDefinition` rather than positions of its own. Stone Arrangement
Engine v1 remains the sole authority on placement: this module chooses which
arrangement primitives express a halo, and the arrangement resolver then does
the arithmetic exactly as it does for a hand-written arrangement.

A HALO COMPOSES, it does not replace. `compose_halo()` takes whatever placement
the design already declares — a compiled family, an explicit arrangement, or
nothing — and returns that same structure with the halo's rings added. This is
what makes "three-stone with a halo around the centre" one design rather than a
choice between two, and it is why a halo is not a fifth family type. See
`docs/bible/27-halo/halo-rfc.md`.

THE CENTRE IS RESOLVED, NEVER GUESSED. A named `centerMemberId` must exist in
the arrangement being composed onto; if it does not, composition is refused
rather than quietly re-anchored on the origin, because a halo around the wrong
stone is worse than a halo that fails loudly. `centerMemberId: null` anchors on
the design origin, which is how a halo surrounds a multi-stone centre.

REJECTS, NEVER REPAIRS. A missing centre, a colliding id, an unsupported
composition or an over-capacity halo raises. Inventing a plausible ring would
produce a design nobody authored — the discipline Sprint 20 set for outlines,
Sprint 22 for arrangements and Sprint 24 for families.

KERNEL-FREE. Nothing here imports CadQuery, any geometry module, or any jewelry
category. The output is arrangement data.
"""

from __future__ import annotations

import math

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
from jewelmind.family.models import FamilyMember
from jewelmind.halo.errors import (
    HaloCapacityExceededError,
    HaloCenterUnresolvedError,
    HaloIdentityCollisionError,
)
from jewelmind.halo.models import (
    MAX_HALO_STONES,
    HaloDefinition,
    HaloRing,
)

#: The role every halo stone carries. A halo stone is not an accent: `ACCENT`
#: describes a stone placed for decoration anywhere on the piece, while `HALO`
#: describes one participating in a ring around a centre. Keeping them distinct
#: is what lets a consumer ask "what surrounds the centre stone?" without
#: inspecting coordinates. `StoneRole` has carried `HALO` since Sprint 21.
HALO_ROLE = "HALO"

#: The role the synthesized centre carries when a halo is declared without any
#: family or arrangement to supply one.
CENTER_ROLE = "CENTER"


def _derived_member_id(ring_id: str, index: int) -> str:
    """A halo stone's id when the document does not name it.

    DERIVED, never random and never a counter across rings: `halo.inner.0` is
    reproducible from the ring's own id and the stone's position in the ring's
    angular sequence, so re-compiling the same halo reproduces the same ids and
    a stored compilation can be compared with a fresh one.
    """

    return f"{ring_id}.{index}"


def _ring_instances(
    ring: HaloRing, anchor: InstanceTransform
) -> list[StoneInstanceDef]:
    """One ring of stones, placed explicitly around `anchor`.

    WHY EXPLICIT RATHER THAN A `RADIAL` PATTERN — the same reason Sprint 24's
    family rings are explicit, and it was a real defect there before it was a
    design note: a pattern's generated members inherit their SOURCE instance's
    overrides, and the only instance at a halo's centre is the CENTRE stone,
    whose scale is its own. Routing a halo through a pattern would silently
    discard `memberScale` and produce full-size halo stones. Anchoring the
    pattern on a ring member instead reintroduces a duplicate stone at the start
    angle, because a pattern keeps its source and generates `count` more.

    These are still arrangement primitives — explicit instances, resolved,
    normalized and fingerprinted by the arrangement engine exactly like any
    others — and the angular sequence comes from `arrangement/radial.py`, the
    same function the resolver uses for a `RADIAL` pattern, so a halo's stones
    sit exactly where a hand-written pattern's would.

    Placing explicitly also lets a ring be elliptical, be an arc, carry a
    vertical offset and name its own members, none of which a circular pattern
    expresses.
    """

    angles = ring_angles_deg(ring.count, ring.startAngleDeg, ring.sweepDeg)
    semi_y = ring.radiusMm if ring.radiusYMm is None else ring.radiusYMm

    # Named members are matched to positions by SORTED ID, never by array order,
    # so reordering the `members` list cannot move a stone.
    named = sorted(ring.members, key=lambda m: m.memberId)

    instances: list[StoneInstanceDef] = []
    for index, angle in enumerate(angles):
        radians = math.radians(angle)
        member: FamilyMember | None = named[index] if index < len(named) else None

        member_id = (
            member.memberId if member is not None else _derived_member_id(ring.ringId, index)
        )
        scale = ring.memberScale
        orientation: float | None = None
        stone_ref = ring.stoneRef
        gem = ring.gem
        override: InstanceTransform | None = None
        if member is not None:
            # The member's own values win over the ring's defaults, so a single
            # unusual halo stone does not require abandoning the ring's
            # parameters. Its gem and stone reference fall back to the ring's
            # rather than to the design's, because the ring is the closer
            # declaration.
            scale = member.scale if member.scale is not None else ring.memberScale
            orientation = member.orientationDeg
            stone_ref = member.stoneRef if member.stoneRef != "primary" else ring.stoneRef
            gem = member.gem if member.gem is not None else ring.gem
            override = member.placementOverride

        # The anchor contributes TRANSLATION only. Its own rotation belongs to
        # the centre stone's orientation, not to the halo's angular layout —
        # composing it in would swing the whole ring whenever the centre stone
        # was turned, which is not what a halo does.
        derived = InstanceTransform(
            xMm=anchor.xMm + ring.radiusMm * math.cos(radians),
            yMm=anchor.yMm + semi_y * math.sin(radians),
            zMm=anchor.zMm + ring.zOffsetMm,
            rotationDeg=angle if ring.alignToRadius else 0.0,
        )

        instances.append(
            StoneInstanceDef(
                instanceId=member_id,
                stoneRef=stone_ref,
                role=HALO_ROLE,
                gem=gem,
                overrides=InstanceOverrides(scale=scale, orientationDeg=orientation),
                placement=InstancePlacement(transform=override or derived),
            )
        )
    return instances


def _anchor_transform(
    base: ArrangementDefinition | None, halo: HaloDefinition
) -> tuple[InstanceTransform, str | None]:
    """Where the halo's centre is, and which instance it is.

    Three cases, and none of them guesses:

    - `centerMemberId is None` — the DESIGN ORIGIN. This is how a halo surrounds
      a multi-stone centre: a toi-et-moi pair straddles the origin, so a ring
      centred there encircles both stones rather than one of them.
    - a named centre with an arrangement to look in — resolved by id. Absent is
      an error, never a fallback.
    - a named centre with nothing to look in — the halo's own declaration IS the
      statement that a centre exists, so one instance is synthesized at the
      origin. That is not inventing an undeclared design: a halo with no centre
      is not a halo, and this is the ordinary solitaire-plus-halo case.
    """

    if halo.centerMemberId is None:
        return InstanceTransform(), None

    if base is None:
        return InstanceTransform(), halo.centerMemberId

    for instance in base.instances:
        if instance.instanceId == halo.centerMemberId:
            return instance.placement.transform, instance.instanceId

    known = sorted(i.instanceId for i in base.instances)
    raise HaloCenterUnresolvedError(
        f"This halo surrounds '{halo.centerMemberId}', which this design's "
        f"arrangement does not contain. Declared instances: "
        f"{', '.join(known) or '(none)'}. Name an existing instance, or set "
        "centerMemberId to null to anchor the halo on the design origin (which "
        "is how a halo surrounds a multi-stone centre)."
    )


def compose_halo(
    base: ArrangementDefinition | None, halo: HaloDefinition | None
) -> ArrangementDefinition | None:
    """Add a halo's rings to the arrangement a design already declares.

    Returns `base` unchanged for `None`, which is the whole
    backward-compatibility story in one line: a design with no halo composes to
    exactly the arrangement it had before this sprint, and a design with neither
    a halo nor anything else still composes to `None`.
    """

    if halo is None:
        return base

    anchor, center_id = _anchor_transform(base, halo)

    existing_ids = {i.instanceId for i in base.instances} if base is not None else set()
    instances: list[StoneInstanceDef] = list(base.instances) if base is not None else []
    relations: list[ArrangementRelation] = (
        list(base.relations) if base is not None else []
    )

    # The synthesized centre, for a halo declared without a family or an
    # arrangement. It keeps the `CENTER` role, so `arrangement/compile.py`'s
    # deterministic primary selection picks it and the centre stone keeps the
    # historical bare `stone_reference` component name.
    if center_id is not None and center_id not in existing_ids:
        instances.append(
            StoneInstanceDef(
                instanceId=center_id,
                stoneRef="primary",
                role=CENTER_ROLE,
                placement=InstancePlacement(transform=InstanceTransform()),
            )
        )
        existing_ids.add(center_id)

    # Rings are processed in sorted-id order so composition never depends on the
    # order they happen to appear in the document.
    ring_anchors: list[tuple[str, str]] = []
    halo_stone_count = 0
    for ring in sorted(halo.rings, key=lambda r: r.ringId):
        ring_instances = _ring_instances(ring, anchor)
        for instance in ring_instances:
            if instance.instanceId in existing_ids:
                raise HaloIdentityCollisionError(
                    f"Halo ring '{ring.ringId}' would create instance "
                    f"'{instance.instanceId}', which this design's arrangement "
                    "already declares. Ids are the authoritative identity, so a "
                    "collision would make every reference to it ambiguous — "
                    "rename the halo ring or the existing instance."
                )
            existing_ids.add(instance.instanceId)
        instances.extend(ring_instances)
        halo_stone_count += len(ring_instances)
        ring_anchors.append((ring.ringId, ring_instances[0].instanceId))

    if halo_stone_count > MAX_HALO_STONES:  # pragma: no cover - model bound first
        raise HaloCapacityExceededError(
            f"This halo composed to {halo_stone_count} stones, above the "
            f"software bound of {MAX_HALO_STONES}."
        )
    if len(instances) > MAX_INSTANCES:
        raise HaloCapacityExceededError(
            f"Composing this halo produced {len(instances)} instances, above "
            f"the arrangement bound of {MAX_INSTANCES}. A software limit, not a "
            "statement about how many stones a design should have."
        )

    # RELATIONS RECORD THE INTENT so a later edit, a Studio grouped operation or
    # a future halo-aware setting strategy can act on the relationship instead
    # of re-deriving it from coordinates that happen to look concentric.
    for ring_id, first_member in ring_anchors:
        if center_id is not None:
            relations.append(
                ArrangementRelation(
                    relationId=f"{ring_id}.concentric",
                    kind="CONCENTRIC_WITH",
                    members=[center_id, first_member],
                    note=(
                        f"Halo ring '{ring_id}' is concentric with the centre "
                        f"stone '{center_id}'."
                    ),
                )
            )

    if center_id is None and len(ring_anchors) >= 2:
        # No named centre to relate to, so the rings' concentricity with each
        # other is what remains true and worth recording.
        relations.append(
            ArrangementRelation(
                relationId="halo.rings.concentric",
                kind="CONCENTRIC_WITH",
                members=[member for _ring_id, member in ring_anchors],
                note=(
                    "Halo rings are concentric with each other, anchored on the "
                    "design origin rather than on a named centre stone."
                ),
            )
        )

    if base is None:
        return ArrangementDefinition(instances=instances, relations=relations)

    return base.model_copy(update={"instances": instances, "relations": relations})


def halo_variants() -> tuple[str, ...]:
    """Halo variants this compiler executes. Derived, never restated."""

    from jewelmind.halo.models import HALO_RING_CARDINALITY

    return tuple(sorted(HALO_RING_CARDINALITY))
