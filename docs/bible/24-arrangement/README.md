---
id: JM-BIBLE-ARRANGE-README
title: "Stone Arrangement Engine v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-03
source_of_truth: true
depends_on:
  - JM-BIBLE-STONEV2-README
  - JM-BIBLE-GEM-README
  - JM-BIBLE-SETTING-README
  - JM-BIBLE-ALCHEMIST-README
related_documents:
  - JM-BIBLE-700
implementation_status: partial
professional_validation: not_required
normative: true
---

# Stone Arrangement Engine v1

Sprint 22. The machine-readable half lives at
[`specs/arrangement/v1/`](../../../specs/arrangement/v1/README.md).

**Implementation status is PARTIAL, deliberately and precisely.** The
declarative layer and its compilation boundary are complete and executing;
multi-stone GEOMETRY is not. See
[`execution-boundary.md`](execution-boundary.md) for exactly where the line
falls and why it was not crossed.

## What this sprint separates

Sprint 20 separated a stone's geometry from its cut. Sprint 21 separated its gem
identity from its geometry. This sprint separates a stone's **occurrence** from
both:

| Concern | Where it lives |
| --- | --- |
| What a stone IS (shape, dimensions, source) | `StoneSpec` + `jewelmind/stone/`, `geometry/stone/` |
| What it is MADE OF | `stone.gem` + `jewelmind/gem/` |
| THIS occurrence of it | `arrangement.instances[]` + `jewelmind/arrangement/` (**this sprint**) |
| How occurrences relate | `arrangement.{groups,patterns,relations}` (**this sprint**) |
| How metal holds a stone | `jewelmind/setting/` |
| Compiled geometry | `jewelmind/geometry/` |
| Production artifacts | `jewelmind/exporters/` |

An occurrence carries no shape and no material of its own. It **references**
them, because two accents cut from one specification are two occurrences of one
stone, not two stones that happen to match.

## What the layer is not

- **Not a geometry engine.** `resolve.py` produces numbers; Atlas turns numbers
  into solids. No field holds a kernel object, and an AST test asserts that no
  module in the package even names a construction verb.
- **Not a constraint solver.** Every model resolves by direct evaluation in a
  fixed order — no iteration to convergence, no search, no solver state. A
  solver's output depends on its iteration order and starting values, which is
  exactly the determinism this layer must guarantee.
- **Not a jewelry-rule layer.** No minimum spacing, no stone-count limit, no
  accent-to-centre proportion. Each needs sourced professional evidence this
  project does not have.
- **Not category-specific.** Nothing imports a jewelry category. A future
  earring arrangement uses these models unchanged.

## Identity is by ID, never by position

Every instance, group, pattern and relation is addressed by a stable string ID.
Array order is a serialization artifact: reordering `instances` must not change
what the arrangement means, and `normalize.py` sorts canonically so it cannot.

That extends to generated members. A pattern's members get **derived** IDs
(`halo.0`, `halo.1`, …) rather than random ones, because re-resolving the same
pattern must produce the same IDs — a UUID would break determinism outright and
make a stored resolution impossible to compare with a fresh one.

The primary-instance selection follows the same rule: the lowest-ID `CENTER`
instance, never `instances[0]`. Choosing by list position would make the built
geometry depend on serialization order.

## Three separate identities

| Identity | Covers | Changes when |
| --- | --- | --- |
| `definitionHash` | the whole JDL document | anything changes |
| `geometryHash` | the document minus provably non-geometry fields | geometry-affecting fields change — **including the arrangement** |
| `arrangementFingerprint` | the arrangement's own content plus the resolver version | the arrangement changes, or the resolution arithmetic does |

The arrangement **participates in `geometryHash`**, unlike gem identity. That is
the correct call and the opposite of Sprint 21's: an arrangement will drive
geometry, so excluding it would serve stale geometry for a real design change —
worse than a slow rebuild (GEM-GOV-013's reasoning, applied in the other
direction).

`arrangementFingerprint` is separate because the same arrangement reused in two
different rings is one arrangement and two designs.

## Patterns: closed-form, not iterative

Three kinds, each a direct evaluation:

- **LINEAR** — `count` copies along a line, optionally centred on the anchor.
- **RADIAL** — `count` copies on a circle, with `startAngle`/`sweep` so a
  partial arc is first-class. A full 360° sweep steps by `sweep/count` (the last
  member would otherwise land on the first); a partial arc steps by
  `sweep/(count-1)` so both endpoints are included. One formula for both would
  either double a stone or leave an arc short of its stated end.
- **MIRROR** — one reflected copy across a principal plane, flipping a chiral
  stone's own orientation. Without that flip a reflection is only a rotation,
  and a mirrored pear points the wrong way.

A `PATH` pattern following an arbitrary curve is deliberately **not**
representable: it needs curve evaluation, which belongs to Atlas.

## Relations are declarations, not constraints

Five kinds (`MIRRORED_PAIR`, `ALIGNED_WITH`, `EVENLY_SPACED_WITH`,
`CONCENTRIC_WITH`, `SHARES_TRANSFORM_WITH`). Resolution checks that every
referenced ID exists and that each kind's arity holds, then passes them through
untouched. **Nothing moves an instance to satisfy a relation.**

Recording the relationship anyway is the point: it survives editing, so a later
grouped operation or a future setting system can act on "these two are a
mirrored pair" instead of re-deriving it from coordinates that happen to look
symmetric. Enforcement is PLANNED, and the capability registry says so.

Member order is meaningful for `MIRRORED_PAIR` (first is the original) and
canonicalized for the rest — sorting a pair would lose which stone is the
reflection.

## Validation: three kinds, kept apart

| Kind | Where | This sprint |
| --- | --- | --- |
| structural / software | `_arrangement_rules` (`JM-ARRANGE-001`…`006`) | six rules |
| geometric | Geometry Inspection | unanswerable until multi-stone geometry exists |
| professional / manufacturing | Professional Validation Framework | **unavailable** — zero records |

Whether two placed stones physically overlap is a **geometric** question, and
answering it structurally would mean inventing a spacing threshold. Two
instances at the same point is therefore not an error here.

`JM-ARRANGE-004` runs the **real resolver**, so Forge can never disagree with
what generation will do. `JM-ARRANGE-006` surfaces the execution boundary as an
`information` result rather than hiding it in a log.

## Component identity, fixed before it is needed

The primary instance keeps the historical component name `stone_reference`
exactly, which is why every Golden baseline, exporter, inspection check and
frontend consumer is unaffected. An additional instance would be
`stone_reference.<instanceId>`, and `geometry/roles.py` already recognizes that
prefix.

That last part matters more than it looks: the default role for an unknown
component name is `production_metal`, which is right for a metal part and
catastrophic for a stone — it would let an additional stone be fused into the
metal body and shipped inside a production export, breaking LAW-006 silently the
first time one was emitted. The classification is in place, and tested, before
any such geometry exists.

## Backward compatibility

`arrangement` is optional and nullable. A document without one is a single-stone
design and behaves exactly as before; `compile_arrangement(None)` returns `None`
and the assembly is unchanged. Nothing synthesizes a one-instance arrangement
for a single-stone design, because that would invent a declaration the document
never made.

`schemaVersion` stays `0.1.0`: an optional additive field is backward
compatible, the same judgment Sprint 21 made for `stone.gem`. Adding it does
change canonical JSON and therefore `definitionHash`, so the derived hash
mirrors under `specs/` were regenerated by running the real implementation —
recorded in [`SPRINT-22-VALIDATION-REPORT.md`](SPRINT-22-VALIDATION-REPORT.md).

## Governance

See [`arrangement-governance.md`](arrangement-governance.md) for the full
`ARRANGE-GOV` rules.
