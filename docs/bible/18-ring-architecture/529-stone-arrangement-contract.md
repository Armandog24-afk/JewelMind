---
id: JM-BIBLE-529
title: Stone Arrangement Contract
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
  - JM-BIBLE-521
  - JM-BIBLE-046
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Arrangement Contract

## The real current state

`StoneArrangementDefinition` (`backend/jewelmind/ring/models.py`):

```python
class StoneArrangementDefinition(RingModel):
    arrangement: StoneArrangementType   # Literal["SINGLE_CENTER"]
    stone: StoneSpec
```

Status, per `models.py`'s own docstring: **CURRENT — single center stone
only.**

`stone` is not a copy of individual `StoneSpec` fields re-declared on a
new model — it *wraps* the real, unmodified
`domain/schema.py::StoneSpec` directly, via `.model_copy()`:

```python
stoneArrangement=StoneArrangementDefinition(
    arrangement="SINGLE_CENTER",
    stone=definition.stone.model_copy(),
),
```

(from [`ring_definition_from_jdl()`](../../../backend/jewelmind/ring/adapter.py)).
`StoneSpec`'s own domain semantics (`shape`, `diameter`, `depth`) are
authoritatively defined at
[`../04-jewelry-domain/046-stone-domain.md`](../04-jewelry-domain/046-stone-domain.md)
and not restated here.

## A potentially SHARED jewelry concept (JEWELRY-ARCH-GOV-006)

`StoneArrangementDefinition` is classified POTENTIALLY-SHARED-BUT-CONTEXTUAL
in [`521-shared-vs-category-specific-domain.md`](521-shared-vs-category-specific-domain.md):
"how many stones, arranged how" is not inherently a *ring* concept — a
future pendant or earring could equally have a stone arrangement. Because
`StoneArrangementDefinition` wraps `StoneSpec` rather than duplicating its
fields, a future category that needed the same wrapping pattern could
reuse the identical composition approach without inheriting anything
ring-specific from `RingDefinition` itself (JEWELRY-ARCH-GOV-006).

## Future PLANNED arrangement values (not implemented, not even in the schema's enum)

This Sprint's brief names five future arrangement values: `MULTI_STONE`,
`THREE_STONE`, `HALO`, `CLUSTER`, `PAVE_ARRAY`. None of these is
implemented. Critically, none of them exists even as an unused member of
an enum today —
[`specs/ring/v2/stone-arrangement.schema.json`](../../../specs/ring/v2/stone-arrangement.schema.json)
declares `"arrangement": { "const": "SINGLE_CENTER" }`, a JSON Schema
`const`, not an `enum` with additional unused values. Widening that `const`
to an `enum` — and widening the matching Python `Literal` in
`StoneArrangementType` — is deliberate future work requiring its own
change, never an oversight or an implicit gap to "complete."

## What this Sprint did not do

- No multi-stone geometry, layout algorithm, or arrangement-selection
  logic was added anywhere in `geometry/` or `jewelmind.ring`.
- `StoneSpec` itself was not modified — this Sprint adds a wrapper, never
  a competing stone schema (restates LAW-006's stone/metal separation
  boundary is untouched; see [`520-jewelry-category-architecture.md`](520-jewelry-category-architecture.md)).
- Adding a new arrangement value requires the domain-extension RFC
  process — see
  [`../04-jewelry-domain/056-domain-extension-strategy.md`](../04-jewelry-domain/056-domain-extension-strategy.md).
