from jewelmind.domain.defaults import default_definition
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring
from jewelmind.geometry.components.band import build_ring_band
from jewelmind.geometry.components.basket import build_basket_support
from jewelmind.geometry.components.prongs import build_prongs
from jewelmind.geometry.components.stone import build_stone_reference


def test_flat_band_is_valid_solid_with_positive_volume():
    d = default_definition()
    d.band.profile = "flat"
    band = build_ring_band(d)
    assert band.shape.Solids()
    assert band.volume_mm3 > 0


def test_comfort_fit_band_is_valid_solid_with_positive_volume():
    d = default_definition()
    d.band.profile = "comfort_fit"
    band = build_ring_band(d)
    assert band.shape.Solids()
    assert band.volume_mm3 > 0


def test_flat_and_comfort_fit_bands_differ_in_volume():
    d_flat = default_definition()
    d_flat.band.profile = "flat"
    d_comfort = default_definition()
    d_comfort.band.profile = "comfort_fit"

    flat = build_ring_band(d_flat)
    comfort = build_ring_band(d_comfort)

    assert abs(flat.volume_mm3 - comfort.volume_mm3) > 0.5


def test_band_bounding_box_is_plausible():
    d = default_definition()
    band = build_ring_band(d)
    bb = band.bounding_box
    outer_r = d.ring.innerDiameter / 2 + d.band.thickness
    assert abs(bb.xmax - outer_r) < 0.05
    assert abs(bb.zmax - outer_r) < 0.05
    assert (bb.ymax - bb.ymin) <= d.band.width + 0.05


def test_stone_reference_is_valid_and_separate_from_metal():
    d = default_definition()
    stone = build_stone_reference(d)
    band = build_ring_band(d)
    assert stone.shape.Solids()
    assert stone.volume_mm3 > 0
    # stone sits strictly above the band, never overlapping the metal
    assert stone.bounding_box.zmin >= band.bounding_box.zmax - 1e-6


def test_prongs_default_count_is_six():
    d = default_definition()
    prongs = build_prongs(d)
    assert prongs.metadata["generatedCount"] == 6
    assert len(prongs.shape.Solids()) == 6


def test_prongs_four_count():
    d = default_definition()
    d.setting.prongCount = 4
    prongs = build_prongs(d)
    assert prongs.metadata["generatedCount"] == 4
    assert len(prongs.shape.Solids()) == 4


def test_basket_exists_and_has_positive_volume():
    d = default_definition()
    basket = build_basket_support(d)
    assert basket.shape.Solids()
    assert basket.volume_mm3 > 0


def test_solitaire_assembly_has_all_required_components():
    d = default_definition()
    model = build_solitaire_ring(d)
    assert set(model.components.keys()) == {
        "band",
        "stone_reference",
        "prongs",
        "basket_support",
    }
    for component in model.components.values():
        assert component.volume_mm3 > 0


def test_solitaire_assembly_metal_is_single_fused_solid_by_default():
    d = default_definition()
    model = build_solitaire_ring(d)
    assert len(model.combined_metal.Solids()) == 1
    assert model.combined_metal_volume_mm3 > 0


def test_solitaire_assembly_bounding_box_plausible():
    d = default_definition()
    model = build_solitaire_ring(d)
    bb = model.bounding_box
    assert bb.zmax > bb.zmin
    assert (bb.xmax - bb.xmin) > 0
    assert (bb.ymax - bb.ymin) > 0


def test_definition_hash_is_deterministic():
    d1 = default_definition()
    d2 = default_definition()
    m1 = build_solitaire_ring(d1)
    m2 = build_solitaire_ring(d2)
    assert m1.definition_hash == m2.definition_hash
    assert m1.combined_metal_volume_mm3 == m2.combined_metal_volume_mm3


def test_definition_hash_changes_with_input():
    d1 = default_definition()
    d2 = default_definition()
    d2.band.width = 3.0
    m1 = build_solitaire_ring(d1)
    m2 = build_solitaire_ring(d2)
    assert m1.definition_hash != m2.definition_hash


def test_four_and_six_prong_models_visibly_differ():
    d4 = default_definition()
    d4.setting.prongCount = 4
    d6 = default_definition()
    d6.setting.prongCount = 6
    m4 = build_solitaire_ring(d4)
    m6 = build_solitaire_ring(d6)
    assert m4.components["prongs"].metadata["generatedCount"] == 4
    assert m6.components["prongs"].metadata["generatedCount"] == 6
    assert abs(m4.components["prongs"].volume_mm3 - m6.components["prongs"].volume_mm3) > 0.5
