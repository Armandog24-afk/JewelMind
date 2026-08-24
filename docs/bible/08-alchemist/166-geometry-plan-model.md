---
id: JM-BIBLE-166
title: Geometry Plan Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-165
related_documents:
  - JM-BIBLE-A29
implementation_status: planned
professional_validation: not_required
normative: true
---

# Geometry Plan Model

**This document formally does not describe running code.** `GeometryPlan` is PLANNED — no object of this shape is materialized anywhere in `backend/jewelmind/`. The normative target shape is `specs/alchemist/v1/geometry-plan.schema.json`; a real worked example (using real derived values from the default definition) is `specs/alchemist/v1/examples/default-solitaire-geometry-plan.json`.

## What `GeometryPlan` is

- Derived from a valid (Forge-passed) JDL Canonical Document.
- Informed by Forge eligibility (it is never generated for a blocked definition).
- Consumed by Atlas (a future `execute_geometry_plan(plan)` call — see [`168-atlas-execution-contract.md`](168-atlas-execution-contract.md)).
- **Not** user-authored — no human ever writes a `GeometryPlan` by hand.
- **Not** a CAD file — it contains no B-Rep, no mesh, no kernel-native geometry.
- **Not** JDL — it is downstream of JDL, with derived values JDL itself doesn't carry.
- Versioned (`planVersion`) and deterministic (`sourceDefinitionHash` + `compilerVersion` fully determine it).

## Conceptual structure

```
GeometryPlan
├── planVersion
├── sourceDefinitionHash
├── compilerVersion
├── coordinateFrame
├── assemblyPlan
├── componentPlans        (see 167 and the geometry-plan-component schema)
├── dependencies
├── buildOrder
├── derivedParameters
├── inspectionRequests
└── artifactHints
```

## Why this is worth formalizing even though nothing implements it

Today, `build_solitaire_ring()` computes every derived value (`inner_radius`, `outer_radius`, `band_top_z`, `prong_center_radius`) and immediately consumes it inline, in the same function call that constructs the actual solids. This works correctly. A `GeometryPlan` would matter once any of the following becomes a real need: inspecting "what would be built" without building it (e.g., for a dry-run cost estimate); caching a plan independently of the final geometry; enabling component-level regeneration (rebuilding only the prong plan after a `setting.prongCount` edit, without recomputing the band); or giving a future non-Python Atlas implementation a stable, language-neutral handoff format. None of these needs exists today — this document exists so the shape is ready if one does, per [`188-open-alchemist-questions.md`](188-open-alchemist-questions.md)'s `ALCHEMIST-OQ-001`.

## Real example values

From `specs/alchemist/v1/examples/default-solitaire-geometry-plan.json`, built from real Sprint 5 data: `sourceDefinitionHash: "355ddca57e7e49ad"`, four component plans (`band`, `stone_reference`, `prongs`, `basket_support`), `buildOrder: ["band", "stone_reference", "prongs", "basket_support", "solitaire"]`, and `derivedParameters` matching `geometry/constants.py`'s real output exactly (`innerRadiusMm: 8.9`, etc.).

## Do not serialize raw CadQuery objects

Per this Sprint's explicit instruction, `geometry` is never a field of `GeometryPlan` — a plan describes *what to build and how*, never a built shape. This mirrors [`07-atlas/130-component-contract.md`](../07-atlas/130-component-contract.md)'s same discipline for `AtlasGeometryComponent`.
