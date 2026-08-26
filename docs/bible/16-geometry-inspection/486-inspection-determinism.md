---
id: JM-BIBLE-486
title: Inspection Determinism
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
  - JM-BIBLE-485
  - JM-BIBLE-492
implementation_status: current
professional_validation: not_required
normative: true
---

# Inspection Determinism

## INSPECT-GOV-011's real proof

> Identical geometry under the same inspection version should produce equivalent geometric facts.

Two independent, real proofs exist for this — one in the Python test suite, one in the machine-readable spec vectors — and both compare the same real quantities, deliberately with tolerance rather than exact equality.

## `backend/tests/test_geometry_inspection.py::TestInspectionDeterminism`

`test_inspecting_the_same_geometry_twice_produces_equivalent_facts` calls `inspect_model(model)` twice against the same `GeneratedModel` object and asserts, in order:

1. `report1.assemblyResult.componentCount == report2.assemblyResult.componentCount`
2. `report1.assemblyResult.productionConnectivity.connectedGroups == report2.assemblyResult.productionConnectivity.connectedGroups` — exact list equality (these are strings and structural groupings, not floats, so exact equality is appropriate here).
3. For each pair of `componentResults` (`zip(..., strict=True)`, one comparison per real component): `c1.solidCount == c2.solidCount` (exact integer equality), `c1.volumeMm3 == pytest.approx(c2.volumeMm3, rel=1e-9)`, `c1.boundingBox.sizeX == pytest.approx(c2.boundingBox.sizeX, rel=1e-9)`.
4. For each pair of `assemblyResult.intersections`: `i1.status == i2.status` (the categorical `INTERSECTS`/`TOUCHES`/`NO_INTERSECTION`/`UNKNOWN` value, not the raw volume).
5. Explicitly asserts the *opposite* for identity fields: `report1.inspectionId != report2.inspectionId` — proving the test author deliberately confirmed non-deterministic fields differ, rather than merely not checking them.

## Exactly which facts are checked for determinism

Per the brief's own list, cross-checked against the real test above: **volume** (`volumeMm3`, `rel=1e-9`), **bounding box size** (`boundingBox.sizeX`, `rel=1e-9` — one axis is checked directly in this test; the full box shares the same underlying `BoundingBox.from_shape()` computation), **solid count** (`solidCount`, exact), **component count** (`assemblyResult.componentCount`, exact), **connectivity groups** (`productionConnectivity.connectedGroups`, exact), and **intersection status** (`IntersectionResult.status`, exact categorical value, not the raw intersection volume itself).

**Only `inspectionId`/timestamps are expected and allowed to differ** between the two runs, per the brief's explicit instruction — the test enforces this directly by asserting inequality on `inspectionId`, rather than simply omitting it from the comparison.

## Why tolerance, not exact equality

Two independent `inspect_model()` calls against the *same in-memory `GeneratedModel` object* (as this test does) would, in practice, likely produce bit-identical floating-point results, since no new kernel operation reconstructs the shape between calls. The `pytest.approx(rel=1e-9)` tolerance is used anyway, consistent with [`08-alchemist/174-determinism-and-version-fingerprint.md`](../08-alchemist/174-determinism-and-version-fingerprint.md)'s finding that OCCT-kernel-derived floating-point values are not guaranteed bit-reproducible across different builds/platforms (that document cites a real observed Windows/Linux divergence in `combined_metal_volume_mm3`) — determinism here means "geometrically equivalent within a tight numerical tolerance," never "identical floating-point bit patterns," even at `rel=1e-9`, which is far tighter than the `regression-vectors.json` baseline comparison's `5%` tolerance (see [`492-inspection-regression-model.md`](492-inspection-regression-model.md) for that separate, looser comparison against a fixed historical baseline).

## `specs/geometry-inspection/v2/test-vectors/determinism-vectors.json`

Two recorded real runs against the default solitaire:

```json
{"run": 1, "componentCount": 4, "productionConnectedGroups": [["band", "basket_support", "prongs"]], "bandVolumeMm3": 250.99168317654699}
{"run": 2, "componentCount": 4, "productionConnectedGroups": [["band", "basket_support", "prongs"]], "bandVolumeMm3": 250.99168317654699}
```

Both runs report identical `componentCount`, identical `productionConnectedGroups`, and the identical `bandVolumeMm3` to full float precision in this recorded case — consistent with, but not itself proof of, the `rel=1e-9` tolerance the live Python test applies (this file is a fixed snapshot; the live test in `test_geometry_inspection.py` is what actually re-verifies the property on every test run).

## The schema-level reproducibility proof

`backend/tests/test_geometry_inspection_schemas.py::test_default_solitaire_example_is_reproducible_live` takes a different, complementary approach: it re-runs `inspect_model()` live against a fresh `build_solitaire_ring(default_definition())` call and compares the result against the *recorded example file* (`specs/geometry-inspection/v2/examples/default-solitaire-inspection.json`), not against a second live run. Before comparing, it strips `inspectionId`, `startedAt`, `completedAt`, and `performance` from the top level, and replaces every `geometricFacts[].generatedAt` with `None` — the same discipline Sprint 12's Conversation Engine reproducibility tests used for their own non-deterministic fields (per this Sprint's brief). This is a stronger check than the in-memory determinism test: it proves a *freshly rebuilt* model (not the same Python object) still produces equivalent facts to a run recorded on a prior occasion, catching pipeline drift the in-memory test alone could not.

## Cross-references

- [`485-inspection-versioning.md`](485-inspection-versioning.md) — determinism holds *for a fixed inspection version*; a version bump is a distinct, classified event, not a determinism violation.
- [`492-inspection-regression-model.md`](492-inspection-regression-model.md) — the separate, looser (5%) tolerance comparison against a fixed historical baseline, as opposed to this document's tight (`1e-9`) same-run/same-version comparison.
- [`08-alchemist/174-determinism-and-version-fingerprint.md`](../08-alchemist/174-determinism-and-version-fingerprint.md) — the geometric-vs-binary-reproducibility distinction this document's tolerance choice follows.
