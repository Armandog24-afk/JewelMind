---
id: JM-BIBLE-PAVE-README
title: "Pavé & Microsetting Engine v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-08
source_of_truth: true
depends_on:
  - JM-BIBLE-ARRANGE-README
  - JM-BIBLE-FAMILY-README
  - JM-BIBLE-HALO-README
  - JM-BIBLE-SETTINGV2-README
  - JM-BIBLE-STONEV2-README
  - JM-BIBLE-GEM-README
related_documents:
  - JM-BIBLE-ADR-011
implementation_status: partial
professional_validation: not_required
normative: true
---

# Pavé & Microsetting Engine v1

Sprint 26. The machine-readable half lives at
[`specs/pave/v1/`](../../../specs/pave/v1/README.md).

**Implementation status is PARTIAL, precisely.** Both field kinds compile,
resolve, and build **real stone geometry AND real retention metal** — beads,
shared beads or micro-prongs fused into the host, plus an optional recess cut
out of it. What is PARTIAL is the *scope*: two host surfaces resolve out of
seven named, and one field per design. See
[`execution-boundary.md`](execution-boundary.md).

## What is new about this sprint

Sprints 24 and 25 built stones with **no metal holding them**, and said so —
`settingGeometry: false` in both registries. Sprint 26 is the first in the
programme where that axis is `true`: a bead is a real solid fused into the
production body, and a recess is the stone's own volume cut out of it.

That is the single substantive difference, and
`test_pave.py::test_this_is_the_first_sprint_to_claim_setting_geometry` asserts
it against the Family and Halo registries so the claim is comparative rather
than self-declared.

## Pavé and microsetting are two models

| | `PaveSpec` | `MicrosettingSpec` |
| --- | --- | --- |
| The designer states | an **area** and a **density** | a **structure** |
| Which is | `angularSpanDeg` + `pitchMm` + `rowCount` | `columnCount` × `rowCount` + spacings |
| What follows | the stone count | the area covered |

They are two models rather than one with a flag because the *inputs* are
genuinely different, and a shared model would have to make half its fields
meaningless for each. They share the lattice primitives — pattern, row offset,
termination, symmetry, host, retention, seat — because they are two ways of
describing one lattice, not two lattices.

## Five separate questions

```
WHAT the stones are        Stone System v2      stone.shape, dimensions
WHAT they are made of      Gem Identity v1      GemIdentity
WHICH individual stones    Arrangement v1       StoneInstanceDef
WHERE they sit             Arrangement v1       InstanceTransform
HOW metal holds them       Setting System v2    setting/retention.py
--------------------------------------------------------------------
WHICH FIELD they populate  THIS SUBSYSTEM       jewelmind/pave/
```

Nothing in `jewelmind/pave/` restates a stone, a gem, a placement or a setting.
It answers one question — *which region of which surface, at what pitch, held
how* — and compiles into arrangement primitives.

## Surface targeting

A host is named with a `PaveHost` value and resolved to **numbers** by
`geometry/pave_surface.py` — the Ring-side translation point, the role
`geometry/setting_adapter.py` plays for settings.

| Host | Kind | Status |
| --- | --- | --- |
| `BAND_OUTER` | cylindrical about the finger axis | **CURRENT** |
| `HEAD_PLANE` | horizontal plane at the head's top | **CURRENT** |
| `SETTING_SURFACE`, `BAND_INNER`, `BAND_SIDE`, `CUSTOM_SURFACE`, `HALO_PLANE`, `PRONG_SURFACE` | — | **PLANNED**, each with a stated reason |

**A surface is resolved from parameters, never picked out of a solid.** A face
index is not reproducible: it can change with the kernel version, or when an
unrelated parameter alters how a solid was built. A pavé whose stones moved
because a fillet renumbered a face would be indefensible, so every supported
host derives from the same `constants.py` expressions the assembly uses.

`HALO_PLANE` is reserved for a reason worth naming here: a halo has **no
metal** (Sprint 25 recorded halo retention as PLANNED), so beads in a halo's
plane would fuse into nothing and ship a disconnected production solid. It is
blocked on the same setting RFC, not on surface targeting.

## The tilt this sprint needed

A cylindrical surface's normal points radially outward, so a stone set into a
shank must lean by its own angular position. `InstanceTransform` accepted one
rotation, about the vertical axis only — correctly, because Sprint 22 refused
to accept a rotation no builder could execute.

Sprint 26 built the builder. `InstanceTransform` gained `tiltDeg` and
`tiltAzimuthDeg`, `geometry/stone/instance.py` applies them as a real kernel
rotation about a horizontal axis through the solid's own centre, and
[`ADR-011`](../03-decisions/ADR-011-instance-axis-tilt.md) records the decision.
The field follows the capability, not the reverse.

## One placement authority

A pavé emits `StoneInstanceDef`s and `ArrangementRelation`s and nothing else.
The lattice is placed **explicitly** rather than through a `RADIAL` pattern, for
the reason Sprint 24 found the hard way: a pattern's generated members inherit
their source instance's overrides, and the only instance at a field's origin is
the centre stone, whose scale is its own — so a pattern route would produce a
field of full-size stones. The angular sequence of a full planar ring still
comes from `arrangement/radial.py`, the same function the resolver uses.

A pavé **composes**: it is added to whatever placement the design declares — a
family, a halo, an explicit arrangement, or nothing. Composed in the assembly
rather than in `effective_arrangement()`, because resolving a host surface means
measuring a band and `jewelmind.family` must not import a geometry module.

**A pavé-only design keeps its centre stone.** Composing onto `None` synthesizes
one `CENTER` instance at the origin; without it the deterministic primary
selection would pick the lowest-id *pavé* stone and the centre stone would
silently become one, inheriting the bare `stone_reference` name while sitting on
the band.

## Retention

| Strategy | What it builds |
| --- | --- |
| `NONE` | nothing — an explicit choice, reported in the field's notes |
| `BEAD` | four spheres per stone, drawn in toward their own stone |
| `SHARED_BEAD` | one sphere per lattice corner, naming every stone it touches |
| `MICRO_PRONG` | a capped cylinder per corner, normal to the surface |

Reserved: `SHARED_PRONG`, `CHANNEL`, `GRAIN`, `THREAD_SET`, each with a stated
reason and no builder.

The builders live in **`setting/retention.py`**, not in `jewelmind/pave/`:
Setting System v2 is authoritative for how metal holds a stone, and a bead is
metal holding a stone. The pavé owns *where* retention goes (it owns the
lattice); the Setting System owns *what a piece is*.

**Anchors are derived in the surface's own parameters**, not in 3D. A corner
computed in the tangent plane at each stone lands on the chord rather than the
surface, so two adjacent stones' shared corner comes out at two slightly
different points — and a `SHARED_BEAD` field silently degrades into an
individual-bead field with four times the solids. Working in (angle, axial) and
mapping to 3D once makes adjacent cells share a corner exactly.

## Recess, not seat

`seat.mode: REFERENCE_RECESS` cuts the field's stones out of the host, routing
through **`setting/seat.py`** — the module whose own source is asserted never to
call `.fuse()` on a stone shape (SETTINGV2-GOV-008, LAW-006). The pavé inherits
that guarantee rather than restating it.

Deliberately called a **recess**: it has no bearing shoulder and makes no claim
that a stone would sit correctly in it.

## Validation

Six rules, all `PAVE_ONLY`: `JM-PAVE-001` (the host resolves), `JM-PAVE-002`
(the field compiles, through the real compiler), `JM-PAVE-003` (cells clipped by
the surface edge, warning), `JM-PAVE-004` (references resolve, warning),
`JM-PAVE-005` (the execution boundary and the professional-review requirement,
information), `JM-PAVE-006` (pitch consistency, warning).

**Only one is numeric, and it is arithmetic.** `JM-PAVE-006` compares the
stone's own resolved footprint, scaled by the field's own scale, against the
pitch between centres: below that, adjacent stones intersect as a matter of
geometry. There is deliberately **no** minimum pavé spacing, no minimum bead
diameter, no maximum density and no settable seat depth — each needs sourced
professional evidence this project does not have.

## Identity and determinism

Placement ids are `<paveId>.r<row>.c<column>` — derived from the field's own id
and the cell's lattice coordinates, never a UUID or a counter. Row and column
are carried as **provenance**, never as identity.

A pavé places stones and cuts metal, so it is inside `geometryHash` as well as
`definitionHash`; `test_pave.py` asserts that every geometry-affecting field
changes it. Repeated generation in one process is **bit-identical**, measured
rather than assumed, which is what justifies the suite's `rel=1e-9` comparisons.

## Software safety limits

`MAX_PAVE_STONES = 120`, `MAX_PAVE_ROWS = 12`, `MAX_PAVE_COLUMNS = 60`. These
are **software safety limits**, documented as such: a pathological pitch on a
wide span would otherwise produce tens of thousands of stones and exhaust memory
before any validation reported it. Nothing here claims how many stones a pavé
should carry. A declared microsetting is refused at the *schema* layer, because
its count is knowable from the document alone; a derived pavé is bounded by the
compiler.

## Backward compatibility

`pave` is optional and nullable. `compose_pave(base, None)` returns `base` — the
same object — and nothing synthesizes a pavé. `schemaVersion` stays `0.1.0`: the
same MINOR judgment Sprints 21–25 made.

The default solitaire's metal volume is unchanged and all 49 pre-existing Golden
baselines hold with no update. Five new cases (`PAVE-001`–`PAVE-005`) cover the
newly executable scope, bringing the suite to 54.

## Governance

See [`pave-governance.md`](pave-governance.md) for the full `PAVE-GOV` rules and
[`execution-boundary.md`](execution-boundary.md) for exactly what does and does
not execute.
