---
id: JM-BIBLE-527
title: Shoulder Contract
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
  - JM-BIBLE-043
implementation_status: current
professional_validation: not_required
normative: true
---

# Shoulder Contract

## The real current state

`ShoulderDefinition`
(`backend/jewelmind/ring/models.py`) has exactly one field:

```python
class ShoulderDefinition(RingModel):
    modeled: Literal[False] = False
```

[`ring_definition_from_jdl()`](../../../backend/jewelmind/ring/adapter.py)
always constructs it with `ShoulderDefinition()` — no data from the real
JDL flows into it, because no shoulder-related field exists anywhere in
`domain/schema.py`.

Status, per `models.py`'s own docstring: **IMPLICIT/PARTIAL.** The current
solitaire has no independently modeled shoulder geometry — the shank
flows directly into the head with no distinct transition component in the
real geometry builders (`geometry/components/`, unchanged this Sprint).
See [`../04-jewelry-domain/043-ring-anatomy.md`](../04-jewelry-domain/043-ring-anatomy.md)
for the anatomical definition of "shoulder" this document assumes but does
not restate.

## Why this contract exists at all

`ShoulderDefinition` exists so a future sprint has a real, named place to
attach real shoulder geometry — not because current geometry has a
shoulder to describe. Giving the concept a stable model name now, even
while it carries no data, lets a later sprint add fields to
`ShoulderDefinition` without inventing a new top-level slot on
`RingDefinition` or renegotiating where "shoulder" belongs in the
composition.

## What this Sprint explicitly did not do

**No shoulder geometry was invented to satisfy this contract.** No new
`geometry/components/` module, no new solid, no new bounding box, and no
new field on `domain/schema.py` was added anywhere in this Sprint to give
`ShoulderDefinition` something to describe. `modeled: Literal[False]` is
the honest, load-bearing statement of that: it is a type-level guarantee
that no code path can construct a `ShoulderDefinition` claiming shoulder
geometry exists, since `True` is not a legal value for the field today.

This mirrors the Bible's standing discipline against marking PLANNED
functionality as CURRENT (see
[`../00-foundation/000-bible-governance.md`](../00-foundation/000-bible-governance.md)):
rather than a docstring claiming "shoulders: PLANNED" while quietly having
no contract to plan against, the contract exists and is honestly empty.
