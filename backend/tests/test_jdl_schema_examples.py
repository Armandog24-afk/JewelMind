"""Keeps specs/jdl/v1/ honest against the real implementation on every test run.

This does not re-implement JDL validation: it re-runs the actual
JSON Schema, the actual JewelryDefinition Pydantic model, and the actual
validation engine against the checked-in example and test-vector files, so
a future change to any of those three cannot silently drift out of sync
with the specification without failing CI.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
from pydantic import ValidationError

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.utils.hashing import canonical_json, definition_hash
from jewelmind.validation.engine import has_errors, validate_definition

SPECS_DIR = Path(__file__).resolve().parents[2] / "specs" / "jdl" / "v1"
EXAMPLES_DIR = SPECS_DIR / "examples"
INVALID_DIR = EXAMPLES_DIR / "invalid"

SCHEMA = json.loads((SPECS_DIR / "jdl.schema.json").read_text(encoding="utf-8"))
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)

VALID_EXAMPLE_FILES = sorted(EXAMPLES_DIR.glob("*.json"))

# (filename, expected diagnostic rule IDs) for examples rejected only at the
# semantic-validation layer (they are structurally well-formed).
SEMANTICALLY_INVALID = {
    "invalid-prong-count.json": {"JM-PRONG-001"},
    "invalid-negative-dimension.json": {"JM-BAND-001", "JM-GEOMETRY-001"},
    "invalid-basket-height.json": {"JM-SETTING-001"},
}

# Files rejected before a JewelryDefinition instance can even be constructed.
STRUCTURALLY_INVALID = {"invalid-schema-version.json", "invalid-non-finite-number.json"}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_schema_itself_is_valid_json_schema():
    jsonschema.Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("path", VALID_EXAMPLE_FILES, ids=lambda p: p.name)
def test_valid_examples_pass_schema_and_semantic_validation(path: Path):
    doc = _load_json(path)

    schema_errors = list(VALIDATOR.iter_errors(doc))
    assert schema_errors == [], f"{path.name} failed JSON Schema: {schema_errors}"

    definition = JewelryDefinition.model_validate(doc)
    results = validate_definition(definition)
    assert not has_errors(results), f"{path.name} has unexpected validation errors: {results}"


@pytest.mark.parametrize("filename", sorted(STRUCTURALLY_INVALID))
def test_structurally_invalid_examples_fail_pydantic_construction(filename: str):
    doc = _load_json(INVALID_DIR / filename)
    with pytest.raises(ValidationError):
        JewelryDefinition.model_validate(doc)


@pytest.mark.parametrize("filename", sorted(SEMANTICALLY_INVALID))
def test_semantically_invalid_examples_fail_expected_rules(filename: str):
    expected_rule_ids = SEMANTICALLY_INVALID[filename]
    doc = _load_json(INVALID_DIR / filename)

    # Semantically-invalid examples must still be structurally valid: they
    # exist specifically to prove the schema/semantic layers are separate.
    assert list(VALIDATOR.iter_errors(doc)) == []

    definition = JewelryDefinition.model_validate(doc)
    results = validate_definition(definition)
    error_rule_ids = {r.ruleId for r in results if r.severity == "error"}
    assert error_rule_ids == expected_rule_ids


def test_canonicalization_and_hash_vectors_match_implementation():
    vectors = _load_json(SPECS_DIR / "test-vectors" / "definition-hash-vectors.json")
    for vector in vectors["vectors"]:
        source_path = SPECS_DIR / vector["source"]
        doc = _load_json(source_path)
        definition = JewelryDefinition.model_validate(doc)
        assert definition_hash(definition) == vector["definitionHash"], source_path.name

    canon_vectors = _load_json(SPECS_DIR / "test-vectors" / "canonicalization-vectors.json")
    for vector in canon_vectors["vectors"]:
        if "canonicalJson" not in vector:
            continue
        source_path = SPECS_DIR / vector["source"]
        doc = _load_json(source_path)
        definition = JewelryDefinition.model_validate(doc)
        assert canonical_json(definition) == vector["canonicalJson"], source_path.name
        assert len(vector["canonicalJson"]) == vector["canonicalJsonLength"]


def test_compatibility_vectors_match_implementation():
    vectors = _load_json(SPECS_DIR / "test-vectors" / "compatibility-vectors.json")
    for vector in vectors["vectors"]:
        try:
            JewelryDefinition.model_validate({"schemaVersion": vector["schemaVersion"]})
            accepted = True
        except ValidationError:
            accepted = False
        assert accepted == vector["accepted"], vector["schemaVersion"]
