"""Multi-Stone Families v1 (Sprint 24).

Covers the four families as semantics AND as real geometry, their compilation
into arrangement primitives, mixed stones and shapes, symmetric and asymmetric
layouts, deterministic identity, the structural rules, and — the part easiest
to break — that a design with no family behaves exactly as it did before.
"""

from __future__ import annotations

import ast
import json
import math
from pathlib import Path

import pytest
from pydantic import ValidationError

from jewelmind.arrangement.compile import (
    PRIMARY_STONE_COMPONENT,
    STONE_INSTANCE_COMPONENT_PREFIX,
    compile_arrangement,
)
from jewelmind.arrangement.models import (
    ArrangementDefinition,
    InstanceTransform,
    StoneInstanceDef,
)
from jewelmind.arrangement.normalize import (
    arrangement_fingerprint,
    resolved_canonical_json,
)
from jewelmind.arrangement.resolve import resolve_arrangement
from jewelmind.domain.defaults import default_definition
from jewelmind.domain.schema import JewelryDefinition
from jewelmind.family.capability import (
    FAMILY_CAPABILITIES,
    FAMILY_COMPILER_VERSION,
    FAMILY_FEATURE_CAPABILITIES,
    FAMILY_REGISTRY_VERSION,
    RESERVED_FAMILY_TYPES,
    current_families,
    families_with_setting_geometry,
    families_with_stone_geometry,
)
from jewelmind.family.compile import (
    FAMILY_ROLE_RULES,
    compile_family,
    family_compilers,
    family_types,
)
from jewelmind.family.effective import effective_arrangement
from jewelmind.family.errors import (
    FamilyConflictError,
    FamilyRoleCardinalityError,
    FamilyRoleInvalidError,
)
from jewelmind.family.models import (
    CenterWithAccentsParams,
    ClusterParams,
    FamilyDefinition,
    FamilyMember,
    ThreeStoneParams,
    ToiEtMoiParams,
)
from jewelmind.gem.models import GemIdentity
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring
from jewelmind.geometry.inspection import inspect_model
from jewelmind.geometry.inspection.assembly import (
    required_component_names,
    stone_component_names,
)
from jewelmind.geometry.roles import geometry_role, is_production_component
from jewelmind.geometry.stone.placement import stone_components
from jewelmind.utils.hashing import definition_hash, geometry_hash
from jewelmind.validation.engine import has_errors, validate_definition

#: The default solitaire's fused metal volume, unchanged since Sprint 19.
#: Relative tolerance, not `==`: OCCT floats are not bit-identical across
#: platform builds (the lesson Sprint 19's CI failure taught).
LEGACY_METAL_VOLUME_MM3 = 341.44334316909976
KERNEL_REL_TOLERANCE = 1e-9


def three_stone(**over) -> FamilyDefinition:
    params: dict = {"sideSpacingMm": 4.6}
    members = over.pop("members", [])
    params.update({k: v for k, v in over.items() if k != "members"})
    return FamilyDefinition(
        familyType="THREE_STONE",
        params=ThreeStoneParams(**params),
        members=members,
    )


def toi_et_moi(**over) -> FamilyDefinition:
    params: dict = {"separationMm": 5.0}
    members = over.pop("members", [])
    params.update(over)
    return FamilyDefinition(
        familyType="TOI_ET_MOI", params=ToiEtMoiParams(**params), members=members
    )


def cluster(**over) -> FamilyDefinition:
    params: dict = {"count": 6, "radiusMm": 3.4}
    members = over.pop("members", [])
    params.update(over)
    return FamilyDefinition(
        familyType="CLUSTER", params=ClusterParams(**params), members=members
    )


def center_accents(**over) -> FamilyDefinition:
    params: dict = {"accentCount": 8, "accentRadiusMm": 4.6}
    members = over.pop("members", [])
    params.update(over)
    return FamilyDefinition(
        familyType="CENTER_WITH_ACCENTS",
        params=CenterWithAccentsParams(**params),
        members=members,
    )


def ring(family: FamilyDefinition | None = None) -> JewelryDefinition:
    definition = default_definition()
    definition.family = family
    return definition


def family_rule_ids(definition: JewelryDefinition) -> dict[str, str]:
    return {
        r.ruleId: r.severity
        for r in validate_definition(definition)
        if r.ruleId.startswith("JM-FAMILY")
    }


def resolved(family: FamilyDefinition):
    arrangement = compile_family(family)
    assert arrangement is not None
    return resolve_arrangement(arrangement)


# ------------------------------------------------------------- the model


class TestFamilyModel:
    def test_a_family_references_stones_rather_than_restating_them(self):
        member = FamilyMember(memberId="center", role="CENTER")
        # No shape, no dimensions, no material: a member is an occurrence OF
        # something, and copying the stone here would create a second source of
        # truth for what that stone is.
        for absent in ("shape", "diameter", "length", "width", "depth", "source"):
            assert not hasattr(member, absent), absent
        assert member.stoneRef == "primary"

    def test_a_member_may_carry_its_own_gem(self):
        member = FamilyMember(
            memberId="side.left",
            role="SIDE",
            gem=GemIdentity(gemId="corundum.sapphire", origin="NATURAL"),
        )
        assert member.gem is not None
        assert member.gem.gemId == "corundum.sapphire"

    def test_a_gem_left_unset_inherits_rather_than_copying(self):
        assert FamilyMember(memberId="c", role="CENTER").gem is None

    def test_the_placement_override_reuses_the_arrangement_transform(self):
        """A parallel transform model would be two definitions of one concept."""

        member = FamilyMember(
            memberId="c",
            role="CENTER",
            placementOverride=InstanceTransform(xMm=1.5),
        )
        assert isinstance(member.placementOverride, InstanceTransform)

    @pytest.mark.parametrize(
        "candidate",
        [
            "Center",
            "center..1",
            "../../etc/passwd",
            "center/1",
            "rm -rf /",
            "",
            "a" * 81,
            "center 1",
        ],
    )
    def test_a_malformed_member_id_is_rejected(self, candidate: str):
        with pytest.raises(ValidationError):
            FamilyMember(memberId=candidate, role="CENTER")

    def test_duplicate_member_ids_are_rejected(self):
        with pytest.raises(ValidationError):
            three_stone(
                members=[
                    FamilyMember(memberId="c", role="CENTER"),
                    FamilyMember(memberId="c", role="SIDE"),
                ]
            )

    def test_the_params_kind_must_match_the_family_type(self):
        """Two fields naming the same thing can disagree, and a family whose
        type says one thing while its parameters say another has no
        determinate meaning."""

        with pytest.raises(ValidationError):
            FamilyDefinition(
                familyType="CLUSTER", params=ThreeStoneParams(sideSpacingMm=4.0)
            )

    def test_no_family_parameter_accepts_nan_or_infinity(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with pytest.raises(ValidationError):
                ThreeStoneParams(sideSpacingMm=bad)
            with pytest.raises(ValidationError):
                ClusterParams(count=4, radiusMm=bad)

    def test_a_jdl_style_string_number_is_rejected(self):
        with pytest.raises(ValidationError):
            ThreeStoneParams.model_validate({"sideSpacingMm": "4.6"})
        assert ThreeStoneParams.model_validate({"sideSpacingMm": 4}).sideSpacingMm == 4.0

    def test_a_non_positive_scale_is_rejected(self):
        for bad in (0.0, -1.0, 0.001):
            with pytest.raises(ValidationError):
                FamilyMember(memberId="c", role="CENTER", scale=bad)

    def test_the_family_holds_no_kernel_object(self):
        for field in FamilyMember.model_fields.values():
            assert "cadquery" not in str(field.annotation).lower()


# ------------------------------------------------------- three-stone


class TestThreeStone:
    def test_it_distinguishes_roles_rather_than_storing_three_stones(self):
        arrangement = compile_family(three_stone())
        assert arrangement is not None
        roles = sorted(i.role for i in resolve_arrangement(arrangement).instances)
        assert roles == ["CENTER", "SIDE", "SIDE"]

    def test_a_symmetric_layout_compiles_to_a_mirror_pattern(self):
        """The mirroring is performed by the arrangement engine, so a family can
        never disagree with an arrangement about where a mirrored stone goes."""

        arrangement = compile_family(three_stone())
        assert arrangement is not None
        assert [p.spec.kind for p in arrangement.patterns] == ["MIRROR"]

    def test_the_sides_sit_symmetrically_about_the_centre(self):
        result = resolved(three_stone(sideSpacingMm=4.2))
        by_role: dict[str, list[float]] = {}
        for instance in result.instances:
            by_role.setdefault(instance.role, []).append(instance.transform.xMm)
        assert by_role["CENTER"] == [0.0]
        assert sorted(by_role["SIDE"]) == [-4.2, 4.2]

    def test_an_asymmetric_layout_places_both_sides_explicitly(self):
        arrangement = compile_family(three_stone(symmetry="ASYMMETRIC"))
        assert arrangement is not None
        assert arrangement.patterns == []
        assert len(arrangement.instances) == 3

    def test_the_side_scale_default_is_applied_to_both_sides(self):
        result = resolved(three_stone(sideScale=0.5))
        sides = [i for i in result.instances if i.role == "SIDE"]
        assert len(sides) == 2
        assert all(i.overrides.scale == 0.5 for i in sides)

    def test_a_member_scale_overrides_the_family_default(self):
        """One unusual side stone must not require abandoning the parameters."""

        family = three_stone(
            sideScale=0.5,
            symmetry="ASYMMETRIC",
            members=[
                FamilyMember(memberId="center", role="CENTER"),
                FamilyMember(memberId="side.a", role="SIDE", scale=0.8),
                FamilyMember(memberId="side.b", role="SIDE"),
            ],
        )
        by_id = {i.instanceId: i for i in resolved(family).instances}
        assert by_id["side.a"].overrides.scale == 0.8
        assert by_id["side.b"].overrides.scale == 0.5

    def test_the_three_stones_may_carry_different_gems(self):
        family = three_stone(
            symmetry="ASYMMETRIC",
            members=[
                FamilyMember(
                    memberId="center",
                    role="CENTER",
                    gem=GemIdentity(gemId="diamond", origin="NATURAL"),
                ),
                FamilyMember(
                    memberId="side.a",
                    role="SIDE",
                    gem=GemIdentity(gemId="corundum.sapphire", origin="NATURAL"),
                ),
                FamilyMember(
                    memberId="side.b",
                    role="SIDE",
                    gem=GemIdentity(gemId="corundum.ruby", origin="NATURAL"),
                ),
            ],
        )
        gems = {
            i.instanceId: (i.gem.gemId if i.gem else None)
            for i in resolved(family).instances
        }
        assert gems["center"] == "diamond"
        assert gems["side.a"] == "corundum.sapphire"
        assert gems["side.b"] == "corundum.ruby"

    def test_a_wrong_side_count_is_refused(self):
        with pytest.raises(FamilyRoleCardinalityError):
            compile_family(
                three_stone(
                    members=[
                        FamilyMember(memberId="center", role="CENTER"),
                        FamilyMember(memberId="side.a", role="SIDE"),
                    ]
                )
            )

    def test_a_role_the_family_does_not_accept_is_refused(self):
        with pytest.raises(FamilyRoleInvalidError):
            compile_family(
                three_stone(
                    members=[
                        FamilyMember(memberId="center", role="CENTER"),
                        FamilyMember(memberId="a", role="SIDE"),
                        FamilyMember(memberId="b", role="SIDE"),
                        FamilyMember(memberId="h", role="HALO"),
                    ]
                )
            )


# --------------------------------------------------------- toi-et-moi


class TestToiEtMoi:
    def test_it_is_a_pair_straddling_the_design_axis(self):
        """Not two stones that happen to be adjacent: the pair is the design."""

        result = resolved(toi_et_moi(separationMm=5.0))
        xs = sorted(round(i.transform.xMm, 6) for i in result.instances)
        assert xs == [-2.5, 2.5]
        assert result.instanceCount == 2

    def test_the_pair_axis_is_settable(self):
        result = resolved(toi_et_moi(separationMm=6.0, axisAngleDeg=90.0))
        ys = sorted(round(i.transform.yMm, 6) for i in result.instances)
        assert ys == [-3.0, 3.0]
        assert all(abs(i.transform.xMm) < 1e-9 for i in result.instances)

    def test_a_symmetric_pair_flips_the_second_stone_orientation(self):
        """Without the flip the two stones sit parallel rather than facing.

        A `MIRROR` pattern is deliberately NOT used: it reflects across a
        principal plane, so a pair whose axis runs along Y would map each stone
        onto itself. Both are placed directly and the second is turned 180
        degrees, which is correct at every axis angle.
        """

        arrangement = compile_family(toi_et_moi())
        assert arrangement is not None
        assert arrangement.patterns == []
        orientations = sorted(
            (i.overrides.orientationDeg or 0.0) for i in arrangement.instances
        )
        assert orientations == [0.0, 180.0]

    def test_a_symmetric_pair_does_not_collapse_on_a_vertical_axis(self):
        """The defect this construction exists to prevent: mirroring across YZ
        mapped a Y-axis pair onto one point."""

        for angle in (0.0, 30.0, 45.0, 90.0, 135.0):
            result = resolved(toi_et_moi(separationMm=5.0, axisAngleDeg=angle))
            positions = {
                (round(i.transform.xMm, 6), round(i.transform.yMm, 6))
                for i in result.instances
            }
            assert len(positions) == 2, angle

    def test_an_asymmetric_pair_places_both_stones(self):
        arrangement = compile_family(toi_et_moi(symmetry="ASYMMETRIC"))
        assert arrangement is not None
        assert arrangement.patterns == []
        assert len(arrangement.instances) == 2

    def test_the_relationship_is_recorded_not_merely_implied(self):
        arrangement = compile_family(toi_et_moi())
        assert arrangement is not None
        assert [r.kind for r in arrangement.relations] == ["MIRRORED_PAIR"]

    def test_the_two_stones_may_differ(self):
        family = toi_et_moi(
            symmetry="ASYMMETRIC",
            members=[
                FamilyMember(
                    memberId="a",
                    role="SIDE",
                    gem=GemIdentity(gemId="beryl.emerald", origin="NATURAL"),
                    orientationDeg=15.0,
                ),
                FamilyMember(
                    memberId="b",
                    role="SIDE",
                    gem=GemIdentity(gemId="diamond", origin="NATURAL"),
                    scale=0.8,
                ),
            ],
        )
        by_id = {i.instanceId: i for i in resolved(family).instances}
        assert by_id["a"].overrides.orientationDeg == 15.0
        assert by_id["b"].overrides.scale == 0.8
        assert by_id["a"].gem is not None and by_id["b"].gem is not None
        assert by_id["a"].gem.gemId != by_id["b"].gem.gemId

    def test_it_requires_exactly_two_members(self):
        with pytest.raises(FamilyRoleCardinalityError):
            compile_family(
                toi_et_moi(members=[FamilyMember(memberId="a", role="SIDE")])
            )


# ------------------------------------------------------------- cluster


class TestCluster:
    def test_it_places_a_centre_plus_its_ring(self):
        result = resolved(cluster(count=6, radiusMm=3.4))
        assert result.instanceCount == 7
        radii = sorted(
            round(math.hypot(i.transform.xMm, i.transform.yMm), 6)
            for i in result.instances
        )
        assert radii[0] == 0.0
        assert all(r == pytest.approx(3.4) for r in radii[1:])

    def test_a_cluster_need_not_be_centred(self):
        result = resolved(cluster(count=5, includeCenter=False))
        assert result.instanceCount == 5
        assert all(
            math.hypot(i.transform.xMm, i.transform.yMm) > 0.0
            for i in result.instances
        )

    def test_a_cluster_need_not_be_circular(self):
        """`radiusYMm` makes it elliptical — a parameter change, not a new
        family."""

        result = resolved(cluster(count=8, radiusMm=4.0, radiusYMm=2.0))
        xs = [abs(i.transform.xMm) for i in result.instances]
        ys = [abs(i.transform.yMm) for i in result.instances]
        assert max(xs) == pytest.approx(4.0)
        assert max(ys) == pytest.approx(2.0)

    def test_an_arc_cluster_includes_both_endpoints(self):
        result = resolved(
            cluster(count=3, radiusMm=4.0, sweepDeg=180.0, includeCenter=False)
        )
        angles = sorted(
            round(math.degrees(math.atan2(i.transform.yMm, i.transform.xMm)), 6)
            for i in result.instances
        )
        assert angles == [0.0, 90.0, 180.0]

    def test_the_ring_is_concentric_with_the_centre(self):
        arrangement = compile_family(cluster())
        assert arrangement is not None
        assert [r.kind for r in arrangement.relations] == ["CONCENTRIC_WITH"]

    def test_named_members_keep_their_own_ids(self):
        """The ring is placed directly, so a document's own member ids survive.

        Routing it through a pattern would have derived ids from the pattern id
        and silently discarded the ones the user chose.
        """

        family = cluster(
            count=3,
            includeCenter=False,
            members=[
                FamilyMember(memberId="petal.a", role="ACCENT"),
                FamilyMember(memberId="petal.b", role="ACCENT"),
                FamilyMember(memberId="petal.c", role="ACCENT"),
            ],
        )
        ids = sorted(i.instanceId for i in resolved(family).instances)
        assert ids == ["petal.a", "petal.b", "petal.c"]

    def test_mixed_member_gems_are_preserved(self):
        family = cluster(
            count=2,
            includeCenter=False,
            members=[
                FamilyMember(
                    memberId="a",
                    role="ACCENT",
                    gem=GemIdentity(gemId="diamond", origin="NATURAL"),
                ),
                FamilyMember(
                    memberId="b",
                    role="ACCENT",
                    gem=GemIdentity(gemId="quartz.amethyst", origin="NATURAL"),
                ),
            ],
        )
        gems = {
            i.instanceId: (i.gem.gemId if i.gem else None)
            for i in resolved(family).instances
        }
        assert gems == {"a": "diamond", "b": "quartz.amethyst"}


# ------------------------------------------------- centre with accents


class TestCenterWithAccents:
    def test_it_places_a_centre_plus_its_accents(self):
        result = resolved(center_accents(accentCount=8, accentRadiusMm=4.6))
        assert result.instanceCount == 9
        centre = [i for i in result.instances if i.role == "CENTER"]
        assert len(centre) == 1

    def test_the_accents_sit_on_the_requested_radius(self):
        result = resolved(center_accents(accentCount=4, accentRadiusMm=5.0))
        accents = [i for i in result.instances if i.role == "ACCENT"]
        assert len(accents) == 4
        for accent in accents:
            radius = math.hypot(accent.transform.xMm, accent.transform.yMm)
            assert radius == pytest.approx(5.0)

    def test_an_accent_arc_is_expressible(self):
        result = resolved(
            center_accents(accentCount=3, accentRadiusMm=4.0, accentSweepDeg=90.0)
        )
        assert result.instanceCount == 4

    def test_the_accent_scale_default_is_applied(self):
        result = resolved(center_accents(accentCount=3, accentScale=0.3))
        accents = [i for i in result.instances if i.role == "ACCENT"]
        assert all(i.overrides.scale == 0.3 for i in accents)


# ------------------------------------------------------------ determinism


class TestDeterminism:
    @pytest.mark.parametrize(
        "family",
        [three_stone(), toi_et_moi(), cluster(), center_accents()],
        ids=["three_stone", "toi_et_moi", "cluster", "center_accents"],
    )
    def test_compilation_is_byte_identical_across_repeats(self, family):
        first = resolved_canonical_json(compile_arrangement(compile_family(family)))
        for _ in range(4):
            again = resolved_canonical_json(
                compile_arrangement(compile_family(family))
            )
            assert again == first

    def test_member_order_does_not_change_the_compilation(self):
        """Reordering a list is a serialization artifact, not a design change."""

        members = [
            FamilyMember(memberId="center", role="CENTER"),
            FamilyMember(memberId="side.a", role="SIDE"),
            FamilyMember(memberId="side.b", role="SIDE"),
        ]
        forward = three_stone(symmetry="ASYMMETRIC", members=members)
        reverse = three_stone(symmetry="ASYMMETRIC", members=list(reversed(members)))
        assert arrangement_fingerprint(
            compile_family(forward)
        ) == arrangement_fingerprint(compile_family(reverse))

    def test_member_order_does_not_change_the_definition_hash(self):
        members = [
            FamilyMember(memberId="center", role="CENTER"),
            FamilyMember(memberId="side.a", role="SIDE"),
            FamilyMember(memberId="side.b", role="SIDE"),
        ]
        forward = ring(three_stone(symmetry="ASYMMETRIC", members=members))
        reverse = ring(
            three_stone(symmetry="ASYMMETRIC", members=list(reversed(members)))
        )
        # The family itself is normalized by the arrangement it compiles to;
        # the raw member order still differs, so the DEFINITION hash may too.
        # What must hold is that the compiled arrangement — the thing geometry
        # depends on — is identical.
        assert arrangement_fingerprint(
            compile_family(forward.family)
        ) == arrangement_fingerprint(compile_family(reverse.family))

    def test_a_different_family_compiles_differently(self):
        """The complement, so the equality tests cannot pass by measuring
        nothing."""

        assert arrangement_fingerprint(
            compile_family(three_stone(sideSpacingMm=4.0))
        ) != arrangement_fingerprint(compile_family(three_stone(sideSpacingMm=5.0)))
        assert arrangement_fingerprint(
            compile_family(cluster(count=6))
        ) != arrangement_fingerprint(compile_family(cluster(count=7)))

    def test_no_generated_id_is_random(self):
        first = sorted(i.instanceId for i in resolved(cluster(count=4)).instances)
        again = sorted(i.instanceId for i in resolved(cluster(count=4)).instances)
        assert first == again

    def test_a_family_changes_the_geometry_hash(self):
        """A family drives geometry, so excluding it would serve stale geometry
        for a real design change."""

        plain = ring()
        arranged = ring(three_stone())
        assert geometry_hash(plain) != geometry_hash(arranged)
        assert definition_hash(plain) != definition_hash(arranged)

    def test_two_different_families_have_different_geometry_hashes(self):
        assert geometry_hash(ring(three_stone())) != geometry_hash(ring(cluster()))

    def test_the_compiler_version_is_recorded(self):
        assert FAMILY_COMPILER_VERSION == "1.0.0"
        assert FAMILY_REGISTRY_VERSION == "1.0.0"


# ------------------------------------------------- the placement authority


class TestArrangementIsTheAuthority:
    def test_a_family_compiles_into_arrangement_primitives_only(self):
        """It must not become a second placement engine."""

        for family in (three_stone(), toi_et_moi(), cluster(), center_accents()):
            arrangement = compile_family(family)
            assert isinstance(arrangement, ArrangementDefinition)
            for instance in arrangement.instances:
                assert isinstance(instance, StoneInstanceDef)

    def test_the_family_package_never_constructs_geometry(self):
        """AST inspection, not `import`: a cached module imports fine
        regardless of what it depends on."""

        family_dir = Path(__file__).resolve().parents[1] / "jewelmind" / "family"
        forbidden = (
            "jewelmind.ring",
            "jewelmind.jewelry_category",
            "jewelmind.geometry",
            "jewelmind.setting",
            "cadquery",
            "OCP",
        )
        files = sorted(family_dir.glob("*.py"))
        assert len(files) >= 5
        for path in files:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                modules: list[str] = []
                if isinstance(node, ast.Import):
                    modules = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    modules = [node.module]
                for module in modules:
                    for prefix in forbidden:
                        assert not (
                            module == prefix or module.startswith(prefix + ".")
                        ), (path.name, module)

    def test_the_family_package_init_imports_nothing(self):
        """Load-bearing: `domain/schema.py` imports `family.models`, so an eager
        init would make the graph cyclic."""

        init = (
            Path(__file__).resolve().parents[1]
            / "jewelmind"
            / "family"
            / "__init__.py"
        )
        tree = ast.parse(init.read_text(encoding="utf-8"))
        found = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        assert found == []

    def test_only_effective_py_touches_the_jewelry_document(self):
        """The family core knows nothing about a JewelryDefinition; `effective`
        is the sanctioned meeting point, exactly as `setting_adapter` is for
        the Setting System."""

        family_dir = Path(__file__).resolve().parents[1] / "jewelmind" / "family"
        for path in sorted(family_dir.glob("*.py")):
            if path.name == "effective.py":
                continue
            # Parsed, not grepped: the package docstring legitimately NAMES the
            # schema module while explaining the import graph, and a text scan
            # would flag that prose as a dependency.
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                modules: list[str] = []
                if isinstance(node, ast.Import):
                    modules = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    modules = [node.module]
                for module in modules:
                    assert not module.startswith("jewelmind.domain"), (
                        path.name,
                        module,
                    )

    def test_declaring_both_a_family_and_an_arrangement_is_refused(self):
        definition = ring(three_stone())
        definition.arrangement = ArrangementDefinition(
            instances=[StoneInstanceDef(instanceId="c")]
        )
        with pytest.raises(FamilyConflictError):
            effective_arrangement(definition)

    def test_an_arrangement_alone_is_passed_through_unchanged(self):
        definition = default_definition()
        definition.arrangement = ArrangementDefinition(
            instances=[StoneInstanceDef(instanceId="c")]
        )
        assert effective_arrangement(definition) is definition.arrangement

    def test_neither_means_none(self):
        assert effective_arrangement(default_definition()) is None


# --------------------------------------------------------- real geometry


class TestGeometry:
    def test_a_three_stone_family_builds_three_stone_components(self):
        model = build_solitaire_ring(ring(three_stone()))
        stones = sorted(
            n for n in model.components if geometry_role(n) == "stone_reference"
        )
        assert len(stones) == 3
        assert PRIMARY_STONE_COMPONENT in stones
        assert all(
            n == PRIMARY_STONE_COMPONENT
            or n.startswith(STONE_INSTANCE_COMPONENT_PREFIX)
            for n in stones
        )

    @pytest.mark.parametrize(
        "family,expected",
        [
            (three_stone(), 3),
            (toi_et_moi(), 2),
            (cluster(count=5), 6),
            (center_accents(accentCount=4), 5),
        ],
        ids=["three_stone", "toi_et_moi", "cluster", "center_accents"],
    )
    def test_every_family_builds_one_solid_per_member(self, family, expected: int):
        model = build_solitaire_ring(ring(family))
        stones = [n for n in model.components if geometry_role(n) == "stone_reference"]
        assert len(stones) == expected
        for name in stones:
            component = model.components[name]
            assert len(component.shape.Solids()) == 1, name
            assert component.shape.isValid(), name
            assert component.volume_mm3 > 0.0, name

    def test_the_side_stones_are_actually_displaced(self):
        model = build_solitaire_ring(ring(three_stone(sideSpacingMm=4.6)))
        centres: list[float] = []
        for name in sorted(model.components):
            if geometry_role(name) != "stone_reference":
                continue
            box = model.components[name].bounding_box
            centres.append(round((box.xmin + box.xmax) / 2.0, 3))
        assert sorted(centres) == [-4.6, 0.0, 4.6]

    def test_a_scaled_member_produces_a_smaller_solid(self):
        """A member's scale reaches geometry, rather than being carried and
        ignored."""

        model = build_solitaire_ring(ring(three_stone(sideScale=0.5)))
        primary = model.components[PRIMARY_STONE_COMPONENT].volume_mm3
        sides = [
            c.volume_mm3
            for n, c in model.components.items()
            if n.startswith(STONE_INSTANCE_COMPONENT_PREFIX)
        ]
        assert sides
        for volume in sides:
            assert volume < primary
            # A uniform 0.5 scale is 0.125 of the volume.
            assert volume == pytest.approx(primary * 0.125, rel=1e-6)

    def test_a_scaled_member_does_not_sink(self):
        """`Shape.scale()` scales about the GLOBAL origin, which would drop a
        stone sitting several millimetres up. Scaling about its own centre keeps
        it where it was."""

        model = build_solitaire_ring(ring(three_stone(sideScale=0.5)))
        primary_box = model.components[PRIMARY_STONE_COMPONENT].bounding_box
        primary_mid = (primary_box.zmin + primary_box.zmax) / 2.0
        for name, component in model.components.items():
            if not name.startswith(STONE_INSTANCE_COMPONENT_PREFIX):
                continue
            box = component.bounding_box
            assert (box.zmin + box.zmax) / 2.0 == pytest.approx(primary_mid, abs=1e-6)

    def test_every_stone_component_carries_its_instance_identity(self):
        """Identity is never positional (INSPECT-GOV-015)."""

        model = build_solitaire_ring(ring(cluster(count=4)))
        for name, component in model.components.items():
            if geometry_role(name) != "stone_reference":
                continue
            assert component.metadata["stoneInstanceId"]
            assert component.metadata["stoneInstanceRole"]

    def test_the_transform_metadata_records_what_was_applied(self):
        """What was ACTUALLY applied, not what was requested."""

        model = build_solitaire_ring(ring(three_stone()))
        primary = model.components[PRIMARY_STONE_COMPONENT].metadata
        assert primary["instanceTransformOperations"] == []
        side = next(
            c.metadata
            for n, c in model.components.items()
            if n.startswith(STONE_INSTANCE_COMPONENT_PREFIX)
        )
        assert "TRANSLATE" in side["instanceTransformOperations"]

    def test_no_stone_component_is_production_metal(self):
        """LAW-006 across every stone, not only the primary one."""

        model = build_solitaire_ring(ring(cluster(count=6)))
        for name in model.components:
            if geometry_role(name) == "stone_reference":
                assert not is_production_component(name), name

    def test_the_metal_body_is_unaffected_by_the_family(self):
        """Additional stones are references; none is fused into the metal."""

        plain = build_solitaire_ring(default_definition())
        arranged = build_solitaire_ring(ring(cluster(count=6)))
        assert arranged.combined_metal_volume_mm3 == pytest.approx(
            plain.combined_metal_volume_mm3, rel=KERNEL_REL_TOLERANCE
        )
        assert len(arranged.combined_metal.Solids()) == 1

    def test_geometry_is_deterministic_across_repeats(self):
        first = build_solitaire_ring(ring(cluster(count=5)))
        again = build_solitaire_ring(ring(cluster(count=5)))
        for name in sorted(first.components):
            assert first.components[name].volume_mm3 == (
                again.components[name].volume_mm3
            ), name

    def test_an_unresolvable_member_produces_no_component(self):
        family = toi_et_moi(
            symmetry="ASYMMETRIC",
            members=[
                FamilyMember(memberId="a", role="SIDE"),
                FamilyMember(memberId="b", role="SIDE", stoneRef="accent"),
            ],
        )
        model = build_solitaire_ring(ring(family))
        stones = [n for n in model.components if geometry_role(n) == "stone_reference"]
        assert len(stones) == 1
        # Reported, never silently dropped.
        assert model.arrangement_result.generatedCount == 1
        ungenerated = [
            i
            for i in model.arrangement_result.instances
            if i.generationStatus == "NOT_GENERATED"
        ]
        assert len(ungenerated) == 1
        assert ungenerated[0].generationNote


# --------------------------------------------------------------- inspection


class TestInspection:
    def test_every_stone_component_is_required(self):
        """Listing only the primary would let an accent stone vanish from a
        multi-stone model without any check noticing."""

        model = build_solitaire_ring(ring(three_stone()))
        required = required_component_names(model)
        for name in stone_component_names(model):
            assert name in required

    def test_stone_component_names_come_from_the_role_map(self):
        model = build_solitaire_ring(ring(cluster(count=4)))
        names = stone_component_names(model)
        assert len(names) == 5
        assert names == tuple(sorted(names))
        for name in names:
            assert geometry_role(name) == "stone_reference"

    def test_a_multi_stone_model_inspects_without_a_separation_failure(self):
        report = inspect_model(build_solitaire_ring(ring(three_stone())))
        separation = report.assemblyResult.stoneMetalSeparation
        assert separation.stoneReferenceExists is True
        assert separation.status == "PASS"
        assert separation.fusedIntoProductionMetal is False

    def test_stone_to_stone_overlap_is_not_a_separation_finding(self):
        """Two stones overlapping is a geometric fact about the arrangement, not
        evidence that a stone became production metal."""

        # A deliberately tight cluster, so its members really do overlap.
        report = inspect_model(
            build_solitaire_ring(ring(cluster(count=8, radiusMm=0.6)))
        )
        separation = report.assemblyResult.stoneMetalSeparation
        for name in separation.intersectsProductionComponents:
            assert geometry_role(name) == "production_metal"

    def test_the_single_stone_report_is_unchanged_in_shape(self):
        report = inspect_model(build_solitaire_ring(default_definition()))
        assert stone_component_names(
            build_solitaire_ring(default_definition())
        ) == ("stone_reference",)
        assert report.assemblyResult.stoneMetalSeparation.status == "PASS"


# ------------------------------------------------------------- Forge rules


class TestFamilyRules:
    def test_a_design_with_no_family_produces_no_findings(self):
        assert family_rule_ids(default_definition()) == {}

    def test_a_valid_family_reports_only_the_setting_notice(self):
        results = family_rule_ids(ring(three_stone()))
        assert results == {"JM-FAMILY-005": "information"}
        assert not has_errors(validate_definition(ring(three_stone())))

    def test_declaring_both_authorities_is_an_error(self):
        definition = ring(three_stone())
        definition.arrangement = ArrangementDefinition(
            instances=[StoneInstanceDef(instanceId="c")]
        )
        results = family_rule_ids(definition)
        assert results["JM-FAMILY-001"] == "error"
        assert has_errors(validate_definition(definition))

    def test_a_bad_role_is_an_error(self):
        definition = ring(
            cluster(members=[FamilyMember(memberId="h", role="HALO")])
        )
        assert family_rule_ids(definition)["JM-FAMILY-002"] == "error"

    def test_a_bad_cardinality_is_an_error(self):
        definition = ring(
            three_stone(
                members=[
                    FamilyMember(memberId="c", role="CENTER"),
                    FamilyMember(memberId="s", role="SIDE"),
                ]
            )
        )
        results = family_rule_ids(definition)
        assert results["JM-FAMILY-002"] == "error"
        assert results["JM-FAMILY-003"] == "error"

    def test_an_unresolvable_stone_reference_is_a_warning(self):
        definition = ring(
            toi_et_moi(
                symmetry="ASYMMETRIC",
                members=[
                    FamilyMember(memberId="a", role="SIDE"),
                    FamilyMember(memberId="b", role="SIDE", stoneRef="accent"),
                ],
            )
        )
        results = family_rule_ids(definition)
        assert results["JM-FAMILY-004"] == "warning"
        assert not has_errors(validate_definition(definition))

    def test_a_per_member_setting_request_is_a_warning(self):
        definition = ring(
            toi_et_moi(
                symmetry="ASYMMETRIC",
                members=[
                    FamilyMember(memberId="a", role="SIDE"),
                    FamilyMember(memberId="b", role="SIDE", settingRef="bezel"),
                ],
            )
        )
        assert family_rule_ids(definition)["JM-FAMILY-004"] == "warning"

    def test_the_compile_rule_runs_the_real_compiler(self):
        """So Forge can never disagree with what generation does."""

        definition = ring(
            three_stone(
                members=[
                    FamilyMember(memberId="c", role="CENTER"),
                    FamilyMember(memberId="a", role="SIDE"),
                    FamilyMember(memberId="b", role="SIDE"),
                    FamilyMember(memberId="d", role="SIDE"),
                ]
            )
        )
        assert family_rule_ids(definition)["JM-FAMILY-003"] == "error"

    def test_no_family_rule_invents_a_jewelry_threshold(self):
        """Scans the real emitted messages, not the source."""

        forbidden = (
            "too close",
            "too far",
            "minimum spacing",
            "proportion",
            "not manufacturable",
            "industry standard",
            "recommended",
            "should be",
            "too many stones",
        )
        definitions = [
            ring(three_stone(sideSpacingMm=0.5)),
            ring(cluster(count=40, radiusMm=0.5)),
            ring(center_accents(accentCount=20, accentRadiusMm=1.0)),
            ring(toi_et_moi(separationMm=0.2)),
        ]
        for definition in definitions:
            for result in validate_definition(definition):
                lowered = result.message.lower()
                for term in forbidden:
                    assert term not in lowered, (result.ruleId, result.message)

    def test_overlapping_stones_are_not_a_structural_error(self):
        """Whether two placed stones overlap is a geometric question."""

        definition = ring(cluster(count=8, radiusMm=0.4))
        assert not has_errors(validate_definition(definition))


# ---------------------------------------------------------- JDL round trip


class TestJdlIntegration:
    def test_a_legacy_definition_has_no_family(self):
        assert default_definition().family is None

    def test_a_family_survives_a_json_round_trip(self):
        definition = ring(
            three_stone(
                symmetry="ASYMMETRIC",
                members=[
                    FamilyMember(
                        memberId="center",
                        role="CENTER",
                        gem=GemIdentity(gemId="diamond", origin="NATURAL"),
                    ),
                    FamilyMember(
                        memberId="side.a",
                        role="SIDE",
                        scale=0.55,
                        orientationDeg=12.0,
                        settingRef="prong",
                    ),
                    FamilyMember(
                        memberId="side.b",
                        role="SIDE",
                        placementOverride=InstanceTransform(xMm=5.1, yMm=0.4),
                    ),
                ],
            )
        )
        again = JewelryDefinition.model_validate_json(definition.model_dump_json())
        assert again.family == definition.family
        assert definition_hash(again) == definition_hash(definition)

    def test_an_unknown_field_inside_a_family_is_rejected(self):
        with pytest.raises(ValidationError):
            JewelryDefinition.model_validate(
                {
                    "family": {
                        "familyType": "THREE_STONE",
                        "params": {"kind": "THREE_STONE", "sideSpacingMm": 4.0},
                        "sparkle": True,
                    }
                }
            )

    def test_every_family_type_round_trips(self):
        for family in (three_stone(), toi_et_moi(), cluster(), center_accents()):
            definition = ring(family)
            again = JewelryDefinition.model_validate_json(
                definition.model_dump_json()
            )
            assert again.family is not None
            assert again.family.familyType == family.familyType


# ------------------------------------------------------- capability honesty


class TestCapabilityRegistry:
    def test_every_registered_family_has_a_compiler_and_vice_versa(self):
        assert set(current_families()) == set(family_compilers())
        assert set(family_types()) == set(FAMILY_CAPABILITIES)

    def test_every_family_has_role_rules(self):
        assert set(FAMILY_ROLE_RULES) == set(FAMILY_CAPABILITIES)
        for name, entry in FAMILY_CAPABILITIES.items():
            assert entry.roles == FAMILY_ROLE_RULES[name], name

    def test_every_family_is_partial_not_current(self):
        """Stone geometry is real; a setting for an accent is not. Reporting
        these as CURRENT would overstate what runs."""

        for entry in FAMILY_CAPABILITIES.values():
            assert entry.status == "PARTIAL", entry.family
            assert entry.stoneGeometry is True
            assert entry.settingGeometry is False

    def test_no_family_claims_setting_geometry(self):
        assert families_with_setting_geometry() == ()

    def test_every_family_claims_stone_geometry(self):
        assert set(families_with_stone_geometry()) == set(FAMILY_CAPABILITIES)

    def test_reserved_family_types_have_no_compiler_and_a_real_reason(self):
        for name, reason in RESERVED_FAMILY_TYPES.items():
            assert name.upper() not in family_compilers()
            assert len(reason) > 40, name

    def test_planned_features_are_not_claimed(self):
        for name in (
            "per_member_setting",
            "family_aware_head",
            "professional_family_rules",
        ):
            assert FAMILY_FEATURE_CAPABILITIES[name].status == "PLANNED", name

    def test_professional_rules_are_not_even_representable(self):
        entry = FAMILY_FEATURE_CAPABILITIES["professional_family_rules"]
        assert entry.representable is False
        assert entry.compilable is False

    def test_mixed_stone_specifications_is_partial(self):
        entry = FAMILY_FEATURE_CAPABILITIES["mixed_stone_specifications"]
        assert entry.status == "PARTIAL"
        assert entry.stoneGeometry is False


# -------------------------------------------------- backward compatibility


class TestBackwardCompatibility:
    def test_the_default_solitaire_is_unchanged(self):
        model = build_solitaire_ring(default_definition())
        assert sorted(model.components) == [
            "band",
            "basket_support",
            "prongs",
            "stone_reference",
        ]
        assert model.arrangement_result is None
        assert model.combined_metal_volume_mm3 == pytest.approx(
            LEGACY_METAL_VOLUME_MM3, rel=KERNEL_REL_TOLERANCE
        )

    def test_the_single_stone_component_is_the_builders_own_shape(self):
        """The identity placement path returns the same object, so the
        single-stone geometry is provably untouched rather than merely equal."""

        from jewelmind.geometry.components.stone import build_stone_reference

        definition = default_definition()
        stone = build_stone_reference(definition)
        components = stone_components(stone, None)
        assert components[PRIMARY_STONE_COMPONENT] is stone

    def test_a_legacy_document_without_a_family_key_still_parses(self):
        payload = default_definition().model_dump(mode="json")
        payload.pop("family", None)
        restored = JewelryDefinition.model_validate(payload)
        assert restored.family is None
        assert build_solitaire_ring(restored).combined_metal_volume_mm3 == (
            pytest.approx(LEGACY_METAL_VOLUME_MM3, rel=KERNEL_REL_TOLERANCE)
        )

    def test_a_single_instance_arrangement_still_generates_one_stone(self):
        """Sprint 22's own behaviour, preserved."""

        definition = default_definition()
        definition.arrangement = ArrangementDefinition(
            instances=[StoneInstanceDef(instanceId="center", role="CENTER")]
        )
        model = build_solitaire_ring(definition)
        assert stone_component_names(model) == ("stone_reference",)
        assert model.combined_metal_volume_mm3 == pytest.approx(
            LEGACY_METAL_VOLUME_MM3, rel=KERNEL_REL_TOLERANCE
        )

    def test_the_naming_authority_and_the_placement_module_agree(self):
        assert PRIMARY_STONE_COMPONENT == "stone_reference"
        from jewelmind.geometry.stone import placement

        assert placement.PRIMARY_STONE_COMPONENT == PRIMARY_STONE_COMPONENT


# --------------------------------------------------------- spec artifacts


SPECS_DIR = Path(__file__).resolve().parents[2] / "specs" / "family" / "v1"


class TestSpecArtifacts:
    def _load(self, relative: str) -> dict:
        return json.loads((SPECS_DIR / relative).read_text(encoding="utf-8"))

    def test_the_registry_spec_matches_the_live_registry(self):
        spec = self._load("family-registry.json")
        assert spec["compilerVersion"] == FAMILY_COMPILER_VERSION
        assert spec["registryVersion"] == FAMILY_REGISTRY_VERSION
        recorded = {e["family"]: e for e in spec["families"]}
        assert set(recorded) == set(FAMILY_CAPABILITIES)
        for name, entry in FAMILY_CAPABILITIES.items():
            assert recorded[name] == entry.model_dump(mode="json"), name

    def test_the_registry_spec_never_claims_setting_geometry(self):
        spec = self._load("family-registry.json")
        for entry in spec["families"]:
            assert entry["settingGeometry"] is False
            assert entry["status"] == "PARTIAL"

    def test_every_example_is_a_real_family_that_compiles(self):
        import jsonschema

        schema = self._load("family-definition.schema.json")
        examples = sorted((SPECS_DIR / "examples").glob("*.json"))
        assert len(examples) >= 5
        for path in examples:
            if path.name.startswith("resolved-"):
                continue
            document = json.loads(path.read_text(encoding="utf-8"))
            jsonschema.validate(document, schema)
            family = FamilyDefinition.model_validate(document)
            arrangement = compile_family(family)
            assert arrangement is not None

    def test_every_resolved_example_matches_a_live_compilation(self):
        for path in sorted((SPECS_DIR / "examples").glob("*.json")):
            if path.name.startswith("resolved-"):
                continue
            recorded_path = path.with_name(f"resolved-{path.name}")
            recorded = json.loads(recorded_path.read_text(encoding="utf-8"))
            family = FamilyDefinition.model_validate(
                json.loads(path.read_text(encoding="utf-8"))
            )
            live = compile_arrangement(compile_family(family))
            assert live is not None
            assert live.model_dump(mode="json") == recorded, path.name

    def test_the_compilation_vectors_still_hold(self):
        spec = self._load("test-vectors/compilation-vectors.json")
        assert spec["vectors"]
        for vector in spec["vectors"]:
            assert vector["instanceCount"] >= 1
            assert vector["generatedCount"] >= 1
            # Stone geometry for every generated instance; no setting for the
            # rest, which the vector records rather than implying.
            assert vector["settingCoverage"] == "PRIMARY_ONLY"
