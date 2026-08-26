---
id: JM-BIBLE-461
title: Inspection Architecture Overview
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
  - JM-BIBLE-463
  - JM-BIBLE-120
  - JM-BIBLE-140
  - JM-BIBLE-106
implementation_status: current
professional_validation: not_required
normative: false
---

# Inspection Architecture Overview

## Where Inspection sits in the real pipeline

```
JDL
  ↓
FORGE (pre-generation)              backend/jewelmind/validation/engine.py
  ↓
ALCHEMIST                           backend/jewelmind/services/model_service.py
  ↓
ATLAS GENERATION                    backend/jewelmind/geometry/assemblies/solitaire.py
  ↓
ATLAS INSPECTION (this Sprint)      backend/jewelmind/geometry/inspection/
  ↓
FORGE (post-generation evaluation — not yet wired to consume facts, see 487-forge-fact-contract.md)
  ↓
VISION / FOUNDRY
```

This is the same diagram as [`README.md`](README.md); it is repeated here because this document is where the "ATLAS INSPECTION" box is actually opened up. `ModelService.generate()` (`backend/jewelmind/services/model_service.py`) calls `build_solitaire_ring()` and then, immediately after the existing preview-manifest step, calls `inspect_model(generated_model)` unconditionally — read-only, on the real `GeneratedModel` that was just produced. There is no flag, no environment variable, and no separate opt-in endpoint that skips this call for a real generation request.

## Module layout

`backend/jewelmind/geometry/inspection/` has 12 files:

| File | Responsibility |
|---|---|
| `__init__.py` | Exposes the one public entry point, `inspect_model`. |
| `models.py` | Every Pydantic result type and the 5 enums (`FactType`, `InspectionStatus`, `IntersectionStatus`, `InspectionDiagnosticCode`, plus the graph-type/operation/basis `Literal`s embedded in individual models). See [`462-geometric-fact-model.md`](462-geometric-fact-model.md). |
| `version.py` | `INSPECTION_VERSION` and `CONTACT_TOLERANCE_MM` — the two constants that give inspection its own, independent versioning and tolerance axis. |
| `diagnostics.py` | The 11 `InspectionDiagnosticCode` string constants, defined once so no call site can typo a code. |
| `shape.py` | Pure shape-level primitives: `solid_count()`, `shape_is_valid()`, `topology_counts()`, `bounding_box_fact()`/`bounding_box_fact_from_box()`. |
| `distance.py` | `inspect_distance()` — one pairwise `Shape.distance()` measurement. |
| `intersection.py` | `inspect_intersection()` and `should_skip_intersection()` — one pairwise `Shape.intersect()` measurement, with broad-phase elimination. |
| `topology.py` | `inspect_topology()` — solid/shell/face/edge/vertex counts plus `Shape.isValid()`, wrapped so a kernel exception never propagates. |
| `components.py` | `inspect_component()` — orchestrates `shape.py`/`topology.py` for one named `GeneratedComponent`. |
| `connectivity.py` | `pairwise_distances()` and `build_connectivity_graph()` — turns a set of real distance measurements into a graph and its connected components. |
| `assembly.py` | `inspect_assembly()` — orchestrates every assembly-level check (required components, distances, intersections, both connectivity graphs, stone-metal separation, prong count, boolean-operation facts) for one `GeneratedModel`. |
| `inspector.py` | `inspect_model()` — the top-level entry point; builds the flattened `geometricFacts` list and assembles the final `GeometryInspectionReport`. |

## Read-only, always

Every function in `shape.py`, `distance.py`, `intersection.py`, `topology.py`, `components.py`, and `assembly.py` takes a shape (or a `GeneratedComponent`/`GeneratedModel` wrapping one) and returns a new structured result. None calls `.fuse()`, `.cut()`, `.fillet()`, or any other geometry-mutating CadQuery method on its input — this restates INSPECT-GOV-013 at the module level. Inspection cannot make the geometry it inspects better or worse; it can only describe what is already there.

## Why this is the single most important architectural fact of this Sprint

Sprint 5's [`07-atlas/140-geometry-inspection-framework.md`](../07-atlas/140-geometry-inspection-framework.md) and Sprint 4's [`06-forge/106-generated-geometry-inspection-rules.md`](../06-forge/106-generated-geometry-inspection-rules.md) both recorded, as the single most important honest finding of their respective Sprints, that only one geometry-inspection check (`FORGE-GEOM-001`, the fuse-solid-count check inside `_fuse_metal()`) actually ran at request time — every other geometric property (component existence, positive volume, plausible bounding box, prong-count match, stone-metal separation) was verified only by `backend/tests/test_geometry.py` against a fixed set of test definitions, never re-checked for a real caller's specific input. This Sprint's `inspect_model()` call inside `ModelService.generate()` is what actually closes that gap for the properties inspection now covers: component existence, shape validity, solid count, volume, bounding box, pairwise distance, pairwise intersection, two connectivity graphs, stone-metal separation, prong count, and boolean-operation outcome are now computed for every real generation, not just exercised by tests. `_fuse_metal()`'s own runtime check is untouched and still the mechanism that decides fuse-vs-fallback; inspection observes its outcome afterward rather than replacing it.

What this Sprint does **not** close: Forge's rule engine (`backend/jewelmind/validation/engine.py`) does not yet read any `GeometricFact` — see [`487-forge-fact-contract.md`](487-forge-fact-contract.md) for the current, honest state of that non-integration, and [`494-current-runtime-inspection-gap-analysis.md`](494-current-runtime-inspection-gap-analysis.md) for why wiring it up was deliberately out of scope this Sprint.

## Related documents

[`462-geometric-fact-model.md`](462-geometric-fact-model.md) for the `GeometricFact` shape and the 16 `FactType` values; [`463-inspection-subsystem-model.md`](463-inspection-subsystem-model.md) for a deeper, function-by-function breakdown of the same modules listed above; [`491-runtime-inspection-policy.md`](491-runtime-inspection-policy.md) for which checks run unconditionally versus are cost-gated.
