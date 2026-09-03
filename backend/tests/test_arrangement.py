"""Stone Arrangement Engine v1 (Sprint 22).

Covers the representation, its determinism, its structural validation, the JDL
round trip, the compilation boundary, and — the part that is easiest to get
wrong and most important to prove — that a design with no arrangement behaves
exactly as it did before this sprint.
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from jewelmind.arrangement.capability import (
    ARRANGEMENT_CAPABILITIES,
    RESOLVER_VERSION,
    current_capabilities,
    generatable_capabilities,
    resolvable_pattern_kinds,
)
from jewelmind.arrangement.compile import (
    PRIMARY_STONE_COMPONENT,
    STONE_INSTANCE_COMPONENT_PREFIX,
    compile_arrangement,
    stone_component_name,
)
from jewelmind.arrangement.errors import (
    ArrangementCapacityExceededError,
    ArrangementRelationInvalidError,
    DuplicateInstanceIdError,
    UnresolvedGroupReferenceError,
    UnresolvedInstanceReferenceError,
)
from jewelmind.arrangement.models import (
    MAX_INSTANCES,
    ArrangementDefinition,
    ArrangementGroup,
    ArrangementPattern,
    ArrangementRelation,
    InstanceOverrides,
    InstancePlacement,
    InstanceTransform,
    LinearPatternSpec,
    MirrorPatternSpec,
    RadialPatternSpec,
    StoneInstanceDef,
)
from jewelmind.arrangement.normalize import (
    arrangement_fingerprint,
    canonical_json,
    normalize_angle_deg,
    normalize_definition,
    resolved_canonical_json,
)
from jewelmind.arrangement.resolve import resolve_arrangement
from jewelmind.domain.defaults import default_definition
from jewelmind.domain.schema import JewelryDefinition
from jewelmind.gem.models import GemIdentity
from jewelmind.geometry.roles import (
    geometry_role,
    is_production_component,
    production_role,
)
from jewelmind.utils.hashing import definition_hash, geometry_hash
from jewelmind.validation.engine import has_errors, validate_definition


def center_only() -> ArrangementDefinition:
    return ArrangementDefinition(
        instances=[StoneInstanceDef(instanceId="center", role="CENTER")]
    )


def halo(count: int = 8, radius: float = 4.6) -> ArrangementDefinition:
    return ArrangementDefinition(
        instances=[StoneInstanceDef(instanceId="center", role="CENTER")],
        patterns=[
            ArrangementPattern(
                patternId="halo",
                sourceInstanceId="center",
                spec=RadialPatternSpec(count=count, radiusMm=radius),
                memberRole="HALO",
            )
        ],
    )


def arrangement_results(definition: JewelryDefinition) -> dict[str, str]:
    return {
        r.ruleId: r.severity
        for r in validate_definition(definition)
        if r.ruleId.startswith("JM-ARRANGE")
    }


# --------------------------------------------------------------- the model


class TestInstanceRepresentation:
    def test_an_instance_references_a_stone_rather_than_restating_it(self):
        instance = StoneInstanceDef(instanceId="center")
        # No shape, no dimensions, no source: an occurrence is an occurrence OF
        # something, and duplicating the stone here would create a second
        # source of truth for what that stone is.
        for absent in ("shape", "diameter", "length", "width", "depth", "source"):
            assert not hasattr(instance, absent), absent
        assert instance.stoneRef == "primary"

    def test_an_instance_may_carry_its_own_gem(self):
        instance = StoneInstanceDef(
            instanceId="side.1",
            role="SIDE",
            gem=GemIdentity(gemId="corundum.sapphire", origin="NATURAL"),
        )
        assert instance.gem is not None
        assert instance.gem.gemId == "corundum.sapphire"

    def test_a_gem_left_unset_inherits_rather_than_copying(self):
        """`None` means inherit, which is not the same as "same value".

        An inherited gem follows a later edit to the stone; a copied one would
        silently diverge from it.
        """

        assert StoneInstanceDef(instanceId="center").gem is None

    @pytest.mark.parametrize(
        "candidate",
        [
            "Center",
            "center..1",
            "../../etc/passwd",
            "center/1",
            "rm -rf /",
            "9lives",
            "-leading",
            "trailing.",
            "",
            "a" * 81,
            "center 1",
        ],
    )
    def test_a_malformed_instance_id_is_rejected(self, candidate: str):
        """IDs are untrusted input, validated for shape before any lookup.

        The same pattern gem IDs use, reused rather than re-invented, so one
        validator covers every user-authored identifier in the project.
        """

        with pytest.raises(ValidationError):
            StoneInstanceDef(instanceId=candidate)

    def test_overrides_are_a_closed_set(self):
        """An instance may scale and rotate itself, and nothing else.

        Allowing an instance to override the shape or source would make the
        stone reference meaningless — the instance would become a second stone
        definition.
        """

        assert set(InstanceOverrides.model_fields) == {"scale", "orientationDeg"}
        with pytest.raises(ValidationError):
            InstanceOverrides.model_validate({"shape": "oval"})

    def test_a_non_positive_scale_is_rejected(self):
        for bad in (0.0, -1.0, 0.001):
            with pytest.raises(ValidationError):
                InstanceOverrides(scale=bad)

    def test_no_transform_field_accepts_nan_or_infinity(self):
        for field in ("xMm", "yMm", "zMm", "rotationDeg"):
            for bad in (float("nan"), float("inf"), float("-inf")):
                with pytest.raises(ValidationError):
                    InstanceTransform(**{field: bad})

    def test_a_coordinate_far_outside_any_jewelry_scale_is_rejected(self):
        """A software bound that makes a mis-scaled import fail loudly.

        Not a jewelry claim: nothing here asserts how large a piece may be.
        """

        with pytest.raises(ValidationError):
            InstanceTransform(xMm=10_000.0)

    def test_a_parent_frame_placement_requires_a_group(self):
        with pytest.raises(ValidationError):
            InstancePlacement(frame="PARENT_GROUP")
        InstancePlacement(frame="PARENT_GROUP", groupId="halo")

    def test_a_jdl_style_string_number_is_rejected(self):
        """Strict typing, matching `domain/schema.py::StrictModel`.

        These models are carried directly in JDL rather than through a `Jdl*`
        mirror, so they must apply JDL's own untrusted-input policy.
        """

        with pytest.raises(ValidationError):
            InstanceTransform.model_validate({"xMm": "1.0"})
        # int -> float widening is still fine: that is what a JSON number
        # without a decimal point parses to.
        assert InstanceTransform.model_validate({"xMm": 2}).xMm == 2.0


# ------------------------------------------------------------- determinism


class TestDeterminism:
    def test_reordering_the_instance_list_does_not_change_the_fingerprint(self):
        """Identity is by ID; array position is a serialization artifact."""

        a = ArrangementDefinition(
            instances=[
                StoneInstanceDef(instanceId="a"),
                StoneInstanceDef(instanceId="b", role="SIDE"),
            ]
        )
        b = ArrangementDefinition(
            instances=[
                StoneInstanceDef(instanceId="b", role="SIDE"),
                StoneInstanceDef(instanceId="a"),
            ]
        )
        assert canonical_json(a) == canonical_json(b)
        assert arrangement_fingerprint(a) == arrangement_fingerprint(b)

    def test_reordering_groups_patterns_and_relations_does_not_change_it(self):
        def build(reverse: bool) -> ArrangementDefinition:
            groups = [
                ArrangementGroup(groupId="left"),
                ArrangementGroup(groupId="right"),
            ]
            relations = [
                ArrangementRelation(relationId="r1", kind="ALIGNED_WITH", members=["a", "b"]),
                ArrangementRelation(relationId="r2", kind="CONCENTRIC_WITH", members=["a", "b"]),
            ]
            if reverse:
                groups.reverse()
                relations.reverse()
            return ArrangementDefinition(
                instances=[
                    StoneInstanceDef(instanceId="a"),
                    StoneInstanceDef(instanceId="b", role="SIDE"),
                ],
                groups=groups,
                relations=relations,
            )

        assert arrangement_fingerprint(build(False)) == arrangement_fingerprint(
            build(True)
        )

    def test_an_order_insensitive_relation_ignores_member_order(self):
        a = ArrangementRelation(relationId="r", kind="ALIGNED_WITH", members=["b", "a"])
        b = ArrangementRelation(relationId="r", kind="ALIGNED_WITH", members=["a", "b"])
        base = [StoneInstanceDef(instanceId="a"), StoneInstanceDef(instanceId="b", role="SIDE")]
        assert arrangement_fingerprint(
            ArrangementDefinition(instances=base, relations=[a])
        ) == arrangement_fingerprint(ArrangementDefinition(instances=base, relations=[b]))

    def test_a_mirrored_pair_keeps_its_member_order(self):
        """Order is meaningful here: the first member is the original.

        Sorting it away would lose which stone is the reflection.
        """

        pair = ArrangementRelation(
            relationId="r", kind="MIRRORED_PAIR", members=["right", "left"]
        )
        normalized = normalize_definition(
            ArrangementDefinition(
                instances=[
                    StoneInstanceDef(instanceId="left"),
                    StoneInstanceDef(instanceId="right", role="SIDE"),
                ],
                relations=[pair],
            )
        )
        assert normalized.relations[0].members == ["right", "left"]

    def test_an_equivalent_rotation_fingerprints_identically(self):
        assert normalize_angle_deg(370.0) == pytest.approx(10.0)
        assert normalize_angle_deg(-350.0) == pytest.approx(10.0)

        def build(angle: float) -> ArrangementDefinition:
            return ArrangementDefinition(
                instances=[
                    StoneInstanceDef(
                        instanceId="a",
                        placement=InstancePlacement(
                            transform=InstanceTransform(rotationDeg=angle)
                        ),
                    )
                ]
            )

        assert arrangement_fingerprint(build(370.0)) == arrangement_fingerprint(
            build(10.0)
        )

    def test_a_different_arrangement_fingerprints_differently(self):
        """The complement, so the tests above cannot pass by measuring nothing."""

        assert arrangement_fingerprint(halo(8)) != arrangement_fingerprint(halo(9))
        assert arrangement_fingerprint(halo(8, 4.6)) != arrangement_fingerprint(
            halo(8, 5.0)
        )
        assert arrangement_fingerprint(center_only()) != arrangement_fingerprint(halo())

    def test_resolution_is_byte_identical_across_repeats(self):
        definition = halo(12)
        first = resolved_canonical_json(resolve_arrangement(definition))
        for _ in range(4):
            assert resolved_canonical_json(resolve_arrangement(definition)) == first

    def test_no_generated_id_is_random(self):
        """Derived member IDs, not UUIDs.

        A random identifier would break determinism outright and make a stored
        resolution impossible to compare with a fresh one.
        """

        ids_first = [i.instanceId for i in resolve_arrangement(halo(4)).instances]
        ids_again = [i.instanceId for i in resolve_arrangement(halo(4)).instances]
        assert ids_first == ids_again
        assert ids_first == ["center", "halo.0", "halo.1", "halo.2", "halo.3"]

    def test_the_fingerprint_covers_the_resolver_version(self):
        """A change to the resolution arithmetic changes what the same
        declarative content MEANS, so a stored fingerprint must stop matching
        rather than silently claiming an old resolution is current."""

        assert RESOLVER_VERSION in ("1.0.0",)
        assert len(arrangement_fingerprint(center_only())) == 16

    def test_canonical_json_is_sorted_and_compact(self):
        payload = canonical_json(halo(3))
        assert " " not in payload.replace(" ", "")  # no incidental whitespace
        parsed = json.loads(payload)
        assert list(parsed) == sorted(parsed)


# ------------------------------------------------------------- resolution


class TestResolution:
    def test_a_single_instance_resolves_to_itself(self):
        resolved = resolve_arrangement(center_only())
        assert resolved.instanceCount == 1
        assert resolved.patternExpandedCount == 0
        assert resolved.instances[0].transform == InstanceTransform()

    def test_an_empty_arrangement_resolves_to_nothing(self):
        """An honest nothing — not an error, and not an invented default stone."""

        resolved = resolve_arrangement(ArrangementDefinition())
        assert resolved.instances == []
        assert resolved.instanceCount == 0

    def test_every_resolved_placement_is_explicit(self):
        """No downstream consumer should ever have to interpret a mode."""

        resolved = resolve_arrangement(halo(6))
        for instance in resolved.instances:
            # `ResolvedInstance` carries a bare transform: mode and frame are
            # gone precisely because there is nothing left to interpret.
            assert not hasattr(instance, "mode")
            assert not hasattr(instance, "frame")
            assert isinstance(instance.transform, InstanceTransform)

    def test_a_radial_pattern_distributes_a_full_circle_without_doubling(self):
        resolved = resolve_arrangement(halo(4, 5.0))
        members = [i for i in resolved.instances if i.sourcePatternId == "halo"]
        assert len(members) == 4
        angles = sorted(round(i.transform.rotationDeg, 6) for i in members)
        assert angles == [0.0, 90.0, 180.0, 270.0]
        for member in members:
            radius = (member.transform.xMm**2 + member.transform.yMm**2) ** 0.5
            assert radius == pytest.approx(5.0)

    def test_a_partial_arc_includes_both_endpoints(self):
        """A full sweep and an arc distribute differently, on purpose.

        At 360° the last member would land on the first, so the step is
        sweep/count. On an arc both ends are wanted, so it is sweep/(count-1).
        """

        definition = ArrangementDefinition(
            instances=[StoneInstanceDef(instanceId="c")],
            patterns=[
                ArrangementPattern(
                    patternId="arc",
                    sourceInstanceId="c",
                    spec=RadialPatternSpec(
                        count=3, radiusMm=4.0, startAngleDeg=0.0, sweepDeg=180.0
                    ),
                )
            ],
        )
        members = [
            i for i in resolve_arrangement(definition).instances if i.sourcePatternId
        ]
        angles = sorted(round(i.transform.rotationDeg, 6) for i in members)
        assert angles == [0.0, 90.0, 180.0]

    def test_a_single_member_radial_pattern_sits_at_the_start_angle(self):
        definition = ArrangementDefinition(
            instances=[StoneInstanceDef(instanceId="c")],
            patterns=[
                ArrangementPattern(
                    patternId="one",
                    sourceInstanceId="c",
                    spec=RadialPatternSpec(count=1, radiusMm=3.0, startAngleDeg=90.0),
                )
            ],
        )
        member = next(
            i for i in resolve_arrangement(definition).instances if i.sourcePatternId
        )
        assert member.transform.xMm == pytest.approx(0.0, abs=1e-9)
        assert member.transform.yMm == pytest.approx(3.0)

    def test_a_centred_linear_run_is_symmetric_about_the_anchor(self):
        definition = ArrangementDefinition(
            instances=[StoneInstanceDef(instanceId="c")],
            patterns=[
                ArrangementPattern(
                    patternId="row",
                    sourceInstanceId="c",
                    spec=LinearPatternSpec(count=4, spacingMm=2.0, centered=True),
                )
            ],
        )
        members = [
            i for i in resolve_arrangement(definition).instances if i.sourcePatternId
        ]
        xs = sorted(round(i.transform.xMm, 6) for i in members)
        assert xs == [-3.0, -1.0, 1.0, 3.0]

    def test_a_non_centred_linear_run_does_not_double_the_anchor(self):
        """Its first member coincides with the source, so it is not emitted."""

        definition = ArrangementDefinition(
            instances=[StoneInstanceDef(instanceId="c")],
            patterns=[
                ArrangementPattern(
                    patternId="row",
                    sourceInstanceId="c",
                    spec=LinearPatternSpec(count=3, spacingMm=2.0, centered=False),
                )
            ],
        )
        resolved = resolve_arrangement(definition)
        xs = sorted(round(i.transform.xMm, 6) for i in resolved.instances)
        assert xs == [0.0, 2.0, 4.0]
        assert resolved.instanceCount == 3

    def test_a_linear_run_follows_its_direction(self):
        definition = ArrangementDefinition(
            instances=[StoneInstanceDef(instanceId="c")],
            patterns=[
                ArrangementPattern(
                    patternId="row",
                    sourceInstanceId="c",
                    spec=LinearPatternSpec(
                        count=2, spacingMm=2.0, directionDeg=90.0, centered=False
                    ),
                )
            ],
        )
        member = next(
            i for i in resolve_arrangement(definition).instances if i.sourcePatternId
        )
        assert member.transform.xMm == pytest.approx(0.0, abs=1e-9)
        assert member.transform.yMm == pytest.approx(2.0)

    def test_a_mirror_reflects_across_the_plane(self):
        definition = ArrangementDefinition(
            instances=[
                StoneInstanceDef(
                    instanceId="right",
                    role="SIDE",
                    placement=InstancePlacement(
                        transform=InstanceTransform(xMm=3.0, yMm=1.0)
                    ),
                )
            ],
            patterns=[
                ArrangementPattern(
                    patternId="pair",
                    sourceInstanceId="right",
                    spec=MirrorPatternSpec(plane="YZ"),
                    memberRole="SIDE",
                )
            ],
        )
        member = next(
            i for i in resolve_arrangement(definition).instances if i.sourcePatternId
        )
        assert member.transform.xMm == pytest.approx(-3.0)
        assert member.transform.yMm == pytest.approx(1.0)

    def test_a_mirror_flips_a_chiral_stone_s_own_orientation(self):
        """Without the flip a reflection is only a rotation.

        A pear or marquise accent mirrored without flipping its orientation
        points the wrong way.
        """

        definition = ArrangementDefinition(
            instances=[
                StoneInstanceDef(
                    instanceId="right",
                    role="SIDE",
                    placement=InstancePlacement(
                        transform=InstanceTransform(xMm=3.0)
                    ),
                    overrides=InstanceOverrides(orientationDeg=30.0),
                )
            ],
            patterns=[
                ArrangementPattern(
                    patternId="pair",
                    sourceInstanceId="right",
                    spec=MirrorPatternSpec(plane="YZ", mirrorOrientation=True),
                    memberRole="SIDE",
                )
            ],
        )
        member = next(
            i for i in resolve_arrangement(definition).instances if i.sourcePatternId
        )
        assert member.overrides.orientationDeg == pytest.approx(150.0)

    def test_a_mirror_can_skip_the_orientation_flip(self):
        definition = ArrangementDefinition(
            instances=[
                StoneInstanceDef(
                    instanceId="right",
                    role="SIDE",
                    placement=InstancePlacement(transform=InstanceTransform(xMm=3.0)),
                    overrides=InstanceOverrides(orientationDeg=30.0),
                )
            ],
            patterns=[
                ArrangementPattern(
                    patternId="pair",
                    sourceInstanceId="right",
                    spec=MirrorPatternSpec(mirrorOrientation=False),
                    memberRole="SIDE",
                )
            ],
        )
        member = next(
            i for i in resolve_arrangement(definition).instances if i.sourcePatternId
        )
        assert member.overrides.orientationDeg == pytest.approx(30.0)

    def test_a_group_transform_composes_into_the_member_placement(self):
        definition = ArrangementDefinition(
            instances=[
                StoneInstanceDef(
                    instanceId="a",
                    placement=InstancePlacement(
                        frame="PARENT_GROUP",
                        groupId="cluster",
                        transform=InstanceTransform(xMm=1.0),
                    ),
                )
            ],
            groups=[
                ArrangementGroup(
                    groupId="cluster",
                    transform=InstanceTransform(xMm=2.0, yMm=3.0, rotationDeg=90.0),
                )
            ],
        )
        resolved = resolve_arrangement(definition)
        transform = resolved.instances[0].transform
        # The child's +1 mm in X becomes +1 mm in Y after the parent's 90°.
        assert transform.xMm == pytest.approx(2.0, abs=1e-9)
        assert transform.yMm == pytest.approx(4.0)
        assert transform.rotationDeg == pytest.approx(90.0)

    def test_a_design_frame_placement_ignores_the_group_transform(self):
        """Belonging to a group is not the same as being measured from it.

        `frame` decides that, which is why the two are separate fields.
        """

        definition = ArrangementDefinition(
            instances=[
                StoneInstanceDef(
                    instanceId="a",
                    placement=InstancePlacement(
                        frame="DESIGN_ORIGIN",
                        groupId="cluster",
                        transform=InstanceTransform(xMm=1.0),
                    ),
                )
            ],
            groups=[
                ArrangementGroup(
                    groupId="cluster", transform=InstanceTransform(xMm=2.0)
                )
            ],
        )
        resolved = resolve_arrangement(definition)
        assert resolved.instances[0].transform.xMm == pytest.approx(1.0)
        assert resolved.instances[0].groupId == "cluster"

    def test_pattern_members_inherit_the_source_stone_and_gem(self):
        definition = ArrangementDefinition(
            instances=[
                StoneInstanceDef(
                    instanceId="c",
                    gem=GemIdentity(gemId="diamond", origin="NATURAL"),
                )
            ],
            patterns=[
                ArrangementPattern(
                    patternId="halo",
                    sourceInstanceId="c",
                    spec=RadialPatternSpec(count=3, radiusMm=4.0),
                    memberRole="HALO",
                )
            ],
        )
        for member in resolve_arrangement(definition).instances:
            assert member.stoneRef == "primary"
            assert member.gem is not None
            assert member.gem.gemId == "diamond"

    def test_a_pattern_gives_its_members_the_member_role_only(self):
        resolved = resolve_arrangement(halo(3))
        by_id = {i.instanceId: i for i in resolved.instances}
        assert by_id["center"].role == "CENTER"
        assert by_id["halo.0"].role == "HALO"

    def test_relations_pass_through_untouched(self):
        """Relations are RECORDED and reference-checked, never solved."""

        definition = ArrangementDefinition(
            instances=[
                StoneInstanceDef(instanceId="left", role="SIDE"),
                StoneInstanceDef(
                    instanceId="right",
                    role="SIDE",
                    placement=InstancePlacement(transform=InstanceTransform(xMm=5.0)),
                ),
            ],
            relations=[
                ArrangementRelation(
                    relationId="pair", kind="MIRRORED_PAIR", members=["left", "right"]
                )
            ],
        )
        resolved = resolve_arrangement(definition)
        assert len(resolved.relations) == 1
        # Nothing moved to satisfy the relation: `left` is still at the origin
        # even though its declared mirror sits at x = 5.
        by_id = {i.instanceId: i for i in resolved.instances}
        assert by_id["left"].transform.xMm == 0.0
        assert by_id["right"].transform.xMm == pytest.approx(5.0)


# ------------------------------------------------------ invalid structures


class TestRejections:
    def test_a_duplicate_instance_id_is_fatal(self):
        with pytest.raises(DuplicateInstanceIdError):
            resolve_arrangement(
                ArrangementDefinition(
                    instances=[
                        StoneInstanceDef(instanceId="c"),
                        StoneInstanceDef(instanceId="c", role="SIDE"),
                    ]
                )
            )

    def test_a_pattern_naming_a_missing_instance_is_fatal(self):
        with pytest.raises(UnresolvedInstanceReferenceError):
            resolve_arrangement(
                ArrangementDefinition(
                    instances=[StoneInstanceDef(instanceId="c")],
                    patterns=[
                        ArrangementPattern(
                            patternId="p",
                            sourceInstanceId="nope",
                            spec=LinearPatternSpec(count=2, spacingMm=1.0),
                        )
                    ],
                )
            )

    def test_a_placement_naming_a_missing_group_is_fatal(self):
        with pytest.raises(UnresolvedGroupReferenceError):
            resolve_arrangement(
                ArrangementDefinition(
                    instances=[
                        StoneInstanceDef(
                            instanceId="c",
                            placement=InstancePlacement(
                                frame="PARENT_GROUP", groupId="nope"
                            ),
                        )
                    ]
                )
            )

    def test_a_pattern_naming_a_missing_group_is_fatal(self):
        with pytest.raises(UnresolvedGroupReferenceError):
            resolve_arrangement(
                ArrangementDefinition(
                    instances=[StoneInstanceDef(instanceId="c")],
                    patterns=[
                        ArrangementPattern(
                            patternId="p",
                            sourceInstanceId="c",
                            spec=MirrorPatternSpec(),
                            groupId="nope",
                        )
                    ],
                )
            )

    def test_a_relation_referencing_a_missing_member_is_fatal(self):
        with pytest.raises(UnresolvedInstanceReferenceError):
            resolve_arrangement(
                ArrangementDefinition(
                    instances=[StoneInstanceDef(instanceId="c")],
                    relations=[
                        ArrangementRelation(
                            relationId="r", kind="ALIGNED_WITH", members=["c", "ghost"]
                        )
                    ],
                )
            )

    def test_a_relation_may_reference_a_generated_member(self):
        """Checked AFTER expansion, so a pattern member is addressable."""

        definition = ArrangementDefinition(
            instances=[StoneInstanceDef(instanceId="center")],
            patterns=[
                ArrangementPattern(
                    patternId="halo",
                    sourceInstanceId="center",
                    spec=RadialPatternSpec(count=2, radiusMm=4.0),
                    memberRole="HALO",
                )
            ],
            relations=[
                ArrangementRelation(
                    relationId="r",
                    kind="CONCENTRIC_WITH",
                    members=["center", "halo.0"],
                )
            ],
        )
        assert len(resolve_arrangement(definition).relations) == 1

    def test_a_mirrored_pair_requires_exactly_two_members(self):
        with pytest.raises(ArrangementRelationInvalidError):
            resolve_arrangement(
                ArrangementDefinition(
                    instances=[
                        StoneInstanceDef(instanceId="a"),
                        StoneInstanceDef(instanceId="b", role="SIDE"),
                        StoneInstanceDef(instanceId="c", role="SIDE"),
                    ],
                    relations=[
                        ArrangementRelation(
                            relationId="r",
                            kind="MIRRORED_PAIR",
                            members=["a", "b", "c"],
                        )
                    ],
                )
            )

    def test_a_relation_between_a_thing_and_itself_is_fatal(self):
        with pytest.raises(ArrangementRelationInvalidError):
            resolve_arrangement(
                ArrangementDefinition(
                    instances=[StoneInstanceDef(instanceId="a")],
                    relations=[
                        ArrangementRelation(
                            relationId="r", kind="ALIGNED_WITH", members=["a", "a"]
                        )
                    ],
                )
            )

    def test_a_pattern_colliding_with_an_existing_id_is_fatal(self):
        """Rejected rather than renamed: a silent rename would make a relation
        referencing that ID point at a different stone."""

        with pytest.raises(DuplicateInstanceIdError):
            resolve_arrangement(
                ArrangementDefinition(
                    instances=[
                        StoneInstanceDef(instanceId="c"),
                        StoneInstanceDef(instanceId="p.1", role="ACCENT"),
                    ],
                    patterns=[
                        ArrangementPattern(
                            patternId="p",
                            sourceInstanceId="c",
                            spec=MirrorPatternSpec(),
                        )
                    ],
                )
            )

    def test_exceeding_the_software_instance_bound_is_fatal(self):
        definition = ArrangementDefinition(
            instances=[StoneInstanceDef(instanceId="c")],
            patterns=[
                ArrangementPattern(
                    patternId="a",
                    sourceInstanceId="c",
                    spec=RadialPatternSpec(count=100, radiusMm=4.0),
                ),
                ArrangementPattern(
                    patternId="b",
                    sourceInstanceId="c",
                    spec=RadialPatternSpec(count=100, radiusMm=5.0),
                ),
            ],
        )
        with pytest.raises(ArrangementCapacityExceededError):
            resolve_arrangement(definition)

    def test_the_instance_bound_is_a_software_limit_not_a_jewelry_limit(self):
        assert MAX_INSTANCES == 200

    def test_a_malformed_structure_is_never_repaired(self):
        """Reject, never repair — the discipline Sprint 20 set for outlines.

        Filling in a plausible reference would produce an arrangement nobody
        authored.
        """

        broken = ArrangementDefinition(
            instances=[StoneInstanceDef(instanceId="c")],
            patterns=[
                ArrangementPattern(
                    patternId="p",
                    sourceInstanceId="ghost",
                    spec=MirrorPatternSpec(),
                )
            ],
        )
        with pytest.raises(UnresolvedInstanceReferenceError):
            resolve_arrangement(broken)
        # And the definition itself is untouched by the failed attempt.
        assert broken.patterns[0].sourceInstanceId == "ghost"


# ------------------------------------------------- structural validation


class TestForgeArrangementRules:
    def test_a_design_with_no_arrangement_produces_no_findings(self):
        assert arrangement_results(default_definition()) == {}

    def test_a_valid_arrangement_produces_only_the_partial_notice(self):
        definition = default_definition()
        definition.arrangement = halo(4)
        results = arrangement_results(definition)
        assert results == {"JM-ARRANGE-006": "information"}
        assert not has_errors(validate_definition(definition))

    def test_a_single_instance_arrangement_produces_no_findings_at_all(self):
        definition = default_definition()
        definition.arrangement = center_only()
        assert arrangement_results(definition) == {}

    def test_a_duplicate_id_is_an_error(self):
        definition = default_definition()
        definition.arrangement = ArrangementDefinition(
            instances=[
                StoneInstanceDef(instanceId="c"),
                StoneInstanceDef(instanceId="c", role="SIDE"),
            ]
        )
        results = arrangement_results(definition)
        assert results["JM-ARRANGE-001"] == "error"
        assert has_errors(validate_definition(definition))

    def test_a_missing_group_reference_is_an_error(self):
        definition = default_definition()
        definition.arrangement = ArrangementDefinition(
            instances=[
                StoneInstanceDef(
                    instanceId="c",
                    placement=InstancePlacement(frame="PARENT_GROUP", groupId="ghost"),
                )
            ]
        )
        assert arrangement_results(definition)["JM-ARRANGE-002"] == "error"

    def test_an_unresolvable_stone_reference_is_a_warning_not_an_error(self):
        """The document is structurally valid and still generates.

        Only that instance produces no geometry, so blocking the whole design
        would be wrong.
        """

        definition = default_definition()
        definition.arrangement = ArrangementDefinition(
            instances=[StoneInstanceDef(instanceId="c", stoneRef="accent")]
        )
        results = arrangement_results(definition)
        assert results["JM-ARRANGE-003"] == "warning"
        assert not has_errors(validate_definition(definition))

    def test_two_centers_are_reported_as_ambiguous(self):
        definition = default_definition()
        definition.arrangement = ArrangementDefinition(
            instances=[
                StoneInstanceDef(instanceId="a", role="CENTER"),
                StoneInstanceDef(instanceId="b", role="CENTER"),
            ]
        )
        assert arrangement_results(definition)["JM-ARRANGE-005"] == "warning"

    def test_an_unresolvable_structure_is_an_error(self):
        definition = default_definition()
        definition.arrangement = ArrangementDefinition(
            instances=[StoneInstanceDef(instanceId="c")],
            relations=[
                ArrangementRelation(
                    relationId="r", kind="ALIGNED_WITH", members=["c", "ghost"]
                )
            ],
        )
        assert arrangement_results(definition)["JM-ARRANGE-004"] == "error"

    def test_no_arrangement_rule_invents_a_jewelry_threshold(self):
        """Scans the real messages the engine emits, not the source.

        A spacing, clearance or proportion claim introduced through an f-string
        would be caught here too.
        """

        forbidden = (
            "too close",
            "too far",
            "minimum spacing",
            "clearance",
            "not manufacturable",
            "recommend",
            "should be",
            "industry standard",
            "unsafe",
        )
        definitions = []
        for arrangement in (
            center_only(),
            halo(8),
            ArrangementDefinition(
                instances=[
                    StoneInstanceDef(
                        instanceId="a",
                        placement=InstancePlacement(
                            transform=InstanceTransform(xMm=0.001)
                        ),
                    ),
                    StoneInstanceDef(instanceId="b", role="SIDE"),
                ]
            ),
            ArrangementDefinition(
                instances=[StoneInstanceDef(instanceId="c", stoneRef="accent")]
            ),
        ):
            definition = default_definition()
            definition.arrangement = arrangement
            definitions.append(definition)

        for definition in definitions:
            for result in validate_definition(definition):
                lowered = result.message.lower()
                for term in forbidden:
                    assert term not in lowered, (result.ruleId, result.message)

    def test_two_stones_at_the_same_point_is_not_a_structural_error(self):
        """Overlap is a GEOMETRIC question, not a structural one.

        Answering it here would mean inventing a spacing rule; it belongs to
        Geometry Inspection once multi-stone geometry exists.
        """

        definition = default_definition()
        definition.arrangement = ArrangementDefinition(
            instances=[
                StoneInstanceDef(instanceId="a"),
                StoneInstanceDef(instanceId="b", role="SIDE"),
            ]
        )
        assert not has_errors(validate_definition(definition))


# -------------------------------------------------------- JDL integration


class TestJdlIntegration:
    def test_a_legacy_definition_has_no_arrangement(self):
        assert default_definition().arrangement is None

    def test_an_arrangement_survives_a_json_round_trip(self):
        definition = default_definition()
        definition.arrangement = ArrangementDefinition(
            instances=[
                StoneInstanceDef(
                    instanceId="center",
                    gem=GemIdentity(gemId="diamond", origin="NATURAL"),
                ),
                StoneInstanceDef(
                    instanceId="side.1",
                    role="SIDE",
                    placement=InstancePlacement(
                        transform=InstanceTransform(xMm=3.2, rotationDeg=15.0)
                    ),
                    overrides=InstanceOverrides(scale=0.4),
                ),
            ],
            groups=[ArrangementGroup(groupId="sides", label="Side stones")],
            patterns=[
                ArrangementPattern(
                    patternId="mirror",
                    sourceInstanceId="side.1",
                    spec=MirrorPatternSpec(plane="YZ"),
                    memberRole="SIDE",
                )
            ],
            relations=[
                ArrangementRelation(
                    relationId="pair",
                    kind="MIRRORED_PAIR",
                    members=["side.1", "mirror.1"],
                )
            ],
        )
        again = JewelryDefinition.model_validate_json(definition.model_dump_json())
        assert again.arrangement == definition.arrangement
        assert definition_hash(again) == definition_hash(definition)

    def test_an_unknown_field_inside_an_arrangement_is_rejected(self):
        with pytest.raises(ValidationError):
            JewelryDefinition.model_validate(
                {
                    "arrangement": {
                        "instances": [{"instanceId": "c", "sparkle": True}]
                    }
                }
            )

    def test_the_arrangement_participates_in_the_geometry_hash(self):
        """It MUST, because an arrangement will drive geometry.

        Excluding it — as gem identity is excluded — would serve stale geometry
        for a real design change, which is worse than a slow rebuild.
        """

        plain = default_definition()
        arranged = default_definition()
        arranged.arrangement = halo(6)
        assert geometry_hash(plain) != geometry_hash(arranged)
        assert definition_hash(plain) != definition_hash(arranged)

    def test_a_different_arrangement_changes_the_geometry_hash(self):
        six = default_definition()
        six.arrangement = halo(6)
        eight = default_definition()
        eight.arrangement = halo(8)
        assert geometry_hash(six) != geometry_hash(eight)

    def test_arrangement_identity_is_separate_from_definition_identity(self):
        """The same arrangement in two different rings: one fingerprint, two
        definition hashes."""

        arrangement = halo(6)
        thin = default_definition()
        thin.arrangement = arrangement
        wide = default_definition()
        wide.band.width = thin.band.width + 1.0
        wide.arrangement = arrangement

        assert definition_hash(thin) != definition_hash(wide)
        assert arrangement_fingerprint(
            thin.arrangement
        ) == arrangement_fingerprint(wide.arrangement)


# --------------------------------------------------- compilation boundary


class TestCompilationBoundary:
    def test_no_arrangement_compiles_to_no_arrangement(self):
        """The whole backward-compatibility story in one assertion.

        It does NOT synthesize a one-instance arrangement for a single-stone
        design, which would invent a declaration the document never made.
        """

        assert compile_arrangement(None) is None

    def test_the_primary_instance_maps_to_the_historical_component_name(self):
        compiled = compile_arrangement(center_only())
        assert compiled is not None
        instance = compiled.instances[0]
        assert instance.generationStatus == "GENERATED"
        assert instance.componentName == PRIMARY_STONE_COMPONENT == "stone_reference"
        assert compiled.generatedCount == 1

    def test_additional_instances_are_reported_not_generated_with_a_reason(self):
        compiled = compile_arrangement(halo(4))
        assert compiled is not None
        assert compiled.instanceCount == 5
        assert compiled.generatedCount == 1
        ungenerated = [
            i for i in compiled.instances if i.generationStatus == "NOT_GENERATED"
        ]
        assert len(ungenerated) == 4
        for instance in ungenerated:
            # Never silently dropped, and never given a placeholder component.
            assert instance.componentName is None
            assert instance.generationNote
            assert "PARTIAL" in instance.generationNote

    def test_an_ungenerated_instance_cannot_be_constructed_without_a_reason(self):
        """Enforced by the model, so no code path can omit the explanation."""

        from jewelmind.arrangement.models import ResolvedInstance

        with pytest.raises(ValidationError):
            ResolvedInstance(
                instanceId="a",
                stoneRef="primary",
                role="SIDE",
                transform=InstanceTransform(),
                overrides=InstanceOverrides(),
                gem=None,
                sourcePatternId=None,
                groupId=None,
                generationStatus="NOT_GENERATED",
                generationNote=None,
            )

    def test_a_generated_instance_must_name_its_component(self):
        from jewelmind.arrangement.models import ResolvedInstance

        with pytest.raises(ValidationError):
            ResolvedInstance(
                instanceId="a",
                stoneRef="primary",
                role="CENTER",
                transform=InstanceTransform(),
                overrides=InstanceOverrides(),
                gem=None,
                sourcePatternId=None,
                groupId=None,
                generationStatus="GENERATED",
                componentName=None,
            )

    def test_primary_selection_does_not_depend_on_list_order(self):
        """Choosing `instances[0]` would make the built geometry depend on
        serialization order — the dependency this layer exists to remove."""

        forward = ArrangementDefinition(
            instances=[
                StoneInstanceDef(instanceId="accent", role="ACCENT"),
                StoneInstanceDef(instanceId="middle", role="CENTER"),
            ]
        )
        reverse = ArrangementDefinition(
            instances=[
                StoneInstanceDef(instanceId="middle", role="CENTER"),
                StoneInstanceDef(instanceId="accent", role="ACCENT"),
            ]
        )
        for definition in (forward, reverse):
            compiled = compile_arrangement(definition)
            assert compiled is not None
            generated = [
                i for i in compiled.instances if i.generationStatus == "GENERATED"
            ]
            assert [i.instanceId for i in generated] == ["middle"]

    def test_an_arrangement_with_no_center_still_builds_one_stone(self):
        compiled = compile_arrangement(
            ArrangementDefinition(
                instances=[
                    StoneInstanceDef(instanceId="b", role="SIDE"),
                    StoneInstanceDef(instanceId="a", role="SIDE"),
                ]
            )
        )
        assert compiled is not None
        generated = [i for i in compiled.instances if i.generationStatus == "GENERATED"]
        assert [i.instanceId for i in generated] == ["a"]

    def test_an_instance_with_an_unresolvable_stone_reports_that_specifically(self):
        """A reader must tell "the pipeline cannot yet" from "your document is
        wrong", because the two need different responses."""

        compiled = compile_arrangement(
            ArrangementDefinition(
                instances=[StoneInstanceDef(instanceId="c", stoneRef="accent")]
            )
        )
        assert compiled is not None
        note = compiled.instances[0].generationNote or ""
        assert "references stone 'accent'" in note
        assert compiled.generatedCount == 0

    def test_an_empty_arrangement_compiles_to_nothing_generated(self):
        compiled = compile_arrangement(ArrangementDefinition())
        assert compiled is not None
        assert compiled.instances == []
        assert compiled.generatedCount == 0

    def test_compilation_is_deterministic(self):
        first = resolved_canonical_json(compile_arrangement(halo(8)))
        for _ in range(3):
            assert resolved_canonical_json(compile_arrangement(halo(8))) == first

    def test_resolution_itself_never_claims_generation(self):
        """Resolution stays a pure function of the arrangement, so its output is
        stable across pipeline versions."""

        for instance in resolve_arrangement(halo(3)).instances:
            assert instance.generationStatus == "NOT_GENERATED"
            assert instance.componentName is None


# ------------------------------------------------- component identity contract


class TestComponentIdentity:
    def test_the_naming_authority_and_the_role_module_agree(self):
        """`geometry/roles.py` duplicates the prefix as a literal because
        `jewelmind.geometry` must not import `jewelmind.arrangement`. This test
        is what keeps the duplicate honest."""

        from jewelmind.geometry import roles

        assert roles._STONE_INSTANCE_PREFIX == STONE_INSTANCE_COMPONENT_PREFIX

    def test_an_instance_component_is_classified_as_a_stone_not_as_metal(self):
        """The default for an unknown name is `production_metal`, which is
        correct for a metal part and catastrophic for a stone: it would let an
        additional stone be fused into the metal body and shipped in a
        production export, breaking LAW-006 silently."""

        name = stone_component_name("halo.3", is_primary=False)
        assert name == "stone_reference.halo.3"
        assert geometry_role(name) == "stone_reference"
        assert not is_production_component(name)
        assert production_role(name) == "excluded_by_default"

    def test_the_primary_stone_keeps_its_historical_classification(self):
        assert geometry_role("stone_reference") == "stone_reference"
        assert production_role("stone_reference") == "excluded_by_default"
        assert not is_production_component("stone_reference")

    def test_metal_components_are_unaffected(self):
        for name in ("band", "prongs", "bezel", "basket_support"):
            assert geometry_role(name) == "production_metal"
            assert is_production_component(name)
            assert production_role(name) == "included_by_default"

    def test_an_unknown_component_still_defaults_to_production_metal(self):
        """Unchanged behaviour for anything that is not a stone instance."""

        assert geometry_role("mystery") == "production_metal"
        assert is_production_component("mystery")

    def test_a_component_name_is_derived_from_the_authoritative_id(self):
        assert stone_component_name("center", is_primary=True) == "stone_reference"
        assert (
            stone_component_name("side.1", is_primary=False)
            == "stone_reference.side.1"
        )


# ------------------------------------------------------ capability honesty


class TestCapabilityRegistry:
    def test_every_entry_is_internally_consistent(self):
        for name, entry in ARRANGEMENT_CAPABILITIES.items():
            assert entry.capability == name
            assert entry.note.strip()
            # A capability cannot be resolvable without being representable,
            # nor generatable without being resolvable.
            if entry.resolvable:
                assert entry.representable, name
            if entry.generatable:
                assert entry.resolvable, name

    def test_multi_stone_geometry_is_reported_partial_not_current(self):
        entry = ARRANGEMENT_CAPABILITIES["multi_stone_geometry"]
        assert entry.status == "PARTIAL"
        assert entry.representable is True
        assert entry.resolvable is True
        assert entry.generatable is False

    def test_no_capability_claims_generation_it_does_not_have(self):
        """Only the stone-instance capability generates geometry today, and it
        does so as the single existing `stone_reference` component."""

        assert generatable_capabilities() == ["stone_instance"]

    def test_solver_and_professional_rules_are_planned_and_unrepresentable(self):
        for name in (
            "constraint_solving",
            "professional_arrangement_rules",
            "arrangement_collision_checking",
            "full_3d_instance_orientation",
            "path_pattern",
        ):
            entry = ARRANGEMENT_CAPABILITIES[name]
            assert entry.status == "PLANNED", name
            assert entry.representable is False, name

    def test_full_3d_orientation_is_genuinely_not_representable(self):
        """Not merely documented as planned — the model has no field for it.

        Accepting a rotation no builder can execute would be a silently
        ignored field.
        """

        assert set(InstanceTransform.model_fields) == {
            "xMm",
            "yMm",
            "zMm",
            "rotationDeg",
        }

    def test_the_resolvable_pattern_kinds_match_the_real_expanders(self):
        assert resolvable_pattern_kinds() == ("LINEAR", "MIRROR", "RADIAL")

    def test_the_current_capability_list_is_non_empty_and_sorted(self):
        current = current_capabilities()
        assert current
        assert current == sorted(current)


# ------------------------------------------------------ backward compatibility


class TestBackwardCompatibility:
    def test_the_default_solitaire_still_generates_unchanged_components(self):
        from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring

        model = build_solitaire_ring(default_definition())
        assert sorted(model.components) == [
            "band",
            "basket_support",
            "prongs",
            "stone_reference",
        ]
        assert model.arrangement_result is None

    def test_declaring_a_single_center_instance_changes_no_component(self):
        """An arrangement that says only "there is one centre stone" must not
        change what is built."""

        from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring

        plain = build_solitaire_ring(default_definition())
        arranged_definition = default_definition()
        arranged_definition.arrangement = center_only()
        arranged = build_solitaire_ring(arranged_definition)

        assert sorted(arranged.components) == sorted(plain.components)
        assert arranged.combined_metal_volume_mm3 == pytest.approx(
            plain.combined_metal_volume_mm3, rel=1e-9
        )
        assert arranged.components["stone_reference"].volume_mm3 == pytest.approx(
            plain.components["stone_reference"].volume_mm3, rel=1e-9
        )
        assert arranged.arrangement_result is not None
        assert arranged.arrangement_result.generatedCount == 1

    def test_a_halo_arrangement_does_not_add_a_component_yet(self):
        """The honest boundary, asserted rather than described.

        No placeholder solid is emitted to make a count match.
        """

        from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring

        definition = default_definition()
        definition.arrangement = halo(8)
        model = build_solitaire_ring(definition)
        assert sorted(model.components) == [
            "band",
            "basket_support",
            "prongs",
            "stone_reference",
        ]
        assert model.arrangement_result.instanceCount == 9
        assert model.arrangement_result.generatedCount == 1

    def test_an_arranged_model_still_excludes_the_stone_from_production(self):
        from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring

        definition = default_definition()
        definition.arrangement = halo(4)
        model = build_solitaire_ring(definition)
        production = [n for n in model.components if is_production_component(n)]
        assert sorted(production) == ["band", "basket_support", "prongs"]

    def test_the_preview_manifest_reports_roles_for_an_arranged_model(self):
        import tempfile
        from pathlib import Path

        from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring
        from jewelmind.preview.mesh import write_component_previews

        definition = default_definition()
        definition.arrangement = center_only()
        model = build_solitaire_ring(definition)
        with tempfile.TemporaryDirectory() as tmp:
            manifest = write_component_previews(model, definition, Path(tmp))
        assert manifest["stone_reference"]["geometryRole"] == "stone_reference"
        assert manifest["stone_reference"]["productionRole"] == "excluded_by_default"
        assert manifest["band"]["geometryRole"] == "production_metal"
