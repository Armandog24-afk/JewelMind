---
id: JM-BIBLE-HALO-RFC
title: "RFC: implementing the reserved `halo` name as a composable structure"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-07
source_of_truth: true
depends_on:
  - JM-BIBLE-HALO-README
  - JM-BIBLE-FAMILY-README
related_documents:
  - JM-BIBLE-ARRANGE-README
implementation_status: current
professional_validation: not_required
normative: true
---

# RFC: implementing the reserved `halo` name as a composable structure

## Why this document exists

`docs/bible/04-jewelry-domain/056-domain-extension-strategy.md` requires an RFC
before a reserved name is implemented, and Sprint 24 reserved `halo` with a
stated reason. The Bible's fundamental rule forbids silently changing the
meaning of the product to make a contradiction disappear, so the reservation is
**superseded here on the record** rather than edited around.

## What Sprint 24 said

`family/capability.py::RESERVED_FAMILY_TYPES["halo"]`:

> A halo is a `CENTER_WITH_ACCENTS` whose accents sit immediately against the
> centre stone. It is already expressible, so adding a separate type would
> create two ways to say one thing — and the two would eventually compile
> differently.

That reasoning was **correct on its own terms** and remains correct: adding
`HALO` as a fifth `FamilyType` would indeed create two ways to say one thing.
This RFC does not overturn it. It observes that the conclusion the reservation
drew — that a halo therefore needs no first-class representation — does not
follow, because the concept is larger than the case the reservation considered.

## What the reservation did not cover

| Halo property | Expressible as `CENTER_WITH_ACCENTS`? |
| --- | --- |
| one flat ring of accents around a centre | **yes** — the reservation is right about this |
| a **hidden** halo, below the centre's girdle plane | **no.** The family model has no vertical axis; `InstanceTransform.zMm` exists at the arrangement layer, and no family parameter reaches it. A hidden halo approximated as a flat accent ring places every stone visibly wrong. |
| a **double** halo | **no.** Two concentric rings need two independent counts, radii, start angles and scales. One `accentCount`/`accentRadiusMm`/`accentScale` triple cannot carry two, and a document would have to choose which ring to describe. |
| **three-stone with a halo around the centre** | **no.** A family is the design's semantics, and a design has one. A fifth family type would force a choice between "this is a three-stone ring" and "this is a halo ring" when it is both. |

The third row is the decisive one. It is not a gap in the family model's
parameters; it is a statement that a halo is a **different kind of thing** from a
family — an orthogonal structure, not an alternative one.

## The decision

Implement a halo as a **composable structure** beside `family` and
`arrangement`, not as a family type:

- `JewelryDefinition.halo: HaloDefinition | None`, optional and nullable.
- `HaloDefinition` compiles into arrangement primitives and is **composed onto**
  whatever placement the design declares.
- `FamilyType` gains **no** new member, so the reservation's own concern — two
  ways to say one thing — is honoured, not violated: there is still exactly one
  way to declare a halo.
- `RESERVED_FAMILY_TYPES["halo"]` is **removed**, because the name is no longer
  reserved-as-a-family; the capability registry's `ring_family|halo` row becomes
  `OUT_OF_SCOPE` with the reason stated, rather than being deleted.

A designer who wants exactly what the reservation described — accents sitting
against the centre — can still express it as `CENTER_WITH_ACCENTS`. That is not
a duplicate representation of a halo; it is a centre-with-accents design that
happens to look like one, and the two carry different semantics on purpose.

## What is NOT decided here

- **No halo setting metal.** The metal that holds a halo — a shared bezel rail,
  a row of shared prongs, cut-down bead setting — remains PLANNED. `SETTING-GOV`
  requires its own RFC, which this sprint deliberately does not pre-empt: each
  candidate strategy is real setter geometry with real professional
  consequences, and choosing one without evidence would be inventing setter
  geometry. See [`execution-boundary.md`](execution-boundary.md).
- **No outline-following halo.** A halo hugging a cushion or emerald outline
  needs an outline-offset walk that does not exist. An ellipse is offered and is
  honestly an ellipse.
- **No professional halo rule.** No spacing minimum, no centre-to-halo
  proportion, no settability judgment.
- **No Designer halo language.** Designer proposes flat scalar JDL paths only;
  neither `family` nor `halo` is in its allow-list, and adding halo alone would
  advertise a capability families do not have.

## Consequences accepted

1. `family/effective.py::effective_arrangement()` becomes the **design-level**
   placement resolution point rather than a family-only helper, and imports
   `jewelmind.halo.compile`. The family core (`models.py`, `compile.py`) stays
   halo-free; `effective.py` was already the sanctioned edge module that meets
   `JewelryDefinition`, so it was extended rather than relocated — relocating it
   would churn every consumer for no functional gain.
2. `jewelmind.halo` depends on `jewelmind.family` for `FamilyMember`. That
   direction is deliberate: the halo REUSES the family's member model rather
   than declaring a parallel one. No module-level cycle exists, and
   `test_halo.py` asserts the halo package imports no category, geometry module
   or kernel.
3. Every pre-Sprint-25 `definitionHash` changes, because `halo` is an additive
   field in canonical JSON. Every derived mirror was regenerated by running the
   real implementation, exactly as Sprints 21–24 did.
