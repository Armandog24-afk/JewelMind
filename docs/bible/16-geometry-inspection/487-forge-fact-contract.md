---
id: JM-BIBLE-487
title: Forge Fact Contract
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
  - JM-BIBLE-462
  - JM-BIBLE-090
  - JM-BIBLE-106
  - JM-BIBLE-111
normative: true
implementation_status: partial
professional_validation: not_required
---

# Forge Fact Contract

## The honest headline

**Forge's real rule engine does not currently read any `GeometricFact`.** `backend/jewelmind/validation/engine.py` and `backend/jewelmind/validation/rules.py` contain zero references to `GeometricFact`, `inspection_report`, or `geometry.inspection` — confirmed by grep against both files during this Sprint. `specs/geometry-inspection/v2/fact-registry.json` states this explicitly for every one of its 16 fact types:

```
"forgeConsumptionStatus": "not_consumed"
```

This is true for `SHAPE_EXISTS`, `SHAPE_VALID`, `SOLID_COUNT`, `VOLUME`, `BOUNDING_BOX`, `COMPONENT_COUNT`, `INTERSECTION_EXISTS`, `INTERSECTION_VOLUME`, `MIN_DISTANCE`, `CONNECTED`, `DISCONNECTED`, `COMPONENT_PRESENT`, `PRONG_COUNT`, `STONE_METAL_SEPARATE`, `BOOLEAN_RESULT_VALID`, and `FALLBACK_USED` — every fact type this Sprint's `FactType` literal in `backend/jewelmind/geometry/inspection/models.py` defines. This document exists to establish the CONTRACT a future Forge rule would consume, not to claim that contract is exercised yet.

## The conceptual kernel-neutral fact-provider shape

The brief for this Sprint proposed a flattened, kernel-neutral fact record. That shape is real today — it is exactly what `GeometricFact.model_dump()` produces from `backend/jewelmind/geometry/inspection/models.py`:

```json
{
  "factId": "component.band.volume",
  "factType": "VOLUME",
  "inspectionVersion": "1.0.0",
  "scope": "COMPONENT",
  "componentIds": ["band"],
  "value": 250.99168317654699,
  "unit": "mm3",
  "status": "PASS",
  "tolerance": null,
  "sourceOperation": "Shape.Volume",
  "generatedAt": "<ISO-8601 timestamp>",
  "diagnostic": null,
  "metadata": {}
}
```

Every field is populated by `inspector.py::_component_facts()` and the analogous assembly-level fact construction in `inspector.py::inspect_model()` (pairwise intersection/distance facts, `assembly.componentCount`, `assembly.prongCount`, `assembly.stoneMetalSeparate`, `production.connectivity.group.<names>`) — this is not a hypothetical shape drawn up for this document, it is what a real generation actually produces and what `GET /api/models/{model_id}/inspection` actually returns embedded inside `GeometryInspectionReport.geometricFacts`.

## The hard rule: no raw kernel objects

Per INSPECT-GOV-016/017, no field in `models.py` ever holds a `cadquery.Shape`, `cadquery.Workplane`, or `OCP` object. `GeometricFact.value` is typed `float | int | bool | str | None` — plain Python/Pydantic types only. This was verified structurally by reading every field declaration in `models.py`: `ComponentInspectionResult`, `DistanceResult`, `IntersectionResult`, `ConnectivityGraph`, `AssemblyInspectionResult`, and `GeometryInspectionReport` all compose only nested `InspectionModel` subclasses, primitives, and `list`/`dict` of those. A future Forge rule could therefore depend on `GeometricFact`/`GeometryInspectionReport` without ever importing `cadquery` — the same discipline `docs/bible/16-geometry-inspection/462-geometric-fact-model.md` documents at the model level, restated here at the consumption boundary.

## Why an unconsumed contract still matters

An unconsumed contract is not a wasted one. Before this Sprint, there was no structured way for a Forge rule to reference "the intersection volume between `stone_reference` and `prongs`," or "whether the production connectivity graph is fully connected," without either (a) writing new CadQuery calls directly inside `validation/engine.py` — which would violate FORGE-GOV-005 (jewelry rules must not hide inside geometry code) by inverting it into geometry code hiding inside jewelry rules — or (b) duplicating the inspection logic a second time. `GeometricFact`'s stable `factId` scheme (`component.<name>.<property>`, `pair.<a>.<b>.<property>`, `assembly.<property>`, `production.connectivity.group.<names>` — INSPECT-GOV-010) and kernel-neutral typing (INSPECT-GOV-016/017) are the necessary prerequisite: they are what makes it *possible* for a future Forge rule to consume a geometric fact by reference (a `factId` string and a comparison) instead of by re-deriving it from a `Workplane`. This Sprint builds that prerequisite and stops there — it does not invent the first fact-consuming rule, because doing so would require a real jewelry-domain judgment (e.g. "is 2.10 mm³ of prong/stone overlap an acceptable grip depth?") this Sprint has no professional-validation basis to make (PROVAL-GOV-006/007 apply to any such threshold exactly as they would to any other Forge rule).

## What a first real consumer would need

Per `docs/bible/06-forge/090-forge-governance.md`'s RFC/ADR triggers, a Forge rule that reads a `GeometricFact` for the first time is not itself an architecture change (Forge already reads `JewelryDefinition` and produces `ValidationResult`s; reading a second input type is additive), but the specific fact and threshold chosen would still need:

1. A provenance declaration (`docs/bible/06-forge/094-rule-provenance-model.md`) — most likely `prototype_heuristic` unless a named professional supplies the threshold.
2. An entry in `specs/forge/v1/current-rule-registry.json` and `docs/bible/appendices/forge-rule-catalog.md`.
3. A corresponding update to `specs/geometry-inspection/v2/fact-registry.json`, changing that fact's `forgeConsumptionStatus` from `not_consumed` to `consumed` — the registry is the authoritative record of which facts are actually read, and it must never silently drift from the real rule engine.

None of this happened this Sprint. See [`494-current-runtime-inspection-gap-analysis.md`](494-current-runtime-inspection-gap-analysis.md) for this gap listed alongside the others this Sprint left open.

## Relationship to prior findings

This document is the direct answer to the question [`06-forge/106-generated-geometry-inspection-rules.md`](../06-forge/106-generated-geometry-inspection-rules.md) leaves open after its own Sprint 14 update: "a caller still cannot get 'your specific definition produced a component with implausible proportions' as a diagnosed rule violation — only the raw fact itself." That sentence is the accurate, current state of the Forge/Inspection boundary, and this document does not attempt to close it.
