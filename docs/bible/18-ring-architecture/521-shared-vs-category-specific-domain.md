---
id: JM-BIBLE-521
title: Shared vs. Category-Specific Domain
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
  - JM-BIBLE-040
  - JM-BIBLE-052
implementation_status: current
professional_validation: not_required
normative: true
---

# Shared vs. Category-Specific Domain

This is the field-by-field audit that `backend/jewelmind/jewelry_category/forge_scope.py`'s
scope classification and `backend/jewelmind/ring/models.py`'s field ownership were
both designed from. It classifies every real top-level field currently defined on
[`domain/schema.py::JewelryDefinition`](../../../backend/jewelmind/domain/schema.py)
(unchanged this Sprint — see [`520-jewelry-category-architecture.md`](520-jewelry-category-architecture.md),
JEWELRY-ARCH-GOV-008) into one of three buckets.

**A field's classification is a design judgment about whether its *semantics*
generalize across jewelry categories, not a guess.** "Reusable" does not mean
"universal" — several fields below are deliberately kept RING-SPECIFIC even
though a naive reading might make them look shared, because forcing reuse
where the meaning genuinely differs across categories would be worse than
duplicating a field name later (JEWELRY-ARCH-GOV-004).

## Classification buckets

- **SHARED** — the field's meaning does not depend on which jewelry category
  it belongs to. Consumed as-is by Ring (JEWELRY-ARCH-GOV-007); never
  re-implemented inside `jewelmind.ring`.
- **RING-SPECIFIC** — the field's meaning is inseparable from "this is a
  ring." A future non-ring category would need its own field, never a
  reuse of this one (JEWELRY-ARCH-GOV-004).
- **POTENTIALLY-SHARED-BUT-CONTEXTUAL** — the underlying concept could
  generalize (a prong setting is not conceptually ring-only), but only one
  instance of it exists in real code today, and *how* it structurally
  integrates into a ring is itself ring-specific (JEWELRY-ARCH-GOV-005).
  Do not read this bucket as "already generalized" — it is "plausible to
  generalize later, not attempted this Sprint."

## The audit

| JDL field group | Real fields | Classification | Where it lives in `RingDefinition` v2 | Forge scope ([`forge_scope.py`](../../../backend/jewelmind/jewelry_category/forge_scope.py)) |
|---|---|---|---|---|
| `project` | `project.name`, `project.units` | SHARED (metadata) | Not part of `RingDefinition` — never consumed by Ring Architecture at all | n/a — no `JM-*` rule prefix covers project metadata |
| `jewelry` | `jewelry.category`, `jewelry.style` | Platform-level category/family identity (its own bucket — see note below) | `RingDefinition.family` (from `jewelry.style`); `jewelry.category` is consumed one level up, by `jewelmind.jewelry_category.dispatch` | n/a |
| `ring` | `ring.sizeSystem`, `ring.size`, `ring.innerDiameter` | RING-SPECIFIC | `RingSizing` — see [`525-ring-sizing-contract.md`](525-ring-sizing-contract.md) | `ring_sizing` (`JM-RING-*`) |
| `band` | `band.width`, `band.thickness`, `band.profile` | RING-SPECIFIC | `ShankDefinition` — see [`526-shank-contract.md`](526-shank-contract.md) | `ring_shank` (`JM-BAND-*`) |
| `stone` | `stone.shape`, `stone.diameter`, `stone.depth` | SHARED (wrapped, never duplicated) | `StoneArrangementDefinition.stone`, via `.model_copy()` of the real `StoneSpec` — see [`529-stone-arrangement-contract.md`](529-stone-arrangement-contract.md) | `shared_stone` (`JM-STONE-*`) |
| `setting.type` / `.prongCount` / `.prongDiameter` / `.prongHeight` | The setting instance itself | POTENTIALLY-SHARED-BUT-CONTEXTUAL | `SettingAttachmentDefinition` — see [`530-setting-attachment-contract.md`](530-setting-attachment-contract.md) | `shared_setting` (`JM-PRONG-*`) |
| `setting.basketHeight` | The setting's structural attachment into the ring | RING-SPECIFIC | `RingHeadDefinition.basketHeightMm` — see [`528-head-contract.md`](528-head-contract.md) | `ring_head` (`JM-SETTING-*`) |
| `material` | `material.metal` | SHARED | Not part of `RingDefinition` — consumed as-is (JEWELRY-ARCH-GOV-007) | n/a |
| `manufacturing` | `manufacturing.method` | SHARED | Not part of `RingDefinition` | `shared_manufacturing` (`JM-MANUFACTURING-*`) |
| `preview` | `preview.meshTolerance`, `preview.angularTolerance` | SHARED | Not part of `RingDefinition` | n/a |

`forge_scope.py` additionally classifies `JM-GEOMETRY-*` rules as `engineering`
— a shared-scope bucket for kernel/geometric constraints that are not
jewelry-domain rules at all (see
[`jewelmind.jewelry_category.forge_scope.is_shared_scope()`](../../../backend/jewelmind/jewelry_category/forge_scope.py)).
An unrecognized rule-ID prefix classifies as `"unknown"`, never a crash —
verified by `test_an_unrecognized_rule_id_prefix_is_unknown_not_a_crash` in
[`backend/tests/test_ring_architecture.py`](../../../backend/tests/test_ring_architecture.py).

## Why `setting` splits across two buckets

`SettingSpec` (one real JDL object) supplies fields to two different
`RingDefinition` sub-models because the setting-*instance* and its
*ring-structural attachment* are different concerns (JEWELRY-ARCH-GOV-005):
the prong count/diameter/height describe the setting itself and could
plausibly serve a future pendant or earring; `basketHeight` describes how
that setting connects into *this specific ring's* structure and has no
category-neutral meaning. See [`528-head-contract.md`](528-head-contract.md)
for the full boundary statement.

## Why `jewelry.category`/`jewelry.style` are neither SHARED nor RING-SPECIFIC

They are not jewelry *domain* data at all — they are the platform's category
and family identifiers, consumed by
`jewelmind.jewelry_category.dispatch`/`jewelmind.ring.families` to decide
*which* domain model applies. Treating them as SHARED domain fields would
misstate their role; treating them as RING-SPECIFIC would misstate that a
future `earring.style` will be an entirely separate field, not a reuse of
`jewelry.style`'s enum (JEWELRY-ARCH-GOV-004).

## What this Sprint did not do

This audit does not introduce a new schema, a new validation layer, or a
new field anywhere. `domain/schema.py` is unchanged (JEWELRY-ARCH-GOV-008).
The classification above is a read of existing fields, used to justify the
already-built `jewelmind.ring.models` field ownership and
`jewelmind.jewelry_category.forge_scope` rule classification — not the
other way around.

For the authoritative description of each shared concept's own domain
semantics (not restated here), see
[`../04-jewelry-domain/046-stone-domain.md`](../04-jewelry-domain/046-stone-domain.md),
[`../04-jewelry-domain/047-setting-domain.md`](../04-jewelry-domain/047-setting-domain.md),
[`../04-jewelry-domain/050-material-domain.md`](../04-jewelry-domain/050-material-domain.md), and
[`../04-jewelry-domain/051-manufacturing-context.md`](../04-jewelry-domain/051-manufacturing-context.md).
