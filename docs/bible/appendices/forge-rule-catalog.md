---
id: JM-BIBLE-A14
title: "Appendix: Forge Rule Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-110
related_documents:
  - JM-BIBLE-054
implementation_status: current
professional_validation: preliminary
normative: true
---

# Appendix: Forge Rule Catalog

The complete, current catalog of all 21 Forge rules — the human-readable companion to `specs/forge/v1/current-rule-registry.json`, which remains the machine-checked source of truth. See [`06-forge/110-current-rule-inventory.md`](../06-forge/110-current-rule-inventory.md) for the fully detailed table (code location, test location, condition, provenance, geometry/manufacturing influence, frontend duplication).

| Rule ID | Name | Category | Stage | Severity | Version | Lifecycle |
|---|---|---|---|---|---|---|
| `JM-RING-001` | Inner diameter range | PROTOTYPE_HEURISTIC | FORGE-4 | error | 1.0.0 | ACCEPTED |
| `JM-RING-002` | EU size range | PROTOTYPE_HEURISTIC | FORGE-4 | error | 1.0.0 | ACCEPTED |
| `JM-RING-003` | Size/diameter consistency | SEMANTIC_COMPATIBILITY | FORGE-1 | information/warning | 1.0.0 | ACCEPTED |
| `JM-BAND-001` | Minimum band width | PROTOTYPE_HEURISTIC | FORGE-4 | error | 1.0.0 | ACCEPTED |
| `JM-BAND-002` | Minimum band thickness | PROTOTYPE_HEURISTIC | FORGE-4 | error/warning | 1.0.0 | ACCEPTED |
| `JM-BAND-003` | Maximum band width advisory | PROTOTYPE_HEURISTIC | FORGE-4 | warning | 1.0.0 | ACCEPTED |
| `JM-STONE-001` | Stone diameter range | PROTOTYPE_HEURISTIC | FORGE-4 | error | 1.0.0 | ACCEPTED |
| `JM-STONE-002` | Depth vs. diameter | DOMAIN_INVARIANT | FORGE-2 | error | 1.0.0 | ACCEPTED |
| `JM-PRONG-001` | Prong count set | PROTOTYPE_HEURISTIC | FORGE-4 | error | 1.0.0 | ACCEPTED |
| `JM-PRONG-002` | Prong diameter minimum | PROTOTYPE_HEURISTIC | FORGE-4 | error/warning | 1.0.0 | ACCEPTED |
| `JM-PRONG-003` | Prong count vs. stone size | PROTOTYPE_HEURISTIC | FORGE-4 | warning | 1.0.0 | ACCEPTED |
| `JM-PRONG-004` | Prong height vs. basket height | SEMANTIC_COMPATIBILITY | FORGE-1 | error | 1.0.0 | ACCEPTED |
| `JM-SETTING-001` | Basket height positivity | GEOMETRY_PRECONDITION | FORGE-3 | error | 1.0.0 | ACCEPTED |
| `JM-SETTING-002` | Basket height maximum | PROTOTYPE_HEURISTIC | FORGE-4 | warning | 1.0.0 | ACCEPTED |
| `JM-SETTING-003` | Bezel wall thickness positivity | GEOMETRY_PRECONDITION | FORGE-3 | error | 1.0.0 | ACCEPTED |
| `JM-SETTING-004` | Bezel wall height positivity | GEOMETRY_PRECONDITION | FORGE-3 | error | 1.0.0 | ACCEPTED |
| `JM-GEM-001` | Gem reference exists | SEMANTIC_COMPATIBILITY | FORGE-1 | warning | 1.0.0 | ACCEPTED |
| `JM-GEM-002` | Origin applicable to entry | SEMANTIC_COMPATIBILITY | FORGE-1 | error | 1.0.0 | ACCEPTED |
| `JM-GEM-003` | Custom gem coherence | SEMANTIC_COMPATIBILITY | FORGE-1 | error | 1.0.0 | ACCEPTED |
| `JM-GEM-004` | Visual profile resolves | SEMANTIC_COMPATIBILITY | FORGE-1 | warning | 1.0.0 | ACCEPTED |
| `JM-GEM-005` | Treatment set coherence | SEMANTIC_COMPATIBILITY | FORGE-1 | warning/error | 1.0.0 | ACCEPTED |
| `JM-GEM-006` | Entry deprecated but resolvable | SEMANTIC_COMPATIBILITY | FORGE-1 | warning | 1.0.0 | ACCEPTED |
| `JM-SETTING-005` | Head parameters complete | GEOMETRY_PRECONDITION | FORGE-3 | error | 1.0.0 | ACCEPTED |
| `JM-SETTING-006` | Field applicable to family | SEMANTIC_COMPATIBILITY | FORGE-1 | information | 1.0.0 | ACCEPTED |
| `JM-SETTING-007` | Seat relief feasible | SEMANTIC_COMPATIBILITY | FORGE-1 | warning | 1.0.0 | ACCEPTED |
| `JM-ARRANGE-001` | Instance ids unique | SEMANTIC_COMPATIBILITY | FORGE-1 | error | 1.0.0 | ACCEPTED |
| `JM-ARRANGE-002` | Arrangement references resolve | SEMANTIC_COMPATIBILITY | FORGE-1 | error | 1.0.0 | ACCEPTED |
| `JM-ARRANGE-003` | Stone reference resolves | SEMANTIC_COMPATIBILITY | FORGE-1 | warning | 1.0.0 | ACCEPTED |
| `JM-ARRANGE-004` | Arrangement structure resolves | SEMANTIC_COMPATIBILITY | FORGE-1 | error | 1.0.0 | ACCEPTED |
| `JM-ARRANGE-005` | Instance role coherence | SEMANTIC_COMPATIBILITY | FORGE-1 | warning | 1.0.0 | ACCEPTED |
| `JM-ARRANGE-006` | Multi-stone generation boundary | SEMANTIC_COMPATIBILITY | FORGE-1 | information | 1.0.0 | ACCEPTED |
| `JM-MANUFACTURING-001` | Minimum feature size (resin) | MANUFACTURING_CONTEXT | FORGE-5 | warning | 1.0.0 | ACCEPTED |
| `JM-GEOMETRY-001` | Positive outer band dimension | GEOMETRY_PRECONDITION | FORGE-3 | error | 1.0.0 | ACCEPTED |
| `FORGE-SCHEMA-001` | Schema version literal | SCHEMA_INTEGRITY | FORGE-0 | fatal | 1.0.0 | ACCEPTED |
| `FORGE-SAFETY-001` | No non-finite numbers | SYSTEM_SAFETY | FORGE-0 | fatal | 1.0.0 | ACCEPTED |
| `FORGE-SAFETY-002` | No unknown fields | SYSTEM_SAFETY | FORGE-0 | fatal | 1.0.0 | ACCEPTED |
| `FORGE-GEOM-001` | Fuse must yield a solid | GEOMETRY_INSPECTION | FORGE-7 | warning | 1.0.0 | ACCEPTED |
| `FORGE-EXPORT-001` | Export requires a valid cached record | EXPORT_PRECONDITION | FORGE-8 | error-equivalent | 1.0.0 | ACCEPTED |

**Total: 21 rules. Professionally validated: 0.**
