---
id: JM-BIBLE-080
title: Errors, Warnings, and Diagnostics
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-075
related_documents:
  - JM-BIBLE-A11
implementation_status: current
professional_validation: not_required
normative: true
---

# Errors, Warnings, and Diagnostics

## Conceptual unified diagnostic shape

```
Diagnostic {
  code: string                 // stable, namespaced
  category: string             // which namespace group (see below)
  severity: fatal | error | warning | information
  message: string
  canonicalFieldPath: string   // e.g. "band.width"
  sourceLocation: optional     // only meaningful once a textual parser exists
  suggestedCorrection: optional
  blocking: boolean            // does this stop generation/export?
  stage: string                // JDL-0..JDL-10, see 063-jdl-processing-model.md
  relatedRule: optional        // e.g. "JM-BAND-001"
  relatedProfessionalValidationStatus: not_required | preliminary | required
}
```

This is a **documentation-level unification**, not a new code type. It does not rename or replace either of the two diagnostic representations that actually exist in the codebase today (below); it gives them one conceptual shape so a client can reason about both uniformly.

## The two diagnostic representations that actually exist today

| Representation | Used for | Fields |
|---|---|---|
| `ValidationResult` (`backend/jewelmind/validation/rules.py`) | Semantic/domain rules (JM-RING-*, JM-BAND-*, JM-STONE-*, JM-PRONG-*, JM-SETTING-*, JM-MANUFACTURING-*, JM-GEOMETRY-*) | `ruleId`, `severity` (`error \| warning \| information`), `message`, `parameter`, `suggestedValue` |
| `AppError` / `ErrorDetail` (`backend/jewelmind/api/errors.py`) | HTTP-level failures (parse, not-found, generation/export failure, engine unavailability) | `code`, `message`, `requestId`, `details` |

## Severities

| Severity | Blocks generation | Blocks export | Current usage |
|---|---|---|---|
| `fatal` | yes | yes | Conceptual only — a malformed request body or an unsupported `schemaVersion` behaves as fatal (HTTP 422 before any `ValidationResult` is even produced), though the current code does not use the literal string `"fatal"` as a severity value |
| `error` | yes | yes | `ValidationResult.severity == "error"` |
| `warning` | no | no | `ValidationResult.severity == "warning"` |
| `information` | no | no | `ValidationResult.severity == "information"` (used only by `JM-RING-003`) |

## Code namespaces — conceptual grouping, mapped to actual current codes

| Conceptual namespace | Actual current codes it groups | Notes |
|---|---|---|
| `JDL-PARSE-*` | No literal code exists yet — malformed JSON produces a generic FastAPI/Starlette 422 | Conceptual placeholder for a future dedicated parse-diagnostic code, once a textual DSL parser exists |
| `JDL-SCHEMA-*` | `REQUEST_VALIDATION_ERROR` (`api/app.py`) | Covers Pydantic structural-validation failures surfaced through FastAPI's request-validation-error handler |
| `JDL-SEMANTIC-*` | No literal code prefix exists; represented by the `ruleId` values below | Conceptual grouping for JM-RING-*/JM-BAND-*/etc. when discussing them as "semantic-layer" diagnostics collectively |
| `JM-DOMAIN-*` | `JM-RING-001..003`, `JM-BAND-001..003`, `JM-STONE-001..002`, `JM-PRONG-001..004`, `JM-SETTING-001..002`, `JM-MANUFACTURING-001` | These are the actual, literal rule IDs in `validation/rules.py` — none renamed; "JM-DOMAIN" is this document's grouping label, not a code prefix in the code itself |
| `JM-GEOMETRY-*` | `JM-GEOMETRY-001` | This one's actual prefix already matches the conceptual namespace name |
| `JM-EXPORT-*` | `EXPORT_FAILED`, `STEP_EXPORT_FAILED`, `STL_EXPORT_FAILED` | Actual `AppError.code` values |
| `JM-SYSTEM-*` | `MODEL_NOT_FOUND`, `MODEL_GENERATION_FAILED`, `BAD_REQUEST`, `CAD_ENGINE_UNAVAILABLE`, `INTERNAL_ERROR`, `VALIDATION_BLOCKED` | Actual `AppError.code` values; `VALIDATION_BLOCKED` is the HTTP-level wrapper raised when `has_errors()` is true, distinct from the individual `ruleId`s carried in its `details` list |

**No existing public code is renamed by this table.** Per JDL-GOV-007, the full authoritative list with exact current values lives in [`jdl-error-code-catalog.md`](../appendices/jdl-error-code-catalog.md).

## Same rule ID, value-dependent severity

`JM-BAND-002` and `JM-PRONG-002` each carry two possible severities depending on the input value (a hard `error` floor and a softer `warning` floor above it) — see [`074-semantic-rules.md`](074-semantic-rules.md). The diagnostic model accommodates this: severity is a property of a specific *diagnostic instance*, not fixed per code.
