"""Tests for `validate-review-record` — structural validation only.

Never asserts that a piece of professional feedback is correct, only that
the record naming/referencing it is well-formed (see item 49 of the
Sprint 13 brief).
"""

from __future__ import annotations

import json

from jewelmind.professional_validation.cli import (
    main,
    validate_review_record_dict,
    validate_review_record_file,
)


def _valid_record() -> dict:
    return {
        "recordId": "JM-PV-001",
        "target": {
            "objectType": "FORGE_RULE",
            "objectId": "JM-PRONG-003",
            "version": "1.0.0",
            "description": "4 prongs blocked when stone diameter > 8mm.",
        },
        "reviewerId": "reviewer-1",
        "decision": "ACCEPTED",
        "status": "VALIDATED",
        "rationale": "Consistent with standard bench practice.",
        "reviewDate": "2026-01-01",
        "evidenceIds": ["evidence-1"],
    }


class TestValidateReviewRecord:
    def test_a_well_formed_record_is_valid(self):
        result = validate_review_record_dict(_valid_record())
        assert result.valid
        assert result.errors == []

    def test_missing_required_field_is_invalid(self):
        raw = _valid_record()
        del raw["reviewDate"]
        result = validate_review_record_dict(raw)
        assert not result.valid
        assert any("reviewDate" in e for e in result.errors)

    def test_empty_reviewer_id_is_invalid(self):
        raw = _valid_record()
        raw["reviewerId"] = "   "
        result = validate_review_record_dict(raw)
        assert not result.valid
        assert any("reviewerId" in e for e in result.errors)

    def test_unknown_decision_value_is_invalid(self):
        raw = _valid_record()
        raw["decision"] = "MAYBE"
        result = validate_review_record_dict(raw)
        assert not result.valid

    def test_empty_evidence_id_entry_is_invalid(self):
        raw = _valid_record()
        raw["evidenceIds"] = [""]
        result = validate_review_record_dict(raw)
        assert not result.valid
        assert any("evidenceIds" in e for e in result.errors)

    def test_accepted_with_conditions_requires_nonempty_conditions(self):
        raw = _valid_record()
        raw["decision"] = "ACCEPTED_WITH_CONDITIONS"
        raw["status"] = "VALIDATED_WITH_CONDITIONS"
        result = validate_review_record_dict(raw)
        assert not result.valid
        assert any("PROVAL-GOV-010" in e for e in result.errors)

    def test_accepted_with_conditions_and_real_conditions_is_valid(self):
        raw = _valid_record()
        raw["decision"] = "ACCEPTED_WITH_CONDITIONS"
        raw["status"] = "VALIDATED_WITH_CONDITIONS"
        raw["conditions"] = "Lost-wax casting only, round stones <= 8mm."
        result = validate_review_record_dict(raw)
        assert result.valid

    def test_it_never_judges_whether_the_feedback_is_correct(self):
        # A record rejecting a rule is exactly as structurally valid as one
        # accepting it — this tool has no opinion on jewelry correctness.
        raw = _valid_record()
        raw["decision"] = "REJECTED"
        raw["status"] = "REJECTED"
        result = validate_review_record_dict(raw)
        assert result.valid


class TestValidateReviewRecordFile:
    def test_reads_a_real_file(self, tmp_path):
        path = tmp_path / "record.json"
        path.write_text(json.dumps(_valid_record()), encoding="utf-8")
        result = validate_review_record_file(path)
        assert result.valid

    def test_malformed_json_is_reported_not_raised(self, tmp_path):
        path = tmp_path / "record.json"
        path.write_text("{not json", encoding="utf-8")
        result = validate_review_record_file(path)
        assert not result.valid
        assert result.errors


class TestCliMain:
    def test_exit_code_0_for_a_valid_record(self, tmp_path, capsys):
        path = tmp_path / "record.json"
        path.write_text(json.dumps(_valid_record()), encoding="utf-8")
        assert main([str(path)]) == 0
        assert "OK" in capsys.readouterr().out

    def test_exit_code_1_for_an_invalid_record(self, tmp_path, capsys):
        raw = _valid_record()
        del raw["reviewerId"]
        path = tmp_path / "record.json"
        path.write_text(json.dumps(raw), encoding="utf-8")
        assert main([str(path)]) == 1
        assert "INVALID" in capsys.readouterr().err
