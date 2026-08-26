---
id: JM-BIBLE-522
title: Ring Architecture Overview
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
  - JM-BIBLE-523
implementation_status: current
professional_validation: not_required
normative: false
---

# Ring Architecture Overview

The target conceptual structure this Sprint establishes, and — critically —
an explicit statement of which layer of that structure is real code today
and which is documentation-only aspiration. Conflating the two is exactly
the mistake this Bible's governance discipline exists to prevent (see
[`docs/bible/00-foundation/000-bible-governance.md`](../00-foundation/000-bible-governance.md)).

## The conceptual structure

```
JewelryDefinition
  -> jewelry.category                (ring: CURRENT; earring/pendant/bracelet/necklace/charm: PLANNED)
    -> RingDefinition v2             (composed, built by ring_definition_from_jdl())
      -> RingSizing                  (CURRENT)
      -> ShankDefinition             (CURRENT — uniform plain shank only)
      -> ShoulderDefinition          (IMPLICIT/PARTIAL — no independent geometry)
      -> RingHeadDefinition          (PARTIAL — basket height only)
      -> StoneArrangementDefinition  (CURRENT — SINGLE_CENTER only)
      -> SettingAttachmentDefinition (CURRENT — prong only)
      -> Decoration                  (NOT MODELED — no field exists anywhere for this)
    -> RingFamily                    (solitaire: CURRENT; 7 reserved families: PLANNED)
```

A future non-ring category — `EarringDefinition`, `PendantDefinition`,
`BraceletDefinition`, `NecklaceDefinition`, `CharmDefinition` — would sit
beside `RingDefinition` at the same conceptual level, dispatched through
the same generic boundary. **None of these five are implemented this
Sprint.** No Pydantic model, no JDL field, no test fixture beyond the
single test-only `DummyPendantDefinition` in
[`backend/tests/test_jewelry_category_extension.py`](../../../backend/tests/test_jewelry_category_extension.py)
exists for any of them (JEWELRY-ARCH-GOV-011).

## What is real code today

| Layer | Real? | Where |
|---|---|---|
| `jewelmind.jewelry_category` package (capability registry, generic dispatch, Forge-scope classification) | Yes | [`backend/jewelmind/jewelry_category/`](../../../backend/jewelmind/jewelry_category/) |
| `RingDefinition` v2 and its six sub-models | Yes | [`backend/jewelmind/ring/models.py`](../../../backend/jewelmind/ring/models.py) |
| `ring_definition_from_jdl()` — the JDL → `RingDefinition` adapter | Yes, called on every real generation | [`backend/jewelmind/ring/adapter.py`](../../../backend/jewelmind/ring/adapter.py), invoked from `jewelmind.ring.families.generate_ring()` |
| `ModelService.generate()` dispatching through `generate_jewelry()` instead of calling `build_solitaire_ring()` directly | Yes | [`backend/jewelmind/services/model_service.py`](../../../backend/jewelmind/services/model_service.py) |
| Ring family dispatch (`solitaire` registered, 7 reserved names recognized but unregistered) | Yes | [`backend/jewelmind/ring/families.py`](../../../backend/jewelmind/ring/families.py) |
| A `JewelryDefinition.categoryDefinition` polymorphic field | **No** | Does not exist. `domain/schema.py::JewelryDefinition` is unchanged — it still has flat top-level `ring`/`band`/`stone`/`setting` fields, exactly as before this Sprint |
| `EarringDefinition`/`PendantDefinition`/`BraceletDefinition`/`NecklaceDefinition`/`CharmDefinition` | **No** | Not implemented; only recognized as `status: "planned"` entries in [`jewelmind.jewelry_category.registry.CATEGORY_CAPABILITIES`](../../../backend/jewelmind/jewelry_category/registry.py) |
| Shoulder or decoration geometry | **No** | No geometry component exists for either; see [`527-shoulder-contract.md`](527-shoulder-contract.md) |

## The gap, stated plainly

The JDL schema was never restructured into a `category` + `categoryDefinition`
polymorphic shape. `RingDefinition` v2 is an **internal, derived model**
built fresh from the real flat `JewelryDefinition` on every generation
(JEWELRY-ARCH-GOV-008) — it is not what the API accepts, not what is
persisted, and not a second canonical schema
(see [`../05-jdl/README.md`](../05-jdl/README.md) — JDL's own canonical-JSON
authority is unaffected by this Sprint). The diagram's top two levels
(`JewelryDefinition -> jewelry.category -> RingDefinition`) describe a real
data flow through code; the sibling `EarringDefinition`/etc. boxes describe
only a registered *capability placeholder*, not a schema or a model.

## How this differs from the solitaire-only implementation it replaces

Before this Sprint, `ModelService.generate()` called
`build_solitaire_ring(definition)` directly. Now it calls
`jewelmind.jewelry_category.dispatch.generate_jewelry(definition)`, which
reads `definition.jewelry.category`, looks up the `ring` generator, and
that generator (`jewelmind.ring.families.generate_ring()`) still calls the
same unmodified `build_solitaire_ring()` — see
[`532-ring-generation-contract.md`](532-ring-generation-contract.md) for the
full generation-time sequence. The change is an added dispatch/adapter
layer around unchanged geometry, never a geometry change
(JEWELRY-ARCH-GOV-009).

Read [`523-ring-definition-model.md`](523-ring-definition-model.md) next for
the field-by-field definition of `RingDefinition` v2 itself.
