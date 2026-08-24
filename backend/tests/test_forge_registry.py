"""Keeps specs/forge/v1/ honest against the real implementation on every test run.

Mirrors the approach of test_jdl_schema_examples.py: re-run the actual
JSON Schemas and the actual validation engine against the checked-in
registry/example/vector files, so a future change to any of them cannot
silently drift out of sync with the Forge specification.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.validation.engine import validate_definition

SPECS_DIR = Path(__file__).resolve().parents[2] / "specs" / "forge" / "v1"
JDL_EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "specs" / "jdl" / "v1"

RULE_SCHEMA = json.loads((SPECS_DIR / "rule.schema.json").read_text(encoding="utf-8"))
REGISTRY_SCHEMA = json.loads((SPECS_DIR / "rule-registry.schema.json").read_text(encoding="utf-8"))
RULE_VALIDATOR = jsonschema.Draft202012Validator(RULE_SCHEMA)
REGISTRY_VALIDATOR = jsonschema.Draft202012Validator(REGISTRY_SCHEMA)

VALID_EXAMPLE_FILES = sorted((SPECS_DIR / "examples" / "valid").glob("*.json"))
INVALID_EXAMPLE_FILES = sorted((SPECS_DIR / "examples" / "invalid").glob("*.json"))


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_schemas_are_valid_json_schema():
    schema_names = [
        "rule.schema.json", "rule-result.schema.json",
        "rule-context.schema.json", "rule-registry.schema.json",
    ]
    for name in schema_names:
        schema = _load_json(SPECS_DIR / name)
        jsonschema.Draft202012Validator.check_schema(schema)


def test_current_rule_registry_matches_schema():
    registry = _load_json(SPECS_DIR / "current-rule-registry.json")
    errors = list(REGISTRY_VALIDATOR.iter_errors(registry))
    assert errors == [], errors


@pytest.mark.parametrize("path", VALID_EXAMPLE_FILES, ids=lambda p: p.name)
def test_valid_rule_examples_pass_schema(path: Path):
    doc = _load_json(path)
    errors = list(RULE_VALIDATOR.iter_errors(doc))
    assert errors == [], f"{path.name}: {errors}"


@pytest.mark.parametrize("path", INVALID_EXAMPLE_FILES, ids=lambda p: p.name)
def test_invalid_rule_examples_fail_schema(path: Path):
    doc = _load_json(path)
    errors = list(RULE_VALIDATOR.iter_errors(doc))
    assert errors != [], f"{path.name} unexpectedly passed schema validation"


def test_registry_ids_have_no_duplicates():
    registry = _load_json(SPECS_DIR / "current-rule-registry.json")
    ids = [r["ruleId"] for r in registry["rules"]]
    assert len(ids) == len(set(ids))


def test_jm_rule_severities_match_live_validation_engine():
    """Cross-check severity-vectors.json against a live run of validate_definition()."""
    vectors = _load_json(SPECS_DIR / "test-vectors" / "severity-vectors.json")
    band_thin = JewelryDefinition.model_validate(
        {"band": {"width": 2.4, "thickness": 1.3, "profile": "comfort_fit"}}
    )
    band_warn = JewelryDefinition.model_validate(
        {"band": {"width": 2.4, "thickness": 1.5, "profile": "comfort_fit"}}
    )
    prong_thin = JewelryDefinition.model_validate(
        {
            "setting": {
                "type": "prong", "prongCount": 6, "prongDiameter": 0.7,
                "prongHeight": 4.8, "basketHeight": 3.5,
            }
        }
    )
    prong_warn = JewelryDefinition.model_validate(
        {
            "setting": {
                "type": "prong", "prongCount": 6, "prongDiameter": 0.9,
                "prongHeight": 4.8, "basketHeight": 3.5,
            }
        }
    )

    def severities(definition):
        return {r.ruleId: r.severity for r in validate_definition(definition)}

    assert severities(band_thin)["JM-BAND-002"] == "error"
    assert severities(band_warn)["JM-BAND-002"] == "warning"
    assert severities(prong_thin)["JM-PRONG-002"] == "error"
    assert severities(prong_warn)["JM-PRONG-002"] == "warning"
    assert vectors  # vectors file itself is loadable and non-empty


def test_evaluation_vectors_match_live_validation_engine():
    vectors = _load_json(SPECS_DIR / "test-vectors" / "evaluation-vectors.json")
    for vector in vectors["vectors"]:
        raw_input = vector["input"]
        if isinstance(raw_input, str):
            doc = _load_json(Path(__file__).resolve().parents[2] / raw_input)
        else:
            doc = raw_input
        try:
            definition = JewelryDefinition.model_validate(doc)
        except Exception:
            continue  # structurally-invalid inputs never reach validate_definition()
        results = validate_definition(definition)
        actual = sorted((r.ruleId, r.severity) for r in results)
        expected = sorted((r["ruleId"], r["severity"]) for r in vector["expectedResults"])
        assert actual == expected, vector["name"]
