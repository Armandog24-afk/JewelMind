---
id: JM-BIBLE-466
title: Shape Validity Inspection
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
  - JM-BIBLE-464
  - JM-BIBLE-467
  - JM-BIBLE-128
implementation_status: current
professional_validation: not_required
normative: true
---

# Shape Validity Inspection

## What was actually investigated this Sprint

The Sprint 14 brief required this specific check to be grounded in a real investigation, not an assumed API. The investigation ran in this order:

1. `cadquery==2.8.0` was confirmed installed and importable in the backend's real virtual environment (the same one `pytest` runs against).
2. OCP's `BRepCheck_Analyzer` was confirmed importable and directly callable: `from OCP.BRepCheck import BRepCheck_Analyzer`. This is the actual OpenCascade class that performs shape validity/defect checking.
3. A simpler path was found and used instead of calling `BRepCheck_Analyzer` directly: `cadquery.Shape.isValid()` is itself a thin wrapper around exactly the same analyzer. Its real docstring (quoted verbatim, not paraphrased):

   > "Returns True if no defect is detected on the shape S or any of its subshapes. See the OCCT docs on BRepCheck_Analyzer::IsValid for a full description of what is checked."

`shape.py::shape_is_valid()` calls `shape.isValid()` directly — there is no separate direct `BRepCheck_Analyzer` call anywhere in `backend/jewelmind/geometry/inspection/`; going through CadQuery's own wrapper is both simpler and exercises the exact same underlying OCCT analyzer.

## Real measured timing

Single-digit-to-low-double-digit milliseconds per component: `band`, `stone_reference`, `prongs`, `basket_support` each measured at 1–3ms; `combined_metal` (the fused, larger, more topologically complex body) measured at roughly 17ms. This is cheap enough to run unconditionally on every generation — the basis for INSPECT-GOV-018's classification of shape validity as an "always run" inspection, alongside component/topology/distance checks generally.

## Real result on current generated geometry

Every current solitaire component — `band`, `stone_reference`, `prongs`, `basket_support` — and the fused `combined_metal` shape reports `isValid() == True` on real generated geometry for the default definition (and every other definition exercised by `backend/tests/test_geometry.py`/`test_geometry_inspection.py`). No invalid shape has been observed from this codebase's own geometry builders during this Sprint's investigation.

## `inspect_topology()`'s isolation of this specific check

`topology.py::inspect_topology()` wraps the `shape_is_valid()` call in its own `try`/`except Exception`, separate from the `try`/`except` around `topology_counts()`. If `isValid()` itself raises (as opposed to returning `False`), the function returns `(counts, None, "ERROR")` — `counts` is still returned if it succeeded, so a validity-check failure never silently discards topology counts that were already computed successfully.

## A real, honest scope limit — not a gap to apologize for

`Shape.isValid()` is a **binary** result: valid or not valid. This Sprint's investigation did not find (and did not attempt to add) any reliable way to surface *which* specific defect, if any, `BRepCheck_Analyzer` detected — OCCT's analyzer supports enumerating individual `BRepCheck_Status` values per subshape, but no code in this Sprint calls that deeper API, and `ComponentInspectionResult.shapeValid` remains a plain `bool | None`. This is stated here plainly as a real, current scope limit, not classified as `NOT_IMPLEMENTED` — the check that *is* implemented (binary validity) is real and runs on every generation; a deeper defect-classification check simply does not exist in any form yet. A future Sprint wanting per-defect classification would need a genuinely new module, not an extension of `shape_is_valid()`'s current contract, and would need its own investigation before being described as implemented.

## Cross-references

[`464-component-inspection-contract.md`](464-component-inspection-contract.md) for how `shapeValid` fits into the full per-component result; [`467-solid-count-inspection.md`](467-solid-count-inspection.md) for the sibling topology check computed in the same `inspect_topology()` call; [`07-atlas/128-brep-and-topology-model.md`](../07-atlas/128-brep-and-topology-model.md) for Atlas's own prior (Sprint 5) documentation of B-Rep/topology concepts, which anticipated this exact check as `PLANNED`/`UNKNOWN` before this Sprint made it real and runtime. `backend/tests/test_geometry_inspection.py::TestComponentExistsInspection` and the broader `TestInspectionRegression`/`TestInspectionDeterminism` classes exercise this path indirectly via `inspect_component()`.
