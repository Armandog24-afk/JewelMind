"""RING_DEFINITION_ADAPTER_TEST, RING_SIZING_MAPPING_TEST,
SHANK_MAPPING_TEST, HEAD_MAPPING_TEST, STONE_ARRANGEMENT_MAPPING_TEST,
SETTING_ATTACHMENT_MAPPING_TEST, SOLITAIRE_FAMILY_DISPATCH_TEST,
UNSUPPORTED_RING_FAMILY_TEST, BACKWARD_COMPATIBLE_JDL_TEST,
STONE_REFERENCE_REGRESSION_TEST, FORGE_SCOPE_TEST.
"""

from __future__ import annotations

import pytest

from jewelmind.domain.defaults import default_definition
from jewelmind.geometry.inspection.inspector import inspect_model
from jewelmind.jewelry_category.dispatch import generate_jewelry
from jewelmind.jewelry_category.errors import RingFamilyUnsupportedError
from jewelmind.jewelry_category.forge_scope import is_ring_specific, is_shared_scope, rule_scope
from jewelmind.ring.adapter import ring_definition_from_jdl
from jewelmind.ring.families import RING_FAMILY_GENERATORS, generate_ring
from jewelmind.validation import rules as R


class TestRingDefinitionAdapter:
    def test_default_solitaire_maps_cleanly_into_ring_definition(self):
        ring_definition = ring_definition_from_jdl(default_definition())
        assert ring_definition.family == "solitaire"

    def test_ring_sizing_mapping(self):
        d = default_definition()
        ring_definition = ring_definition_from_jdl(d)
        assert ring_definition.sizing.sizeSystem == d.ring.sizeSystem
        assert ring_definition.sizing.size == d.ring.size
        assert ring_definition.sizing.innerDiameter == d.ring.innerDiameter

    def test_shank_mapping(self):
        d = default_definition()
        d.band.profile = "flat"
        d.band.width = 3.2
        d.band.thickness = 2.1
        ring_definition = ring_definition_from_jdl(d)
        assert ring_definition.shank.profile == "flat"
        assert ring_definition.shank.widthMm == 3.2
        assert ring_definition.shank.thicknessMm == 2.1

    def test_head_mapping(self):
        d = default_definition()
        d.setting.basketHeight = 4.2
        ring_definition = ring_definition_from_jdl(d)
        assert ring_definition.head.basketHeightMm == 4.2
        # RingHead owns basket height only — prong fields belong to
        # SettingAttachmentDefinition, not RingHeadDefinition.
        assert not hasattr(ring_definition.head, "prongCount")

    def test_stone_arrangement_mapping(self):
        d = default_definition()
        d.stone.diameter = 7.0
        d.stone.depth = 4.5
        ring_definition = ring_definition_from_jdl(d)
        assert ring_definition.stoneArrangement.arrangement == "SINGLE_CENTER"
        assert ring_definition.stoneArrangement.stone.diameter == 7.0
        assert ring_definition.stoneArrangement.stone.depth == 4.5

    def test_setting_attachment_mapping(self):
        d = default_definition()
        d.setting.prongCount = 4
        d.setting.prongDiameter = 1.3
        d.setting.prongHeight = 5.5
        ring_definition = ring_definition_from_jdl(d)
        assert ring_definition.setting.settingType == "prong"
        assert ring_definition.setting.prongCount == 4
        assert ring_definition.setting.prongDiameterMm == 1.3
        assert ring_definition.setting.prongHeightMm == 5.5

    def test_adapter_is_pure_and_deterministic(self):
        d = default_definition()
        a = ring_definition_from_jdl(d)
        b = ring_definition_from_jdl(d)
        assert a.model_dump() == b.model_dump()


class TestSolitaireFamilyDispatch:
    def test_solitaire_is_the_only_registered_family(self):
        assert set(RING_FAMILY_GENERATORS) == {"solitaire"}

    def test_generate_ring_dispatches_to_the_real_solitaire_builder(self):
        model = generate_ring(default_definition())
        assert model.components  # a real GeneratedModel, not a mock

    def test_unsupported_ring_family_raises_a_clean_error(self):
        # "three_stone" is a real, recognized RingFamilyId (models.py) with
        # deliberately no generator (families.py) — bypass StrictModel
        # validation to simulate a future JDL that allowed it, and confirm
        # the dispatch boundary (not a schema error) is what rejects it.
        d = default_definition()
        object.__setattr__(d.jewelry, "style", "three_stone")
        with pytest.raises(RingFamilyUnsupportedError):
            generate_ring(d)

    def test_reserved_planned_families_have_no_generator_yet(self):
        from jewelmind.ring.families import RESERVED_PLANNED_RING_FAMILIES

        for family in RESERVED_PLANNED_RING_FAMILIES:
            assert family not in RING_FAMILY_GENERATORS


class TestBackwardCompatibleJdl:
    """The refactor must not change what a real, pre-existing JDL
    definition accepts or produces."""

    def test_default_definition_still_generates_through_the_new_dispatch(self):
        model = generate_jewelry(default_definition())
        assert isinstance(model.definition_hash, str) and model.definition_hash

    def test_generate_jewelry_and_generate_ring_produce_identical_geometry(self):
        d = default_definition()
        via_category_dispatch = generate_jewelry(d)
        via_ring_dispatch = generate_ring(d)
        assert via_category_dispatch.definition_hash == via_ring_dispatch.definition_hash
        assert via_category_dispatch.combined_metal_volume_mm3 == via_ring_dispatch.combined_metal_volume_mm3


class TestStoneReferenceRegression:
    """Ring Architecture must not disturb LAW-006 (stone/metal
    separation) — verified against real inspection output through the
    new dispatch path."""

    def test_stone_reference_remains_separate_from_production_metal(self):
        model = generate_jewelry(default_definition())
        report = inspect_model(model)
        assert report.assemblyResult.stoneMetalSeparation.fusedIntoProductionMetal is False


class TestForgeScope:
    def test_ring_sizing_rules_are_ring_specific(self):
        assert rule_scope(R.RING_INNER_DIAMETER_RANGE) == "ring_sizing"
        assert rule_scope(R.RING_SIZE_RANGE) == "ring_sizing"
        assert is_ring_specific(R.RING_INNER_DIAMETER_RANGE)

    def test_shank_rules_are_ring_specific(self):
        assert rule_scope(R.BAND_WIDTH_MIN) == "ring_shank"
        assert is_ring_specific(R.BAND_WIDTH_MIN)

    def test_head_rules_are_ring_specific(self):
        assert rule_scope(R.SETTING_BASKET_HEIGHT_POSITIVE) == "ring_head"
        assert is_ring_specific(R.SETTING_BASKET_HEIGHT_POSITIVE)

    def test_stone_and_prong_rules_are_shared_scope(self):
        assert rule_scope(R.STONE_DIAMETER_RANGE) == "shared_stone"
        assert rule_scope(R.PRONG_COUNT) == "shared_setting"
        assert is_shared_scope(R.STONE_DIAMETER_RANGE)
        assert is_shared_scope(R.PRONG_COUNT)

    def test_manufacturing_and_geometry_rules_are_shared_scope(self):
        assert rule_scope(R.MANUFACTURING_MIN_FEATURE) == "shared_manufacturing"
        assert rule_scope(R.GEOMETRY_OUTER_BAND_POSITIVE) == "engineering"
        assert is_shared_scope(R.MANUFACTURING_MIN_FEATURE)
        assert is_shared_scope(R.GEOMETRY_OUTER_BAND_POSITIVE)

    def test_an_unrecognized_rule_id_prefix_is_unknown_not_a_crash(self):
        assert rule_scope("JM-NOTAREALPREFIX-999") == "unknown"
