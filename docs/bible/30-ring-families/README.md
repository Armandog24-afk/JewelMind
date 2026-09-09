---
id: JM-BIBLE-RINGFAM-README
title: "Ring Families v2"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-09
source_of_truth: true
depends_on:
  - JM-BIBLE-JEWELRY-CATEGORY-ARCHITECTURE
  - JM-BIBLE-SHANK-GOVERNANCE
  - JM-BIBLE-FAMILY-GOVERNANCE
  - JM-BIBLE-HALO-GOVERNANCE
  - JM-BIBLE-PAVE-GOVERNANCE
  - JM-BIBLE-ESM-README
related_documents:
  - JM-BIBLE-RINGFAM-GOVERNANCE
  - JM-BIBLE-RINGFAM-EXECUTION-BOUNDARY
  - JM-BIBLE-RINGFAM-COVERAGE-REVIEW
  - JM-BIBLE-ADR-014
implementation_status: current
---

# Ring Families v2

**Sprint 28.** The machine half of this section lives at
[`specs/ring-family/v1/`](../../../specs/ring-family/v1/README.md).

## What this sprint decided

**A ring family is a parametric relation, not a preset.** That sentence is the
whole design, and the brief's own final test was whether a jewelry designer
could really use the result as a parametric system or whether we had built a
catalogue of names.

A catalogue would have been much easier to build and would have passed a test
suite that checked JSON. So the distinction is enforced in three places, and
each is checked against measured geometry rather than against declarations:

1. **Every variant must produce geometry that differs from its family's
   baseline.** Measured by rebuilding both and comparing solids. Exactly one
   variant may report no difference — `SOLITAIRE_CLASSIC`, which *is* the
   baseline — and it is flagged `isFamilyBaseline` so that answer can never be
   mistaken for an unfinished variant.
2. **A fundamental parameter must propagate without the model being rebuilt by
   hand.** Ring size, centre stone, side stones, setting type and shank profile
   each have a test that changes one input and measures the geometric result.
3. **Family parameters MODULATE what the document already states.** A variant's
   head factor multiplies `setting.basketHeight`; a halo's radius multiplies the
   *centre stone's own half width*. Nothing is replaced with a constant, so
   `ring.innerDiameter` and `stone.diameter` keep driving the geometry.

## Two flat fields, and no second authority

| Field | Meaning |
| --- | --- |
| `jewelry.style` | the **family** |
| `ringFamily.variant` | which **variant** of it |

`jewelry.style` has meant "ring family" since Sprint 16, so this sprint
**extended** it rather than adding a competing `ringFamily.family` that could
disagree with it. A variant belonging to another family is **refused**
(`JM-RINGFAM-001`), never resolved by precedence — the discipline
`JM-FAMILY-001` and `JM-SETTING-008` already carry, for the same reason: two
authorities over one design have no determinate resolution.

`resolve_ring_family()` is the **single resolution point**, the role
`effective_arrangement()` plays for placement and `resolve_primary_mode()` for
setting variants. A second consumer that re-derived the family would eventually
disagree with the geometry, and the disagreement would surface as a design that
validates and then fails to build.

## What it orchestrates rather than duplicates

The sprint's own §0 constraint: *Ring Families must ORCHESTRATE the existing
systems, not replace them.* So the layer computes **no placement, no outline and
no solid of its own**. It derives JDL and lets each subsystem do its job:

| Derived | Executed by |
| --- | --- |
| `family.*` (side stones) | Multi-Stone Families v1 → the Stone Arrangement Engine |
| `halo.*` | the Halo System |
| `pave.*` | the Pavé & Microsetting Engine |
| `setting.basketHeight` | Setting System v2 |
| `band.architecture` + separations | the Shank subsystem's new architecture builders |
| `band.widthTaper` | `shank/taper.py::taper_ratio()`, unchanged |

An explicit `arrangement` beside a family that would derive one is **refused**,
because that is the same two-authorities problem one layer down.

## The six families

| Family | Status | Variants |
| --- | --- | --- |
| `solitaire` | CURRENT | `CLASSIC`, `CATHEDRAL`, `LOW_PROFILE`, `ELEVATED` |
| `three_stone` | CURRENT | `SYMMETRIC`, `GRADUATED` |
| `halo` | **PARTIAL** | `SINGLE`, `DOUBLE`, `HIDDEN` |
| `split_shank` | CURRENT | `PARALLEL`, `TAPERED` |
| `bypass` | CURRENT | `CROSSOVER` |
| `signet` | **PARTIAL** | `FLAT_TABLE` |

A family's status is the **weakest** of its variants'. Reporting the strongest
would let a family look complete while part of it is not.

Nine names are **reserved** with real technical reasons — `eternity`,
`toi_et_moi`, `cluster`, `plain_band`, `SOLITAIRE_TRELLIS`,
`SPLIT_SHANK_SCULPTED`, `BYPASS_TWIST`, `SIGNET_ENGRAVED`,
`SIGNET_OVAL_TABLE`. None is an enum member, so none can be chosen; each states
what is actually missing rather than "planned". See
[`coverage-review.md`](coverage-review.md).

## New geometry

Three real components, and the first of them closes a four-sprint gap:

- **`shoulders`** — `ring/models.py::ShoulderDefinition` has recorded
  `modeled: False` since Sprint 16. Cathedral builds two arches and split rails
  four, each lofted from the band's *own* profile wire up to the head's *own*
  height, so a shoulder can never disagree with the band about its
  cross-section.
- **`band` with a `SPLIT` or `BYPASS` architecture** — a split shank is two
  rails joined over the bottom span and genuinely separated at the top; the
  axial gap between them contains no metal. A bypass is **one** open rail
  travelling past a full turn.
- **`signet_body`** — a real solid with a rectangular table at the ring's top,
  built as its own component so it has parametric identity.

`UNIFORM` remains the default and keeps its pre-Sprint-17 fast path
byte-for-byte (SHANK-GOV-003): the architecture dispatch is tried *after* the
uniform path, never instead of it.

## Compatibility

Every pre-Sprint-28 document is a `solitaire` with no `ringFamily`, resolves to
`SOLITAIRE_CLASSIC`, and generates the pre-Sprint-28 geometry exactly:
**`341.44334316909976 mm³`**, the same number Sprints 19, 23 and 27 each had to
preserve. Zero Golden baselines were updated.

The adapter returns the **original document object** when a family changes
nothing. "Nothing changed" is not the same as "nothing derived": the baseline
*does* derive `setting.basketHeight` from the document's own value times two
factors of 1.0, which is a real provenance record and a no-op write. Comparing
each write's result — rather than counting derivations — is what keeps every
existing design on the exact path it always took.

## What is deliberately absent

**No professional threshold, and no claim of one.** Nothing here says how thin a
rail may be, whether a shoulder is castable, whether a signet table is thick
enough, or whether a bypass would hold. Each needs sourced professional evidence
this project does not have. Every variant is `NOT_REVIEWED` and the active
professional-validation registry still holds zero records.

The two numeric limits that exist are **arithmetic**, and each says so:

- `JM-RINGFAM-004` refuses a rail separation that leaves *no rail*. The rails
  share the band's width, so a wider separation narrows them rather than
  widening the ring — subtraction, not a judgment about thinness. A 0.15 mm rail
  is thin and is **not** refused.
- `MAX_ARCH_SPAN_DEG = 90.0` is the measured limit of a ruled-loft arch. See
  [`execution-boundary.md`](execution-boundary.md).

## Two defects this sprint found by measuring

Both were found by building and measuring rather than by reading code, and both
are fixed at the source with a permanent guard. They are recorded here because
each is a class of failure the codebase will meet again:

1. **A ruled loft self-intersects past a quarter turn, silently.**
   `shoulderSpanDeg` was bounded at 170; any value past 90 built an arch whose
   own `isValid()` passed while the ring's combined metal went invalid and the
   arches' volume collapsed from 84.651 mm³ to 19.577 mm³. The bound is now the
   measured construction limit, refused in both the schema and the builder.
   *OCC's validity check does not catch a self-intersecting loft* — so the
   guard is a precondition, not a check on the result.
2. **A boolean fuse can succeed and return nonsense.** A bypass whose two passes
   clear each other by ~0.07 mm produced a fuse that raised nothing, reported
   `isValid() == True`, and returned six solids of *negative* volume — the six
   prongs, inverted, with the band and the basket gone — with no warning.
   `_fuse_metal()` now checks the one invariant available without redoing the
   boolean: **a union is never smaller than its largest input.** A result that
   fails it takes the same honest compound fallback as a raised failure, with a
   warning naming the measurement.

## Where things live

| Concern | Module |
| --- | --- |
| taxonomy, parameters, reserved names | `backend/jewelmind/ring_family/models.py` |
| the parametric dependency table | `backend/jewelmind/ring_family/dependencies.py` |
| resolution and derivation | `backend/jewelmind/ring_family/resolve.py` |
| the capability registry | `backend/jewelmind/ring_family/capability.py` |
| the JDL meeting point | `backend/jewelmind/geometry/ring_family_adapter.py` |
| shank architectures | `backend/jewelmind/geometry/shank/architecture.py` |
| shoulders | `backend/jewelmind/geometry/shoulder.py` |
| the signet body | `backend/jewelmind/geometry/signet.py` |
| Forge rules | `backend/jewelmind/validation/engine.py::_ring_family_rules` |
| Studio | `frontend/src/components/RingFamilySection.tsx` |
| tests | `backend/tests/test_ring_families.py` |

## Read next

- [`ring-family-governance.md`](ring-family-governance.md) — the RINGFAM-GOV rules.
- [`execution-boundary.md`](execution-boundary.md) — exactly what does and does not execute.
- [`coverage-review.md`](coverage-review.md) — why each deferred family is deferred.
- [`SPRINT-28-VALIDATION-REPORT.md`](SPRINT-28-VALIDATION-REPORT.md) — what was verified, and how.
- [`ADR-014`](../03-decisions/ADR-014-ring-family-orchestration.md) — the two architectural decisions.
