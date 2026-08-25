---
id: JM-BIBLE-ALCHEMIST-README
title: Alchemist Compiler v1 — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-JDL-README
  - JM-BIBLE-FORGE-README
  - JM-BIBLE-ATLAS-README
related_documents:
  - JM-BIBLE-README
implementation_status: partial
professional_validation: not_required
normative: false
---

# Alchemist Compiler v1 — Index

This is **Sprint 6** of the Technical Bible: **Alchemist Compiler v1**. Alchemist is the compilation orchestration layer — the formal translation from validated JDL and Forge evaluation into a deterministic `GeometryPlan`, Atlas execution, and a final artifact manifest. **This Sprint is almost entirely architecture-before-implementation**: the current backend already performs every step Alchemist describes, correctly and deterministically, but does so inline — with no explicit `GeometryPlan` object, no `CompilationResult` object, and no `compilationHash`. This Sprint names, formalizes, and honestly gap-analyzes that reality; it does not build a new runtime.

**Read this README, then [`160-alchemist-governance.md`](160-alchemist-governance.md), before changing anything in `backend/jewelmind/services/model_service.py`, `api/routes.py`, or how generation/export orchestration works.**

## The five-layer architecture Alchemist sits inside

| Layer | Owns |
|---|---|
| **JDL** (Sprint 3) | Declarative design definition |
| **Forge** (Sprint 4) | Rule evaluation and eligibility |
| **Alchemist** (this Sprint) | Orchestration and deterministic compilation planning |
| **Atlas** (Sprint 5) | Geometry construction and geometric facts |
| **Foundry** (Sprint 7, not yet formalized) | Artifact production/export |
| **Vision** (not yet formalized) | Preview/rendering |

Alchemist does **not** own jewelry-domain thresholds (Forge's job), CAD-kernel algorithms (Atlas's job), visual rendering (Vision's job), STEP/STL serialization details (Foundry's job — formalized next in Sprint 7), or professional manufacturing approval (nobody's job yet — see [`04-jewelry-domain/058-professional-validation-register.md`](../04-jewelry-domain/058-professional-validation-register.md)). Alchemist coordinates the pipeline and preserves traceability from JDL field to generated artifact.

## Reading order

1. [`160-alchemist-governance.md`](160-alchemist-governance.md) — 15 non-negotiable rules.
2. [`161-compiler-architecture-overview.md`](161-compiler-architecture-overview.md), [`162-compiler-boundaries.md`](162-compiler-boundaries.md).
3. [`163-compilation-input-contract.md`](163-compilation-input-contract.md), [`164-normalization-stage.md`](164-normalization-stage.md), [`165-forge-evaluation-integration.md`](165-forge-evaluation-integration.md).
4. The `GeometryPlan`: [`166-geometry-plan-model.md`](166-geometry-plan-model.md), [`167-geometry-plan-generation.md`](167-geometry-plan-generation.md), [`168-atlas-execution-contract.md`](168-atlas-execution-contract.md), [`169-component-build-order.md`](169-component-build-order.md).
5. [`170-compilation-state-machine.md`](170-compilation-state-machine.md), [`171-compilation-result-model.md`](171-compilation-result-model.md), [`172-diagnostics-and-failure-propagation.md`](172-diagnostics-and-failure-propagation.md), [`173-partial-compilation-policy.md`](173-partial-compilation-policy.md).
6. Identity and versioning: [`174-determinism-and-version-fingerprint.md`](174-determinism-and-version-fingerprint.md), [`175-definition-hash-vs-compilation-hash.md`](175-definition-hash-vs-compilation-hash.md), [`176-compilation-cache-model.md`](176-compilation-cache-model.md).
7. Artifacts: [`177-artifact-request-model.md`](177-artifact-request-model.md), [`178-artifact-manifest-contract.md`](178-artifact-manifest-contract.md), [`179-preview-generation-integration.md`](179-preview-generation-integration.md), [`180-export-generation-integration.md`](180-export-generation-integration.md).
8. [`181-compiler-capability-model.md`](181-compiler-capability-model.md), [`182-compiler-versioning.md`](182-compiler-versioning.md), [`183-current-backend-to-compiler-mapping.md`](183-current-backend-to-compiler-mapping.md).
9. [`184-compiler-observability.md`](184-compiler-observability.md), [`185-compiler-performance-model.md`](185-compiler-performance-model.md), [`186-compiler-security-and-resource-limits.md`](186-compiler-security-and-resource-limits.md).
10. [`187-alchemist-gap-analysis.md`](187-alchemist-gap-analysis.md), [`188-open-alchemist-questions.md`](188-open-alchemist-questions.md).

## Appendices

[`alchemist-stage-catalog.md`](../appendices/alchemist-stage-catalog.md), [`alchemist-state-transition-matrix.md`](../appendices/alchemist-state-transition-matrix.md), [`geometry-plan-field-catalog.md`](../appendices/geometry-plan-field-catalog.md), [`compilation-result-field-catalog.md`](../appendices/compilation-result-field-catalog.md), [`compiler-diagnostic-catalog.md`](../appendices/compiler-diagnostic-catalog.md), [`compiler-code-mapping.md`](../appendices/compiler-code-mapping.md), [`compiler-test-matrix.md`](../appendices/compiler-test-matrix.md).

## Machine-readable specification

[`specs/alchemist/v1/`](../../../specs/alchemist/v1/README.md) holds 8 JSON Schemas, 6 example records, and 7 test-vector files. `backend/tests/test_alchemist_registry.py` re-checks all of it on every test run.

## The single most important finding of this Sprint

**Preview generation is coupled to core geometry generation; export generation is correctly decoupled.** `ModelService.generate()` calls `write_component_previews()` inline — a hypothetical preview-tessellation failure today would fail the *entire* compilation (`MODEL_GENERATION_FAILED`), even though the underlying B-Rep geometry was completely valid. STEP/STL export, by contrast, is a genuinely separate later call against an already-cached model, so an export failure correctly never invalidates the geometry that was already generated. See [`173-partial-compilation-policy.md`](173-partial-compilation-policy.md) and [`187-alchemist-gap-analysis.md`](187-alchemist-gap-analysis.md).

## Relationship to Sprint 9

[`11-studio/`](../11-studio/README.md) (Sprint 9) is the human-facing workflow layer around Alchemist's compilation pipeline — its `computeModelState()`/`ModelStatusBadge` name the same generation lifecycle this Sprint's `170-compilation-state-machine.md` already modeled conceptually, now given a real, visible, 7-state frontend implementation. Studio orchestrates when the user *sees* a compilation result; it never orchestrates the compilation itself.

## Relationship to Sprint 10

[`12-designer/`](../12-designer/README.md) (Sprint 10) never touches Alchemist orchestration directly — `backend/jewelmind/designer/` has no import of, or call into, `services/model_service.py`. An accepted Designer proposal only ever updates design state (`currentDefinition`, via `useProjectStore.applyDesignerProposal()`) the same way a manual parameter edit does; Alchemist's compilation pipeline reads that state on the next `generate()` call exactly as before, with no awareness that a particular edit originated from natural language rather than a form field. See [`12-designer/320-current-studio-integration.md`](../12-designer/320-current-studio-integration.md).

## Validation of this sprint

See [`SPRINT-6-VALIDATION-REPORT.md`](SPRINT-6-VALIDATION-REPORT.md) for the checks run against this section and the findings from that pass.
