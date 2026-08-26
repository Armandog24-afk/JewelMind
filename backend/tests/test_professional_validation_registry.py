"""ZERO_VALIDATION_DEFAULT_TEST, NO_FAKE_VALIDATED_RULE_TEST,
VALIDATION_REGISTRY_TEST — see the Sprint 13 brief, item 59: this is the
mandatory regression guard that the real active registry contains zero
validated entries until a real professional review actually happens.
"""

from __future__ import annotations

import json

import pytest

from jewelmind.professional_validation.errors import TemplateRecordInRegistryError
from jewelmind.professional_validation.registry import (
    count_by_status,
    count_validated,
    load_active_registry,
    registry_path,
    validated_object_ids,
)


class TestZeroValidationDefault:
    def test_the_real_active_registry_file_exists(self):
        assert registry_path().is_file()

    def test_the_real_active_registry_has_zero_records(self):
        records = load_active_registry()
        assert records == []

    def test_count_validated_on_the_real_registry_is_zero(self):
        records = load_active_registry()
        assert count_validated(records) == 0

    def test_no_object_id_is_reported_as_validated(self):
        records = load_active_registry()
        assert validated_object_ids(records) == []


class TestNoFakeValidatedRule:
    def test_a_template_record_in_the_registry_file_is_rejected(self, tmp_path):
        bad_registry = tmp_path / "current-validation-registry.json"
        bad_registry.write_text(
            json.dumps(
                {
                    "registryVersion": "1.0.0",
                    "records": [
                        {
                            "recordId": "JM-PV-FAKE",
                            "target": {
                                "objectType": "FORGE_RULE",
                                "objectId": "JM-PRONG-003",
                                "version": "1.0.0",
                                "description": "fake",
                            },
                            "reviewerId": "nobody",
                            "decision": "ACCEPTED",
                            "status": "VALIDATED",
                            "rationale": "fake",
                            "reviewDate": "2026-01-01",
                            "isTemplate": True,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        with pytest.raises(TemplateRecordInRegistryError):
            load_active_registry(bad_registry)

    def test_examples_directory_is_never_the_registry_path(self):
        # Structural separation: the loader's own default path must never
        # point inside examples/ — this would defeat the whole guarantee.
        assert "examples" not in str(registry_path())


class TestValidationRegistryHelpers:
    def test_count_by_status_counts_only_the_requested_status(self, tmp_path):
        registry = tmp_path / "current-validation-registry.json"
        registry.write_text(
            json.dumps(
                {
                    "registryVersion": "1.0.0",
                    "records": [
                        {
                            "recordId": "JM-PV-A",
                            "target": {
                                "objectType": "FORGE_RULE",
                                "objectId": "JM-PRONG-003",
                                "version": "1.0.0",
                                "description": "x",
                            },
                            "reviewerId": "r1",
                            "decision": "ACCEPTED",
                            "status": "VALIDATED",
                            "rationale": "x",
                            "reviewDate": "2026-01-01",
                        },
                        {
                            "recordId": "JM-PV-B",
                            "target": {
                                "objectType": "FORGE_RULE",
                                "objectId": "JM-BAND-001",
                                "version": "1.0.0",
                                "description": "x",
                            },
                            "reviewerId": "r2",
                            "decision": "REJECTED",
                            "status": "REJECTED",
                            "rationale": "x",
                            "reviewDate": "2026-01-01",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        records = load_active_registry(registry)
        assert count_by_status(records, "VALIDATED") == 1
        assert count_by_status(records, "REJECTED") == 1
        assert count_validated(records) == 1
        assert validated_object_ids(records) == ["JM-PRONG-003"]
