---
id: JM-BIBLE-129
title: Mesh Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-122
related_documents:
  - JM-BIBLE-144
  - JM-BIBLE-146
implementation_status: current
professional_validation: not_required
normative: true
---

# Mesh Model

## B-Rep vs. mesh — the separation that must never collapse

**B-Rep is design/source geometry — exact, parametric, the only thing JewelMind's geometry code ever constructs. Mesh is a derived representation — an approximation, computed only when needed for preview or STL, and discarded afterward (never fed back into construction).** ATLAS-GOV-009 formalizes this: meshes must not become the source of B-Rep truth.

## Where meshing happens

| Use | Function | Tolerance source |
|---|---|---|
| Preview (per-component STL) | `component.shape.exportStl(path, tolerance, angularTolerance)` + `component.shape.tessellate(tolerance, angular)` for vertex/triangle counts | `definition.preview.meshTolerance` / `angularTolerance` (`preview/mesh.py`) |
| STL export (combined metal, or metal+stone) | `shape.exportStl(destination, tolerance=tolerance, angularTolerance=angular)` | Same defaults, overridable per export request (`exporters/stl_exporter.py`) |

Both paths ultimately call CadQuery's `Shape.mesh()`/`.tessellate()`/`.exportStl()`, which forward directly into OCCT's `BRepMesh_IncrementalMesh(shape, tolerance, True, angularTolerance)` — confirmed by inspecting the installed CadQuery source in Sprint 3 (see [`05-jdl/071-units-and-numeric-model.md`](../05-jdl/071-units-and-numeric-model.md)). `angularTolerance` is in **radians**.

## Tessellation and loss of parametric information

Tessellation is a one-way, lossy operation: a mesh cannot be converted back into the exact B-Rep it was derived from. Once a component is tessellated for preview, the resulting STL file carries no curve/surface parametrization, no feature history, and no way to recover exact dimensions beyond the mesh's own vertex precision (bounded by `meshTolerance`). JewelMind never attempts to reconstruct geometry from a mesh — every export always re-tessellates from the live B-Rep `GeneratedComponent.shape`, not from a previously-written STL file.

## STL must never become the canonical editable design representation

Stated explicitly, restating ATLAS-GOV-009 and CLAUDE.md's "never fake an export": the B-Rep solids held in `GeneratedModel`/`GeneratedComponent` are the only source of truth for a generated model's geometry. STL files (preview or export) are always a downstream, disposable artifact of that B-Rep — never read back in, never used to answer "what did this model actually measure," and never treated as equivalent to the parametric definition itself.

## Preview and export tessellation are not currently identical calls

Preview tessellates each of the four original components individually (`band`, `stone_reference`, `prongs`, `basket_support`, before fuse); STL export tessellates `combined_metal` (the fused-or-compound result, after fuse, excluding stone by default). Both use the same default tolerance values, but they are two separate tessellation operations on two different shape graphs — see [`144-preview-mesh-contract.md`](144-preview-mesh-contract.md) and [`146-stl-export-geometry-contract.md`](146-stl-export-geometry-contract.md) for the full contract, and open question `ATLAS-OQ-007` in [`151-open-atlas-questions.md`](151-open-atlas-questions.md) for whether they should ever be required to use identical settings.
