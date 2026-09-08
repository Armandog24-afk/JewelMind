---
id: JM-BIBLE-PAVE-SPRINT-26-REPORT
title: "Sprint 26 Validation Report — Pavé & Microsetting Engine v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-08
source_of_truth: false
depends_on:
  - JM-BIBLE-PAVE-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 26 Validation Report — Pavé & Microsetting Engine v1

## Test results

| Gate | Result |
| --- | --- |
| `backend/.venv/Scripts/python -m ruff check .` | clean |
| `backend/.venv/Scripts/python -m pytest -q` | **2210 passed**, 1 pre-existing unrelated warning |
| `python -m jewelmind.geometry_quality.cli verify-all` | **All 54 goldens PASS** (49 before), **zero pre-existing baseline updates** |
| `frontend/ npx tsc -b` | clean |
| `frontend/ npm run test` | **227 passed** across 29 files |

New tests: `test_pave.py` (132), `paveValidation.test.ts` (14).

## What executes

Two first-class field kinds — a `PAVE` (an area at a density) and a
`MICROSETTING` (a stated structure) — each declared in JDL, each compiled into
**arrangement primitives** on a host surface resolved from the design's own
parameters, and each producing:

- **one real stone solid per cell**, individually identified, scaled, and
  leaning along the surface normal;
- **real retention metal** — beads, shared beads or micro-prongs — fused into
  the production body;
- **an optional recess**, the stones' own volume cut out of the host.

Five lattice patterns, containment against the surface edge, mixed gem identity,
Studio configuration, EN/IT Designer language, and Conversation modification
through the existing action set.

## The one substantive first

**This is the first sprint in the programme where `settingGeometry` is `true`.**
Sprints 24 and 25 built stones with no metal holding them and said so; a pavé's
retention is real metal. `test_pave.py::test_this_is_the_first_sprint_to_claim_setting_geometry`
asserts it against the Family and Halo registries, so the claim is comparative
rather than self-declared.

## The one architectural extension

A cylindrical surface's normal points radially outward, so a stone set into a
shank must lean by its own angular position. `InstanceTransform` accepted one
rotation about the vertical axis only — correctly, because Sprint 22 refused to
accept a rotation no builder could execute (ARRANGE-GOV-011).

Sprint 26 built the builder, then added the field:
[`ADR-011`](../03-decisions/ADR-011-instance-axis-tilt.md). `tiltDeg` plus
`tiltAzimuthDeg` and the existing spin are ZXZ Euler angles — a complete
orientation. `full_3d_instance_orientation` moved from PLANNED to CURRENT, and
`test_arrangement.py`'s two assertions moved with it rather than being loosened.

Confining the field to where the normal is already vertical was rejected as a
capability, not as an implementation: it would have shipped a shank pavé one
stone wide and called it a shank pavé.

## Verified by execution, not by reading

- **A tilt is a real kernel rotation.** At 90° a stone's X and Z extents swap
  exactly and its volume is unchanged, measured on the built solid.
- **Retention metal is real and joins the body.** Every pavé Golden reports four
  production components in one fully-connected group, and the metal grows by
  *less* than the beads' own volume — because they are embedded in the host
  rather than resting on it.
- **`BEAD` and `SHARED_BEAD` build different metal.** Measured, and it took a
  fix to make true (below).
- **The recess removes real material.** Three Golden cases record a band volume
  below the untouched `250.991683`; the two that request no recess record
  exactly `250.991683`.
- **A pavé-only design keeps its centre stone**, at the full `58.22142 mm³`.
- **The pitch rule is arithmetic.** Its suggested value is the scale at which the
  footprint equals the pitch — derived, not recommended.
- **Repeated generation is bit-identical in one process**, measured rather than
  assumed, which is what justifies the suite's `rel=1e-9` comparisons instead of
  a tolerance chosen by feel.
- **A design with no pavé is unchanged.** The default solitaire's metal volume
  still matches `341.44334316909976` and its component set is the historical
  four.

## Defects found and fixed during the sprint

1. **A pavé-only design lost its centre stone.** Composing onto `None` produced
   an arrangement containing only pavé stones, so the deterministic primary
   selection picked the lowest-id pavé stone — and the centre stone became one,
   inheriting the bare `stone_reference` name while sitting on the band. Fixed
   by synthesizing the design's own `CENTER` instance.
2. **`SHARED_BEAD` was only a label.** Anchors were computed in the tangent
   plane at each stone, so on a curved surface two neighbours' shared corner
   landed at two slightly different points and nothing was shared — 76 anchors
   where 40 were expected. Fixed by deriving anchors in the surface's own
   (angle, axial) parameters, where adjacent cells share a corner exactly.
3. **`BEAD` produced metal identical to `SHARED_BEAD`.** Placed at the full
   half-pitch, an individual bead lands on the corner its neighbours also use,
   so four coincident spheres fused into one: the strategy reported four times
   the pieces and delivered the same solid. Fixed by drawing an individual bead
   in toward its own stone (`_INDIVIDUAL_BEAD_INSET_FRACTION`, documented as a
   construction parameter). Found by measuring volume, not by reading the code.
4. **Beads were buried inside their stones.** The corner reach was derived from
   the bead's own radius rather than the lattice half-pitch, and a pavé stone is
   wider than its bead.
5. **Designer could not turn a pavé on.** `pave.spec` is a discriminated union,
   so a dotted-path patch could not construct one and "add a pavé to the shank"
   failed with a diagnostic the user could not act on. Fixed by seeding the
   domain's own `default_pave_field()`, kind-aware, from the one function the
   Studio toggle mirrors.

## Tests updated rather than weakened

Two assertions in `test_arrangement.py` and one in `test_capability_coverage.py`
encoded Sprint 22's truth — that no tilt field existed and nothing claimed 3D
orientation. Each became *more* specific rather than looser: the transform's
field set is still asserted exactly, so a future field added without a builder
still fails, and the moved capability is now asserted true in all three axes so
the move cannot be a documentation-only claim.

## Pre-existing defects fixed in passing

Both were directly on this sprint's path:

1. **Designer reported `pave` AND `halo` as unsupported concepts.** Both were
   true when written; neither is now. `pave` was removed because Designer can
   propose its parameters. `halo` moved to a new
   `PRODUCT_SUPPORTED_NOT_PROPOSABLE` map, because "the product does not have
   this" and "Designer cannot compose this" are different statements and the
   first was a misreport.
2. **The Forge rule catalog's total** was refreshed again from the registry (54).

## Boundaries held

- Nothing under `jewelmind/pave/` imports a jewelry category, a geometry module,
  the Setting System, the kernel or `JewelryDefinition` — AST-verified.
- `geometry/pave_surface.py` is kernel-free, which is what lets Forge resolve a
  host surface with the same code generation uses.
- Retention geometry lives in `setting/retention.py`; no `makeSphere` appears
  anywhere under `jewelmind/pave/`, asserted by scanning the package.
- `pave_adapter.py` contains no `.fuse` call at all — AST-verified. The recess
  routes through `setting/seat.py` and inherits its guarantee.
- **No second placement engine, and no duplicated registry.** The pavé reuses
  the arrangement's transform, the arrangement's ring arithmetic, the family's
  member conventions, the Setting System's seat module, and Sprint 24's
  per-instance stone placement.
- Six new Forge rules; only one is numeric and it is classified
  `GEOMETRY_PRECONDITION`. No professional threshold anywhere — verified by
  scanning the real emitted messages across five deliberately extreme
  configurations.
- **No new `ConversationActionType`.** "Metti micro pavé sul gambo" classifies
  as an existing `MODIFY_DESIGN_PROPOSAL` and routes through
  `DesignerService.interpret()`, exactly as CONV-GOV requires.
- One field per design, expressed as a singular `pave` field so the limitation
  is visible in the schema rather than implied.

## Adversarial input

Zero, negative, NaN and infinite dimensions; a JDL-style string number; an
unknown field; a path-traversal id; an over-capacity declared structure; a
pathological pitch that would produce a runaway field; a field overrunning its
host; an id collision. Every case is refused, and
`specs/pave/v1/test-vectors/invalid-pave-vectors.json` records which **layer**
refused it — fourteen at the schema, two at the compiler.

The API returns 422 with the rule id and no traceback, no exception class name
and no server path.

## GeometryPlan

The brief asks to extend `GeometryPlan` where necessary. **It does not exist** —
ALCHEMIST-GOV-004 describes it conditionally, and materializing it is an
ADR-level change this sprint did not make. The pavé's compilation output travels
on `GeneratedModel.pave_result` beside `setting_result` and
`arrangement_result`: every placement with its lattice provenance, every anchor
with the stones it serves, the clipped-cell count, and what was not built. That
satisfies the requirement behind the request — no anonymous geometry — without
inventing a pipeline stage.

## Professional validation status

Unchanged: **zero records** in the active professional-validation registry.
Every pavé host, pattern, retention strategy and dimension is `NOT_REVIEWED`.
`JM-PAVE-005` states on every field that no pavé dimension is professionally
validated and that a qualified jewelry professional must review it before
production; the Studio panel repeats it as permanent copy, and every new Golden
baseline records it as a known limitation.
