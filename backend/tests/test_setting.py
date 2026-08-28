"""Setting System v1 (Sprint 19) tests — brief section 54.

Covers ROUND_4/6_PRONG_REGRESSION, NONROUND/OVAL_PRONG_PLACEMENT,
BEZEL_ROUND/OVAL_GENERATION, SETTING_REGISTRY, SETTING_CAPABILITY_MATRIX,
SETTING_INSPECTION, STONE_REFERENCE_SEPARATION, SETTING_PRODUCTION_ROLE,
SETTING_CONNECTIVITY, STEP_STL_SETTING_EXPORT, BEZEL_STEP_ROUNDTRIP,
JDL_SETTING_TYPE, FORGE_PRONG_RULE_SCOPE, UNSUPPORTED_SETTING_COMBINATION
and NO_FAKE_PROFESSIONAL_VALIDATION.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import pytest

from jewelmind.domain.defaults import default_definition
from jewelmind.domain.schema import JewelryDefinition, SettingSpec, StoneSpec
from jewelmind.exporters.step_exporter import export_step
from jewelmind.exporters.stl_exporter import export_stl
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring
from jewelmind.geometry.components.stone import build_stone_reference
from jewelmind.geometry.constants import prong_center_radius
from jewelmind.geometry.inspection.inspector import inspect_model
from jewelmind.geometry.roles import GEOMETRY_ROLE, PRODUCTION_ROLE, is_production_component
from jewelmind.geometry.setting_adapter import setting_definition_from_jdl
from jewelmind.geometry_quality.artifact_regression import step_roundtrip_check, stl_structure_check
from jewelmind.setting.capability import (
    RESERVED_SETTING_FAMILIES,
    SETTING_CAPABILITIES,
    compatibility_matrix,
    compatibility_status,
    get_setting_capability,
)
from jewelmind.setting.dispatch import generate_setting, setting_generators
from jewelmind.setting.errors import (
    SettingStoneCombinationUnsupportedError,
    SettingTypeUnsupportedError,
)
from jewelmind.setting.models import SettingDefinition
from jewelmind.setting.placement import (
    GIRDLE_INSET_PRONG_RADIUS_FRACTION,
    outline_cardinal_positions,
    prong_positions,
    radial_positions,
    resolve_strategy,
)
from jewelmind.setting.stone_interface import build_stone_setting_reference, girdle_outline_wire
from jewelmind.validation.engine import validate_definition

NON_ROUND_SHAPES = ["oval", "pear", "emerald", "cushion", "princess", "marquise"]

#: The pre-Sprint-19 recorded values for the default 6-prong round solitaire.
#:
#: `PRE_SPRINT19_PRONG_VOLUME` is asserted EXACTLY: a prong compound is built by
#: primitive construction only, and reproduces bit-for-bit on every platform CI
#: runs on. That exactness is the real backward-compatibility signal.
#:
#: `PRE_SPRINT19_COMBINED_METAL_VOLUME` is the volume of the BOOLEAN FUSE of
#: band + basket + prongs, and OCCT's boolean result carries genuine
#: platform-dependent floating-point drift: this value is 341.44334316909976 on
#: Windows and 341.44334316907685 on CI's Linux build — a relative difference of
#: ~6.7e-14, i.e. last-two-digits-of-a-double. Asserting exact equality on it
#: claimed a cross-platform guarantee the CAD kernel does not offer, and failed
#: on CI while passing locally. It is compared with `math.isclose` instead; see
#: `BOOLEAN_VOLUME_REL_TOL` for why that tolerance still catches a real
#: regression.
PRE_SPRINT19_COMBINED_METAL_VOLUME = 341.44334316909976
PRE_SPRINT19_PRONG_VOLUME = 29.650351464580467

#: Tolerance for comparing an OCCT boolean-fuse volume across platforms.
#:
#: This is a SOFTWARE COMPARISON TOLERANCE, never a manufacturing or jewelry
#: tolerance. It is ~4 orders of magnitude above the largest drift actually
#: observed (~6.7e-14) and ~6 orders of magnitude below any geometry change this
#: test could plausibly need to catch — a moved, resized, added or dropped
#: component shifts this volume by a fraction of a mm³, not by a rounding step.
BOOLEAN_VOLUME_REL_TOL = 1e-9


def _definition(shape="round", setting_type="prong", prong_count=6, length=8.0, width=6.0):
    d = default_definition()
    if shape != "round":
        d.stone = StoneSpec.model_validate(
            {"shape": shape, "length": length, "width": width, "depth": 4.0}
        )
    d.setting.type = setting_type
    d.setting.prongCount = prong_count
    return d


def _stone_ref(d: JewelryDefinition):
    return build_stone_setting_reference(d.stone, build_stone_reference(d))


def _setting_def(d: JewelryDefinition) -> SettingDefinition:
    return setting_definition_from_jdl(d, build_stone_reference(d))


class TestRoundProngBackwardCompatibility:
    """ROUND_4_PRONG_REGRESSION / ROUND_6_PRONG_REGRESSION (SETTING-GOV-017)."""

    def test_default_six_prong_round_reproduces_pre_sprint19_volumes(self):
        model = build_solitaire_ring(default_definition())
        # Exact: primitive-built prong geometry is bit-identical everywhere.
        assert model.components["prongs"].volume_mm3 == PRE_SPRINT19_PRONG_VOLUME
        # Tolerance: boolean-fuse volume drifts across platforms. See the
        # constants' docstring above.
        assert math.isclose(
            model.combined_metal_volume_mm3,
            PRE_SPRINT19_COMBINED_METAL_VOLUME,
            rel_tol=BOOLEAN_VOLUME_REL_TOL,
        ), f"{model.combined_metal_volume_mm3!r} != {PRE_SPRINT19_COMBINED_METAL_VOLUME!r}"

    @pytest.mark.parametrize("count", [4, 6])
    def test_round_prong_counts_generate_exactly_that_many_solids(self, count):
        model = build_solitaire_ring(_definition(prong_count=count))
        assert len(model.components["prongs"].shape.Solids()) == count
        assert model.components["prongs"].metadata["generatedCount"] == count

    def test_round_uses_radial_placement(self):
        d = default_definition()
        assert resolve_strategy(_stone_ref(d)) == "RADIAL"

    def test_radial_placement_matches_the_legacy_prong_center_radius_helper(self):
        """`geometry/constants.py::prong_center_radius()` is still used by the
        basket builder. The Setting System computes the same radius
        independently, so this asserts the two cannot drift apart."""

        d = default_definition()
        ref = _stone_ref(d)
        prong_r = d.setting.prongDiameter / 2
        positions = radial_positions(ref, 6, prong_r)
        setting_radius = math.hypot(*positions[0])
        assert setting_radius == pytest.approx(prong_center_radius(d), rel=1e-12)

    def test_prong_component_metadata_preserves_legacy_keys(self):
        meta = build_solitaire_ring(default_definition()).components["prongs"].metadata
        for key in ("requestedCount", "generatedCount", "prongRadiusMm", "centerRadiusMm", "positions"):
            assert key in meta


class TestNonRoundProngPlacement:
    """NONROUND_PRONG_PLACEMENT / OVAL_PRONG_PLACEMENT (SETTING-GOV-008)."""

    @pytest.mark.parametrize("shape", NON_ROUND_SHAPES)
    def test_non_round_shapes_use_outline_cardinal_placement(self, shape):
        assert resolve_strategy(_stone_ref(_definition(shape=shape))) == "OUTLINE_CARDINAL"

    @pytest.mark.parametrize("shape", NON_ROUND_SHAPES)
    def test_non_round_prong_setting_generates_the_requested_solids(self, shape):
        model = build_solitaire_ring(_definition(shape=shape))
        assert len(model.components["prongs"].shape.Solids()) == 6
        assert model.components["prongs"].volume_mm3 > 0

    def test_outline_placement_puts_prongs_closer_to_the_real_outline_than_radial(self):
        """The measurable justification for the change: under radial
        placement an oval's off-axis prongs float away from the stone."""

        d = _definition(shape="oval", length=8.0, width=6.0)
        ref = _stone_ref(d)
        prong_r = 0.55
        wire = girdle_outline_wire(ref)
        outline = [(wire.positionAt(k / 720).x, wire.positionAt(k / 720).y) for k in range(720)]

        def nearest(pos):
            return min(math.hypot(pos[0] - px, pos[1] - py) for px, py in outline)

        radial = radial_positions(ref, 6, prong_r)
        cardinal = outline_cardinal_positions(ref, 6, prong_r)

        # Index 1 is an off-axis prong (60 degrees) — where the two differ.
        assert nearest(radial[1]) > 0.5
        assert nearest(cardinal[1]) < 0.1

    def test_outline_placement_agrees_with_radial_on_the_x_axis_prong(self):
        """Both strategies must place the +X prong at the documented girdle
        inset, so the shape-aware strategy is a generalization rather than a
        different convention."""

        ref = _stone_ref(_definition(shape="oval"))
        prong_r = 0.55
        radial = radial_positions(ref, 6, prong_r)
        cardinal = outline_cardinal_positions(ref, 6, prong_r)
        assert cardinal[0] == pytest.approx(radial[0], abs=1e-6)

    def test_placement_honours_stone_orientation(self):
        """A rotated stone's prongs must rotate with it."""

        base = _definition(shape="oval", length=9.0, width=5.0)
        rotated = _definition(shape="oval", length=9.0, width=5.0)
        rotated.stone = rotated.stone.model_copy(update={"orientation": 90.0})

        p0 = outline_cardinal_positions(_stone_ref(base), 4, 0.55)
        p90 = outline_cardinal_positions(_stone_ref(rotated), 4, 0.55)
        # At 0 degrees the long axis is Y; at 90 it is X.
        assert max(abs(y) for _, y in p0) > max(abs(x) for x, _ in p0)
        assert max(abs(x) for x, _ in p90) > max(abs(y) for _, y in p90)

    def test_zero_prong_count_returns_no_positions(self):
        positions, _ = prong_positions(_stone_ref(_definition(shape="oval")), 0, 0.55)
        assert positions == []

    def test_girdle_inset_fraction_is_the_documented_construction_value(self):
        assert GIRDLE_INSET_PRONG_RADIUS_FRACTION == 0.3


class TestBezelGeneration:
    """BEZEL_ROUND_GENERATION / BEZEL_OVAL_GENERATION (brief section 16)."""

    @pytest.mark.parametrize("shape", ["round", "oval"])
    def test_required_bezel_shapes_generate_one_valid_solid(self, shape):
        model = build_solitaire_ring(_definition(shape=shape, setting_type="bezel"))
        bezel = model.components["bezel"]
        assert len(bezel.shape.Solids()) == 1
        assert bezel.shape.isValid()
        assert bezel.volume_mm3 > 0

    @pytest.mark.parametrize("shape", ["round", "oval", *NON_ROUND_SHAPES])
    def test_every_current_stone_shape_produces_a_valid_bezel(self, shape):
        model = build_solitaire_ring(_definition(shape=shape, setting_type="bezel"))
        bezel = model.components["bezel"]
        assert len(bezel.shape.Solids()) == 1
        assert bezel.shape.isValid()

    def test_bezel_derives_from_the_stone_outline(self):
        model = build_solitaire_ring(_definition(setting_type="bezel"))
        assert model.components["bezel"].metadata["outlineSource"] == "stone_girdle_outline"

    def test_bezel_outer_extent_exceeds_the_stone_by_the_wall_thickness(self):
        """Proves the wall is a real geometric offset of the stone, not an
        arbitrary ring: a round stone of diameter D must yield an outer
        extent of D + 2 * thickness."""

        d = _definition(setting_type="bezel")
        model = build_solitaire_ring(d)
        bb = model.components["bezel"].bounding_box
        expected = d.stone.diameter + 2 * d.setting.bezelWallThickness
        assert (bb.xmax - bb.xmin) == pytest.approx(expected, abs=0.01)

    def test_oval_bezel_is_elliptical_not_circular(self):
        d = _definition(shape="oval", setting_type="bezel", length=9.0, width=5.0)
        bb = build_solitaire_ring(d).components["bezel"].bounding_box
        assert (bb.ymax - bb.ymin) == pytest.approx(9.0 + 2 * 0.6, abs=0.05)
        assert (bb.xmax - bb.xmin) == pytest.approx(5.0 + 2 * 0.6, abs=0.05)

    def test_bezel_wall_is_centred_on_the_girdle_plane(self):
        d = _definition(setting_type="bezel")
        model = build_solitaire_ring(d)
        meta = model.components["bezel"].metadata
        half = d.setting.bezelWallHeight / 2
        assert meta["wallBottomZMm"] == pytest.approx(meta["girdlePlaneZMm"] - half)
        assert meta["wallTopZMm"] == pytest.approx(meta["girdlePlaneZMm"] + half)

    def test_only_the_oval_needs_step_safety_repair(self):
        """The repair trigger is the real offset curve TYPE, not a shape
        name — so exactly the shape whose outline is an analytic ellipse
        gets repaired."""

        repaired = {}
        for shape in ["round", "oval", *NON_ROUND_SHAPES]:
            model = build_solitaire_ring(_definition(shape=shape, setting_type="bezel"))
            repaired[shape] = model.components["bezel"].metadata["stepSafetyRepairApplied"]
        assert repaired["oval"] is True
        assert all(v is False for k, v in repaired.items() if k != "oval")

    def test_step_safety_repair_is_reported_as_an_observable_fallback_event(self):
        """SETTING-GOV-013: a fallback must never be silent."""

        d = _definition(shape="oval", setting_type="bezel")
        _components, result = generate_setting(_setting_def(d))
        assert len(result.fallbackEvents) == 1
        assert result.fallbackEvents[0].stage == "bezel_outline_offset"
        assert "OFFSET" in result.fallbackEvents[0].reason

    def test_bezel_wall_thickness_scales_the_wall(self):
        thin = _definition(setting_type="bezel")
        thin.setting.bezelWallThickness = 0.4
        thick = _definition(setting_type="bezel")
        thick.setting.bezelWallThickness = 1.2
        v_thin = build_solitaire_ring(thin).components["bezel"].volume_mm3
        v_thick = build_solitaire_ring(thick).components["bezel"].volume_mm3
        assert v_thick > v_thin


class TestSettingRegistry:
    """SETTING_REGISTRY / SETTING_CAPABILITY_MATRIX."""

    def test_only_implemented_families_are_registered(self):
        assert set(setting_generators()) == {"prong", "bezel"}

    def test_every_registered_generator_has_a_capability_entry(self):
        assert set(setting_generators()) == set(SETTING_CAPABILITIES)

    def test_reserved_families_have_no_generator(self):
        for family in RESERVED_SETTING_FAMILIES:
            assert family not in setting_generators()
            assert family not in SETTING_CAPABILITIES

    def test_every_capability_is_generatable_and_inspectable_and_category_neutral(self):
        for capability in SETTING_CAPABILITIES.values():
            assert capability.status == "CURRENT"
            assert capability.generatable is True
            assert capability.inspectable is True
            assert capability.categoryNeutral is True

    def test_seats_bearings_and_cutters_are_honestly_planned(self):
        """Brief section 24: no production seat geometry exists, so claiming
        anything other than PLANNED would be false."""

        for capability in SETTING_CAPABILITIES.values():
            assert capability.seatSupport == "PLANNED"
            assert capability.bearingSupport == "PLANNED"
            assert capability.cutterSupport == "PLANNED"

    def test_compatibility_matrix_covers_every_family_and_shape(self):
        rows = compatibility_matrix()
        assert len(rows) == 2 * 7
        assert {r["settingType"] for r in rows} == {"prong", "bezel"}

    def test_only_round_is_supported_for_prong(self):
        assert compatibility_status("prong", "round") == "SUPPORTED_SOFTWARE"
        for shape in NON_ROUND_SHAPES:
            assert compatibility_status("prong", shape) == "EXPERIMENTAL"

    def test_round_and_oval_are_supported_for_bezel(self):
        assert compatibility_status("bezel", "round") == "SUPPORTED_SOFTWARE"
        assert compatibility_status("bezel", "oval") == "SUPPORTED_SOFTWARE"
        for shape in ["pear", "emerald", "cushion", "princess", "marquise"]:
            assert compatibility_status("bezel", shape) == "EXPERIMENTAL"

    def test_unknown_family_or_shape_reports_unsupported(self):
        assert compatibility_status("channel", "round") == "UNSUPPORTED"
        assert compatibility_status("prong", "asscher") == "UNSUPPORTED"
        assert get_setting_capability("channel") is None


class TestNoFakeProfessionalValidation:
    """NO_FAKE_PROFESSIONAL_VALIDATION (SETTING-GOV-007; brief section 56)."""

    def test_no_setting_family_claims_professional_validation(self):
        for capability in SETTING_CAPABILITIES.values():
            assert capability.professionalValidationStatus == "NOT_REVIEWED"

    def test_compatibility_matrix_never_claims_validation(self):
        for row in compatibility_matrix():
            assert row["professionalValidation"] == "NOT_REVIEWED"

    def test_generatable_does_not_imply_validated(self):
        """The two axes must be independent: every family is generatable AND
        unreviewed at the same time."""

        for capability in SETTING_CAPABILITIES.values():
            assert capability.generatable is True
            assert capability.professionalValidationStatus != "VALIDATED"


class TestUnsupportedSettingCombination:
    """UNSUPPORTED_SETTING_COMBINATION (SETTING-GOV-012/013)."""

    def test_unregistered_setting_type_raises_explicitly(self):
        d = _definition(setting_type="bezel")
        setting_def = _setting_def(d)
        broken = setting_def.model_copy(update={"settingType": "channel"})
        with pytest.raises(SettingTypeUnsupportedError):
            generate_setting(broken)

    def test_unsupported_stone_shape_raises_rather_than_substituting(self):
        d = _definition(setting_type="bezel")
        setting_def = _setting_def(d)
        broken = setting_def.model_copy(
            update={"stone": setting_def.stone.model_copy(update={"shape": "asscher"})}
        )
        with pytest.raises(SettingStoneCombinationUnsupportedError):
            generate_setting(broken)

    def test_error_messages_never_leak_a_kernel_stack_trace(self):
        d = _definition(setting_type="bezel")
        broken = _setting_def(d).model_copy(update={"settingType": "channel"})
        with pytest.raises(SettingTypeUnsupportedError) as exc:
            generate_setting(broken)
        assert "Traceback" not in str(exc.value)
        assert "OCP" not in str(exc.value)


class TestSettingProductionRoleAndStoneSeparation:
    """SETTING_PRODUCTION_ROLE / STONE_REFERENCE_SEPARATION."""

    @pytest.mark.parametrize("setting_type", ["prong", "bezel"])
    def test_setting_component_is_production_metal(self, setting_type):
        build_solitaire_ring(_definition(setting_type=setting_type))
        name = "prongs" if setting_type == "prong" else "bezel"
        assert GEOMETRY_ROLE[name] == "production_metal"
        assert PRODUCTION_ROLE[name] == "included_by_default"
        assert is_production_component(name)

    def test_stone_reference_is_never_production_metal(self):
        assert GEOMETRY_ROLE["stone_reference"] == "stone_reference"
        assert PRODUCTION_ROLE["stone_reference"] == "excluded_by_default"
        assert not is_production_component("stone_reference")

    @pytest.mark.parametrize("setting_type", ["prong", "bezel"])
    def test_stone_is_never_fused_into_production_metal(self, setting_type):
        model = build_solitaire_ring(_definition(setting_type=setting_type))
        report = inspect_model(model)
        assert report.assemblyResult.stoneMetalSeparation.fusedIntoProductionMetal is False

    @pytest.mark.parametrize("setting_type", ["prong", "bezel"])
    def test_step_export_excludes_the_stone_by_default(self, setting_type):
        model = build_solitaire_ring(_definition(setting_type=setting_type))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.step"
            export_step(model, path, include_stone=False)
            assert path.stat().st_size > 0


class TestSettingConnectivity:
    """SETTING_CONNECTIVITY (brief section 27)."""

    @pytest.mark.parametrize("setting_type", ["prong", "bezel"])
    @pytest.mark.parametrize("shape", ["round", "oval"])
    def test_setting_is_connected_to_the_ring_head(self, setting_type, shape):
        model = build_solitaire_ring(_definition(shape=shape, setting_type=setting_type))
        report = inspect_model(model)
        assert report.assemblyResult.productionConnectivity.isFullyConnected is True

    @pytest.mark.parametrize("setting_type", ["prong", "bezel"])
    def test_metal_fuses_into_a_single_solid(self, setting_type):
        model = build_solitaire_ring(_definition(setting_type=setting_type))
        assert len(model.combined_metal.Solids()) == 1


class TestSettingInspection:
    """SETTING_INSPECTION (brief section 25)."""

    def _facts(self, model):
        return {
            f.factType: f.value
            for f in inspect_model(model).geometricFacts
            if f.factId.startswith("setting.")
        }

    def test_prong_facts_are_reported(self):
        facts = self._facts(build_solitaire_ring(_definition(prong_count=4)))
        assert facts["SETTING_TYPE"] == "prong"
        assert facts["SETTING_REQUESTED_PRONG_COUNT"] == 4
        assert facts["SETTING_GENERATED_PRONG_COUNT"] == 4
        assert facts["SETTING_PLACEMENT_STRATEGY"] == "RADIAL"
        assert facts["SETTING_COMPATIBILITY_STATUS"] == "SUPPORTED_SOFTWARE"

    def test_bezel_facts_are_reported(self):
        facts = self._facts(build_solitaire_ring(_definition(setting_type="bezel")))
        assert facts["SETTING_TYPE"] == "bezel"
        assert facts["BEZEL_OUTLINE_SOURCE"] == "stone_girdle_outline"
        assert facts["BEZEL_WALL_CONTINUOUS"] is True

    def test_prong_only_facts_are_absent_for_a_bezel(self):
        facts = self._facts(build_solitaire_ring(_definition(setting_type="bezel")))
        assert "SETTING_REQUESTED_PRONG_COUNT" not in facts
        assert "SETTING_PLACEMENT_STRATEGY" not in facts

    def test_bezel_only_facts_are_absent_for_a_prong_setting(self):
        facts = self._facts(build_solitaire_ring(default_definition()))
        assert "BEZEL_OUTLINE_SOURCE" not in facts
        assert "BEZEL_WALL_CONTINUOUS" not in facts

    def test_non_round_placement_strategy_is_reported_honestly(self):
        facts = self._facts(build_solitaire_ring(_definition(shape="oval")))
        assert facts["SETTING_PLACEMENT_STRATEGY"] == "OUTLINE_CARDINAL"
        assert facts["SETTING_COMPATIBILITY_STATUS"] == "EXPERIMENTAL"

    def test_prong_count_is_not_applicable_rather_than_failed_for_a_bezel(self):
        """Brief section 26: a bezel having no prongs is not a defect."""

        report = inspect_model(build_solitaire_ring(_definition(setting_type="bezel")))
        assert report.assemblyResult.prongCount.status == "NOT_APPLICABLE"
        assert report.status == "PASS"

    @pytest.mark.parametrize("setting_type", ["prong", "bezel"])
    def test_required_components_are_present_for_both_families(self, setting_type):
        report = inspect_model(build_solitaire_ring(_definition(setting_type=setting_type)))
        assert report.assemblyResult.requiredComponentsPresent is True
        assert report.assemblyResult.missingComponentIds == []


class TestSettingExports:
    """STEP_STL_SETTING_EXPORT / BEZEL_STEP_ROUNDTRIP."""

    @pytest.mark.parametrize("shape", ["round", "oval"])
    def test_bezel_step_roundtrip_has_no_regressions(self, shape):
        model = build_solitaire_ring(_definition(shape=shape, setting_type="bezel"))
        assert step_roundtrip_check(model) == []

    @pytest.mark.parametrize("shape", ["round", "oval"])
    def test_bezel_stl_structure_has_no_regressions(self, shape):
        d = _definition(shape=shape, setting_type="bezel")
        assert stl_structure_check(build_solitaire_ring(d), d) == []

    def test_non_round_prong_step_roundtrip_has_no_regressions(self):
        model = build_solitaire_ring(_definition(shape="oval"))
        assert step_roundtrip_check(model) == []

    def test_bezel_stl_export_is_non_empty(self):
        d = _definition(setting_type="bezel")
        model = build_solitaire_ring(d)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.stl"
            export_stl(model, d, path, include_stone=False)
            assert path.stat().st_size > 0


class TestJdlSettingType:
    """JDL_SETTING_TYPE — the additive MINOR schema change."""

    def test_bezel_is_an_accepted_setting_type(self):
        assert SettingSpec.model_validate({"type": "bezel"}).type == "bezel"

    def test_prong_remains_the_default(self):
        assert SettingSpec().type == "prong"

    def test_bezel_fields_have_preliminary_software_defaults(self):
        spec = SettingSpec()
        assert spec.bezelWallThickness == 0.6
        assert spec.bezelWallHeight == 2.5

    def test_a_pre_sprint19_document_without_bezel_fields_still_validates(self):
        """Backward compatibility: the two new fields are optional."""

        spec = SettingSpec.model_validate(
            {"type": "prong", "prongCount": 6, "prongDiameter": 1.1, "prongHeight": 4.8, "basketHeight": 3.5}
        )
        assert spec.type == "prong"
        assert spec.bezelWallThickness == 0.6

    def test_unknown_setting_type_is_rejected(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SettingSpec.model_validate({"type": "channel"})

    def test_prong_fields_are_not_required_for_a_bezel(self):
        spec = SettingSpec.model_validate({"type": "bezel", "bezelWallThickness": 0.5})
        assert spec.type == "bezel"


class TestForgeProngRuleScope:
    """FORGE_PRONG_RULE_SCOPE (brief section 32)."""

    def test_prong_rules_never_fire_for_a_bezel(self):
        d = _definition(setting_type="bezel")
        d.setting.prongCount = 99
        d.setting.prongDiameter = 0.1
        d.setting.prongHeight = 0.1
        fired = [r.ruleId for r in validate_definition(d) if r.ruleId.startswith("JM-PRONG")]
        assert fired == []

    def test_prong_rules_still_fire_for_a_prong_setting(self):
        d = _definition(prong_count=99)
        fired = [r.ruleId for r in validate_definition(d) if r.ruleId == "JM-PRONG-001"]
        assert fired == ["JM-PRONG-001"]

    def test_bezel_rules_never_fire_for_a_prong_setting(self):
        d = default_definition()
        d.setting.bezelWallThickness = -5.0
        fired = [r.ruleId for r in validate_definition(d) if r.ruleId in ("JM-SETTING-003", "JM-SETTING-004")]
        assert fired == []

    @pytest.mark.parametrize(
        "field,rule",
        [("bezelWallThickness", "JM-SETTING-003"), ("bezelWallHeight", "JM-SETTING-004")],
    )
    def test_bezel_constructibility_rules_fire_for_a_bezel(self, field, rule):
        d = _definition(setting_type="bezel")
        setattr(d.setting, field, 0.0)
        fired = [r.ruleId for r in validate_definition(d) if r.ruleId == rule]
        assert fired == [rule]

    def test_a_valid_bezel_produces_no_errors(self):
        errors = [r for r in validate_definition(_definition(setting_type="bezel")) if r.severity == "error"]
        assert errors == []

    def test_no_minimum_bezel_wall_dimension_is_asserted(self):
        """SETTING-GOV-010: a minimum wall thickness would be a professional
        manufacturing threshold, and no sourced value exists."""

        d = _definition(setting_type="bezel")
        d.setting.bezelWallThickness = 0.01
        errors = [r for r in validate_definition(d) if r.severity == "error"]
        assert errors == []


class TestSettingAttachmentInterface:
    """The generic attachment contract (brief section 21)."""

    def test_attachment_interface_is_supplied_by_the_ring_side(self):
        d = default_definition()
        setting_def = _setting_def(d)
        attachment = setting_def.attachment
        assert attachment.attachmentPlaneZMm > 0
        assert attachment.embedMm > 0
        assert attachment.supportHeightMm == d.setting.basketHeight

    @pytest.mark.parametrize("setting_type", ["prong", "bezel"])
    def test_result_reports_the_attachment_interface_it_used(self, setting_type):
        _components, result = generate_setting(_setting_def(_definition(setting_type=setting_type)))
        assert len(result.attachmentInterfaces) == 1

    def test_attachment_plane_is_independent_of_the_setting_family(self):
        prong_attachment = _setting_def(_definition()).attachment
        bezel_attachment = _setting_def(_definition(setting_type="bezel")).attachment
        assert prong_attachment == bezel_attachment


class TestSettingGeometryResult:
    @pytest.mark.parametrize("setting_type,component", [("prong", "prongs"), ("bezel", "bezel")])
    def test_result_reports_real_components_and_roles(self, setting_type, component):
        _components, result = generate_setting(_setting_def(_definition(setting_type=setting_type)))
        assert result.generatedComponents == [component]
        assert result.productionComponents == [component]
        assert result.referenceComponents == []
        assert result.geometryFacts[0].componentId == component
        assert result.geometryFacts[0].solidCount >= 1

    def test_model_carries_the_setting_result(self):
        model = build_solitaire_ring(default_definition())
        assert model.setting_result is not None
        assert model.setting_result.settingType == "prong"
