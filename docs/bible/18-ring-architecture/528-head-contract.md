---
id: JM-BIBLE-528
title: Head Contract
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
  - JM-BIBLE-523
  - JM-BIBLE-530
  - JM-BIBLE-049
implementation_status: current
professional_validation: not_required
normative: true
---

# Head Contract

## The real current state

`RingHeadDefinition` (`backend/jewelmind/ring/models.py`) has exactly one
field:

```python
class RingHeadDefinition(RingModel):
    basketHeightMm: float
```

Mapped by [`ring_definition_from_jdl()`](../../../backend/jewelmind/ring/adapter.py)
from `definition.setting.basketHeight` — the same real field the
unchanged basket-support geometry builder consumes (see
[`../04-jewelry-domain/049-basket-and-support-domain.md`](../04-jewelry-domain/049-basket-and-support-domain.md)
for `BasketSupport`'s own domain definition, not restated here).

Status, per `models.py`'s own docstring: **PARTIAL** — "the structural
integration of the setting into the ring — currently just the basket
support height."

## The deliberate separation from `SettingAttachmentDefinition`

`RingHeadDefinition` never owns `prongCount`, `prongDiameterMm`, or
`prongHeightMm` — those live on
[`SettingAttachmentDefinition`](530-setting-attachment-contract.md)
instead (JEWELRY-ARCH-GOV-005). The reasoning:

- A **setting** (e.g. a prong setting) is a concept potentially reusable
  outside rings — a future earring or pendant could use a prong setting
  too, independent of anything ring-shaped.
- **How that setting structurally integrates into a ring specifically** —
  its basket support, its height above the shank — is ring-specific and
  has no category-neutral meaning.

`test_head_mapping` in
[`backend/tests/test_ring_architecture.py`](../../../backend/tests/test_ring_architecture.py)
asserts this boundary directly: `not hasattr(ring_definition.head, "prongCount")`.

## Two different concerns that could otherwise look inconsistent

The real geometry component graph (see
[`531-ring-component-graph.md`](531-ring-component-graph.md)) groups
**both** the `basket_support` and `prongs` real Atlas components
(`geometry/assemblies/solitaire.py`'s `components` dict) under a "head"
architectural grouping, even though their **data** fields live in two
separate `RingDefinition` sub-models — `basketHeightMm` on
`RingHeadDefinition`, `prongCount`/`prongDiameterMm`/`prongHeightMm` on
`SettingAttachmentDefinition`.

This is not an inconsistency; it is two different axes of classification:

- **Data ownership** (this document's concern): which `RingDefinition`
  sub-model a field belongs to, driven by whether the field's *meaning*
  is ring-specific or potentially shared (JEWELRY-ARCH-GOV-005).
- **Geometric composition** (531's concern): which real Atlas components
  are physically grouped together when reasoning about "the head" as an
  assembly of solids, regardless of which JDL field drove each one.

A component can be architecturally grouped under "head" for composition
purposes while its driving data field is owned by a different, more
semantically precise sub-model. Do not read the component-graph grouping
as evidence that `RingHeadDefinition` should also own prong data — the
grouping and the data-ownership boundary answer different questions.

## What this Sprint did not do

No new head/basket geometry was added; `geometry/components/` is
unchanged. No field beyond `basketHeightMm` was added to
`RingHeadDefinition`.
