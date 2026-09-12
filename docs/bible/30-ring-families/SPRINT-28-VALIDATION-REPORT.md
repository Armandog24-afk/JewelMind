---
id: JM-BIBLE-RINGFAM-SPRINT-28-REPORT
title: "Sprint 28 Validation Report — Ring Families v2"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-09
source_of_truth: true
depends_on:
  - JM-BIBLE-RINGFAM-README
related_documents:
  - JM-BIBLE-RINGFAM-GOVERNANCE
  - JM-BIBLE-RINGFAM-EXECUTION-BOUNDARY
  - JM-BIBLE-RINGFAM-COVERAGE-REVIEW
  - JM-BIBLE-ADR-014
implementation_status: current
---

# Sprint 28 Validation Report — Ring Families v2

## The question the sprint had to answer

> Could a jewelry designer really use Ring Families as a parametric system, or
> have we only built a catalogue of names?

**A parametric system.** The evidence is below, and all of it is measured
geometry rather than declared capability — because a catalogue would have passed
a test suite that checked JSON.

## What was built

| | Count |
| --- | --- |
| Families | 6 |
| Variants with a real derivation | 13 |
| Reserved names, each with a real technical reason | 9 |
| Declared parametric dependencies | 18 |
| Designer/Conversation terms | 40 |
| New geometry components | 3 |
| New Forge rules | 5 (2 mirrored to the frontend) |
| New inspection fact types | 14 |
| New Golden cases | 7 |
| Backend tests in `test_ring_families.py` | 126 |
| Frontend tests | 24 |

Three real new components: **`shoulders`** (the first geometry the shoulder has
ever had — `ShoulderDefinition` recorded `modeled: False` from Sprint 16 until
this sprint), **`band` under a `SPLIT` or `BYPASS` architecture**, and
**`signet_body`**.

## The parametric claim, measured

Each test below changes ONE input and measures the geometric result. A system of
stored presets would pass none of them.

| Input changed | Measured consequence |
| --- | --- |
| `ring.innerDiameter` | More metal and a larger envelope, in every family, with no ring-family rule firing |
| `stone.diameter` | The head's own volume changes, because the family MODULATES `setting.basketHeight` rather than replacing it |
| `stone.diameter` (halo) | The halo's radius moves, because it is derived from the centre stone's own half width |
| `sideStoneScale` | The side stones' own solids grow |
| `sideSpacingMm` | The stones' combined X extent grows |
| `setting.type` → `bezel` | The setting geometry changes AND the family's shoulders are still built |
| `band.profile` → `flat` | The band's volume changes **under a split-shank architecture**, which is the hardest case because the family builds the band itself |
| `band.width` | The rails NARROW rather than the ring widening — the relation stated as arithmetic |

And one test states the whole claim directly: for every parameter a variant
reads, changing it must change the measured metal volume. Five variant/parameter
pairs are asserted individually.

### One finding worth recording

**`ring.size` alone does not drive geometry — `ring.innerDiameter` does.**
`ring.size` is the nominal EU size, and `JM-RING-003` reports a disagreement
between the two rather than choosing one. This is stated as its own test,
because it is the one place a reader could reasonably expect `ring.size` to be
the parametric input and be wrong.

## Measured geometry, per variant

| Variant | Combined metal (mm³) | Solids | Stones |
| --- | --- | --- | --- |
| `SOLITAIRE_CLASSIC` | 341.443 | 1 | 1 |
| `SOLITAIRE_CATHEDRAL` | 363.167 | 1 | 1 |
| `SOLITAIRE_LOW_PROFILE` | 319.575 | 1 | 1 |
| `SOLITAIRE_ELEVATED` | 398.060 | 1 | 1 |
| `THREE_STONE_SYMMETRIC` | 341.443 | 1 | **3** |
| `THREE_STONE_GRADUATED` | 341.443 | 1 | **3** |
| `HALO_SINGLE` | 341.443 | 1 | **17** |
| `HALO_DOUBLE` | 341.443 | 1 | **39** |
| `HALO_HIDDEN` | 349.644 | 1 | **17** |
| `SPLIT_SHANK_PARALLEL` | 304.465 | 1 | 1 |
| `SPLIT_SHANK_TAPERED` | 293.019 | 1 | 1 |
| `BYPASS_CROSSOVER` | 177.413 | 1 | 1 |
| `SIGNET_FLAT_TABLE` | 573.036 | 1 | 1 |

The three-stone and halo rows carry *exactly* the baseline's metal, to the last
digit, because those families add **stones and no metal**. That is the honest
recorded boundary rather than a measurement error, and it is why the halo family
is PARTIAL.

## Compatibility

| Check | Result |
| --- | --- |
| Default solitaire metal volume | **`341.44334316909976 mm³`** — unchanged, the same number Sprints 19, 23 and 27 each preserved |
| Golden baselines | **all 68 PASS, zero modified** (61 before the 7 new cases were added) |
| Adapter object identity for a document with no family | **preserved** — `effective_definition()` returns the original |
| New components on a default document | **none** |
| Ring-family errors on a default document | **none** |

An additive schema change (`JewelryDefinition.ringFamily` plus five `BandSpec`
fields) moved every document's `definitionHash` and moved **no geometry at
all**. That distinction is the sprint's central compatibility result.

## Defects found, and how

Every one was found by **building and measuring**, never by reading code, and
every one is fixed at the source with a permanent test guard. Not one was fixed
by adjusting an assertion.

### Geometry

1. **Both split rails came out coincident.** `Workplane.translate()` before
   `.revolve()` silently loses the axial offset; the fused volume was exactly one
   rail's (66.5012 mm³). Fixed by revolving first and translating the SHAPE.
2. **A partial `revolve()` swept unpredictably** — 60° from `u=0` produced
   `zmax = 0.00`. Arcs are now built by intersecting a full revolve with a pie
   sector.
3. **A bypass built as two axially separated arcs came out as two disconnected
   solids.** Rebuilt as ONE open rail lofted over `360 + overlap` degrees with
   the axial offset interpolated.
4. **`SOLITAIRE_LOW_PROFILE` and `SOLITAIRE_ELEVATED` produced geometry
   identical to `CLASSIC`** — all three had `headHeightFactor = 1.0` and the
   variant contributed nothing of its own. Fixed with
   `VARIANT_HEAD_HEIGHT_FACTOR`, composed as `basketHeight × variant factor ×
   params.headHeightFactor`.
5. **`SPLIT_SHANK_TAPERED` derived `band.widthTaper` that the architecture
   builder ignored** — a silently ignored derived value, producing a volume
   identical to the parallel variant. Now 189.431 against 202.048 mm³.
6. **A ruled loft self-intersects past a quarter turn, and OCC reports the solid
   valid.** `shoulderSpanDeg` was bounded at 170; at 92° the arches collapsed
   from 84.651 to 19.577 mm³ and the ring's combined metal went invalid while the
   arch's own `isValid()` passed. `MAX_ARCH_SPAN_DEG = 90.0` is now enforced as a
   PRECONDITION in both the schema and the builder, derived arithmetically from
   the section-rotation formula.
7. **A boolean fuse can succeed and return nonsense.** A bypass whose two passes
   clear each other by ~0.07 mm produced a fuse that raised nothing, reported
   `isValid() == True`, and returned **six solids of negative volume** — the six
   prongs, inverted, with the band and basket gone — and emitted no warning.
   `_fuse_metal()` now checks that **a union is never smaller than its largest
   input** and takes the honest compound fallback with a warning naming the
   measurement.

### Architecture and contracts

8. **The ring-family layer imported geometry.** `capability.py` reached into
   `jewelmind.geometry` to measure `structuralGeometry`. Found by the AST
   neutrality guard. Resolved the way `pave/capability.py` resolves the same
   tension: the axis is declared and the correspondence is asserted in the test
   file, in both directions.
9. **`default_variant_for()` raised a bare `KeyError`.** `ring/adapter.py` guards
   on `RingFamilyError`, so the guard silently did not apply and a family with no
   generator surfaced as an untyped exception instead of the clean dispatch
   refusal. Now raises a domain error, with a test asserting every error class
   derives from the base.
10. **`ShoulderDefinition.modeled` was `Literal[False]`** and became a false
    claim the moment shoulders existed. Widened to a real `bool` plus an
    `architecture` field, read from the RESOLVED family so it cannot disagree
    with the component actually built.
11. **The TypeScript runtime guard hardcoded `jewelry['style'] !== 'solitaire'`**
    — correct while that was the only family, and it would have rejected every
    Sprint 28 family. The same class of stale literal Sprint 27 found in the JDL
    schema's `{"const": "prong"}` for `setting.type`.
12. **The JDL schema declared `jewelry.style` as `{"const": "solitaire"}`** —
    the identical defect, in the identical file, one field over. Both the
    `jewelry` and `band` subtrees were regenerated from live Pydantic.
13. **Designer reported `trilogy` / `three_stone` / `multi_stone` as
    unsupported** with "Only a single-stone solitaire is currently supported."
    That stopped being true in Sprint 24, and
    `PRODUCT_SUPPORTED_NOT_PROPOSABLE` already contradicted it in the same file.
    Both statements are now gone: a family became proposable this sprint.
14. **The shank capability registry marked `split_shank` and `cathedral_shank`
    `planned`.** Both are now real; SHANK-GOV-015 requires the registry to move
    when the code does.
15. **The capability coverage guard was wrong about five rows.** `three_stone`
    PLANNED, `halo` OUT_OF_SCOPE, `signet` PLANNED, `split_shank` PLANNED,
    `cathedral` PLANNED — all now real.
16. **`manifest.json`'s `fullSuite` had been incomplete since Sprint 24** — 22
    of 68 golden cases were missing. Nothing reads it, so no test caught it.
17. **`ShankDefinition` stopped mapping 1:1 from `band`.** Its docstring and its
    `specs/ring/v2/` schema both claim a 1:1 mapping, and Sprint 28 gave
    `BandSpec` five new fields without mirroring them — so the claim was false
    for part of the sprint. SHANK-GOV exists to prevent exactly this, and the
    fix landed in all three places the contract lives: the model, the adapter
    and the schema.
18. **Two Ring Architecture v2 contract documents were falsified.**
    `527-shoulder-contract.md` described a `Literal[False]` field and stated the
    shoulder has no geometry; `526-shank-contract.md` stated no split geometry
    was built. Neither was rewritten into having always said the current thing:
    each keeps its original statement, marked as what was true then, with the
    change recorded — the Bible's rule is to report a contradiction, not to make
    it disappear.

### Test errors of my own, corrected against the real APIs

The recorded fact names were `RING_FAMILY_SHANK_ARCHITECTURE` (not
`SHANK_ARCHITECTURE`); `inspect_model()` takes the model alone; the split
metadata key is `separatedAtTheHead`; the halo derivation writes `halo.variant`
and `halo.rings` rather than `halo`; `definition_hash` is a function in
`utils/hashing.py`, not a model method; and the golden manifest's `goldenIds`
holds objects, not strings. Each was corrected to the real API rather than the
API changed to suit the test.

## Governance

**No professional threshold was invented, and none is claimed.** Every variant
is `NOT_REVIEWED`; the active professional-validation registry still holds zero
records. `TestNoInventedProfessionalRule` reads every `JM-RINGFAM-*` message and
asserts none contains "production safe", "manufacturing validated", "casting
validated", "jeweler approved", "structurally safe", "strong enough" or
"castable".

The two numeric limits are **arithmetic**, and each is tested as such:

- `JM-RINGFAM-004` refuses a separation that leaves *no rail*. A 1.5 mm band with
  a 1.2 mm separation leaves a 0.15 mm rail — thin, and **not refused**, with a
  test asserting exactly that.
- `MAX_ARCH_SPAN_DEG = 90.0` follows from `angle_deg_for_u(u) = −90 + u × 360`.

**Two families are honestly PARTIAL**, each stating what is missing: `halo`
generates no metal to hold its stones (Sprint 25's boundary, unchanged), and
`signet`'s table is flat because no engraving, relief or texture exists anywhere
in the pipeline.

**Sprint 25's halo position was not silently reversed.** That sprint decided a
halo is not a family — a claim about where the *geometry* lives, which has not
moved. The capability note now carries both facts, and a test asserts both are
present.

## The whole pipeline, exercised end to end

Not just the geometry: every endpoint, for every structurally distinct family,
against the real FastAPI app. Real STEP and STL bytes, not a stub.

| Variant | generate | components | STEP | STL | specification | inspection |
| --- | --- | --- | --- | --- | --- | --- |
| `SPLIT_SHANK_TAPERED` | 200 | 5 | 200 (2,438,838 B) | 200 (1,003,584 B) | 200 | 200 |
| `SOLITAIRE_CATHEDRAL` | 200 | 5 | 200 (530,321 B) | 200 (465,684 B) | 200 | 200 |
| `SIGNET_FLAT_TABLE` | 200 | 5 | 200 (160,854 B) | 200 (420,084 B) | 200 | 200 |
| `HALO_HIDDEN` | 200 | 20 | 200 (197,239 B) | 200 (522,784 B) | 200 | 200 |
| `BYPASS_CROSSOVER` | 200 | 4 | 200 (973,876 B) | 200 (321,284 B) | 200 | 200 |

**No new endpoint was added, and none needed to change** — a ring family is
expressed entirely in the request body.

### And in the running application

Not only through the API. The real Studio, against the real backend, in a
browser:

- The **Ring family** section renders first among the design controls, with all
  six families and no reserved name.
- Selecting `split_shank` swapped the variant list to
  `SPLIT_SHANK_PARALLEL`/`SPLIT_SHANK_TAPERED` **and** revealed exactly the
  controls that variant reads — rail separation, joined span, shoulder reach,
  shoulder narrowing — while leaving the band, stone and head values untouched.
  That is the parametric claim visible in the interface rather than only in a
  test.
- **Generate model** produced a real split-shank ring with five components,
  including `shoulders` as its own toggle in the component list, each fetched as
  a real backend-generated STL.
- Validation reported *"No validation findings — this definition looks good."*
  and the permanent header notice — that models are preliminary and require
  review by a qualified jewelry professional — is intact.

## CI failed once, and why

The first push (`9904ed9`) failed CI on Linux after passing every gate on
Windows. Worth recording in full, because **this project had already made the
same mistake, in the same place, one sprint earlier** — and `test_setting.py`
documents it at length.

**An OCCT volume is platform-dependent.** The default solitaire's combined metal
is `341.44334316909976` on this repo's Windows build and `341.44334316907685`
on CI's Linux build — a relative difference of ~6.7e-14. `Volume()` is an
integration over a shape's faces, so this is not unique to the boolean fuse.

Every pre-existing test in the suite therefore compares that number with
`rel=1e-9`. Two of my new assertions compared **live geometry against a
recorded value exactly**:

- `test_the_default_design_keeps_its_exact_metal_volume`
- `TestSpecArtifacts::test_the_compatibility_vector_still_holds`

Both now use `KERNEL_VOLUME_REL_TOL = 1e-9` — the value five existing test
modules already use, so no new number was introduced. The constant's comment
records the measured drift and points at `test_setting.py`'s own explanation, so
the next sprint has it in front of it.

**Determinism assertions stay exact, and that distinction is the point.** Two
builds of the same design in the same process must agree bit for bit — that is
what determinism means. A recorded value compared against live geometry is a
different question and gets the tolerance. Both are now labelled as such.

### Two other platform bets, removed while there

Neither is known to have failed; both were assertions about the KERNEL rather
than about my own logic, which is not a thing a test may depend on:

- **`test_a_degenerate_fuse_is_reported_rather_than_shipped`** asserted that the
  bypass at 175° *does* degenerate. Whether a given OpenCascade build degenerates
  on a given input is build-specific, so asserting a kernel misbehaves
  reproducibly is asserting the wrong thing. The invariant is arithmetic, so it
  was extracted as the pure function `fuse_result_is_degenerate()` and is now
  tested as a table of numbers — including the real measured `−60.904` against
  `110.690`, so the case that motivated the guard is still recorded as data. The
  ring-level test now asserts only what holds either way: real geometry, and a
  warning **if** the fallback fired.
- **`test_an_extreme_but_legal_parameter_still_builds`** asserted
  `combined_metal.isValid()` on a configuration that may legitimately take the
  compound fallback. It now asserts every component is real geometry instead.

## Gates

| Gate | Result |
| --- | --- |
| `ruff check .` | **All checks passed** |
| `pytest -q` (backend) | **2641 passed, 0 failed** |
| `geometry-quality verify-all` | **All 68 goldens PASS**, zero baselines modified |
| `npx tsc -b` (frontend) | **exit 0** |
| `npm run test` (frontend) | **33 files, 275 tests passed** |

## Artifacts

- `specs/ring-family/v1/` — 20 files: 6 schemas, the registry, the dependency
  graph, 7 examples, 4 test-vector files, and a README. All generated by running
  the real implementation and re-derived by `TestSpecArtifacts` on every run,
  with the geometry vectors **re-measured** by rebuilding each variant.
- `docs/bible/30-ring-families/` — README, governance (14 RINGFAM-GOV rules),
  execution boundary, coverage review, and this report.
- `docs/bible/03-decisions/ADR-014-ring-family-orchestration.md`.
- `goldens/solitaire-v1/RF-001` … `RF-007`, each recorded in the
  golden-update register.

## Not done, and why

- **Metal that holds halo stones** — an RFC, and what would make the `halo`
  family CURRENT.
- **A surface-decoration system** — an RFC, and what would make `signet`
  CURRENT.
- **A swept solid along a 3D spline** — one RFC that three reserved variants
  share.
- **Sprint 29's specialty rings** — deliberately untouched.
