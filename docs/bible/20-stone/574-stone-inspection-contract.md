---
id: JM-BIBLE-574
title: Stone Inspection Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-STONE-README
  - JM-BIBLE-560
related_documents:
  - JM-BIBLE-460
  - JM-BIBLE-462
  - JM-BIBLE-577
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Inspection Contract

## What is inspected

A `stone_reference` component goes through the same generic component inspection every component does — presence, solid count, volume, bounding box, topology validity — plus **6 new stone-specific dimension facts** added in Sprint 18.

The generic facts are unchanged and are documented in [`../16-geometry-inspection/464-component-inspection-contract.md`](../16-geometry-inspection/464-component-inspection-contract.md); this document covers only what is new.

## The 6 new `FactType` values

Added to `geometry/inspection/models.py::FactType`, emitted by `inspector.py::_stone_dimension_facts()` for the `stone_reference` component only:

| `FactType` | Source | Classification |
|---|---|---|
| `STONE_REQUESTED_LENGTH` | `GeneratedComponent.metadata["lengthMm"]` | CONSTRUCTION_PARAMETER |
| `STONE_MEASURED_LENGTH` | `BoundingBoxFact.sizeY` | MEASURED_GEOMETRY |
| `STONE_REQUESTED_WIDTH` | `GeneratedComponent.metadata["widthMm"]` | CONSTRUCTION_PARAMETER |
| `STONE_MEASURED_WIDTH` | `BoundingBoxFact.sizeX` | MEASURED_GEOMETRY |
| `STONE_REQUESTED_DEPTH` | `GeneratedComponent.metadata["depthMm"]` | CONSTRUCTION_PARAMETER |
| `STONE_MEASURED_DEPTH` | `BoundingBoxFact.sizeZ` | MEASURED_GEOMETRY |

All six carry `unit: "mm"`, `scope: "COMPONENT"`, and `componentIds: ["stone_reference"]`. They are registered in `specs/geometry-inspection/v2/fact-registry.json` (now 22 fact types, registry version `1.1.0`) and catalogued in [`../appendices/geometry-fact-catalog.md`](../appendices/geometry-fact-catalog.md).

The fact registry is no longer verified against a hardcoded count. `test_geometry_inspection_schemas.py::test_fact_registry_covers_exactly_the_live_fact_type_values` derives the expected set from the live `FactType` literal via `get_args()`, so the registry cannot silently drift out of sync when a fact type is added — a small improvement prompted directly by this Sprint adding six.

## CONSTRUCTION_PARAMETER vs MEASURED_GEOMETRY

This pairing is the whole point of the design, and it mirrors Sprint 17's `widthSamplesMm` convention for the Shank.

- **`STONE_REQUESTED_*`** echoes back the value that was *fed into* the builder. It is honest about being a construction parameter: it proves nothing about the resulting solid.
- **`STONE_MEASURED_*`** is computed independently from the finished solid's real axis-aligned bounding box, via the same `bounding_box_fact()` every component already used.

Because the two come from genuinely different sources, a divergence between them is a real signal. Reporting only one would have been useless: the requested value alone cannot detect a scaling bug, and the measured value alone has nothing to be wrong *against*.

This is INSPECT-GOV-001 applied to stones: every fact is a measurement or an echoed parameter, never a judgement. No fact says "correct", "acceptable", or "too small" — Forge alone may interpret (INSPECT-GOV-002), and today no Forge rule consumes any `GeometricFact` at all (`forgeConsumptionStatus: "not_consumed"` for all 22).

## Comparison tolerance

The tests compare requested against measured with a **software geometry tolerance**, never a professional or manufacturing tolerance:

| Test | Tolerance |
|---|---|
| `TestStoneMeasuredDimensions::test_round_requested_and_measured_dimensions_match` | `abs=1e-3` mm |
| `TestStoneMeasuredDimensions::test_non_round_requested_and_measured_dimensions_match` | `abs=0.05` mm |

Real measured example, the default round stone:

| Fact | Value |
|---|---|
| `STONE_REQUESTED_LENGTH` | 6.5 |
| `STONE_MEASURED_LENGTH` | 6.5000002 |
| `STONE_REQUESTED_DEPTH` | 4.0 |
| `STONE_MEASURED_DEPTH` | 4.000000199999999 |

The ~2e-7 mm residual is OpenCascade bounding-box padding, not a geometry error. The non-round tolerance is looser (0.05 mm) because a lofted outline's extreme point need not land exactly on the nominal half-extent for every shape — an arc's discretised extremum can sit fractionally inside it. Both tolerances are comparison tools, chosen to absorb real kernel noise while still catching a genuine regression, which would be orders of magnitude larger. Neither is a claim about manufacturing precision.

## Known limitation: measurement under rotation

`STONE_MEASURED_LENGTH` and `STONE_MEASURED_WIDTH` read `sizeY` and `sizeX` of the **axis-aligned** bounding box. That isolates LENGTH from WIDTH exactly only at `stone.orientation == 0`.

At an arbitrary orientation the axis-aligned box no longer separates the two: a 9 × 5 oval rotated 45° has X and Y extents that are both larger than its width and smaller than its length, and neither corresponds to a real stone dimension. At exactly 90° the two swap cleanly (which is what `TestStoneOrientation::test_90_degree_rotation_swaps_bounding_box_extents` verifies), but that is a special case, not the general one.

This is stated as a real, documented limitation rather than assumed away. The honest consequence: **the requested-vs-measured comparison is a meaningful regression check at `orientation == 0`, and only a weak one at other angles.** An orientation-aware measurement — projecting onto the stone's own rotated local axes rather than the world axes — would fix it and is recorded as an open question in [`579-open-stone-questions.md`](579-open-stone-questions.md). The relevant docstring in `_stone_dimension_facts()` says the same thing in the code.

## What regressions this catches

At `orientation == 0`, a divergence between requested and measured detects:

- **Accidental scaling** — a factor-of-2 or unit error in the outline or dimension resolution.
- **Wrong shape** — an outline that produces different extents than requested (e.g. a shape falling back to another shape's builder, which STONE-GOV-013 forbids).
- **Changed depth** — a crown/pavilion fraction drift.
- **Axis swap** — a LENGTH/WIDTH mapping regression, since length is asserted against `sizeY` specifically.

Two further stone invariants are checked by pre-existing assembly facts rather than the new ones:

- **Lost StoneReference role** — `assemblyResult.stoneMetalSeparation.fusedIntoProductionMetal` must stay `False`, asserted by `TestStoneMeasuredDimensions::test_stone_reference_never_reported_as_production_metal`. This remains a **structural** check by component identity, never "zero intersection volume" — the stone legitimately intersects prongs and basket by design (INSPECT-GOV-008).
- **Component presence and solid count** — the generic `COMPONENT_PRESENT` / `SOLID_COUNT` facts, which would catch a shape silently producing no solid.

## Inspection is read-only

`_stone_dimension_facts()` reads `ComponentInspectionResult.metadata` and `.boundingBox` and constructs `GeometricFact` objects. It never touches the shape, and nothing in the inspection path mutates or repairs stone geometry (INSPECT-GOV-013/014). Every value it reports is a plain Python scalar — no `cadquery.Shape` or OCP object ever reaches a fact (INSPECT-GOV-016/017).

## Real recorded output

`specs/geometry-inspection/v2/examples/default-solitaire-inspection.json` and `four-prong-inspection.json` were regenerated from live code this Sprint and now each contain **42** geometric facts (up from 36 — the 6 new stone facts). Both are re-derived live and compared fact-by-fact by `test_geometry_inspection_schemas.py::test_default_solitaire_example_is_reproducible_live`.

## Coverage per shape

`TestStoneMeasuredDimensions::test_non_round_requested_and_measured_dimensions_match` is parametrized over all 6 non-round shapes at `9.0 × 5.0 × 3.5`, so every shape's requested-vs-measured agreement is genuinely exercised, not just oval's. Per STONE-GOV-015, a new shape must add its own inspection coverage.
