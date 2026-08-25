---
id: JM-BIBLE-FORGE-README
title: Forge Rule System v1 — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-DOMAIN-README
  - JM-BIBLE-JDL-README
related_documents:
  - JM-BIBLE-README
  - JM-BIBLE-054
implementation_status: partial
professional_validation: not_required
normative: false
---

# Forge Rule System v1 — Index

This is **Sprint 4** of the Technical Bible: **Forge Rule System v1**. Forge is the formal model of every jewelry-domain rule JewelMind evaluates — before, during, and after deterministic geometry generation. It does not add a new rule, a new jewelry style, a new geometry family, AI generation, or any new blocking behavior. **It is a specification and classification layer over the validation engine that already exists** (`backend/jewelmind/validation/engine.py`), not a new runtime system.

**Read this README, then [`090-forge-governance.md`](090-forge-governance.md), before modifying `backend/jewelmind/validation/`, `shared/validation/`, or introducing a new jewelry-domain threshold anywhere in the codebase.**

## The single most important fact in this section

**Forge is the authoritative repository of jewelry-domain rules. Geometry builders (Atlas — see Sprint 5) must never become a hidden source of jewelry-domain thresholds.** The frontend (`shared/validation/engine.ts`) may mirror rules for instant UX feedback, but the backend Forge evaluation is always authoritative — this is unchanged from ADR-004 and LAW-004, restated here as a Forge-level architectural principle. AI may in the future propose candidate rules, classifications, explanations, or fixes; **AI must never automatically promote a candidate rule to an accepted professional rule** — see [`114-future-ai-assisted-rule-discovery.md`](114-future-ai-assisted-rule-discovery.md).

## Zero professionally validated rules

As of this Sprint, **0 of the 21 registered Forge rules are professionally validated.** Every rule is `preliminary` or `not_required` — see [`103-professional-validation-lifecycle.md`](103-professional-validation-lifecycle.md) and [`appendices/forge-professional-validation-matrix.md`](../appendices/forge-professional-validation-matrix.md). Existing implementation, no matter how long it has run in production, does not itself count as professional validation.

## Reading order

1. [`090-forge-governance.md`](090-forge-governance.md) — 15 non-negotiable rules (FORGE-GOV-001..015).
2. [`091-rule-system-overview.md`](091-rule-system-overview.md) — the conceptual pipeline and a Mermaid architecture diagram.
3. [`092-rule-anatomy.md`](092-rule-anatomy.md) — the normative `ForgeRule` model.
4. [`093-rule-classification-model.md`](093-rule-classification-model.md) — 11 categories, every current rule reclassified.
5. [`094-rule-provenance-model.md`](094-rule-provenance-model.md) — where a rule's justification comes from.
6. [`095-rule-lifecycle.md`](095-rule-lifecycle.md) — 8 lifecycle states and their transitions.
7. [`096-rule-evaluation-pipeline.md`](096-rule-evaluation-pipeline.md) — FORGE-0 through FORGE-9.
8. [`097-rule-context-model.md`](097-rule-context-model.md), [`098-rule-result-and-diagnostics.md`](098-rule-result-and-diagnostics.md), [`099-severity-and-blocking-semantics.md`](099-severity-and-blocking-semantics.md).
9. [`100-rule-dependencies-and-ordering.md`](100-rule-dependencies-and-ordering.md), [`101-conflicts-precedence-and-resolution.md`](101-conflicts-precedence-and-resolution.md), [`102-suggestions-and-auto-fix-contract.md`](102-suggestions-and-auto-fix-contract.md).
10. [`103-professional-validation-lifecycle.md`](103-professional-validation-lifecycle.md).
11. Rule families: [manufacturing profile](104-manufacturing-profile-rules.md), [geometry precondition](105-geometry-precondition-rules.md), [generated geometry inspection](106-generated-geometry-inspection-rules.md), [export precondition](107-export-precondition-rules.md).
12. [`108-rule-versioning.md`](108-rule-versioning.md), [`109-rule-registry.md`](109-rule-registry.md), [`110-current-rule-inventory.md`](110-current-rule-inventory.md), [`111-domain-rule-gap-analysis.md`](111-domain-rule-gap-analysis.md), [`112-rule-testing-strategy.md`](112-rule-testing-strategy.md).
13. [`113-forge-api-contract.md`](113-forge-api-contract.md), [`114-future-ai-assisted-rule-discovery.md`](114-future-ai-assisted-rule-discovery.md) (VISION), [`115-open-forge-questions.md`](115-open-forge-questions.md).

## Appendices

[`forge-rule-catalog.md`](../appendices/forge-rule-catalog.md), [`forge-rule-provenance-register.md`](../appendices/forge-rule-provenance-register.md), [`forge-severity-matrix.md`](../appendices/forge-severity-matrix.md), [`forge-professional-validation-matrix.md`](../appendices/forge-professional-validation-matrix.md), [`forge-rule-dependency-matrix.md`](../appendices/forge-rule-dependency-matrix.md), [`forge-rule-test-matrix.md`](../appendices/forge-rule-test-matrix.md).

## Machine-readable specification

[`specs/forge/v1/`](../../../specs/forge/v1/README.md) holds `rule.schema.json`, `rule-result.schema.json`, `rule-context.schema.json`, `rule-registry.schema.json`, the real `current-rule-registry.json` (21 rules), 6 example rule definitions, and 4 test-vector files — all generated from or validated against the actual running implementation. `backend/tests/test_forge_registry.py` re-checks all of it on every test run.

## Relationship to Sprint 2 and Sprint 3

Sprint 2 ([`04-jewelry-domain/`](../04-jewelry-domain/README.md)) established the classification of jewelry-domain statements (IMPLEMENTED FACT / PRELIMINARY SOFTWARE RULE / PROFESSIONALLY VALIDATED RULE / etc.) and the 16 current validation rules. Sprint 3 ([`05-jdl/`](../05-jdl/README.md)) formalized the language those rules operate over and folded semantic/domain validation into JDL stages JDL-5/JDL-6. **Sprint 4 does not redefine either** — it gives the rule *system itself* (not the document format, not individual domain facts) a formal architecture: anatomy, provenance, lifecycle, evaluation pipeline, and professional-validation process. [`04-jewelry-domain/054-domain-validation-classification.md`](../04-jewelry-domain/054-domain-validation-classification.md) and [`05-jdl/075-validation-pipeline.md`](../05-jdl/075-validation-pipeline.md) were both updated this Sprint to cross-reference Forge rather than duplicate it.

## Relationship to Sprint 9

[`11-studio/`](../11-studio/README.md) (Sprint 9) presents Forge's diagnostics (`ValidationResult`) to the user via `ValidationPanel`/`ValidationItem`, unchanged this Sprint, and never filters, reclassifies, or hides a diagnostic Forge returns (STUDIO-GOV-010). Studio's own client-side `NumericField` `min`/`max` hints are advisory UI feedback only, never a duplicate of a Forge rule threshold (STUDIO-GOV-001) — the backend's evaluation remains the sole authority.

## Validation of this sprint

See [`SPRINT-4-VALIDATION-REPORT.md`](SPRINT-4-VALIDATION-REPORT.md) for the checks run against this section and the findings from that pass.
