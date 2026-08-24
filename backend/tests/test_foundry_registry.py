"""Keeps specs/foundry/v1/ honest against the real implementation.

Mirrors the approach of test_jdl_schema_examples.py, test_forge_registry.py,
test_atlas_registry.py, and test_alchemist_registry.py. Numeric comparisons
involving OCCT-kernel-derived values use a tolerance rather than exact
equality (see docs/bible/07-atlas/137-determinism-and-reproducibility.md and
the Sprint 5 CI failure it documents) — this file follows the same
discipline from the start rather than reactively.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from jewelmind.domain.defaults import default_definition
from jewelmind.exporters.filenames import sanitize_filename
from jewelmind.exporters.selection import select_export_shapes
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring

SPECS_DIR = Path(__file__).resolve().parents[2] / "specs" / "foundry" / "v1"

SCHEMA_FILES = [
    "artifact-request.schema.json",
    "artifact-record.schema.json",
    "artifact-manifest.schema.json",
    "export-diagnostic.schema.json",
    "export-validation-result.schema.json",
    "export-version-fingerprint.schema.json",
]

EXAMPLE_TO_SCHEMA = {
    "step-artifact-request.json": "artifact-request.schema.json",
    "stl-artifact-request.json": "artifact-request.schema.json",
    "json-artifact-request.json": "artifact-request.schema.json",
    "specification-artifact-request.json": "artifact-request.schema.json",
    "successful-artifact-manifest.json": "artifact-manifest.schema.json",
    "partial-artifact-manifest.json": "artifact-manifest.schema.json",
    "failed-export-diagnostic.json": "export-diagnostic.schema.json",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_foundry_schemas_are_valid_json_schema():
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


def test_filename_vectors_match_live_sanitizer():
    vectors = _load_json(SPECS_DIR / "test-vectors" / "filename-vectors.json")
    for vector in vectors["vectors"]:
        kwargs = {}
        if "default" in vector:
            kwargs["default"] = vector["default"]
        result = sanitize_filename(
            vector["input"] if "input" in vector else vector["inputChar"] * vector["inputLength"],
            **kwargs,
        )
        if "output" in vector:
            assert result == vector["output"], vector
        if "outputStartsWithDot" in vector:
            assert result.startswith(".") == vector["outputStartsWithDot"], vector
        if "outputStartsWithDash" in vector:
            assert result.startswith("-") == vector["outputStartsWithDash"], vector
        if "outputLength" in vector:
            assert len(result) == vector["outputLength"], vector
        if vector.get("input") == "a:b*c?d\"e<f>g|h":
            assert not any(c in result for c in ':*?"<>|'), vector


def test_component_inclusion_vectors_match_live_default_export():
    vectors = _load_json(SPECS_DIR / "test-vectors" / "component-inclusion-vectors.json")
    definition = default_definition()
    model = build_solitaire_ring(definition)

    assert set(model.components.keys()) == {"band", "stone_reference", "prongs", "basket_support"}

    default_export_shape = select_export_shapes(model, include_stone=False)
    with_stone_shape = select_export_shapes(model, include_stone=True)

    default_solids = default_export_shape.Solids()
    with_stone_solids = with_stone_shape.Solids()
    assert len(with_stone_solids) == len(default_solids) + 1, (
        "including the stone must add exactly one solid to the exported shape, "
        "never fuse into the existing metal solid count"
    )

    real_sets = vectors["realExportedComponentSets"]
    assert set(real_sets["STEP_default"]) == {"band", "prongs", "basket_support"}
    assert set(real_sets["STEP_with_stone"]) == {"band", "prongs", "basket_support", "stone_reference"}
    assert real_sets["STL_default"] == real_sets["STEP_default"]
    assert real_sets["STL_with_stone"] == real_sets["STEP_with_stone"]


def test_artifact_integrity_vectors_are_internally_consistent():
    vectors = _load_json(SPECS_DIR / "test-vectors" / "artifact-integrity-vectors.json")
    step = vectors["step"]
    stl = vectors["stl"]

    assert stl["expectedSizeComputed"] == 84 + stl["triangleCount"] * 50 == stl["byteSize"]
    assert step["roundtripVolumeRelativeDifference"] == pytest.approx(
        abs(step["reimportedVolumeMm3"] - step["originalCombinedMetalVolumeMm3"])
        / step["originalCombinedMetalVolumeMm3"],
        rel=1e-2,
    )
    assert step["checksumIsStableAcrossRepeatedExports"] is False
    assert stl["checksumIsStableAcrossRepeatedExports"] is True


def test_version_fingerprint_vectors_have_no_unlabeled_guesses():
    vectors = _load_json(SPECS_DIR / "test-vectors" / "version-fingerprint-vectors.json")
    for vector in vectors["vectors"]:
        assert vector["status"] in {"CURRENT", "PARTIAL", "PLANNED"}, vector
        assert "howObtained" in vector, vector
