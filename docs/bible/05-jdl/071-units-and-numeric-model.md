---
id: JM-BIBLE-071
title: Units and Numeric Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-070
related_documents:
  - JM-BIBLE-065
implementation_status: current
professional_validation: not_required
normative: true
---

# Units and Numeric Model

## Angular tolerance unit — verified, not guessed

`preview.angularTolerance` is passed to CadQuery's tessellation call as `angularTolerance` (see `backend/jewelmind/preview/mesh.py` and `backend/jewelmind/exporters/stl_exporter.py`, both of which forward it into `Shape.tessellate()`/`Shape.mesh()`). Inspecting the installed CadQuery source directly (`inspect.getsource`) during this Sprint shows:

```python
def mesh(self, tolerance: float, angularTolerance: float = 0.1) -> None:
    if not BRepTools.Triangulation_s(self.wrapped, tolerance):
        BRepMesh_IncrementalMesh(self.wrapped, tolerance, True, angularTolerance)
```

`BRepMesh_IncrementalMesh` is OpenCascade's native tessellation constructor, whose angular-deflection parameter OCCT documents in **radians**. This was confirmed by reading CadQuery's actual installed source in this Sprint, per the explicit instruction not to guess. The current default, `0.2`, is therefore 0.2 radians (~11.46°), not 0.2 degrees.

## Internal, display, and canonical units

| Axis | Value |
|---|---|
| Internal unit (what the CAD kernel operates in) | Millimeters for all lengths; radians for `angularTolerance` |
| Canonical unit (what a JDL document declares) | Millimeters for all lengths (`project.units: "mm"` is a fixed literal); radians for `angularTolerance`, undocumented-as-a-unit-string because there is no `units` field for angles today |
| Display unit (what the frontend shows) | Millimeters, unchanged — `frontend/src/components/*` render the same numeric values with an "mm" suffix in labels; no conversion occurs anywhere in the UI layer |

There is exactly one unit system in play for lengths (millimeters) and one for the one angular field (radians) — no display-vs-storage divergence exists in the current codebase.

## Precision

Pydantic `float` fields use standard IEEE-754 double precision, with no explicit rounding or truncation applied at the schema layer. `sizing.py::sizing_consistency()` rounds a *suggested* value to 2 decimal places for display purposes only (`round(implied, 2)`); this rounding never touches the stored `ring.innerDiameter` or `ring.size` values themselves.

## Hashing implications

Because canonicalization serializes the exact float value Pydantic holds (see [`076-canonicalization-and-definition-hashing.md`](076-canonicalization-and-definition-hashing.md)), two documents that are numerically equal but written with different literal text (`16` vs `16.0000`) produce the *same* hash once parsed into a `float` field — Python's `json.dumps` renders both as `16.0`. Two documents that differ by even a single unit in the last place of a `float` produce different hashes; there is no numeric tolerance/rounding applied before hashing.

## Prohibited numeric forms (all currently enforced or currently guaranteed impossible)

| Form | Status |
|---|---|
| `NaN` | Impossible to construct a `JewelryDefinition` with one — `allow_inf_nan=False` on every `float` field |
| `Infinity` / `-Infinity` | Same as above |
| Locale-formatted numbers with commas (`"1,234.5"`) | Rejected — Pydantic strict mode requires a real JSON number, not a numeric-looking string, for any `float`/`int` field |
| Numeric values passed as strings (`"2.4"` for `band.width`) | Rejected in strict mode, per the `StrictModel` docstring in `backend/jewelmind/domain/schema.py` |
| Hidden unit conversion | Never occurs — a value is stored and used exactly as received; there is no inches/points/other-unit code path anywhere (LAW-007) |

## What this document does not do

It does not introduce a distinct `Angle` JDL type (see [`070-type-system.md`](070-type-system.md) for why) and does not propose changing the current radians-based `angularTolerance` default — that is an existing, tested behavior, not a Sprint 3 decision.
