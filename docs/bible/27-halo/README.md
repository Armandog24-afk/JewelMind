---
id: JM-BIBLE-HALO-README
title: "Halo System v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-07
source_of_truth: true
depends_on:
  - JM-BIBLE-ARRANGE-README
  - JM-BIBLE-FAMILY-README
  - JM-BIBLE-SETTINGV2-README
  - JM-BIBLE-STONEV2-README
  - JM-BIBLE-GEM-README
related_documents:
  - JM-BIBLE-900
implementation_status: partial
professional_validation: not_required
normative: true
---

# Halo System v1

Sprint 25. The machine-readable half lives at
[`specs/halo/v1/`](../../../specs/halo/v1/README.md).

**Implementation status is PARTIAL, precisely.** All three variants compose,
resolve and build **real stone geometry for every halo stone** — individually
identified, placed, scaled, oriented and (for a hidden halo) vertically offset.
What is not built is the **metal that holds them**. See
[`execution-boundary.md`](execution-boundary.md).

## What a halo is

A **structural relationship** between a centre and one or more rings of stones
surrounding it. It answers *what surrounds what*, and compiles into the
arrangement primitives that put the stones there.

A halo is not a stone (Stone System v2 owns that), not a material (Gem Identity
owns that), not a placement engine (Stone Arrangement Engine v1 owns that), not
a setting (Setting System v2 owns that) and not a design's overall semantics
(Multi-Stone Families owns that). It is a layer that **composes** with the last
two.

## Why it is not a fifth family type

Sprint 24 reserved the name `halo` in
`family/capability.py::RESERVED_FAMILY_TYPES`, on the ground that "a halo is a
`CENTER_WITH_ACCENTS` whose accents sit immediately against the centre stone".
That reasoning was correct for one flat ring and incomplete for the concept:

| Halo property | Why `CENTER_WITH_ACCENTS` cannot express it |
| --- | --- |
| A **hidden** halo sits below the centre's girdle plane | the family has no vertical axis at all |
| A **double** halo is two rings with independent counts, radii, start angles and scales | one `accentCount`/`accentRadiusMm` pair cannot carry two |
| A halo **composes** with a family | a fifth family type would force a choice between them |

[`halo-rfc.md`](halo-rfc.md) records that supersession explicitly, per
`SETTING-GOV`/`FAMILY-GOV`'s requirement of an RFC before a reserved name is
implemented — rather than editing quietly around the reservation.

## The model

```
HaloDefinition
  variant          SINGLE | DOUBLE | HIDDEN
  rings            1..2 HaloRing
  centerMemberId   an arrangement instance id, or null for the design origin
  label

HaloRing
  ringId, count, radiusMm, radiusYMm, startAngleDeg, sweepDeg,
  zOffsetMm, memberScale, alignToRadius,
  stoneRef, gem, settingRef,
  members          per-stone overrides, reusing FamilyMember
```

Nothing here restates what a stone is or what it is made of. Per-stone
overrides reuse `FamilyMember` — the same seven fields already defined for a
family member — rather than a parallel member model, and `placementOverride`
reuses the arrangement layer's own `InstanceTransform`.

## Variants

| Variant | Rings | What it is |
| --- | --- | --- |
| `SINGLE` | 1 | one ring around the centre, level with it |
| `DOUBLE` | 2 | two concentric rings, each independently parameterized |
| `HIDDEN` | 1 | one ring below the centre's girdle plane |

`HIDDEN` is a **structural** claim, enforced: its ring's `zOffsetMm` must be
negative. No minimum offset is prescribed and none could be without sourced
evidence; what is checked is only that a halo calling itself hidden is actually
below the centre plane, because a hidden halo at or above it is a `SINGLE` halo
mislabelled and the label is what every downstream consumer reads.

Reserved variants — `cushion_halo`, `floral_halo`, `compass_halo`,
`triple_halo`, `pave_halo` — live in
`halo/capability.py::RESERVED_HALO_VARIANTS` with real reasons, are refused by
the model, and are never silently substituted with a `SINGLE` halo.

## Composition

A halo is **added** to whatever placement the design declares:

| Document declares | Effective arrangement |
| --- | --- |
| a halo only | a synthesized `CENTER` instance at the origin, plus the rings |
| a family + a halo | the compiled family, plus the rings |
| an arrangement + a halo | the arrangement, plus the rings |
| a family + an arrangement | refused — `JM-FAMILY-001`, unchanged |
| nothing | `None`, exactly as before Sprint 22 |

`family/effective.py::effective_arrangement()` is the single point where all
three meet. It is no longer a family-only helper but the **design-level
placement resolution point**; every consumer already reaches it, so it was
extended rather than relocated.

### The centre is resolved, never guessed

A named `centerMemberId` is looked up by id in the arrangement being composed
onto. If it is absent, composition is **refused** (`JM-HALO-001`) rather than
re-anchored on the origin: a halo around the wrong stone is worse than a halo
that fails loudly.

`centerMemberId: null` anchors on the design origin, and that is how a halo
surrounds a **multi-stone centre** — a toi-et-moi pair straddles the origin, so
an origin-anchored ring encircles both stones rather than one of them.

### The centre a halo-only design supplies

A halo declared with no family and no arrangement synthesizes one `CENTER`
instance at the origin. That is not inventing an undeclared design: a halo with
no centre is not a halo, and this is the ordinary solitaire-plus-halo case. The
synthesized instance keeps the `CENTER` role, so `arrangement/compile.py`'s
deterministic primary selection picks it and the centre stone keeps the
historical bare `stone_reference` component name.

## One placement authority

A halo emits `StoneInstanceDef`s and `ArrangementRelation`s and nothing else.
The angular sequence comes from `arrangement/radial.py::ring_angles_deg()` —
**the same function the resolver uses to expand a `RADIAL` pattern**, shared
rather than copied, so a halo's stones sit exactly where a hand-written pattern's
would. Sprint 24's family compiler previously carried a second copy of that
arithmetic; Sprint 25 extracted the one function rather than adding a third
copy.

Rings are placed **explicitly** rather than through a `RADIAL` pattern, for the
reason Sprint 24 found the hard way: a pattern's generated members inherit their
source instance's overrides, and the only instance at a halo's centre is the
centre stone — so routing a halo through a pattern would silently discard
`memberScale` and produce full-size halo stones.

## Identity

Ring and member ids are authoritative; array order carries no meaning.
Reordering `rings`, or a ring's `members`, produces the same composed
arrangement and the same `arrangementFingerprint`. Named members are matched to
ring positions by **sorted id**, never by array order.

Derived ids are `<ringId>.<index>` — reproducible from the ring's own id and the
stone's position in the angular sequence, never a counter across rings, a UUID
or a timestamp.

A halo moves stones, so it is inside `geometryHash` as well as
`definitionHash`. `halo.label` is geometrically inert and still inside
`geometryHash`, which costs an unnecessary rebuild when a label changes; the
alternative error mode is a stale-geometry cache hit, which ARRANGE-GOV-007
calls the worse one. `family.label` behaves identically.

## Validation

Five structural rules, all `HALO_ONLY`:
`JM-HALO-001` (the centre resolves), `JM-HALO-002` (the halo composes, through
the real compiler), `JM-HALO-003` (the family/halo combination is supported),
`JM-HALO-004` (references resolve, warning), `JM-HALO-005` (the metal-coverage
report, information).

None is a jewelry judgment. There is deliberately no rule about minimum halo
stone spacing, a centre-to-halo proportion, a settable radius, or whether a
hidden halo clears the centre stone's pavilion — each needs sourced professional
evidence this project does not have. Whether two placed stones physically
overlap is a **geometric** fact for Geometry Inspection.

## Backward compatibility

`halo` is optional and nullable. A document without one behaves exactly as
before; `compose_halo(base, None)` returns `base` — the same object — and
nothing synthesizes a halo for a solitaire. `schemaVersion` stays `0.1.0`: the
same MINOR judgment Sprints 21–24 made.

The default solitaire's metal volume is unchanged and all 44 pre-existing Golden
baselines hold with no update. Five new cases (`HALO-001`–`HALO-005`) cover the
newly executable scope, bringing the suite to 49.

## Governance

See [`halo-governance.md`](halo-governance.md) for the full `HALO-GOV` rules and
[`halo-rfc.md`](halo-rfc.md) for the reserved-name supersession.
