"""Keeps specs/vision/v1/ honest against the real frontend implementation.

Mirrors the approach of test_jdl_schema_examples.py, test_forge_registry.py,
test_atlas_registry.py, test_alchemist_registry.py, and
test_foundry_registry.py. Vision's real logic lives in the frontend
(frontend/src/vision/*.ts), so this file validates schema/example
consistency only — it cannot exercise TypeScript directly, unlike the
Python-side registries in prior sprints.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

SPECS_DIR = Path(__file__).resolve().parents[2] / "specs" / "vision" / "v1"

SCHEMA_FILES = [
    "scene-state.schema.json",
    "camera-state.schema.json",
    "component-visual-state.schema.json",
    "material-presentation.schema.json",
    "render-result.schema.json",
    "image-capture-request.schema.json",
]

EXAMPLE_TO_SCHEMA = {
    "technical-view.json": "scene-state.schema.json",
    "presentation-view-yellow-gold.json": "scene-state.schema.json",
    "presentation-view-white-gold.json": "scene-state.schema.json",
    "presentation-view-rose-gold.json": "scene-state.schema.json",
    "presentation-view-platinum.json": "scene-state.schema.json",
    "presentation-view-silver.json": "scene-state.schema.json",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_vision_schemas_are_valid_json_schema():
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


def test_all_five_metals_have_a_presentation_example():
    metals = set()
    for example_name in EXAMPLE_TO_SCHEMA:
        if example_name == "technical-view.json":
            continue
        doc = _load_json(SPECS_DIR / "examples" / example_name)
        metals.add(doc["material"]["metal"])
    assert metals == {"yellow_gold_18k", "white_gold_18k", "rose_gold_18k", "platinum", "silver"}


def test_camera_vectors_target_the_backend_z_range_center():
    """The recorded target.y must equal the scene-space center of the real
    bounding box's backend-Z range, confirming the documented
    backend-Z-to-scene-Y coordinate mapping (see
    docs/bible/07-atlas/123-coordinate-system-and-orientation.md and
    docs/bible/10-vision/225-scene-graph-model.md)."""

    vectors = _load_json(SPECS_DIR / "test-vectors" / "camera-vectors.json")
    bbox = vectors["boundingBoxMm"]
    expected_target_y = (bbox["zmin"] + bbox["zmax"]) / 2
    for vector in vectors["vectors"]:
        assert vector["target"][1] == expected_target_y
    assert vectors["groundY"] == bbox["zmin"]


def test_visibility_vectors_never_mention_export_fields():
    vectors = _load_json(SPECS_DIR / "test-vectors" / "visibility-vectors.json")
    assert "definitionHash" in vectors["neverAffects"]
    assert "includeStoneReferenceInExport" in vectors["neverAffects"]
