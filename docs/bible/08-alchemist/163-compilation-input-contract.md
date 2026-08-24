---
id: JM-BIBLE-163
title: Compilation Input Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-162
related_documents:
  - JM-BIBLE-A27
implementation_status: partial
professional_validation: not_required
normative: true
---

# Compilation Input Contract

The normative shape is `specs/alchemist/v1/compilation-input.schema.json`.

## Fields and current status

| Field | Current status |
|---|---|
| `canonicalJDL` | CURRENT — the only field the real API actually receives (`generate_model(definition: JewelryDefinition)` in `api/routes.py`) |
| `requestedArtifacts` | PLANNED — no upfront artifact list exists; each artifact is a separate later HTTP call against an already-generated `modelId` |
| `compilerOptions` | PARTIAL — the only option-like fields today are STL export overrides (`meshTolerance`, `angularTolerance`), scoped to one export call, not a general options bag |
| `capabilityRequirements` | PLANNED |
| `requestContext` | PARTIAL — `ErrorDetail.requestId` exists only on error responses |
| `expectedSchemaVersion` | PARTIAL — implicit via `schemaVersion`'s `Literal["0.1.0"]` |
| `previousCompilationReference` | PLANNED |

## Raw frontend UI state is never included

Per this Sprint's explicit instruction, `CompilationInput` never includes raw frontend state (`useProjectStore.ts`'s `isStale`, `generationStatus`, `exportStatus`, etc.) — this restates ALCHEMIST-GOV-015. The frontend already respects this boundary today: it sends only a `JewelryDefinition`, never its own internal UI state, to `/api/models/generate`.

## Why this document doesn't propose implementing `CompilationInput` now

The current single-field reality (`canonicalJDL` only) already satisfies every real current use case. Wrapping it in a `CompilationInput` object today would add structure with no current consumer — recorded as a target shape for when `requestedArtifacts`/`compilerOptions` genuinely need to travel together in one request (e.g., if a future unified compile-and-export-everything endpoint is built).
