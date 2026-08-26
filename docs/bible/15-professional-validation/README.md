---
id: JM-BIBLE-PROVAL-README
title: Professional Validation Framework v1 — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-DOMAIN-README
  - JM-BIBLE-FORGE-README
related_documents:
  - JM-BIBLE-README
  - JM-BIBLE-058
  - JM-BIBLE-103
implementation_status: current
professional_validation: not_required
normative: false
---

# Professional Validation Framework v1 — Index

This is **Sprint 13** of the Technical Bible: **Professional Validation Framework v1**. Every prior sprint has been honest that JewelMind's jewelry-domain rules, geometry, and manufacturing-context assumptions are **preliminary software assumptions**, never professionally validated. This Sprint does not change that fact — it builds the infrastructure that would let it change, later, for real: a controlled system through which a real jewelry CAD designer, goldsmith, stone setter, casting specialist, or CAD-interoperability specialist can review JewelMind rigorously and have that review captured as structured, versioned, auditable evidence.

**Read this README, then [`410-validation-governance.md`](410-validation-governance.md), before changing anything in `backend/jewelmind/professional_validation/` or claiming any rule, geometry component, or workflow is professionally validated.**

## The fundamental principle

> Professional validation is versioned evidence. It is never a generic label.

INVALID: *"1.6 mm band thickness is professionally validated."*

VALID CONCEPTUAL FORM: *"Forge rule JM-XYZ version 1.2.0 was reviewed on YYYY-MM-DD by reviewer R under lost-wax casting scope for a specified alloy/process context and accepted with conditions C."*

A validation statement must name a precise object, an exact version, a defined scope, a qualified reviewer, a date, evidence, conditions (if any), and a decision — see [`412-validation-object-model.md`](412-validation-object-model.md) through [`418-validation-decision-model.md`](418-validation-decision-model.md).

## Where Professional Validation sits

```
             PROFESSIONAL REVIEW
                     │
                     ↓
             VALIDATION EVIDENCE
                     │
                     ↓
       PROFESSIONAL VALIDATION SYSTEM     (this Sprint)
           │                 │
           ↓                 ↓
         FORGE             ATLAS
      rule status        geometry evidence
           │                 │
           └────────┬────────┘
                    ↓
                ALCHEMIST
                    ↓
                 STUDIO
```

This framework does **not** directly control geometry or Forge rule behavior. It supplies validated knowledge, scoped evidence, review status, acceptance conditions, and review requirements — Forge and every other system consume accepted, versioned professional knowledge only through a controlled implementation change (see [`435-validation-to-forge-workflow.md`](435-validation-to-forge-workflow.md) and [`436-validation-to-atlas-workflow.md`](436-validation-to-atlas-workflow.md)). A professional finding never mutates runtime behavior automatically.

## Claude Code is not a jewelry professional reviewer

Stated as plainly as possible, because it is the single most important constraint on this entire Sprint: an AI agent's judgment that a rule "seems reasonable" is not evidence, is never recorded as a `ValidationRecord`, and can never move a rule's status toward `VALIDATED`. Neither can a passing automated test, a successful geometry generation, a successful STEP/STL export, or an internet source that merely mentions something similar (PROVAL-GOV-006/007, [`410-validation-governance.md`](410-validation-governance.md)).

## Current state: zero professional validation

`specs/professional-validation/v1/current-validation-registry.json` contains **zero records**. This is verified — not just claimed — by `backend/tests/test_professional_validation_registry.py::TestZeroValidationDefault` and the mandatory regression guard `test_count_validated_on_the_real_registry_is_zero`. Every rule in `specs/forge/v1/current-rule-registry.json` remains `professionalValidationStatus: preliminary` (16 jewelry-domain rules) or `not_required` (5 schema/system/geometry-inspection/export rules) — see [`443-current-preliminary-rule-review-plan.md`](443-current-preliminary-rule-review-plan.md).

## Reading order

1. [`410-validation-governance.md`](410-validation-governance.md) — 20 non-negotiable rules (PROVAL-GOV-001 through 020).
2. [`411-professional-validation-overview.md`](411-professional-validation-overview.md), [`412-validation-object-model.md`](412-validation-object-model.md).
3. Reviewer model: [`413-reviewer-role-model.md`](413-reviewer-role-model.md), [`414-reviewer-qualification-model.md`](414-reviewer-qualification-model.md).
4. Scope and evidence: [`415-validation-scope-model.md`](415-validation-scope-model.md), [`416-review-session-model.md`](416-review-session-model.md), [`417-review-evidence-model.md`](417-review-evidence-model.md), [`418-validation-decision-model.md`](418-validation-decision-model.md).
5. Review processes: [`419-rule-validation-process.md`](419-rule-validation-process.md), [`420-geometry-validation-process.md`](420-geometry-validation-process.md), [`421-manufacturing-validation-process.md`](421-manufacturing-validation-process.md), [`422-setting-validation-process.md`](422-setting-validation-process.md), [`423-material-validation-process.md`](423-material-validation-process.md), [`424-cad-workflow-validation-process.md`](424-cad-workflow-validation-process.md).
6. Cases and packages: [`425-review-case-model.md`](425-review-case-model.md), [`426-review-package-contract.md`](426-review-package-contract.md), [`427-review-checklist-model.md`](427-review-checklist-model.md).
7. Findings and outcomes: [`428-review-observation-model.md`](428-review-observation-model.md), [`429-severity-and-finding-classification.md`](429-severity-and-finding-classification.md), [`430-professional-disagreement-model.md`](430-professional-disagreement-model.md), [`431-conditional-acceptance-model.md`](431-conditional-acceptance-model.md).
8. Lifecycle: [`432-validation-versioning.md`](432-validation-versioning.md), [`433-validation-expiration-and-revalidation.md`](433-validation-expiration-and-revalidation.md), [`434-implementation-change-impact.md`](434-implementation-change-impact.md).
9. Downstream workflows: [`435-validation-to-forge-workflow.md`](435-validation-to-forge-workflow.md), [`436-validation-to-atlas-workflow.md`](436-validation-to-atlas-workflow.md), [`437-validation-to-product-workflow.md`](437-validation-to-product-workflow.md).
10. Trust and integrity: [`438-professional-review-audit-trail.md`](438-professional-review-audit-trail.md), [`439-reviewer-independence-and-conflicts.md`](439-reviewer-independence-and-conflicts.md), [`440-evidence-quality-model.md`](440-evidence-quality-model.md).
11. Practical plans: [`441-review-sampling-strategy.md`](441-review-sampling-strategy.md), [`442-golden-review-models.md`](442-golden-review-models.md), [`443-current-preliminary-rule-review-plan.md`](443-current-preliminary-rule-review-plan.md), [`444-current-solitaire-review-plan.md`](444-current-solitaire-review-plan.md), [`445-professional-validation-register.md`](445-professional-validation-register.md).
12. Tooling: [`446-review-package-generation.md`](446-review-package-generation.md), [`447-studio-professional-review-mode.md`](447-studio-professional-review-mode.md), [`448-validation-security-and-privacy.md`](448-validation-security-and-privacy.md).
13. Quality: [`449-validation-evaluation-framework.md`](449-validation-evaluation-framework.md), [`450-current-code-mapping.md`](450-current-code-mapping.md).
14. [`451-validation-gap-analysis.md`](451-validation-gap-analysis.md), [`452-open-professional-validation-questions.md`](452-open-professional-validation-questions.md).

## Appendices

[`professional-reviewer-role-catalog.md`](../appendices/professional-reviewer-role-catalog.md), [`professional-validation-object-catalog.md`](../appendices/professional-validation-object-catalog.md), [`professional-review-checklist-catalog.md`](../appendices/professional-review-checklist-catalog.md), [`professional-validation-decision-catalog.md`](../appendices/professional-validation-decision-catalog.md), [`professional-finding-catalog.md`](../appendices/professional-finding-catalog.md), [`professional-validation-status-matrix.md`](../appendices/professional-validation-status-matrix.md), [`professional-rule-review-matrix.md`](../appendices/professional-rule-review-matrix.md), [`professional-geometry-review-matrix.md`](../appendices/professional-geometry-review-matrix.md), [`professional-evidence-catalog.md`](../appendices/professional-evidence-catalog.md), [`professional-code-mapping.md`](../appendices/professional-code-mapping.md), [`professional-test-matrix.md`](../appendices/professional-test-matrix.md) (`JM-BIBLE-A81` through `A91`, continuing from Sprint 12's last appendix, `A80`).

## Professional review templates (not part of the Bible's numbered docs)

[`docs/professional-review/`](../../professional-review/README.md) holds the actual forms a real reviewer would fill in — reviewer onboarding, a confidentiality/scope template, and role-specific review forms. None of them contain a fake completed review.

## Machine-readable specification

[`specs/professional-validation/v1/`](../../../specs/professional-validation/v1/README.md) holds 10 JSON Schemas, an active registry (empty), 5 example/template records, and 6 test-vector files, all generated by actually constructing and validating the real Pydantic models — never hand-invented.

## Real tooling shipped this Sprint

Unlike a purely descriptive Bible sprint, this one ships working code: `backend/jewelmind/professional_validation/` (schemas, registry loader, scope matcher, `validate-review-record` CLI, and a real **Professional Review Package generator** — `POST /api/professional-validation/review-package` produces a ZIP of the CURRENT model's real STEP, STL, JDL, technical specification, Forge report, geometry metadata, and an empty review form). See [`446-review-package-generation.md`](446-review-package-generation.md).

## Relationship to prior sprints

[`04-jewelry-domain/058-professional-validation-register.md`](../04-jewelry-domain/058-professional-validation-register.md) (Sprint 2) and [`06-forge/103-professional-validation-lifecycle.md`](../06-forge/103-professional-validation-lifecycle.md) (Sprint 4) already established that zero rules are validated and sketched a process. This Sprint does not contradict either — it formalizes, machine-readably implements, and becomes the authoritative process both documents now point to. Their historical content is preserved, not overwritten.

## Validation of this sprint

See [`SPRINT-13-VALIDATION-REPORT.md`](SPRINT-13-VALIDATION-REPORT.md) for the checks run against this section and the findings from that pass.
