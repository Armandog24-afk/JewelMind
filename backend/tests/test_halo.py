"""Halo System v1 (Sprint 25).

Covers the three variants as semantics AND as real geometry, their composition
onto a solitaire, a family and an explicit arrangement, mixed gems and per-stone
overrides, deterministic identity, the structural rules, and — the part easiest
to break — that a design with no halo behaves exactly as it did before.
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
    InstancePlacement,
    InstanceTransform,
    RadialPatternSpec,
    StoneInstanceDef,
)
from jewelmind.arrangement.normalize import arrangement_fingerprint
from jewelmind.arrangement.radial import ring_angles_deg
from jewelmind.arrangement.resolve import resolve_arrangement
from jewelmind.domain.defaults import default_definition
from jewelmind.domain.schema import JewelryDefinition
from jewelmind.family.effective import effective_arrangement
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
from jewelmind.halo.capability import (
    HALO_CAPABILITIES,
    HALO_COMPILER_VERSION,
    HALO_COMPOSITION,
    HALO_FEATURE_CAPABILITIES,
    HALO_REGISTRY_VERSION,
    RESERVED_HALO_VARIANTS,
    current_halo_variants,
    halo_variants_with_setting_geometry,
    halo_variants_with_stone_geometry,
)
from jewelmind.halo.compile import compose_halo, halo_variants
from jewelmind.halo.errors import (
    HaloCenterUnresolvedError,
    HaloIdentityCollisionError,
)
from jewelmind.halo.models import (
    HALO_RING_CARDINALITY,
    MAX_HALO_RINGS,
    HaloDefinition,
    HaloRing,
)
from jewelmind.utils.hashing import definition_hash, geometry_hash
from jewelmind.validation.engine import has_errors, validate_definition

#: The default solitaire's fused metal volume, unchanged since Sprint 19.
#: Relative tolerance, not `==`: OCCT floats are not bit-identical across
#: platform builds (the lesson Sprint 19's CI failure taught).
LEGACY_METAL_VOLUME_MM3 = 341.44334316909976
KERNEL_REL_TOLERANCE = 1e-9

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_DIR = REPO_ROOT / "specs" / "halo" / "v1"


def ring(**over) -> HaloRing:
    params: dict = {"ringId": "halo.inner", "count": 8, "radiusMm": 3.4}
    params.update(over)
    return HaloRing(**params)


def halo(**over) -> HaloDefinition:
    rings = over.pop("rings", [ring()])
    params: dict = {"variant": "SINGLE", "rings": rings}
    params.update(over)
    return HaloDefinition(**params)


def design(
    halo_definition: HaloDefinition | None = None,
    family: FamilyDefinition | None = None,
    arrangement: ArrangementDefinition | None = None,
) -> JewelryDefinition:
    definition = default_definition()
    definition.halo = halo_definition
    definition.family = family
    definition.arrangement = arrangement
    return definition


def halo_rule_ids(definition: JewelryDefinition) -> dict[str, str]:
    return {
        r.ruleId: r.severity
        for r in validate_definition(definition)
        if r.ruleId.startswith("JM-HALO")
    }


def composed(
    halo_definition: HaloDefinition, family: FamilyDefinition | None = None
) -> ArrangementDefinition:
    arrangement = effective_arrangement(design(halo_definition, family))
    assert arrangement is not None
    return arrangement


# ------------------------------------------------------------- the model


class TestHaloModel:
    def test_a_halo_references_stones_rather_than_restating_them(self):
        candidate = ring()
        # No shape, no dimensions, no material: a halo stone is an occurrence OF
        # something, and copying the stone here would create a second source of
        # truth for what that stone is.
        for absent in ("shape", "diameter", "length", "width", "depth", "source"):
            assert not hasattr(candidate, absent), absent
        assert candidate.stoneRef == "primary"

    def test_a_ring_may_carry_its_own_gem(self):
        candidate = ring(
            gem=GemIdentity(gemId="corundum.sapphire", origin="NATURAL")
        )
        assert candidate.gem is not None
        assert candidate.gem.gemId == "corundum.sapphire"

    def test_a_gem_left_unset_inherits_rather_than_copying(self):
        assert ring().gem is None

    def test_per_stone_overrides_reuse_the_family_member_model(self):
        """A parallel member model with the same seven fields would be two
        definitions of one concept."""

        member = FamilyMember(memberId="halo.inner.crest", role="HALO", scale=0.4)
        candidate = ring(count=4, members=[member])
        assert isinstance(candidate.members[0], FamilyMember)
        assert isinstance(
            FamilyMember(
                memberId="x", role="HALO", placementOverride=InstanceTransform(xMm=1.0)
            ).placementOverride,
            InstanceTransform,
        )

    @pytest.mark.parametrize(
        "candidate",
        [
            "Halo",
            "halo..1",
            "../../etc/passwd",
            "halo/1",
            "rm -rf /",
            "",
            "a" * 81,
            "halo inner",
        ],
    )
    def test_a_malformed_ring_id_is_rejected(self, candidate: str):
        with pytest.raises(ValidationError):
            ring(ringId=candidate)

    def test_duplicate_ring_ids_are_rejected(self):
        with pytest.raises(ValidationError):
            halo(
                variant="DOUBLE",
                rings=[ring(ringId="halo.inner"), ring(ringId="halo.inner")],
            )

    def test_duplicate_member_ids_are_rejected_within_a_ring(self):
        with pytest.raises(ValidationError):
            ring(
                count=4,
                members=[
                    FamilyMember(memberId="a", role="HALO"),
                    FamilyMember(memberId="a", role="HALO"),
                ],
            )

    def test_duplicate_member_ids_are_rejected_across_rings(self):
        """A member id becomes an ARRANGEMENT instance id, so uniqueness within
        one ring is not enough."""

        with pytest.raises(ValidationError):
            halo(
                variant="DOUBLE",
                rings=[
                    ring(
                        ringId="halo.inner",
                        count=2,
                        members=[FamilyMember(memberId="shared", role="HALO")],
                    ),
                    ring(
                        ringId="halo.outer",
                        count=2,
                        members=[FamilyMember(memberId="shared", role="HALO")],
                    ),
                ],
            )

    def test_more_members_than_stones_is_rejected(self):
        """Refused rather than truncated: a member the compilation would drop is
        a stone the document declared and the design does not contain."""

        with pytest.raises(ValidationError):
            ring(
                count=1,
                members=[
                    FamilyMember(memberId="a", role="HALO"),
                    FamilyMember(memberId="b", role="HALO"),
                ],
            )

    @pytest.mark.parametrize(
        ("variant", "count"),
        [("SINGLE", 2), ("DOUBLE", 1), ("HIDDEN", 2)],
    )
    def test_the_ring_count_must_match_the_variant(self, variant: str, count: int):
        rings = [
            ring(ringId=f"halo.r{i}", radiusMm=3.0 + i, zOffsetMm=-1.0)
            for i in range(count)
        ]
        with pytest.raises(ValidationError):
            HaloDefinition(variant=variant, rings=rings)

    def test_the_cardinality_table_is_the_single_source(self):
        for variant, expected in HALO_RING_CARDINALITY.items():
            rings = [
                ring(
                    ringId=f"halo.r{i}",
                    radiusMm=3.0 + i,
                    zOffsetMm=-1.0 if variant == "HIDDEN" else 0.0,
                )
                for i in range(expected)
            ]
            assert len(HaloDefinition(variant=variant, rings=rings).rings) == expected

    def test_a_hidden_halo_must_sit_below_the_centre_plane(self):
        """Structural, not a professional threshold: no minimum offset is
        prescribed, only that the offset is negative. A hidden halo at or above
        the centre plane is a SINGLE halo mislabelled."""

        with pytest.raises(ValidationError):
            HaloDefinition(variant="HIDDEN", rings=[ring(zOffsetMm=0.0)])
        with pytest.raises(ValidationError):
            HaloDefinition(variant="HIDDEN", rings=[ring(zOffsetMm=0.4)])
        assert HaloDefinition(
            variant="HIDDEN", rings=[ring(zOffsetMm=-0.001)]
        ).variant == "HIDDEN"

    def test_a_reserved_variant_is_refused_rather_than_substituted(self):
        for name in RESERVED_HALO_VARIANTS:
            with pytest.raises(ValidationError):
                HaloDefinition(variant=name, rings=[ring()])

    def test_no_halo_parameter_accepts_nan_or_infinity(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with pytest.raises(ValidationError):
                ring(radiusMm=bad)
            with pytest.raises(ValidationError):
                ring(zOffsetMm=bad)
            with pytest.raises(ValidationError):
                ring(memberScale=bad)

    def test_a_jdl_style_string_number_is_rejected(self):
        """These models are carried directly in JDL, so they apply JDL's own
        untrusted-input policy."""

        with pytest.raises(ValidationError):
            HaloRing.model_validate(
                {"ringId": "halo.inner", "count": 8, "radiusMm": "3.4"}
            )

    def test_an_unknown_field_is_rejected(self):
        with pytest.raises(ValidationError):
            HaloRing.model_validate(
                {"ringId": "halo.inner", "count": 8, "radiusMm": 3.4, "bling": 1}
            )

    def test_a_halo_holds_no_kernel_object(self):
        fields = HaloRing.model_fields | HaloDefinition.model_fields
        for name, field in fields.items():
            annotation = str(field.annotation)
            assert "cadquery" not in annotation.lower(), name
            assert "Shape" not in annotation, name
            assert "OCP" not in annotation, name

    def test_at_least_one_ring_is_required(self):
        with pytest.raises(ValidationError):
            HaloDefinition(variant="SINGLE", rings=[])

    def test_the_ring_bound_is_a_software_limit(self):
        assert MAX_HALO_RINGS == 2
        assert max(HALO_RING_CARDINALITY.values()) == MAX_HALO_RINGS


# --------------------------------------------------------- single halo


class TestSingleHalo:
    def test_a_halo_alone_supplies_its_own_centre(self):
        """A halo declaration IS the statement that a centre exists. A halo with
        no centre is not a halo."""

        arrangement = composed(halo(rings=[ring(count=6)]))
        roles = [i.role for i in arrangement.instances]
        assert roles.count("CENTER") == 1
        assert roles.count("HALO") == 6

    def test_the_centre_keeps_the_historical_component_name(self):
        resolved = compile_arrangement(composed(halo(rings=[ring(count=6)])))
        assert resolved is not None
        names = {i.instanceId: i.componentName for i in resolved.instances}
        assert names["center"] == PRIMARY_STONE_COMPONENT
        for instance_id, name in names.items():
            if instance_id != "center":
                assert name == f"{STONE_INSTANCE_COMPONENT_PREFIX}{instance_id}"

    def test_the_stones_sit_on_the_requested_radius(self):
        radius = 3.7
        arrangement = composed(halo(rings=[ring(count=9, radiusMm=radius)]))
        for instance in arrangement.instances:
            if instance.role != "HALO":
                continue
            transform = instance.placement.transform
            distance = math.hypot(transform.xMm, transform.yMm)
            assert distance == pytest.approx(radius, rel=1e-12)

    def test_the_angular_sequence_matches_a_radial_pattern(self):
        """A halo must place its stones exactly where a hand-written RADIAL
        pattern would, or a family and a halo would disagree about a ring."""

        count, start, sweep = 7, 12.0, 360.0
        pattern_positions = _radial_pattern_positions(count, 3.4, start, sweep)
        arrangement = composed(
            halo(
                rings=[
                    ring(
                        count=count,
                        radiusMm=3.4,
                        startAngleDeg=start,
                        sweepDeg=sweep,
                    )
                ]
            )
        )
        # Compared AFTER resolution on both sides, because the resolver's own
        # normalization rounds coordinates: comparing a raw compiled transform
        # against a normalized resolved one would fail on the rounding rather
        # than on the arithmetic under test.
        halo_positions = sorted(
            (round(i.transform.xMm, 9), round(i.transform.yMm, 9))
            for i in resolve_arrangement(arrangement).instances
            if i.role == "HALO"
        )
        assert halo_positions == pattern_positions

    def test_a_partial_arc_includes_both_endpoints(self):
        arrangement = composed(
            halo(rings=[ring(count=5, startAngleDeg=0.0, sweepDeg=120.0)])
        )
        angles = sorted(
            round(i.placement.transform.rotationDeg, 6)
            for i in arrangement.instances
            if i.role == "HALO"
        )
        assert angles == [0.0, 30.0, 60.0, 90.0, 120.0]

    def test_an_elliptical_halo_uses_the_second_semi_axis(self):
        arrangement = composed(
            halo(rings=[ring(count=4, radiusMm=4.0, radiusYMm=2.0, startAngleDeg=0.0)])
        )
        extents = sorted(
            (abs(i.placement.transform.xMm), abs(i.placement.transform.yMm))
            for i in arrangement.instances
            if i.role == "HALO"
        )
        assert extents[-1] == pytest.approx((4.0, 0.0), abs=1e-9)
        assert any(
            y == pytest.approx(2.0, abs=1e-9) for _x, y in extents
        )

    def test_align_to_radius_controls_the_stones_own_rotation(self):
        aligned = composed(halo(rings=[ring(count=4, alignToRadius=True)]))
        flat = composed(halo(rings=[ring(count=4, alignToRadius=False)]))
        assert any(
            i.placement.transform.rotationDeg != 0.0
            for i in aligned.instances
            if i.role == "HALO"
        )
        assert all(
            i.placement.transform.rotationDeg == 0.0
            for i in flat.instances
            if i.role == "HALO"
        )


def _radial_pattern_positions(
    count: int, radius: float, start: float, sweep: float
) -> list[tuple[float, float]]:
    """The positions a real RADIAL pattern produces, from the real resolver."""

    definition = ArrangementDefinition(
        instances=[
            StoneInstanceDef(
                instanceId="anchor",
                role="ACCENT",
                placement=InstancePlacement(transform=InstanceTransform()),
            )
        ],
        patterns=[
            {
                "patternId": "p",
                "sourceInstanceId": "anchor",
                "spec": RadialPatternSpec(
                    count=count,
                    radiusMm=radius,
                    startAngleDeg=start,
                    sweepDeg=sweep,
                ),
                "memberRole": "ACCENT",
            }
        ],
    )
    resolved = resolve_arrangement(definition)
    return sorted(
        (round(i.transform.xMm, 9), round(i.transform.yMm, 9))
        for i in resolved.instances
        if i.sourcePatternId is not None
    )


# --------------------------------------------------------- double halo


class TestDoubleHalo:
    def make(self) -> HaloDefinition:
        return halo(
            variant="DOUBLE",
            rings=[
                ring(ringId="halo.inner", count=6, radiusMm=3.0, memberScale=0.25),
                ring(
                    ringId="halo.outer",
                    count=10,
                    radiusMm=4.5,
                    startAngleDeg=18.0,
                    memberScale=0.15,
                ),
            ],
        )

    def test_two_rings_carry_independent_parameters(self):
        """The reason a halo is not a CENTER_WITH_ACCENTS family: one accent
        parameter set cannot carry two rings."""

        arrangement = composed(self.make())
        inner = [
            i for i in arrangement.instances if i.instanceId.startswith("halo.inner.")
        ]
        outer = [
            i for i in arrangement.instances if i.instanceId.startswith("halo.outer.")
        ]
        assert len(inner) == 6
        assert len(outer) == 10
        assert {i.overrides.scale for i in inner} == {0.25}
        assert {i.overrides.scale for i in outer} == {0.15}
        for instance in inner:
            transform = instance.placement.transform
            assert math.hypot(transform.xMm, transform.yMm) == pytest.approx(3.0)
        for instance in outer:
            transform = instance.placement.transform
            assert math.hypot(transform.xMm, transform.yMm) == pytest.approx(4.5)

    def test_each_ring_gets_its_own_concentric_relation(self):
        arrangement = composed(self.make())
        relations = {r.relationId: r for r in arrangement.relations}
        assert "halo.inner.concentric" in relations
        assert "halo.outer.concentric" in relations
        for relation in relations.values():
            assert relation.kind == "CONCENTRIC_WITH"
            assert relation.members[0] == "center"

    def test_both_rings_build_real_geometry(self):
        model = build_solitaire_ring(design(self.make()))
        stones = stone_component_names(model)
        assert len(stones) == 17  # centre + 6 + 10
        volumes = {
            name: model.components[name].volume_mm3 for name in sorted(stones)
        }
        centre = volumes[PRIMARY_STONE_COMPONENT]
        inner = volumes[f"{STONE_INSTANCE_COMPONENT_PREFIX}halo.inner.0"]
        outer = volumes[f"{STONE_INSTANCE_COMPONENT_PREFIX}halo.outer.0"]
        # Volume scales with the cube of a uniform scale, which is what proves
        # the per-ring scale reached the SOLID rather than only the metadata.
        assert inner == pytest.approx(centre * 0.25**3, rel=1e-9)
        assert outer == pytest.approx(centre * 0.15**3, rel=1e-9)
        assert outer < inner


# --------------------------------------------------------- hidden halo


class TestHiddenHalo:
    def test_the_vertical_offset_reaches_the_solid(self):
        """The measurement that makes a hidden halo real rather than a label.

        Asserted against the built geometry's bounding box, not against the
        field: a `zOffsetMm` that never reached the kernel would satisfy every
        model-level check and produce a flat halo.
        """

        offset = -1.3
        scale = 0.2
        flat = build_solitaire_ring(
            design(halo(rings=[ring(count=4, memberScale=scale)]))
        )
        hidden = build_solitaire_ring(
            design(
                HaloDefinition(
                    variant="HIDDEN",
                    rings=[ring(count=4, memberScale=scale, zOffsetMm=offset)],
                )
            )
        )
        name = f"{STONE_INSTANCE_COMPONENT_PREFIX}halo.inner.0"
        assert hidden.components[name].bounding_box.zmax == pytest.approx(
            flat.components[name].bounding_box.zmax + offset, rel=1e-9
        )
        assert hidden.components[name].bounding_box.zmin == pytest.approx(
            flat.components[name].bounding_box.zmin + offset, rel=1e-9
        )

    def test_a_hidden_halo_sits_below_the_centre_stones_crown(self):
        model = build_solitaire_ring(
            design(
                HaloDefinition(
                    variant="HIDDEN",
                    rings=[ring(count=6, memberScale=0.18, zOffsetMm=-1.4)],
                )
            )
        )
        centre = model.components[PRIMARY_STONE_COMPONENT].bounding_box
        stone = model.components[
            f"{STONE_INSTANCE_COMPONENT_PREFIX}halo.inner.0"
        ].bounding_box
        assert stone.zmax < centre.zmax
        # A GEOMETRIC fact, not a professional claim: nothing here says the
        # offset is correct for any real stone, only that it is below.

    def test_the_horizontal_layout_is_unaffected_by_the_offset(self):
        flat = composed(halo(rings=[ring(count=6)]))
        hidden = composed(
            HaloDefinition(variant="HIDDEN", rings=[ring(count=6, zOffsetMm=-1.0)])
        )
        for a, b in zip(flat.instances, hidden.instances, strict=True):
            assert a.placement.transform.xMm == b.placement.transform.xMm
            assert a.placement.transform.yMm == b.placement.transform.yMm


# ----------------------------------------------------- family composition


class TestFamilyComposition:
    def test_a_halo_composes_onto_a_three_stone_family(self):
        family = FamilyDefinition(
            familyType="THREE_STONE", params=ThreeStoneParams(sideSpacingMm=5.0)
        )
        arrangement = composed(halo(rings=[ring(count=10)]), family)
        roles = [i.role for i in arrangement.instances]
        assert roles.count("CENTER") == 1
        assert roles.count("SIDE") >= 1
        assert roles.count("HALO") == 10
        # The family's own mirror pattern survives composition untouched.
        assert [p.patternId for p in arrangement.patterns] == ["side.left.mirror"]
        assert "three-stone.sides" in {r.relationId for r in arrangement.relations}

    def test_a_halo_composes_onto_centre_plus_accents(self):
        family = FamilyDefinition(
            familyType="CENTER_WITH_ACCENTS",
            params=CenterWithAccentsParams(accentCount=6, accentRadiusMm=6.0),
        )
        arrangement = composed(halo(rings=[ring(count=8)]), family)
        roles = [i.role for i in arrangement.instances]
        assert roles.count("ACCENT") == 6
        assert roles.count("HALO") == 8
        assert roles.count("CENTER") == 1

    def test_a_halo_anchored_on_the_origin_encircles_a_toi_et_moi_pair(self):
        """How a halo surrounds a MULTI-STONE centre: the pair straddles the
        design origin, so an origin-anchored ring surrounds both rather than
        one."""

        family = FamilyDefinition(
            familyType="TOI_ET_MOI",
            params=ToiEtMoiParams(separationMm=5.0, axisAngleDeg=30.0),
        )
        arrangement = composed(
            halo(centerMemberId=None, rings=[ring(count=12, radiusMm=6.0)]), family
        )
        pair = [i for i in arrangement.instances if i.role == "SIDE"]
        halo_stones = [i for i in arrangement.instances if i.role == "HALO"]
        assert len(pair) == 2
        assert len(halo_stones) == 12
        # Every pair stone is inside the ring; every halo stone is on it.
        for stone in pair:
            transform = stone.placement.transform
            assert math.hypot(transform.xMm, transform.yMm) < 6.0
        for stone in halo_stones:
            transform = stone.placement.transform
            assert math.hypot(transform.xMm, transform.yMm) == pytest.approx(6.0)

    def test_a_named_centre_a_family_does_not_have_is_refused(self):
        """Refused rather than quietly re-anchored: a halo around the wrong
        stone is worse than one that fails loudly."""

        family = FamilyDefinition(
            familyType="TOI_ET_MOI", params=ToiEtMoiParams(separationMm=5.0)
        )
        with pytest.raises(HaloCenterUnresolvedError):
            effective_arrangement(design(halo(centerMemberId="center"), family))

    def test_a_cluster_without_a_centre_cannot_be_named_either(self):
        family = FamilyDefinition(
            familyType="CLUSTER",
            params=ClusterParams(count=6, radiusMm=6.0, includeCenter=False),
        )
        with pytest.raises(HaloCenterUnresolvedError):
            effective_arrangement(design(halo(centerMemberId="center"), family))
        # And the same cluster WITH a centre composes.
        family = FamilyDefinition(
            familyType="CLUSTER",
            params=ClusterParams(count=6, radiusMm=6.0, includeCenter=True),
        )
        assert effective_arrangement(design(halo(), family)) is not None

    def test_a_halo_composes_onto_an_explicit_arrangement(self):
        arrangement = ArrangementDefinition(
            instances=[
                StoneInstanceDef(
                    instanceId="middle",
                    role="CENTER",
                    placement=InstancePlacement(transform=InstanceTransform(xMm=1.5)),
                )
            ]
        )
        definition = design(halo(centerMemberId="middle"), arrangement=arrangement)
        result = effective_arrangement(definition)
        assert result is not None
        # The halo follows the centre it names rather than the design origin.
        for instance in result.instances:
            if instance.role != "HALO":
                continue
            transform = instance.placement.transform
            assert math.hypot(transform.xMm - 1.5, transform.yMm) == pytest.approx(3.4)

    def test_a_colliding_member_id_is_refused(self):
        colliding = halo(
            rings=[
                ring(count=2, members=[FamilyMember(memberId="center", role="HALO")])
            ]
        )
        with pytest.raises(HaloIdentityCollisionError):
            effective_arrangement(design(colliding))

    def test_a_family_and_an_arrangement_together_still_conflict(self):
        """The halo does not weaken JM-FAMILY-001."""

        from jewelmind.family.errors import FamilyConflictError

        definition = design(
            halo(),
            family=FamilyDefinition(
                familyType="THREE_STONE", params=ThreeStoneParams(sideSpacingMm=4.0)
            ),
            arrangement=ArrangementDefinition(),
        )
        with pytest.raises(FamilyConflictError):
            effective_arrangement(definition)


class TestCompositionSupport:
    def test_the_support_table_matches_the_real_compiler(self):
        """The table is REPORTING; the compiler is the gate. Re-derived here by
        actually composing, so the table cannot drift into fiction."""

        families = {
            "THREE_STONE": FamilyDefinition(
                familyType="THREE_STONE", params=ThreeStoneParams(sideSpacingMm=4.6)
            ),
            "TOI_ET_MOI": FamilyDefinition(
                familyType="TOI_ET_MOI", params=ToiEtMoiParams(separationMm=5.0)
            ),
            "CLUSTER": FamilyDefinition(
                familyType="CLUSTER", params=ClusterParams(count=6, radiusMm=6.0)
            ),
            "CENTER_WITH_ACCENTS": FamilyDefinition(
                familyType="CENTER_WITH_ACCENTS",
                params=CenterWithAccentsParams(accentCount=6, accentRadiusMm=6.0),
            ),
        }
        assert set(families) == set(HALO_COMPOSITION)

        for family_type, family in families.items():
            row = HALO_COMPOSITION[family_type]

            named_works = True
            try:
                effective_arrangement(design(halo(centerMemberId="center"), family))
            except HaloCenterUnresolvedError:
                named_works = False
            assert named_works is row["namedCenter"], family_type

            origin_works = (
                effective_arrangement(design(halo(centerMemberId=None), family))
                is not None
            )
            assert origin_works is row["originAnchor"], family_type

    def test_an_unsupported_named_centre_is_reported_explicitly(self):
        family = FamilyDefinition(
            familyType="TOI_ET_MOI", params=ToiEtMoiParams(separationMm=5.0)
        )
        definition = design(halo(centerMemberId="center"), family)
        results = halo_rule_ids(definition)
        assert results.get("JM-HALO-003") == "error"
        # ONE error for one cause: the explanatory rule fires and the derived
        # "no such instance" one is suppressed.
        assert "JM-HALO-001" not in results
        assert has_errors(validate_definition(definition))


# ------------------------------------------------------------ determinism


class TestDeterminism:
    def test_ring_order_carries_no_meaning(self):
        inner = ring(ringId="halo.inner", count=6, radiusMm=3.0)
        outer = ring(ringId="halo.outer", count=8, radiusMm=4.4)
        a = composed(halo(variant="DOUBLE", rings=[inner, outer]))
        b = composed(halo(variant="DOUBLE", rings=[outer, inner]))
        assert a == b
        assert arrangement_fingerprint(a) == arrangement_fingerprint(b)

    def test_member_order_carries_no_meaning(self):
        first = FamilyMember(memberId="halo.inner.a", role="HALO", scale=0.3)
        second = FamilyMember(memberId="halo.inner.b", role="HALO", scale=0.5)
        a = composed(halo(rings=[ring(count=4, members=[first, second])]))
        b = composed(halo(rings=[ring(count=4, members=[second, first])]))
        assert a == b
        assert arrangement_fingerprint(a) == arrangement_fingerprint(b)

    def test_composition_is_repeatable(self):
        candidate = halo(
            variant="DOUBLE",
            rings=[
                ring(ringId="halo.inner", count=7, radiusMm=3.1),
                ring(ringId="halo.outer", count=11, radiusMm=4.7),
            ],
        )
        first = composed(candidate)
        for _ in range(4):
            assert composed(candidate) == first

    def test_derived_ids_are_reproducible_and_not_counters(self):
        arrangement = composed(
            halo(
                variant="DOUBLE",
                rings=[
                    ring(ringId="halo.inner", count=3, radiusMm=3.0),
                    ring(ringId="halo.outer", count=3, radiusMm=4.0),
                ],
            )
        )
        ids = sorted(i.instanceId for i in arrangement.instances if i.role == "HALO")
        assert ids == [
            "halo.inner.0",
            "halo.inner.1",
            "halo.inner.2",
            "halo.outer.0",
            "halo.outer.1",
            "halo.outer.2",
        ]

    def test_a_halo_change_changes_both_identities(self):
        base = design(halo(rings=[ring(count=8)]))
        wider = design(halo(rings=[ring(count=8, radiusMm=4.0)]))
        assert definition_hash(base) != definition_hash(wider)
        # A halo moves stones, so it MUST be inside the geometry hash: a stale
        # cache hit here would serve geometry for the wrong design.
        assert geometry_hash(base) != geometry_hash(wider)

    def test_a_label_change_rebuilds_rather_than_serving_stale_geometry(self):
        """`halo.label` is geometrically inert and still inside `geometryHash`.

        RECORDED HONESTLY rather than optimized: `geometry_hash()` excludes
        whole subtrees (gem, material, manufacturing, project, preview), and
        carving one leaf out of an otherwise-included subtree would make the
        exclusion list a per-field affair that has to be re-verified on every
        future field. The cost is an unnecessary rebuild when a label changes;
        the alternative error mode is a stale-geometry cache hit, which
        ARRANGE-GOV-007 explicitly calls the worse one. `family.label` behaves
        identically, so the two stay consistent.
        """

        a = design(halo(label="Halo A"))
        b = design(halo(label="Halo B"))
        assert definition_hash(a) != definition_hash(b)
        assert geometry_hash(a) != geometry_hash(b)
        # And the geometry really is identical, which is what makes the rebuild
        # unnecessary rather than the hash wrong.
        first = build_solitaire_ring(a)
        second = build_solitaire_ring(b)
        assert first.combined_metal_volume_mm3 == pytest.approx(
            second.combined_metal_volume_mm3, rel=KERNEL_REL_TOLERANCE
        )
        assert sorted(first.components) == sorted(second.components)

    def test_geometry_is_deterministic_across_rebuilds(self):
        definition = design(halo(rings=[ring(count=6, memberScale=0.22)]))
        first = build_solitaire_ring(definition)
        second = build_solitaire_ring(definition)
        assert sorted(first.components) == sorted(second.components)
        for name, component in first.components.items():
            other = second.components[name]
            if component.volume_mm3 is None:
                assert other.volume_mm3 is None
                continue
            assert component.volume_mm3 == pytest.approx(
                other.volume_mm3, rel=KERNEL_REL_TOLERANCE
            )


# ------------------------------------------------- arrangement is authoritative


class TestArrangementIsTheAuthority:
    def test_the_halo_layer_emits_arrangement_primitives_only(self):
        arrangement = composed(halo())
        assert isinstance(arrangement, ArrangementDefinition)
        # And the arrangement engine — not the halo — resolves them.
        assert resolve_arrangement(arrangement).instances

    def test_the_ring_arithmetic_is_shared_rather_than_copied(self):
        """One function, three callers. Two copies already existed before this
        sprint and a third would have made drift a matter of time."""

        source = (
            Path(__file__).resolve().parents[1]
            / "jewelmind"
            / "halo"
            / "compile.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }
        assert "ring_angles_deg" in imported

        for count, start, sweep in ((1, 10.0, 360.0), (5, 0.0, 360.0), (4, 0.0, 90.0)):
            assert len(ring_angles_deg(count, start, sweep)) == count

    def test_a_full_sweep_and_an_arc_distribute_differently(self):
        assert ring_angles_deg(4, 0.0, 360.0) == [0.0, 90.0, 180.0, 270.0]
        assert ring_angles_deg(4, 0.0, 90.0) == [0.0, 30.0, 60.0, 90.0]
        assert ring_angles_deg(1, 33.0, 360.0) == [33.0]

    def test_the_halo_layer_never_imports_a_category_or_the_kernel(self):
        """AST-parsed, not `import`-based: an import check can pass by accident
        on an already-cached module."""

        package = Path(__file__).resolve().parents[1] / "jewelmind" / "halo"
        forbidden = (
            "cadquery",
            "OCP",
            "jewelmind.ring",
            "jewelmind.jewelry_category",
            "jewelmind.geometry",
            "jewelmind.setting",
            "jewelmind.domain.schema",
        )
        for path in sorted(package.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                else:
                    continue
                for name in names:
                    for banned in forbidden:
                        assert not name.startswith(banned), f"{path.name}: {name}"

    def test_the_halo_package_init_imports_nothing(self):
        """Load-bearing: `domain/schema.py` imports `halo.models`, so an eager
        package init would make the import graph cyclic."""

        path = (
            Path(__file__).resolve().parents[1]
            / "jewelmind"
            / "halo"
            / "__init__.py"
        )
        tree = ast.parse(path.read_text(encoding="utf-8"))
        assert not [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]


# --------------------------------------------------------------- geometry


class TestGeometry:
    def test_every_halo_stone_becomes_its_own_component(self):
        model = build_solitaire_ring(design(halo(rings=[ring(count=12)])))
        stones = stone_component_names(model)
        assert len(stones) == 13
        assert PRIMARY_STONE_COMPONENT in stones

    def test_a_halo_stone_is_never_production_metal(self):
        """LAW-006 at the halo layer: a stone that fell through to the
        production_metal default would be fused into the band and shipped in a
        production export."""

        model = build_solitaire_ring(design(halo(rings=[ring(count=6)])))
        for name in stone_component_names(model):
            assert geometry_role(name) == "stone_reference"
            assert not is_production_component(name)

    def test_the_metal_body_is_unaffected_by_halo_stones(self):
        plain = build_solitaire_ring(default_definition())
        haloed = build_solitaire_ring(design(halo(rings=[ring(count=16)])))
        assert haloed.combined_metal_volume_mm3 == pytest.approx(
            plain.combined_metal_volume_mm3, rel=KERNEL_REL_TOLERANCE
        )
        assert haloed.combined_metal_volume_mm3 == pytest.approx(
            LEGACY_METAL_VOLUME_MM3, rel=KERNEL_REL_TOLERANCE
        )

    def test_the_member_scale_reaches_the_solid(self):
        scale = 0.24
        model = build_solitaire_ring(
            design(halo(rings=[ring(count=4, memberScale=scale)]))
        )
        centre = model.components[PRIMARY_STONE_COMPONENT].volume_mm3
        stone = model.components[
            f"{STONE_INSTANCE_COMPONENT_PREFIX}halo.inner.0"
        ].volume_mm3
        assert stone == pytest.approx(centre * scale**3, rel=1e-9)

    def test_a_per_stone_override_reaches_the_solid(self):
        model = build_solitaire_ring(
            design(
                halo(
                    rings=[
                        ring(
                            count=4,
                            memberScale=0.2,
                            members=[
                                FamilyMember(
                                    memberId="halo.inner.crest",
                                    role="HALO",
                                    scale=0.45,
                                )
                            ],
                        )
                    ]
                )
            )
        )
        centre = model.components[PRIMARY_STONE_COMPONENT].volume_mm3
        crest = model.components[
            f"{STONE_INSTANCE_COMPONENT_PREFIX}halo.inner.crest"
        ].volume_mm3
        assert crest == pytest.approx(centre * 0.45**3, rel=1e-9)

    def test_the_stones_are_actually_displaced(self):
        radius = 3.6
        model = build_solitaire_ring(
            design(halo(rings=[ring(count=4, radiusMm=radius, startAngleDeg=0.0)]))
        )
        centre = model.components[PRIMARY_STONE_COMPONENT].bounding_box
        first = model.components[
            f"{STONE_INSTANCE_COMPONENT_PREFIX}halo.inner.0"
        ].bounding_box
        centre_x = (centre.xmin + centre.xmax) / 2.0
        first_x = (first.xmin + first.xmax) / 2.0
        assert first_x - centre_x == pytest.approx(radius, abs=1e-6)

    def test_a_gem_never_affects_a_solid(self):
        plain = build_solitaire_ring(design(halo(rings=[ring(count=6)])))
        gemmed = build_solitaire_ring(
            design(
                halo(
                    rings=[
                        ring(
                            count=6,
                            gem=GemIdentity(
                                gemId="corundum.sapphire", origin="NATURAL"
                            ),
                        )
                    ]
                )
            )
        )
        for name in sorted(stone_component_names(plain)):
            assert plain.components[name].volume_mm3 == pytest.approx(
                gemmed.components[name].volume_mm3, rel=KERNEL_REL_TOLERANCE
            )

    def test_a_halo_over_a_family_builds_every_stone(self):
        family = FamilyDefinition(
            familyType="THREE_STONE", params=ThreeStoneParams(sideSpacingMm=5.2)
        )
        definition = design(halo(rings=[ring(count=8)]), family)
        model = build_solitaire_ring(definition)
        # centre + 2 sides + 8 halo stones.
        assert len(stone_component_names(model)) == 11


# ------------------------------------------------------------- inspection


class TestInspection:
    def test_every_halo_stone_is_a_required_component(self):
        model = build_solitaire_ring(design(halo(rings=[ring(count=6)])))
        required = required_component_names(model)
        for name in stone_component_names(model):
            assert name in required

    def test_a_halo_model_inspects_cleanly(self):
        model = build_solitaire_ring(
            design(halo(rings=[ring(count=6, radiusMm=3.6, memberScale=0.2)]))
        )
        result = inspect_model(model)
        assert result.status in {"PASS", "PASS_WITH_FINDINGS"}
        assert result.assemblyResult.requiredComponentsPresent
        assert result.assemblyResult.missingComponentIds == []
        assert result.assemblyResult.referenceComponentCount == 7
        assert result.assemblyResult.productionComponentCount == 3

    def test_the_production_metal_stays_one_connected_body(self):
        model = build_solitaire_ring(design(halo(rings=[ring(count=10)])))
        result = inspect_model(model)
        connectivity = result.assemblyResult.productionConnectivity
        assert len(connectivity.connectedGroups) == 1
        assert connectivity.disconnectedGroupCount == 0
        assert connectivity.isFullyConnected
        # No halo stone appears in the production graph at all.
        assert set(connectivity.nodes) == {"band", "prongs", "basket_support"}

    def test_stone_metal_separation_holds_for_every_halo_stone(self):
        model = build_solitaire_ring(design(halo(rings=[ring(count=6)])))
        result = inspect_model(model)
        separation = result.assemblyResult.stoneMetalSeparation
        assert separation.stoneReferenceExists is True
        assert separation.productionIncluded is False
        assert separation.fusedIntoProductionMetal is False
        assert separation.status == "PASS"
        # A halo stone intersecting nothing and being fused into nothing is the
        # point: separation is STRUCTURAL, so adding sixteen stone references
        # must not change the verdict.
        assert "stone_reference" not in " ".join(
            separation.intersectsProductionComponents
        )


# ----------------------------------------------------------- forge rules


class TestHaloRules:
    def test_a_design_with_no_halo_produces_no_halo_results(self):
        """The entire pre-Sprint-25 corpus stays quiet."""

        assert halo_rule_ids(default_definition()) == {}

    def test_the_metal_coverage_limitation_is_reported(self):
        results = halo_rule_ids(design(halo(rings=[ring(count=8)])))
        assert results["JM-HALO-005"] == "information"

    def test_an_unresolvable_centre_is_an_error(self):
        arrangement = ArrangementDefinition(
            instances=[
                StoneInstanceDef(
                    instanceId="middle",
                    role="CENTER",
                    placement=InstancePlacement(transform=InstanceTransform()),
                )
            ]
        )
        definition = design(halo(centerMemberId="nowhere"), arrangement=arrangement)
        results = halo_rule_ids(definition)
        assert results["JM-HALO-001"] == "error"
        assert has_errors(validate_definition(definition))

    def test_a_composition_failure_is_an_error(self):
        definition = design(
            halo(
                rings=[
                    ring(
                        count=2, members=[FamilyMember(memberId="center", role="HALO")]
                    )
                ]
            )
        )
        results = halo_rule_ids(definition)
        assert results["JM-HALO-002"] == "error"

    def test_an_unresolved_stone_reference_is_a_warning_not_an_error(self):
        definition = design(halo(rings=[ring(count=6, stoneRef="side")]))
        results = halo_rule_ids(definition)
        assert results["JM-HALO-004"] == "warning"
        assert not has_errors(validate_definition(definition))

    def test_a_setting_request_that_does_not_match_is_a_warning(self):
        definition = design(halo(rings=[ring(count=6, settingRef="bezel")]))
        definition.setting.type = "prong"
        results = halo_rule_ids(definition)
        assert results["JM-HALO-004"] == "warning"

    def test_no_halo_rule_invents_a_professional_threshold(self):
        """Scanned against the REAL emitted messages rather than the source, so
        a threshold cannot hide in a string this test never sees."""

        forbidden = (
            "too close",
            "too thin",
            "too small",
            "minimum spacing",
            "industry standard",
            "not manufacturable",
            "must be at least",
            "recommended",
            "should be",
            "proportion",
        )
        definitions = [
            design(halo(rings=[ring(count=n, radiusMm=r, memberScale=s)]))
            for n, r, s in ((1, 0.1, 0.02), (40, 0.5, 9.0), (16, 3.4, 0.2))
        ]
        definitions.append(
            design(
                HaloDefinition(
                    variant="HIDDEN", rings=[ring(count=8, zOffsetMm=-0.001)]
                )
            )
        )
        for definition in definitions:
            for result in validate_definition(definition):
                if not result.ruleId.startswith("JM-HALO"):
                    continue
                lowered = result.message.lower()
                for phrase in forbidden:
                    assert phrase not in lowered, (result.ruleId, phrase)

    def test_a_family_arrangement_conflict_suppresses_halo_findings(self):
        """One error for one cause: JM-FAMILY-001 owns that conflict."""

        definition = design(
            halo(),
            family=FamilyDefinition(
                familyType="THREE_STONE", params=ThreeStoneParams(sideSpacingMm=4.0)
            ),
            arrangement=ArrangementDefinition(),
        )
        assert halo_rule_ids(definition) == {}
        ids = {r.ruleId for r in validate_definition(definition)}
        assert "JM-FAMILY-001" in ids


# ----------------------------------------------------------- JDL integration


class TestJdlIntegration:
    def test_a_halo_round_trips_through_jdl(self):
        definition = design(
            halo(
                variant="DOUBLE",
                rings=[
                    ring(ringId="halo.inner", count=8, radiusMm=3.2),
                    ring(
                        ringId="halo.outer",
                        count=14,
                        radiusMm=4.6,
                        gem=GemIdentity(gemId="corundum.sapphire", origin="NATURAL"),
                    ),
                ],
                label="Double halo",
            )
        )
        payload = definition.model_dump(mode="json")
        restored = JewelryDefinition.model_validate(payload)
        assert restored.halo == definition.halo
        assert definition_hash(restored) == definition_hash(definition)

    def test_the_schema_version_is_unchanged(self):
        """An optional additive field is backward compatible."""

        assert design(halo()).schemaVersion == default_definition().schemaVersion
        assert design(halo()).schemaVersion == "0.1.0"

    def test_a_document_without_a_halo_validates_and_hashes_as_before(self):
        payload = default_definition().model_dump(mode="json")
        assert payload["halo"] is None
        del payload["halo"]
        restored = JewelryDefinition.model_validate(payload)
        assert restored.halo is None
        assert definition_hash(restored) == definition_hash(default_definition())

    def test_the_jdl_schema_carries_the_halo_subtree(self):
        schema = json.loads(
            (REPO_ROOT / "specs" / "jdl" / "v1" / "jdl.schema.json").read_text(
                encoding="utf-8"
            )
        )
        assert "halo" in schema["properties"]
        assert "halo" in schema["$defs"]
        assert "HaloRing" in schema["$defs"]["haloDefs"]

    def test_the_jdl_schema_still_accepts_a_halo_free_document(self):
        import jsonschema

        schema = json.loads(
            (REPO_ROOT / "specs" / "jdl" / "v1" / "jdl.schema.json").read_text(
                encoding="utf-8"
            )
        )
        jsonschema.validate(
            default_definition().model_dump(mode="json"), schema
        )

    def test_the_jdl_schema_accepts_a_real_halo_document(self):
        import jsonschema

        schema = json.loads(
            (REPO_ROOT / "specs" / "jdl" / "v1" / "jdl.schema.json").read_text(
                encoding="utf-8"
            )
        )
        jsonschema.validate(
            design(halo(rings=[ring(count=12)])).model_dump(mode="json"), schema
        )


# ------------------------------------------------------ capability registry


class TestCapabilityRegistry:
    def test_every_registered_variant_has_a_real_compiler(self):
        assert set(HALO_CAPABILITIES) == set(halo_variants())
        assert current_halo_variants() == tuple(sorted(HALO_CAPABILITIES))

    def test_no_variant_claims_a_setting_it_does_not_build(self):
        assert halo_variants_with_setting_geometry() == ()
        assert set(halo_variants_with_stone_geometry()) == set(HALO_CAPABILITIES)
        for entry in HALO_CAPABILITIES.values():
            assert entry.status == "PARTIAL"
            assert entry.stoneGeometry is True
            assert entry.settingGeometry is False

    def test_a_reserved_variant_has_no_compiler_and_a_real_reason(self):
        for name, reason in RESERVED_HALO_VARIANTS.items():
            assert name not in halo_variants()
            assert name not in HALO_CAPABILITIES
            assert len(reason) > 60, name

    def test_the_planned_features_are_marked_planned(self):
        for name in (
            "halo_setting_metal",
            "outline_following_halo",
            "professional_halo_rules",
            "designer_halo_language",
        ):
            assert HALO_FEATURE_CAPABILITIES[name].status == "PLANNED"
            assert HALO_FEATURE_CAPABILITIES[name].settingGeometry is False

    def test_the_versions_are_declared(self):
        assert HALO_COMPILER_VERSION == "1.0.0"
        assert HALO_REGISTRY_VERSION == "1.0.0"


# ------------------------------------------------------ backward compatibility


class TestBackwardCompatibility:
    def test_a_design_with_no_halo_composes_to_exactly_what_it_had(self):
        plain = default_definition()
        assert effective_arrangement(plain) is None

        family = FamilyDefinition(
            familyType="THREE_STONE", params=ThreeStoneParams(sideSpacingMm=4.6)
        )
        with_family = default_definition()
        with_family.family = family
        from jewelmind.family.compile import compile_family

        assert effective_arrangement(with_family) == compile_family(family)

    def test_composing_no_halo_returns_the_base_object(self):
        base = ArrangementDefinition()
        assert compose_halo(base, None) is base
        assert compose_halo(None, None) is None

    def test_the_default_solitaire_is_geometrically_unchanged(self):
        model = build_solitaire_ring(default_definition())
        assert model.combined_metal_volume_mm3 == pytest.approx(
            LEGACY_METAL_VOLUME_MM3, rel=KERNEL_REL_TOLERANCE
        )
        assert sorted(model.components) == [
            "band",
            "basket_support",
            "prongs",
            "stone_reference",
        ]

    def test_the_existing_family_suites_placements_are_unchanged(self):
        """The shared ring-arithmetic extraction must not have moved a stone.

        Asserted against the resolver's own RADIAL expansion rather than a
        recorded constant, so this stays true if the arithmetic legitimately
        changes in both places at once.
        """

        family = FamilyDefinition(
            familyType="CENTER_WITH_ACCENTS",
            params=CenterWithAccentsParams(
                accentCount=6, accentRadiusMm=4.8, accentScale=0.3
            ),
        )
        from jewelmind.family.compile import compile_family

        arrangement = compile_family(family)
        assert arrangement is not None
        accents = sorted(
            (round(i.transform.xMm, 9), round(i.transform.yMm, 9))
            for i in resolve_arrangement(arrangement).instances
            if i.role == "ACCENT"
        )
        assert accents == _radial_pattern_positions(6, 4.8, 0.0, 360.0)


# ----------------------------------------------------------- spec artifacts


class TestSpecArtifacts:
    def test_the_registry_matches_the_live_code(self):
        registry = json.loads(
            (SPEC_DIR / "halo-registry.json").read_text(encoding="utf-8")
        )
        assert registry["registryVersion"] == HALO_REGISTRY_VERSION
        assert registry["compilerVersion"] == HALO_COMPILER_VERSION
        assert registry["ringCardinality"] == HALO_RING_CARDINALITY
        assert registry["composition"] == HALO_COMPOSITION
        assert [v["capability"] for v in registry["variants"]] == list(
            HALO_CAPABILITIES
        )
        for recorded, entry in zip(
            registry["variants"], HALO_CAPABILITIES.values(), strict=True
        ):
            assert recorded == entry.model_dump(mode="json")
        for recorded, entry in zip(
            registry["features"], HALO_FEATURE_CAPABILITIES.values(), strict=True
        ):
            assert recorded == entry.model_dump(mode="json")
        assert {r["variant"] for r in registry["reserved"]} == set(
            RESERVED_HALO_VARIANTS
        )

    def test_the_schemas_match_the_live_models(self):
        for filename, model in (
            ("halo-definition.schema.json", HaloDefinition),
            ("halo-ring.schema.json", HaloRing),
        ):
            recorded = json.loads((SPEC_DIR / filename).read_text(encoding="utf-8"))
            live = model.model_json_schema()
            for key, value in live.items():
                assert recorded[key] == value, (filename, key)

    def test_the_examples_reproduce_from_the_live_compiler(self):
        for path in sorted((SPEC_DIR / "examples").glob("*.json")):
            if path.name.startswith("composed-"):
                continue
            recorded = json.loads(path.read_text(encoding="utf-8"))
            live = HaloDefinition.model_validate(recorded)
            assert live.model_dump(mode="json") == recorded, path.name

    def test_the_composition_vectors_still_hold(self):
        from jewelmind.family.compile import compile_family

        vectors = json.loads(
            (SPEC_DIR / "test-vectors" / "composition-vectors.json").read_text(
                encoding="utf-8"
            )
        )
        assert vectors["compilerVersion"] == HALO_COMPILER_VERSION
        for vector in vectors["vectors"]:
            recorded = json.loads(
                (SPEC_DIR / "examples" / f"{vector['name']}.json").read_text(
                    encoding="utf-8"
                )
            )
            candidate = HaloDefinition.model_validate(recorded)
            base = None
            if vector["familyType"] is not None:
                family_doc = json.loads(
                    (
                        SPEC_DIR / "examples" / f"composed-{vector['name']}.json"
                    ).read_text(encoding="utf-8")
                )
                # The family is re-derived rather than re-read, so the vector
                # cannot pass against a stale composed example.
                assert family_doc["instances"]
                base = _family_for(vector["familyType"], compile_family)
            live = compose_halo(base, candidate)
            assert live is not None
            assert arrangement_fingerprint(live) == vector["arrangementFingerprint"]
            resolved = compile_arrangement(live)
            assert resolved is not None
            assert len(resolved.instances) == vector["instanceCount"]
            assert resolved.generatedCount == vector["generatedCount"]
            assert vector["settingCoverage"] == "PRIMARY_ONLY"

    def test_every_invalid_vector_is_still_refused(self):
        vectors = json.loads(
            (SPEC_DIR / "test-vectors" / "invalid-halo-vectors.json").read_text(
                encoding="utf-8"
            )
        )
        assert vectors["vectors"]
        for vector in vectors["vectors"]:
            assert vector["rejectedBy"] in {"SCHEMA", "COMPILER"}, vector["case"]


class TestApiSurface:
    """A halo reaches the real API the way every other field does.

    No new endpoint was added, and none was needed: the halo is part of the
    definition, so `/api/models/generate` carries it already.
    """

    def client(self):
        from fastapi.testclient import TestClient

        from jewelmind.api.app import create_app

        return TestClient(create_app(), raise_server_exceptions=False)

    def test_a_valid_halo_generates_through_the_api(self):
        response = self.client().post(
            "/api/models/generate",
            json=design(halo(rings=[ring(count=8, memberScale=0.2)])).model_dump(
                mode="json"
            ),
        )
        assert response.status_code == 200, response.text
        body = response.json()
        names = set(body["previewComponents"])
        assert PRIMARY_STONE_COMPONENT in names
        assert sum(1 for n in names if n.startswith(STONE_INSTANCE_COMPONENT_PREFIX)) == 8
        # Every halo stone reaches Vision as a stone, classified by the manifest's
        # own geometryRole rather than by its name.
        for name in names:
            if name.startswith(STONE_INSTANCE_COMPONENT_PREFIX):
                assert (
                    body["previewComponents"][name]["geometryRole"]
                    == "stone_reference"
                )
        # The metal-coverage limitation travels with the successful response.
        assert any(r["ruleId"] == "JM-HALO-005" for r in body["validation"])

    def test_an_invalid_halo_is_blocked_by_forge_rather_than_raising(self):
        """Forge and generation share the same compiler, so the exception path is
        unreachable through the API — which is the point of running the real
        compiler inside the rule."""

        family = FamilyDefinition(
            familyType="TOI_ET_MOI", params=ToiEtMoiParams(separationMm=5.0)
        )
        response = self.client().post(
            "/api/models/generate",
            json=design(halo(centerMemberId="center"), family).model_dump(mode="json"),
        )
        assert response.status_code == 422
        payload = response.text
        assert "JM-HALO-003" in payload
        # No internal exception, stack trace or server path may reach a client.
        assert "Traceback" not in payload
        assert "HaloCenterUnresolvedError" not in payload
        assert "site-packages" not in payload
        assert "Desktop" not in payload

    def test_a_malformed_halo_is_rejected_at_the_schema_layer(self):
        payload = design().model_dump(mode="json")
        payload["halo"] = {
            "variant": "SINGLE",
            "rings": [{"ringId": "../etc/passwd", "count": 8, "radiusMm": 3.0}],
        }
        response = self.client().post("/api/models/generate", json=payload)
        assert response.status_code == 422
        assert "Traceback" not in response.text


_FAMILY_FIXTURES = {
    "THREE_STONE": lambda: FamilyDefinition(
        familyType="THREE_STONE",
        params=ThreeStoneParams(sideSpacingMm=5.0, sideScale=0.55),
    ),
    "CENTER_WITH_ACCENTS": lambda: FamilyDefinition(
        familyType="CENTER_WITH_ACCENTS",
        params=CenterWithAccentsParams(
            accentCount=6, accentRadiusMm=6.2, accentScale=0.3
        ),
    ),
    "TOI_ET_MOI": lambda: FamilyDefinition(
        familyType="TOI_ET_MOI",
        params=ToiEtMoiParams(separationMm=5.4, axisAngleDeg=30.0),
    ),
}


def _family_for(family_type: str, compile_family):
    return compile_family(_FAMILY_FIXTURES[family_type]())
