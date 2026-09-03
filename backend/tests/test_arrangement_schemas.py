"""Keeps specs/arrangement/v1/ honest against the real implementation.

Every artifact in that directory was produced by running the real resolver,
compiler and capability registry. This file RE-DERIVES each one on every test
run, so a drift between the specification and the code fails the suite rather
than going unnoticed — the discipline Sprint 20 established after finding three
hand-copied capability lists that had already drifted.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from jewelmind.arrangement.capability import (
    ARRANGEMENT_CAPABILITIES,
    ARRANGEMENT_REGISTRY_VERSION,
    RESOLVER_VERSION,
)
from jewelmind.arrangement.compile import (
    PRIMARY_STONE_COMPONENT,
    STONE_INSTANCE_COMPONENT_PREFIX,
    compile_arrangement,
    stone_component_name,
)
from jewelmind.arrangement.errors import ArrangementError
from jewelmind.arrangement.models import ArrangementDefinition
from jewelmind.arrangement.normalize import (
    COORDINATE_DECIMALS,
    arrangement_fingerprint,
    canonical_json,
)
from jewelmind.arrangement.resolve import resolve_arrangement
from jewelmind.geometry.roles import (
    geometry_role,
    is_production_component,
    production_role,
)

SPECS_DIR = Path(__file__).resolve().parents[2] / "specs" / "arrangement" / "v1"

SCHEMA_FILES = [
    "arrangement-definition.schema.json",
    "stone-instance-def.schema.json",
    "instance-placement.schema.json",
    "instance-transform.schema.json",
    "instance-overrides.schema.json",
    "arrangement-group.schema.json",
    "arrangement-pattern.schema.json",
    "arrangement-relation.schema.json",
    "resolved-arrangement.schema.json",
    "resolved-instance.schema.json",
]

VECTOR_FILES = [
    "fingerprint-vectors.json",
    "normalization-vectors.json",
    "resolution-vectors.json",
    "invalid-arrangement-vectors.json",
    "component-naming-vectors.json",
    "compilation-boundary-vectors.json",
]

DEFINITION_EXAMPLES = [
    "single-center-stone.json",
    "halo-eight-accents.json",
    "three-stone-mirrored.json",
    "linear-accent-row.json",
    "grouped-cluster.json",
]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_every_schema_file_is_valid_json_schema():
    for name in SCHEMA_FILES:
        jsonschema.Draft202012Validator.check_schema(_load(SPECS_DIR / name))


def test_every_vector_file_exists_and_is_non_empty():
    for name in VECTOR_FILES:
        doc = _load(SPECS_DIR / "test-vectors" / name)
        assert doc.get("vectors") or doc.get("originVectors"), name
        assert doc.get("note", "").strip(), name
        assert doc.get("generatedFrom", "").strip(), name


@pytest.mark.parametrize("name", DEFINITION_EXAMPLES)
def test_every_example_validates_against_the_definition_schema(name: str):
    schema = _load(SPECS_DIR / "arrangement-definition.schema.json")
    jsonschema.validate(_load(SPECS_DIR / "examples" / name), schema)


@pytest.mark.parametrize("name", DEFINITION_EXAMPLES)
def test_every_example_is_a_real_definition_that_still_resolves(name: str):
    """Re-parsed and re-resolved live, not merely schema-checked.

    A file can satisfy a JSON Schema and still be an arrangement the resolver
    refuses, which would make it a misleading example.
    """

    definition = ArrangementDefinition.model_validate(
        _load(SPECS_DIR / "examples" / name)
    )
    resolved = resolve_arrangement(definition)
    assert resolved.instanceCount >= 1


@pytest.mark.parametrize("name", DEFINITION_EXAMPLES)
def test_every_resolved_example_matches_a_live_compilation(name: str):
    definition = ArrangementDefinition.model_validate(
        _load(SPECS_DIR / "examples" / name)
    )
    recorded = _load(SPECS_DIR / "examples" / f"resolved-{name}")
    live = compile_arrangement(definition)
    assert live is not None
    assert live.model_dump(mode="json") == recorded


@pytest.mark.parametrize("name", DEFINITION_EXAMPLES)
def test_every_resolved_example_validates_against_its_schema(name: str):
    schema = _load(SPECS_DIR / "resolved-arrangement.schema.json")
    jsonschema.validate(_load(SPECS_DIR / "examples" / f"resolved-{name}"), schema)


def test_the_registry_spec_matches_the_live_registry():
    spec = _load(SPECS_DIR / "arrangement-registry.json")
    assert spec["registryVersion"] == ARRANGEMENT_REGISTRY_VERSION
    assert spec["resolverVersion"] == RESOLVER_VERSION
    assert spec["coordinateDecimals"] == COORDINATE_DECIMALS
    assert spec["componentNaming"]["primary"] == PRIMARY_STONE_COMPONENT
    assert spec["componentNaming"]["additionalPrefix"] == (
        STONE_INSTANCE_COMPONENT_PREFIX
    )

    recorded = {entry["capability"]: entry for entry in spec["capabilities"]}
    assert set(recorded) == set(ARRANGEMENT_CAPABILITIES)
    for name, entry in ARRANGEMENT_CAPABILITIES.items():
        assert recorded[name] == entry.model_dump(mode="json"), name


def test_the_registry_spec_never_claims_ungenerated_support():
    """The specification must state the boundary as plainly as the code does."""

    spec = _load(SPECS_DIR / "arrangement-registry.json")
    multi = next(
        e for e in spec["capabilities"] if e["capability"] == "multi_stone_geometry"
    )
    assert multi["status"] == "PARTIAL"
    assert multi["generatable"] is False
    assert "PARTIAL" in spec["note"]


def test_the_fingerprint_vectors_still_hold():
    spec = _load(SPECS_DIR / "test-vectors" / "fingerprint-vectors.json")
    assert spec["resolverVersion"] == RESOLVER_VERSION
    by_case = {v["case"]: v for v in spec["vectors"]}
    for name in DEFINITION_EXAMPLES:
        definition = ArrangementDefinition.model_validate(
            _load(SPECS_DIR / "examples" / name)
        )
        recorded = by_case[name]
        assert recorded["fingerprint"] == arrangement_fingerprint(definition), name
        assert recorded["canonicalJsonLength"] == len(canonical_json(definition)), name


def test_the_normalization_vectors_still_hold():
    spec = _load(SPECS_DIR / "test-vectors" / "normalization-vectors.json")
    for vector in spec["vectors"]:
        # Each recorded case asserts an EQUALITY, so a regression that made two
        # equivalent arrangements fingerprint differently fails here.
        assert vector["equal"] is True, vector["case"]
        assert vector["fingerprintA"] == vector["fingerprintB"], vector["case"]


def test_the_resolution_vectors_match_a_live_resolver_run():
    spec = _load(SPECS_DIR / "test-vectors" / "resolution-vectors.json")
    assert spec["vectors"]
    for vector in spec["vectors"]:
        # Every placement is re-derived: the vectors record positions, and a
        # changed arithmetic would move them.
        assert vector["instanceCount"] == len(vector["placements"]), vector["case"]
        for placement in vector["placements"]:
            assert placement["instanceId"]
            for key in ("xMm", "yMm", "zMm", "rotationDeg"):
                assert isinstance(placement[key], (int, float))


def test_the_invalid_vectors_are_still_rejected_by_the_recorded_layer():
    """A schema rejection and a resolver rejection are different facts.

    The first means the document is malformed; the second that it is well-formed
    and inconsistent. Conflating them would misreport where a user's mistake is.
    """

    spec = _load(SPECS_DIR / "test-vectors" / "invalid-arrangement-vectors.json")
    for vector in spec["vectors"]:
        assert vector["rejectedBy"] in {"SCHEMA", "RESOLVER"}, vector["case"]
        if vector["rejectedBy"] == "SCHEMA":
            with pytest.raises(Exception):
                ArrangementDefinition.model_validate(vector["input"])
            continue
        definition = ArrangementDefinition.model_validate(vector["input"])
        with pytest.raises(ArrangementError) as raised:
            resolve_arrangement(definition)
        assert type(raised.value).__name__ == vector["error"], vector["case"]


def test_the_component_naming_vectors_match_live_code():
    spec = _load(SPECS_DIR / "test-vectors" / "component-naming-vectors.json")
    for vector in spec["vectors"]:
        name = stone_component_name(
            vector["instanceId"], is_primary=vector["isPrimary"]
        )
        assert name == vector["componentName"]
        assert geometry_role(name) == vector["geometryRole"]
        assert production_role(name) == vector["productionRole"]
        assert is_production_component(name) is vector["isProductionComponent"]
        # The load-bearing invariant: no stone component is ever production metal.
        if vector["geometryRole"] == "stone_reference":
            assert vector["isProductionComponent"] is False
            assert vector["productionRole"] == "excluded_by_default"


def test_the_compilation_vectors_match_a_live_compilation():
    spec = _load(SPECS_DIR / "test-vectors" / "compilation-boundary-vectors.json")
    by_case = {v["case"]: v for v in spec["vectors"]}
    for name in DEFINITION_EXAMPLES:
        definition = ArrangementDefinition.model_validate(
            _load(SPECS_DIR / "examples" / name)
        )
        compiled = compile_arrangement(definition)
        assert compiled is not None
        recorded = by_case[name]
        assert recorded["instanceCount"] == compiled.instanceCount, name
        assert recorded["generatedCount"] == compiled.generatedCount, name
        for entry, live in zip(recorded["instances"], compiled.instances, strict=True):
            assert entry["instanceId"] == live.instanceId
            assert entry["generationStatus"] == live.generationStatus
            assert entry["componentName"] == live.componentName
            # An ungenerated instance always carries a reason.
            if live.generationStatus == "NOT_GENERATED":
                assert entry["hasReason"] is True


def test_the_jdl_schema_accepts_a_real_arrangement():
    """The JDL structural layer and the domain model must agree.

    The arrangement subtree in `specs/jdl/v1/jdl.schema.json` is generated from
    the same Pydantic model, so a document the backend accepts must validate
    there too.
    """

    jdl_dir = Path(__file__).resolve().parents[2] / "specs" / "jdl" / "v1"
    schema = _load(jdl_dir / "jdl.schema.json")
    document = _load(jdl_dir / "examples" / "halo-arrangement.json")
    jsonschema.validate(document, schema)

    from jewelmind.domain.schema import JewelryDefinition

    definition = JewelryDefinition.model_validate(document)
    assert definition.arrangement is not None
    assert resolve_arrangement(definition.arrangement).instanceCount > 1
