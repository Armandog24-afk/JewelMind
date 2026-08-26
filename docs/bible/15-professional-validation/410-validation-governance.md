---
id: JM-BIBLE-410
title: Validation Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
related_documents:
  - JM-BIBLE-058
  - JM-BIBLE-103
  - JM-BIBLE-411
implementation_status: current
professional_validation: not_required
normative: true
---

# Validation Governance

## PROVAL-GOV-001 through PROVAL-GOV-020

| ID | Rule |
|---|---|
| **PROVAL-GOV-001** | No professional-validation claim without a validation record. `count_validated()` (`backend/jewelmind/professional_validation/registry.py`) only ever counts real `ValidationRecord` entries loaded from the active registry file — there is no other code path in JewelMind that can assert a rule, component, or workflow is validated. |
| **PROVAL-GOV-002** | Every validation record refers to an exact object and version. `ValidationRecord.target` (`ValidationTarget`) requires `objectId` and `version` as non-optional fields — a record naming "the prong rule" with no version is not a valid `ValidationRecord`. |
| **PROVAL-GOV-003** | Every validation has explicit scope. `ValidationRecord.scope` (`ValidationScope`) always exists, even when every field within it is left unset — an empty scope is a real, honest statement ("this record claims nothing about any dimension"), never an implicit "applies everywhere." |
| **PROVAL-GOV-004** | Reviewer qualification must match review domain. `ReviewerQualification.role` is one of 8 specific roles (`413-reviewer-role-model.md`); `professionalFocus` states the specific fit for a specific review — qualification is fit-for-review, not a prestige score. |
| **PROVAL-GOV-005** | A software developer cannot self-certify jewelry-domain validity merely by implementing the system. No code path in `backend/jewelmind/` ever constructs a `ValidationRecord` from the fact that a feature was implemented, tested, or merged — a record requires a real `reviewerId` naming a person outside the implementation act itself. |
| **PROVAL-GOV-006** | Passing automated tests does not constitute professional validation. `backend/tests/test_professional_validation_registry.py::TestZeroValidationDefault` proves the active registry stays empty regardless of how many of JewelMind's 675+ automated tests pass — test success and validation status are structurally unconnected. |
| **PROVAL-GOV-007** | AI output cannot constitute professional validation. `EvidenceQualityClass` includes `AI_ASSISTED` precisely so it can be named and excluded — [`440-evidence-quality-model.md`](440-evidence-quality-model.md) states plainly that `AI_ASSISTED` and `SOFTWARE_ONLY` can never alone justify a `VALIDATED`/`VALIDATED_WITH_CONDITIONS` status. |
| **PROVAL-GOV-008** | Professional feedback cannot silently become an active Forge rule. [`435-validation-to-forge-workflow.md`](435-validation-to-forge-workflow.md) defines the required intermediate steps (engineering analysis, rule proposal, tests, ADR/RFC where required) between a review finding and a Forge rule-version change — no automation in this codebase skips them. |
| **PROVAL-GOV-009** | Accepted professional findings require implementation review and tests before changing runtime behaviour. Same workflow as PROVAL-GOV-008 — a `ValidationRecord` is data describing a review outcome; it has no execution semantics of its own and cannot itself alter `backend/jewelmind/validation/engine.py`. |
| **PROVAL-GOV-010** | Conditional acceptance must preserve its conditions. `ValidationRecord.conditions` is required to be non-empty whenever `decision == "ACCEPTED_WITH_CONDITIONS"` — enforced by `cli.py::validate_review_record_dict()` (`backend/tests/test_professional_validation_cli.py::test_accepted_with_conditions_requires_nonempty_conditions`). |
| **PROVAL-GOV-011** | Rejected findings remain in the audit history. `_handle_reject`-equivalent logic does not exist for `ValidationRecord` — a record with `decision: REJECTED`/`status: REJECTED` is a first-class, permanently retained entry, never deleted (`test_professional_validation_schemas.py::TestRejectedValidation`). |
| **PROVAL-GOV-012** | Conflicting professional reviews must remain visible. `DisagreementRecord` names both conflicting `recordIds` explicitly rather than resolving them; `test_professional_validation_schemas.py::TestDisagreementPreservation` proves two conflicting records are never merged into one. See [`430-professional-disagreement-model.md`](430-professional-disagreement-model.md). |
| **PROVAL-GOV-013** | Changes to validated semantics trigger impact analysis. [`434-implementation-change-impact.md`](434-implementation-change-impact.md) defines the CHANGE → affected validated objects → impact analysis → status downgrade → revalidation queue flow — currently zero validated objects exist, so this flow has never yet had to run, but the model exists ready for when it must. |
| **PROVAL-GOV-014** | Validation can expire. `ValidationRecord.expirationOrReviewTrigger` is a real, optional field; [`433-validation-expiration-and-revalidation.md`](433-validation-expiration-and-revalidation.md) lists real triggers — never an arbitrary annual expiration unless a reviewer states one. |
| **PROVAL-GOV-015** | Professional validation has no broader scope than the evidence supports. `scope_matches()` (`backend/jewelmind/professional_validation/scope.py`) only ever returns true when every field a scope actually constrains matches the candidate context — an unset scope field never silently narrows or broadens a match beyond what was recorded. |
| **PROVAL-GOV-016** | A manufacturing-specific validation cannot automatically apply to all manufacturing methods. `ValidationScope.manufacturingMethod`, when set, is one specific value (e.g. `lost_wax_casting`) — `test_professional_validation_scope.py::test_round_lost_wax_scope_does_not_cover_oval_resin_context` proves a resin-printing context is not covered by a casting-scoped record. |
| **PROVAL-GOV-017** | A material-specific validation cannot automatically apply to all materials. Same mechanism as PROVAL-GOV-016, via `ValidationScope.material`/`alloy`. |
| **PROVAL-GOV-018** | A reviewed example does not automatically validate every possible parameter combination. A `ValidationRecord`'s `scope` may name a `sizeRange`/`stoneDimensionRangeMm`; nothing outside a named range is asserted to be covered — see [`441-review-sampling-strategy.md`](441-review-sampling-strategy.md) for why sampling breadth (not one default ring) matters here. |
| **PROVAL-GOV-019** | Professional review records must be auditable. Every `ValidationRecord` carries `recordId`, `reviewerId`, `reviewDate`, `evidenceIds`, and `rationale` together — no field lets a decision exist without its supporting trail. See [`438-professional-review-audit-trail.md`](438-professional-review-audit-trail.md). |
| **PROVAL-GOV-020** | Professional approval does not remove the need for final case-specific manufacturing review. [`421-manufacturing-validation-process.md`](421-manufacturing-validation-process.md) and every generated review package's README state this explicitly — a `VALIDATED` record is evidence a professional reviewed something, never a manufacturing sign-off for a specific production run. |

## The three-layer distinction this governance protects

**AUTOMATED VALIDATION** (JDL/Forge/Atlas checks) is not **PROFESSIONAL VALIDATION** (evidence-based expert review) is not **CASE-SPECIFIC MANUFACTURING APPROVAL** (the final human decision for an actual production run). These three layers are never merged in code, in this documentation, or in any user-facing copy — restated in full in [`411-professional-validation-overview.md`](411-professional-validation-overview.md).

## When an ADR is required

Letting a `ValidationRecord` write directly to `backend/jewelmind/validation/engine.py` without the intermediate workflow in [`435-validation-to-forge-workflow.md`](435-validation-to-forge-workflow.md), moving the active registry to a database, or any change that violates PROVAL-GOV-001 through 020 without superseding this document first.

## When an RFC is required

A new validation object type beyond the 11 in [`412-validation-object-model.md`](412-validation-object-model.md), a new reviewer role beyond the 8 in [`413-reviewer-role-model.md`](413-reviewer-role-model.md), or a structural change to how review packages are generated; see [`451-validation-gap-analysis.md`](451-validation-gap-analysis.md).
