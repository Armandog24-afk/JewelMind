"""Keeps specs/atlas/v1/ honest against the real geometry implementation.

Mirrors the approach of test_jdl_schema_examples.py and
test_forge_registry.py: re-run the actual JSON Schemas and the actual
geometry builders against the checked-in example/vector files, so a
future change to any of them cannot silently drift out of sync with the
Atlas specification.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from jewelmind.domain.defaults import default_definition
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring

SPECS_DIR = Path(__file__).resolve().parents[2] / "specs" / "atlas" / "v1"

SCHEMA_FILES = [
    "geometry-component.schema.json",
    "geometry-assembly.schema.json",
    "geometry-metadata.schema.json",
    "geometry-inspection-result.schema.json",
    "geometry-error.schema.json",
    "component-manifest.schema.json",
]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_atlas_schemas_are_valid_json_schema():
    for name in SCHEMA_FILES:
        schema = _load_json(SPECS_DIR / name)
        jsonschema.Draft202012Validator.check_schema(schema)


def test_component_examples_pass_schema():
    schema = _load_json(SPECS_DIR / "geometry-component.schema.json")
    validator = jsonschema.Draft202012Validator(schema)
    for name in [
        "band-component.json",
        "stone-reference-component.json",
        "prong-component.json",
        "basket-component.json",
    ]:
        doc = _load_json(SPECS_DIR / "examples" / name)
        errors = list(validator.iter_errors(doc))
        assert errors == [], f"{name}: {errors}"


def test_assembly_example_passes_schema():
    schema = _load_json(SPECS_DIR / "geometry-assembly.schema.json")
    validator = jsonschema.Draft202012Validator(schema)
    doc = _load_json(SPECS_DIR / "examples" / "solitaire-assembly.json")
    errors = list(validator.iter_errors(doc))
    assert errors == [], errors


def test_metadata_vectors_match_live_geometry_generation():
    vectors = _load_json(SPECS_DIR / "test-vectors" / "metadata-vectors.json")
    definition = default_definition()
    model = build_solitaire_ring(definition)

    assert model.definition_hash == vectors["definitionHash"]
    assert model.generator_version == vectors["generatorVersion"]
    assert model.combined_metal_volume_mm3 == vectors["totalProductionMetalVolume"]
    assert model.component_volumes() == vectors["componentVolumes"]
    assert model.bounding_box.as_dict() == vectors["aggregateBoundingBox"]
    assert model.components["prongs"].metadata["generatedCount"] == vectors["generatedProngCount"]


def test_coordinate_vectors_match_live_geometry_constants():
    from jewelmind.geometry.constants import (
        EMBED_MM,
        band_top_z,
        inner_radius,
        outer_radius,
        prong_center_radius,
    )

    vectors = _load_json(SPECS_DIR / "test-vectors" / "coordinate-vectors.json")
    definition = default_definition()
    by_name = {v["name"]: v["value"] for v in vectors["vectors"]}

    assert inner_radius(definition) == by_name["inner_radius"]
    assert outer_radius(definition) == by_name["outer_radius"]
    assert band_top_z(definition) == by_name["band_top_z"]
    assert prong_center_radius(definition) == by_name["prong_center_radius"]
    assert EMBED_MM == by_name["EMBED_MM"]
