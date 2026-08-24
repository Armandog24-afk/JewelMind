"""Keeps specs/alchemist/v1/ honest against the real implementation.

Mirrors the approach of test_jdl_schema_examples.py, test_forge_registry.py,
and test_atlas_registry.py. Numeric comparisons involving OCCT-kernel-derived
values use a tolerance rather than exact equality (see
docs/bible/07-atlas/137-determinism-and-reproducibility.md and the Sprint 5
CI failure it documents) — this file follows the same discipline from the
start rather than reactively.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.utils.hashing import definition_hash

SPECS_DIR = Path(__file__).resolve().parents[2] / "specs" / "alchemist" / "v1"

SCHEMA_FILES = [
    "compilation-input.schema.json",
    "geometry-plan.schema.json",
    "geometry-plan-component.schema.json",
    "compilation-result.schema.json",
    "compiler-diagnostic.schema.json",
    "artifact-request.schema.json",
    "artifact-manifest.schema.json",
    "compiler-capabilities.schema.json",
]

EXAMPLE_TO_SCHEMA = {
    "default-solitaire-compilation-input.json": "compilation-input.schema.json",
    "default-solitaire-geometry-plan.json": "geometry-plan.schema.json",
    "default-solitaire-compilation-result.json": "compilation-result.schema.json",
    "failed-validation-compilation-result.json": "compilation-result.schema.json",
    "partial-preview-request.json": "artifact-request.schema.json",
    "step-export-request.json": "artifact-request.schema.json",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_alchemist_schemas_are_valid_json_schema():
    for name in SCHEMA_FILES:
        schema = _load_json(SPECS_DIR / name)
        jsonschema.Draft202012Validator.check_schema(schema)


def test_examples_pass_their_schema():
    for example_name, schema_name in EXAMPLE_TO_SCHEMA.items():
        schema = _load_json(SPECS_DIR / schema_name)
        validator = jsonschema.Draft202012Validator(schema)
        doc = _load_json(SPECS_DIR / "examples" / example_name)
        errors = list(validator.iter_errors(doc))
        assert errors == [], f"{example_name}: {errors}"


def test_normalization_vectors_match_live_implementation():
    vectors = _load_json(SPECS_DIR / "test-vectors" / "normalization-vectors.json")
    for vector in vectors["vectors"]:
        definition = JewelryDefinition.model_validate(vector["input"])
        assert definition_hash(definition) == vector["normalizedDefinitionHash"], vector["name"]


def test_proposed_compilation_hash_vectors_are_reproducible():
    """The proposed formula is not implemented in application code, but this
    test proves the checked-in vectors are at least internally consistent
    and reproducible from the documented formula itself."""
    vectors = _load_json(SPECS_DIR / "test-vectors" / "compilation-hash-vectors.json")
    for vector in vectors["vectors"]:
        payload = (
            f"{vector['definitionHash']}|{vector['compilerVersion']}|"
            f"{vector['geometryGeneratorVersion']}|{vector['forgeRuleSetVersion']}"
        ).encode()
        expected = hashlib.sha256(payload).hexdigest()[:16]
        assert expected == vector["proposedCompilationHash"]


def test_capability_vectors_match_live_schema_enums():
    from jewelmind.domain.schema import BandProfile, ManufacturingMethod, MetalType, StoneShape

    vectors = _load_json(SPECS_DIR / "test-vectors" / "capability-vectors.json")
    caps = vectors["currentCapabilities"]
    assert set(caps["supportedBandProfiles"]) == set(BandProfile.__args__)
    assert set(caps["supportedStoneShapes"]) == set(StoneShape.__args__)
    assert set(caps["supportedManufacturingContexts"]) == set(ManufacturingMethod.__args__)
    assert "yellow_gold_18k" in MetalType.__args__  # sanity check the import is meaningful
