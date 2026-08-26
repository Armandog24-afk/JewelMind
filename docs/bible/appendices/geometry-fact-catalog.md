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

The 16 real `FactType` values (`backend/jewelmind/geometry/inspection/models.py`), a table-only re-statement of [`462-geometric-fact-model.md`](../16-geometry-inspection/462-geometric-fact-model.md), sourced from `specs/geometry-inspection/v2/fact-registry.json`. No fact type encodes a professional or manufacturing threshold — every "meaning" describes a geometric measurement or a structural presence/absence check only.

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

## Real, honest current state

Every entry above is `forgeConsumptionStatus: not_consumed` as of Sprint 14 — Forge's real rule engine (`backend/jewelmind/validation/engine.py`) does not read any `GeometricFact` yet. Of the 16 fact types, `inspector.py::inspect_model()` currently flattens 11 into the real `geometricFacts` list it produces (`COMPONENT_PRESENT`, `SOLID_COUNT`, `VOLUME`, `SHAPE_VALID`, `BOUNDING_BOX`, `COMPONENT_COUNT`, `PRONG_COUNT`, `STONE_METAL_SEPARATE`, `INTERSECTION_VOLUME`, `MIN_DISTANCE`, `CONNECTED`/`DISCONNECTED`) — `SHAPE_EXISTS`, `INTERSECTION_EXISTS`, `BOOLEAN_RESULT_VALID`, and `FALLBACK_USED` are real, defined types whose underlying data already exists on the structured `ComponentInspectionResult`/`IntersectionResult`/`BooleanOperationResult` objects but is not yet independently emitted as its own flattened fact entry — a real, minor, tracked gap, see [`494-current-runtime-inspection-gap-analysis.md`](../16-geometry-inspection/494-current-runtime-inspection-gap-analysis.md).

## Cross-references

- [`462-geometric-fact-model.md`](../16-geometry-inspection/462-geometric-fact-model.md) — full `GeometricFact` field table and narrative.
- [`487-forge-fact-contract.md`](../16-geometry-inspection/487-forge-fact-contract.md) — the kernel-neutral contract Forge would eventually consume.
- `specs/geometry-inspection/v2/fact-registry.json` — the machine-readable source this table restates.
