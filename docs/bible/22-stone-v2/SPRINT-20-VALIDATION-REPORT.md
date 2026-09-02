---
id: JM-BIBLE-SPRINT20-REPORT
title: "Sprint 20 Validation Report — Stone System v2"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-STONEV2-README
  - JM-BIBLE-600
related_documents:
  - JM-BIBLE-SPRINT19-REPORT
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 20 Validation Report — Stone System v2

## Documents and specifications created

22 documents in `docs/bible/22-stone-v2/`, including this report.

42 files under `specs/stone/v2/`: 12 JSON Schemas, three registries generated
from the live code, a README, 19 examples and 8 test-vector files. Every
example, registry and vector is produced by **running the real
implementation**; the schemas are authored and then validated against those
generated artifacts, so a schema that fails to describe reality fails at
generation time.

## Stone v1 preserved

**Zero** Stone v1 Golden baseline updates. All 23 pre-existing cases pass
unchanged, including the exact-equality guards:

```
combined metal volume  341.44334316909976
prong volume            29.650351464580467
round stone volume      58.22141924499569
```

The six non-round v1 shapes are now routed through the v2 pipeline and are
**bit-identical** doing so — verified by running both implementations on the
same definition and requiring exact equality of volume and all six
bounding-box extents.

An earlier version of that test hardcoded expected volumes, and **five of the
six were wrong** — typed rather than measured, which is exactly what
JDL-GOV-009 forbids. The test now compares implementations instead of literals,
which is both correct and undriftable.

## Extended native shapes

**14 attempted, 14 CURRENT**, for 21 native cuts total:

heart, radiant, asscher, trillion, baguette, tapered_baguette, triangle,
trapezoid, lozenge, hexagon, kite, shield, half_moon, pearl.

None PARTIAL, none BLOCKED. Every one generates a real single valid solid, is
deterministic across runs, survives a STEP roundtrip with matching volume,
rotates 90° cleanly, and has a bounding box equal to the request.

All 25 shape × profile combinations were verified exact and valid.

Brief section 69 pre-authorized microscopic stabilization for pointed shapes.
**None was needed and none was implemented** — pinned by a test, so a future
change making a pointed shape fragile fails loudly rather than being quietly
patched with a hidden distortion.

## The dimension contract, and the four shapes that broke it

Requested dimensions must equal measured dimensions. Four constructions
violated that during development, and each was fixed at the source rather than
by adjusting what was reported:

| Shape | Measured overshoot | Cause | Fix |
|---|---|---|---|
| `shield` | 6.05mm for 6.00mm | Arc-based lower boundary | Made fully polygonal |
| `trillion` | 7.63mm for 7.00mm | Bowed bottom edge | Pre-inset the base vertices |
| `half_moon` | 7.50mm for 6.00mm | A circular arc through the chord endpoints always has radius > half-length | Rebuilt as half an ELLIPSE |
| `heart` | 3.3e-4mm at 8×6 | An unconverged fixed-point normalization | Rebuilt **exact by construction** |

The heart is the most instructive. The original construction corrected its
control box with a fixed-point iteration that converged linearly at ~0.34 per
step and **did not reach tolerance for elongated hearts** — a 10×6 heart was
still 8e-6mm too wide after forty steps. Solving the lobe geometry exactly (each
lobe a circle whose own extreme points ARE the requested bounds) removed both
the residual error and the iteration.

## Source modes

All four implemented: `PARAMETRIC_REFERENCE`, `CUSTOM_OUTLINE`, `MEASURED`
(CURRENT) and `IMPORTED_CAD` (PARTIAL).

`SCANNED_MESH` was deliberately **not** added: a scan arrives as a mesh or a
converted CAD file, which `IMPORTED_CAD` already normalizes, and a fifth mode
would duplicate that pipeline while implying scan-specific processing that does
not exist.

## Custom outline — the architecture proof

Real CAD generation for **convex and concave** outlines, and both drive real
bezel and prong settings through the generic interface.

Before this sprint they could not: `girdle_outline_wire()` looked outlines up by
shape NAME and dimensions came from named-cut fields, so a custom stone raised a
bare `AssertionError` deep inside `resolved_length_mm()`.

The fix required `StoneSettingReference` to carry `outlinePoints`, and
`build_stone_setting_reference()` to read dimensions from the **built
component** rather than the request — which is a better contract regardless,
because it describes the stone that exists.

**The proof is structural, not just behavioural.** An AST scan of every setting
module for a comparison of `.shape` against a string literal finds none. That
scan also caught two *pre-existing* name branches and removed them: strategy
selection now reads `isRadiallySymmetric` (a geometric property), and `round`
was given a signature-adapted entry in the outline-builder table instead of its
own conditional.

**One subtlety worth recording.** The carried points were initially preferred
over a native shape's analytic builder, which was simpler and measurably wrong:
an oval bezel built from a 48-point discretization stopped needing its
documented STEP-safety repair (a polyline has no ELLIPSE edge to offset into an
`OFFSET` curve) and the oval's `OUTLINE_CARDINAL` prong moved by 6.3e-5mm. The
exact builder now wins; carried points are the path for stones with no analytic
outline.

## Validation that rejects rather than repairs

Nine checks, each with a stable error code. Two findings:

**The bow-tie fixture would have passed for the wrong reason.** A symmetric
bow-tie has zero signed area, so the area check catches it and the
self-intersection detector never fires. The test now uses a crossed pentagon
with a real area (−19.5 mm²).

**A vertex touching a non-adjacent edge is not a proper crossing.** A Z-shaped
outline with a real area, no degenerate segments and no duplicated point passed
every check while not being a simple polygon — offsetting it, which is exactly
what a bezel does, is ambiguous. `_find_vertex_touching_edge` closes that.

Four valid controls — convex, concave, square, and a 64-point sampled ellipse —
must all pass, so the detectors cannot succeed by rejecting everything.

## Measured and imported stones

Measured stones preserve provenance verbatim, label a dimension-only result
`MEASURED_DIMENSION_REFERENCE`, and **never invent a missing measurement**.
Provenance carries no wall-clock timestamp; two builds of the same stone produce
byte-identical provenance.

Imported stones: STEP/BREP → real B-Rep solid with a real volume; STL → mesh
with 0 solids and a null volume. `supportsBrepOperations` is computed from the
real parsed geometry. Formats are declared from what the installed kernel
actually does — `.obj`, `.gltf`, `.glb`, `.iges`, `.igs`, `.3dm` are refused at
store time with the real per-format reason.

## Eight real bugs found and fixed

Every one was found by **exercising real objects**, not by reading code.

1. **Forge crashed on an imported stone.** `_stone_rules` called
   `resolved_length_mm()`, which correctly refuses for `IMPORTED_CAD`, so
   validation raised instead of validating.
2. **Forge fired on every valid pearl.** `STONE_DEPTH_RANGE` asserts
   `depth < min(length, width)`; for a sphere that is `d < d`. Scoped away
   rather than loosened, which would have weakened it for every other shape.
3. **Mesh transforms did nothing** — see below.
4. **`half_moon` was not centred on the origin.** `ellipseArc(...,
   startAtCurrent=False)` centres on the current point. Its bounding-box *size*
   was correct, so only a centre assertion caught it.
5. **Three shapes overshot their dimensions**, plus heart's unconverged
   normalization.
6. **A pearl request failed deep in the outline builder**, because `profile`
   defaults to `FACETED_REFERENCE` and a sphere supports only
   `SPHERICAL_REFERENCE`.
7. **A non-simple outline passed validation** (the touching case above).
8. **Designer produced a dead end** for a shape named without dimensions. It
   now asks a structured question per missing dimension — brief section 39's
   explicit requirement, verified rather than asserted in prose.

## The defining technical finding

**A mesh must be transformed node by node.** Neither
`cadquery.Shape.scale()` nor `BRepBuilderAPI_Transform` moves a triangulation
attached to an otherwise-empty face:

| Method | Bounding box after a requested 10× scale |
|---|---|
| `Shape.scale(10)` | 6 × 8 × 4 — **unchanged** |
| `BRepBuilderAPI_Transform` | 6 × 8 × 4 — **unchanged** |
| Direct node scaling | 60 × 80 × 40 — correct |

So an STL declared in centimetres came back at millimetre size. That was the
visible half.

**The worse half:** `normalizationOperations` still recorded
`UNIT_CONVERSION:cm->mm`. The provenance record asserted a conversion that had
never happened — and a false provenance entry is more damaging than a missing
one, because a missing entry prompts a question while a false entry answers it
wrongly.

The regression test asserts **correspondence**, not presence: a claimed unit
conversion must coincide with a real size change, for both representations.

## Three drifted hand-copies removed

Each was a *misreport of a real capability* — the same failure Sprint 18 had to
correct:

1. **Setting's shape lists** still held only the seven Stone v1 shapes, so a
   bezel over a custom outline was refused as "not supported" even though the
   geometry pipeline built it correctly.
2. **Designer's `KNOWN_UNSUPPORTED_CONCEPTS`** still listed heart, radiant,
   asscher, trillion, baguette and cabochon as unsupported.
3. **Designer's synonym table** lacked the underscored canonical IDs, so
   `tapered_baguette` and `half_moon` were reported unsupported.

All three are now derived from the Stone System registry rather than copied.

## Forge rule scoping

`STONE_DIAMETER_RANGE` remains ROUND_ONLY. `STONE_DEPTH_RANGE` is skipped for
spherical and imported stones, and **still fires correctly** for every other
shape — verified: a round d=20 fires `JM-STONE-001`, an over-deep heart and an
over-deep custom outline both fire `JM-STONE-002`, and pearl and imported
produce no errors.

Mirrored identically in `shared/validation/engine.ts` (FORGE-GOV-004).

Two gaps left open rather than closed by invention: `pearl` has no
diameter-range rule, and a non-round shape's `length`/`width` have none
individually (STONEV2-GOV-011).

## Golden coverage

**39 cases, all passing. Zero baseline updates.** 16 new `STV2-*` cases, each a
new case rather than a retrofit.

`STV2-001-heart-prong` records a **pre-existing** finding rather than avoiding
it: `productionIsFullyConnected: false`, with the band 0.0681mm from
`basket_support`. Measured proof that it is footprint-driven and not
shape-specific:

| Stone | Connected | band↔basket |
|---|---|---|
| princess 8 × 7.5 | yes | 0.0378 |
| princess 8 × 8 | **no** | 0.0681 |
| **round d = 8.0** | **no** | 0.0681 |
| heart 8 × 8 | **no** | 0.0681 |

A `round` stone of diameter 8.0mm — a capability since Sprint 2 — reproduces the
identical distances. Sprint 20 surfaced this; it did not cause it.

No Golden ring case exists for `pearl` or imported stones, because neither can
be set, so no ring can be assembled around them. Covered by unit tests and real
import vectors instead — a deliberate, recorded gap.

## Shape versus gem identity

No shape enum member is a gem species. The rhombus is `lozenge`, never
`diamond`. `StoneSpec` carries no material or species field. No shape synonym
resolves a species name to a cut. `emerald` reports
`family: CLIPPED_RECTILINEAR` and carries no species metadata.

**Known confusions remaining: 0.**

## No fabricated equivalent diameter

**0 introduced.** Verified structurally: no helper whose name contains both
"equivalent" and "diameter" exists in `stone_dimensions` or `normalize`, and
every non-round shape's normalized length and width genuinely differ.

## Capability Coverage Guard

137 entries (from 101): 56 `CURRENT`, 69 `PLANNED`, 2 `PARTIAL`, 7 `BLOCKED`,
3 `OUT_OF_SCOPE`. The 49 stone entries span six domains and are all generated
from the live registries.

`test_capability_coverage.py` grew to 18 tests, including a new one pinning the
Stone v1 and v2 registries together — two registries describing the same seven
shapes is a drift hazard, and what must never diverge is the facts they both
state.

## Professional validation

**0 records created. 0 unsupported claims introduced.**

Every shape, profile and source is `NOT_REVIEWED`. The active
professional-validation registry remains at **zero records**.

## Test results

| Suite | Result |
|---|---|
| Backend | **1397 passed** |
| Frontend | **137 passed** (22 files) |
| Golden suite | **39/39 PASS** |
| `test_stone_v2.py` | 192 |
| `test_stone_v2_no_category_dependency.py` | 29 |
| `test_capability_coverage.py` | 18 |
| ruff | clean |
| `tsc -b` | clean |

## Category neutrality

Zero jewelry-category imports anywhere in the Stone System, verified by AST
parsing rather than `import` — so it cannot pass by accident on a module another
test already imported.

`build_stone_geometry(stone, girdle_z_mm)` is the category-neutral entry point.
Before Sprint 20 the only way to build a stone was to hand the builder an entire
`JewelryDefinition`, which meant no other category — and no test — could
construct a stone without fabricating a ring around it.

## `definitionHash` drift — fourth consecutive occurrence

The additive `StoneSpec` fields changed the hash for every document, same
mechanism as Sprints 17–19. Still not a Migration Requirement 4 violation.
`compare_snapshot()` still never reads `definitionHash`. Twelve stored fixtures
regenerated by running real code.

Now genuinely predictable rather than surprising; resolving it needs an ADR.

## Known limitations carried forward

- **The head floats above the band for a footprint above ~7.5mm** —
  pre-existing, size-driven, recorded with measurements.
- **No outline projection from imported geometry** — this is what keeps
  imported stones `UNSUPPORTED` for both settings.
- **Concave custom outlines are not bezel-verified for every concavity.**
- **No seat, bearing or cutter geometry** for any setting — from Sprint 19.
- **Prong placement is not tip-, cleft- or corner-aware** for any of the 13
  new outline shapes; all are honestly `EXPERIMENTAL`.
- **No Studio UI** for custom, measured or imported stones. The runtime
  capability exists and the UI does not, which is the honest order.
- **No custom-outline editor** — deferred to Sprint 32 by the brief.
- **A mesh stone has never been exported to STEP** — untested rather than
  broken, since stones are excluded from production exports by default.
- **Nothing in Stone v2 is professionally validated.**
