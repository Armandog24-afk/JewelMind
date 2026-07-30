"""Data-safety hardening tests for JewelryDefinition parsing.

These guard against malformed or hostile input reaching the geometry
pipeline: numeric-looking strings, NaN/Infinity, and unsupported schema
versions must all be rejected with a clear pydantic ValidationError rather
than silently coerced or passed through to CadQuery.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from jewelmind.domain.defaults import default_definition
from jewelmind.domain.schema import JewelryDefinition

EXAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "examples"


def _base() -> dict:
    return default_definition().model_dump(mode="json")


# -- numeric strings pretending to be numbers -------------------------------


@pytest.mark.parametrize(
    "path,value",
    [
        (("ring", "size"), "16"),
        (("ring", "innerDiameter"), "17.8"),
        (("band", "width"), "2.4"),
        (("band", "thickness"), "1.8"),
        (("stone", "diameter"), "6.5"),
        (("stone", "depth"), "4.0"),
        (("setting", "prongDiameter"), "1.1"),
        (("setting", "prongHeight"), "4.8"),
        (("setting", "basketHeight"), "3.5"),
        (("preview", "meshTolerance"), "0.1"),
        (("preview", "angularTolerance"), "0.2"),
    ],
)
def test_numeric_string_is_rejected(path, value):
    data = _base()
    node = data
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    with pytest.raises(ValidationError):
        JewelryDefinition.model_validate(data)


def test_prong_count_as_string_is_rejected():
    data = _base()
    data["setting"]["prongCount"] = "6"
    with pytest.raises(ValidationError):
        JewelryDefinition.model_validate(data)


# -- NaN / Infinity -----------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    [
        ("ring", "size"),
        ("ring", "innerDiameter"),
        ("band", "width"),
        ("band", "thickness"),
        ("stone", "diameter"),
        ("stone", "depth"),
        ("setting", "prongDiameter"),
        ("setting", "prongHeight"),
        ("setting", "basketHeight"),
        ("preview", "meshTolerance"),
        ("preview", "angularTolerance"),
    ],
)
@pytest.mark.parametrize("bad_value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_value_is_rejected(path, bad_value):
    data = _base()
    node = data
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = bad_value
    with pytest.raises(ValidationError):
        JewelryDefinition.model_validate(data)


def test_infinity_in_raw_json_text_is_rejected():
    # Python's json module (unlike strict JSON) accepts the bare literals
    # NaN / Infinity / -Infinity by default; pydantic-core must still refuse
    # them for a `float` field with allow_inf_nan=False.
    data = _base()
    data["preview"]["meshTolerance"] = 0.1
    raw = json.dumps(data)
    raw = raw.replace('"meshTolerance": 0.1', '"meshTolerance": Infinity')
    assert "Infinity" in raw
    with pytest.raises(ValidationError):
        JewelryDefinition.model_validate_json(raw)


# -- meshTolerance / angularTolerance must be finite and > 0 -----------------


@pytest.mark.parametrize("field", ["meshTolerance", "angularTolerance"])
@pytest.mark.parametrize("bad_value", [0, -0.1, float("nan"), float("inf"), float("-inf")])
def test_preview_tolerance_must_be_positive_and_finite(field, bad_value):
    data = _base()
    data["preview"][field] = bad_value
    with pytest.raises(ValidationError):
        JewelryDefinition.model_validate(data)


@pytest.mark.parametrize("field", ["meshTolerance", "angularTolerance"])
def test_preview_tolerance_accepts_small_positive_value(field):
    data = _base()
    data["preview"][field] = 0.001
    # Should not raise.
    JewelryDefinition.model_validate(data)


# -- schemaVersion -------------------------------------------------------------


@pytest.mark.parametrize("bad_version", ["0.0.9", "0.2.0", "1.0.0", "", "0.1"])
def test_unsupported_schema_version_is_rejected(bad_version):
    data = _base()
    data["schemaVersion"] = bad_version
    with pytest.raises(ValidationError):
        JewelryDefinition.model_validate(data)


def test_current_schema_version_is_accepted():
    data = _base()
    data["schemaVersion"] = "0.1.0"
    JewelryDefinition.model_validate(data)  # should not raise


# -- widening conversions that must still work (no false positives) ----------


def test_integer_json_number_is_still_accepted_for_float_field():
    # A JSON integer (no decimal point) for a float field is a legitimate,
    # lossless widening conversion and must keep working.
    data = _base()
    data["ring"]["size"] = 16
    data["band"]["width"] = 2
    d = JewelryDefinition.model_validate(data)
    assert d.ring.size == 16
    assert d.band.width == 2


def test_clear_error_structure_for_invalid_definition():
    data = _base()
    data["band"]["width"] = "not-a-number"
    with pytest.raises(ValidationError) as exc_info:
        JewelryDefinition.model_validate(data)
    errors = exc_info.value.errors()
    assert errors
    assert any(err["loc"] == ("band", "width") for err in errors)


# -- existing valid JewelryDefinition files continue to work ------------------


@pytest.mark.parametrize(
    "filename",
    ["solitaire-default.json", "solitaire-flat-four-prong.json"],
)
def test_example_definition_files_still_parse(filename):
    raw = json.loads((EXAMPLES_DIR / filename).read_text(encoding="utf-8"))
    d = JewelryDefinition.model_validate(raw)
    assert d.schemaVersion == "0.1.0"


def test_unknown_field_still_rejected_alongside_strict_mode():
    data = _base()
    data["band"]["unexpectedField"] = 1
    with pytest.raises(ValidationError):
        JewelryDefinition.model_validate(data)


def test_deepcopy_of_valid_definition_is_unaffected():
    # sanity: mutating a deep copy must not affect the original fixture
    data = _base()
    mutated = copy.deepcopy(data)
    mutated["band"]["width"] = "bad"
    JewelryDefinition.model_validate(data)  # original still valid
    with pytest.raises(ValidationError):
        JewelryDefinition.model_validate(mutated)
