---
id: JM-BIBLE-A31
title: "Appendix: Compiler Diagnostic Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-172
related_documents:
  - JM-BIBLE-A11
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Compiler Diagnostic Catalog

Every failure scenario from [`08-alchemist/172-diagnostics-and-failure-propagation.md`](../08-alchemist/172-diagnostics-and-failure-propagation.md), with real current codes — none renamed from Sprint 3/4's catalogs.

| Scenario | Real code | HTTP status |
|---|---|---|
| Invalid JDL (structural) | `REQUEST_VALIDATION_ERROR` | 422 |
| Forge generation blocker | `VALIDATION_BLOCKED` | 422 |
| Required component construction failure | `MODEL_GENERATION_FAILED` | 500 |
| Combined-metal fuse failure | (not an error — a warning, generation succeeds) | 200 |
| STEP export failure | `STEP_EXPORT_FAILED` | 500 |
| STL export failure | `STL_EXPORT_FAILED` | 500 |
| Unknown/evicted `modelId` | `MODEL_NOT_FOUND` | 404 |
| CAD engine unavailable | `CAD_ENGINE_UNAVAILABLE` | 503 |

See [`appendices/jdl-error-code-catalog.md`](jdl-error-code-catalog.md) for the complete, original, unmodified list this table draws from.
