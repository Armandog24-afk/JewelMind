---
id: JM-BIBLE-PAVE-BOUNDARY
title: "Pavé execution boundary"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-08
source_of_truth: true
depends_on:
  - JM-BIBLE-PAVE-README
implementation_status: partial
professional_validation: not_required
normative: true
---

# Pavé execution boundary

What executes, what does not, and why the line sits where it does.

## Executes today

| Capability | Evidence |
| --- | --- |
| Declare a pavé or microsetting in JDL | round-trips; validates against `specs/jdl/v1/jdl.schema.json` |
| Compose it onto a solitaire, a family, a halo or an arrangement | `pave/compile.py`; composed in the assembly |
| Resolve two host surfaces | `geometry/pave_surface.py`, derived from `constants.py` |
| Build a stone solid per cell | `geometry/stone/instance.py`; measured: 0.1 scale gives 0.1³ of the volume |
| Lean each stone along the surface normal | measured: at 90° a stone's X and Z extents swap exactly and its volume is unchanged |
| Build **real retention metal** | measured: bead/shared-bead/micro-prong volumes are non-zero and differ per strategy |
| Fuse retention into the production body | measured: one connected production group, four production components |
| **Cut a recess** out of the host | measured: the band's volume drops; `paveRecessOperation: CUT_STONE_FROM_METAL` |
| Five lattice patterns | `GRID`, `STAGGERED`, `ROW_OFFSET`, `RADIAL`, `EXPLICIT` |
| Clip or refuse a field that overruns the surface | `containment`; a clipped field reports how many cells it lost |
| Mixed gem identity per field | the real Sprint 21 registry |
| Structural validation | `JM-PAVE-001`…`006` |
| Studio configuration | `frontend/src/components/PaveSection.tsx` |
| Designer natural language, EN/IT | `pave.host`, `pave.kind`, `pave.retention.strategy`, … |
| Conversation modification | through the existing `MODIFY_DESIGN_PROPOSAL` action; **no new action type** |
| Export | STEP/STL/JSON/specification carry the retention metal; stone references stay excluded by default |
| Keep pavé-free designs identical | metal volume unchanged; 49 pre-existing Goldens, zero updates |

## Does not execute

### Five of seven host surfaces — PLANNED

`SETTING_SURFACE` (a basket wall or prong flank is a swept surface with no
closed-form parameterization; targeting it means picking faces out of a solid),
`BAND_INNER` (the finger bore), `BAND_SIDE` (its extent depends on the band
profile's own section, and comfort-fit has no flat side at all),
`CUSTOM_SURFACE` (needs a real surface import and a robust offset walk),
`PRONG_SURFACE` (needs per-prong targeting and shared retention across two
curved bodies), and `HALO_PLANE`.

`HALO_PLANE` deserves its own line: it is **trivially resolvable** and still
blocked, because a halo has **no metal**. Sprint 25 recorded halo retention as
PLANNED, so beads in a halo's plane would fuse into nothing and ship as a
disconnected production solid. It is blocked on the same setting RFC that Sprints
24 and 25 both named — not on surface targeting.

### More than one field per design — PLANNED

`pave` is singular, deliberately. A shank pavé **and** a gallery pavé in one
document needs a rule for what happens where two fields meet: whether their
retention lattices merge, which host wins in an overlap, and how two recesses
compose on one component. None of that exists, so the limitation is visible in
the schema rather than implied by a plural field.

### Four retention strategies — PLANNED

`SHARED_PRONG` (needs the shared-prong geometry Sprint 23 recorded as PLANNED;
a bead already shares between four cells, but a shared *prong* is a different
solid with a different contact topology), `CHANNEL` (needs the support rails
Sprint 23 recorded as PLANNED), `GRAIN` (a cut-and-pushed surface treatment, not
a placed solid), `THREAD_SET` (needs a swept cut along the lattice, which a
per-stone cut does not express).

### An outline-following field — PLANNED

A field following a non-circular stone's own girdle outline needs the
outline-offset walk Sprint 25 already recorded as absent for halos. The planar
host offers concentric circles and says so.

### Mixed pavé stone shapes — PARTIAL

A field's `stoneRef` may name a stone specification other than `primary`, and
that reference is preserved and reported (`JM-PAVE-004`). It does not resolve,
because JDL carries exactly one `stone`, so such a field produces no geometry.

### Designer metric spacings — deliberate

Designer proposes the field's **structure** — kind, host, pattern, retention,
recess, stone size, row count — and **not** the metric spacings. `pitchMm`
belongs to a `PaveSpec` and `stoneSpacingMm` to a `MicrosettingSpec`, so a flat
dotted patch naming one could land on a spec that has no such field.

More importantly, "make the stones denser" names a **relative density**, not a
millimetre value. Turning one into the other requires knowing what pitch is
appropriate — exactly the professional judgment this project has no evidence
for. The density vocabulary is recognized
(`normalizer.PAVE_DENSITY_TERMS`) so such a request can be understood and
clarified, never resolved to a number on the user's behalf.

Switching the field **kind** through Designer works, and had to be special-cased
in one place: `pave.spec` is a discriminated union, so a flat patch cannot
rebuild it. The requested kind selects which of the domain's two default fields
is seeded, from `pave/models.py::default_pave_field()` — the same function the
Studio toggle's default mirrors, so a spoken instruction and a UI toggle cannot
produce different designs.

### GeometryPlan — still unmaterialized

The Sprint 26 brief asks to extend `GeometryPlan` "only where necessary".
**`GeometryPlan` does not exist**: ALCHEMIST-GOV-004 describes it
conditionally ("if and when it is ever implemented"), and materializing it is an
ADR-level change this sprint did not make.

The real artifacts that carry compilation output are `GeneratedModel`'s
`setting_result`, `arrangement_result` and — new in this sprint —
`pave_result`, a `CompiledPaveField` carrying every placement with its lattice
provenance, every retention anchor with the stones it serves, the clipped-cell
count, and what was not built. That satisfies the brief's actual requirement
(no anonymous geometry; every solid traceable to the definition that produced
it) without inventing a pipeline stage.

### Vision — works, and deliberately unchanged

A pavé stone and the retention field reach the viewer as real
backend-generated STLs, classified by the `geometryRole` the preview manifest
already computes: `pave_retention` is registered explicitly in
`geometry/roles.py` as `production_metal` rather than left to the default, so
the classification is a stated fact. No frontend geometry was added, and none
was needed — a parallel visual-only pavé is exactly what VISION-GOV-001/002
forbid.

### Any professional pavé rule — PLANNED

No minimum spacing, no minimum bead diameter, no maximum density, no settable
seat depth, no judgment about whether a field could be cut by a setter. Each
needs sourced professional evidence this project does not have. The active
professional-validation registry holds **zero** records, and every pavé
capability is `NOT_REVIEWED`.

## What earlier sprints recorded, and what changed

| Recorded | Status after Sprint 26 |
| --- | --- |
| Sprint 22: tilt and roll are PLANNED and deliberately unrepresentable | **built** — ADR-011, because a curved-surface field needs it |
| Sprint 24: no accent setting strategy exists | **still true** for family members; a pavé's own retention is real |
| Sprint 25: halo metal does not exist | **still true**, and it is why `HALO_PLANE` is reserved |
| Sprint 24: `pave` needs a region-fill capability the arrangement engine lacks | **superseded** — a field is a lattice of explicit instances, not a region fill, and the capability row was corrected |
