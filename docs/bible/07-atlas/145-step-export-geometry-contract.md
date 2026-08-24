---
id: JM-BIBLE-145
title: STEP Export Geometry Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-127
related_documents:
  - JM-BIBLE-079
implementation_status: current
professional_validation: not_required
normative: true
---

# STEP Export Geometry Contract

## Contract, exactly

`export_step(model, destination, *, include_stone=False)`:

- **Source geometry**: `model.combined_metal` (the fused-or-compound production metal), plus `model.components["stone_reference"].shape` if `include_stone=True`.
- **Production component inclusion**: always `combined_metal`, no per-sub-component opt-out (a caller cannot request "band only," for example).
- **Stone-reference exclusion default**: `include_stone=False` — matches LAW-006.
- **Multi-solid behavior**: if `combined_metal` is itself a 3-solid compound (the fuse fallback), STEP export still succeeds — `exportStep()` accepts a `TopoDS_Compound` directly.
- **Union behavior**: if `include_stone=True`, the two shapes (`combined_metal` + `stone_reference`) are wrapped in a *new* `cq.Compound.makeCompound([...])` for export purposes only — this compound is never fused, and is never stored back onto `GeneratedModel`; it exists only for the duration of this export call.
- **Units**: millimeters, implicitly — STEP files carry their own unit metadata, and CadQuery's `exportStep()` writes it consistently with the mm-based geometry (not independently verified in this Sprint beyond what `docs/geometry-conventions.md` already asserts for the whole system).
- **Filename handling**: `exporters/filenames.py::sanitize_filename()`, applied by the API layer before this function is called (not inside `export_step()` itself).
- **Failure handling**: any exception during `exportStep()` propagates to `ModelService.export_step_file()`, which deletes the empty/partial temp file and re-raises; the API layer converts this to `STEP_EXPORT_FAILED` (500).

## STEP is a neutral CAD exchange artifact, not a claim of professional equivalence

**STEP is not equivalent to a professional MatrixGold or Rhino project file.** It carries exact B-Rep geometry (ISO 10303), importable by professional CAD software, but nothing about the export process itself performs, checks, or claims any manufacturing-specific validation (draft angles, wall thickness for casting, support structures for printing). This restates LAW-010's manufacturing-readiness disclaimer specifically for the STEP artifact.

## Never a placeholder

`export_step()` always calls the real `.exportStep()` on real, previously-constructed OCCT geometry — there is no code path that writes a stub or sample STEP file, consistent with CLAUDE.md's "Never fake an export" rule.
