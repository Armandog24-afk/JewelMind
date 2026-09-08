"""Persistence readiness and compilation identity (pre-Sprint-27).

Two things are proven here, and the second exists to protect the first:

1. **The compilation identity is real and correct.** `compilationHash` is
   distinct from `definitionHash`, deterministic, and sensitive to exactly the
   environment components that can change generated geometry — no more, no
   less. The cache is keyed on it.

2. **Nothing durable was introduced.** No database, no ORM, no auth, no object
   storage, and no filesystem persistence outside the temporary directories
   that already existed. The domain layer still knows nothing about storage,
   so a future persistence layer can be added without touching it.

The second set of tests is deliberately adversarial toward this very
intervention: an audit that only checks what it built would not notice a
database sneaking in.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from jewelmind.compilation.environment import (
    current_fingerprint,
    forge_rule_set_version,
    ocp_version,
)
from jewelmind.compilation.identity import (
    ABSENT,
    HASH_LENGTH,
    CompilationFingerprint,
    compilation_hash,
)
from jewelmind.domain.defaults import default_definition
from jewelmind.domain.schema import JewelryDefinition
from jewelmind.gem.models import GemIdentity
from jewelmind.services.model_service import ModelService
from jewelmind.utils.hashing import definition_hash, geometry_hash

BACKEND = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND.parent

#: Technologies this intervention must NOT have introduced. Checked against
#: real imports and real dependency declarations, not against intent.
FORBIDDEN_TECHNOLOGIES = (
    "sqlalchemy",
    "psycopg",
    "psycopg2",
    "asyncpg",
    "alembic",
    "sqlite3",
    "sqlmodel",
    "tortoise",
    "peewee",
    "pymongo",
    "motor",
    "redis",
    "supabase",
    "firebase",
    "boto3",
    "azure.storage",
    "google.cloud",
    "minio",
)


def fingerprint(**over) -> CompilationFingerprint:
    params: dict = {
        "compilerVersion": "0.1.0",
        "geometryGeneratorVersion": "0.1.0",
        "forgeRuleSetVersion": "1.0.0",
        "kernelVersion": "2.8.0",
        "ocpVersion": "7.9.3.1",
    }
    params.update(over)
    return CompilationFingerprint(**params)


def python_modules(package: Path) -> list[Path]:
    return sorted(package.rglob("*.py"))


def imported_names(path: Path) -> set[str]:
    """Every module name imported by `path`, via AST.

    Parsed rather than imported: an `import`-based check passes by accident on
    an already-cached module, and a text grep matches its own docstrings.
    """

    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.add(node.module or "")
    return names


# ---------------------------------------------- 1. definitionHash unchanged


class TestDefinitionHashUnchanged:
    """`definitionHash` is not silently replaced or altered.

    175-definition-hash-vs-compilation-hash.md is explicit that
    `compilationHash` is ADDITIVE. These tests exist so the addition cannot
    quietly redefine what every Golden baseline and stored vector already
    means.
    """

    def test_it_is_deterministic_across_repeated_computation(self):
        definition = default_definition()
        first = definition_hash(definition)
        for _ in range(5):
            assert definition_hash(definition) == first

    def test_it_is_deterministic_across_a_json_round_trip(self):
        definition = default_definition()
        restored = JewelryDefinition.model_validate(
            definition.model_dump(mode="json")
        )
        assert definition_hash(restored) == definition_hash(definition)

    def test_it_still_matches_the_checked_in_vectors(self):
        """The authoritative check: the shipped vectors are unchanged by this
        intervention."""

        specs = REPO_ROOT / "specs" / "jdl" / "v1"
        vectors = json.loads(
            (specs / "test-vectors" / "definition-hash-vectors.json").read_text(
                encoding="utf-8"
            )
        )
        for vector in vectors["vectors"]:
            document = json.loads(
                (specs / vector["source"]).read_text(encoding="utf-8")
            )
            definition = JewelryDefinition.model_validate(document)
            assert definition_hash(definition) == vector["definitionHash"]

    def test_a_semantic_only_change_still_changes_it(self):
        """Unchanged behaviour: a gem change is a different design."""

        plain = default_definition()
        gemmed = default_definition()
        gemmed.stone = gemmed.stone.model_copy(
            update={"gem": GemIdentity(gemId="corundum.ruby", origin="NATURAL")}
        )
        assert definition_hash(plain) != definition_hash(gemmed)
        # And still the same GEOMETRY, which is the Sprint 21 contract.
        assert geometry_hash(plain) == geometry_hash(gemmed)


# ------------------------------------------------- 2 & 3. compilationHash


class TestCompilationHash:
    def test_the_same_inputs_give_the_same_hash(self):
        definition = default_definition()
        base = definition_hash(definition)
        expected = compilation_hash(base, fingerprint())
        for _ in range(5):
            assert compilation_hash(base, fingerprint()) == expected

    def test_it_is_stable_across_separately_constructed_fingerprints(self):
        """Two equal fingerprints built independently must hash identically.

        This is what rules out any dependence on object identity or on the
        order a model's fields happen to be populated in.
        """

        base = definition_hash(default_definition())
        a = CompilationFingerprint(
            compilerVersion="0.1.0",
            geometryGeneratorVersion="0.1.0",
            forgeRuleSetVersion="1.0.0",
            kernelVersion="2.8.0",
            ocpVersion="7.9.3.1",
        )
        b = CompilationFingerprint(
            ocpVersion="7.9.3.1",
            kernelVersion="2.8.0",
            forgeRuleSetVersion="1.0.0",
            geometryGeneratorVersion="0.1.0",
            compilerVersion="0.1.0",
        )
        assert compilation_hash(base, a) == compilation_hash(base, b)

    def test_it_differs_from_the_definition_hash(self):
        """The whole point. If these were equal the gap would be unclosed."""

        base = definition_hash(default_definition())
        assert compilation_hash(base, fingerprint()) != base

    def test_a_different_design_gives_a_different_hash(self):
        wide = default_definition()
        wide.band = wide.band.model_copy(update={"width": 3.2})
        assert compilation_hash(
            definition_hash(default_definition()), fingerprint()
        ) != compilation_hash(definition_hash(wide), fingerprint())

    @pytest.mark.parametrize(
        "component",
        [
            "compilerVersion",
            "geometryGeneratorVersion",
            "forgeRuleSetVersion",
            "kernelVersion",
            "ocpVersion",
        ],
    )
    def test_every_fingerprint_component_changes_the_hash(self, component: str):
        """EVERY component, asserted individually.

        A component that did not change the hash would be decoration: it would
        appear in the fingerprint and be silently ignored by the identity.
        """

        base = definition_hash(default_definition())
        original = compilation_hash(base, fingerprint())
        changed = compilation_hash(base, fingerprint(**{component: "9.9.9"}))
        assert changed != original, component

    def test_an_absent_ocp_build_is_recorded_rather_than_dropped(self):
        """`None` is a fact about the environment, and hashing it as one stops
        an environment that cannot read its OCP build from colliding with one
        whose build is literally named for the placeholder."""

        base = definition_hash(default_definition())
        assert compilation_hash(base, fingerprint(ocpVersion=None)) != (
            compilation_hash(base, fingerprint(ocpVersion="7.9.3.1"))
        )
        assert fingerprint(ocpVersion=None).components()[-1] == ABSENT

    def test_the_separator_prevents_component_collisions(self):
        """`("1.0", "0")` and `("1", "0.0")` must not hash alike."""

        base = definition_hash(default_definition())
        a = compilation_hash(
            base, fingerprint(compilerVersion="1.0", geometryGeneratorVersion="0")
        )
        b = compilation_hash(
            base, fingerprint(compilerVersion="1", geometryGeneratorVersion="0.0")
        )
        assert a != b

    def test_it_uses_the_existing_truncation_scheme(self):
        """Not a new hashing convention — the same shape as
        `definition_hash()`, as 175 prescribes."""

        value = compilation_hash(definition_hash(default_definition()), fingerprint())
        assert len(value) == HASH_LENGTH == 16
        assert all(c in "0123456789abcdef" for c in value)
        assert len(definition_hash(default_definition())) == HASH_LENGTH

    def test_it_is_pure_and_kernel_free(self):
        """The pure half must stay importable without CadQuery, so Forge, the
        tests and any future persistence layer can use it freely."""

        imports = imported_names(
            BACKEND / "jewelmind" / "compilation" / "identity.py"
        )
        for name in imports:
            assert not name.startswith("cadquery"), name
            assert not name.startswith("OCP"), name
            assert not name.startswith("jewelmind.geometry"), name

    def test_the_package_init_imports_nothing(self):
        tree = ast.parse(
            (BACKEND / "jewelmind" / "compilation" / "__init__.py").read_text(
                encoding="utf-8"
            )
        )
        assert not [
            n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))
        ]


class TestCompilationHashIsNotEnvironmentDependent:
    """4. Changing something irrelevant must NOT change the identity."""

    def test_the_inspection_version_is_not_part_of_it(self):
        """Geometry Inspection is read-only by contract (INSPECT-GOV-013): it
        measures geometry and never produces it. Including it would discard
        correct cached geometry whenever a measurement changed."""

        assert "inspectionVersion" not in CompilationFingerprint.model_fields

    def test_the_jdl_schema_version_is_not_part_of_it(self):
        """Already inside `definitionHash`, because `schemaVersion` is a field
        of the document."""

        assert "jdlSchemaVersion" not in CompilationFingerprint.model_fields

    def test_the_fingerprint_is_a_closed_set(self):
        assert set(CompilationFingerprint.model_fields) == {
            "compilerVersion",
            "geometryGeneratorVersion",
            "forgeRuleSetVersion",
            "kernelVersion",
            "ocpVersion",
        }
        with pytest.raises(ValidationError):
            CompilationFingerprint.model_validate(
                {
                    "compilerVersion": "0.1.0",
                    "geometryGeneratorVersion": "0.1.0",
                    "forgeRuleSetVersion": "1.0.0",
                    "kernelVersion": "2.8.0",
                    "hostname": "someones-laptop",
                }
            )

    def test_nothing_non_deterministic_participates(self):
        """AST-scanned rather than trusted: no clock, no randomness, no process
        id, no environment variable, no object identity."""

        for name in ("identity.py", "environment.py"):
            source = (
                BACKEND / "jewelmind" / "compilation" / name
            ).read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    modules = [node.module or ""]
                else:
                    continue
                for module in modules:
                    root = module.split(".")[0]
                    assert root not in {
                        "time",
                        "datetime",
                        "random",
                        "secrets",
                        "uuid",
                        "socket",
                        "getpass",
                        "platform",
                    }, f"{name}: {module}"
            for banned in ("os.environ", "getenv", "id(", "time()", "uuid4"):
                assert banned not in source, f"{name}: {banned}"

    def test_the_live_environment_reports_real_values(self):
        """Every component must come from something actually installed."""

        live = current_fingerprint()
        assert live.forgeRuleSetVersion == forge_rule_set_version()
        assert live.forgeRuleSetVersion != "unknown", (
            "the Forge registry could not be read; the fingerprint would be "
            "hashing an error string"
        )
        assert live.ocpVersion == ocp_version()
        import cadquery as cq

        assert live.kernelVersion == cq.__version__

    def test_the_live_fingerprint_is_stable_within_a_process(self):
        assert current_fingerprint() == current_fingerprint()


# ---------------------------------------------------------- 5. cache identity


class TestCacheIdentity:
    def test_the_cache_is_not_keyed_on_the_definition_hash_alone(self):
        """ALCHEMIST-GOV-010, now enforced rather than recorded as a gap."""

        service = ModelService()
        record = service.generate(default_definition())
        assert record.model_id != record.definition_hash
        assert record.model_id == compilation_hash(
            record.definition_hash, current_fingerprint()
        )
        assert list(service._records) == [record.model_id]

    def test_the_record_carries_both_identities_separately(self):
        """Two fields so neither can silently stand in for the other."""

        record = ModelService().generate(default_definition())
        assert record.definition_hash == definition_hash(record.definition)
        assert record.compilation_fingerprint == current_fingerprint()

    def test_regenerating_the_same_design_hits_the_same_key(self):
        service = ModelService()
        first = service.generate(default_definition())
        second = service.generate(default_definition())
        assert second.model_id == first.model_id
        assert len(service._records) == 1

    def test_a_record_from_another_environment_is_not_reused(self):
        """The reuse path is subject to the SAME constraint as the key.

        Without this the compilation identity would be honoured on lookup and
        bypassed by geometry reuse — a cached model built by another kernel
        could still lend its shapes to a new definition.
        """

        service = ModelService()
        stale = service.generate(default_definition())
        # Simulate a record produced by a different kernel build.
        stale.compilation_fingerprint = stale.compilation_fingerprint.model_copy(
            update={"kernelVersion": "0.0.1-other"}
        )
        gemmed = default_definition()
        gemmed.stone = gemmed.stone.model_copy(
            update={"gem": GemIdentity(gemId="corundum.ruby", origin="NATURAL")}
        )
        assert service._find_reusable_geometry(gemmed) is None

    def test_reuse_still_works_within_one_environment(self):
        """The gate must not have disabled the Sprint 21 optimization."""

        service = ModelService()
        service.generate(default_definition())
        gemmed = default_definition()
        gemmed.stone = gemmed.stone.model_copy(
            update={"gem": GemIdentity(gemId="corundum.ruby", origin="NATURAL")}
        )
        assert service._find_reusable_geometry(gemmed) is not None

    def test_the_api_reports_both_identities(self):
        from fastapi.testclient import TestClient

        from jewelmind.api.app import create_app

        client = TestClient(create_app(), raise_server_exceptions=False)
        body = client.post(
            "/api/models/generate",
            json=default_definition().model_dump(mode="json"),
        ).json()
        assert body["definitionHash"] == definition_hash(default_definition())
        assert body["compilationHash"] == body["modelId"]
        assert body["compilationHash"] != body["definitionHash"]

        metadata = client.get(f"/api/models/{body['modelId']}/metadata").json()
        assert metadata["compilationHash"] == body["compilationHash"]
        assert metadata["definitionHash"] == body["definitionHash"]


# ------------------------------------------------- 6. nothing was persisted


class TestNothingIsPersisted:
    def test_a_fresh_service_starts_empty(self):
        """6. A restart introduces no persistence.

        A new `ModelService` is what a restarted process has: if anything had
        been written to disk or to a store, the cache would come back
        populated.
        """

        first = ModelService()
        record = first.generate(default_definition())
        assert len(first._records) == 1

        restarted = ModelService()
        assert len(restarted._records) == 0
        from jewelmind.api.errors import ModelNotFoundError

        with pytest.raises(ModelNotFoundError):
            restarted.get_record(record.model_id)

    def test_the_cache_remains_in_memory_only(self):
        """The store is an `OrderedDict` in the instance, nothing more."""

        from collections import OrderedDict

        service = ModelService()
        assert isinstance(service._records, OrderedDict)

    def test_generation_writes_only_inside_a_temp_directory(self):
        """The only bytes written are the preview meshes, in a
        `tempfile`-owned directory that is cleaned up on eviction and at exit
        — the behaviour that already existed."""

        import tempfile

        service = ModelService()
        record = service.generate(default_definition())
        temp_root = Path(tempfile.gettempdir()).resolve()
        assert record.temp_dir.resolve().is_relative_to(temp_root)
        assert not record.temp_dir.resolve().is_relative_to(REPO_ROOT.resolve())


# --------------------------------------- 7. the boundary the future relies on


class TestPersistenceBoundary:
    """The domain and CAD layers must stay free of storage concerns, so a
    future persistence layer can be added without touching them.

    Asserted over the real package tree rather than over a list of modules
    someone remembered to add.
    """

    DOMAIN_PACKAGES = (
        "domain",
        "stone",
        "gem",
        "arrangement",
        "family",
        "halo",
        "pave",
        "setting",
        "geometry",
        "validation",
        "compilation",
        "jewelry_category",
        "ring",
    )

    def test_no_domain_or_cad_module_imports_a_database_technology(self):
        offenders: list[str] = []
        for package in self.DOMAIN_PACKAGES:
            for path in python_modules(BACKEND / "jewelmind" / package):
                for name in imported_names(path):
                    root = name.split(".")[0]
                    if root in FORBIDDEN_TECHNOLOGIES or name in FORBIDDEN_TECHNOLOGIES:
                        offenders.append(f"{path.name}: {name}")
        assert not offenders, offenders

    def test_no_module_anywhere_in_the_backend_imports_one(self):
        """Wider than the domain layer on purpose: this intervention must not
        have introduced a database ANYWHERE, including in the service and API
        layers."""

        offenders: list[str] = []
        for path in python_modules(BACKEND / "jewelmind"):
            for name in imported_names(path):
                root = name.split(".")[0]
                if root in FORBIDDEN_TECHNOLOGIES or name in FORBIDDEN_TECHNOLOGIES:
                    offenders.append(f"{path.relative_to(BACKEND)}: {name}")
        assert not offenders, offenders

    def test_no_database_dependency_was_declared(self):
        requirements = (BACKEND / "requirements.txt").read_text(encoding="utf-8").lower()
        for technology in FORBIDDEN_TECHNOLOGIES:
            assert technology not in requirements, technology

    def test_no_auth_dependency_or_module_was_introduced(self):
        requirements = (BACKEND / "requirements.txt").read_text(encoding="utf-8").lower()
        for technology in ("python-jose", "passlib", "authlib", "bcrypt", "pyjwt"):
            assert technology not in requirements, technology
        assert not list((BACKEND / "jewelmind").rglob("auth*.py"))

    def test_the_domain_layer_does_not_read_or_write_the_filesystem(self):
        """A domain model that opened a file would already be a persistence
        layer, whatever it was called.

        `stone/importing.py` is the deliberate exception and the reason this
        test names it: it is the ASSET STORE ABSTRACTION, whose whole purpose
        is to keep filesystem access behind an interface. It is tested
        separately below.
        """

        allowed = {"importing.py"}
        offenders: list[str] = []
        for package in ("domain", "stone", "gem", "arrangement", "family", "halo", "pave"):
            for path in python_modules(BACKEND / "jewelmind" / package):
                if path.name in allowed:
                    continue
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                        if node.func.id == "open":
                            offenders.append(f"{path.name}: open()")
                    if isinstance(node, ast.Attribute) and node.attr in {
                        "write_text",
                        "write_bytes",
                        "read_text",
                        "read_bytes",
                    }:
                        offenders.append(f"{path.name}: {node.attr}")
        assert not offenders, offenders

    def test_the_asset_store_is_an_interface_with_a_filesystem_implementation(self):
        """6 (brief): the existing abstraction is sufficient and untouched.

        The Stone System declares only what it actually needs of a store —
        `resolve()`, the READ side — and the filesystem class implements it.
        That the protocol does NOT declare `store()` is correct rather than
        incomplete: nothing in the domain writes an asset, and a protocol
        method no consumer calls would be speculative surface. Writing belongs
        to a future upload path that does not exist.

        Nothing here needed changing, so nothing was changed.
        """

        from jewelmind.stone import importing

        assert hasattr(importing, "StoneAssetStore")
        assert hasattr(importing, "FilesystemStoneAssetStore")
        assert hasattr(importing.StoneAssetStore, "resolve")
        # The concrete implementation may do more than the domain asks of it.
        for method in ("store", "resolve"):
            assert hasattr(importing.FilesystemStoneAssetStore, method), method

        source = (BACKEND / "jewelmind" / "stone" / "importing.py").read_text(
            encoding="utf-8"
        )
        protocol = next(
            node
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.ClassDef) and node.name == "StoneAssetStore"
        )
        protocol_source = ast.get_source_segment(source, protocol)
        assert protocol_source is not None
        # The interface performs no I/O of its own: only the implementation
        # knows how bytes are stored.
        for io_call in ("open(", "write_bytes", "read_bytes", "mkdir", "glob"):
            assert io_call not in protocol_source, io_call

    def test_the_asset_store_protocol_returns_a_path_today(self):
        """A RECORDED OBSERVATION, deliberately not a change.

        `StoneAssetStore.resolve()` is typed to return `pathlib.Path`, which is
        a filesystem type appearing in an otherwise storage-agnostic interface.
        It is honest for today — the only implementation is a filesystem one,
        and the importer hands the path to a CAD reader that wants a file — but
        an object-storage implementation would have to materialize a local file
        to satisfy it.

        Asserted rather than fixed because widening the return type has no
        consumer yet: §6 of this intervention says not to modify a sufficient
        abstraction, and inventing a `BinaryIO`/bytes contract for a caller
        that does not exist would be the speculative abstraction §2 forbids.
        This test exists so the next sprint that adds a second implementation
        finds the constraint stated rather than discovering it.
        """

        import inspect
        from pathlib import Path as _Path

        from jewelmind.stone import importing

        signature = inspect.signature(importing.StoneAssetStore.resolve)
        assert signature.return_annotation in {_Path, "Path"}

    def test_the_domain_models_are_serializable_without_any_adapter(self):
        """5 (brief): the current model could be persisted later without
        touching the geometric domain.

        Not a claim that persistence exists — a check that nothing blocks it:
        every domain model round-trips through plain JSON, which is the only
        property a future store needs from them.
        """

        definition = default_definition()
        payload = definition.model_dump(mode="json")
        assert json.loads(json.dumps(payload)) == payload
        restored = JewelryDefinition.model_validate(json.loads(json.dumps(payload)))
        assert definition_hash(restored) == definition_hash(definition)

        for block in ("stone", "setting", "band", "ring", "material"):
            assert block in payload

        # And the optional multi-stone subsystems, which a future project row
        # would have to carry verbatim.
        for block in ("arrangement", "family", "halo", "pave"):
            assert block in payload, block

    def test_a_generated_model_is_not_expected_to_be_serializable(self):
        """The honest counterpart: `GeneratedModel` holds kernel objects and is
        NOT a persistence candidate.

        Recording this stops a future sprint from assuming it could store one.
        Geometry is reproduced from the definition plus the compilation
        fingerprint — which is exactly why `compilationHash` had to exist
        first.
        """

        from jewelmind.geometry.model import GeneratedModel

        assert not hasattr(GeneratedModel, "model_dump_json")
        record = ModelService().generate(default_definition())
        with pytest.raises(TypeError):
            json.dumps(record.generated_model.components)
