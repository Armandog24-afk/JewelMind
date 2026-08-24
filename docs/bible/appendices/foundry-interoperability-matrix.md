---
id: JM-BIBLE-A40
title: "Appendix: Foundry Interoperability Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-209
related_documents:
  - JM-BIBLE-210
  - JM-BIBLE-211
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Foundry Interoperability Matrix

| Format | Target | Level | Basis |
|---|---|---|---|
| STEP | CadQuery/OpenCascade (self) | `IMPORT_TESTED` (self-consistency only) | `cadquery.importers.importStep()` roundtrip, Sprint 7 |
| STEP | FreeCAD | `EXPORT_SUPPORTED` only | Never installed or tested |
| STEP | Rhino | `EXPORT_SUPPORTED` only | Commercial license not obtained, per CLAUDE.md |
| STEP | MatrixGold (via Rhino) | `EXPORT_SUPPORTED` only | Depends on Rhino |
| STEP | Autodesk Fusion | `EXPORT_SUPPORTED` only | No license available |
| STL | This codebase (structural self-validation) | `IMPORT_TESTED`-equivalent | `binary_stl_triangle_count()`, Sprint 7 |
| STL | 3D-printing slicers | `EXPORT_SUPPORTED` only | No specific slicer tested |
| STL | Mesh-inspection tools | `EXPORT_SUPPORTED` only | Not tested |
| STL | Physical prototyping services | `EXPORT_SUPPORTED` only | No physical print produced |

**`WORKFLOW_VALIDATED` claims made: 0.** **Real, recorded `IMPORT_TESTED` results against an independent third-party application: 0** (the one `IMPORT_TESTED` entry above is CadQuery re-importing its own output, explicitly not counted as independent — see [`09-foundry/209-cad-interoperability-philosophy.md`](../09-foundry/209-cad-interoperability-philosophy.md)).
