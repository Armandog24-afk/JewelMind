"""Deterministic resolution: declarative arrangement -> explicit placements.

THE ONE PLACE PATTERN EXPANSION AND FRAME COMPOSITION HAPPEN. Every downstream
consumer — Atlas, Vision, Foundry, Forge — reads a `ResolvedArrangement` and
never the raw definition, so this arithmetic exists once. A second consumer
doing its own expansion would eventually disagree with this one, and the
disagreement would surface as geometry that does not match the preview.

DIRECT EVALUATION, NOT SOLVING. Resolution is a single pass in a fixed order:
validate references, expand patterns, compose group frames, sort by ID. No
iteration to convergence, no dependency search, no fixpoint. That is what makes
the output a pure function of the input — the determinism requirement — and it
is why placement relative to another INSTANCE is deliberately left PLANNED:
that needs a dependency order, and a cyclic reference has no determinate answer.

REJECTS, NEVER REPAIRS. A missing reference, a duplicate ID or an impossible
pattern raises. Filling in a plausible value would produce an arrangement nobody
authored (the discipline Sprint 20 set for custom outlines).

KERNEL-FREE. Nothing here imports CadQuery, any geometry module, or any jewelry
category. The output is numbers.
"""

from __future__ import annotations

import math
import re

from jewelmind.arrangement.capability import RESOLVER_VERSION
from jewelmind.arrangement.errors import (
    ArrangementCapacityExceededError,
    ArrangementIdInvalidError,
    ArrangementPatternInvalidError,
    ArrangementRelationInvalidError,
    DuplicateInstanceIdError,
    UnresolvedGroupReferenceError,
    UnresolvedInstanceReferenceError,
)
from jewelmind.arrangement.models import (
    ARRANGEMENT_ID_PATTERN,
    MAX_ARRANGEMENT_ID_LENGTH,
    MAX_INSTANCES,
    ArrangementDefinition,
    ArrangementGroup,
    ArrangementPattern,
    InstancePlacement,
    InstanceTransform,
    LinearPatternSpec,
    MirrorPatternSpec,
    RadialPatternSpec,
    ResolvedArrangement,
    ResolvedInstance,
    StoneInstanceDef,
)
from jewelmind.arrangement.normalize import (
    arrangement_fingerprint,
    normalize_angle_deg,
    normalize_definition,
    normalize_transform,
)

#: Relation kinds that mean exactly two participants. Checked here rather than
#: in the model because arity is a semantic property of the KIND, and a single
#: `min_length=2` on the field cannot express "exactly 2 for this kind, 2 or
#: more for that one".
_EXACT_PAIR_RELATIONS = frozenset({"MIRRORED_PAIR"})

#: Compiled once. Used to validate DERIVED ids, which never pass through field
#: validation because `model_copy(update=...)` does not re-validate.
_ID_RE = re.compile(ARRANGEMENT_ID_PATTERN)


def _compose(parent: InstanceTransform, child: InstanceTransform) -> InstanceTransform:
    """Compose a child transform into its parent's frame.

    Rotation composes additively, and the child's translation is rotated by the
    parent's angle before being added — the ordinary rigid composition, spelled
    out because getting it backwards would silently mirror a group's contents.

    Only the vertical-axis rotation exists (see `InstanceTransform`), so this is
    a 2D rotation in XY plus a Z translation, not a general 3×3 product.
    """

    theta = math.radians(parent.rotationDeg)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    return InstanceTransform(
        xMm=parent.xMm + child.xMm * cos_t - child.yMm * sin_t,
        yMm=parent.yMm + child.xMm * sin_t + child.yMm * cos_t,
        zMm=parent.zMm + child.zMm,
        rotationDeg=normalize_angle_deg(parent.rotationDeg + child.rotationDeg),
    )


def _linear_offsets(spec: LinearPatternSpec) -> list[InstanceTransform]:
    """Member offsets for a linear run, in member order.

    Member order is index order along the direction vector, which is stable and
    independent of how the pattern was authored. When `centered`, the run is
    symmetric about the anchor: an odd count puts one member exactly on it, an
    even count straddles it.
    """

    theta = math.radians(spec.directionDeg)
    ux = math.cos(theta)
    uy = math.sin(theta)
    if spec.centered:
        start = -spec.spacingMm * (spec.count - 1) / 2.0
    else:
        start = 0.0
    offsets: list[InstanceTransform] = []
    for index in range(spec.count):
        distance = start + spec.spacingMm * index
        offsets.append(InstanceTransform(xMm=distance * ux, yMm=distance * uy))
    return offsets


def _radial_offsets(spec: RadialPatternSpec) -> list[InstanceTransform]:
    """Member offsets around a circle, in increasing-angle order.

    A FULL SWEEP AND A PARTIAL ARC DISTRIBUTE DIFFERENTLY, and the difference
    matters. At 360° the last member would land on the first, so the step is
    `sweep / count`. On a partial arc both endpoints are wanted, so the step is
    `sweep / (count - 1)`. Using one formula for both would either double a
    stone at 0° or leave an arc short of its stated end.
    """

    if spec.count == 1:
        # A single member sits at the start angle; neither divisor applies.
        angles = [spec.startAngleDeg]
    elif spec.sweepDeg >= 360.0:
        step = spec.sweepDeg / spec.count
        angles = [spec.startAngleDeg + step * i for i in range(spec.count)]
    else:
        step = spec.sweepDeg / (spec.count - 1)
        angles = [spec.startAngleDeg + step * i for i in range(spec.count)]

    offsets: list[InstanceTransform] = []
    for angle in angles:
        radians = math.radians(angle)
        offsets.append(
            InstanceTransform(
                xMm=spec.radiusMm * math.cos(radians),
                yMm=spec.radiusMm * math.sin(radians),
                # Facing outward means the member's own rotation follows its
                # angular position; otherwise every member keeps the source's.
                rotationDeg=normalize_angle_deg(angle) if spec.alignToRadius else 0.0,
            )
        )
    return offsets


def _mirror_offset(
    spec: MirrorPatternSpec, source: InstanceTransform
) -> tuple[InstanceTransform, float]:
    """The reflected transform, and the orientation flip that accompanies it.

    Reflection is applied to the SOURCE'S ABSOLUTE POSITION rather than as a
    relative offset, because a mirror is defined by a plane through the origin,
    not by a displacement. The orientation flip is returned separately because
    it belongs to the stone's own orientation override, not to the placement:
    reflecting a chiral stone (pear, marquise, half moon) without flipping its
    orientation produces a rotation, not a mirror image.
    """

    if spec.plane == "YZ":
        mirrored = InstanceTransform(
            xMm=-source.xMm,
            yMm=source.yMm,
            zMm=source.zMm,
            rotationDeg=normalize_angle_deg(180.0 - source.rotationDeg),
        )
        flip = 180.0
    else:  # "XZ"
        mirrored = InstanceTransform(
            xMm=source.xMm,
            yMm=-source.yMm,
            zMm=source.zMm,
            rotationDeg=normalize_angle_deg(-source.rotationDeg),
        )
        flip = 0.0
    return mirrored, flip


def _member_id(pattern_id: str, index: int) -> str:
    """A generated member's ID: derived, deterministic, and collision-checked.

    Derived from the pattern ID and the member index so re-resolving the same
    pattern produces the same IDs — a UUID here would break the determinism
    requirement outright, and would make a stored resolution impossible to
    compare with a fresh one.

    VALIDATED, not merely constructed. `model_copy(update=...)` does not
    re-run field validation, so a derived ID that failed the pattern would exist
    happily in memory and only fail later, when the arrangement was serialized
    to JDL. That is exactly the inconsistency this check exists to make
    impossible.
    """

    member_id = f"{pattern_id}.{index}"
    if not _ID_RE.match(member_id) or len(member_id) > MAX_ARRANGEMENT_ID_LENGTH:
        raise ArrangementIdInvalidError(
            f"pattern {pattern_id!r} would derive the member id {member_id!r}, which "
            "is not a valid arrangement identifier. Shorten the pattern id."
        )
    return member_id


def _expand_pattern(
    pattern: ArrangementPattern,
    source: StoneInstanceDef,
    group_by_id: dict[str, ArrangementGroup],
) -> list[StoneInstanceDef]:
    """The instances a pattern generates, excluding its source.

    The source instance is never re-emitted: it already exists in the
    definition, and duplicating it would double a stone at the anchor.
    """

    spec = pattern.spec
    if pattern.groupId is not None and pattern.groupId not in group_by_id:
        raise UnresolvedGroupReferenceError(
            f"pattern {pattern.patternId!r} names group {pattern.groupId!r}, "
            "which does not exist."
        )

    generated: list[StoneInstanceDef] = []

    if isinstance(spec, MirrorPatternSpec):
        mirrored, flip = _mirror_offset(spec, source.placement.transform)
        orientation = source.overrides.orientationDeg
        if spec.mirrorOrientation:
            base = orientation if orientation is not None else 0.0
            orientation = normalize_angle_deg(flip - base)
        generated.append(
            source.model_copy(
                update={
                    "instanceId": _member_id(pattern.patternId, 1),
                    "role": pattern.memberRole,
                    "sourcePatternId": pattern.patternId,
                    "overrides": source.overrides.model_copy(
                        update={"orientationDeg": orientation}
                    ),
                    "placement": InstancePlacement(
                        mode="PATTERN_MEMBER",
                        frame=source.placement.frame,
                        transform=mirrored,
                        groupId=pattern.groupId or source.placement.groupId,
                    ),
                }
            )
        )
        return generated

    if isinstance(spec, LinearPatternSpec):
        offsets = _linear_offsets(spec)
    elif isinstance(spec, RadialPatternSpec):
        offsets = _radial_offsets(spec)
    else:  # pragma: no cover - the union is closed and discriminated
        raise ArrangementPatternInvalidError(
            f"pattern {pattern.patternId!r} has an unrecognized kind."
        )

    anchor = source.placement.transform
    for index, offset in enumerate(offsets):
        if spec.count > 1 and index == 0 and _is_anchor_offset(spec, offset):
            # The first member of a non-centred run coincides with the source;
            # emitting it would place two stones at one point.
            continue
        transform = InstanceTransform(
            xMm=anchor.xMm + offset.xMm,
            yMm=anchor.yMm + offset.yMm,
            zMm=anchor.zMm + offset.zMm,
            rotationDeg=normalize_angle_deg(anchor.rotationDeg + offset.rotationDeg),
        )
        generated.append(
            source.model_copy(
                update={
                    "instanceId": _member_id(pattern.patternId, index),
                    "role": pattern.memberRole,
                    "sourcePatternId": pattern.patternId,
                    "placement": InstancePlacement(
                        mode="PATTERN_MEMBER",
                        frame=source.placement.frame,
                        transform=transform,
                        groupId=pattern.groupId or source.placement.groupId,
                    ),
                }
            )
        )
    return generated


def _is_anchor_offset(
    spec: LinearPatternSpec | RadialPatternSpec, offset: InstanceTransform
) -> bool:
    """Whether a member's offset is the zero offset, i.e. the anchor itself.

    Only a non-centred linear run has one: a centred run's first member is
    displaced, and a radial run's members sit on a circle of positive radius.
    """

    return (
        isinstance(spec, LinearPatternSpec)
        and not spec.centered
        and offset.xMm == 0.0
        and offset.yMm == 0.0
        and offset.zMm == 0.0
    )


def _validate_relations(
    definition: ArrangementDefinition, known_ids: set[str], group_ids: set[str]
) -> None:
    """Every relation member must name a real instance or group.

    Checked AFTER pattern expansion, so a relation may legitimately reference a
    generated member by its derived ID.
    """

    for relation in definition.relations:
        if len(set(relation.members)) != len(relation.members):
            raise ArrangementRelationInvalidError(
                f"relation {relation.relationId!r} lists the same member twice; a "
                "relationship between a thing and itself has no meaning."
            )
        if relation.kind in _EXACT_PAIR_RELATIONS and len(relation.members) != 2:
            raise ArrangementRelationInvalidError(
                f"relation {relation.relationId!r} of kind {relation.kind} requires "
                f"exactly 2 members, got {len(relation.members)}."
            )
        for member in relation.members:
            if member not in known_ids and member not in group_ids:
                raise UnresolvedInstanceReferenceError(
                    f"relation {relation.relationId!r} references {member!r}, which is "
                    "neither an instance nor a group in this arrangement."
                )


def resolve_arrangement(definition: ArrangementDefinition) -> ResolvedArrangement:
    """Resolve a declarative arrangement into explicit placements.

    Order is fixed and load-bearing:

    1. normalize (canonical ordering, so the result cannot depend on input order)
    2. reject duplicate instance IDs
    3. expand patterns (a pattern's source must already exist)
    4. compose group frames into absolute placements
    5. validate relations against the post-expansion ID set
    6. sort by instance ID

    Every instance comes back `NOT_GENERATED`: resolution has no opinion about
    what a geometry pipeline can build. The compilation boundary
    (`compile.py`) sets generation status, which is what keeps this function a
    pure function of its input.
    """

    normalized = normalize_definition(definition)

    instance_by_id: dict[str, StoneInstanceDef] = {}
    for instance in normalized.instances:
        if instance.instanceId in instance_by_id:
            raise DuplicateInstanceIdError(
                f"instance id {instance.instanceId!r} is declared more than once. IDs "
                "are the authoritative identity, so a duplicate makes every reference "
                "to it ambiguous."
            )
        instance_by_id[instance.instanceId] = instance

    group_by_id = {group.groupId: group for group in normalized.groups}

    for instance in normalized.instances:
        group_id = instance.placement.groupId
        if group_id is not None and group_id not in group_by_id:
            raise UnresolvedGroupReferenceError(
                f"instance {instance.instanceId!r} names group {group_id!r}, which "
                "does not exist."
            )

    expanded: list[StoneInstanceDef] = list(normalized.instances)
    pattern_expanded_count = 0
    for pattern in normalized.patterns:
        source = instance_by_id.get(pattern.sourceInstanceId)
        if source is None:
            raise UnresolvedInstanceReferenceError(
                f"pattern {pattern.patternId!r} repeats instance "
                f"{pattern.sourceInstanceId!r}, which does not exist."
            )
        members = _expand_pattern(pattern, source, group_by_id)
        for member in members:
            if member.instanceId in instance_by_id:
                raise DuplicateInstanceIdError(
                    f"pattern {pattern.patternId!r} would generate instance id "
                    f"{member.instanceId!r}, which already exists. Rename the pattern "
                    "or the conflicting instance."
                )
            instance_by_id[member.instanceId] = member
        expanded.extend(members)
        pattern_expanded_count += len(members)

    if len(expanded) > MAX_INSTANCES:
        raise ArrangementCapacityExceededError(
            f"resolution would produce {len(expanded)} instances, above the software "
            f"bound of {MAX_INSTANCES}. This is an implementation limit, not a "
            "statement about how many stones a design should have."
        )

    resolved_instances: list[ResolvedInstance] = []
    for instance in expanded:
        transform = instance.placement.transform
        group_id = instance.placement.groupId
        if instance.placement.frame == "PARENT_GROUP":
            # `frame == PARENT_GROUP` is only constructible with a groupId (the
            # model enforces it) and the group's existence was checked above.
            parent = group_by_id[str(group_id)]
            transform = _compose(parent.transform, transform)
        resolved_instances.append(
            ResolvedInstance(
                instanceId=instance.instanceId,
                stoneRef=instance.stoneRef,
                role=instance.role,
                transform=normalize_transform(transform),
                overrides=instance.overrides,
                gem=instance.gem,
                sourcePatternId=instance.sourcePatternId,
                groupId=group_id,
                generationStatus="NOT_GENERATED",
                generationNote=(
                    "Resolution reports placement only; generation status is set by "
                    "the compilation boundary."
                ),
            )
        )

    _validate_relations(
        normalized, set(instance_by_id), set(group_by_id)
    )

    resolved_instances.sort(key=lambda i: i.instanceId)

    return ResolvedArrangement(
        instances=resolved_instances,
        relations=list(normalized.relations),
        arrangementFingerprint=arrangement_fingerprint(definition),
        resolverVersion=RESOLVER_VERSION,
        instanceCount=len(resolved_instances),
        generatedCount=0,
        patternExpandedCount=pattern_expanded_count,
        notes=[],
    )
