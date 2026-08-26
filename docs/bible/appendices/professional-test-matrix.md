---
id: JM-BIBLE-A91
title: "Appendix: Professional Validation Test Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-450
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Professional Validation Test Matrix

Real counts verified by running `cd backend && .venv/Scripts/python.exe -m pytest tests/test_professional_validation_schemas.py tests/test_professional_validation_registry.py tests/test_professional_validation_cli.py tests/test_professional_validation_scope.py tests/test_professional_validation_specs.py tests/test_professional_validation_versioning.py tests/test_review_package.py tests/test_review_package_api.py --collect-only -q` (each file also collected individually to get its own count) during this appendix's own preparation, plus a direct read of `frontend/src/components/ProfessionalReviewPanel.test.tsx`.

**Note on a discrepancy found while verifying:** [`450-current-code-mapping.md`](../15-professional-validation/450-current-code-mapping.md) states `test_professional_validation_schemas.py` has 18 tests. The real, freshly collected count is **37** — `TestReviewerRole::test_every_documented_role_is_accepted` (8 `ReviewerRole` values), `TestValidationStatusAndDecisionVocabulary::test_every_documented_status_is_accepted` (9 `ValidationStatus` values), and `TestDisagreementPreservation::test_every_documented_disagreement_type_is_accepted` (5 `DisagreementType` values) are each `@pytest.mark.parametrize`d, expanding 18 distinct `def test_*` definitions into 37 collected test items (15 non-parametrized + 8 + 9 + 5 = 37). This is reported here as found, not silently reconciled to the earlier document's number — every other file's count matches `450-current-code-mapping.md` exactly.

| Test file | Layer | Real test count (verified) | Key scenarios covered |
|---|---|---|---|
| `backend/tests/test_professional_validation_schemas.py` | Unit — schema construction/validation for every model in `schemas.py` | **37** | Minimal valid `ValidationRecord` round-trips; `extra="forbid"` rejects an unknown field; unknown `decision`/`status` values rejected; `isTemplate` defaults `False`; all 8 `ReviewerRole` values accepted, an invented role rejected; `yearsOfExperience` is optional; no PII field (`email`/`phone`/`address`/`ssn`) ever appears; `PASS`/`FAIL` rejected as invalid decisions; all 9 `ValidationStatus` values accepted; conditions preserved verbatim, scope restricts what a decision covers; a rejected record still carries full evidence/rationale; two conflicting records are never merged, a `DisagreementRecord` names both, all 5 `DisagreementType` values accepted; an observation alone never changes validation status. |
| `backend/tests/test_professional_validation_registry.py` | Unit — `registry.py` | **7** | `TestZeroValidationDefault` (4): the real active registry file exists, has zero records, `count_validated()` on it is zero, no object ID is reported validated. `TestNoFakeValidatedRule` (2): a template record found in the registry file is rejected, the examples directory is never the registry path. `TestValidationRegistryHelpers` (1): `count_by_status()` counts only the requested status. |
| `backend/tests/test_professional_validation_cli.py` | Unit — `cli.py` (`validate-review-record`) | **12** | `TestValidateReviewRecord` (8): a well-formed record is valid; missing required field, empty `reviewerId`, unknown `decision`, empty `evidenceIds` entry are each invalid; `ACCEPTED_WITH_CONDITIONS` requires non-empty conditions (and is valid once supplied); the CLI never judges whether the feedback itself is correct. `TestValidateReviewRecordFile` (2): reads a real file; malformed JSON is reported, not raised. `TestCliMain` (2): exit code 0 for a valid record, exit code 1 for an invalid one. |
| `backend/tests/test_professional_validation_scope.py` | Unit — `scope.py::scope_matches()` | **5** | An empty scope matches any context; a matching context is covered; a `lost_wax_casting` scope does not cover an oval `direct_resin_printing` context; a scope field left unset never narrows the match; a context missing a constrained field does not match. |
| `backend/tests/test_professional_validation_specs.py` | Spec — `specs/professional-validation/v1/` vs. real Pydantic models | **8** | All schema files exist and are valid JSON Schema; single-record examples validate against the `validation-record` schema; the conflicting-review example validates both records; every example record is marked `isTemplate: true`; all test-vector files exist and are valid JSON; status-transition vectors only use real `ValidationStatus` values; scope vectors reproduce live via `scope_matches()`; the active registry is reproducibly empty. |
| `backend/tests/test_professional_validation_versioning.py` | Unit — `versioning.py::classify_version_impact()` and review-case reproducibility | **6** | `TestVersionChangeImpact` (4): identical version is unchanged; a minor/patch change requires review, not automatic revalidation; a major change requires revalidation; a validated rule does not silently carry forward after a major change. `TestReviewCaseReproducibility` (2): the same JDL produces the same `definitionHash` every time; a review case built from a real definition carries a real, reproducible hash. |
| `backend/tests/test_review_package.py` | Integration — `review_package.py::build_review_package()` | **14** | `TestReviewPackageGeneration` (3): the ZIP exists and is non-empty; all required artifacts are present; the manifest is valid and references the real `definitionHash`. `TestReviewPackageChecksums` (2): every included file's checksum matches its real content; the checksums dict matches the included-files list. `TestReviewPackageComponents` (3): the component manifest lists real geometry components; geometry metadata uses real generated values, never fabricated; the Forge report reflects real validation results. `TestStoneReferenceDocumentation` (2): stone-included and stone-excluded cases are each documented in the generated README. `TestStaleModelProtection` (1): a model ID with no live record is rejected. `TestNoLeakage` (2): no absolute temp path leaks into package contents; no API secret env-var names appear in package contents. `TestPackageCleansUp` (1): export temp files are deleted after zipping. |
| `backend/tests/test_review_package_api.py` | API — `POST /api/professional-validation/review-package` via `TestClient` | **5** | Returns a real ZIP; `caseId` defaults respect its `min_length`; an unknown `modelId` returns 404; `includeStoneReference` defaults to `true`; stone reference can be explicitly excluded. |
| `frontend/src/components/ProfessionalReviewPanel.test.tsx` | Frontend component | **6** | "Generate a model first" shown and the button disabled with no model; blocked with "Design changed — regenerate first" when `isStale`; blocked the same way when there are blocking Forge validation errors; a successful generate-and-download using an entered case ID (`generateReviewPackage` called with the exact case ID, `triggerBrowserDownload` called with the resulting blob); falls back to a `JMCASE-<definitionHash>`-based case ID when the field is left blank; an error message from a rejected `generateReviewPackage()` call is displayed. |

## Totals

- **Backend Professional Validation tests: 94** (37 + 7 + 12 + 5 + 8 + 6 + 14 + 5), verified by collecting all 8 files together in one `pytest --collect-only -q` run, matching the sum of the 8 individual per-file collections.
- **Frontend Professional Validation tests: 6**, the entire real count of `ProfessionalReviewPanel.test.tsx` (the only Professional Validation-specific frontend test file this Sprint adds — `RightPanelTabs.tsx`'s registration of the `'review'` tab is covered structurally by that component's own existing test suite, not duplicated here).
- **Combined: 100** real test functions/items across 9 files.

## Notes on honesty of coverage

- The one discrepancy found while verifying counts for this appendix is `test_professional_validation_schemas.py`: [`450-current-code-mapping.md`](../15-professional-validation/450-current-code-mapping.md) states 18 tests (the count of distinct `def test_*` definitions); the real, collected count is 37 once the 3 parametrized tests are expanded across their real enum-value counts (8 + 9 + 5 = 22 parametrized cases from 3 definitions, plus 15 non-parametrized definitions). This is reported as found rather than adjusted to match the earlier document.
- Every other file's real count matches `450-current-code-mapping.md` exactly: `test_professional_validation_registry.py` (7), `test_professional_validation_cli.py` (12), `test_professional_validation_scope.py` (5), `test_professional_validation_specs.py` (8), `test_professional_validation_versioning.py` (6), `test_review_package.py` (14), `test_review_package_api.py` (5), `ProfessionalReviewPanel.test.tsx` (6).

## Cross-references

- [`450-current-code-mapping.md`](../15-professional-validation/450-current-code-mapping.md) — file responsibilities and the terminology-collision table for "validation."
- [`professional-code-mapping.md`](professional-code-mapping.md) (`JM-BIBLE-A90`) — PROVAL-GOV rule → function/file → test.
