"""GOLDEN_COMPONENT_PRESENCE_TEST, GOLDEN_SOLID_COUNT_TEST,
GOLDEN_CONNECTIVITY_TEST, GOLDEN_INTERSECTION_RELATION_TEST,
GOLDEN_PRONG_COUNT_TEST, GOLDEN_STONE_ROLE_TEST,
GOLDEN_VOLATILE_FIELD_NORMALIZATION_TEST, GOLDEN_METADATA_EQUIVALENCE_TEST.

Uses the real JDL -> validation -> geometry -> inspection pipeline; never
mocks geometry (QUALITY-GOV-015).
"""

from __future__ import annotations

import pytest

from jewelmind.domain.defaults import default_definition
from jewelmind.geometry_quality.snapshot import generate_snapshot


class TestComponentPresence:
    def test_all_four_real_components_are_present(self):
        snapshot, _model, _report = generate_snapshot(default_definition())
        component_ids = {c.componentId for c in snapshot.components}
        assert component_ids == {"band", "stone_reference", "prongs", "basket_support"}
        assert all(c.present for c in snapshot.components)


class TestSolidCount:
    def test_band_is_a_single_solid(self):
        snapshot, _model, _report = generate_snapshot(default_definition())
        band = next(c for c in snapshot.components if c.componentId == "band")
        assert band.solidCount == 1

    def test_default_prongs_solid_count_matches_generated_count(self):
        snapshot, _model, _report = generate_snapshot(default_definition())
        prongs = next(c for c in snapshot.components if c.componentId == "prongs")
        assert prongs.solidCount == snapshot.designConsistency.generatedProngCount


class TestConnectivity:
    def test_production_metal_is_fully_connected_by_default(self):
        snapshot, _model, _report = generate_snapshot(default_definition())
        assert snapshot.assembly.productionIsFullyConnected is True
        assert snapshot.assembly.productionConnectivityGroups == 1


class TestIntersectionRelations:
    def test_band_and_stone_reference_do_not_intersect(self):
        snapshot, _model, _report = generate_snapshot(default_definition())
        rel = next(
            r
            for r in snapshot.relationships
            if {r.componentA, r.componentB} == {"band", "stone_reference"}
        )
        assert rel.intersectionStatus == "NO_INTERSECTION"

    def test_prongs_and_basket_support_intersect(self):
        snapshot, _model, _report = generate_snapshot(default_definition())
        rel = next(
            r for r in snapshot.relationships if {r.componentA, r.componentB} == {"prongs", "basket_support"}
        )
        assert rel.intersectionStatus == "INTERSECTS"


class TestProngCount:
    def test_default_six_prong_matches(self):
        snapshot, _model, _report = generate_snapshot(default_definition())
        assert snapshot.designConsistency.requestedProngCount == 6
        assert snapshot.designConsistency.generatedProngCount == 6
        assert snapshot.designConsistency.prongCountMatches is True

    def test_four_prong_matches(self):
        d = default_definition()
        d.setting.prongCount = 4
        snapshot, _model, _report = generate_snapshot(d)
        assert snapshot.designConsistency.requestedProngCount == 4
        assert snapshot.designConsistency.generatedProngCount == 4
        assert snapshot.designConsistency.prongCountMatches is True


class TestStoneRole:
    def test_stone_reference_is_never_production_metal(self):
        snapshot, _model, _report = generate_snapshot(default_definition())
        stone = next(c for c in snapshot.components if c.componentId == "stone_reference")
        assert stone.role == "REFERENCE"
        assert snapshot.designConsistency.stoneReferenceIsProductionMetal is False


class TestVolatileFieldNormalization:
    """A GeometrySnapshot must never carry an inspection ID, a timestamp,
    or any other value that would make two snapshots of identical
    geometry compare unequal (QUALITY-GOV-002)."""

    def test_snapshot_has_no_volatile_fields(self):
        snapshot, _model, _report = generate_snapshot(default_definition())
        dumped = snapshot.model_dump_json()
        for forbidden in ("inspectionId", "startedAt", "completedAt", "generatedAt", "performance"):
            assert forbidden not in dumped

    def test_two_snapshots_of_identical_geometry_are_equal(self):
        s1, _m1, _r1 = generate_snapshot(default_definition())
        s2, _m2, _r2 = generate_snapshot(default_definition())
        assert s1.model_dump() == s2.model_dump()


class TestMetadataOnlyEquivalence:
    """metal/manufacturing.method are currently metadata/validation-context
    only, never geometry-driving inputs (see
    docs/bible/04-jewelry-domain/052-parametric-dependency-model.md).
    Two definitions differing only in these fields get different
    definitionHash values (current JDL hashing is not scoped by this
    subsystem, per brief section 9), but their GeometrySnapshots must be
    equal in every geometric fact."""

    @pytest.mark.parametrize("metal", ["white_gold_18k", "rose_gold_18k", "platinum", "silver"])
    def test_metal_choice_does_not_change_geometry_snapshot(self, metal):
        baseline, _m, _r = generate_snapshot(default_definition())
        d = default_definition()
        d.material.metal = metal
        varied, _m2, _r2 = generate_snapshot(d)
        assert baseline.definitionHash != varied.definitionHash
        assert baseline.model_dump(exclude={"definitionHash"}) == varied.model_dump(
            exclude={"definitionHash"}
        )

    def test_manufacturing_method_does_not_change_geometry_snapshot(self):
        baseline, _m, _r = generate_snapshot(default_definition())
        d = default_definition()
        d.manufacturing.method = "direct_resin_printing"
        varied, _m2, _r2 = generate_snapshot(d)
        assert baseline.definitionHash != varied.definitionHash
        assert baseline.model_dump(exclude={"definitionHash"}) == varied.model_dump(
            exclude={"definitionHash"}
        )
