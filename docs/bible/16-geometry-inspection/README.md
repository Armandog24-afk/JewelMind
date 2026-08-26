---
id: JM-BIBLE-INSPECTION-README
title: Geometry Inspection v2 — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-120
  - JM-BIBLE-090
related_documents:
  - JM-BIBLE-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Geometry Inspection v2 — Index

This is **Sprint 14** of the Technical Bible: **Geometry Inspection v2**. Sprint 5 (Atlas) established the conceptual boundary — Atlas reports geometric facts, Forge interprets them — but found that only one geometry-inspection property (a fuse-solid-count check, `FORGE-GEOM-001`) actually ran at runtime; everything else was enforced only by tests against a fixed set of definitions. This Sprint closes most of that gap with real, real, runtime code: `backend/jewelmind/geometry/inspection/`, called on every single `ModelService.generate()` call, producing a structured `GeometryInspectionReport` for the model that was actually generated.

**Read this README, then [`460-inspection-governance.md`](460-inspection-governance.md), before changing anything in `backend/jewelmind/geometry/inspection/`.**

## Where Inspection sits

```
JDL
  ↓
FORGE (pre-generation)
  ↓
ALCHEMIST
  ↓
ATLAS GENERATION
  ↓
ATLAS INSPECTION        (this Sprint — real runtime geometric facts)
  ↓
FORGE (post-generation evaluation — not yet wired to consume facts, see 487)
  ↓
VISION / FOUNDRY
```

Inspection reports facts. It never decides whether a fact violates a jewelry or manufacturing rule — that remains exclusively Forge's job, restated in [`460-inspection-governance.md`](460-inspection-governance.md)'s 20 INSPECT-GOV rules.

## The core principle

> Atlas reports geometric facts. Forge decides whether those facts violate jewelry or manufacturing rules.

"The band and basket intersect by 0.12 mm³" is an Atlas fact. "Given lost-wax casting, that relationship is acceptable" would be a Forge rule — none currently exists that consumes this specific fact, and this Sprint does not invent one (see [`487-forge-fact-contract.md`](487-forge-fact-contract.md) for the honest current state of that integration).

## Reading order

1. [`460-inspection-governance.md`](460-inspection-governance.md) — 20 non-negotiable rules (INSPECT-GOV-001 through 020).
2. [`461-inspection-architecture-overview.md`](461-inspection-architecture-overview.md), [`462-geometric-fact-model.md`](462-geometric-fact-model.md), [`463-inspection-subsystem-model.md`](463-inspection-subsystem-model.md).
3. Component-level: [`464-component-inspection-contract.md`](464-component-inspection-contract.md), [`466-shape-validity-inspection.md`](466-shape-validity-inspection.md), [`467-solid-count-inspection.md`](467-solid-count-inspection.md), [`468-volume-inspection.md`](468-volume-inspection.md), [`469-bounding-box-inspection.md`](469-bounding-box-inspection.md), [`477-topology-inspection-model.md`](477-topology-inspection-model.md).
4. Assembly-level: [`465-assembly-inspection-contract.md`](465-assembly-inspection-contract.md), [`470-component-connectivity-model.md`](470-component-connectivity-model.md), [`471-component-intersection-model.md`](471-component-intersection-model.md), [`472-component-distance-model.md`](472-component-distance-model.md), [`473-production-metal-integrity.md`](473-production-metal-integrity.md), [`474-stone-metal-separation-inspection.md`](474-stone-metal-separation-inspection.md), [`475-prong-count-and-identity-inspection.md`](475-prong-count-and-identity-inspection.md), [`476-component-presence-inspection.md`](476-component-presence-inspection.md), [`480-assembly-graph-model.md`](480-assembly-graph-model.md).
5. Operations: [`478-boolean-result-inspection.md`](478-boolean-result-inspection.md), [`479-fallback-result-inspection.md`](479-fallback-result-inspection.md).
6. Results: [`481-inspection-result-model.md`](481-inspection-result-model.md), [`482-inspection-status-and-confidence.md`](482-inspection-status-and-confidence.md), [`483-inspection-error-model.md`](483-inspection-error-model.md), [`484-inspection-performance-model.md`](484-inspection-performance-model.md).
7. Change management: [`485-inspection-versioning.md`](485-inspection-versioning.md), [`486-inspection-determinism.md`](486-inspection-determinism.md), [`492-inspection-regression-model.md`](492-inspection-regression-model.md).
8. Integration: [`487-forge-fact-contract.md`](487-forge-fact-contract.md), [`488-alchemist-inspection-integration.md`](488-alchemist-inspection-integration.md), [`489-foundry-inspection-integration.md`](489-foundry-inspection-integration.md), [`490-vision-inspection-integration.md`](490-vision-inspection-integration.md), [`491-runtime-inspection-policy.md`](491-runtime-inspection-policy.md).
9. [`493-current-solitaire-inspection-map.md`](493-current-solitaire-inspection-map.md), [`494-current-runtime-inspection-gap-analysis.md`](494-current-runtime-inspection-gap-analysis.md), [`495-open-inspection-questions.md`](495-open-inspection-questions.md).

## Appendices

[`geometry-fact-catalog.md`](../appendices/geometry-fact-catalog.md), [`inspection-type-catalog.md`](../appendices/inspection-type-catalog.md), [`component-connectivity-catalog.md`](../appendices/component-connectivity-catalog.md), [`intersection-fact-catalog.md`](../appendices/intersection-fact-catalog.md), [`inspection-diagnostic-catalog.md`](../appendices/inspection-diagnostic-catalog.md), [`inspection-code-mapping.md`](../appendices/inspection-code-mapping.md), [`inspection-test-matrix.md`](../appendices/inspection-test-matrix.md), [`solitaire-inspection-baseline.md`](../appendices/solitaire-inspection-baseline.md) (`JM-BIBLE-A92` through `A99`, continuing from Sprint 13's last appendix, `A91`).

## Machine-readable specification

[`specs/geometry-inspection/v2/`](../../../specs/geometry-inspection/v2/README.md) holds 9 JSON Schemas, a hand-authored `fact-registry.json` (16 fact types, zero professional thresholds), 5 examples, and 8 test-vector files, all generated by actually running the real `inspect_model()` pipeline against real generated solitaire geometry.

## The single most important finding of this Sprint

**Real runtime inspection now exists and runs on every generation, not just in tests.** `ModelService.generate()` calls `inspect_model()` unconditionally; the result is stored on `ModelRecord.inspection_report`, summarized into `/api/models/generate` and `/api/models/{id}/metadata` responses, available in full via `GET /api/models/{id}/inspection`, embedded in the technical specification, and included as `geometry-inspection.json` in every Professional Review Package. This was verified against the real default solitaire and a real 4-prong variant — both fully connected, both with the stone reference correctly identified as separate from production metal (see [`493-current-solitaire-inspection-map.md`](493-current-solitaire-inspection-map.md)).

## What was investigated, not invented

Every kernel operation this Sprint relies on (`cadquery.Shape.distance()`, `.intersect()`, `.isValid()`, `.Solids()`/`.Shells()`/`.Faces()`/`.Edges()`/`.Vertices()`) was verified to actually exist and work against the installed `cadquery==2.8.0` build by running it against real generated geometry before being wired into production code — never assumed from documentation or guessed OCP method names. See [`466-shape-validity-inspection.md`](466-shape-validity-inspection.md) and [`472-component-distance-model.md`](472-component-distance-model.md) for what was tested and measured.

## Validation of this sprint

See [`SPRINT-14-VALIDATION-REPORT.md`](SPRINT-14-VALIDATION-REPORT.md) for the checks run against this section and the findings from that pass.
