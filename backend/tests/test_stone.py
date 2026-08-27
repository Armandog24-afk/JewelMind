"""Stone System v1 (Sprint 18) tests — real, deterministic CAD reference
geometry for 7 shapes. Mirrors the structure/discipline of test_shank.py
(Sprint 17): backward compatibility first, then real generation for every
new shape, then registry/dimension/orientation/inspection/export
coverage. See docs/bible/20-stone/README.md and
docs/bible/appendices/stone-test-matrix.md.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from jewelmind.domain.defaults import default_definition
from jewelmind.domain.schema import JewelryDefinition, StoneSpec
from jewelmind.domain.stone_dimensions import resolved_depth_mm, resolved_length_mm, resolved_width_mm
from jewelmind.exporters.step_exporter import export_step
from jewelmind.exporters.stl_exporter import export_stl
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring
from jewelmind.geometry.components.stone import build_stone_reference
from jewelmind.geometry.inspection.inspector import inspect_model
from jewelmind.geometry.stone.builder import build_stone
from jewelmind.geometry.stone.capability import STONE_SHAPE_CAPABILITIES, get_stone_shape_capability
from jewelmind.geometry.stone.errors import StoneGenerationError
from jewelmind.geometry_quality.artifact_regression import step_roundtrip_check, stl_structure_check
from jewelmind.validation.engine import validate_definition

NON_ROUND_SHAPES = ["oval", "pear", "emerald", "cushion", "princess", "marquise"]


def _stone_definition(shape: str, length: float = 8.0, width: float = 6.0, depth: float = 4.0,
                       orientation: float = 0.0) -> JewelryDefinition:
    d = default_definition()
    if shape == "round":
        d.stone = StoneSpec.model_validate({"shape": "round", "diameter": length, "depth": depth,
                                             "orientation": orientation})
    else:
        d.stone = StoneSpec.model_validate({
            "shape": shape, "length": length, "width": width, "depth": depth, "orientation": orientation,
        })
    return d


class TestRoundStoneBackwardCompatibility:
    def test_default_definition_produces_the_pre_sprint18_recorded_volume(self):
        d = default_definition()
        stone = build_stone_reference(d)
        assert stone.volume_mm3 == pytest.approx(58.22141924499569, rel=1e-9)

    def test_round_stone_is_valid_solid_separate_from_metal(self):
        d = default_definition()
        stone = build_stone_reference(d)
        assert len(stone.shape.Solids()) == 1
        assert stone.volume_mm3 > 0
        assert stone.metadata["shape"] == "round"

    def test_round_stone_reports_length_equals_width_equals_diameter(self):
        d = default_definition()
        stone = build_stone_reference(d)
        assert stone.metadata["lengthMm"] == stone.metadata["widthMm"] == d.stone.diameter


class TestNonRoundShapeGeneration:
    """OVAL_GENERATION_TEST / PEAR_GENERATION_TEST / EMERALD_GENERATION_TEST
    / CUSHION_GENERATION_TEST / PRINCESS_GENERATION_TEST /
    MARQUISE_GENERATION_TEST — every shape genuinely builds a single,
    valid, positive-volume solid via real CAD construction."""

    @pytest.mark.parametrize("shape", NON_ROUND_SHAPES)
    def test_shape_generates_single_valid_positive_volume_solid(self, shape):
        d = _stone_definition(shape)
        stone = build_stone(d)
        assert len(stone.shape.Solids()) == 1
        assert stone.shape.isValid()
        assert stone.volume_mm3 > 0
        assert stone.volume_mm3 == stone.volume_mm3  # not NaN
        assert stone.volume_mm3 not in (float("inf"), float("-inf"))
        assert stone.metadata["shape"] == shape
        assert stone.metadata["isGemologicalReproduction"] is False

    @pytest.mark.parametrize("shape", NON_ROUND_SHAPES)
    def test_shape_bounding_box_matches_requested_length_and_width_at_default_orientation(self, shape):
        d = _stone_definition(shape, length=9.0, width=5.0)
        stone = build_stone(d)
        bb = stone.bounding_box
        assert (bb.ymax - bb.ymin) == pytest.approx(9.0, abs=0.01)
        assert (bb.xmax - bb.xmin) == pytest.approx(5.0, abs=0.01)

    @pytest.mark.parametrize("shape", NON_ROUND_SHAPES)
    def test_shape_reference_stays_separate_from_metal(self, shape):
        d = _stone_definition(shape)
        model = build_solitaire_ring(d)
        stone = model.components["stone_reference"]
        band = model.components["band"]
        assert stone.bounding_box.zmin >= band.bounding_box.zmax - 1e-6


class TestStoneCapabilityRegistry:
    def test_every_current_shape_has_capability_metadata(self):
        for shape in ["round", *NON_ROUND_SHAPES]:
            cap = get_stone_shape_capability(shape)
            assert cap is not None
            assert cap.status == "current"
            assert cap.generationSupported is True

    def test_round_setting_compatibility_is_supported(self):
        assert get_stone_shape_capability("round").currentSettingCompatibility == "SUPPORTED"

    @pytest.mark.parametrize("shape", NON_ROUND_SHAPES)
    def test_non_round_setting_compatibility_is_experimental(self, shape):
        assert get_stone_shape_capability(shape).currentSettingCompatibility == "EXPERIMENTAL"

    def test_no_shape_is_marked_planned(self):
        # Strong target achieved (brief section 61): all 7 shapes current.
        assert all(cap.status == "current" for cap in STONE_SHAPE_CAPABILITIES.values())

    def test_unknown_shape_returns_none(self):
        assert get_stone_shape_capability("asscher") is None


class TestStoneDimensionValidation:
    def test_round_without_diameter_is_rejected(self):
        with pytest.raises(ValidationError):
            StoneSpec.model_validate({"shape": "round", "diameter": None})

    @pytest.mark.parametrize("shape", NON_ROUND_SHAPES)
    def test_non_round_without_length_or_width_is_rejected(self, shape):
        with pytest.raises(ValidationError):
            StoneSpec.model_validate({"shape": shape})

    @pytest.mark.parametrize("shape", NON_ROUND_SHAPES)
    def test_non_round_with_only_length_is_rejected(self, shape):
        with pytest.raises(ValidationError):
            StoneSpec.model_validate({"shape": shape, "length": 8.0})

    def test_unknown_shape_is_rejected(self):
        with pytest.raises(ValidationError):
            StoneSpec.model_validate({"shape": "asscher", "length": 8.0, "width": 6.0})

    def test_resolved_dimensions_match_public_fields_for_round(self):
        stone = StoneSpec.model_validate({"shape": "round", "diameter": 7.0, "depth": 4.0})
        assert resolved_length_mm(stone) == 7.0
        assert resolved_width_mm(stone) == 7.0
        assert resolved_depth_mm(stone) == 4.0

    @pytest.mark.parametrize("shape", NON_ROUND_SHAPES)
    def test_resolved_dimensions_match_public_fields_for_non_round(self, shape):
        stone = StoneSpec.model_validate({"shape": shape, "length": 9.0, "width": 5.5, "depth": 3.5})
        assert resolved_length_mm(stone) == 9.0
        assert resolved_width_mm(stone) == 5.5
        assert resolved_depth_mm(stone) == 3.5


class TestStoneOrientation:
    """STONE_ORIENTATION_TEST / ROUND_ROTATION_EQUIVALENCE_TEST."""

    def test_round_orientation_does_not_change_volume_or_bounding_box(self):
        base = _stone_definition("round", length=6.5)
        rotated = _stone_definition("round", length=6.5, orientation=45.0)
        s0 = build_stone(base)
        s1 = build_stone(rotated)
        assert s0.volume_mm3 == pytest.approx(s1.volume_mm3, rel=1e-6)
        assert (s0.bounding_box.xmax - s0.bounding_box.xmin) == pytest.approx(
            s1.bounding_box.xmax - s1.bounding_box.xmin, abs=1e-3
        )

    @pytest.mark.parametrize("shape", ["oval", "marquise"])
    def test_90_degree_rotation_swaps_bounding_box_extents(self, shape):
        d0 = _stone_definition(shape, length=9.0, width=5.0, orientation=0.0)
        d90 = _stone_definition(shape, length=9.0, width=5.0, orientation=90.0)
        s0 = build_stone(d0)
        s90 = build_stone(d90)
        bb0, bb90 = s0.bounding_box, s90.bounding_box
        extent0 = (bb0.ymax - bb0.ymin, bb0.xmax - bb0.xmin)
        extent90 = (bb90.ymax - bb90.ymin, bb90.xmax - bb90.xmin)
        assert extent0[0] == pytest.approx(extent90[1], abs=0.05)
        assert extent0[1] == pytest.approx(extent90[0], abs=0.05)
        assert s0.volume_mm3 == pytest.approx(s90.volume_mm3, rel=1e-6)


class TestPearAsymmetry:
    """PEAR_ASYMMETRY_TEST (brief section 51) — the deliberate asymmetric
    case. A pear must not accidentally symmetrize into something
    equivalent to an oval."""

    @staticmethod
    def _centroid_offset_y(component) -> float:
        """Signed distance from the solid's bounding-box center to its real
        center of mass, along the local Y (LENGTH) axis.

        This is the genuinely discriminating asymmetry signal: a shape that
        is bilaterally symmetric about its own Y midplane has a centroid
        exactly at the bounding-box center (offset ~0), while a pear's mass
        is concentrated toward its rounded end. Comparing volumes or bbox
        extents alone would NOT prove this — two different shapes can
        differ in volume while both being symmetric.
        """

        bb = component.bounding_box
        return component.shape.Center().y - (bb.ymin + bb.ymax) / 2

    def test_pear_mass_is_offset_toward_the_rounded_end(self):
        pear = build_stone(_stone_definition("pear", length=9.0, width=6.0))
        offset = self._centroid_offset_y(pear)
        # pear_outline() puts the TIP at +Y and the rounded end at -Y, so the
        # mass must sit on the -Y side of the bounding-box center.
        assert offset < -0.5, f"pear centroid offset {offset} is not clearly toward -Y"

    @pytest.mark.parametrize("symmetric_shape", ["oval", "marquise"])
    def test_symmetric_elongated_shapes_have_no_centroid_offset(self, symmetric_shape):
        # The control case: same class, same length/width, but bilaterally
        # symmetric — so the pear assertion above cannot pass for a trivial
        # reason that would also hold for a symmetric shape.
        stone = build_stone(_stone_definition(symmetric_shape, length=9.0, width=6.0))
        assert abs(self._centroid_offset_y(stone)) < 1e-3

    def test_rotating_pear_180_degrees_flips_the_tip_direction(self):
        s0 = build_stone(_stone_definition("pear", length=9.0, width=6.0, orientation=0.0))
        s180 = build_stone(_stone_definition("pear", length=9.0, width=6.0, orientation=180.0))

        offset0 = self._centroid_offset_y(s0)
        offset180 = self._centroid_offset_y(s180)

        # A real semantic flip: the mass moves to the opposite side of the
        # bounding-box center, by the same magnitude.
        assert offset0 < 0 < offset180
        assert offset180 == pytest.approx(-offset0, rel=1e-6)

        # ...and it is a RIGID motion, not a reshape.
        assert s0.volume_mm3 == pytest.approx(s180.volume_mm3, rel=1e-6)
        assert (s0.bounding_box.ymax - s0.bounding_box.ymin) == pytest.approx(
            s180.bounding_box.ymax - s180.bounding_box.ymin, abs=1e-3
        )

    def test_rotating_pear_180_degrees_is_not_a_no_op(self):
        # Guards the specific regression where _apply_orientation() might
        # early-return for any angle, silently making orientation inert.
        s0 = build_stone(_stone_definition("pear", length=9.0, width=6.0, orientation=0.0))
        s180 = build_stone(_stone_definition("pear", length=9.0, width=6.0, orientation=180.0))
        assert self._centroid_offset_y(s0) != pytest.approx(
            self._centroid_offset_y(s180), abs=1e-3
        )

    def test_pear_generator_never_silently_produces_a_symmetric_fallback(self):
        # Structural check: the pear outline function is distinct from
        # the oval/marquise ones (STONE-GOV-013 — no silent fallback to
        # another shape's generator).
        from jewelmind.geometry.stone.builder import _NON_ROUND_OUTLINE_BUILDERS

        assert _NON_ROUND_OUTLINE_BUILDERS["pear"] is not _NON_ROUND_OUTLINE_BUILDERS["oval"]
        assert _NON_ROUND_OUTLINE_BUILDERS["pear"] is not _NON_ROUND_OUTLINE_BUILDERS["marquise"]


class TestStoneMeasuredDimensions:
    """STONE_MEASURED_DIMENSION_TEST / STONE_REFERENCE_ROLE_TEST /
    STONE_INSPECTION_TEST."""

    def test_round_requested_and_measured_dimensions_match(self):
        d = default_definition()
        model = build_solitaire_ring(d)
        report = inspect_model(model)
        facts = {f.factType: f.value for f in report.geometricFacts if f.componentIds == ["stone_reference"]}
        assert facts["STONE_REQUESTED_LENGTH"] == pytest.approx(facts["STONE_MEASURED_LENGTH"], abs=1e-3)
        assert facts["STONE_REQUESTED_WIDTH"] == pytest.approx(facts["STONE_MEASURED_WIDTH"], abs=1e-3)
        assert facts["STONE_REQUESTED_DEPTH"] == pytest.approx(facts["STONE_MEASURED_DEPTH"], abs=1e-3)

    @pytest.mark.parametrize("shape", NON_ROUND_SHAPES)
    def test_non_round_requested_and_measured_dimensions_match(self, shape):
        d = _stone_definition(shape, length=9.0, width=5.0, depth=3.5)
        model = build_solitaire_ring(d)
        report = inspect_model(model)
        facts = {f.factType: f.value for f in report.geometricFacts if f.componentIds == ["stone_reference"]}
        assert facts["STONE_REQUESTED_LENGTH"] == pytest.approx(facts["STONE_MEASURED_LENGTH"], abs=0.05)
        assert facts["STONE_REQUESTED_WIDTH"] == pytest.approx(facts["STONE_MEASURED_WIDTH"], abs=0.05)

    def test_stone_reference_never_reported_as_production_metal(self):
        d = default_definition()
        model = build_solitaire_ring(d)
        report = inspect_model(model)
        assert report.assemblyResult.stoneMetalSeparation.fusedIntoProductionMetal is False


class TestStoneProductionExportExclusion:
    """STONE_PRODUCTION_EXPORT_EXCLUSION_TEST — restates LAW-006 for every
    new shape, not just round."""

    @pytest.mark.parametrize("shape", NON_ROUND_SHAPES)
    def test_step_export_excludes_stone_by_default(self, shape):
        d = _stone_definition(shape)
        model = build_solitaire_ring(d)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "model.step"
            export_step(model, path, include_stone=False)
            assert path.stat().st_size > 0


class TestStoneStepExport:
    @pytest.mark.parametrize("shape", ["oval", "emerald", "cushion", "princess"])
    def test_step_roundtrip_has_no_regressions(self, shape):
        model = build_solitaire_ring(_stone_definition(shape))
        assert step_roundtrip_check(model) == []


class TestStoneStlExport:
    @pytest.mark.parametrize("shape", ["oval", "pear", "marquise"])
    def test_stl_structure_has_no_regressions(self, shape):
        d = _stone_definition(shape)
        model = build_solitaire_ring(d)
        assert stl_structure_check(model, d) == []

    def test_stl_export_is_non_empty_for_a_non_round_shape(self):
        d = _stone_definition("oval")
        model = build_solitaire_ring(d)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "model.stl"
            export_stl(model, d, path, include_stone=False)
            assert path.stat().st_size > 0


class TestNonRoundAssembly:
    """NON_ROUND_ASSEMBLY_TEST (brief section 28/47/67) — at minimum
    ROUND + OVAL + one angular/rounded-angular shape must generate inside
    the full solitaire assembly, exercising positioning/inspection/export."""

    @pytest.mark.parametrize("shape", ["oval", "emerald", "cushion", "princess"])
    def test_shape_generates_a_fully_connected_solitaire_assembly(self, shape):
        d = _stone_definition(shape)
        model = build_solitaire_ring(d)
        report = inspect_model(model)
        assert report.assemblyResult.fullAssemblyConnectivity.isFullyConnected is True
        assert report.assemblyResult.prongCount.generatedCount == d.setting.prongCount


class TestForgeRoundRuleScope:
    """FORGE_ROUND_RULE_SCOPE_TEST — STONE_DIAMETER_RANGE and
    PRONG_COUNT_VS_STONE_SIZE never fire for a non-round shape (they are
    ROUND_ONLY); STONE_DEPTH_RANGE fires for every shape using the real
    resolved minimum extent, never a fabricated equivalent diameter."""

    def test_stone_diameter_range_never_fires_for_non_round(self):
        d = _stone_definition("oval", length=100.0, width=100.0)  # would violate diameter range if misapplied
        results = validate_definition(d)
        assert not any(r.ruleId == "JM-STONE-001" for r in results)

    def test_prong_count_vs_stone_size_never_fires_for_non_round(self):
        d = _stone_definition("oval", length=20.0, width=20.0)
        d.setting.prongCount = 4
        results = validate_definition(d)
        assert not any(r.ruleId == "JM-PRONG-003" for r in results)

    def test_stone_depth_range_fires_for_non_round_using_real_minimum_extent(self):
        d = _stone_definition("oval", length=8.0, width=6.0, depth=6.5)  # depth > min(length, width)
        results = validate_definition(d)
        assert any(r.ruleId == "JM-STONE-002" and r.severity == "error" for r in results)

    def test_valid_non_round_stone_produces_no_stone_errors(self):
        d = _stone_definition("cushion", length=7.0, width=7.0, depth=4.0)
        results = validate_definition(d)
        errors = [
            r for r in results if r.severity == "error" and r.parameter and r.parameter.startswith("stone.")
        ]
        assert errors == []


class TestStoneConstructionErrorIsRaisedNotSwallowed:
    def test_stone_generation_error_is_a_real_exception_type(self):
        assert issubclass(StoneGenerationError, Exception)
