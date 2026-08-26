---
id: JM-BIBLE-A106
title: "Appendix: Ring Component Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-RING-README
  - JM-BIBLE-520
related_documents:
  - JM-BIBLE-531
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Ring Component Catalog

## Architecture node -> real component IDs

From
[`specs/ring/v2/test-vectors/component-composition-vectors.json`](../../../specs/ring/v2/test-vectors/component-composition-vectors.json)
(real generated data):

| Architecture node | Real component IDs | `graphType` |
|---|---|---|
| `shank` | `band` | `CURRENT` |
| `head` | `basket_support`, `prongs` | `CURRENT` |
| `stoneArrangement` | `stone_reference` | `CURRENT` |

## Real `GeneratedComponent` identities and roles

From
[`backend/jewelmind/geometry/model.py`](../../../backend/jewelmind/geometry/model.py)
(`GeneratedComponent`/`GeneratedModel`) and
[`backend/jewelmind/geometry/roles.py`](../../../backend/jewelmind/geometry/roles.py)
(`GEOMETRY_ROLE`/`PRODUCTION_ROLE`) — unchanged this Sprint:

| Component name | `GeometryRole` | `ProductionRole` |
|---|---|---|
| `band` | `production_metal` | `included_by_default` |
| `prongs` | `production_metal` | `included_by_default` |
| `basket_support` | `production_metal` | `included_by_default` |
| `stone_reference` | `stone_reference` | `excluded_by_default` |

These are the complete set of 4 named components the real solitaire
builder produces. `production_metal` components are unioned into the
combined metal body and included in an export by default;
`stone_reference` is never unioned into metal, and is only included in
an export when the caller explicitly opts in with
`includeStoneReference: true` (LAW-006).

See [`531-ring-component-graph.md`](../18-ring-architecture/531-ring-component-graph.md)
for the reconciliation between this component grouping and where
setting/prong *data* (as opposed to geometry) lives in `RingDefinition`
v2.
