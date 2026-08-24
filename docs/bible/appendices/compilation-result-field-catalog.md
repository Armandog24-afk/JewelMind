---
id: JM-BIBLE-A30
title: "Appendix: Compilation Result Field Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-171
related_documents: []
implementation_status: partial
professional_validation: not_required
normative: true
---

# Appendix: Compilation Result Field Catalog

The field-status summary from [`08-alchemist/171-compilation-result-model.md`](../08-alchemist/171-compilation-result-model.md), condensed.

| Status | Count | Fields |
|---|---|---|
| CURRENT | 8 | `schemaVersion`, `geometryGeneratorVersion`, `sourceDefinitionHash`, `normalizedDefinition`, `forgeEvaluation`, `geometryMetadata`, `createdAt`, `componentManifest` (preview only) |
| PARTIAL | 5 | `status`, `diagnostics`, `artifacts`, `timings`, `cacheStatus` |
| PLANNED | 6 | `compilationId`, `compilerVersion`, `forgeRuleSetVersion`, `kernelVersion`, `compilationHash`, `geometryPlanSummary` |

Real examples: `specs/alchemist/v1/examples/default-solitaire-compilation-result.json` (clean success), `failed-validation-compilation-result.json` (BLOCKED, real Forge diagnostics from the Sprint 3 `invalid-negative-dimension` case).
