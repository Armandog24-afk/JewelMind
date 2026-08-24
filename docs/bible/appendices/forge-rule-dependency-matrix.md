---
id: JM-BIBLE-A18
title: "Appendix: Forge Rule Dependency Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-100
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Forge Rule Dependency Matrix

Fixed evaluation order (from `_RULE_GROUPS` in `backend/jewelmind/validation/engine.py`) and declared documentation-only dependencies (from `specs/forge/v1/current-rule-registry.json`).

| Order | Rule group | Rules | Declared dependencies |
|---|---|---|---|
| 1 | Ring | `JM-RING-001`, `JM-RING-002`, `JM-RING-003` | none |
| 2 | Band | `JM-BAND-001`, `JM-BAND-002`, `JM-BAND-003` | none |
| 3 | Stone | `JM-STONE-001`, `JM-STONE-002` | none |
| 4 | Prong | `JM-PRONG-001`, `JM-PRONG-002`, `JM-PRONG-003`, `JM-PRONG-004` | `JM-PRONG-003` documentation-references `JM-PRONG-001` (see [`06-forge/100-rule-dependencies-and-ordering.md`](../06-forge/100-rule-dependencies-and-ordering.md) for why this is not an enforced dependency) |
| 5 | Setting | `JM-SETTING-001`, `JM-SETTING-002` | none |
| 6 | Manufacturing | `JM-MANUFACTURING-001` | none |
| 7 | Geometry | `JM-GEOMETRY-001` | none |
| (pre-engine) | Schema/safety | `FORGE-SCHEMA-001`, `FORGE-SAFETY-001`, `FORGE-SAFETY-002` | none — these run at Pydantic construction time, before `validate_definition()` is ever called |
| (post-generation) | Geometry inspection | `FORGE-GEOM-001` | none — structurally cannot run before FORGE-6 (geometry generation) has produced a shape |
| (export time) | Export precondition | `FORGE-EXPORT-001` | Transitively depends on every FORGE-1..5 rule having produced zero `error` results at generation time |

## No short-circuiting

Every rule within `validate_definition()`'s seven groups runs to completion regardless of earlier results — there is no rule whose evaluation is skipped because an earlier rule fired. Short-circuiting only occurs at the `has_errors()` gate, after all rules have run, before FORGE-6.

## No arbitrary numeric priorities

Ordering is expressed purely as stage + fixed group order + optional documentation-only dependency, per [`06-forge/100-rule-dependencies-and-ordering.md`](../06-forge/100-rule-dependencies-and-ordering.md) — no rule carries a numeric priority field.
