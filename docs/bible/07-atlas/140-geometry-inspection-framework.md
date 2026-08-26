---
id: JM-BIBLE-140
title: Geometry Inspection Framework
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-132
related_documents:
  - JM-BIBLE-106
  - JM-BIBLE-A24
implementation_status: partial
professional_validation: not_required
normative: true
---

# Geometry Inspection Framework

**This is the document that enforces the Atlas/Forge boundary at the inspection layer.** The normative shape is `specs/atlas/v1/geometry-inspection-result.schema.json`; real facts for the default definition are in `specs/atlas/v1/test-vectors/inspection-vectors.json`.

## GEOMETRIC FACT vs. FORGE INTERPRETATION

An `AtlasInspection` result states a **fact**: a number, a boolean, a count — never a verdict. Forge is the only layer permitted to say a fact violates a rule.

| Atlas may detect (a fact) | Forge decides (an interpretation) |
|---|---|
| "1 solid detected after fuse" | Whether 1-vs-3 solids matters for this manufacturing context |
| "combined_metal volume = 341.44 mm³" | Whether that volume is a reasonable/expected mass for this metal |
| "bounding box spans x:[-10.7,10.7]" | Whether that size is appropriate for the requested ring size |
| "component count = 4" | Whether 4 components correctly represent "a complete solitaire" |
| "stone_reference.bbox.zmin >= band.bbox.zmax" | Whether that gap represents correct clearance |
| (not currently detectable) topology validity | Whether an invalid solid should block export |

## `checkType` vocabulary

`SHAPE_EXISTS`, `SOLID_COUNT`, `VOLUME`, `BOUNDING_BOX`, `COMPONENT_COUNT`, `CONNECTIVITY`, `TOPOLOGY_VALIDITY`, `INTERSECTION`, `DISTANCE`, `MESH_GENERATION`.

## Status vocabulary

`PASS`, `FAIL`, `UNKNOWN`, `NOT_APPLICABLE`. **`UNKNOWN` and `NOT_APPLICABLE` are used deliberately** in `inspection-vectors.json` for checks that genuinely do not exist yet (e.g. `TOPOLOGY_VALIDITY` is `UNKNOWN`, not assumed `PASS`) — see [`128-brep-and-topology-model.md`](128-brep-and-topology-model.md).

## What is CURRENT vs. what is TEST_ONLY vs. what is PLANNED

| Fact | Runtime (affects a real API response)? | Test-only? | Planned? |
|---|---|---|---|
| Fuse solid count (`FORGE-GEOM-001`) | Yes | — | — |
| Component/shape existence | **Yes (Sprint 14)** | Yes (`test_geometry.py`, dev-time) | — |
| Positive volume | **Yes (Sprint 14)** | Yes | — |
| Plausible bounding box (extent computed; plausibility itself still uninterpreted) | **Yes (Sprint 14)** | Yes | — |
| Requested-vs-generated prong count match | **Yes (Sprint 14)** | Yes | — |
| Stone-metal separation (structural, not Z-comparison) | **Yes (Sprint 14)** | Yes | — |
| Intersection/distance between named components | **Yes (Sprint 14)** | — | — |
| Connectivity (disconnected production bodies) | **Yes (Sprint 14)** | — | — |
| Topology validity (binary valid/invalid) | **Yes (Sprint 14)** | — | — |
| Detailed topology defect classification, self-intersection beyond named-pair intersection, coincident surfaces, tiny edges | No | No | Yes — see [`150-atlas-gap-analysis.md`](150-atlas-gap-analysis.md) and [`16-geometry-inspection/494-current-runtime-inspection-gap-analysis.md`](../16-geometry-inspection/494-current-runtime-inspection-gap-analysis.md) |

**This was the single most important honest finding of Sprint 4 and Sprint 5 combined, and Sprint 14 (Geometry Inspection v2) materially closes it**: before Sprint 14, real-time API callers received geometric assurance only from the one fuse-solid-count check; every other geometric property this Bible documented as "current" was proven only at development/CI time against a fixed set of test definitions. As of Sprint 14, `jewelmind.geometry.inspection.inspect_model()` runs unconditionally inside `ModelService.generate()` and produces most of the facts above as real, structured, runtime output — available via `GET /api/models/{id}/inspection`, a concise summary in `/generate`/`/metadata`, the technical specification, and the Professional Review Package. What remains genuinely unrealized is Forge *consuming* any of these facts to produce a rule violation — see [`16-geometry-inspection/487-forge-fact-contract.md`](../16-geometry-inspection/487-forge-fact-contract.md) — and the detailed-defect-classification row above. This was first surfaced in Sprint 4's [`06-forge/106-generated-geometry-inspection-rules.md`](../06-forge/106-generated-geometry-inspection-rules.md) and is restated here at the Atlas (geometry-owning) level with the full inspection vocabulary this document defines.

## No professional meaning inside Atlas inspection

An `AtlasInspection` result's `message` field must state a fact ("1 solid detected") and never a judgment ("too thin," "not manufacturable," "acceptable"). Judgment vocabulary belongs exclusively to Forge's `ValidationResult.message` strings.

## Relationship to Sprint 13

This document's boundary — Atlas states geometric facts, never professional judgment — is exactly the boundary [`15-professional-validation/420-geometry-validation-process.md`](../15-professional-validation/420-geometry-validation-process.md) and [`15-professional-validation/436-validation-to-atlas-workflow.md`](../15-professional-validation/436-validation-to-atlas-workflow.md) build on: automated geometric inspection (this document's subject) can tell a reviewer *what* a shape is, but never *whether* it is professionally acceptable — that judgment belongs exclusively to a real, named jewelry professional, captured as a `ValidationRecord`.

## Relationship to Sprint 14

[`16-geometry-inspection/`](../16-geometry-inspection/README.md) (Sprint 14) is the real, runtime implementation of the inspection vocabulary this document conceptually defines — `backend/jewelmind/geometry/inspection/`, called unconditionally on every generation. The `AtlasInspection`-shaped facts this document describes (a fact, never a judgment) are exactly what `GeometricFact`/`ComponentInspectionResult`/`AssemblyInspectionResult` now are in real code. This document remains the conceptual/historical record of the gap; [`16-geometry-inspection/493-current-solitaire-inspection-map.md`](../16-geometry-inspection/493-current-solitaire-inspection-map.md) is the current, authoritative coverage map.
