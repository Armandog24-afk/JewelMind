from jewelmind.domain.defaults import default_definition
from jewelmind.domain.schema import JewelryDefinition


def test_default_definition_matches_spec():
    d = default_definition()
    assert d.schemaVersion == "0.1.0"
    assert d.project.name == "Solitaire Ring"
    assert d.project.units == "mm"
    assert d.jewelry.category == "ring"
    assert d.jewelry.style == "solitaire"
    assert d.ring.sizeSystem == "EU"
    assert d.ring.size == 16
    assert d.ring.innerDiameter == 17.8
    assert d.band.width == 2.4
    assert d.band.thickness == 1.8
    assert d.band.profile == "comfort_fit"
    assert d.stone.shape == "round"
    assert d.stone.diameter == 6.5
    assert d.stone.depth == 4.0
    assert d.setting.type == "prong"
    assert d.setting.prongCount == 6
    assert d.setting.prongDiameter == 1.1
    assert d.setting.prongHeight == 4.8
    assert d.setting.basketHeight == 3.5
    assert d.material.metal == "yellow_gold_18k"
    assert d.manufacturing.method == "lost_wax_casting"
    assert d.preview.meshTolerance == 0.1
    assert d.preview.angularTolerance == 0.2


def test_default_definition_round_trips_through_json():
    d = default_definition()
    dumped = d.model_dump(mode="json")
    restored = JewelryDefinition.model_validate(dumped)
    assert restored == d


def test_unknown_field_is_rejected():
    import pytest
    from pydantic import ValidationError

    data = default_definition().model_dump(mode="json")
    data["unexpectedField"] = True
    with pytest.raises(ValidationError):
        JewelryDefinition.model_validate(data)
