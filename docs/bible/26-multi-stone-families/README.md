---
id: JM-BIBLE-FAMILY-README
title: "Multi-Stone Families v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-04
source_of_truth: true
depends_on:
  - JM-BIBLE-ARRANGE-README
  - JM-BIBLE-SETTINGV2-README
  - JM-BIBLE-STONEV2-README
  - JM-BIBLE-GEM-README
related_documents:
  - JM-BIBLE-900
implementation_status: partial
professional_validation: not_required
normative: true
---

# Multi-Stone Families v1

Sprint 24. The machine-readable half lives at
[`specs/family/v1/`](../../../specs/family/v1/README.md).

**Implementation status is PARTIAL, precisely.** Every family compiles, resolves
and builds **real stone geometry for every member**. What is not built is a
**setting** for a non-primary member. See
[`execution-boundary.md`](execution-boundary.md).

## What a family is

The semantic structure of a multi-stone design: that this *is* a three-stone
ring rather than a design that happens to contain three stones, which member is
the centre, and that the sides are meant to be a mirrored pair.

| Layer | Owns |
| --- | --- |
| Stone System | what a stone *is* — shape, dimensions, source |
| Gem System | what it is *made of* |
| **Family** (this sprint) | which stones participate, in what **roles**, with what **intent** |
| Arrangement | **where** every stone sits |
| Setting System | how metal **holds** a stone |
| Atlas | the solids |

A family holds none of the others' data. A member **references** a stone
specification and may carry a `GemIdentity`; three stones of different cuts is
three references, not three copies.

## Why a layer above the arrangement

An arrangement can already express three stones in a row — but not that the row
*is* a three-stone design, which side is which, or that widening it should move
both sides together. Without those facts every consumer would re-infer intent
from coordinates. A family records the intent once.

## Compilation: the arrangement stays the authority

A family **compiles into** an `ArrangementDefinition`. It never computes a final
position of its own:

```
family semantics → arrangement primitives → resolver → placements → Atlas
```

A symmetric three-stone emits one side instance plus a `MIRROR` pattern, so the
mirroring is performed by the same engine that mirrors anything else — a family
therefore *cannot* disagree with an arrangement about where a mirrored stone
goes.

`family/effective.py` is the single point where a family and an explicit
arrangement meet. **Declaring both is refused** (`JM-FAMILY-001`), never merged:
two authorities over one set of placements has no determinate resolution.

## The four families

- **THREE_STONE** — a centre with two flanking stones. Symmetric compiles to a
  mirror; asymmetric places both sides explicitly.
- **TOI_ET_MOI** — two stones as a deliberate pair, straddling the design axis
  along a settable angle. Symmetric means a **point reflection** through the
  centre with the second stone's orientation flipped, so the two face each
  other.
- **CLUSTER** — stones around an optional centre. Not necessarily circular
  (`radiusYMm` makes it elliptical), not necessarily a full circle
  (`sweepDeg`), and not necessarily centred (`includeCenter`).
- **CENTER_WITH_ACCENTS** — the least specialized family, so a design that is
  neither a strict three-stone nor a cluster still has a semantic home instead
  of forcing one of the others to stretch.

A **halo** is deliberately *not* a fifth type: it is a `CENTER_WITH_ACCENTS`
whose accents sit against the centre, and a separate type would create two ways
to say one thing that would eventually compile differently. See
`RESERVED_FAMILY_TYPES` for `pave`, `eternity`, `bypass` and `channel_row`, each
with its real reason.

## Mixed stones, mixed shapes

A member may carry its own gem, its own scale and its own orientation, and all
three reach geometry. Nothing about the stone or the gem is duplicated — the
references do the work, so a later edit to the stone follows through to every
member that inherits it.

## Identity

Member ids are authoritative; array order is a serialization artifact.
Reordering `members` produces the same compiled arrangement and the same
`arrangementFingerprint`. Derived member ids (`accent.0`, `side.left`) come from
the family's own structure, never from a counter or a UUID, so re-compiling the
same family reproduces them exactly.

Three identities stay distinct, as before: `definitionHash` (the whole
document), `geometryHash` (which **includes** the family, because a family
drives geometry), and `arrangementFingerprint` (the compiled arrangement's own
content).

## Geometry

`geometry/stone/instance.py` applies each resolved instance's transform, scale
and orientation to the built stone. The stone is built **once** and placed many
times — two occurrences of one stone must not differ in their last bits, and
rebuilding would repeat identical kernel work.

Order is fixed: scale about the stone's own centre, rotate about its own
vertical axis, then translate. Scaling about the global origin would drop a
stone sitting above the band; rotating about the design axis would swing it
around the ring instead of spinning it in place.

An instance at the origin with no scale and no rotation returns the builder's
own shape **object**, so single-stone geometry is provably untouched rather than
merely equal.

## Component identity and inspection

The primary instance keeps `stone_reference`; every other gets
`stone_reference.<instanceId>` — the naming contract Sprint 22 fixed before any
such geometry existed. `geometry/roles.py` already classified that prefix, so an
additional stone was never at risk of being treated as production metal.

Geometry Inspection now derives its stone set from the role map, **requires**
every stone component, and evaluates stone/metal separation across all of them.
A stone-to-stone overlap is reported as a pairwise geometric fact, not as a
separation failure — two stones overlapping says nothing about whether a stone
became metal.

## Validation

Five structural rules, `JM-FAMILY-001`…`005`: one authority, valid roles,
correct cardinality, resolvable references, and an honest report of what a
compiled family does not get.

None is a jewelry judgment. There is no rule about centre-to-accent proportion,
minimum spacing, or whether a cluster could be set — each needs sourced
professional evidence this project does not have. Whether two placed stones
overlap is a **geometric** question, answered by Inspection and interpreted by
nobody.

`JM-FAMILY-003` runs the **real compiler**, so Forge can never disagree with
what generation does.

## Backward compatibility

`family` is optional and nullable. A document without one behaves exactly as
before; `compile_family(None)` returns `None` and nothing synthesizes a
solitaire family. `schemaVersion` stays `0.1.0` — the same MINOR judgment
Sprints 21–23 made.

The default solitaire's metal volume is unchanged and all 39 pre-existing Golden
baselines hold with no update. Five new cases (`FAM-001`–`FAM-005`) cover the
newly executable scope, bringing the suite to 44.

## Governance

See [`family-governance.md`](family-governance.md) for the full `FAMILY-GOV`
rules.
