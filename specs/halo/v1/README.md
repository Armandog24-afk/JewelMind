# Halo System v1 — machine-readable specification

The **structural relationship** between a centre and one or more rings of stones
surrounding it. A different question from *where any individual stone sits*
([`specs/arrangement/v1/`](../../arrangement/v1/README.md)), *what a stone is*
([`specs/stone/v2/`](../../stone/v2/README.md)), *what it is made of*
([`specs/gem/v1/`](../../gem/v1/README.md)), *what the design means as a whole*
([`specs/family/v1/`](../../family/v1/README.md)) and *how metal holds a stone*
([`specs/setting/v2/`](../../setting/v2/README.md)).

Narrative half: [`docs/bible/27-halo/`](../../../docs/bible/27-halo/README.md).

## Status: PARTIAL, precisely

All three variants — `SINGLE`, `DOUBLE`, `HIDDEN` — compose, resolve and build
**real stone geometry for every halo stone**: individually identified, placed,
scaled, oriented and (for a hidden halo) vertically offset. What is **not**
built is the **metal that holds them**: a halo design generates one setting, the
centre stone's.

That is why every registry entry is `PARTIAL` rather than `CURRENT`, and why
every test vector records `settingCoverage: "PRIMARY_ONLY"`. Nothing here may be
read as full halo support. See
[`execution-boundary.md`](../../../docs/bible/27-halo/execution-boundary.md).

## Why a halo is not a fifth family type

Sprint 24 reserved the name `halo` on the ground that "a halo is a
`CENTER_WITH_ACCENTS` whose accents sit against the centre". That holds for one
flat ring and fails for the rest of the concept:

- a **hidden** halo sits *below* the centre stone's girdle plane, and
  `CENTER_WITH_ACCENTS` has no vertical axis at all;
- a **double** halo is two concentric rings with independent counts, radii,
  start angles and scales, and one accent parameter set cannot carry two;
- a halo **composes** with a family rather than replacing it — "three-stone with
  a halo around the centre" needs both structures at once.

So a halo is a composable layer over whatever placement a design already
declares. [`halo-rfc.md`](../../../docs/bible/27-halo/halo-rfc.md) records that
supersession explicitly rather than editing around the reservation.

## What this is not

- **Not a placement engine.** A halo compiles into arrangement primitives; the
  Stone Arrangement Engine resolves them, using the same shared ring arithmetic
  (`arrangement/radial.py`) a hand-written `RADIAL` pattern uses.
- **Not a stone or gem model.** A ring references a stone specification and may
  carry a gem identity. Nothing about the stone is copied, and a halo stone need
  not share the centre's gem, shape, size or material.
- **Not a member model of its own.** Per-stone overrides reuse
  `FamilyMember` — the same seven fields, one definition.
- **Not a setting implementation.** A ring may *request* a setting by name; the
  Setting System decides what that means.
- **Not geometry.** No schema field holds a kernel object.
- **Not category-specific.** No schema here mentions a ring.
- **Not professionally validated.** No spacing, proportion or settability rule
  exists.

## Files

| File | Contents |
| --- | --- |
| `halo-definition.schema.json` | The halo: variant, rings, centre reference, label. |
| `halo-ring.schema.json` | One concentric ring of stones. |
| `halo-registry.json` | Capabilities, ring cardinality, composition support and reserved names, from live code. |
| `examples/*.json` | Real halos, and the composed arrangement each produces. |
| `test-vectors/*.json` | Behaviour recorded by running the real compiler. |

Every artifact was produced by running the real code, and
`backend/tests/test_halo.py` re-derives the registry, the composed examples and
the vectors on every test run.

## Four independent capability axes

| Axis | Question |
| --- | --- |
| `representable` | can the model express it, and does it round-trip through JDL? |
| `composable` | does the compiler add it to a real arrangement? |
| `stoneGeometry` | does Atlas build a stone solid for every halo stone? |
| `settingGeometry` | does the Setting System build metal that holds them? |

Today the first three are `true` for all three variants and the fourth is
`false` for all of them. Collapsing the last two would turn "the stones exist"
into "the halo is complete", which is precisely the overstatement the axes exist
to prevent.

## One placement authority

A halo **composes onto** the arrangement a design already has, and
`family/effective.py::effective_arrangement()` is the single point where a
family, an arrangement and a halo meet. A named `centerMemberId` is resolved
against the real compiled instances; an unresolvable centre is **refused**
(`JM-HALO-001`), never re-anchored, because a halo around the wrong stone is
worse than one that fails loudly. `centerMemberId: null` anchors on the design
origin, which is how a halo encircles a multi-stone centre.

## Identity

Ring and member ids are authoritative; array order carries no meaning.
Reordering `rings`, or a ring's `members`, produces the same composed
arrangement and the same `arrangementFingerprint`. Derived ids
(`halo.inner.0`) come from the ring's own id and the stone's position in the
ring's angular sequence, never from a counter, a UUID or a timestamp, so
re-composing reproduces them exactly.

## Forge rules

| Rule | Checks | Severity |
| --- | --- | --- |
| `JM-HALO-001` | the centre the halo names exists in this design's placement | error |
| `JM-HALO-002` | the halo composes, via the real compiler | error |
| `JM-HALO-003` | this family/halo combination is supported | error |
| `JM-HALO-004` | halo stone and setting references resolve | warning |
| `JM-HALO-005` | the halo-metal limitation | information |

None is a jewelry judgment. `test-vectors/invalid-halo-vectors.json` records
which **layer** refuses each malformed case — a schema rejection means the
document is malformed, a compiler rejection means it is well-formed and not
composable against the placement this design actually declares.
