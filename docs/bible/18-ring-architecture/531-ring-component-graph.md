---
id: JM-BIBLE-531
title: Ring Component Graph
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-RING-README
  - JM-BIBLE-520
related_documents:
  - JM-BIBLE-521
implementation_status: current
professional_validation: not_required
normative: true
---

# Ring Component Graph

This document maps the **real** geometry component graph — which actual
Atlas solids (`GeneratedComponent` entries in a `GeneratedModel`, see
[`geometry/model.py`](../../../backend/jewelmind/geometry/model.py)) sit
under each `RingDefinition` v2 architectural node
([`ring/models.py`](../../../backend/jewelmind/ring/models.py)). Every
row below is real generated data from
[`specs/ring/v2/test-vectors/component-composition-vectors.json`](../../../specs/ring/v2/test-vectors/component-composition-vectors.json),
never invented for this document.

## The graph

| Architecture node | Real component IDs | `GEOMETRY_ROLE` ([`roles.py`](../../../backend/jewelmind/geometry/roles.py)) | `PRODUCTION_ROLE` | `graphType` |
|---|---|---|---|---|
| `shank` | `band` | `production_metal` | `included_by_default` | CURRENT |
| `head` | `basket_support`, `prongs` | `production_metal`, `production_metal` | `included_by_default`, `included_by_default` | CURRENT |
| `stoneArrangement` | `stone_reference` | `stone_reference` | `excluded_by_default` | CURRENT |

These are the complete four `GeneratedComponent` names the real solitaire
builder produces — no fifth component exists, and no component listed
above is silently dropped from any node (ATLAS-GOV-006 restated at this
mapping layer).

## Reconciling an apparent inconsistency: where prong *geometry* lives vs. where prong *data* lives

The table above groups `prongs` under the **`head`** node — this is a
statement about physical geometry composition: the prong solids are
built and reported as part of the head assembly region of the ring, the
same region `basket_support` occupies.

This does **not** match where prong *data* lives in the Pydantic model.
`prongCount`, `prongDiameterMm`, and `prongHeightMm` are owned by
`SettingAttachmentDefinition`, not `RingHeadDefinition` — see
[`ring/models.py`](../../../backend/jewelmind/ring/models.py):
`RingHeadDefinition` carries only `basketHeightMm`, and its own docstring
states it "deliberately excludes prong/setting fields, which belong to
`SettingAttachmentDefinition`."

These are **two different concerns, not a contradiction**:

- **Geometric composition** (this document): which real Atlas solids are
  physically grouped under which architectural region. Prong solids are
  part of the head region because that is where they are built.
- **Data ownership** (governed by JEWELRY-ARCH-GOV-005, see
  [`520-jewelry-category-architecture.md`](520-jewelry-category-architecture.md)):
  a setting (prong count/diameter/height) is a concept potentially
  reusable outside rings; *how* it structurally attaches to a ring head
  (the basket height) is ring-specific. Splitting the data this way lets
  a future non-ring category reuse `SettingAttachmentDefinition`-shaped
  data without inheriting `RingHeadDefinition`'s ring-only basket
  concept, even though today, for a ring, the prong solids and the
  basket solid happen to occupy the same physical region.

Nothing in the geometry graph or the data model was changed to make this
line up artificially — both are simply true at the same time, for
different reasons.

## CURRENT vs. TARGET

The brief's own illustrative target graph for the ring category is:

```
Ring
  Shank    -> Band
  Head     -> BasketSupport, Prongs
  StoneArrangement -> StoneReference
```

This is **identical** to the CURRENT graph above for the solitaire
family — every node the brief's target illustration names already maps
to a real component today, and no node is empty or aspirational. So for
this specific case, **TARGET == CURRENT**; there is no gap to close for
solitaire.

The CURRENT/TARGET distinction only becomes meaningful once a second
ring family, or a non-ring category, is implemented (none is, this
Sprint — [`524-ring-family-model.md`](524-ring-family-model.md),
[`537-open-ring-architecture-questions.md`](537-open-ring-architecture-questions.md)).
For example, a future `three_stone` family would need `stoneArrangement`
to map to more than one `stone_reference`-role component, and a future
`halo` family would need a new component name entirely — neither is
defined here, since neither exists in real code
(`RING_FAMILY_GENERATORS` in
[`ring/families.py`](../../../backend/jewelmind/ring/families.py)
registers only `solitaire`; see
[`536-current-code-mapping-and-gaps.md`](536-current-code-mapping-and-gaps.md)).

## Non-goals of this document

This is not a second geometry specification. The authoritative component
contract remains
[`../07-atlas/130-component-contract.md`](../07-atlas/130-component-contract.md)
and the [`atlas-component-catalog.md`](../appendices/atlas-component-catalog.md)
appendix; this document only adds the architecture-node grouping layer
introduced by Ring Architecture v2 on top of those unchanged Atlas
facts.
