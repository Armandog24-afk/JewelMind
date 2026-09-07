# Multi-Stone Families v1 — machine-readable specification

The **semantic structure** of a multi-stone design: which stones participate,
in what roles, with what intent. A different question from *where they sit*
([`specs/arrangement/v1/`](../../arrangement/v1/README.md)), *what a stone is*
([`specs/stone/v2/`](../../stone/v2/README.md)), *what it is made of*
([`specs/gem/v1/`](../../gem/v1/README.md)) and *how metal holds it*
([`specs/setting/v2/`](../../setting/v2/README.md)).

Narrative half: [`docs/bible/26-multi-stone-families/`](../../../docs/bible/26-multi-stone-families/README.md).

## Status: PARTIAL, precisely

All four families compile, resolve and build **real stone geometry for every
member** — placed, scaled and oriented. What is **not** built is a **setting**
for a non-primary member: a three-stone design builds three stones and one
setting.

That is why every registry entry is `PARTIAL` rather than `CURRENT`, and why
every test vector records `settingCoverage: "PRIMARY_ONLY"`. Nothing here may be
read as full multi-stone support. See
[`execution-boundary.md`](../../../docs/bible/26-multi-stone-families/execution-boundary.md).

## What this is not

- **Not a placement engine.** A family compiles into arrangement primitives; the
  Stone Arrangement Engine resolves them. There is no second placement path.
- **Not a stone or gem model.** A member references a specification and may
  carry a gem identity. Nothing about the stone is copied.
- **Not a setting implementation.** A member may *request* a setting by name;
  the Setting System decides what that means.
- **Not geometry.** No schema field holds a kernel object.
- **Not category-specific.** No schema here mentions a ring.
- **Not professionally validated.** No proportion, spacing or settability rule
  exists.

## Files

| File | Contents |
| --- | --- |
| `family-definition.schema.json` | The family: type, parameters, members, label. |
| `family-member.schema.json` | One participating stone, by role. |
| `three-stone-params.schema.json` | Centre plus two flanking stones. |
| `toi-et-moi-params.schema.json` | Two stones as a deliberate pair. |
| `cluster-params.schema.json` | Stones around an optional centre; circular or elliptical, full or arc. |
| `center-with-accents-params.schema.json` | The general centre-plus-accents family. |
| `family-registry.json` | Capabilities, role rules and reserved names, from live code. |
| `examples/*.json` | Real families, and the compiled arrangement each produces. |
| `test-vectors/*.json` | Behaviour recorded by running the real compiler. |

Every artifact was produced by running the real code, and
`backend/tests/test_multi_stone_families.py` re-derives the registry, the
resolved examples and the vectors on every test run.

## Four independent capability axes

| Axis | Question |
| --- | --- |
| `representable` | can the model express it, and does it round-trip through JDL? |
| `compilable` | does the compiler turn it into a real arrangement? |
| `stoneGeometry` | does Atlas build a stone solid for every member? |
| `settingGeometry` | does the Setting System build a setting for every member? |

Today the first three are `true` for all four families and the fourth is `false`
for all of them. Collapsing the last two would turn "the stones exist" into
"the design is complete", which is precisely the overstatement the axes exist to
prevent.

## One placement authority

A family **compiles into** an arrangement. Declaring both `family` and
`arrangement` in one document is **refused** (`JM-FAMILY-001`), never merged:
two authorities over one set of placements has no determinate resolution.

## Identity

Member ids are authoritative; array order carries no meaning. Reordering
`members` produces the same compiled arrangement and the same
`arrangementFingerprint`. Derived ids (`side.left`, `accent.0`) come from the
family's structure, never from a counter or a UUID, so re-compiling reproduces
them exactly.

## Forge rules

| Rule | Checks | Severity |
| --- | --- | --- |
| `JM-FAMILY-001` | a family and an arrangement are not both declared | error |
| `JM-FAMILY-002` | every member's role is accepted, with the right cardinality | error |
| `JM-FAMILY-003` | the family compiles, via the real compiler | error |
| `JM-FAMILY-004` | member stone and setting references resolve | warning |
| `JM-FAMILY-005` | the setting-coverage limitation | information |

None is a jewelry judgment. `test-vectors/invalid-family-vectors.json` records
which **layer** refuses each malformed case — a schema rejection means the
document is malformed, a compiler rejection means it is well-formed and not the
family it claims to be.
