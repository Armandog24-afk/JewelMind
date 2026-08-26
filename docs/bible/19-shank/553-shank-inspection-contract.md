---
id: JM-BIBLE-553
title: Shank Inspection Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-542
  - JM-BIBLE-554
implementation_status: current
professional_validation: not_required
normative: true
---

# Shank Inspection Contract

## What runtime inspection sees today: generic component inspection only

`backend/jewelmind/geometry/inspection/` currently has no Shank-specific or `band`-specific inspection code path and no dedicated Shank `FactType`. The `band` component produced by `build_shank()` is inspected exactly like every other component (`stone_reference`, `prongs`, `basket_support`) via `geometry/inspection/inspector.py::_component_facts()`, which emits, for any `ComponentInspectionResult`: `COMPONENT_PRESENT` (does it exist), `SOLID_COUNT` (`Shape.Solids()`), `VOLUME` (`Shape.Volume`), `SHAPE_VALID` (`Shape.isValid()`), and, when a bounding box was computed, `BOUNDING_BOX`. These are the only `FactType` values `geometry/inspection/models.py` currently defines that apply to a single component; `FactType`'s full enum (`SHAPE_EXISTS`, `SHAPE_VALID`, `SOLID_COUNT`, `VOLUME`, `BOUNDING_BOX`, `COMPONENT_COUNT`, `INTERSECTION_EXISTS`, `INTERSECTION_VOLUME`, `MIN_DISTANCE`, `CONNECTED`, `DISCONNECTED`, `COMPONENT_PRESENT`, `PRONG_COUNT`, `STONE_METAL_SEPARATE`, `BOOLEAN_RESULT_VALID`, `FALLBACK_USED`) has no member for width, thickness, or any per-`u` measurement of a shank's cross-section — none was added this Sprint.

This means whether a tapered shank's actual solid measures the width/thickness it was asked to build, at any given angular position, is not something `inspect_model()` checks today. Inspection confirms the `band` component exists, is a single valid solid, has some volume and bounding box — the same generic checks every component receives — and nothing more specific to Shank's own construction.

## CONSTRUCTION_PARAMETER vs MEASURED_GEOMETRY

`_build_tapered_shank()`'s metadata includes `widthSamplesMm`/`thicknessSamplesMm` (each `{headMm, bottomMm}`), but these are computed from the same `taper_ratio()` calls that built the loft's section wires in the first place — `builder.py` calls `taper_ratio(0.0, width_taper)` and `taper_ratio(0.5, width_taper)` a second time purely to populate this metadata, not by re-examining the resulting solid. They are **CONSTRUCTION_PARAMETER** facts: values that were fed into (or directly derived from the same function that fed) the geometry construction, not values independently re-measured from the geometry that resulted. This distinction is INSPECT-GOV-001's own framing — a `GeometricFact` reports a measurement, and INSPECT-GOV-002 keeps that reporting free of jewelry-domain judgment — applied honestly here to note that these two particular values are not measurements in the inspection sense at all; they never pass through `geometry/inspection/` and are not part of any `GeometryInspectionReport`.

SHANK-GOV-013 states this distinction as governance: Shank must report geometric facts, distinguishing CONSTRUCTION_PARAMETER from MEASURED_GEOMETRY, never a jewelry-domain judgment, and `widthSamplesMm`/`thicknessSamplesMm` are documented as CONSTRUCTION_PARAMETER exactly because they are computed, not measured.

## The real, honest gap

There is no dedicated per-section or per-`u` **MEASURED_GEOMETRY** fact for a shank's width or thickness anywhere in the current inspection package — nothing independently re-measures, say, the actual radial thickness of the resulting solid at `u=0.25` from the solid itself (e.g. via a cross-sectional slice or distance query), the way `MIN_DISTANCE`/`INTERSECTION_VOLUME` independently measure distance and intersection between two component solids today. This is a real, identified gap, not a silent omission: it is recorded here as PLANNED, not implemented.

Adding such a fact would require a new `FactType` member in `geometry/inspection/models.py`, a new measurement function under `geometry/inspection/` (following the existing pattern of `distance.py`/`intersection.py`/`topology.py`), and an entry in `specs/geometry-inspection/v2/fact-registry.json` with an honest `implementationStatus`, per [`460-inspection-governance.md`](../16-geometry-inspection/460-inspection-governance.md)'s own update requirement. If that new fact were ever intended to feed a Forge rule (rather than remain purely informational), it would additionally require its own RFC under the "new rule family" process in [`06-forge/090-forge-governance.md`](../06-forge/090-forge-governance.md), since evaluating a jewelry-domain threshold against a per-section measurement rather than a single base value is a new kind of rule semantics, not an extension of an existing one — see [`554-shank-forge-boundary.md`](554-shank-forge-boundary.md) for the Forge-side half of this same gap.

## Generic facts still catch real regressions

Even without a Shank-specific fact type, the generic `VOLUME`/`BOUNDING_BOX`/`SOLID_COUNT`/`SHAPE_VALID` facts are exactly what feeds the Golden Suite's `compare_snapshot()` comparison for the `band` component on every case, including the three new taper cases SOL-010/011/012 (see [`555-shank-golden-strategy.md`](555-shank-golden-strategy.md)). A regression that changed a tapered shank's actual volume or bounding box — for example, an accidental change to `SECTION_COUNT` or the interpolation formula — would still be caught by these generic facts even though no fact independently confirms the per-`u` width/thickness driving that volume. What the current facts cannot catch is a regression that preserves overall volume and bounding box while distributing width/thickness incorrectly along the shank's length (e.g. swapping which end tapers) — that class of defect is exactly what the identified gap above would close if implemented.

## Why this boundary is preserved deliberately

`geometry/shank/` reporting only CONSTRUCTION_PARAMETER samples, and inspection reporting only generic component facts, keeps the Atlas/Forge boundary intact for this subsystem exactly as it is everywhere else: Shank and Inspection report facts; only Forge interprets a fact as satisfying or violating a jewelry-domain rule (INSPECT-GOV-002, restated by SHANK-GOV-013 for this subsystem specifically). Neither `geometry/shank/` nor `geometry/inspection/` imports `jewelmind.validation`, and no numeric jewelry threshold exists in either package — verified by inspecting both packages' imports directly.

## Summary of the current inspection surface for Shank

| What | Source | Kind |
|---|---|---|
| `COMPONENT_PRESENT`, `SOLID_COUNT`, `VOLUME`, `SHAPE_VALID`, `BOUNDING_BOX` | `geometry/inspection/inspector.py::_component_facts()` | MEASURED_GEOMETRY (generic, applies to every component including `band`) |
| `widthSamplesMm`/`thicknessSamplesMm` (`headMm`/`bottomMm`) | `builder.py::_build_tapered_shank()` metadata | CONSTRUCTION_PARAMETER (tapered only; never passes through `geometry/inspection/`) |
| Per-`u` independently measured width/thickness | — | Does not exist (PLANNED gap, see above) |

This table is the complete current state; no other row exists for Shank in either the real fact registry or the metadata shapes documented in [`542-shank-domain-model.md`](542-shank-domain-model.md). Any future addition to this table must be made in the same change as the corresponding code change, per this document's own governing rule — never documented ahead of the implementation it describes.

## Reading this alongside the fact registry

`specs/geometry-inspection/v2/fact-registry.json` is the machine-readable source of truth for every `FactType` and its `implementationStatus`/`forgeConsumptionStatus`; this document's table above is a Shank-focused narrative view of that same underlying registry, not a competing source. If the two ever appear to disagree, the fact registry is authoritative and this document should be corrected to match it, per the same discipline [`460-inspection-governance.md`](../16-geometry-inspection/460-inspection-governance.md) applies everywhere else in the Geometry Inspection section.
