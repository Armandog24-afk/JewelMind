---
id: JM-BIBLE-450
title: Current Code Mapping
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
  - JM-BIBLE-451
implementation_status: current
professional_validation: not_required
normative: true
---

# Current Code Mapping

Mirrors the structure of
[`14-conversation/403-current-code-mapping.md`](../14-conversation/403-current-code-mapping.md).
Every file below was opened and read directly; every test count was
obtained by grepping the real file, never estimated.

## Backend: `backend/jewelmind/professional_validation/`

| File | Responsibility |
|---|---|
| `__init__.py` | Package init. |
| `schemas.py` | Every Pydantic model for this framework: `ReviewerQualification`, `ValidationScope`, `ValidationTarget`, `ValidationEvidence`, `ReviewObservation`, `ValidationDecision`, `ReviewCase`, `ReviewSession`, `ValidationRecord`, `DisagreementRecord`, `ReviewPackageFile`, `ReviewPackageManifest`, plus the `ReviewerRole`/`ValidationObjectType`/`EvidenceType`/`EvidenceQualityClass`/`ValidationDecisionType`/`ValidationStatus`/`FindingSeverity`/`DisagreementType`/`ImportOutcome` type aliases. See [`412-validation-object-model.md`](412-validation-object-model.md) through [`418-validation-decision-model.md`](418-validation-decision-model.md). |
| `errors.py` | 3 `AppError` subclasses: `ReviewPackageGenerationFailedError` (500), `ReviewRecordInvalidError` (400), `TemplateRecordInRegistryError` (500). |
| `registry.py` | `registry_path()`, `load_active_registry()`, `count_by_status()`, `count_validated()`, `validated_object_ids()` — the only code path that reads the active registry file. See [`445-professional-validation-register.md`](445-professional-validation-register.md). |
| `scope.py` | `scope_matches(scope, context)` — the one function deciding whether a candidate context falls inside a recorded `ValidationScope`. See [`415-validation-scope-model.md`](415-validation-scope-model.md). |
| `review_package.py` | `build_review_package()` and its private helpers (`_forge_registry_version`, `_readme_text`, `_review_form_text`, `_geometry_metadata`, `_forge_report`) — the real ZIP generator. See [`446-review-package-generation.md`](446-review-package-generation.md). |
| `cli.py` | `validate-review-record` CLI: `ReviewRecordCheckResult`, `validate_review_record_file()`, `validate_review_record_dict()`, `main()`. Structural validation only — never judges whether feedback is correct. |
| `versioning.py` | `classify_version_impact(validated_version, current_version) -> VersionImpact` — the real, tested implementation of [`432-validation-versioning.md`](432-validation-versioning.md)'s three-outcome model. **This file was not known to earlier agents in this Sprint** and is the key real-code discovery this batch of documents incorporates. |

## Backend: modified files outside `professional_validation/`

| File | Change this Sprint |
|---|---|
| `backend/jewelmind/api/routes.py` | Added `POST /api/professional-validation/review-package` (`review_package_route`) — fetches the live model record, calls `build_review_package()`, returns a `FileResponse` with `X-Content-SHA256`/`X-Package-Id` headers and a `BackgroundTask(_delete_file, zip_path)` cleanup, identical in shape to the existing STEP/STL export routes. |
| `backend/jewelmind/api/schemas.py` | Added `ReviewPackageRequest(_StrictRequest)`: `modelId: str`, `caseId: str = Field(min_length=1, max_length=100)`, `includeStoneReference: bool = True`. |

## Backend tests

| File | Real test count | Layer |
|---|---|---|
| `backend/tests/test_professional_validation_schemas.py` | 18 | Unit — schema construction/validation for every model in `schemas.py`. |
| `backend/tests/test_professional_validation_registry.py` | 7 | Unit — `TestZeroValidationDefault` (4), `TestNoFakeValidatedRule` (2), `TestValidationRegistryHelpers` (1). |
| `backend/tests/test_professional_validation_cli.py` | 12 | Unit — `TestValidateReviewRecord` (8, including `test_it_never_judges_whether_the_feedback_is_correct`), `TestValidateReviewRecordFile` (2), `TestCliMain` (2). |
| `backend/tests/test_professional_validation_scope.py` | 5 | Unit — `scope_matches()`, including `test_round_lost_wax_scope_does_not_cover_oval_resin_context`. |
| `backend/tests/test_professional_validation_specs.py` | 8 | Spec — validates `specs/professional-validation/v1/` schemas, examples, and test vectors against the real Pydantic models. |
| `backend/tests/test_professional_validation_versioning.py` | 6 | Unit — `TestVersionChangeImpact` (4) + `TestReviewCaseReproducibility` (2), the latter proving `definitionHash` reproducibility via `default_definition()`. |
| `backend/tests/test_review_package.py` | 14 | Integration — `TestReviewPackageGeneration` (3), `TestReviewPackageChecksums` (2), `TestReviewPackageComponents` (3), `TestStoneReferenceDocumentation` (2), `TestStaleModelProtection` (1), `TestNoLeakage` (2), `TestPackageCleansUp` (1). |
| `backend/tests/test_review_package_api.py` | 5 | API — `TestClient` round trips through `POST /api/professional-validation/review-package`, including the 404-on-unknown-model and stone-inclusion-default cases. |

**Total: 8 backend test files, 75 real test functions**, one more file
(`test_professional_validation_versioning.py`) than earlier Sprint 13
agents may have known about when writing files 410-434.

## Frontend

| File | Responsibility |
|---|---|
| `frontend/src/components/ProfessionalReviewPanel.tsx` | The Studio "Review" tab component. See [`447-studio-professional-review-mode.md`](447-studio-professional-review-mode.md) for full detail. |
| `frontend/src/components/ProfessionalReviewPanel.test.tsx` | 6 real `it(...)` cases: no-model state, stale-blocked state, blocking-validation-error state, successful generate-and-download with an entered case ID, fallback to a definition-hash-based case ID, and error-message display on a rejected `generateReviewPackage()` call. |
| `frontend/src/components/RightPanelTabs.tsx` | Registers the `'review'` `TabKey` and mounts `<ProfessionalReviewPanel />` alongside the 5 pre-existing tabs. |
| `frontend/src/api/client.ts` | `generateReviewPackage(modelId, caseId, includeStoneReference)` — POSTs to `/api/professional-validation/review-package` via the shared `downloadPost()` helper; `triggerBrowserDownload(blob, filename)` — the shared download-trigger helper this and every other export button use. |

## Machine-readable specification: `specs/professional-validation/v1/`

| Path | Contents |
|---|---|
| `README.md` | Explains the schema set and generation discipline. |
| `current-validation-registry.json` | The single active registry — `{"registryVersion": "1.0.0", "records": []}`. |
| 10 `*.schema.json` files | `review-case`, `review-observation`, `review-package-manifest`, `review-session`, `reviewer-qualification`, `reviewer`, `validation-decision`, `validation-evidence`, `validation-record`, `validation-scope`. |
| `examples/` (5 files) | `conditional-validation-example`, `conflicting-review-example`, `empty-geometry-review`, `empty-rule-review`, `rejected-validation-example` — all marked `isTemplate: true`, structurally separate from the active registry. |
| `test-vectors/` (6 files) | `disagreement-vectors`, `expiration-vectors`, `qualification-vectors`, `scope-vectors`, `status-transition-vectors`, `version-impact-vectors`. |

## Terminology-collision risk: three different things named "Validation"

This codebase now has three structurally unrelated concepts that share
the word "validation," and this Sprint adds a fourth naming surface. A
future agent (or this Sprint's own remaining work) must not conflate
them:

| Name | What it actually is | Where |
|---|---|---|
| `ValidationStatus` / `ValidationRecord` (this Sprint) | A **professional human review** outcome — `NOT_REVIEWED` through `VALIDATED_WITH_CONDITIONS`. | `backend/jewelmind/professional_validation/schemas.py` |
| `ValidationResult` / `validate_definition()` (Forge, Sprint 4+) | An **automated JDL/Forge rule check** outcome — pass/warning/error against `backend/jewelmind/validation/engine.py`. | `backend/jewelmind/validation/engine.py` |
| `ValidationBlockedError` (existing API error) | An **HTTP error** raised when Forge's automated validation blocks model generation. | `backend/jewelmind/api/errors.py` |
| `validationResults` (frontend store field) | The frontend's copy of Forge's automated results, used by `ProfessionalReviewPanel`'s own `hasBlockingValidationErrors` check. | `frontend/src/store/useProjectStore.ts` |

**Recommendation, not a rename:** always say "professional validation" or
"Forge validation" explicitly in prose, code comments, and commit
messages when the distinction matters — as this document and its
siblings in `docs/bible/15-professional-validation/` already do. No
symbol in any of the four rows above should be renamed to resolve this;
renaming a published Forge diagnostic code or error code would itself
violate FOUNDRY-GOV-010/FORGE-GOV-001. The collision is a naming risk to
stay alert to, not a defect to fix.

## Cross-references

- [`445-professional-validation-register.md`](445-professional-validation-register.md) — `registry.py`'s role in detail.
- [`446-review-package-generation.md`](446-review-package-generation.md) — `review_package.py`'s role in detail.
- [`451-validation-gap-analysis.md`](451-validation-gap-analysis.md) — what this real code inventory does *not* yet cover.
