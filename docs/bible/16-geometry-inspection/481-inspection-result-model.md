---
id: JM-BIBLE-481
title: Inspection Result Model
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
  - JM-BIBLE-462
  - JM-BIBLE-463
  - JM-BIBLE-482
  - JM-BIBLE-484
implementation_status: current
professional_validation: not_required
normative: true
---

# Inspection Result Model

## `GeometryInspectionReport` — the complete field list

```python
class GeometryInspectionReport(InspectionModel):
    inspectionId: str
    inspectionVersion: str
    definitionHash: str
    geometryGeneratorVersion: str
    kernelVersion: str | None = None
    startedAt: str
    completedAt: str
    status: InspectionStatus
    componentResults: list[ComponentInspectionResult]
    assemblyResult: AssemblyInspectionResult
    geometricFacts: list[GeometricFact]
    diagnostics: list[InspectionDiagnostic] = Field(default_factory=list)
    performance: InspectionPerformance
    unavailableInspections: list[str] = Field(default_factory=list)
```

(`backend/jewelmind/geometry/inspection/models.py:213-227`.) This is the response body of `GET /api/models/{modelId}/inspection` (`api/routes.py::model_inspection()`) and the exact object serialized into `geometry-inspection.json` in every Professional Review Package (`professional_validation/review_package.py`).

## How `inspect_model()` assembles each field

`inspector.py::inspect_model()` is the single real entry point (`backend/jewelmind/geometry/inspection/inspector.py:111-252`):

| Field | Real source |
|---|---|
| `inspectionId` | `f"inspection-{uuid.uuid4()}"` — a fresh random id every call, deliberately non-deterministic (see [`486-inspection-determinism.md`](486-inspection-determinism.md)). |
| `inspectionVersion` | The constant `INSPECTION_VERSION = "1.0.0"` (`version.py`), independent of `GENERATOR_VERSION`. |
| `definitionHash` | Taken directly from `model.definition_hash` — never recomputed by the inspection layer. |
| `geometryGeneratorVersion` | Taken directly from `model.generator_version` — never recomputed. |
| `kernelVersion` | `_kernel_version()`: `cadquery.__version__` wrapped in `try`/`except Exception`, returning `None` on any failure. Version introspection itself is not allowed to crash inspection — a real, deliberate defensive choice, not an oversight. |
| `startedAt` / `completedAt` | Real UTC ISO-8601 timestamps via `datetime.now(UTC).isoformat()`, captured at the true start and true end of `inspect_model()`. |
| `status` | See "Overall status" below. |
| `componentResults` | `list(component_results.values())`, one `ComponentInspectionResult` per entry in `model.components` (4 for the current solitaire), each from `inspect_component()`. |
| `assemblyResult` | The `AssemblyInspectionResult` returned by `inspect_assembly()`. |
| `geometricFacts` | The full flattened list built in `inspect_model()` itself — per-component facts (`_component_facts()`), plus assembly-scope facts (`COMPONENT_COUNT`, `PRONG_COUNT`, `STONE_METAL_SEPARATE`, one `CONNECTED`/`DISCONNECTED` fact per production connectivity group), plus pair-scope facts (`INTERSECTION_VOLUME`, `MIN_DISTANCE`, one of each per real pair). |
| `diagnostics` | Every `InspectionDiagnostic` collected from every `ComponentInspectionResult.diagnostics` — flattened into one top-level list. |
| `performance` | An `InspectionPerformance` built from `component_ms` (measured around the `component_results` comprehension) and the `distance`/`intersection`/`topology` values `inspect_assembly()` returns in its second tuple element. |
| `unavailableInspections` | Currently always `[]` — see "`unavailableInspections` is currently always empty" below. |

## Overall `status` — real computation

```python
overall_status: InspectionStatus = "PASS"
if not assembly_result.requiredComponentsPresent:
    overall_status = "FAIL"
elif any(d.severity == "error" for d in diagnostics):
    overall_status = "FAIL"
```

Two conditions, checked in order, either of which sets `FAIL`: a required component missing (`AssemblyInspectionResult.requiredComponentsPresent is False`), or any collected diagnostic having `severity == "error"`. A diagnostic with `severity == "warning"` or `severity == "info"` never flips overall status to `FAIL` on its own — this is the direct real implementation of INSPECT-GOV-019 ("failed optional inspections must not automatically erase otherwise valid geometry").

This top-level `status` is deliberately a different field from any individual fact's own `status` — see [`482-inspection-status-and-confidence.md`](482-inspection-status-and-confidence.md) and [`483-inspection-error-model.md`](483-inspection-error-model.md) for INSPECT-GOV-005's real implementation (`GeometryInspectionReport.status` vs. a per-fact `status`).

## `unavailableInspections` is currently always empty

The field exists (`list[str] = Field(default_factory=list)`) and `inspect_model()` always constructs the report with `unavailableInspections=[]` — no current inspection reports itself as fully unavailable at the model level. This is distinct from a single pair's distance or intersection measurement failing (which produces `status: "ERROR"`/`"UNKNOWN"` on that one `DistanceResult`/`IntersectionResult`, not an entry in `unavailableInspections`). The field is reserved for a genuinely absent future capability — the same honest pattern INSPECT-GOV-007 describes for a check this Sprint's investigation found no reliable kernel API for (see [`466-shape-validity-inspection.md`](466-shape-validity-inspection.md) for what was actually tested against `cadquery==2.8.0`) — not a currently-reachable code path.

## Tests

`backend/tests/test_geometry_inspection.py::TestInspectionMetadata` — `test_generated_model_record_carries_a_real_inspection_report` (asserts `record.inspection_report.status in ("PASS", "FAIL")` and `assemblyResult.componentCount == 4` against a real `ModelService.generate()` call) and `test_inspection_report_accessor_returns_the_same_report` (`service.inspection_report(record.model_id) is record.inspection_report` — identity, not just equality).

## Cross-references

- [`462-geometric-fact-model.md`](462-geometric-fact-model.md) — the flattened `GeometricFact` shape assembled into `geometricFacts`.
- [`482-inspection-status-and-confidence.md`](482-inspection-status-and-confidence.md) — the 6 `InspectionStatus` values used throughout this report.
- [`484-inspection-performance-model.md`](484-inspection-performance-model.md) — how `InspectionPerformance`'s 5 fields are really measured.
- [`08-alchemist/174-determinism-and-version-fingerprint.md`](../08-alchemist/174-determinism-and-version-fingerprint.md) — `kernelVersion` is the first place a CadQuery/OCCT build identifier is recorded on any generated-model artifact; see [`485-inspection-versioning.md`](485-inspection-versioning.md) for why it is not yet part of Alchemist's own fingerprint model.
