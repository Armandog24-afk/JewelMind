---
id: JM-BIBLE-468
title: Volume Inspection
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
  - JM-BIBLE-465
  - JM-BIBLE-142
implementation_status: current
professional_validation: not_required
normative: true
---

# Volume Inspection

## What is checked, and what is not recomputed

`component.volume_mm3` is already computed by each geometry builder at construction time (`GeneratedComponent.volume_mm3`, set from a real `.Volume()` call inside `band.py`/`stone.py`/`prongs.py`/`basket.py`). `inspect_component()` (`components.py`) does **not** call `.Volume()` again — it validates the value that is already there:

```python
volume = component.volume_mm3
volume_ok = volume is not None and volume >= 0.0 and volume == volume  # NaN check via self-equality
```

`volume == volume` is `False` only for `NaN` (per IEEE 754, `NaN` is never equal to itself, including itself) — this is a real, standard technique for detecting `NaN` without importing `math.isnan()`, not an ad hoc trick specific to this codebase. If `volume_ok` is `False`, an `INSPECTION_VOLUME_FAILED` diagnostic is appended and the component's `status` becomes `FAIL`.

## Real component volumes, default definition

| Component | Volume (mm³) |
|---|---|
| `band` | 250.99 |
| `stone_reference` | 58.22 |
| `prongs` (6-prong default) | 29.65 |
| `basket_support` | 83.16 |

`backend/tests/test_geometry_inspection.py::TestInspectionRegression::test_default_solitaire_matches_the_recorded_baseline_within_tolerance` asserts `band.volumeMm3 == pytest.approx(250.99, rel=0.05)` and `stone.volumeMm3 == pytest.approx(58.22, rel=0.05)` — a 5% relative tolerance, never exact floating-point equality, consistent with INSPECT-GOV-011/012's guidance to compare floating-point facts with documented tolerances.

## A pure geometric invariant, never a manufacturing interpretation

This check exists to catch a structurally broken solid — a required component whose volume is negative or non-finite is not a physically meaningful shape, regardless of what it is meant to represent. It is not, and must never become, a metal-weight estimate or a manufacturing-cost interpretation: `inspect_component()` never converts a volume into a mass (that would require a density, which is a jewelry-domain/material fact that belongs to Forge/`validation/`, not Inspection — see INSPECT-GOV-002), and never compares a volume against any expected or acceptable range. "This component's volume is 250.99 mm³" is the entire fact; "this is a reasonable band volume for this ring size" would be a Forge judgment this module does not and must not make.

## Relationship to `07-atlas/142-volume-and-bounding-box-inspection.md`

Sprint 5's [`142-volume-and-bounding-box-inspection.md`](../07-atlas/142-volume-and-bounding-box-inspection.md) documented the same real component volumes and recorded, as an explicit limitation, that "positive volume does not prove manufacturability" and that this property was verified only by `backend/tests/test_geometry.py` at development time, never re-checked for a real caller's input. This Sprint's `inspect_component()` closes exactly that runtime gap for volume finiteness/non-negativity: the same check Sprint 5 could only run in CI now runs on every real generation via `ModelService.generate()`. The explicit limitation itself (positive volume alone cannot detect self-intersection or a topologically broken interior that still integrates to a positive net volume) remains true and is restated, not resolved, by this Sprint — `inspect_topology()`'s `shapeValid` (see [`466-shape-validity-inspection.md`](466-shape-validity-inspection.md)) is the closest current check to that concern, and it is itself a binary validity check, not a defect classifier.

## Cross-references

[`464-component-inspection-contract.md`](464-component-inspection-contract.md) for the full per-component contract; [`465-assembly-inspection-contract.md`](465-assembly-inspection-contract.md) for how per-component volumes are summed into `totalProductionVolumeMm3` (a plain sum, not a re-derivation from `combined_metal.Volume()` — those two numbers differ by the `EMBED_MM`-driven overlap the fuse operation consumes, exactly as documented in `07-atlas/139-geometry-metadata-model.md`). `backend/tests/test_geometry_inspection.py::TestComponentVolumeInspection` and `TestInspectionRegression` exercise this directly.
