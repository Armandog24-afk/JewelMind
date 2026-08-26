---
id: JM-BIBLE-492
title: Inspection Regression Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
  - JM-BIBLE-QUALITY-README
related_documents:
  - JM-BIBLE-486
normative: true
implementation_status: current
professional_validation: not_required
---

# Inspection Regression Model

## The real baseline

`specs/geometry-inspection/v2/test-vectors/regression-vectors.json` is a real `GeometryFactSnapshot` baseline, captured from an actual run of `inspect_model()` against the default solitaire. Its one vector (`definitionHash: "355ddca57e7e49ad"`) records:

```json
{
  "definitionHash": "355ddca57e7e49ad",
  "componentCount": 4,
  "productionComponentCount": 3,
  "prongCount": { "requestedCount": 6, "generatedCount": 6, "matches": true, "status": "PASS" },
  "productionConnectivityFullyConnected": true,
  "componentVolumesMm3": {
    "band": 250.99168317654699,
    "stone_reference": 58.22141924499569,
    "prongs": 29.650351464580467,
    "basket_support": 83.15575842566426
  },
  "toleranceNote": "Compare with a relative tolerance (e.g. 5%), never exact float equality — see 486-inspection-determinism.md."
}
```

The `toleranceNote` field is itself normative guidance embedded in the fixture, not incidental — it exists precisely so nothing downstream is tempted into exact floating-point comparison, consistent with INSPECT-GOV-011/012 and [`486-inspection-determinism.md`](486-inspection-determinism.md)'s treatment of geometric-vs-binary reproducibility.

## The real automated regression test

`backend/tests/test_geometry_inspection.py::TestInspectionRegression::test_default_solitaire_matches_the_recorded_baseline_within_tolerance` is the working, currently-passing assertion of this baseline against a freshly-generated model:

```python
assert report.assemblyResult.componentCount == 4
assert report.assemblyResult.productionComponentCount == 3
assert report.assemblyResult.prongCount.generatedCount == 6
assert report.assemblyResult.productionConnectivity.isFullyConnected is True

band = next(c for c in report.componentResults if c.componentId == "band")
assert band.volumeMm3 == pytest.approx(250.99, rel=0.05)

stone = next(c for c in report.componentResults if c.componentId == "stone_reference")
assert stone.volumeMm3 == pytest.approx(58.22, rel=0.05)
```

This is a real, working test — it runs `inspect_model()` against a real generated model and compares against the recorded baseline with `pytest.approx(..., rel=0.05)` (5% relative tolerance), never exact equality. It is one of the 34 real tests in `backend/tests/test_geometry_inspection.py`, all currently passing.

## What the baseline is minimal about — a real, honest scope limit

The automated regression assertion above checks **four scalar counts/booleans and two component volumes** (band, stone reference). It does **not** assert:

- Connectivity edges (`ConnectivityGraph.edges`) — the raw vector JSON captures only `productionConnectivityFullyConnected` as a boolean, not the edge list.
- Intersection volumes (`IntersectionResult.intersectionVolumeMm3` for any pair) — not present in `regression-vectors.json` at all.
- Topology counts (`TopologyCounts.solids/shells/faces/edges/vertices`) — not present in the regression vector, even though they are computed and available on every `ComponentInspectionResult` returned by a real inspection.
- `prongs`/`basket_support` volumes — only `band` and `stone_reference` are asserted with a tolerance in the test; `prongs` and `basket_support` appear in the raw vector JSON's `componentVolumesMm3` but are not independently asserted in `TestInspectionRegression`.

These values genuinely exist and are genuinely captured in the raw test-vector JSON — the gap is specifically that the **automated regression assertions** do not yet compare them, not that the underlying facts are missing from the pipeline. This is a real, deliberate, honest scope limit for a minimal first regression baseline, not an oversight discovered after the fact.

## Where a richer baseline belongs

Expanding this regression model — snapshotting connectivity edges, intersection volumes, and topology counts as automated assertions, not just raw vector data — is explicitly out of scope for this Sprint and is the natural home for **Sprint 15, "Geometry Quality & Golden Models v1"**, cited here as the next sprint and a plausible target for this specific expansion (this document does not commit Sprint 15 to any other scope beyond this one item). See [`494-current-runtime-inspection-gap-analysis.md`](494-current-runtime-inspection-gap-analysis.md) for this gap listed alongside the others, and [`495-open-inspection-questions.md`](495-open-inspection-questions.md) (question on regression snapshot depth) for the open policy question this raises.

## Relationship to determinism

This regression model is a different concern from `TestInspectionDeterminism` (`backend/tests/test_geometry_inspection.py`), which asserts two independent inspection runs of the *same* geometry produce equivalent facts (INSPECT-GOV-011) — determinism is about repeatability within one code version; regression is about detecting an unintended *change* across code versions. Both are real and passing today, but they answer different questions and neither substitutes for the other. See [`486-inspection-determinism.md`](486-inspection-determinism.md) for the determinism side of this pair.

## Sprint 15 closed this document's own forward-reference

The "next sprint" this document named above is now real: [`docs/bible/17-geometry-quality/`](../17-geometry-quality/README.md) (Sprint 15, "Geometry Quality & Golden Models v1") built exactly the richer, multi-case regression baseline this document called out as missing — connectivity, intersection status, topology counts, and design-consistency facts are now all part of every accepted `GeometrySnapshot`, compared across 9 real solitaire variations rather than the single minimal vector described above. This document's own baseline and test remain unchanged and still real/passing; Sprint 15 is a separate, additive layer (`backend/jewelmind/geometry_quality/`), not a replacement of `inspect_model()`'s own regression assertion. See [`docs/bible/17-geometry-quality/504-regression-comparison-model.md`](../17-geometry-quality/504-regression-comparison-model.md).
