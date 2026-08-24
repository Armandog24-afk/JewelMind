---
id: JM-BIBLE-146
title: STL Export Geometry Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-129
related_documents:
  - JM-BIBLE-079
implementation_status: current
professional_validation: not_required
normative: true
---

# STL Export Geometry Contract

## Contract, exactly

`export_stl(model, definition, destination, *, include_stone=False, mesh_tolerance=None, angular_tolerance=None)`:

- **Source B-Rep**: `model.combined_metal` (identical source shape to STEP export), plus `stone_reference` if requested.
- **Tessellation**: `shape.exportStl(destination, tolerance=tolerance, angularTolerance=angular)`, where `tolerance`/`angular` default to `definition.preview.meshTolerance`/`angularTolerance` unless the request explicitly overrides them.
- **Mesh tolerance / angular tolerance**: same defaults as preview (0.1mm / 0.2 radians), independently overridable per export request via `api/schemas.py::ExportStlRequest`.
- **Stone-reference exclusion**: same default (`False`) as STEP.
- **Multi-component strategy**: `exportStl()` accepts a multi-solid compound directly — if `combined_metal` is the 3-solid fuse-fallback, every solid is written into the one STL file; no component is dropped (matches `docs/known-limitations.md`'s "no component is silently dropped" statement).
- **Unit expectations**: millimeters, matching the source B-Rep exactly — STL itself has no unit metadata, so the exported triangle coordinates are simply the mm-valued B-Rep coordinates.
- **Limitations**: a single mesh-tolerance/angular-tolerance pair applies to the entire exported shape (whether one fused solid or three compound solids) — there is no per-component tolerance override for a combined export.

## STL is not parametric; STL is not the source of truth

Restating [`129-mesh-model.md`](129-mesh-model.md) specifically for this artifact: the exported STL file cannot be edited to change `band.width` or any other JDL parameter — it is a one-way, disposable derivative of the B-Rep. Every STL export is freshly tessellated from the live `GeneratedModel`, never read back from a previously-written file.

## Relationship to preview tessellation

STL export tessellates `combined_metal` (the fused/compound production-metal shape, post-fuse); preview tessellates each of the four original pre-fuse components individually (see [`144-preview-mesh-contract.md`](144-preview-mesh-contract.md)). These are genuinely two different tessellation operations over two different shape graphs, even though they typically use the same default tolerance values — see open question `ATLAS-OQ-007` in [`151-open-atlas-questions.md`](151-open-atlas-questions.md) for whether they should ever be required to match exactly.
