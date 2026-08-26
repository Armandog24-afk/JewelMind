---
id: JM-BIBLE-489
title: Foundry Inspection Integration
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-190
  - JM-BIBLE-A25
normative: true
implementation_status: current
professional_validation: not_required
---

# Foundry Inspection Integration

## Export preconditions are unchanged

`ModelService.export_step_file()` and `ModelService.export_stl_file()` (`backend/jewelmind/services/model_service.py`) were read in full for this Sprint. Neither method references `inspection_report`, `GeometryInspectionReport`, or any field of either. Both are gated on exactly one precondition, unchanged since before this Sprint: `self.get_record(model_id)`, which raises `ModelNotFoundError` (`backend/jewelmind/api/errors.py`) if no cached `ModelRecord` exists for that `model_id`. That is the entire gate. Everything downstream of it — `export_step()`, `export_stl()`, `validate_non_empty()` — operates on `record.generated_model`, never on `record.inspection_report`.

## This is a deliberate non-integration, not an oversight

Per this Sprint's brief and per `docs/bible/06-forge/106-generated-geometry-inspection-rules.md`'s own Sprint 14 update: *"Sprint 14 deliberately did NOT make export depend on inspection."* Stated plainly: **a model with a disconnected production group would still export successfully today**, hypothetically — inspection reports facts for human and (eventually) Forge consumption, it does not gate Foundry. This is not a currently-observable failure mode: the real default solitaire and the real 4-prong variant both produced `productionConnectivity.isFullyConnected == True` with zero disconnected groups during this Sprint's investigation (see [`493-current-solitaire-inspection-map.md`](493-current-solitaire-inspection-map.md)). But the code path does not block on it either way, and this document states that as a fact about the code, not as a claim that the current geometry ever exercises it.

This preserves FOUNDRY-GOV-018 (Foundry reports what was exported and whether it passed an integrity check; it never interprets a geometric fact as a jewelry-domain violation) and the Atlas/Forge boundary this Sprint's whole subsystem exists to make real: an export succeeding or failing remains a question of whether `export_step()`/`export_stl()` themselves produced real, non-empty geometry (`validate_non_empty()`), not a question of what `inspect_model()` reported about that geometry.

## Foundry-relevant inspection facts do exist — four real, already-wired consumption points

None of the four is a blocking precondition on STEP/STL export. All four are real and already wired as of this Sprint:

| Consumption point | What it exposes | Where |
|---|---|---|
| Concise summary in generate/metadata responses | `status`, `version`, `componentCount`, `productionSolidCount`, `disconnectedProductionGroups`, `diagnosticsCount` | `GenerateResponse.metadata["inspection"]` and `ModelMetadataResponse.inspection`, built by `api/routes.py::_inspection_summary()` |
| Full report via dedicated endpoint | The complete `GeometryInspectionReport` | `GET /api/models/{model_id}/inspection` → `ModelService.inspection_report(model_id)` |
| Technical specification Markdown section | Inspection status, version, production connectivity, requested-vs-generated prong count, and an explicit non-manufacturability disclaimer line | `exporters/specification.py::build_specification()`'s `## Geometry inspection summary` section, appended only when `inspection_report` is passed (which `ModelService.export_specification_text()` always does) |
| Professional Review Package | The full real `GeometryInspectionReport`, serialized as JSON | `geometry-inspection.json` inside the ZIP built by `professional_validation/review_package.py::build_review_package()`, verified by `backend/tests/test_geometry_inspection.py::TestReviewPackageInspectionFile` |

The specification's inspection section (`specification.py`, lines ~104-123) ends with an explicit disclaimer: *"This is a geometric fact summary, not a manufacturability or professional-quality assessment"* — restating the Atlas/Forge boundary at the export-artifact layer, consistent with FOUNDRY-GOV-002/008's requirement that no exported artifact overstate what it actually verified.

## Component-inclusion defaults are unaffected

Nothing in this Sprint changes which components a STEP/STL export includes by default. `includeStoneReference` still defaults to excluded (LAW-006, FOUNDRY-GOV-004) — inspection reads and reports on the stone reference (`StoneMetalSeparationResult`) but has no code path that could change export inclusion, because `export_step_file()`/`export_stl_file()` never consult `inspection_report` at all, as established above. This is not a MAJOR export-default change under FOUNDRY-GOV-016 because nothing about the default changed.

## Relationship to the fallback register

`docs/bible/appendices/atlas-fallback-register.md` records the two existing fallback paths (`ATLAS-FALLBACK-001` band fillet, `ATLAS-FALLBACK-002` combined-metal fuse) as having **no regression tests** that force them to trigger — verified only by code review. This Sprint's `BooleanOperationResult.fallbackUsed` (populated in `assembly.py::_boolean_operations()`, detecting more than one top-level solid in `combined_metal`) is a real, runtime-observable signal for `ATLAS-FALLBACK-002` specifically — the first time this codebase can *detect*, not merely warn about, that fallback having triggered on a real generation. It does not add a regression test for the fallback itself, and it does not change Foundry's export behavior when the fallback is active: a 3-solid `combined_metal` compound still exports exactly as it did before this Sprint (LAW-005 — no component silently dropped). See [`479-fallback-result-inspection.md`](479-fallback-result-inspection.md) for the fuller treatment of this signal at the inspection-model level.
