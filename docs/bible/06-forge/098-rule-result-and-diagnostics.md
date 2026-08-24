---
id: JM-BIBLE-098
title: Rule Result and Diagnostics
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-096
related_documents:
  - JM-BIBLE-080
implementation_status: partial
professional_validation: not_required
normative: true
---

# Rule Result and Diagnostics

The normative `ForgeRuleResult` shape is `specs/forge/v1/rule-result.schema.json`.

## Field-by-field mapping to the current `ValidationResult`

| `ForgeRuleResult` field | Current `ValidationResult` field | Status |
|---|---|---|
| `ruleId` | `ruleId` | CURRENT |
| `ruleVersion` | — | PLANNED — no current result carries a rule version; `specs/forge/v1/current-rule-registry.json` fixes every rule at `1.0.0` today, so the field is trivially satisfiable but not actually threaded through `ValidationResult` |
| `status` | — | PLANNED — see below |
| `severity` | `severity` | CURRENT |
| `message` | `message` | CURRENT |
| `fieldPath` | `parameter` | CURRENT (renamed only in this conceptual model; the real field is still called `parameter` in code, per JDL-GOV-007-equivalent discipline — this document does not claim `parameter` was renamed) |
| `affectedComponent` | — | PLANNED — no current rule identifies a specific `GeneratedComponent` by name |
| `actualValue` | — | PLANNED — the current result does not echo back the offending value |
| `expectedConstraint` | — | PLANNED — implicit in `message` text today, not a separate structured field |
| `suggestedValue` | `suggestedValue` | CURRENT |
| `suggestionText` | — | PLANNED — folded into `message` today |
| `blocking` | derived from `severity == "error"` via `has_errors()` | CURRENT, but computed at the caller, not stored on the result itself |
| `blockingScope` | — | PLANNED — see [`099-severity-and-blocking-semantics.md`](099-severity-and-blocking-semantics.md) |
| `provenanceStatus` | — | PLANNED — see `specs/forge/v1/test-vectors/provenance-vectors.json` for the current mapping, computed outside the runtime result |
| `professionalValidationStatus` | — | PLANNED |
| `stage` | — | PLANNED — see `specs/forge/v1/current-rule-registry.json` for the current mapping |
| `timestamp` | — | PLANNED — `ModelRecord.generated_at` exists at the generation level, not per-diagnostic |
| `metadata` | — | PLANNED |

## Why `status` is PLANNED

`validate_definition()` only ever returns diagnostics for rules that **fired** — a rule that passed produces no entry in the result list at all. There is no current way to distinguish "this rule ran and passed" from "this rule was never evaluated." A future full-evaluation-trace mode (returning `PASSED`/`SKIPPED`/`NOT_APPLICABLE` entries too) would be a MINOR, additive change to the API response shape, but is not implemented in this Sprint.

## No breaking change to current public codes

This document does not rename `ruleId`, `severity`, `message`, `parameter`, or `suggestedValue` in the real `ValidationResult` Pydantic model, and does not change `/api/models/validate`'s response shape. `ForgeRuleResult` is a superset conceptual model for future evolution, cross-referenced against [`05-jdl/080-errors-warnings-and-diagnostics.md`](../05-jdl/080-errors-warnings-and-diagnostics.md)'s existing diagnostic-code-namespace table, which remains the authority on actual current public codes.
