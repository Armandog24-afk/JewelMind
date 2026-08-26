---
id: JM-BIBLE-509
title: Artifact Regression Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-500
related_documents:
  - JM-BIBLE-503
  - JM-BIBLE-504
  - JM-BIBLE-209
implementation_status: current
professional_validation: not_required
normative: true
---

# Artifact Regression Model

`backend/jewelmind/geometry_quality/artifact_regression.py` implements the `ARTIFACT_REGRESSION` signal type (QUALITY-GOV-007/008): checking that STEP/STL export still behaves correctly, without ever requiring byte-for-byte equality.

## STEP: export → re-import → compare facts, never bytes

`step_roundtrip_check(model: GeneratedModel) -> list[ArtifactChange]` exports the model's production metal (`export_step(model, destination, include_stone=False)`), re-imports it with `cadquery.importers.importStep()`, and compares three real facts between the *source shape that was exported* and the *re-imported shape*:

1. **Solid count** — `len(model.combined_metal.Solids())` vs. `len(reimported.val().Solids())`. If the re-import produces zero solids at all, that alone is reported and the function returns early.
2. **Volume** — `model.combined_metal_volume_mm3` vs. `shape.Volume()`, compared with `_numeric_close()` (the same absolute-OR-relative tolerance logic as [`505-comparison-tolerance-policy.md`](505-comparison-tolerance-policy.md)'s `ABSOLUTE_COMPARISON_TOLERANCE_MM`/`RELATIVE_COMPARISON_TOLERANCE`).
3. **Bounding box** — `sizeX`/`sizeY`/`sizeZ` from `bounding_box_fact()` on the source shape vs. the re-imported shape, same tolerance.

### Why never bytes (QUALITY-GOV-007/008)

CadQuery's STEP writer embeds variable OpenCascade metadata — a generation timestamp, a GUID, product-definition counters — that differ between two exports of *identical* input geometry. This is proven directly, not assumed: `test_two_step_exports_of_identical_geometry_are_not_byte_identical` (`backend/tests/test_geometry_quality_artifacts.py`) exports the same default solitaire's STEP twice, SHA-256-hashes both files, and deliberately does **not** assert the checksums are equal — the test's own comment states OpenCascade's STEP writer "embeds a variable timestamp/GUID even for identical input geometry," and golden verification must never depend on that being stable. A second test, `test_step_roundtrip_check_never_compares_raw_bytes`, inspects `step_roundtrip_check`'s own source and asserts neither `"sha256"` nor `"read_bytes"` appears in it — a structural guarantee, the same discipline `TestNoAutoUpdate` applies to `save_golden` (see [`507-golden-update-policy.md`](507-golden-update-policy.md)).

## STL: structural check, never mesh volume

`stl_structure_check(model, definition) -> list[ArtifactChange]` exports the model's production metal to STL (`export_stl(model, definition, destination, include_stone=False)`) and checks:

1. **Non-empty file** — `destination.stat().st_size != 0`.
2. **Non-zero triangle count** — via the existing `exporters/integrity.py::binary_stl_triangle_count()`, which reads only the binary STL header (an 80-byte header plus a little-endian `uint32` triangle count at bytes 80–84) without a full parse.
3. **Approximate bounding-box consistency** — a new lightweight full parse, `_binary_stl_bounding_box()` (defined in `artifact_regression.py`, not `integrity.py`), reads every triangle's three vertices (12 floats per 50-byte record: a 3-float normal, then three 3-float vertices) and computes min/max X/Y/Z across all of them. This is compared against `model.bounding_box` (the exact B-Rep bounding box) with `loose_tolerance_mm = ABSOLUTE_COMPARISON_TOLERANCE_MM * 100` plus an additional flat `1.0mm` margin on each side, since mesh tessellation can slightly over/undershoot the exact B-Rep extent — a deliberately looser check than the standard numeric tolerance, for this comparison only.

No mesh **volume** comparison is performed for STL, because no reliable tooling exists in this repository for computing a trustworthy mesh-derived volume from a raw triangle soup — the structural checks above (non-empty, non-zero triangles, bounding-box sanity) are the real, implemented STL regression signal; nothing stronger is silently assumed to also be checked.

## STL checksum: supplemental, never primary

The module's own docstring notes STL, unlike STEP, is a pure triangulation with no embedded metadata, so a checksum *could* in principle serve as supplemental evidence alongside the primary structural check. No current code in `stl_structure_check()` actually computes or compares an STL checksum — the structural checks above are what's implemented; this is noted here only to avoid implying a checksum comparison exists that does not.

## Golden STEP roundtrip is NOT external CAD interoperability validation

`step_roundtrip_check()`'s re-import uses `cadquery.importers.importStep()` — the same CadQuery/OpenCascade library that wrote the file in the first place. Per [`09-foundry/209-cad-interoperability-philosophy.md`](../09-foundry/209-cad-interoperability-philosophy.md)'s own three-level distinction (`EXPORT_SUPPORTED` / `IMPORT_TESTED` / `WORKFLOW_VALIDATED`), that document already classifies this exact kind of self-import as a **self-consistency check**, explicitly **not** an `IMPORT_TESTED` result against a genuinely separate application — CadQuery importing its own STEP output proves the file is well-formed STEP, nothing about whether Rhino, MatrixGold, or any other real jewelry-CAD application can open it. This Sprint's Golden regression harness inherits that exact same limitation for the identical reason (it calls the identical `cadquery.importers.importStep()` function) and does not attempt to close it — closing it remains Sprint 7/Foundry's separate domain, and whatever real external-tool testing eventually happens belongs in [`15-professional-validation/424-cad-workflow-validation-process.md`](../15-professional-validation/424-cad-workflow-validation-process.md)'s process, not in this subsystem. See [`514-professional-validation-boundary.md`](514-professional-validation-boundary.md) for the fuller boundary statement.

## Interaction with severity (see 504 for the full rule)

A real artifact change always escalates a `GeometryDiff`'s `severity` to at least `REGRESSION` — from `NONE` or from `INFO` (an unrelated within-tolerance numeric change never masks it). See [`504-regression-comparison-model.md`](504-regression-comparison-model.md#how-artifact-checks-fold-into-severity) for the exact rule and its regression test.
