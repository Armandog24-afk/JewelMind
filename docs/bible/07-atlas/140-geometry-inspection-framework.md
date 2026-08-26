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
| Fuse solid count (`FORGE-GEOM-001`) | **Yes — the only runtime check** | — | — |
| Component/shape existence | No | Yes (`test_geometry.py`) | — |
| Positive volume | No | Yes | — |
| Plausible bounding box | No | Yes | — |
| Requested-vs-generated prong count match | No | Yes | — |
| Stone-metal Z separation | No | Yes | — |
| Topology validity, self-intersection, coincident surfaces, tiny edges | No | No | Yes — see [`150-atlas-gap-analysis.md`](150-atlas-gap-analysis.md) |
| Intersection/distance between arbitrary components | No | No | Yes |
| Connectivity (disconnected metal bodies) | No | No | Yes |

**This is the single most important honest finding of Sprint 4 and Sprint 5 combined**: real-time API callers currently receive geometric assurance only from the one fuse-solid-count check. Every other geometric property this Bible documents as "current" is proven only at development/CI time against a fixed set of test definitions, not re-verified for each real user's specific input. This was first surfaced in Sprint 4's [`06-forge/106-generated-geometry-inspection-rules.md`](../06-forge/106-generated-geometry-inspection-rules.md) and is restated here at the Atlas (geometry-owning) level with the full inspection vocabulary this document defines.

## No professional meaning inside Atlas inspection

An `AtlasInspection` result's `message` field must state a fact ("1 solid detected") and never a judgment ("too thin," "not manufacturable," "acceptable"). Judgment vocabulary belongs exclusively to Forge's `ValidationResult.message` strings.

## Relationship to Sprint 13

This document's boundary — Atlas states geometric facts, never professional judgment — is exactly the boundary [`15-professional-validation/420-geometry-validation-process.md`](../15-professional-validation/420-geometry-validation-process.md) and [`15-professional-validation/436-validation-to-atlas-workflow.md`](../15-professional-validation/436-validation-to-atlas-workflow.md) build on: automated geometric inspection (this document's subject) can tell a reviewer *what* a shape is, but never *whether* it is professionally acceptable — that judgment belongs exclusively to a real, named jewelry professional, captured as a `ValidationRecord`.
