---
id: JM-BIBLE-FOUNDRY-README
title: Foundry Export System v1 — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-ALCHEMIST-README
  - JM-BIBLE-ATLAS-README
related_documents:
  - JM-BIBLE-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Foundry Export System v1 — Index

This is **Sprint 7** of the Technical Bible: **Foundry Export System v1**. Foundry is the artifact-generation and export-integrity layer — the boundary between a validated, compiled model and a file the outside world can open: STEP, STL, canonical JDL JSON, or a technical specification. **Unlike Sprint 6 (Alchemist), Foundry v1 formalizes an export system that already runs in production** — `export_step()`, `export_stl()`, `export_json()`, and `build_specification()` are real, exercised code paths today, not a target architecture. This Sprint also permits, and performs, a small set of targeted hardening changes (shared shape-selection extraction, checksums, non-empty-file validation) that Sprint 6 explicitly deferred to it.

**Read this README, then [`190-foundry-governance.md`](190-foundry-governance.md), before changing anything in `backend/jewelmind/exporters/`.**

## The five-layer architecture Foundry sits inside

| Layer | Owns |
|---|---|
| **JDL** (Sprint 3) | Declarative design definition |
| **Forge** (Sprint 4) | Rule evaluation and eligibility |
| **Alchemist** (Sprint 6) | Orchestration and deterministic compilation planning |
| **Atlas** (Sprint 5) | Geometry construction and geometric facts |
| **Foundry** (this Sprint) | Artifact generation and file-level integrity validation |
| **Vision** (Sprint 8, not yet formalized) | Preview/presentation rendering |

Foundry does not own jewelry-domain thresholds (Forge's job), geometry construction (Atlas's job), compilation orchestration or `definitionHash`/`compilationHash` (Alchemist's job), or visual rendering (Vision's job). Foundry selects already-built shapes, serializes them (or the definition, or a report) to a real file, and validates the result at the file level.

## Reading order

1. [`190-foundry-governance.md`](190-foundry-governance.md) — 18 non-negotiable rules.
2. [`191-foundry-architecture-overview.md`](191-foundry-architecture-overview.md), [`192-artifact-domain-model.md`](192-artifact-domain-model.md), [`193-artifact-request-contract.md`](193-artifact-request-contract.md), [`194-generation-pipeline.md`](194-generation-pipeline.md).
3. Component selection: [`195-component-inclusion-policy.md`](195-component-inclusion-policy.md), [`196-production-geometry-selection.md`](196-production-geometry-selection.md).
4. Per-format contracts: [`197-step-export-contract.md`](197-step-export-contract.md), [`198-stl-export-contract.md`](198-stl-export-contract.md), [`199-json-export-contract.md`](199-json-export-contract.md), [`200-technical-specification-contract.md`](200-technical-specification-contract.md).
5. Records and integrity: [`201-artifact-manifest-model.md`](201-artifact-manifest-model.md), [`202-artifact-integrity-model.md`](202-artifact-integrity-model.md), [`203-export-validation-pipeline.md`](203-export-validation-pipeline.md), [`204-export-diagnostics.md`](204-export-diagnostics.md), [`205-export-failure-and-partial-success.md`](205-export-failure-and-partial-success.md).
6. Safety and lifecycle: [`206-filename-and-path-safety.md`](206-filename-and-path-safety.md), [`207-temp-file-lifecycle.md`](207-temp-file-lifecycle.md), [`208-export-version-fingerprint.md`](208-export-version-fingerprint.md).
7. Interoperability: [`209-cad-interoperability-philosophy.md`](209-cad-interoperability-philosophy.md), [`210-step-interoperability-boundaries.md`](210-step-interoperability-boundaries.md), [`211-stl-interoperability-boundaries.md`](211-stl-interoperability-boundaries.md), [`212-unit-and-scale-contract.md`](212-unit-and-scale-contract.md).
8. [`213-multi-solid-and-fusion-policy.md`](213-multi-solid-and-fusion-policy.md), [`214-export-roundtrip-validation.md`](214-export-roundtrip-validation.md).
9. [`215-foundry-performance-model.md`](215-foundry-performance-model.md), [`216-foundry-security-and-resource-limits.md`](216-foundry-security-and-resource-limits.md), [`217-current-exporter-code-mapping.md`](217-current-exporter-code-mapping.md).
10. [`218-foundry-gap-analysis.md`](218-foundry-gap-analysis.md), [`219-open-foundry-questions.md`](219-open-foundry-questions.md).

## Appendices

[`foundry-artifact-catalog.md`](../appendices/foundry-artifact-catalog.md), [`foundry-mime-type-catalog.md`](../appendices/foundry-mime-type-catalog.md), [`foundry-component-inclusion-matrix.md`](../appendices/foundry-component-inclusion-matrix.md), [`foundry-export-diagnostic-catalog.md`](../appendices/foundry-export-diagnostic-catalog.md), [`foundry-export-test-matrix.md`](../appendices/foundry-export-test-matrix.md), [`foundry-code-mapping.md`](../appendices/foundry-code-mapping.md), [`foundry-interoperability-matrix.md`](../appendices/foundry-interoperability-matrix.md).

## Machine-readable specification

[`specs/foundry/v1/`](../../../specs/foundry/v1/README.md) holds 6 JSON Schemas, 7 example records, and 7 test-vector files. `backend/tests/test_foundry_registry.py` re-checks all of it, plus live cross-checks against `sanitize_filename()` and `select_export_shapes()`, on every test run.

## The single most important finding of this Sprint

**STEP and STL export have opposite determinism profiles, and this was previously undocumented.** STL export is byte-for-byte deterministic across repeated exports of the same design (identical SHA-256 checksums, confirmed this Sprint). STEP export is not: two exports of an identical model differ in exactly 2 of ~4315 lines — an embedded wall-clock timestamp and an incrementing OpenCascade translator-instance counter — while every line of actual geometry data is identical. This means a STEP checksum cannot serve as a stable content-identity proxy the way an STL checksum can, a fact with direct consequences for any future caching or deduplication strategy built on export checksums. See [`197-step-export-contract.md`](197-step-export-contract.md) and [`202-artifact-integrity-model.md`](202-artifact-integrity-model.md).

## Validation of this sprint

See [`SPRINT-7-VALIDATION-REPORT.md`](SPRINT-7-VALIDATION-REPORT.md) for the checks run against this section and the findings from that pass.
