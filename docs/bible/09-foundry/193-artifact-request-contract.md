---
id: JM-BIBLE-193
title: Artifact Request Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-192
related_documents:
  - JM-BIBLE-177
implementation_status: partial
professional_validation: not_required
normative: true
---

# Artifact Request Contract

## One authoritative source, two schemas with distinct scope

Sprint 6's `specs/alchemist/v1/artifact-request.schema.json` already defines a minimal `ArtifactRequest` covering `STEP | STL | JSON | PREVIEW_MESH`. Rather than duplicate it, `specs/foundry/v1/artifact-request.schema.json` is declared a genuine superset **scoped to production/technical artifacts only** (`STEP | STL | JSON | TECHNICAL_SPECIFICATION` — no `PREVIEW_MESH`, since preview requests are Alchemist/Vision's concern, never Foundry's). Alchemist's schema stays authoritative for the minimal cross-cutting shape any artifact request has; Foundry's schema stays authoritative for the additional fields production/technical exports specifically need (`requestId`, `requestedBy`, `sourceCompilationId`, `includeComponents`, `excludeComponents`, `outputPreferences`).

## Field-by-field status (Foundry's schema)

| Field | Status | Real mapping today |
|---|---|---|
| `artifactType` | CURRENT | Chosen implicitly by which of the 4 endpoints/functions is called (`export_step_file`, `export_stl_file`, `export_json`, `build_specification`). |
| `sourceDefinitionHash` | CURRENT, implicit | Every `GeneratedModel` already carries `definition_hash`; no request field carries it explicitly today because there is no request *object*, only a `model_id` path parameter that already identifies a cached model. |
| `requestId` | PLANNED | No request identifier of any kind exists; each HTTP call is independently handled and logged only by its `model_id`. |
| `requestedBy` | PLANNED | No user/session identity exists anywhere in the backend (no auth — see CLAUDE.md's explicit out-of-scope list). |
| `sourceCompilationId` | PLANNED | Depends on `CompilationResult` (Sprint 6, not materialized). |
| `includeComponents` / `excludeComponents` | PARTIAL | The only real toggle today is the single boolean `includeStoneReference` on `export_step_file`/`export_stl_file`; there is no way to include/exclude `band`, `prongs`, or `basket_support` independently. |
| `outputPreferences` | PARTIAL | `meshTolerance`/`angularTolerance` are real, already-existing fields on `JewelryDefinition.preview`, not on a request object; STL export reads them from there unless explicitly overridden by function arguments (never by an HTTP request field). |

## Why `includeStoneReference` is the only real inclusion toggle

Every other production component (`band`, `prongs`, `basket_support`) is fused into a single `combined_metal` shape at geometry-generation time (`_fuse_metal()` in `geometry/assemblies/solitaire.py`), before Foundry ever sees it. Foundry cannot selectively exclude one of those three today because the shape it receives is already a single fused solid — see [`196-production-geometry-selection.md`](196-production-geometry-selection.md) and [`213-multi-solid-and-fusion-policy.md`](213-multi-solid-and-fusion-policy.md). Only `stone_reference`, which is deliberately never fused (LAW-006), can be independently included or excluded.
