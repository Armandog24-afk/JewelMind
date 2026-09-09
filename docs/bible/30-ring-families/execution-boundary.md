---
id: JM-BIBLE-RINGFAM-EXECUTION-BOUNDARY
title: "Ring Families — execution boundary"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-09
source_of_truth: true
depends_on:
  - JM-BIBLE-RINGFAM-README
related_documents:
  - JM-BIBLE-RINGFAM-GOVERNANCE
  - JM-BIBLE-PAVE-EXECUTION-BOUNDARY
  - JM-BIBLE-ESM-EXECUTION-BOUNDARY
implementation_status: current
---

# Ring Families — execution boundary

Exactly what runs, exactly what does not, and every number measured rather than
claimed. A capability is CURRENT only if the runtime produces it.

## Measured geometry, per variant

Built by `build_solitaire_ring()` against the real default document. Volumes are
the CAD kernel's own, in mm³. **These are software measurements, not
manufacturing figures, and nothing here is professionally validated.**

| Variant | Combined metal | Solids | Stones | Components |
| --- | --- | --- | --- | --- |
| `SOLITAIRE_CLASSIC` | 341.443 | 1 | 1 | 4 |
| `SOLITAIRE_CATHEDRAL` | 363.167 | 1 | 1 | 5 |
| `SOLITAIRE_LOW_PROFILE` | 319.575 | 1 | 1 | 4 |
| `SOLITAIRE_ELEVATED` | 398.060 | 1 | 1 | 5 |
| `THREE_STONE_SYMMETRIC` | 341.443 | 1 | **3** | 6 |
| `THREE_STONE_GRADUATED` | 341.443 | 1 | **3** | 6 |
| `HALO_SINGLE` | 341.443 | 1 | **17** | 20 |
| `HALO_DOUBLE` | 341.443 | 1 | **39** | 42 |
| `HALO_HIDDEN` | 349.644 | 1 | **17** | 20 |
| `SPLIT_SHANK_PARALLEL` | 304.465 | 1 | 1 | 5 |
| `SPLIT_SHANK_TAPERED` | 293.019 | 1 | 1 | 5 |
| `BYPASS_CROSSOVER` | 177.413 | 1 | 1 | 4 |
| `SIGNET_FLAT_TABLE` | 573.036 | 1 | 1 | 5 |

**Read the three-stone and halo rows carefully.** Their metal is *exactly* the
baseline's, to the last digit, because those families add **stones and no
metal**. That is the honest recorded boundary rather than a measurement error —
their difference from the baseline is the stone count, which is what the tests
assert for them.

## What executes

| Capability | Evidence |
| --- | --- |
| Resolution of all 13 variants | `resolve_ring_family()`; the resolver self-checks every derived path against the dependency table |
| Derivation into real JDL | 1–6 paths per variant, each with the source parameters it was computed from |
| Cathedral shoulders | 2 arches, one connected solid, 64.847 mm³, rising 3.5 mm above the band |
| Split-rail shoulders | 4 arches, one connected solid |
| Split shank | 2 rails, **one** connected solid, no metal in the axial gap at the top, 9.778 mm³ at the bottom bridge |
| Tapered split shank | band 189.431 mm³ against the parallel variant's 202.048 mm³ |
| Bypass | **one** open rail over 420°, one connected solid, metal on both axial sides at the crossing and none at the centre |
| Signet body | one connected solid with a flat rectangular table |
| Head modulation | basket 53.305 / 83.156 / 116.738 mm³ for low-profile / classic / elevated |
| Side stones | 3 stone solids; graduated sides are measurably smaller than symmetric ones |
| Halos | 17 / 39 / 17 stone solids, the radius derived from the centre stone's own half width |
| Pavé shoulders | composed onto the Pavé Engine, which builds the retention metal |
| Inspection facts | 14 new `FactType` members, all recorded on a real report |
| Forge rules | 5 `JM-RINGFAM-*` rules; 2 mirrored to `shared/validation/` |
| Designer | `jewelry.style` and `ringFamily.variant` proposable; 40 recognised terms |
| Studio | `RingFamilySection.tsx`, showing only the parameters the chosen variant reads |

## What does NOT execute

Stated plainly, because a boundary presented as a detail is a boundary hidden.

| Not built | Why |
| --- | --- |
| **Metal that holds halo stones** | Sprint 25's recorded boundary, unchanged. The halo stones are real solids and nothing retains them. This is why the `halo` family is PARTIAL. |
| **Any engraving, relief or texture** | No pattern representation exists anywhere in the pipeline. The signet table is flat and rectangular, which is why the `signet` family is PARTIAL, and why `SIGNET_ENGRAVED` is reserved. |
| **A non-rectangular signet table** | Would need the table's outline to come from the Stone System's outline machinery, whose contract is currently a *stone's* girdle. `SIGNET_OVAL_TABLE` is reserved. |
| **A swept solid along a 3D spline** | The shared prerequisite for `SOLITAIRE_TRELLIS`, `SPLIT_SHANK_SCULPTED` and `BYPASS_TWIST`. Every current construction is a revolve, a ruled loft, or a boolean of them. |
| **A stone-less ring** | `stone_reference` and `basket_support` are required components. `plain_band` is reserved, and changing the required set is an ADR condition. |
| **A 360° pavé field** | The Pavé Engine's containment policy clips a field at the host's declared extent rather than wrapping it. `eternity` is reserved on this. |
| **Any structural or manufacturing claim** | No force, no stress, no castability, no retention. Every variant is `NOT_REVIEWED`. |

## The two construction limits, and what they are not

Both are **arithmetic**. Neither says anything about how a piece of jewelry
ought to be proportioned.

### The rail separation

Two rails **share** the band's width, so what is left between them is
`(band.width − separation) / 2`. A separation at or above the width leaves
none, and `JM-RINGFAM-004` refuses it. Subtraction, not a judgment about
thinness: a 1.5 mm band with a 1.2 mm separation leaves a 0.15 mm rail, which is
thin and is **not** refused, because nothing here judges thinness.

### The shoulder arch span — `MAX_ARCH_SPAN_DEG = 90.0`

The arch is a ruled loft from the band's own section at `u = span/360` up to a
section at the head's height at `u = 0`. Section rotation is
`angle_deg_for_u(u) = −90 + u × 360`, so the base section's rotation is
`−90 + span`: at `span = 90` it reaches 0°, the same orientation as the head's
section, and past that it rotates **beyond** it. A ruled loft between two
sections that have crossed turns back on itself.

**Found by measuring, and the cliff is sharp:**

| Span | Fused arches | Ring metal valid? |
| --- | --- | --- |
| 80° | 83.365 mm³ | yes |
| 88° | 84.600 mm³ | yes |
| **90°** | **84.651 mm³** | **yes** |
| 92° | 19.577 mm³ | **no** |
| 120° | 16.964 mm³ | no |

The individual arch still reports `isValid() == True` at 92° — **OCC's own
validity check does not catch the self-intersection** — which is why the limit
is a *precondition* checked before construction rather than a check on the
result. It is enforced in both layers: the schema refuses the value, and
`build_shoulders()` refuses the call. Neither clamps.

## The fuse invariant

A boolean fuse can **succeed and return nonsense**, which `_fuse_metal()`
assumed it could not until this sprint measured it. A bypass whose two passes
clear each other by ~0.07 mm produced a fuse that raised nothing, reported
`isValid() == True`, and returned **six solids of negative volume** — the six
prongs, inverted, with the band and the basket gone entirely — and emitted no
warning. `combined_metal_volume_mm3` was −60.904.

The result is now checked against the one invariant available without redoing
the boolean: **a union is never smaller than its largest input.** That is
arithmetic about unions, not a tolerance and not a jewelry threshold, so it
needs no invented number.

A result that fails it takes the same honest multi-solid compound fallback a
raised failure takes, with a warning naming the measurement
(ATLAS-GOV-006, ALCHEMIST-GOV-007). Verified: at 175° overlap the ring is now
223.496 mm³ across 8 solids with the warning present, every real component
intact, and no variant with a sound fuse is affected.

## Compatibility, measured

`341.44334316909976 mm³` — the default solitaire, unchanged, the same number
Sprints 19, 23 and 27 each preserved. Zero Golden baselines updated.

`effective_definition()` returns the **original document object** for it. The
baseline *does* derive `setting.basketHeight`, from the document's own value
times two factors of 1.0 — a real provenance record and a no-op write — so
identity is preserved by comparing each write's result rather than by counting
derivations.
