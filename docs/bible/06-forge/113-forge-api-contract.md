---
id: JM-BIBLE-113
title: Forge API Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-097
  - JM-BIBLE-098
related_documents:
  - JM-BIBLE-023
  - JM-BIBLE-165
implementation_status: partial
professional_validation: not_required
normative: true
---

# Forge API Contract

**Relationship to Alchemist (Sprint 6):** [`08-alchemist/165-forge-evaluation-integration.md`](../08-alchemist/165-forge-evaluation-integration.md)
defines exactly how the compiler consumes this contract's conceptual
`evaluate()` output (passed rules, diagnostics, blockers, advisory
warnings) and confirms `professionalReviewRequired` would always be
`false` today, since zero rules currently have
`professionalValidationStatus: required`.

## Conceptual future API

```
evaluate(document: JDLDocumentV1, context: ForgeEvaluationContext) -> ForgeEvaluation
```

```
ForgeEvaluation {
  ruleSetVersion: string
  evaluatedRules: string[]        // ruleIds that were considered
  passedRules: string[]           // ruleIds that ran and did not fire
  diagnostics: ForgeRuleResult[]  // ruleIds that fired
  blockingDiagnostics: ForgeRuleResult[]
  advisoryDiagnostics: ForgeRuleResult[]
  professionalReviewRequired: boolean
  evaluationDuration: number
  resultStatus: "PASS" | "BLOCKED" | "ADVISORY_ONLY"
}
```

## Mapping to the current, real endpoint

| `ForgeEvaluation` field | Current equivalent | Status |
|---|---|---|
| `ruleSetVersion` | — | PLANNED — no current response carries a rule-set version; it would be `"1.0.0"` for the entire current registry today |
| `evaluatedRules` | — | PLANNED — `validate_definition()` does not report which rules ran, only which fired |
| `passedRules` | — | PLANNED, same reason |
| `diagnostics` | The full `list[ValidationResult]` returned by `/api/models/validate` | CURRENT |
| `blockingDiagnostics` | The subset with `severity == "error"` | CURRENT, but not pre-split in the response — the caller filters client-side today |
| `advisoryDiagnostics` | The subset with `severity in {"warning", "information"}` | CURRENT, same caveat |
| `professionalReviewRequired` | — | PLANNED — would currently always be `false`-equivalent in spirit for every rule (`professionalValidationStatus != "required"` for all 21 current rules), but no such flag is computed or returned today |
| `evaluationDuration` | — | PLANNED — `validate_definition()` is not separately timed; only geometry generation is (`GeneratedModel.generation_duration_s`) |
| `resultStatus` | Implicit in `has_errors()`'s boolean plus HTTP status (200 vs. 422) | CURRENT, but not returned as a named enum field |

## Current real endpoint this maps to

`POST /api/models/validate` (see [`02-architecture/023-data-flow.md`](../02-architecture/023-data-flow.md)) is the entry point that most closely matches `evaluate()` conceptually: it accepts a `JewelryDefinition` and returns `{results, hasErrors}`. It does not accept a `ForgeEvaluationContext` — only the bare document.

## No new runtime endpoint added this Sprint

Per this Sprint's explicit scope, no new API route, response field, or request parameter was added to the running FastAPI application. `ForgeEvaluation` is a documented target shape for a future evolution of `/api/models/validate`'s response, not a change made now.
