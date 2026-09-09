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

> **Superseded in part by Sprint 28.** This document described a contract
> that was honestly empty, and Sprint 28 filled it: `geometry/shoulder.py`
> builds real shoulder arches. The original statement is kept below as what
> was true from Sprint 16 to Sprint 27, with the change recorded at the end —
> the Bible's rule is to report a contradiction, never to rewrite a document
> into having always said the current thing. See
> [`../30-ring-families/README.md`](../30-ring-families/README.md).

`ShoulderDefinition` (`backend/jewelmind/ring/models.py`) had exactly one
field, from Sprint 16 until Sprint 28:

```python
class ShoulderDefinition(RingModel):
    modeled: Literal[False] = False
```

It now carries two, and `modeled` is a real `bool`:

```python
class ShoulderDefinition(RingModel):
    modeled: bool = False
    architecture: Literal["NONE", "CATHEDRAL", "SPLIT_RAILS"] = "NONE"
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

## What Sprint 28 changed

The contract is no longer empty, and the `Literal[False]` had to go **because
it became a false claim**, not because it was inconvenient.

`geometry/shoulder.py` builds real arches: two for `SOLITAIRE_CATHEDRAL`, four
for a split shank (one per rail per side). Each is a ruled loft between two real
sections — the base is the band's OWN profile wire from `shank/profile.py`, so a
shoulder can never disagree with the band about its cross-section — and the pair
is fused into one connected `shoulders` component.

**`modeled` is still `False` for most designs, and that is the honest answer
rather than a gap.** A classic solitaire has no shoulder component, and
reporting one would describe geometry that is not there. `architecture` names
which builder produced it, or `NONE`.

**It is read from the RESOLVED ring family, not inferred from `jewelry.style`**
(`ring/adapter.py::_shoulders_from_jdl()`), because the architecture belongs to
the VARIANT: a classic solitaire has no shoulders and a cathedral one has two
arches, and both are `solitaire`. Reading the resolver is what keeps this
contract from disagreeing with the component the assembly actually built.

The prediction this document made — that a later sprint could add fields to
`ShoulderDefinition` without renegotiating where "shoulder" belongs in the
composition — held exactly as written.
