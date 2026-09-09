---
id: JM-BIBLE-RINGFAM-COVERAGE-REVIEW
title: "Ring Families — taxonomy coverage review"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-09
source_of_truth: true
depends_on:
  - JM-BIBLE-RINGFAM-README
related_documents:
  - JM-BIBLE-RINGFAM-GOVERNANCE
  - JM-BIBLE-ESM-COVERAGE-REVIEW
implementation_status: current
---

# Ring Families — taxonomy coverage review

Brief §35. Which ring families a jeweler would name, which of them JewelMind
builds, and — for each one it does not — **what is actually missing**, not
"planned".

The distinction matters because a reserved name with a real reason is a
decision, and a reserved name with no reason is an omission wearing a label. A
reader must be able to tell which they are looking at.

## Built (13 variants across 6 families)

| Family | Variant | What makes it a structure rather than a name |
| --- | --- | --- |
| solitaire | `CLASSIC` | The baseline. Reproduces the pre-Sprint-28 solitaire exactly. |
| solitaire | `CATHEDRAL` | Two real shoulder arches — the first geometry the shoulder has ever had. |
| solitaire | `LOW_PROFILE` | Head factor 0.6: basket 53.305 mm³ against the classic's 83.156. |
| solitaire | `ELEVATED` | Head factor 1.45 **and** shoulder arches to reach the taller head. |
| three_stone | `SYMMETRIC` | 3 real stone solids, placed by the Stone Arrangement Engine. |
| three_stone | `GRADUATED` | The same delegation with measurably smaller side solids. |
| halo | `SINGLE` | 17 stone solids; the radius derived from the centre stone's own half width. |
| halo | `DOUBLE` | 39 stone solids, both rings measured from the centre stone. |
| halo | `HIDDEN` | 17 stones below the centre plane, plus a raised head (349.644 mm³) to make room. |
| split_shank | `PARALLEL` | A real shank architecture: 2 rails, one solid, no metal in the axial gap at the top. |
| split_shank | `TAPERED` | The same architecture with the Shank subsystem's own width taper: band 189.431 against 202.048. |
| bypass | `CROSSOVER` | **One** open rail over 420°, whose two ends pass each other. |
| signet | `FLAT_TABLE` | A real solid body with a table at the ring's top: 573.036 mm³ total. |

## Reserved, with the real reason

### Families

**`eternity`** — needs a pavé field whose host is the band's own outer surface
over **360 degrees**, plus a channel or bead retention that follows it. The
Pavé Engine's containment policy *clips* a field at the host's declared extent
rather than wrapping it, so a 360-degree field is not expressible. The missing
piece is a wrapping containment policy, not a ring family.

**`toi_et_moi`** — two equal stones side by side is **already** expressible as
the `TOI_ET_MOI` stone family (Sprint 24). A ring family of the same name would
be a second authority over the same placement, which is exactly what
`JM-FAMILY-001` refuses. It stays reserved so the name cannot be taken for
something else.

**`cluster`** — same reasoning: the stones are already the `CLUSTER` stone
family, composable onto any ring family. A separate ring family would duplicate
it for no capability gain.

**`plain_band`** — a ring with no stone requires the assembly to build no stone,
no setting and no head. `stone_reference` and `basket_support` are **required
components** in every current contract — the inspection required-set, every
preview manifest, every export list — so a stone-less ring changes the required
set. That is an ADR condition, not a family parameter.

### Variants

**`SOLITAIRE_TRELLIS`** — the arches are the reserved `TRELLIS` head
architecture (Sprint 27), which needs a verifiable swept solid along a 3D
spline. No builder exists.

**`SPLIT_SHANK_SCULPTED`** — rails following a sculpted 3D path rather than the
ring's own circle. Needs the same swept-solid primitive.

**`BYPASS_TWIST`** — a bypass whose rails twist about their own axis as they
travel. The current construction lofts sections that translate axially; adding a
per-section rotation about the rail's tangent is a different sweep and is not
yet verifiable.

**`SIGNET_ENGRAVED`** — an engraved table needs a **surface-decoration system**:
a relief or engraving is a cut driven by a 2D pattern, and no pattern
representation exists anywhere in the pipeline. Specialty decoration is
Sprint 29's territory.

**`SIGNET_OVAL_TABLE`** — needs the table's outline to come from the same
outline machinery the Stone System uses. Reusing it would be correct and is not
wired: `stone/outline.py` builds a **stone's** girdle, and giving it a second
caller for a metal table is a real change to that module's contract.

## The one prerequisite three reserved variants share

`SOLITAIRE_TRELLIS`, `SPLIT_SHANK_SCULPTED` and `BYPASS_TWIST` all wait on the
same thing: **a verified swept solid along a 3D spline**. Every construction in
JewelMind today is a revolve, a ruled loft, or a boolean of them.

That is worth stating as one item rather than three, because it is one piece of
work — and because this sprint's own findings are a warning about how it must be
approached. A ruled loft self-intersects past a quarter turn while OCC reports
the solid valid; a boolean fuse can succeed and return negative volumes without
raising. A swept-solid primitive needs the same kind of measured verification,
not a documentation claim.

## Families deliberately NOT reserved

Not every jeweler's term needs a name here. A few are absent on purpose:

- **"cocktail", "statement", "vintage", "art deco"** — these describe an
  aesthetic, not a parametric structure. Turning one into a set of dimensions
  requires the professional judgment this project has no evidence for, and it
  would be exactly the "subjective descriptor into arbitrary numbers" mapping
  the Design Intent layer exists to refuse.
- **"cathedral" as its own family** — it is a solitaire variant, because that is
  what it is: a solitaire whose shoulders rise. Making it a family would suggest
  a cathedral three-stone is a different thing, which it is not.
- **"pavé ring", "channel ring"** — these name a *setting technique* applied to
  a ring, and both are already real: the Pavé Engine and the `channel` setting
  family. A ring family per setting technique would multiply the taxonomy
  without adding a capability.

## What would make each PARTIAL family CURRENT

Stated so the next sprint has an unambiguous target rather than a status to
argue about.

**`halo` → CURRENT** requires **metal that holds the halo stones**. Nothing
else: the stones are already real geometry, at the right radii, derived from the
centre stone. This is Sprint 25's own recorded boundary and it has not moved.
The Pavé Engine's bead and micro-prong builders are the obvious starting point —
`setting/retention.py` already builds real retention metal — but a halo's
retention is not a pavé lattice, so it is an RFC rather than a wiring job.

**`signet` → CURRENT** requires a **surface-decoration system**, because a
signet's decoration is the point of one. A flat rectangular table is a real
signet body and an honest PARTIAL signet.
