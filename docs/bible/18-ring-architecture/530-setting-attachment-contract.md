---
id: JM-BIBLE-530
title: Setting Attachment Contract
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
  - JM-BIBLE-528
  - JM-BIBLE-047
  - JM-BIBLE-048
implementation_status: current
professional_validation: not_required
normative: true
---

# Setting Attachment Contract

## The real current state

`SettingAttachmentDefinition` (`backend/jewelmind/ring/models.py`):

```python
class SettingAttachmentDefinition(RingModel):
    settingType: SettingType        # Literal["prong"]
    prongCount: int
    prongDiameterMm: float
    prongHeightMm: float
```

Mapped 1:1 by
[`ring_definition_from_jdl()`](../../../backend/jewelmind/ring/adapter.py)
from `domain/schema.py::SettingSpec`'s `type`, `prongCount`,
`prongDiameter`, `prongHeight` fields (`basketHeight` is deliberately
excluded — see below). Status, per `models.py`'s own docstring:
**CURRENT — prong only.** `SettingSpec`'s and `ProngSet`'s own domain
semantics are authoritatively defined at
[`../04-jewelry-domain/047-setting-domain.md`](../04-jewelry-domain/047-setting-domain.md)
and [`../04-jewelry-domain/048-prong-domain.md`](../04-jewelry-domain/048-prong-domain.md)
and not restated here.

## The boundary this contract formalizes

A `ProngSetting` concept may eventually be reusable across ring, pendant,
and earring categories — nothing about "a stone held by N prongs of a
given diameter and height" is inherently ring-shaped. **How that setting
connects to a ring head is ring-specific** — that is
[`RingHeadDefinition.basketHeightMm`](528-head-contract.md), a completely
separate field on a completely separate model
(JEWELRY-ARCH-GOV-005). `SettingAttachmentDefinition` never owns
basket-height data, and `RingHeadDefinition` never owns prong data —
verified by `test_head_mapping` and `test_setting_attachment_mapping` in
[`backend/tests/test_ring_architecture.py`](../../../backend/tests/test_ring_architecture.py).

## This Sprint does not build a general Setting System

This Sprint deliberately does not attempt to fully redesign a general
Setting System — that belongs to a later sprint, per this Sprint's own
brief. `SettingAttachmentDefinition` is a same-shape wrapper around the
existing, unmodified `SettingSpec` prong fields, not a new abstraction
over bezel, tension, channel, or other setting types.
`domain/schema.py::SettingType` remains `Literal["prong"]`; no code in
`jewelmind.ring` or `jewelmind.jewelry_category` widens it or adds a
setting-type registry.

## What this Sprint did not do

- No new setting type (bezel, tension, channel, halo) was implemented
  anywhere — these remain listed only as unsupported concepts in
  [`backend/jewelmind/designer/capability.py::KNOWN_UNSUPPORTED_CONCEPTS`](../../../backend/jewelmind/designer/capability.py).
- No general, category-agnostic "Setting System" abstraction was
  introduced; `SettingAttachmentDefinition` is Ring Architecture's own
  wrapper, not a shared package.
- `jewelmind.jewelry_category.forge_scope.rule_scope()` classifies
  `PRONG_COUNT` (`JM-PRONG-*`) as `shared_setting` scope, distinct from
  `SETTING_BASKET_HEIGHT_POSITIVE`'s `ring_head` scope — see
  [`521-shared-vs-category-specific-domain.md`](521-shared-vs-category-specific-domain.md).
