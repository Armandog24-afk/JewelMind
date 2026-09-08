# Pavé & Microsetting Engine v1 — machine-readable specification

The **rule for populating a surface**: which region of which host, at what
pitch, in what pattern, held how. A different question from *where any
individual stone sits*
([`specs/arrangement/v1/`](../../arrangement/v1/README.md)), *what a stone is*
([`specs/stone/v2/`](../../stone/v2/README.md)), *what it is made of*
([`specs/gem/v1/`](../../gem/v1/README.md)), *what the design means as a whole*
([`specs/family/v1/`](../../family/v1/README.md)), *what surrounds the centre*
([`specs/halo/v1/`](../../halo/v1/README.md)) and *how metal holds one stone*
([`specs/setting/v2/`](../../setting/v2/README.md)).

Narrative half: [`docs/bible/28-pave/`](../../../docs/bible/28-pave/README.md).

## Status: PARTIAL, precisely

Both field kinds compile, resolve and build **real stone geometry AND real
retention metal** — beads, shared beads or micro-prongs fused into the host,
plus an optional recess cut out of it.

**This is the first sprint in the programme where `settingGeometry` is `true`.**
Sprints 24 and 25 built stones with no metal holding them and said so; a pavé's
own retention is real. What is PARTIAL is the *scope*: two host surfaces resolve
out of seven named, and one field per design. See
[`execution-boundary.md`](../../../docs/bible/28-pave/execution-boundary.md).

## Two first-class models

| | `PaveSpec` | `MicrosettingSpec` |
| --- | --- | --- |
| Stated | an **area** and a **density** | a **structure** |
| Derived | the stone count | the area covered |

Two models rather than one with a flag, because the inputs are genuinely
different. They share the lattice primitives — pattern, row offset,
termination, symmetry, host, retention, seat — because they are two ways of
describing one lattice.

## What this is not

- **Not a placement engine.** A field compiles into arrangement primitives; the
  Stone Arrangement Engine resolves them.
- **Not a stone or gem model.** A field references a stone specification and may
  carry a gem identity. Nothing about the stone is copied.
- **Not a setting implementation.** Retention is named here and BUILT by the
  Setting System (`setting/retention.py`).
- **Not geometry.** No schema field holds a kernel object.
- **Not category-specific.** No schema here mentions a ring; a host surface is
  named abstractly and resolved to numbers by the category adapter.
- **Not professionally validated.** No spacing, bead size, density or seat depth
  has been reviewed.

## Files

| File | Contents |
| --- | --- |
| `pave-definition.schema.json` | The field: kind, host, spec, stone, retention, seat, containment. |
| `pave-spec.schema.json` | Surface population: an area at a density. |
| `microsetting-spec.schema.json` | A stated retention topology. |
| `pave-retention.schema.json` | How metal holds the stones. |
| `pave-seat.schema.json` | Whether the host is recessed. |
| `resolved-host-surface.schema.json` | Everything the pavé layer knows about a surface, as numbers. |
| `pave-registry.json` | Capabilities, patterns and reserved names, from live code. |
| `examples/*.json` | Real fields, and the compiled field each produces. |
| `test-vectors/*.json` | Behaviour recorded by running the real compiler. |

Every artifact was produced by running the real code, and
`backend/tests/test_pave.py` re-derives the registry, the schemas, the examples
and the vectors on every test run.

## Four independent capability axes

| Axis | Question |
| --- | --- |
| `representable` | can the model express it, and does it round-trip through JDL? |
| `composable` | does the compiler add it to a real arrangement? |
| `stoneGeometry` | does Atlas build a stone solid for every cell? |
| `settingGeometry` | does Atlas build real metal that holds them? |

Statuses use JewelMind's established `CURRENT`/`PARTIAL`/`PLANNED` vocabulary.
The brief's "SUPPORTED" and "NOT_IMPLEMENTED" map to `CURRENT` and `PLANNED`:
a second status vocabulary for one subsystem would be exactly the registry drift
the same brief asks the audit to hunt for.

## Surface targeting

`BAND_OUTER` (cylindrical) and `HEAD_PLANE` (planar) resolve. Every other target
is reserved with a stated reason in `pave-registry.json`.

**A surface is resolved from parameters, never picked out of a solid.** A face
index is not reproducible across kernel versions, and a pavé whose stones moved
because a fillet renumbered a face would be indefensible.

`HALO_PLANE` is reserved even though it is trivially resolvable: a halo has no
metal, so beads in its plane would fuse into nothing.

## Identity

Placement ids are `<paveId>.r<row>.c<column>` — derived, reproducible, never a
UUID or a counter. Row and column are provenance, never identity. Reordering a
ring's explicit placements cannot move a stone: they are matched by sorted id.

## Forge rules

| Rule | Checks | Severity |
| --- | --- | --- |
| `JM-PAVE-001` | the host surface resolves for this design | error |
| `JM-PAVE-002` | the field compiles, via the real compiler | error |
| `JM-PAVE-003` | cells clipped by the surface edge | warning |
| `JM-PAVE-004` | stone and setting references resolve | warning |
| `JM-PAVE-005` | the execution boundary and the professional-review requirement | information |
| `JM-PAVE-006` | the pitch is geometrically consistent with the stones | warning |

**Only `JM-PAVE-006` is numeric, and it is arithmetic**: stones wider than the
pitch between their centres overlap as a matter of geometry. Its Forge
classification is `GEOMETRY_PRECONDITION`. There is deliberately no minimum
spacing, no minimum bead diameter, no maximum density and no settable seat
depth.

`test-vectors/invalid-pave-vectors.json` records which **layer** refuses each
malformed case, including the two software safety limits — a pathological pitch
must not be able to ask the kernel for an unbounded number of solids.
