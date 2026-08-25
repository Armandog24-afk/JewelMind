"""Keeps specs/studio/v1/ honest against the real frontend implementation.

Mirrors the approach of test_jdl_schema_examples.py, test_forge_registry.py,
test_atlas_registry.py, test_alchemist_registry.py, test_foundry_registry.py,
and test_vision_schemas.py. Studio's real logic lives in the frontend
(frontend/src/studio/*.ts), so this file validates schema/example
consistency only.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

SPECS_DIR = Path(__file__).resolve().parents[2] / "specs" / "studio" / "v1"

SCHEMA_FILES = [
    "studio-state.schema.json",
    "project-session.schema.json",
    "generation-state.schema.json",
    "output-state.schema.json",
    "notification.schema.json",
]

EXAMPLE_TO_SCHEMA = {
    "initial-session.json": "studio-state.schema.json",
    "valid-ready-to-generate.json": "studio-state.schema.json",
    "generated-current-model.json": "studio-state.schema.json",
    "generated-stale-model.json": "studio-state.schema.json",
    "generation-error-with-last-good.json": "studio-state.schema.json",
    "export-ready-state.json": "studio-state.schema.json",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_studio_schemas_are_valid_json_schema():
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


def test_every_example_lists_exactly_the_5_current_outputs():
    expected = {"step", "stl", "json", "specification", "presentation_png"}
    for example_name in EXAMPLE_TO_SCHEMA:
        doc = _load_json(SPECS_DIR / "examples" / example_name)
        artifacts = {row["artifact"] for row in doc["outputs"]}
        assert artifacts == expected, example_name


def test_state_transition_vectors_cover_all_7_model_states():
    vectors = _load_json(SPECS_DIR / "test-vectors" / "state-transition-vectors.json")
    covered = {v["expected"] for v in vectors["vectors"]}
    expected = {
        "NO_MODEL",
        "GENERATING_FIRST_MODEL",
        "CURRENT",
        "STALE",
        "REGENERATING",
        "FAILED_NO_MODEL",
        "FAILED_WITH_LAST_GOOD",
    }
    assert covered == expected


def test_export_eligibility_vectors_cover_all_5_states():
    vectors = _load_json(SPECS_DIR / "test-vectors" / "export-eligibility-vectors.json")
    covered = {v["expected"] for v in vectors["vectors"]}
    assert covered == {"AVAILABLE", "UNAVAILABLE", "EXPORTING", "FAILED", "STALE_BLOCKED"}
