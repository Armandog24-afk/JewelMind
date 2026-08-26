---
id: JM-BIBLE-414
title: Reviewer Qualification Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-413
  - JM-BIBLE-415
implementation_status: current
professional_validation: not_required
normative: false
---

# Reviewer Qualification Model

`ReviewerQualification` (`backend/jewelmind/professional_validation/schemas.py`) records why a specific person is a reasonable reviewer for a specific kind of review. It is deliberately narrow: **fit-for-review, not prestige scoring** (PROVAL-GOV-004).

## Fields

| Field | Type | Notes |
|---|---|---|
| `reviewerId` | `str` | A stable identifier for the reviewer. Required. |
| `role` | `ReviewerRole` | One of the 8 values in [`413-reviewer-role-model.md`](413-reviewer-role-model.md). Required. |
| `yearsOfExperience` | `float \| None` | Optional — see below. |
| `professionalFocus` | `str` | The specific fit for a specific review (e.g. `"prong and bezel settings"`). Required. |
| `processes` | `str[]` | Manufacturing processes the reviewer works with (e.g. `["lost_wax_casting"]`). Default empty. |
| `materials` | `str[]` | Materials the reviewer works with. Default empty. |
| `softwareExperience` | `str[]` | CAD software the reviewer has real experience with (e.g. `["Rhino", "MatrixGold"]`). Default empty. |
| `relevantPortfolioOrEvidence` | `str \| None` | Optional pointer to supporting evidence of the reviewer's practice. |
| `geographicPractice` | `str \| None` | Optional — jewelry conventions can be regional or process-specific, echoing [`058-professional-validation-register.md`](../04-jewelry-domain/058-professional-validation-register.md)'s "geographic or process scope" field. |
| `qualificationNotes` | `str` | Free text. Defaults to `""`. |
| `verificationStatus` | `ReviewerVerificationStatus` | `"UNVERIFIED"` \| `"SELF_ATTESTED"` \| `"VERIFIED"`. Defaults to `"UNVERIFIED"`. |

## `yearsOfExperience` is optional, and that is deliberate

`test_professional_validation_schemas.py::TestQualificationScope::test_qualification_does_not_require_years_of_experience` proves a `ReviewerQualification` can be constructed with `yearsOfExperience` left `None` and still be a valid qualification, with `verificationStatus` defaulting to `"UNVERIFIED"`. Fitness for a specific review is judged by `professionalFocus` matching the object being reviewed, not by a tenure threshold this framework does not define and has no authority to define.

## This model does not force unnecessary personal information

There is no `email`, `phone`, `address`, or `ssn` field anywhere on `ReviewerQualification` — verified directly by `test_professional_validation_schemas.py::TestQualificationScope::test_qualification_never_requires_unnecessary_personal_data`, which dumps a constructed qualification and asserts none of those four keys appear. `ProvalModel`'s `extra="forbid"` `ConfigDict` (shared by every model in `schemas.py`) means no caller can silently smuggle such a field in either — an attempt to add one is a hard Pydantic validation error, not a warning. See also [`448-validation-security-and-privacy.md`](448-validation-security-and-privacy.md) for the broader privacy posture of this framework.

## This model does not invent a credentialing standard

There is no `certificationLevel`, no point system, and no external accreditation body referenced anywhere in `ReviewerQualification`. `verificationStatus` only ever describes *how JewelMind came to know about this reviewer's claimed experience* (unverified claim, self-attestation, or independently verified) — never a claim about how good the reviewer is at their trade. Inventing a scoring scheme here would itself violate the domain-governance rule against inventing unsourced measurements (`docs/bible/04-jewelry-domain/040-domain-governance.md`), applied here to reviewers rather than jewelry parameters.

## Relationship to `ValidationDecision.reviewerId`

A `ValidationDecision` or `ValidationRecord` (see [`418-validation-decision-model.md`](418-validation-decision-model.md)) references a reviewer only by `reviewerId` string — it does not embed the qualification inline. This keeps a reviewer's qualification as one reusable record referenced by ID across every review they participate in, rather than duplicated and potentially drifting across many decisions. There is currently no code path that cross-checks a decision's `reviewerId` against an actual stored `ReviewerQualification` record (see [`452-open-professional-validation-questions.md`](452-open-professional-validation-questions.md) for this and related open items) — `cli.py::validate_review_record_dict()` checks only that `reviewerId` is a non-empty string, not that a matching qualification exists.
