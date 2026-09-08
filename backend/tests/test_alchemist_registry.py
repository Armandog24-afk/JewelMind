"""Keeps specs/alchemist/v1/ honest against the real implementation.

Mirrors the approach of test_jdl_schema_examples.py, test_forge_registry.py,
and test_atlas_registry.py. Numeric comparisons involving OCCT-kernel-derived
values use a tolerance rather than exact equality (see
docs/bible/07-atlas/137-determinism-and-reproducibility.md and the Sprint 5
CI failure it documents) — this file follows the same discipline from the
start rather than reactively.
"""

from __future__ import annotations

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


def test_compilation_hash_vectors_are_reproducible():
    """The checked-in vectors recompute from the REAL implementation.

    Renamed from `test_proposed_...` when `compilationHash` stopped being a
    proposal (ADR-012). It now exercises the shipped function rather than a
    formula transcribed into the test — a transcription would pass even if the
    implementation diverged from it, which is the whole failure mode a vector
    file exists to prevent.

    Recomputed from each vector's own recorded components rather than compared
    against a pinned digest, because two CadQuery/OpenCascade builds
    legitimately produce different hashes for one design: that is the
    identifier's purpose, not a defect.
    """

    from jewelmind.compilation.identity import CompilationFingerprint, compilation_hash

    vectors = _load_json(SPECS_DIR / "test-vectors" / "compilation-hash-vectors.json")
    assert vectors["status"] == "IMPLEMENTED"
    assert vectors["vectors"]
    for vector in vectors["vectors"]:
        fingerprint = CompilationFingerprint(
            compilerVersion=vector["compilerVersion"],
            geometryGeneratorVersion=vector["geometryGeneratorVersion"],
            forgeRuleSetVersion=vector["forgeRuleSetVersion"],
            kernelVersion=vector["kernelVersion"],
            ocpVersion=vector["ocpVersion"],
        )
        assert compilation_hash(vector["definitionHash"], fingerprint) == (
            vector["compilationHash"]
        ), vector["case"]

    # And the vectors must actually demonstrate the distinction they exist for:
    # one design under two environments, hashing differently.
    by_case = {v["case"]: v for v in vectors["vectors"]}
    same_design = [
        v
        for v in vectors["vectors"]
        if v["definitionHash"] == by_case["default solitaire, this environment"]["definitionHash"]
    ]
    assert len({v["compilationHash"] for v in same_design}) == len(same_design)


def test_the_live_environment_reproduces_its_own_vector():
    """The first vector is this environment's real value, not a recorded one."""

    from jewelmind.compilation.environment import current_fingerprint
    from jewelmind.compilation.identity import compilation_hash

    vectors = _load_json(SPECS_DIR / "test-vectors" / "compilation-hash-vectors.json")
    live = next(
        v for v in vectors["vectors"] if v["case"] == "default solitaire, this environment"
    )
    assert compilation_hash(live["definitionHash"], current_fingerprint()) == (
        live["compilationHash"]
    )


def test_capability_vectors_match_live_schema_enums():
    from jewelmind.domain.schema import BandProfile, ManufacturingMethod, MetalType, StoneShape

    vectors = _load_json(SPECS_DIR / "test-vectors" / "capability-vectors.json")
    caps = vectors["currentCapabilities"]
    assert set(caps["supportedBandProfiles"]) == set(BandProfile.__args__)
    assert set(caps["supportedStoneShapes"]) == set(StoneShape.__args__)
    assert set(caps["supportedManufacturingContexts"]) == set(ManufacturingMethod.__args__)
    assert "yellow_gold_18k" in MetalType.__args__  # sanity check the import is meaningful
