---
id: JM-BIBLE-ATLAS-README
title: Atlas Geometry Core v1 — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-JDL-README
  - JM-BIBLE-FORGE-README
related_documents:
  - JM-BIBLE-README
implementation_status: partial
professional_validation: not_required
normative: false
---

# Atlas Geometry Core v1 — Index

This is **Sprint 5** of the Technical Bible: **Atlas Geometry Core v1**. Atlas is the deterministic geometry layer of JewelMind — the formal model of the geometric primitives, coordinate conventions, component/assembly contracts, construction pipeline, and inspection framework already implemented in `backend/jewelmind/geometry/`. **Atlas v1 is a specification and classification layer over CadQuery/OpenCascade code that already exists — it replaces no kernel, changes no generated geometry, and adds no new ring style.**

**Read this README, then [`120-atlas-governance.md`](120-atlas-governance.md), before changing anything in `backend/jewelmind/geometry/`, `backend/jewelmind/preview/`, or `backend/jewelmind/exporters/`.**

## The fundamental architectural boundary

**Atlas knows geometry. Atlas must never become the hidden source of jewelry-domain knowledge.**

| Layer | Owns |
|---|---|
| JDL (Sprint 3) | Declarative design input — the canonical document |
| Atlas (this Sprint) | Geometric primitives, transformations, coordinate systems, topology, construction operations, component geometry, geometric metadata, geometric inspection, deterministic construction behavior |
| Forge (Sprint 4) | Jewelry-domain constraints, applicability rules, warnings, domain thresholds, manufacturing-context rules, rule provenance, professional-validation status |

Atlas may report a geometric **fact**: *"minimum detected local dimension = X."* Only Forge may turn that fact into a rule verdict: *"X violates rule Y for context Z."* Atlas must never decide how many prongs are professionally appropriate, what thickness is acceptable for a manufacturing process, whether a setting is professionally manufacturable, or what alloy-specific tolerances are safe — see [`140-geometry-inspection-framework.md`](140-geometry-inspection-framework.md) for how this separation is enforced in the inspection model specifically.

## Reading order

1. [`120-atlas-governance.md`](120-atlas-governance.md) — 15 non-negotiable rules (ATLAS-GOV-001..015).
2. [`121-atlas-architecture-overview.md`](121-atlas-architecture-overview.md) — the conceptual pipeline with a Mermaid diagram.
3. Representation model: [`122-geometric-representation-model.md`](122-geometric-representation-model.md), [`123-coordinate-system-and-orientation.md`](123-coordinate-system-and-orientation.md), [`124-geometric-primitives.md`](124-geometric-primitives.md), [`125-transformations.md`](125-transformations.md).
4. Shapes: [`126-curve-and-profile-model.md`](126-curve-and-profile-model.md), [`127-surface-and-solid-model.md`](127-surface-and-solid-model.md), [`128-brep-and-topology-model.md`](128-brep-and-topology-model.md), [`129-mesh-model.md`](129-mesh-model.md).
5. Contracts: [`130-component-contract.md`](130-component-contract.md), [`131-assembly-contract.md`](131-assembly-contract.md).
6. Pipeline and operations: [`132-construction-pipeline.md`](132-construction-pipeline.md), [`133-operation-contracts.md`](133-operation-contracts.md), [`134-boolean-operation-strategy.md`](134-boolean-operation-strategy.md), [`135-fillets-rounding-and-fallbacks.md`](135-fillets-rounding-and-fallbacks.md).
7. Rigor: [`136-tolerance-model.md`](136-tolerance-model.md), [`137-determinism-and-reproducibility.md`](137-determinism-and-reproducibility.md), [`138-component-naming-and-identity.md`](138-component-naming-and-identity.md), [`139-geometry-metadata-model.md`](139-geometry-metadata-model.md).
8. Inspection: [`140-geometry-inspection-framework.md`](140-geometry-inspection-framework.md), [`141-connectivity-and-component-integrity.md`](141-connectivity-and-component-integrity.md), [`142-volume-and-bounding-box-inspection.md`](142-volume-and-bounding-box-inspection.md), [`143-stone-metal-separation-contract.md`](143-stone-metal-separation-contract.md).
9. Artifacts: [`144-preview-mesh-contract.md`](144-preview-mesh-contract.md), [`145-step-export-geometry-contract.md`](145-step-export-geometry-contract.md), [`146-stl-export-geometry-contract.md`](146-stl-export-geometry-contract.md).
10. [`147-geometry-error-model.md`](147-geometry-error-model.md), [`148-performance-and-resource-model.md`](148-performance-and-resource-model.md).
11. [`149-current-solitaire-geometry-mapping.md`](149-current-solitaire-geometry-mapping.md), [`150-atlas-gap-analysis.md`](150-atlas-gap-analysis.md), [`151-open-atlas-questions.md`](151-open-atlas-questions.md).

## Appendices

[`atlas-component-catalog.md`](../appendices/atlas-component-catalog.md), [`atlas-operation-catalog.md`](../appendices/atlas-operation-catalog.md), [`atlas-coordinate-reference.md`](../appendices/atlas-coordinate-reference.md), [`atlas-geometry-invariant-catalog.md`](../appendices/atlas-geometry-invariant-catalog.md), [`atlas-inspection-catalog.md`](../appendices/atlas-inspection-catalog.md), [`atlas-fallback-register.md`](../appendices/atlas-fallback-register.md), [`atlas-code-mapping.md`](../appendices/atlas-code-mapping.md).

## Machine-readable specification

[`specs/atlas/v1/`](../../../specs/atlas/v1/README.md) holds 6 JSON Schemas, 5 real example records (generated by running `build_solitaire_ring(default_definition())` directly), and 5 test-vector files. `backend/tests/test_atlas_registry.py` re-checks all of it on every test run.

## Relationship to prior Sprints

Sprint 2 ([`04-jewelry-domain/`](../04-jewelry-domain/README.md)) established what a solitaire ring *means*. Sprint 3 ([`05-jdl/`](../05-jdl/README.md)) established how that meaning is *expressed as data*. Sprint 4 ([`06-forge/`](../06-forge/README.md)) established the *rule system* that judges that data. **Sprint 5 establishes how that data becomes real geometry** — [`05-jdl/077-compiler-contract.md`](../05-jdl/077-compiler-contract.md) and [`05-jdl/078-geometry-generation-contract.md`](../05-jdl/078-geometry-generation-contract.md) were both updated this Sprint to cross-reference Atlas rather than duplicate it, and [`06-forge/105-geometry-precondition-rules.md`](../06-forge/105-geometry-precondition-rules.md) / [`106-generated-geometry-inspection-rules.md`](../06-forge/106-generated-geometry-inspection-rules.md) were updated to reference Atlas's inspection framework.

## Validation of this sprint

See [`SPRINT-5-VALIDATION-REPORT.md`](SPRINT-5-VALIDATION-REPORT.md) for the checks run against this section and the findings from that pass.
