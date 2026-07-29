from jewelmind.domain.defaults import default_definition
from jewelmind.validation import rules as R
from jewelmind.validation.engine import has_errors, validate_definition


def ids(results):
    return {r.ruleId for r in results}


def test_default_definition_has_no_errors():
    results = validate_definition(default_definition())
    assert not has_errors(results)


def test_ring_inner_diameter_out_of_range_is_error():
    d = default_definition()
    d.ring.innerDiameter = 5
    results = validate_definition(d)
    assert R.RING_INNER_DIAMETER_RANGE in ids(results)
    assert has_errors(results)


def test_ring_size_out_of_range_is_error():
    d = default_definition()
    d.ring.size = 0.5
    results = validate_definition(d)
    assert R.RING_SIZE_RANGE in ids(results)


def test_ring_size_diameter_inconsistency_flagged():
    d = default_definition()
    d.ring.size = 16
    d.ring.innerDiameter = 25  # wildly inconsistent with size 16
    results = validate_definition(d)
    matches = [r for r in results if r.ruleId == R.RING_SIZE_DIAMETER_CONSISTENCY]
    assert matches
    assert matches[0].severity == "warning"
    # the inconsistency must not have silently rewritten either field
    assert d.ring.innerDiameter == 25
    assert d.ring.size == 16


def test_band_width_below_min_is_error():
    d = default_definition()
    d.band.width = 1.0
    results = validate_definition(d)
    assert R.BAND_WIDTH_MIN in ids(results)
    assert has_errors(results)


def test_band_width_above_max_is_warning_not_error():
    d = default_definition()
    d.band.width = 13
    results = validate_definition(d)
    matches = [r for r in results if r.ruleId == R.BAND_WIDTH_MAX]
    assert matches and matches[0].severity == "warning"
    assert not has_errors(results)


def test_band_thickness_below_min_is_error():
    d = default_definition()
    d.band.thickness = 1.0
    results = validate_definition(d)
    assert R.BAND_THICKNESS_MIN in ids(results)
    assert has_errors(results)


def test_band_thickness_warning_band():
    d = default_definition()
    d.band.thickness = 1.5
    results = validate_definition(d)
    matches = [r for r in results if r.ruleId == R.BAND_THICKNESS_MIN]
    assert matches and matches[0].severity == "warning"
    assert not has_errors(results)


def test_stone_diameter_out_of_range_is_error():
    d = default_definition()
    d.stone.diameter = 1
    results = validate_definition(d)
    assert R.STONE_DIAMETER_RANGE in ids(results)


def test_stone_depth_must_be_less_than_diameter():
    d = default_definition()
    d.stone.diameter = 6.5
    d.stone.depth = 7.0
    results = validate_definition(d)
    assert R.STONE_DEPTH_RANGE in ids(results)


def test_prong_count_invalid_is_error():
    d = default_definition()
    d.setting.prongCount = 5
    results = validate_definition(d)
    assert R.PRONG_COUNT in ids(results)


def test_prong_diameter_below_min_is_error():
    d = default_definition()
    d.setting.prongDiameter = 0.5
    results = validate_definition(d)
    assert R.PRONG_DIAMETER_MIN in ids(results)
    assert has_errors(results)


def test_prong_diameter_warning_band():
    d = default_definition()
    d.setting.prongDiameter = 0.9
    results = validate_definition(d)
    matches = [r for r in results if r.ruleId == R.PRONG_DIAMETER_MIN]
    assert matches and matches[0].severity == "warning"
    assert not has_errors(results)


def test_large_stone_with_four_prongs_warns():
    d = default_definition()
    d.stone.diameter = 9
    d.setting.prongCount = 4
    results = validate_definition(d)
    matches = [r for r in results if r.ruleId == R.PRONG_COUNT_VS_STONE_SIZE]
    assert matches and matches[0].severity == "warning"


def test_prong_height_must_exceed_basket_height():
    d = default_definition()
    d.setting.prongHeight = 3.0
    d.setting.basketHeight = 3.5
    results = validate_definition(d)
    assert R.PRONG_HEIGHT_VS_BASKET in ids(results)


def test_basket_height_must_be_positive():
    d = default_definition()
    d.setting.basketHeight = -1
    results = validate_definition(d)
    assert R.SETTING_BASKET_HEIGHT_POSITIVE in ids(results)


def test_basket_height_above_max_warns():
    d = default_definition()
    d.setting.basketHeight = 9
    d.setting.prongHeight = 10
    results = validate_definition(d)
    matches = [r for r in results if r.ruleId == R.SETTING_BASKET_HEIGHT_MAX]
    assert matches and matches[0].severity == "warning"


def test_direct_resin_printing_thin_feature_warns():
    d = default_definition()
    d.manufacturing.method = "direct_resin_printing"
    d.band.thickness = 1.6  # comfortably clears JM-BAND-002 but thin for resin
    d.band.width = 0.7
    results = validate_definition(d)
    matches = [r for r in results if r.ruleId == R.MANUFACTURING_MIN_FEATURE]
    assert any(m.parameter == "band.width" for m in matches)


def test_geometry_rejects_non_positive_outer_band():
    d = default_definition()
    d.band.thickness = 0
    results = validate_definition(d)
    assert R.GEOMETRY_OUTER_BAND_POSITIVE in ids(results)


def test_warnings_alone_do_not_block():
    d = default_definition()
    d.band.width = 13  # warning only
    results = validate_definition(d)
    assert not has_errors(results)
