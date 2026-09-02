---
id: JM-BIBLE-614
title: "Stone Inspection v2"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-600
related_documents:
  - JM-BIBLE-615
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Inspection v2

Geometry Inspection gained 17 stone fact types in Sprint 20, bringing the live
`FactType` literal to 47 and the fact registry to version 1.3.0.

## The Atlas/Forge boundary holds

Every fact reports **what a stone is**, never whether it is any good:

- `STONE_SOURCE_MODE` says `MEASURED`. It does not say measured stones are
  preferable.
- `STONE_REPRESENTATION` says `MESH`. It does not say a mesh is inadequate.
- `STONE_OUTLINE_AVAILABLE` says `false` for a pearl. It does not say a pearl
  cannot be set — that interpretation belongs to the Setting capability registry
  and to Forge (INSPECT-GOV-001/002).

No file under `geometry/inspection/` imports `jewelmind.validation` or
references a Forge rule ID, and none of the 17 new facts is consumed by a Forge
rule (`forgeConsumptionStatus: not_consumed` for all of them). Saying so is
honest; claiming they drive rules would not be.

## The facts

| Fact | Reports |
|---|---|
| `STONE_SOURCE_MODE` | which of the four source modes produced the stone |
| `STONE_SHAPE_IDENTITY` | the canonical cut (a cut, never a gem species) |
| `STONE_PROFILE_IDENTITY` | faceted / cabochon / spherical |
| `STONE_SHAPE_FAMILY` | the geometry-reuse family |
| `STONE_SYMMETRY_CLASS` | radial / bilateral / asymmetric / unknown |
| `STONE_REPRESENTATION` | parametric / B-Rep solid / mesh |
| `STONE_DIMENSION_PROVENANCE` | requested / measured / imported / derived |
| `STONE_MEASURED_REFERENCE_CLASS` | dimension-reference vs outline-reference |
| `STONE_OUTLINE_AVAILABLE` | whether a normalized outline exists |
| `STONE_OUTLINE_POINT_COUNT` | exact vertex count, or sampling resolution |
| `STONE_ANCHOR_COUNT` | how many deterministic anchors were derived |
| `STONE_ORIENTATION_DEG` | applied rotation about the local vertical |
| `STONE_GENERATOR_VERSION` | which construction built it |
| `STONE_IMPORTER_VERSION` | which normalization pipeline ran |
| `STONE_SOURCE_ASSET_HASH` | the imported asset's content hash |
| `STONE_NORMALIZATION_OPERATION_COUNT` | how many operations were applied |
| `STONE_IS_PRODUCTION_METAL` | structurally always `false` (LAW-006) |

Plus Sprint 18's six requested-vs-measured dimension facts, which now carry the
Stone v2 provenance distinction (brief section 46):

| Provenance | Meaning |
|---|---|
| `REQUESTED_PARAMETER` | the caller asked for this size |
| `INPUT_MEASUREMENT` | the caller **measured** this size |
| `IMPORTED_GEOMETRY_MEASUREMENT` | measured from the imported asset |
| `DERIVED_FROM_OUTLINE` | computed from the supplied outline points |
| `GENERATED_REFERENCE_MEASUREMENT` | measured off generated geometry |

## `NOT_APPLICABLE` rather than omission

A fact that genuinely does not apply is emitted with
`status: NOT_APPLICABLE`, never left out.

That distinction matters: a reader can tell *"this stone has no measured
reference class"* from *"inspection forgot to look"*. It is
ATLAS-GOV-006's never-silently-discard principle applied to facts rather than
components, and it is exactly the class of gap Sprint 19's `_ALL_PAIRS` bug
created — a hardcoded list silently excluded `bezel` from all pairwise
inspection, and nothing failed because the facts were simply absent.

## The default stone was the least inspectable one

Enriching the round fast path was not cosmetic. Before Sprint 20, the **default
solitaire** — the most-generated model in the product — reported
`NOT_APPLICABLE` for its own shape family, symmetry, outline and anchors, while
every other stone reported them. The fast path exists to keep round's GEOMETRY
byte-identical, which is no reason for it to be the least described.

`_build_round_stone()` now records `sourceMode`, `profile`, `family`,
`symmetry`, `representation`, `dimensionProvenance`, provenance, its sampled
outline and its anchors — all **additive metadata**, with the geometry untouched
and all three volumes verified unchanged to the last digit.

`symmetry` in particular turned out to be load-bearing: it is what let the
Setting System stop branching on `shape == "round"` and start reading
`isRadiallySymmetric`, a geometric property.

## Verified across sources

| Stone | Source | Family | Symmetry | Anchors | Outline pts | Dimension provenance |
|---|---|---|---|---|---|---|
| round (default) | `PARAMETRIC_REFERENCE` | `RADIAL` | `RADIAL` | 5 | 48 | `REQUESTED_PARAMETER` |
| heart 8×8 | `PARAMETRIC_REFERENCE` | `SPECIAL_OUTLINE` | `BILATERAL_ONE_AXIS` | 9 | 98 | `REQUESTED_PARAMETER` |
| measured oval | `MEASURED` | `ELLIPTICAL` | `BILATERAL_BOTH_AXES` | 5 | 48 | `INPUT_MEASUREMENT` |
| custom (cm input) | `CUSTOM_OUTLINE` | `CUSTOM` | `UNKNOWN` | 5 | 5 | `DERIVED_FROM_OUTLINE` |

24 stone fact types are emitted per model, and the report status is `PASS` for
all four.

## Kernel objects never cross into a contract

No field in `geometry/inspection/models.py` holds a `cadquery.Shape`,
`Workplane` or OCP object (INSPECT-GOV-016/017). The new facts carry strings,
numbers and booleans only — `STONE_ANCHOR_COUNT` is a count, not the anchors
themselves, and the anchors that reach a consumer do so as plain `{anchor, x, y}`
records.

Inspection also remains **read-only**: nothing under `geometry/inspection/`
mutates a shape it inspects (INSPECT-GOV-013).

## Cross-references

- [`stone-v2-golden-strategy.md`](stone-v2-golden-strategy.md)
- [`../16-geometry-inspection/460-inspection-governance.md`](../16-geometry-inspection/460-inspection-governance.md)
- [`../20-stone/README.md`](../20-stone/README.md) — the Sprint 18 dimension facts.
