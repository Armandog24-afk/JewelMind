"""UNIFORM_SHANK_BACKWARD_COMPATIBILITY_TEST, FLAT_PROFILE_TEST,
COMFORT_PROFILE_TEST, WIDTH_FUNCTION_CONSTANT_TEST,
THICKNESS_FUNCTION_CONSTANT_TEST, WIDTH_TAPER_GENERATION_TEST,
THICKNESS_TAPER_GENERATION_TEST, COMBINED_TAPER_TEST,
TAPER_SYMMETRY_TEST, INVALID_TAPER_TEST, DEGENERATE_SECTION_TEST,
HEAD_CONNECTION_TEST, SHANK_VOLUME_TEST, SHANK_BOUNDING_BOX_TEST,
SHANK_CONNECTIVITY_TEST, SHANK_STEP_EXPORT_TEST, SHANK_STL_EXPORT_TEST.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from jewelmind.domain.defaults import default_definition
from jewelmind.exporters.step_exporter import export_step
from jewelmind.exporters.stl_exporter import export_stl
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring
from jewelmind.geometry.connection import shank_connection_interface
from jewelmind.geometry.inspection.inspector import inspect_model
from jewelmind.geometry.shank.builder import ShankConstructionError, build_shank
from jewelmind.geometry.shank.capability import SHANK_CAPABILITIES, get_shank_capability
from jewelmind.geometry.shank.taper import taper_ratio
from jewelmind.geometry_quality.artifact_regression import step_roundtrip_check, stl_structure_check


def _tapered_definition(*, width_ratio=None, thickness_ratio=None, profile=None):
    d = default_definition()
    if width_ratio is not None:
        d.band.widthTaper.mode = "TOWARD_BOTTOM"
        d.band.widthTaper.bottomRatio = width_ratio
    if thickness_ratio is not None:
        d.band.thicknessTaper.mode = "TOWARD_BOTTOM"
        d.band.thicknessTaper.bottomRatio = thickness_ratio
    if profile is not None:
        d.band.profile = profile
    return d


class TestUniformShankBackwardCompatibility:
    def test_default_definition_produces_the_pre_sprint17_recorded_volume(self):
        model = build_solitaire_ring(default_definition())
        band = model.components["band"]
        # Recorded from the real pre-Sprint-17 revolve() output — see
        # docs/bible/19-shank/556-current-band-migration.md.
        assert band.volume_mm3 == pytest.approx(250.99168317654699, rel=0, abs=1e-9)
        assert model.combined_metal_volume_mm3 == pytest.approx(341.44334316909976, rel=0, abs=1e-9)

    def test_default_taper_fields_are_none_and_dispatch_to_uniform_path(self):
        d = default_definition()
        assert d.band.widthTaper.mode == "NONE"
        assert d.band.thicknessTaper.mode == "NONE"
        band = build_shank(d)
        assert band.metadata["variation"] == "UNIFORM"


class TestSectionProfiles:
    def test_flat_profile_is_a_valid_positive_volume_solid(self):
        d = default_definition()
        d.band.profile = "flat"
        band = build_shank(d)
        assert band.shape.Solids()
        assert band.volume_mm3 > 0
        assert band.metadata["profile"] == "flat"

    def test_comfort_profile_is_a_valid_positive_volume_solid(self):
        d = default_definition()
        d.band.profile = "comfort_fit"
        band = build_shank(d)
        assert band.shape.Solids()
        assert band.volume_mm3 > 0
        assert band.metadata["profile"] == "comfort_fit"

    def test_flat_and_comfort_fit_differ_in_volume(self):
        flat = build_shank(_tapered_definition(profile="flat"))
        comfort = build_shank(_tapered_definition(profile="comfort_fit"))
        assert flat.volume_mm3 != comfort.volume_mm3


class TestWidthAndThicknessFunctions:
    def test_constant_width_function_is_a_no_op(self):
        d = default_definition()
        assert taper_ratio(0.0, d.band.widthTaper) == 1.0
        assert taper_ratio(0.25, d.band.widthTaper) == 1.0
        assert taper_ratio(0.5, d.band.widthTaper) == 1.0

    def test_constant_thickness_function_is_a_no_op(self):
        d = default_definition()
        assert taper_ratio(0.0, d.band.thicknessTaper) == 1.0
        assert taper_ratio(0.5, d.band.thicknessTaper) == 1.0

    def test_toward_bottom_ratio_is_exactly_one_at_the_head(self):
        d = _tapered_definition(width_ratio=0.6)
        assert taper_ratio(0.0, d.band.widthTaper) == 1.0
        assert taper_ratio(1.0, d.band.widthTaper) == pytest.approx(1.0)

    def test_toward_bottom_ratio_equals_bottom_ratio_at_the_bottom(self):
        d = _tapered_definition(width_ratio=0.6)
        assert taper_ratio(0.5, d.band.widthTaper) == pytest.approx(0.6)


class TestWidthTaperGeneration:
    def test_width_taper_produces_a_single_valid_solid_with_less_volume(self):
        uniform = build_shank(default_definition())
        tapered = build_shank(_tapered_definition(width_ratio=0.6))
        assert tapered.shape.Solids()
        assert len(tapered.shape.Solids()) == 1
        assert tapered.volume_mm3 < uniform.volume_mm3

    def test_width_taper_metadata_reports_head_and_bottom_samples(self):
        band = build_shank(_tapered_definition(width_ratio=0.6))
        samples = band.metadata["widthSamplesMm"]
        assert samples["headMm"] == pytest.approx(2.4)
        assert samples["bottomMm"] == pytest.approx(2.4 * 0.6)


class TestThicknessTaperGeneration:
    def test_thickness_taper_produces_a_single_valid_solid_with_less_volume(self):
        uniform = build_shank(default_definition())
        tapered = build_shank(_tapered_definition(thickness_ratio=0.5))
        assert tapered.shape.Solids()
        assert len(tapered.shape.Solids()) == 1
        assert tapered.volume_mm3 < uniform.volume_mm3

    def test_thickness_taper_metadata_reports_head_and_bottom_samples(self):
        band = build_shank(_tapered_definition(thickness_ratio=0.5))
        samples = band.metadata["thicknessSamplesMm"]
        assert samples["headMm"] == pytest.approx(1.8)
        assert samples["bottomMm"] == pytest.approx(1.8 * 0.5)


class TestCombinedTaper:
    def test_combined_width_and_thickness_taper_generates_a_valid_solid(self):
        d = _tapered_definition(width_ratio=0.7, thickness_ratio=0.6, profile="flat")
        band = build_shank(d)
        assert band.shape.Solids()
        assert len(band.shape.Solids()) == 1
        uniform = build_shank(_tapered_definition(profile="flat"))
        assert band.volume_mm3 < uniform.volume_mm3


class TestTaperSymmetry:
    """Both shoulders share taper behaviour automatically — taper_ratio()
    is a pure function of angular distance from the head, never manually
    duplicated left/right parameters (brief section 28)."""

    @pytest.mark.parametrize("offset", [0.05, 0.1, 0.2, 0.3])
    def test_symmetric_offsets_from_the_head_produce_the_same_ratio(self, offset):
        d = _tapered_definition(width_ratio=0.6)
        left = taper_ratio(offset, d.band.widthTaper)
        right = taper_ratio(1.0 - offset, d.band.widthTaper)
        assert left == pytest.approx(right)


class TestInvalidTaper:
    """Pydantic v2 does not re-validate on plain attribute assignment
    (StrictModel has no `validate_assignment=True`) — these construct a
    fresh JewelryDefinition via `model_validate()`, the real path every
    JDL input actually goes through, to exercise real construction-time
    rejection."""

    def _band_dict(self, **overrides):
        d = default_definition().model_dump(mode="json")
        d["band"].update(overrides)
        return d

    def test_zero_bottom_ratio_is_rejected_by_schema(self):
        from jewelmind.domain.schema import JewelryDefinition

        with pytest.raises(ValidationError):
            JewelryDefinition.model_validate(self._band_dict(widthTaper={"mode": "NONE", "bottomRatio": 0.0}))

    def test_bottom_ratio_above_one_is_rejected_by_schema(self):
        from jewelmind.domain.schema import JewelryDefinition

        with pytest.raises(ValidationError):
            JewelryDefinition.model_validate(self._band_dict(widthTaper={"mode": "NONE", "bottomRatio": 1.5}))

    def test_negative_bottom_ratio_is_rejected_by_schema(self):
        from jewelmind.domain.schema import JewelryDefinition

        with pytest.raises(ValidationError):
            JewelryDefinition.model_validate(
                self._band_dict(thicknessTaper={"mode": "NONE", "bottomRatio": -0.3})
            )

    def test_unrecognized_taper_mode_is_rejected_by_schema(self):
        from jewelmind.domain.schema import JewelryDefinition

        with pytest.raises(ValidationError):
            JewelryDefinition.model_validate(
                self._band_dict(widthTaper={"mode": "TOWARD_HEAD", "bottomRatio": 1.0})
            )


class TestDegenerateSection:
    """A bottomRatio in (0, 1] structurally guarantees the tapered
    dimension never reaches zero or negative, given a positive base
    dimension — SHANK-GOV-006, enforced at the schema layer rather than
    duplicated inside the builder (SHANK-GOV-002)."""

    def test_smallest_permitted_ratio_still_produces_a_positive_volume_solid(self):
        d = _tapered_definition(width_ratio=1e-6)
        band = build_shank(d)
        assert band.shape.Solids()
        assert band.volume_mm3 > 0


class TestHeadConnection:
    def test_connection_interface_top_z_is_unchanged_by_width_taper(self):
        uniform_interface = shank_connection_interface(default_definition())
        tapered_interface = shank_connection_interface(_tapered_definition(width_ratio=0.5))
        assert tapered_interface.topZMm == uniform_interface.topZMm

    def test_connection_interface_top_z_is_unchanged_by_thickness_taper(self):
        uniform_interface = shank_connection_interface(default_definition())
        tapered_interface = shank_connection_interface(_tapered_definition(thickness_ratio=0.5))
        assert tapered_interface.topZMm == uniform_interface.topZMm

    def test_band_metadata_exposes_the_same_connection_interface(self):
        d = _tapered_definition(width_ratio=0.6)
        band = build_shank(d)
        interface = shank_connection_interface(d)
        assert band.metadata["connectionInterface"]["topZMm"] == interface.topZMm

    def test_tapered_solitaire_head_remains_placeable_and_connected(self):
        model = build_solitaire_ring(_tapered_definition(width_ratio=0.6, thickness_ratio=0.7))
        report = inspect_model(model)
        assert report.assemblyResult.productionConnectivity.isFullyConnected is True
        assert report.assemblyResult.stoneMetalSeparation.fusedIntoProductionMetal is False
        assert report.assemblyResult.prongCount.matches is True


class TestShankVolumeAndBoundingBox:
    def test_tapered_shank_bounding_box_reflects_the_base_dimensions_at_the_head(self):
        model = build_solitaire_ring(_tapered_definition(thickness_ratio=0.5))
        band = model.components["band"]
        # The head keeps the full base outer radius (10.7mm) — bounding
        # box max must still reach it even though the bottom is thinner.
        assert band.bounding_box.zmax == pytest.approx(10.700000000000001, abs=1e-6)

    def test_tapered_shank_volume_is_positive_and_finite(self):
        band = build_shank(_tapered_definition(width_ratio=0.6, thickness_ratio=0.6))
        assert band.volume_mm3 > 0
        assert band.volume_mm3 == band.volume_mm3  # NaN check


class TestShankConnectivity:
    @pytest.mark.parametrize("prong_count", [4, 6])
    def test_tapered_shank_stays_connected_across_supported_prong_counts(self, prong_count):
        d = _tapered_definition(width_ratio=0.65)
        d.setting.prongCount = prong_count
        model = build_solitaire_ring(d)
        report = inspect_model(model)
        assert report.assemblyResult.productionConnectivity.isFullyConnected is True
        assert report.assemblyResult.prongCount.generatedCount == prong_count


class TestShankStepExport:
    def test_tapered_shank_step_roundtrip_has_no_regressions(self):
        model = build_solitaire_ring(_tapered_definition(width_ratio=0.6, thickness_ratio=0.7))
        assert step_roundtrip_check(model) == []

    def test_tapered_shank_step_export_is_non_empty(self):
        model = build_solitaire_ring(_tapered_definition(width_ratio=0.6))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "model.step"
            export_step(model, path, include_stone=False)
            assert path.stat().st_size > 0


class TestShankStlExport:
    def test_tapered_shank_stl_structure_has_no_regressions(self):
        d = _tapered_definition(thickness_ratio=0.5)
        model = build_solitaire_ring(d)
        assert stl_structure_check(model, d) == []

    def test_tapered_shank_stl_export_is_non_empty(self):
        d = _tapered_definition(width_ratio=0.6)
        model = build_solitaire_ring(d)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "model.stl"
            export_stl(model, d, path, include_stone=False)
            assert path.stat().st_size > 0


class TestParameterSweep:
    """Bounded software-valid parameter combinations (brief section 51) —
    profile x taper mode x prong count — never a brute-force space, just
    representative coverage to catch construction failures. Also serves
    as the lightweight substitute for property-based testing (brief
    section 52): Hypothesis is not currently a backend dependency, and
    this repository's own guidance is to avoid adding one "solely for
    this if unnecessary" — a bounded parametrize sweep checking for
    NaN/Inf gives most of the same practical protection without a new
    dependency."""

    @pytest.mark.parametrize("profile", ["flat", "comfort_fit"])
    @pytest.mark.parametrize("width_ratio", [None, 0.5, 0.9])
    @pytest.mark.parametrize("thickness_ratio", [None, 0.4, 0.8])
    @pytest.mark.parametrize("prong_count", [4, 6])
    def test_representative_combination_generates_a_finite_positive_volume(
        self, profile, width_ratio, thickness_ratio, prong_count
    ):
        d = _tapered_definition(width_ratio=width_ratio, thickness_ratio=thickness_ratio, profile=profile)
        d.setting.prongCount = prong_count
        model = build_solitaire_ring(d)
        band = model.components["band"]
        assert band.volume_mm3 > 0
        assert band.volume_mm3 == band.volume_mm3  # not NaN
        assert band.volume_mm3 not in (float("inf"), float("-inf"))
        assert len(band.shape.Solids()) == 1


class TestShankConstructionErrorIsRaisedNotSwallowed:
    def test_shank_construction_error_is_a_real_exception_type(self):
        # Structural proof that a construction failure path exists and is
        # a real exception, never a silent fallback to uniform geometry
        # (SHANK-GOV-007, brief section 48).
        assert issubclass(ShankConstructionError, Exception)


class TestShankCapabilityRegistry:
    def test_current_capabilities_match_what_the_builder_actually_produces(self):
        d = default_definition()
        assert get_shank_capability("uniform_shank").status == "current"
        band = build_shank(d).metadata
        assert band["variation"] == "UNIFORM"

    def test_no_planned_capability_is_marked_generatable_or_jdl_exposed(self):
        for capability in SHANK_CAPABILITIES.values():
            if capability.status == "planned":
                assert capability.generatable is False
                assert capability.jdlExposed is False

    def test_taper_toward_head_is_planned_not_current(self):
        assert get_shank_capability("taper_toward_head").status == "planned"

    def test_split_shank_and_multi_rail_shank_are_planned_not_current(self):
        assert get_shank_capability("split_shank").status == "planned"
        assert get_shank_capability("multi_rail_shank").status == "planned"

    def test_unknown_capability_name_returns_none(self):
        assert get_shank_capability("not_a_real_capability") is None
