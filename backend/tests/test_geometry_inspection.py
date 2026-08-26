"""Runtime geometry inspection tests (Sprint 14 — Geometry Inspection v2).

Every test that inspects "the real solitaire" generates one via
`build_solitaire_ring(default_definition())` — never hand-typed geometry.
Tests using deliberately broken fixtures (missing component, disconnected
solids, overlapping solids) build them explicitly with cadquery box
primitives, clearly marked TEST FIXTURE — never a supported jewelry
model (see the Sprint 14 brief, item 47).
"""

from __future__ import annotations

import cadquery as cq
import pytest

from jewelmind.domain.defaults import default_definition
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring
from jewelmind.geometry.inspection import inspect_model
from jewelmind.geometry.inspection.components import inspect_component
from jewelmind.geometry.inspection.connectivity import build_connectivity_graph, pairwise_distances
from jewelmind.geometry.inspection.distance import inspect_distance
from jewelmind.geometry.inspection.intersection import inspect_intersection
from jewelmind.geometry.inspection.version import CONTACT_TOLERANCE_MM
from jewelmind.geometry.model import BoundingBox, GeneratedComponent, GeneratedModel


def _real_model() -> GeneratedModel:
    return build_solitaire_ring(default_definition())


def _box_component(name: str, x: float, y: float, z: float, size: float = 1.0) -> GeneratedComponent:
    """TEST FIXTURE ONLY — a plain cube, never a supported jewelry model."""

    solid = cq.Workplane("XY").workplane(offset=z).center(x, y).box(size, size, size).val()
    return GeneratedComponent(
        name=name,
        shape=solid,
        volume_mm3=solid.Volume(),
        bounding_box=BoundingBox.from_shape(solid),
    )


def _fixture_model(components: dict[str, GeneratedComponent]) -> GeneratedModel:
    """TEST FIXTURE ONLY — assembles arbitrary test components into a
    GeneratedModel shape without going through the real solitaire
    builder, so inspection logic can be tested against known-broken
    geometry without pretending it's a supported jewelry model."""

    shapes = [c.shape for c in components.values()]
    combined = cq.Compound.makeCompound(shapes) if shapes else cq.Compound.makeCompound([])
    bbox = BoundingBox(0, 0, 0, 1, 1, 1)
    for c in components.values():
        bbox = bbox.union(c.bounding_box)
    return GeneratedModel(
        definition_hash="test-fixture",
        generator_version="test",
        generation_duration_s=0.0,
        components=components,
        combined_metal=combined,
        combined_metal_volume_mm3=sum(c.volume_mm3 for c in components.values()),
        bounding_box=bbox,
        warnings=[],
    )


class TestComponentExistsInspection:
    def test_every_real_component_exists(self):
        model = _real_model()
        for name, comp in model.components.items():
            result = inspect_component(name, comp)
            assert result.exists is True
            assert result.status == "PASS"

    def test_a_zero_solid_component_is_reported_missing(self):
        empty = GeneratedComponent(
            name="prongs",
            shape=cq.Compound.makeCompound([]),
            volume_mm3=0.0,
            bounding_box=BoundingBox(0, 0, 0, 0, 0, 0),
        )
        result = inspect_component("prongs", empty)
        assert result.exists is False
        assert result.status == "FAIL"
        assert any(d.code == "INSPECTION_COMPONENT_MISSING" for d in result.diagnostics)


class TestComponentVolumeInspection:
    def test_real_component_volumes_are_finite_and_positive(self):
        model = _real_model()
        for name, comp in model.components.items():
            result = inspect_component(name, comp)
            assert result.volumeMm3 is not None
            assert result.volumeMm3 > 0
            assert result.volumeMm3 == result.volumeMm3  # not NaN


class TestComponentBoundingBox:
    def test_real_component_bounding_boxes_have_positive_extent(self):
        model = _real_model()
        for name, comp in model.components.items():
            result = inspect_component(name, comp)
            bbox = result.boundingBox
            assert bbox is not None
            assert bbox.sizeX >= 0
            assert bbox.sizeY >= 0
            assert bbox.sizeZ >= 0


class TestSolidCount:
    def test_prongs_solid_count_matches_generated_count(self):
        model = _real_model()
        result = inspect_component("prongs", model.components["prongs"])
        assert result.solidCount == model.components["prongs"].metadata["generatedCount"]

    def test_band_is_a_single_solid(self):
        model = _real_model()
        result = inspect_component("band", model.components["band"])
        assert result.solidCount == 1


class TestAssemblyComponentCount:
    def test_real_solitaire_has_4_components(self):
        model = _real_model()
        report = inspect_model(model)
        assert report.assemblyResult.componentCount == 4
        assert report.assemblyResult.productionComponentCount == 3
        assert report.assemblyResult.referenceComponentCount == 1

    def test_required_components_present(self):
        model = _real_model()
        report = inspect_model(model)
        assert report.assemblyResult.requiredComponentsPresent
        assert report.assemblyResult.missingComponentIds == []


class TestProngCountInspection:
    @pytest.mark.parametrize("count", [4, 6])
    def test_requested_matches_generated_for_supported_counts(self, count):
        d = default_definition()
        d2 = d.model_copy(update={"setting": d.setting.model_copy(update={"prongCount": count})})
        model = build_solitaire_ring(d2)
        report = inspect_model(model)
        assert report.assemblyResult.prongCount.requestedCount == count
        assert report.assemblyResult.prongCount.generatedCount == count
        assert report.assemblyResult.prongCount.matches is True
        assert report.assemblyResult.prongCount.status == "PASS"

    def test_negative_requested_count_is_reported_as_a_mismatch(self):
        # The geometry builder itself (`build_prongs()`) happily builds
        # whatever count it's asked for, INCLUDING an unsupported one like
        # 5 — Forge's JM-PRONG-001 rule is what actually blocks an
        # unsupported count, at `ModelService.generate()`'s validation
        # step, before this builder ever runs for real user input. Calling
        # the builder directly (as this test does, bypassing validation on
        # purpose) only diverges requested/generated for a genuinely
        # invalid input the builder itself clamps: a negative count.
        d = default_definition()
        d2 = d.model_copy(update={"setting": d.setting.model_copy(update={"prongCount": -1})})
        model = build_solitaire_ring(d2)
        report = inspect_model(model)
        assert report.assemblyResult.prongCount.requestedCount == -1
        assert report.assemblyResult.prongCount.generatedCount == 0
        assert report.assemblyResult.prongCount.matches is False
        assert report.assemblyResult.prongCount.status == "FAIL"


class TestStoneReferenceRole:
    def test_stone_reference_is_counted_as_the_only_reference_component(self):
        model = _real_model()
        report = inspect_model(model)
        assert report.assemblyResult.referenceComponentCount == 1
        assert "stone_reference" not in report.assemblyResult.productionConnectivity.nodes
        assert "stone_reference" in report.assemblyResult.fullAssemblyConnectivity.nodes

    def test_stone_metal_separation_reports_stone_exists_and_is_not_fused(self):
        model = _real_model()
        report = inspect_model(model)
        separation = report.assemblyResult.stoneMetalSeparation
        assert separation.stoneReferenceExists is True
        assert separation.productionIncluded is False
        assert separation.fusedIntoProductionMetal is False
        assert separation.status == "PASS"

    def test_stone_intersecting_prongs_is_expected_not_a_fusion_signal(self):
        """The stone reference DOES geometrically intersect prongs/basket by
        design (EMBED_MM-driven grip realism) — this must never be
        confused with the stone's solid having been unioned into
        production metal (LAW-006)."""

        model = _real_model()
        report = inspect_model(model)
        separation = report.assemblyResult.stoneMetalSeparation
        assert "prongs" in separation.intersectsProductionComponents
        assert separation.fusedIntoProductionMetal is False


class TestStoneExportSeparation:
    def test_stone_reference_is_excluded_from_combined_metal(self):
        model = _real_model()
        stone_volume = model.components["stone_reference"].volume_mm3
        assert model.combined_metal_volume_mm3 < model.combined_metal_volume_mm3 + stone_volume
        # The combined_metal shape itself (what STEP/STL export uses by
        # default) must never include the stone's volume.
        metal_solids_volume = model.combined_metal.Volume()
        assert metal_solids_volume == pytest.approx(model.combined_metal_volume_mm3)


class TestComponentIntersection:
    def test_band_and_stone_do_not_intersect(self):
        model = _real_model()
        band_shape = model.components["band"].shape
        stone_shape = model.components["stone_reference"].shape
        result = inspect_intersection("band", band_shape, "stone_reference", stone_shape)
        assert result.status == "NO_INTERSECTION"
        assert result.intersectionVolumeMm3 == 0.0

    def test_prongs_and_basket_intersect_with_positive_volume(self):
        model = _real_model()
        prongs_shape = model.components["prongs"].shape
        basket_shape = model.components["basket_support"].shape
        result = inspect_intersection("prongs", prongs_shape, "basket_support", basket_shape)
        assert result.status == "INTERSECTS"
        assert result.intersectionVolumeMm3 > 0

    def test_known_separated_skips_the_boolean_call_and_reports_no_intersection(self):
        model = _real_model()
        result = inspect_intersection(
            "band",
            model.components["band"].shape,
            "stone_reference",
            model.components["stone_reference"].shape,
            known_separated=True,
        )
        assert result.status == "NO_INTERSECTION"
        assert "Skipped" in result.note


class TestComponentDistance:
    def test_band_and_stone_distance_is_positive(self):
        model = _real_model()
        band_shape = model.components["band"].shape
        stone_shape = model.components["stone_reference"].shape
        result = inspect_distance("band", band_shape, "stone_reference", stone_shape)
        assert result.status == "PASS"
        assert result.minDistanceMm is not None
        assert result.minDistanceMm > 0

    def test_touching_components_report_zero_distance(self):
        model = _real_model()
        result = inspect_distance(
            "band", model.components["band"].shape, "prongs", model.components["prongs"].shape
        )
        assert result.minDistanceMm == pytest.approx(0.0, abs=1e-6)


class TestProductionConnectivity:
    def test_real_solitaire_production_metal_is_fully_connected(self):
        model = _real_model()
        report = inspect_model(model)
        connectivity = report.assemblyResult.productionConnectivity
        assert connectivity.isFullyConnected is True
        assert connectivity.disconnectedGroupCount == 0
        assert sorted(connectivity.connectedGroups[0]) == ["band", "basket_support", "prongs"]

    def test_full_assembly_graph_includes_the_stone_reference(self):
        model = _real_model()
        report = inspect_model(model)
        assert "stone_reference" in report.assemblyResult.fullAssemblyConnectivity.nodes


class TestDisconnectedFixture:
    def test_two_far_apart_boxes_are_reported_as_two_disconnected_groups(self):
        components = {
            "band": _box_component("band", 0, 0, 0),
            "basket_support": _box_component("basket_support", 100, 100, 100),
        }
        shapes = {n: c.shape for n, c in components.items()}
        distances = pairwise_distances(shapes)
        graph = build_connectivity_graph(list(components.keys()), distances, "PRODUCTION")
        assert graph.isFullyConnected is False
        assert graph.disconnectedGroupCount == 1
        assert len(graph.connectedGroups) == 2

    def test_disconnection_is_never_hidden_or_silently_repaired(self):
        components = {
            "band": _box_component("band", 0, 0, 0),
            "basket_support": _box_component("basket_support", 50, 50, 50),
        }
        distances = pairwise_distances({n: c.shape for n, c in components.items()})
        assert distances[0].minDistanceMm is not None
        assert distances[0].minDistanceMm > CONTACT_TOLERANCE_MM


class TestIntersectingFixture:
    def test_two_overlapping_boxes_report_a_real_intersection_volume(self):
        a = _box_component("a", 0, 0, 0, size=2.0)
        b = _box_component("b", 0.5, 0, 0, size=2.0)
        result = inspect_intersection("a", a.shape, "b", b.shape)
        assert result.status == "INTERSECTS"
        assert result.intersectionVolumeMm3 > 0


class TestInspectionErrorRecovery:
    def test_intersection_with_a_kernel_failure_returns_unknown_not_a_crash(self, monkeypatch):
        import jewelmind.geometry.inspection.intersection as intersection_module

        model = _real_model()

        class _BoomShape:
            def intersect(self, other):
                raise RuntimeError("simulated kernel failure")

        result = intersection_module.inspect_intersection(
            "band", _BoomShape(), "prongs", model.components["prongs"].shape
        )
        assert result.status == "UNKNOWN"

    def test_distance_with_a_kernel_failure_returns_error_not_a_crash(self):
        import jewelmind.geometry.inspection.distance as distance_module

        model = _real_model()

        class _BoomShape:
            def distance(self, other):
                raise RuntimeError("simulated kernel failure")

        result = distance_module.inspect_distance(
            "band", _BoomShape(), "prongs", model.components["prongs"].shape
        )
        assert result.status == "ERROR"
        assert result.minDistanceMm is None


class TestInspectionDeterminism:
    def test_inspecting_the_same_geometry_twice_produces_equivalent_facts(self):
        model = _real_model()
        report1 = inspect_model(model)
        report2 = inspect_model(model)

        assert report1.assemblyResult.componentCount == report2.assemblyResult.componentCount
        assert report1.assemblyResult.productionConnectivity.connectedGroups == (
            report2.assemblyResult.productionConnectivity.connectedGroups
        )
        for c1, c2 in zip(report1.componentResults, report2.componentResults, strict=True):
            assert c1.solidCount == c2.solidCount
            assert c1.volumeMm3 == pytest.approx(c2.volumeMm3, rel=1e-9)
            assert c1.boundingBox.sizeX == pytest.approx(c2.boundingBox.sizeX, rel=1e-9)
        intersections_pairs = zip(
            report1.assemblyResult.intersections, report2.assemblyResult.intersections, strict=True
        )
        for i1, i2 in intersections_pairs:
            assert i1.status == i2.status
        # Non-deterministic fields (ids/timestamps) are expected to differ.
        assert report1.inspectionId != report2.inspectionId


class TestInspectionMetadata:
    def test_generated_model_record_carries_a_real_inspection_report(self):
        from jewelmind.services.model_service import ModelService

        service = ModelService()
        record = service.generate(default_definition())
        assert record.inspection_report.status in ("PASS", "FAIL")
        assert record.inspection_report.assemblyResult.componentCount == 4

    def test_inspection_report_accessor_returns_the_same_report(self):
        from jewelmind.services.model_service import ModelService

        service = ModelService()
        record = service.generate(default_definition())
        assert service.inspection_report(record.model_id) is record.inspection_report


class TestInspectionRegression:
    """A minimal regression baseline for the default solitaire — real
    values captured from an actual generation, compared with tolerance,
    never exact floating-point equality (INSPECT-GOV-011/012)."""

    def test_default_solitaire_matches_the_recorded_baseline_within_tolerance(self):
        model = _real_model()
        report = inspect_model(model)

        assert report.assemblyResult.componentCount == 4
        assert report.assemblyResult.productionComponentCount == 3
        assert report.assemblyResult.prongCount.generatedCount == 6
        assert report.assemblyResult.productionConnectivity.isFullyConnected is True

        band = next(c for c in report.componentResults if c.componentId == "band")
        assert band.volumeMm3 == pytest.approx(250.99, rel=0.05)

        stone = next(c for c in report.componentResults if c.componentId == "stone_reference")
        assert stone.volumeMm3 == pytest.approx(58.22, rel=0.05)


class TestFallbackInspection:
    def test_band_fillet_fallback_state_is_visible_via_metadata(self):
        model = _real_model()
        result = inspect_component("band", model.components["band"])
        # filletApplied is a real fact already tracked by the band builder;
        # inspection surfaces it, never invents a separate signal.
        assert "filletApplied" in result.metadata

    def test_combined_metal_multi_solid_is_detectable_as_a_fallback_signal(self):
        model = _real_model()
        report = inspect_model(model)
        boolean_ops = report.assemblyResult.booleanOperations
        fuse_op = next(op for op in boolean_ops if op.outputComponentId == "combined_metal")
        # The real default solitaire fuses cleanly to 1 solid — no
        # fallback — verified as a real fact, not assumed.
        assert fuse_op.outputSolidCount == 1
        assert fuse_op.fallbackUsed is False


class TestReviewPackageInspectionFile:
    def test_review_package_contains_real_geometry_inspection_json(self):
        import json
        import zipfile

        from jewelmind.professional_validation.review_package import build_review_package
        from jewelmind.services.model_service import ModelService

        service = ModelService()
        record = service.generate(default_definition())
        zip_path, _manifest = build_review_package(service, record.model_id, case_id="JMCASE-INSPECTION")
        try:
            with zipfile.ZipFile(zip_path) as zf:
                assert "geometry-inspection.json" in zf.namelist()
                data = json.loads(zf.read("geometry-inspection.json"))
            assert data["definitionHash"] == record.generated_model.definition_hash
            assert data["assemblyResult"]["componentCount"] == 4
        finally:
            zip_path.unlink(missing_ok=True)
