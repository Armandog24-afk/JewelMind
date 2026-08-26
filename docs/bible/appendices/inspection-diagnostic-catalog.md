---
id: JM-BIBLE-A96
title: "Appendix: Inspection Diagnostic Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-483
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Inspection Diagnostic Catalog

The 11 real `InspectionDiagnosticCode` values (`backend/jewelmind/geometry/inspection/diagnostics.py`). An inspection diagnostic never implies geometry invalidity on its own — see [`483-inspection-error-model.md`](../16-geometry-inspection/483-inspection-error-model.md).

| Code | Meaning | Actually raised today? (verified by grep) |
|---|---|---|
| `INSPECTION_COMPONENT_MISSING` | A required component produced no solids. | **Yes** — `components.py` |
| `INSPECTION_SHAPE_INVALID` | `Shape.isValid()` reported a defect. | No — schema-complete, unreachable |
| `INSPECTION_VOLUME_FAILED` | A component's volume was non-finite or negative. | **Yes** — `components.py` |
| `INSPECTION_BOUNDING_BOX_FAILED` | A kernel bounding-box computation raised. | **Yes** — `components.py` |
| `INSPECTION_CONNECTIVITY_FAILED` | Connectivity-graph construction failed. | No — schema-complete, unreachable |
| `INSPECTION_INTERSECTION_FAILED` | A boolean-common (intersection) call raised. | No — see note below |
| `INSPECTION_DISTANCE_FAILED` | A distance call raised. | No — see note below |
| `INSPECTION_TOPOLOGY_FAILED` | A topology-count query raised. | **Yes** — `components.py` |
| `INSPECTION_KERNEL_UNAVAILABLE` | The kernel itself was unavailable. | No — schema-complete, unreachable |
| `INSPECTION_UNSUPPORTED` | This inspection is not supported for this object. | No — schema-complete, unreachable |
| `INSPECTION_INTERNAL_ERROR` | An unexpected internal failure. | No — schema-complete, unreachable |

## A real gap worth stating plainly

`distance.py`/`intersection.py` do **not** import or construct `InspectionDiagnostic` at all — a kernel exception in either module is reflected only in the result's own `status` field (`"ERROR"`/`"UNKNOWN"`), never surfaced as a diagnostic entry in `GeometryInspectionReport.diagnostics`. This means `INSPECTION_DISTANCE_FAILED` and `INSPECTION_INTERSECTION_FAILED` are real, well-named codes with no current code path that ever constructs them — a genuine, minor documentation-vs-code gap, not a hidden defect (the failure is still honestly reported via `status`, just not doubly reported as a diagnostic). See [`494-current-runtime-inspection-gap-analysis.md`](../16-geometry-inspection/494-current-runtime-inspection-gap-analysis.md).

Only 4 of the 11 codes are actually reachable in the current codebase — the same honest schema-complete-but-unreachable pattern used throughout every prior sprint's own diagnostic/status vocabularies.

## Cross-references

- [`483-inspection-error-model.md`](../16-geometry-inspection/483-inspection-error-model.md) — full narrative and the rule that a diagnostic never implies invalidity unless a required invariant is violated.
- `backend/tests/test_geometry_inspection.py::TestInspectionErrorRecovery` — the real tests proving a kernel failure returns `UNKNOWN`/`ERROR`, never a crash.
