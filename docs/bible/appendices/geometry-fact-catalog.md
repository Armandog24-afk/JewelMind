---
id: JM-BIBLE-A92
title: "Appendix: Geometry Fact Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-462
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Geometry Fact Catalog

The 22 real `FactType` values (`backend/jewelmind/geometry/inspection/models.py`) — 16 from Sprint 14 plus the 6 `STONE_*` dimension facts added in Sprint 18 — a table-only re-statement of [`462-geometric-fact-model.md`](../16-geometry-inspection/462-geometric-fact-model.md), sourced from `specs/geometry-inspection/v2/fact-registry.json`. No fact type encodes a professional or manufacturing threshold — every "meaning" describes a geometric measurement or a structural presence/absence check only.

| Fact type | Meaning | Value type | Unit | Scope | Forge consumption |
|---|---|---|---|---|---|
| `SHAPE_EXISTS` | A component produced at least one solid. | boolean | — | COMPONENT | not_consumed |
| `SHAPE_VALID` | `Shape.isValid()` (OpenCascade `BRepCheck_Analyzer`) reports no defects. | boolean | — | COMPONENT | not_consumed |
| `SOLID_COUNT` | Number of top-level solids in a shape. | integer | — | COMPONENT | not_consumed |
| `VOLUME` | Solid volume. | number | mm3 | COMPONENT | not_consumed |
| `BOUNDING_BOX` | Axis-aligned bounding box (min/max/size/center per axis). | object | mm | COMPONENT | not_consumed |
| `COMPONENT_COUNT` | Number of named components in the assembly. | integer | — | ASSEMBLY | not_consumed |
| `INTERSECTION_EXISTS` | Real pairwise geometric-intersection classification. | string | — | PAIR | not_consumed |
| `INTERSECTION_VOLUME` | Boolean-common solid volume between two components. | number | mm3 | PAIR | not_consumed |
| `MIN_DISTANCE` | Minimum distance between two components. | number | mm | PAIR | not_consumed |
| `CONNECTED` | A production connectivity group is connected. | boolean | — | ASSEMBLY | not_consumed |
| `DISCONNECTED` | A production connectivity group is NOT connected to the rest of production metal. | boolean | — | ASSEMBLY | not_consumed |
| `COMPONENT_PRESENT` | A specific required component exists. | boolean | — | COMPONENT | not_consumed |
| `PRONG_COUNT` | Requested vs. actually generated prong count. | integer | — | ASSEMBLY | not_consumed |
| `STONE_METAL_SEPARATE` | StoneReference remains distinct from (never fused into) production metal. | boolean | — | ASSEMBLY | not_consumed |
| `BOOLEAN_RESULT_VALID` | A fuse/cut/common operation produced a real, non-empty result. | boolean | — | COMPONENT | not_consumed |
| `FALLBACK_USED` | A geometry builder fell back from its primary operation to a simpler alternative. | boolean | — | COMPONENT | not_consumed |
| `STONE_REQUESTED_LENGTH` | Stone reference's requested major horizontal dimension, from build-time metadata (CONSTRUCTION_PARAMETER). | number | mm | COMPONENT | not_consumed |
| `STONE_MEASURED_LENGTH` | Stone reference's measured major horizontal extent, from the independently computed bounding box (`sizeY`). | number | mm | COMPONENT | not_consumed |
| `STONE_REQUESTED_WIDTH` | Stone reference's requested minor horizontal dimension, from build-time metadata (CONSTRUCTION_PARAMETER). | number | mm | COMPONENT | not_consumed |
| `STONE_MEASURED_WIDTH` | Stone reference's measured minor horizontal extent, from the bounding box (`sizeX`). | number | mm | COMPONENT | not_consumed |
| `STONE_REQUESTED_DEPTH` | Stone reference's requested vertical dimension, from build-time metadata (CONSTRUCTION_PARAMETER). | number | mm | COMPONENT | not_consumed |
| `STONE_MEASURED_DEPTH` | Stone reference's measured vertical extent, from the bounding box (`sizeZ`). | number | mm | COMPONENT | not_consumed |

## Real, honest current state

Every entry above is `forgeConsumptionStatus: not_consumed` — Forge's real rule engine (`backend/jewelmind/validation/engine.py`) does not read any `GeometricFact` yet.

Of the original 16 Sprint-14 fact types, `inspector.py::inspect_model()` flattens 11 into the real `geometricFacts` list it produces (`COMPONENT_PRESENT`, `SOLID_COUNT`, `VOLUME`, `SHAPE_VALID`, `BOUNDING_BOX`, `COMPONENT_COUNT`, `PRONG_COUNT`, `STONE_METAL_SEPARATE`, `INTERSECTION_VOLUME`, `MIN_DISTANCE`, `CONNECTED`/`DISCONNECTED`) — `SHAPE_EXISTS`, `INTERSECTION_EXISTS`, `BOOLEAN_RESULT_VALID`, and `FALLBACK_USED` are real, defined types whose underlying data already exists on the structured `ComponentInspectionResult`/`IntersectionResult`/`BooleanOperationResult` objects but is not yet independently emitted as its own flattened fact entry — a real, minor, tracked gap, see [`494-current-runtime-inspection-gap-analysis.md`](../16-geometry-inspection/494-current-runtime-inspection-gap-analysis.md).

The 6 `STONE_*` dimension facts (Sprint 18, `inspector.py::_stone_dimension_facts()`) are all genuinely emitted, for the `stone_reference` component only. They deliberately pair a CONSTRUCTION_PARAMETER with an independently MEASURED_GEOMETRY counterpart so an accidental scaling or shape regression shows up as a divergence between the two, compared with a software geometry tolerance — never a professional or manufacturing tolerance. `STONE_MEASURED_LENGTH`/`STONE_MEASURED_WIDTH` derive from an axis-aligned bounding box, so they isolate length from width exactly only at `stone.orientation == 0`; see [`docs/bible/20-stone/574-stone-inspection-contract.md`](../20-stone/574-stone-inspection-contract.md).

## Cross-references

- [`462-geometric-fact-model.md`](../16-geometry-inspection/462-geometric-fact-model.md) — full `GeometricFact` field table and narrative.
- [`487-forge-fact-contract.md`](../16-geometry-inspection/487-forge-fact-contract.md) — the kernel-neutral contract Forge would eventually consume.
- `specs/geometry-inspection/v2/fact-registry.json` — the machine-readable source this table restates.
