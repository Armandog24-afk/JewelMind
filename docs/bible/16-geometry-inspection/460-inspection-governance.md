---
id: JM-BIBLE-460
title: Inspection Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-INSPECTION-README
related_documents:
  - JM-BIBLE-120
  - JM-BIBLE-090
implementation_status: current
professional_validation: not_required
normative: true
---

# Inspection Governance

## INSPECT-GOV-001 through INSPECT-GOV-020

| ID | Rule |
|---|---|
| **INSPECT-GOV-001** | Inspection reports geometric facts, not aesthetic judgment. Every field in `backend/jewelmind/geometry/inspection/models.py` holds a measurement, a count, a boolean presence/absence, or a status — never a word like "acceptable," "good," or "professional-quality." |
| **INSPECT-GOV-002** | Jewelry-domain thresholds belong to Forge. No file under `backend/jewelmind/geometry/inspection/` imports `backend/jewelmind/validation/` or references a Forge rule ID; `specs/geometry-inspection/v2/fact-registry.json` explicitly notes zero professional thresholds appear in the fact catalog. |
| **INSPECT-GOV-003** | Inspection must operate on actual generated geometry. `inspect_model()` (`inspector.py`) always takes a real `GeneratedModel` produced by `build_solitaire_ring()` — never a synthetic or assumed shape for real production use (test-only fixtures are explicitly marked as such, see [`493-current-solitaire-inspection-map.md`](493-current-solitaire-inspection-map.md)). |
| **INSPECT-GOV-004** | Required runtime inspections must not rely only on tests. `ModelService.generate()` calls `inspect_model()` on every single generation — the same code path a real API caller exercises, not just `backend/tests/test_geometry_inspection.py`. |
| **INSPECT-GOV-005** | Inspection failure must be distinguishable from geometry failure. `GeometryInspectionReport.status` (whether inspection itself succeeded in producing facts) is a separate field from any fact's own `status` (whether that specific measurement passed) — see [`483-inspection-error-model.md`](483-inspection-error-model.md). |
| **INSPECT-GOV-006** | UNKNOWN is preferable to fabricated PASS. `distance.py`/`intersection.py`/`topology.py` return `status: "ERROR"` or `"UNKNOWN"` on a kernel exception — never a guessed `PASS`. Verified by `test_geometry_inspection.py::TestInspectionErrorRecovery`. |
| **INSPECT-GOV-007** | Unavailable kernel capabilities must be reported honestly. `GeometryInspectionReport.unavailableInspections` exists precisely for a check this Sprint's investigation found no reliable kernel API for — see [`466-shape-validity-inspection.md`](466-shape-validity-inspection.md) for what was actually tested against cadquery==2.8.0. |
| **INSPECT-GOV-008** | StoneReference must remain semantically identifiable during inspection. `assembly.py::_stone_metal_separation()` always reports `stoneReferenceExists`/`fusedIntoProductionMetal` by component identity, never by inferring role from a geometric coincidence. |
| **INSPECT-GOV-009** | Production geometry and reference geometry must be inspected separately. Two distinct connectivity graphs always exist — `productionConnectivity` (metal only) and `fullAssemblyConnectivity` (includes `stone_reference`) — built via `jewelmind.geometry.roles.production_component_names()`. |
| **INSPECT-GOV-010** | Inspection output must use stable fact IDs. `GeometricFact.factId` is a deterministic, human-readable string (e.g. `component.band.volume`, `pair.band.prongs.minDistance`) — never a random UUID that would differ between two inspections of the same geometry. |
| **INSPECT-GOV-011** | Identical geometry under the same inspection version should produce equivalent geometric facts. Verified by `test_geometry_inspection.py::TestInspectionDeterminism` and `specs/geometry-inspection/v2/test-vectors/determinism-vectors.json` (two real, independent inspection runs of the same model). |
| **INSPECT-GOV-012** | Floating-point facts must use documented tolerances for comparison. `CONTACT_TOLERANCE_MM = 1e-6` (`version.py`) is a real kernel/geometric tolerance — one order of magnitude looser than OpenCascade's own `Precision::Confusion()` default of `1e-7` — never an invented jewelry tolerance. |
| **INSPECT-GOV-013** | Inspection must not mutate geometry. Every function in `shape.py`, `distance.py`, `intersection.py`, `topology.py`, `components.py`, `assembly.py` takes a shape and returns a new structured result — none calls `.fuse()`, `.cut()`, `.fillet()`, or any other geometry-mutating method on its input. |
| **INSPECT-GOV-014** | Inspection must not repair geometry silently. If a component is missing, disconnected, or invalid, inspection reports that fact (`INSPECTION_COMPONENT_MISSING`, a `DISCONNECTED` group, `shapeValid: false`) — it never attempts to fix the underlying shape. |
| **INSPECT-GOV-015** | Inspection facts must be traceable to components. Every `GeometricFact` carries `componentIds`; every `ComponentInspectionResult` carries `componentId`; every pairwise result names both `componentA`/`componentB` explicitly. |
| **INSPECT-GOV-016** | Forge must not depend on raw CadQuery/OCP objects. No field in `models.py` ever holds a `cadquery.Shape`, `cadquery.Workplane`, or `OCP` object — every value is a plain Python/Pydantic type (float, int, bool, str, list, or a nested inspection model). |
| **INSPECT-GOV-017** | Inspection facts supplied to Forge must use kernel-neutral structured values. `GeometricFact.value` is typed `float \| int \| bool \| str \| None` — the same discipline as INSPECT-GOV-016, restated at the flattened-fact level Forge would actually consume (see [`487-forge-fact-contract.md`](487-forge-fact-contract.md) for the current, honest state of that consumption — not yet wired up). |
| **INSPECT-GOV-018** | Expensive inspections must have explicit performance policy. [`491-runtime-inspection-policy.md`](491-runtime-inspection-policy.md) classifies every current inspection by real measured cost (component/topology/distance: cheap, run ALWAYS; pairwise intersection: noticeably more expensive, still run by default at the current 4-component scale, with broad-phase elimination via `intersection.should_skip_intersection()`). |
| **INSPECT-GOV-019** | Failed optional inspections must not automatically erase otherwise valid geometry. A `distance()`/`intersect()` kernel exception produces an `ERROR`/`UNKNOWN` result for that one pair — it never sets the whole `GeometryInspectionReport.status` to `FAIL` unless a required-component or diagnostic-severity condition is independently met. |
| **INSPECT-GOV-020** | Geometry regressions must be observable. [`492-inspection-regression-model.md`](492-inspection-regression-model.md) and `specs/geometry-inspection/v2/test-vectors/regression-vectors.json` establish a real baseline for the default solitaire, compared with tolerance in `test_geometry_inspection.py::TestInspectionRegression`. |

## Relationship to Atlas and Forge governance

This document sits alongside [`07-atlas/120-atlas-governance.md`](../07-atlas/120-atlas-governance.md) (Sprint 5) and [`06-forge/090-forge-governance.md`](../06-forge/090-forge-governance.md) (Sprint 4) — it does not supersede either. ATLAS-GOV-001/002 ("Atlas reports geometric facts; only Forge may interpret a fact as a jewelry-domain or manufacturing rule violation") is the exact architectural boundary this Sprint's entire subsystem exists to make real and runtime, rather than aspirational.

## When an ADR is required

Replacing the underlying kernel-query mechanism (moving off `cadquery.Shape.distance()`/`.intersect()`/`.isValid()`), changing the definition of "connected" away from a pure distance/contact tolerance, or any change that violates INSPECT-GOV-001 through 020 without superseding this document first.

## When an RFC is required

A new inspection family beyond component/assembly/connectivity/intersection/distance/topology (e.g. local-thickness analysis, curvature analysis, mesh manifold checks) — see [`494-current-runtime-inspection-gap-analysis.md`](494-current-runtime-inspection-gap-analysis.md) for the candidates already identified but explicitly deferred.
