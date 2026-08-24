---
id: JM-BIBLE-171
title: Compilation Result Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-170
related_documents:
  - JM-BIBLE-A30
implementation_status: partial
professional_validation: not_required
normative: true
---

# Compilation Result Model

The normative shape is `specs/alchemist/v1/compilation-result.schema.json`; two real worked examples (a clean success and a blocked failure, both using real Sprint 3/5 data) are in `specs/alchemist/v1/examples/`.

## Field status summary

| Field | Status | Real current source |
|---|---|---|
| `compilationId` | PLANNED | — |
| `status` | PLANNED (as an explicit enum) / CURRENT (as implicit HTTP status + exception type) | — |
| `schemaVersion` | CURRENT | `JewelryDefinition.schemaVersion` |
| `compilerVersion` | PLANNED as a distinct concept | — |
| `geometryGeneratorVersion` | CURRENT | `GeneratedModel.generator_version` |
| `forgeRuleSetVersion` | PLANNED (no aggregate version exists) | — |
| `kernelVersion` | PLANNED | — |
| `sourceDefinitionHash` | CURRENT | `GeneratedModel.definition_hash` |
| `compilationHash` | PLANNED | see [`175-definition-hash-vs-compilation-hash.md`](175-definition-hash-vs-compilation-hash.md) |
| `normalizedDefinition` | CURRENT | the `JewelryDefinition` instance |
| `forgeEvaluation` | CURRENT | `list[ValidationResult]` |
| `geometryPlanSummary` | PLANNED | no `GeometryPlan` exists |
| `componentManifest` | CURRENT (preview only) | `ModelRecord.preview_manifest` |
| `geometryMetadata` | CURRENT | `GeneratedModel`'s volume/bbox/warnings fields |
| `diagnostics` | CURRENT (as `ValidationResult`) / PARTIAL (as `compiler-diagnostic.schema.json` shape) | — |
| `artifacts` | PARTIAL | each artifact independently knowable, never aggregated |
| `timings` | CURRENT (total only) / PLANNED (per-stage) | `GeneratedModel.generation_duration_s` |
| `fallbacks` | PARTIAL | a subset of `warnings`, not structurally distinguished |
| `cacheStatus` | PARTIAL | `ModelService`'s cache exists; no hit/miss field is surfaced |
| `createdAt` | CURRENT | `ModelRecord.generated_at` |

**8 of 19 fields are CURRENT** (fully mapped to real data), **5 are PARTIAL** (a real analogue exists but doesn't match the full conceptual shape), **6 are PLANNED** (no current analogue at all).

## No claim of full current implementation

This document does not claim `CompilationResult` is returned by any real endpoint today — `GenerateResponse` and `ModelMetadataResponse` (`api/schemas.py`) are the two real response shapes, and neither matches this conceptual model field-for-field. `CompilationResult` is the target shape a future unification of those two (plus artifact/diagnostic aggregation) could converge toward.
