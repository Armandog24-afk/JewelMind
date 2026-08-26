---
id: JM-BIBLE-523
title: RingDefinition Model
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
  - JM-BIBLE-522
  - JM-BIBLE-524
implementation_status: current
professional_validation: not_required
normative: true
---

# RingDefinition Model

`RingDefinition` — defined in
[`backend/jewelmind/ring/models.py`](../../../backend/jewelmind/ring/models.py)
— is the composed, internal ring domain model this Sprint introduces. It
replaces treating "the solitaire" as one monolithic object with seven
named, independently classified sub-models. Every field below is real; no
field, default, or classification is invented here — it is a direct read
of `models.py`'s own docstrings and type annotations.

## Fields

| Field | Type | Classification (per `models.py` docstring) |
|---|---|---|
| `family` | `RingFamilyId` | See [`524-ring-family-model.md`](524-ring-family-model.md) |
| `sizing` | `RingSizing` | CURRENT |
| `shank` | `ShankDefinition` | CURRENT (uniform plain shank only) |
| `shoulders` | `ShoulderDefinition` | IMPLICIT/PARTIAL |
| `head` | `RingHeadDefinition` | PARTIAL |
| `stoneArrangement` | `StoneArrangementDefinition` | CURRENT (single center stone only) |
| `setting` | `SettingAttachmentDefinition` | CURRENT (prong only) |

Each sub-model has its own contract document:
[`525-ring-sizing-contract.md`](525-ring-sizing-contract.md),
[`526-shank-contract.md`](526-shank-contract.md),
[`527-shoulder-contract.md`](527-shoulder-contract.md),
[`528-head-contract.md`](528-head-contract.md),
[`529-stone-arrangement-contract.md`](529-stone-arrangement-contract.md),
[`530-setting-attachment-contract.md`](530-setting-attachment-contract.md).

All seven sub-models — including `RingDefinition` itself — extend
`RingModel`, a thin `BaseModel` subclass with `extra="forbid"`
(`ConfigDict(extra="forbid")`); an unrecognized field on any of them is a
hard validation error, matching the strictness discipline of
`domain/schema.py::StrictModel` (see
[`../05-jdl/README.md`](../05-jdl/README.md)) without literally reusing that
base class.

## `RingDefinition` is built, never hand-constructed

`RingDefinition` objects are produced exclusively by
[`ring_definition_from_jdl()`](../../../backend/jewelmind/ring/adapter.py)
— see that function's own docstring: "Every field is copied from a real
`JewelryDefinition`, never invented." No code path in `jewelmind.ring`
constructs a `RingDefinition` from literal values outside a test file.

## `ring_definition_from_jdl()` runs on every real generation — this is live code, not an unused capability

`jewelmind.ring.families.generate_ring()` — the function registered as the
`ring` category's generator in
[`jewelmind.jewelry_category.dispatch._category_generators()`](../../../backend/jewelmind/jewelry_category/dispatch.py)
— calls `ring_definition_from_jdl(definition)` as its first statement, on
every real request:

```python
def generate_ring(definition: JewelryDefinition) -> GeneratedModel:
    ring_definition_from_jdl(definition)  # validates the real RingDefinition v2 mapping on every generation
    ...
```

The built `RingDefinition` is discarded immediately after — `generate_ring()`
then dispatches geometry generation using the original `JewelryDefinition`,
not the `RingDefinition` object (see
[`532-ring-generation-contract.md`](532-ring-generation-contract.md) for why:
`build_solitaire_ring()` itself was not touched this Sprint and still reads
from the flat schema). The call exists so that every real production
generation exercises, and would fail loudly on, a `RingDefinition` mapping
that no longer validates — it is a live correctness check integrated into
the request path, not dead or merely-available code.

## What this Sprint did not change

`RingDefinition` never becomes a second source of truth for a generated
model's dimensions — geometry is still produced from the original
`JewelryDefinition` by the unchanged `build_solitaire_ring()`
(JEWELRY-ARCH-GOV-009). See [`533-solitaire-migration-model.md`](533-solitaire-migration-model.md)
for the full field-by-field JDL → `RingDefinition` mapping table.
