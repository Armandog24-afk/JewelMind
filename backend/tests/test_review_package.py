"""REVIEW_PACKAGE_GENERATION_TEST, REVIEW_PACKAGE_CHECKSUM_TEST,
REVIEW_PACKAGE_COMPONENT_TEST, STALE_MODEL_REVIEW_PACKAGE_BLOCK_TEST — the
Sprint 13 brief's item 60 acceptance test, run against a real generated
default solitaire. Every artifact checked here is real output from the
real exporters/Forge engine, never a fabricated value.
"""

from __future__ import annotations

import hashlib
import json
import zipfile

import pytest

from jewelmind.api.errors import ModelNotFoundError
from jewelmind.domain.defaults import default_definition
from jewelmind.professional_validation.review_package import build_review_package
from jewelmind.professional_validation.schemas import ReviewPackageManifest
from jewelmind.services.model_service import ModelService


@pytest.fixture()
def service() -> ModelService:
    return ModelService()


@pytest.fixture()
def generated_record(service: ModelService):
    return service.generate(default_definition())


class TestReviewPackageGeneration:
    def test_zip_exists_and_is_non_empty(self, service, generated_record):
        zip_path, _manifest = build_review_package(
            service, generated_record.model_id, case_id="JMCASE001"
        )
        try:
            assert zip_path.exists()
            assert zip_path.stat().st_size > 0
        finally:
            zip_path.unlink(missing_ok=True)

    def test_all_required_artifacts_are_present(self, service, generated_record):
        zip_path, _manifest = build_review_package(
            service, generated_record.model_id, case_id="JMCASE001"
        )
        try:
            with zipfile.ZipFile(zip_path) as zf:
                names = set(zf.namelist())
            required = {
                "README.md",
                "review-form.md",
                "design.json",
                "technical-specification.md",
                "forge-report.json",
                "geometry-metadata.json",
                "component-manifest.json",
                "manifest.json",
                "model.step",
                "model.stl",
            }
            assert required <= names
        finally:
            zip_path.unlink(missing_ok=True)

    def test_manifest_is_valid_and_references_real_definition_hash(self, service, generated_record):
        zip_path, manifest = build_review_package(
            service, generated_record.model_id, case_id="JMCASE001"
        )
        try:
            assert isinstance(manifest, ReviewPackageManifest)
            assert manifest.sourceDefinitionHash == generated_record.generated_model.definition_hash
            assert manifest.caseId == "JMCASE001"

            with zipfile.ZipFile(zip_path) as zf:
                manifest_in_zip = json.loads(zf.read("manifest.json"))
            assert manifest_in_zip["sourceDefinitionHash"] == manifest.sourceDefinitionHash
        finally:
            zip_path.unlink(missing_ok=True)


class TestReviewPackageChecksums:
    def test_every_included_file_checksum_matches_its_real_content(self, service, generated_record):
        zip_path, manifest = build_review_package(
            service, generated_record.model_id, case_id="JMCASE001"
        )
        try:
            with zipfile.ZipFile(zip_path) as zf:
                for entry in manifest.includedFiles:
                    content = zf.read(entry.name)
                    assert hashlib.sha256(content).hexdigest() == entry.sha256
                    assert len(content) == entry.sizeBytes
        finally:
            zip_path.unlink(missing_ok=True)

    def test_checksums_dict_matches_included_files_list(self, service, generated_record):
        zip_path, manifest = build_review_package(
            service, generated_record.model_id, case_id="JMCASE001"
        )
        try:
            for entry in manifest.includedFiles:
                assert manifest.checksums[entry.name] == entry.sha256
        finally:
            zip_path.unlink(missing_ok=True)


class TestReviewPackageComponents:
    def test_component_manifest_lists_real_geometry_components(self, service, generated_record):
        zip_path, _manifest = build_review_package(
            service, generated_record.model_id, case_id="JMCASE001"
        )
        try:
            with zipfile.ZipFile(zip_path) as zf:
                component_manifest = json.loads(zf.read("component-manifest.json"))
            assert set(component_manifest.keys()) == set(
                generated_record.generated_model.components.keys()
            )
        finally:
            zip_path.unlink(missing_ok=True)

    def test_geometry_metadata_uses_real_generated_values_not_fabricated(self, service, generated_record):
        zip_path, _manifest = build_review_package(
            service, generated_record.model_id, case_id="JMCASE001"
        )
        try:
            with zipfile.ZipFile(zip_path) as zf:
                metadata = json.loads(zf.read("geometry-metadata.json"))
            assert metadata["definitionHash"] == generated_record.generated_model.definition_hash
            assert metadata["combinedMetalVolumeMm3"] == pytest.approx(
                generated_record.generated_model.combined_metal_volume_mm3
            )
        finally:
            zip_path.unlink(missing_ok=True)

    def test_forge_report_reflects_real_validation_results(self, service, generated_record):
        zip_path, _manifest = build_review_package(
            service, generated_record.model_id, case_id="JMCASE001"
        )
        try:
            with zipfile.ZipFile(zip_path) as zf:
                forge_report = json.loads(zf.read("forge-report.json"))
            assert len(forge_report["results"]) == len(generated_record.validation_results)
            assert forge_report["hasErrors"] is False
        finally:
            zip_path.unlink(missing_ok=True)


class TestStoneReferenceDocumentation:
    def test_stone_included_is_documented_in_the_readme(self, service, generated_record):
        zip_path, _manifest = build_review_package(
            service, generated_record.model_id, case_id="JMCASE001", include_stone_reference=True
        )
        try:
            with zipfile.ZipFile(zip_path) as zf:
                readme = zf.read("README.md").decode("utf-8")
            assert "IS included" in readme
        finally:
            zip_path.unlink(missing_ok=True)

    def test_stone_excluded_is_documented_in_the_readme(self, service, generated_record):
        zip_path, _manifest = build_review_package(
            service, generated_record.model_id, case_id="JMCASE001", include_stone_reference=False
        )
        try:
            with zipfile.ZipFile(zip_path) as zf:
                readme = zf.read("README.md").decode("utf-8")
            assert "NOT included" in readme
        finally:
            zip_path.unlink(missing_ok=True)


class TestStaleModelProtection:
    def test_a_model_id_with_no_live_record_is_rejected(self, service):
        # There is no independent backend concept of "stale" — model_id IS
        # the content hash of what was generated. A model_id the service
        # has never generated (or has since evicted) cannot produce a
        # package, which is exactly the guarantee the frontend's own
        # isStale gate relies on before ever sending a request.
        with pytest.raises(ModelNotFoundError):
            build_review_package(service, "not-a-real-model-id", case_id="JMCASE001")


class TestNoLeakage:
    def test_no_absolute_temp_path_leaks_into_package_contents(self, service, generated_record):
        zip_path, manifest = build_review_package(
            service, generated_record.model_id, case_id="JMCASE001"
        )
        try:
            with zipfile.ZipFile(zip_path) as zf:
                readme = zf.read("README.md").decode("utf-8")
                manifest_text = zf.read("manifest.json").decode("utf-8")
            assert str(zip_path.parent) not in readme
            assert str(zip_path.parent) not in manifest_text
            assert manifest.model_dump_json()  # never raises, no secret leaks via repr
        finally:
            zip_path.unlink(missing_ok=True)

    def test_no_api_secret_env_names_appear_in_package_contents(self, service, generated_record):
        zip_path, _manifest = build_review_package(
            service, generated_record.model_id, case_id="JMCASE001"
        )
        try:
            with zipfile.ZipFile(zip_path) as zf:
                all_text = "".join(
                    zf.read(name).decode("utf-8", errors="ignore")
                    for name in zf.namelist()
                    if not name.endswith((".step", ".stl"))
                )
            assert "ANTHROPIC_API_KEY" not in all_text
        finally:
            zip_path.unlink(missing_ok=True)


class TestPackageCleansUp:
    def test_export_temp_files_are_deleted_after_zipping(self, service, generated_record, tmp_path):
        import os

        before = set(os.listdir(os.environ.get("TEMP", "/tmp")))
        zip_path, _manifest = build_review_package(
            service, generated_record.model_id, case_id="JMCASE001"
        )
        try:
            after = set(os.listdir(os.environ.get("TEMP", "/tmp")))
            leaked_exports = [
                f for f in (after - before) if f.endswith((".step", ".stl")) and "_review_" not in f
            ]
            assert leaked_exports == []
        finally:
            zip_path.unlink(missing_ok=True)
