"""VALIDATION_RECORD_SCHEMA_TEST, REVIEWER_ROLE_TEST, QUALIFICATION_SCOPE_TEST,
VALIDATION_STATUS_TRANSITION_TEST, CONDITIONAL_VALIDATION_TEST,
REJECTED_VALIDATION_TEST, DISAGREEMENT_PRESERVATION_TEST — see the Sprint 13
brief's testing section. Every model here is pure data validation; none of
it asserts that a piece of professional feedback is correct.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from jewelmind.professional_validation.schemas import (
    DisagreementRecord,
    ReviewerQualification,
    ReviewObservation,
    ValidationDecision,
    ValidationRecord,
    ValidationScope,
    ValidationTarget,
)


def _target(**overrides) -> ValidationTarget:
    base = dict(
        objectType="FORGE_RULE",
        objectId="JM-PRONG-003",
        version="1.0.0",
        description="4 prongs blocked when stone diameter > 8mm.",
    )
    base.update(overrides)
    return ValidationTarget(**base)


def _record(**overrides) -> ValidationRecord:
    base = dict(
        recordId="JM-PV-001",
        target=_target(),
        reviewerId="reviewer-1",
        decision="ACCEPTED",
        status="VALIDATED",
        rationale="Matches standard bench-jeweler practice for this stone size.",
        reviewDate="2026-01-01",
    )
    base.update(overrides)
    return ValidationRecord(**base)


class TestValidationRecordSchema:
    def test_a_minimal_valid_record_round_trips(self):
        record = _record()
        again = ValidationRecord.model_validate_json(record.model_dump_json())
        assert again == record

    def test_extra_field_is_rejected(self):
        with pytest.raises(ValidationError):
            ValidationRecord.model_validate({**_record().model_dump(), "notARealField": 1})

    def test_unknown_decision_value_is_rejected(self):
        with pytest.raises(ValidationError):
            _record(decision="MAYBE")

    def test_unknown_status_value_is_rejected(self):
        with pytest.raises(ValidationError):
            _record(status="PROBABLY_FINE")

    def test_is_template_defaults_to_false(self):
        assert _record().isTemplate is False


class TestReviewerRole:
    @pytest.mark.parametrize(
        "role",
        [
            "JEWELRY_CAD_DESIGNER",
            "GOLDSMITH_BENCH_JEWELER",
            "STONE_SETTER",
            "CASTING_SPECIALIST",
            "RESIN_PRINTING_SPECIALIST",
            "JEWELRY_MANUFACTURING_ENGINEER",
            "GEMOLOGIST",
            "CAD_INTEROPERABILITY_SPECIALIST",
        ],
    )
    def test_every_documented_role_is_accepted(self, role):
        qualification = ReviewerQualification(
            reviewerId="r1", role=role, professionalFocus="testing", qualificationNotes=""
        )
        assert qualification.role == role

    def test_an_invented_role_is_rejected(self):
        with pytest.raises(ValidationError):
            ReviewerQualification(reviewerId="r1", role="MASTER_JEWELER_SUPREME", professionalFocus="x")


class TestQualificationScope:
    def test_qualification_does_not_require_years_of_experience(self):
        # A reviewer's fitness for a specific review is not prestige scoring
        # (PROVAL-GOV-004) — years-of-experience is explicitly optional.
        qualification = ReviewerQualification(
            reviewerId="r1", role="STONE_SETTER", professionalFocus="prong and bezel settings"
        )
        assert qualification.yearsOfExperience is None
        assert qualification.verificationStatus == "UNVERIFIED"

    def test_qualification_never_requires_unnecessary_personal_data(self):
        qualification = ReviewerQualification(
            reviewerId="r1", role="GEMOLOGIST", professionalFocus="stone grading"
        )
        dumped = qualification.model_dump()
        for forbidden in ("email", "phone", "address", "ssn"):
            assert forbidden not in dumped


class TestValidationStatusAndDecisionVocabulary:
    def test_pass_fail_is_not_a_valid_decision(self):
        with pytest.raises(ValidationError):
            _record(decision="PASS")
        with pytest.raises(ValidationError):
            _record(decision="FAIL")

    @pytest.mark.parametrize(
        "status",
        [
            "NOT_REVIEWED",
            "REVIEW_PLANNED",
            "UNDER_REVIEW",
            "INSUFFICIENT_EVIDENCE",
            "VALIDATED",
            "VALIDATED_WITH_CONDITIONS",
            "REJECTED",
            "REVALIDATION_REQUIRED",
            "SUPERSEDED",
        ],
    )
    def test_every_documented_status_is_accepted(self, status):
        record = _record(status=status)
        assert record.status == status


class TestConditionalValidation:
    def test_conditions_are_preserved_verbatim(self):
        record = _record(
            decision="ACCEPTED_WITH_CONDITIONS",
            status="VALIDATED_WITH_CONDITIONS",
            conditions="Accepted only for lost-wax casting in 18k gold, stone diameter <= 8mm.",
        )
        again = ValidationRecord.model_validate_json(record.model_dump_json())
        assert again.conditions == record.conditions

    def test_scope_restricts_what_the_decision_covers(self):
        decision = ValidationDecision(
            decision="ACCEPTED_WITH_CONDITIONS",
            reviewerId="r1",
            statementValidated="4-prong setting is acceptable up to 8mm round stones.",
            conditions="Round stones only, lost-wax casting only.",
            rationale="Standard bench practice for this size class.",
            scope=ValidationScope(stoneShape="round", manufacturingMethod="lost_wax_casting"),
            reviewDate="2026-01-01",
        )
        assert decision.scope.stoneShape == "round"
        # A scope that says nothing about resin printing must not be
        # assumed to cover it (PROVAL-GOV-016).
        assert decision.scope.manufacturingMethod != "direct_resin_printing"


class TestRejectedValidation:
    def test_a_rejected_record_still_carries_full_evidence_and_rationale(self):
        record = _record(
            decision="REJECTED",
            status="REJECTED",
            rationale="Prong height is insufficient for secure stone retention at this diameter.",
            evidenceIds=["evidence-1", "evidence-2"],
        )
        assert record.status == "REJECTED"
        assert record.evidenceIds == ["evidence-1", "evidence-2"]
        assert record.rationale


class TestDisagreementPreservation:
    def test_two_conflicting_records_are_never_merged_into_one(self):
        accepted = _record(
            recordId="JM-PV-001", reviewerId="reviewer-a", decision="ACCEPTED", status="VALIDATED"
        )
        rejected = _record(
            recordId="JM-PV-002",
            reviewerId="reviewer-b",
            decision="REJECTED",
            status="REJECTED",
            scope=ValidationScope(manufacturingMethod="direct_resin_printing"),
        )
        # Both real, distinct records — never averaged or collapsed into one.
        assert accepted.recordId != rejected.recordId
        assert accepted.status != rejected.status

    def test_disagreement_record_names_both_conflicting_records(self):
        disagreement = DisagreementRecord(
            disagreementId="disagreement-1",
            objectId="JM-PRONG-003",
            type="SCOPE_DIFFERENCE",
            recordIds=["JM-PV-001", "JM-PV-002"],
            description="Accepted for casting, rejected for resin printing at the same stone size.",
        )
        assert disagreement.recordIds == ["JM-PV-001", "JM-PV-002"]

    @pytest.mark.parametrize(
        "disagreement_type",
        [
            "AGREEMENT",
            "SCOPE_DIFFERENCE",
            "METHOD_DIFFERENCE",
            "PROFESSIONAL_DISAGREEMENT",
            "INSUFFICIENT_CONTEXT",
        ],
    )
    def test_every_documented_disagreement_type_is_accepted(self, disagreement_type):
        disagreement = DisagreementRecord(
            disagreementId="d1", objectId="x", type=disagreement_type, description="test"
        )
        assert disagreement.type == disagreement_type


class TestReviewObservationIsNotADecision:
    def test_an_observation_alone_does_not_change_validation_status(self):
        observation = ReviewObservation(
            observationId="obs-1",
            caseId="case-1",
            reviewerId="r1",
            target="setting.prongs",
            category="geometry",
            severity="MAJOR",
            observation="Prong tips are not tapered — would need bench finishing before setting.",
        )
        # An observation has no `decision`/`status` field at all — it is
        # structurally incapable of being mistaken for a ValidationRecord.
        assert not hasattr(observation, "decision")
        assert not hasattr(observation, "status")
