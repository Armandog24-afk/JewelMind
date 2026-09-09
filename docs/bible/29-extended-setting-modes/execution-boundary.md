---
id: JM-BIBLE-ESM-EXECUTION-BOUNDARY
title: "Extended Setting Modes execution boundary"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-09
source_of_truth: true
depends_on:
  - JM-BIBLE-ESM-README
implementation_status: partial
professional_validation: not_required
normative: true
---

# Extended Setting Modes execution boundary

Exactly what executes, exactly what does not, and in which order the gaps have
to close. The point of this document is that "supported" is not one question:
a mode can be expressible in JDL, resolvable by the compiler, buildable by
Atlas and still absent from Studio, and a registry that answered only
"SUPPORTED" would hide which.

## The four capability axes

| Axis | Question |
| --- | --- |
| `representable` | Can a JDL document express it? |
| `compilable` | Does the compiler resolve it? |
| `stoneGeometry` | Do the stones exist as solids? |
| `settingGeometry` | Is real retention or support metal built? |

For all twenty implemented modes, all four are `true`. `settingGeometry` is
**measured** from the live builder registries rather than declared, so that
claim is a fact about the code rather than a statement about it.

## The eleven pipeline stages

Every mode declares a status for each of: `schema`, `parser`, `validator`,
`compiler`, `geometry`, `inspection`, `export`, `vision`, `studio`, `designer`,
`conversation`.

Nineteen of the twenty are `CURRENT` at every stage. The exception is
`PRONG_SHARED`, whose `studio`, `designer` and `conversation` stages are
`PLANNED` because no interface authors explicit prong positions.

## What executes

| Capability | State |
| --- | --- |
| Six setting families dispatched from one registry | executes |
| Five head architectures, all one connected solid | executes |
| Four field-retention strategies | executes |
| Angular openings cut through a bezel wall | executes |
| Windows pierced through a head wall | executes |
| A solid collar with the stone cut out of it | executes |
| Two opposing supports, each relieved by the stone | executes |
| Channel walls and end caps | executes |
| Transverse bars at a stated pitch, symmetric or asymmetric | executes |
| Mode resolution from `type` + `prongStyle` + `setting.mode` | executes |
| A deterministic mode fingerprint | executes |
| Per-component provenance naming the mode, stone and instances | executes |
| Nineteen new Geometry Inspection facts | executes |
| Six Forge rules | executes |
| STEP, STL, JSON and specification export for every family | executes |
| Studio controls for every mode axis | executes |
| Designer proposing a family, a variant, a head and relief | executes |
| Conversation modifying any of them incrementally | executes |
| Seven new Golden baselines | executes |

## What does NOT execute, and what it depends on

### Structural behaviour of a tension setting — needs engineering evidence

Nothing computes the elastic response of the metal, the force the supports
apply, or whether a stone is retained. This is not a code gap: it needs material
properties and a validated engineering model, and then a real
professional-validation record. Until then `TENSION_OPPOSED` is PARTIAL,
`professionalReviewRequirement` is `REQUIRED`, and
`SETTING_STRUCTURAL_BEHAVIOUR_MODELLED` reports `false` as a geometric fact.

**No stress threshold may be invented in the meantime.**

### Derived shared-prong placement — needs anchor-driven placement

`PRONG_SHARED` builds real prongs at positions the DOCUMENT states. Deriving the
shared position from two stones' own geometry needs a placement strategy that
consumes Stone v2's anchors, which does not exist — the same dependency
`PRONG_COMPASS_POINT` records. Order: anchor-driven placement first, then
derived sharing, then a Studio/Designer surface for it.

### A rail or a bar as pavé retention — needs a non-corner anchor topology

The pavé's retention anchors are lattice CORNERS. A rail runs a whole row and a
bar sits at a cell midpoint, so neither is expressible in that topology.
Channel and bar setting exist as PRIMARY families instead. Closing this properly
means giving the pavé a retention-topology registry, not adding a strategy that
misuses the corner set.

### Halo retention metal — unchanged since Sprint 25

Halo `settingGeometry` is still `false`: the halo layer composes placements and
no builder holds a halo member. `HALO_HIDDEN_SETTING` would have nothing to
build. Order: a setting strategy for a non-primary member (the RFC Sprint 24
identified) has to land first.

### A swept trellis head — needs a verifiable swept solid

Interwoven curved rails need a swept solid along a 3D spline. Order: a verified
sweep primitive in Atlas, then the head builder. A "simplified trellis" of four
bent prongs would be a different structure wearing the name.

### Decorative piercing (azure, millgrain) — needs a pattern representation

Arbitrary decorative piercing is not expressible as parameters, and no texturing
or knurling operation exists. `HEAD_OPEN_GALLERY` is the parametric subset that
is, and is deliberately not called azure.

### Per-instance settings for a channel or bar row — SETTING_COVERAGE_PRIMARY_ONLY

Metal is generated for the design's own stone. A channel or bar row spanning
arrangement instances records which instances it holds and does not build a
separate setting per instance. Order: the same RFC as halo retention.

### `GeometryPlan` — deliberately still not materialized

The provenance requirement is met on the existing setting result. Materializing
`GeometryPlan` is an explicit ADR condition and remains unmet; nothing in this
sprint needed it.

## The order the remaining gaps close in

1. **Anchor-driven placement** (Stone v2 anchors → a placement strategy).
   Unblocks derived shared prongs and compass-point heads.
2. **A setting strategy for a non-primary member** (the RFC Sprint 24 named).
   Unblocks halo retention and per-instance channel/bar settings.
3. **A verified sweep primitive.** Unblocks the trellis head and tapered
   channels and bars.
4. **A retention-topology registry in the pavé layer.** Unblocks rails and bars
   as field retention, if that is ever wanted alongside the families.
5. **Professional review**, which unblocks nothing technically and is the only
   thing that could ever make a functional claim about a tension setting true.

Steps 1–4 are engineering. Step 5 is not, and cannot be substituted for by any
amount of it.
