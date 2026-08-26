---
id: JM-BIBLE-168
title: Atlas Execution Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-166
related_documents:
  - JM-BIBLE-132
implementation_status: partial
professional_validation: not_required
normative: true
---

# Atlas Execution Contract

## Conceptual interface

```
execute_geometry_plan(plan: GeometryPlan) -> AtlasExecutionResult
```

```
AtlasExecutionResult {
  executionStatus
  componentResults
  assembly
  geometryMetadata
  inspectionFacts
  fallbacks
  warnings
  errors
  duration
}
```

## Current mapping

| `AtlasExecutionResult` field | Current mapping |
|---|---|
| `executionStatus` | Implicit — success is "a `GeneratedModel` was returned"; failure is "an exception propagated" |
| `componentResults` | `GeneratedModel.components` |
| `assembly` | `GeneratedModel.combined_metal` + its bounding box/volume |
| `geometryMetadata` | `GeneratedModel`'s volume/bounding-box/warnings fields |
| `inspectionFacts` | As of Sprint 14: a real, separate, structured `GeometryInspectionReport` (`jewelmind.geometry.inspection.inspect_model()`), stored on `ModelRecord.inspection_report`, computed immediately after `GeneratedModel` construction — see [`16-geometry-inspection/488-alchemist-inspection-integration.md`](../16-geometry-inspection/488-alchemist-inspection-integration.md) |
| `fallbacks` | A subset of `GeneratedModel.warnings`, not structurally distinguished |
| `warnings` | `GeneratedModel.warnings` |
| `errors` | Not returned — a construction failure raises an exception rather than populating an `errors` list on a still-returned result |
| `duration` | `GeneratedModel.generation_duration_s` |

## Current call shape vs. the conceptual interface

**No function named `execute_geometry_plan` exists.** The real call is `build_solitaire_ring(definition: JewelryDefinition) -> GeneratedModel` — it takes the *definition* directly, not a `GeometryPlan`, because no `GeometryPlan` exists to pass. This is the direct consequence of [`166-geometry-plan-model.md`](166-geometry-plan-model.md)'s PLANNED status: the conceptual interface above describes what Alchemist-to-Atlas communication would look like once a plan exists, not a change made now.

## Alchemist must not inspect CadQuery internals directly

**Confirmed true for the orchestration layer, with one honest exception found in Foundry-to-be code.** `services/model_service.py`, `api/routes.py`, and `preview/mesh.py` never import `cadquery` and operate only on `GeneratedModel`/`GeneratedComponent` (Atlas's own result types) — confirmed by grepping every `import cadquery`/`from cadquery` statement in the codebase during this Sprint. However, `exporters/step_exporter.py` and `exporters/stl_exporter.py` **do** import `cadquery` directly, each calling `cq.Compound.makeCompound([combined_metal, stone_reference])` when `include_stone=True` — a small, genuine CAD-kernel operation performed outside `geometry/`. This is a minor, low-risk boundary crossing (combining two already-Atlas-built shapes into an export-only compound, never constructing new primitive geometry), not a violation of ALCHEMIST-GOV-006-adjacent orchestration purity, but it is recorded honestly here and in [`183-current-backend-to-compiler-mapping.md`](183-current-backend-to-compiler-mapping.md) rather than glossed over.

**Sprint 14 addition**: `backend/jewelmind/geometry/inspection/` (the new inspection subsystem) does import `cadquery` directly — but it lives inside `geometry/`, alongside `geometry/components/` and `geometry/assemblies/`, i.e. inside Atlas's own territory, not inside the orchestration layer this section audits. `services/model_service.py` still never imports `cadquery` itself; it only calls `jewelmind.geometry.inspection.inspect_model()`, which returns a plain, kernel-neutral `GeometryInspectionReport` — the same orchestration-purity boundary this document establishes for `build_solitaire_ring()` itself.
