---
id: JM-BIBLE-524
title: Ring Family Model
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
  - JM-BIBLE-042
implementation_status: current
professional_validation: not_required
normative: true
---

# Ring Family Model

`RingFamily` is a concept distinct from jewelry *category*
(JEWELRY-ARCH-GOV-001/010): category answers "what kind of jewelry piece is
this" (ring, earring, ...); family answers "which style of ring is this"
(solitaire, three-stone, ...). The two are dispatched through two separate,
nested boundaries — see [`532-ring-generation-contract.md`](532-ring-generation-contract.md).

## `RingFamilyId` — the real 8-value vocabulary

Defined in
[`backend/jewelmind/ring/models.py`](../../../backend/jewelmind/ring/models.py):

```python
RingFamilyId = Literal[
    "solitaire",
    "three_stone",
    "toi_et_moi",
    "halo",
    "eternity",
    "signet",
    "plain_band",
    "cluster",
]
```

| Family | Status | Generator registered? |
|---|---|---|
| `solitaire` | CURRENT | Yes — `RING_FAMILY_GENERATORS["solitaire"] = build_solitaire_ring` |
| `three_stone`, `toi_et_moi`, `halo`, `eternity`, `signet`, `plain_band`, `cluster` | PLANNED (reserved) | No |

The 7 reserved names are also exposed as
`jewelmind.ring.families.RESERVED_PLANNED_RING_FAMILIES` — metadata only,
proving the family dispatch boundary is not solitaire-specific without
implementing any of them.

## Why the reserved names exist at all

Their sole purpose is to prove `RingFamilyId` and the family-dispatch
mechanism in
[`jewelmind.ring.families.generate_ring()`](../../../backend/jewelmind/ring/families.py)
are not accidentally coupled to solitaire being the only possible value.
None of the 7 has a generator, a geometry builder, a JDL default, or a
test that exercises real generation for it (JEWELRY-ARCH-GOV-010).

## The real dispatch-boundary proof, and the design correction it forced

[`backend/tests/test_ring_architecture.py::TestSolitaireFamilyDispatch::test_unsupported_ring_family_raises_a_clean_error`](../../../backend/tests/test_ring_architecture.py)
is the test that proves an unsupported-but-recognized family is rejected
at the **dispatch boundary** (`RING_FAMILY_GENERATORS.get()` returning
`None`), never at schema validation. It does this by bypassing
`domain/schema.py::StrictModel`'s Pydantic validation with
`object.__setattr__(d.jewelry, "style", "three_stone")`, simulating a
future JDL input that allowed `"three_stone"` as a `jewelry.style` value,
then asserting `generate_ring(d)` raises `RingFamilyUnsupportedError`.

This test forced a real design correction during this Sprint's own
implementation: `RingFamilyId` was initially typed as `Literal["solitaire"]`
only. Under that typing, the defensive test above failed with a Pydantic
`ValidationError` when constructing the `RingDefinition` — the rejection
happened at the wrong layer (schema-shaped validation on an internal model,
not the intended `RingFamilyUnsupportedError` from
`jewelmind.jewelry_category.errors`), because `RingDefinition.family` could
never legally hold `"three_stone"` in the first place. The literal was
deliberately widened to the current 8-value vocabulary specifically so
that "recognized but unregistered" and "not recognized at all" remain two
distinguishable, testable states, and so that the dispatch check in
`generate_ring()` — not Pydantic — is what raises
`RingFamilyUnsupportedError` (JEWELRY-ARCH-GOV-010).

## What this Sprint did not do

No reserved family has geometry, a JDL-reachable path (the real
`domain/schema.py::JewelryStyle` is still `Literal["solitaire"]` — see
[`520-jewelry-category-architecture.md`](520-jewelry-category-architecture.md),
JEWELRY-ARCH-GOV-008), or a Designer/Conversation capability entry.
Widening `JewelryStyle` itself to accept a second real value is future
work requiring the domain-extension RFC process — see
[`../04-jewelry-domain/056-domain-extension-strategy.md`](../04-jewelry-domain/056-domain-extension-strategy.md).
