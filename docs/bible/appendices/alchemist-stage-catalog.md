---
id: JM-BIBLE-A27
title: "Appendix: Alchemist Stage Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-161
related_documents: []
implementation_status: partial
professional_validation: not_required
normative: true
---

# Appendix: Alchemist Stage Catalog

The 13 conceptual compilation stages, from [`08-alchemist/161-compiler-architecture-overview.md`](../08-alchemist/161-compiler-architecture-overview.md), with current implementation status.

| Stage | Status | Current code |
|---|---|---|
| Authoring Input → JDL Canonical Document | CURRENT | `JewelryDefinition.model_validate()` |
| Compiler Input | PARTIAL | Bare `JewelryDefinition`, no wrapper |
| Normalization | CURRENT | Pydantic default-filling |
| Forge Evaluation | CURRENT | `validate_definition()` |
| Eligibility Decision | CURRENT | `has_errors()` gate |
| GeometryPlan | PLANNED | Does not exist |
| Atlas Execution | CURRENT (direct call, not via plan) | `build_solitaire_ring()` |
| Atlas Inspection | PARTIAL | 1 runtime check |
| Post-Geometry Forge Evaluation | NOT IMPLEMENTED | — |
| Artifact Requests | PARTIAL | 4 separate endpoints |
| Foundry / Vision | CURRENT, not yet named as layers | `exporters/*.py`, `preview/mesh.py` |
| Artifact Manifest | PARTIAL | Preview only |
| CompilationResult | PARTIAL | `GenerateResponse`/`ModelMetadataResponse` |

**5 CURRENT, 6 PARTIAL, 1 PLANNED, 1 NOT IMPLEMENTED.**
