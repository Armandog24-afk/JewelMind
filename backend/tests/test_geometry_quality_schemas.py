"""GOLDEN_SCHEMA_TEST, GOLDEN_MANIFEST_TEST, and the mandated
"no professional claim" test (brief section 39). Also re-derives the test
vectors live to catch drift, mirroring test_geometry_inspection_schemas.py.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from jewelmind.geometry_quality.compare import compare_snapshot
from jewelmind.geometry_quality.registry import (
    list_golden_ids,
    load_design,
    load_golden,
    suite_dir,
)

SPECS_DIR = Path(__file__).resolve().parents[2] / "specs" / "geometry-quality" / "v1"

SCHEMA_FILES = [
    "version-fingerprint.schema.json",
    "geometry-snapshot.schema.json",
    "golden-model.schema.json",
    "geometry-diff.schema.json",
    "quality-result.schema.json",
    "golden-suite.schema.json",
]

PROHIBITED_CLAIMS = (
    "manufacturing_ready",
    "manufacturing-ready",
    "production_approved",
    "production-approved",
    "professionally_validated",
    "professionally validated",
    "industry_standard",
    "industry standard",
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_schema_files_exist_and_are_valid_json_schema():
    for name in SCHEMA_FILES:
        schema = _load_json(SPECS_DIR / name)
        jsonschema.Draft202012Validator.check_schema(schema)


def test_manifest_exists_and_validates_against_golden_suite_schema():
    schema = _load_json(SPECS_DIR / "golden-suite.schema.json")
    manifest = _load_json(suite_dir() / "manifest.json")
    jsonschema.validate(manifest, schema)


def test_manifest_has_no_duplicate_golden_ids():
    manifest = _load_json(suite_dir() / "manifest.json")
    ids = [c["goldenId"] for c in manifest["goldenIds"]]
    assert len(ids) == len(set(ids))


def test_at_least_eight_golden_cases_exist():
    assert len(list_golden_ids()) >= 8


def test_every_golden_snapshot_json_validates_against_golden_model_schema():
    schema = _load_json(SPECS_DIR / "golden-model.schema.json")
    for golden_id in list_golden_ids():
        path = suite_dir() / golden_id / "snapshot.json"
        jsonschema.validate(_load_json(path), schema)


def test_every_golden_design_json_is_a_valid_jewelry_definition():
    for golden_id in list_golden_ids():
        load_design(golden_id)  # raises if invalid


def test_every_test_vector_file_exists_and_is_non_empty():
    for name in (
        "exact-invariant-vectors.json",
        "numeric-diff-vectors.json",
        "relationship-diff-vectors.json",
        "version-mismatch-vectors.json",
        "baseline-update-vectors.json",
    ):
        data = _load_json(SPECS_DIR / "test-vectors" / name)
        assert "vectors" in data
        assert len(data["vectors"]) > 0


def test_exact_invariant_vectors_are_reproducible_live():
    vectors = _load_json(SPECS_DIR / "test-vectors" / "exact-invariant-vectors.json")["vectors"]
    golden = load_golden("SOL-001-default-solitaire")
    expected = golden.geometrySnapshot
    fp = golden.versionFingerprint

    mutated = expected.model_copy(deep=True)
    mutated.assembly.componentCount = 3
    live_diff = compare_snapshot("SOL-001-default-solitaire", expected, mutated, fp, fp)

    recorded = vectors[0]["diff"]
    assert live_diff.severity == recorded["severity"]
    assert len(live_diff.exactChanges) == len(recorded["exactChanges"])


class TestNoProfessionalClaim:
    """Golden documentation/metadata must never claim manufacturing
    readiness or professional validation (QUALITY-GOV-001)."""

    def test_no_golden_snapshot_contains_a_prohibited_claim(self):
        for golden_id in list_golden_ids():
            text = json.dumps(load_golden(golden_id).model_dump()).lower()
            for claim in PROHIBITED_CLAIMS:
                assert claim.lower() not in text, f"{golden_id} contains prohibited claim: {claim}"

    def test_manifest_contains_no_prohibited_claim(self):
        text = json.dumps(_load_json(suite_dir() / "manifest.json")).lower()
        for claim in PROHIBITED_CLAIMS:
            assert claim.lower() not in text
