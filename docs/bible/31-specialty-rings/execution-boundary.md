---
id: JM-BIBLE-SPECIALTY-EXECUTION-BOUNDARY
title: "Specialty Rings — execution boundary"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-12
source_of_truth: true
depends_on:
  - JM-BIBLE-SPECIALTY-README
related_documents:
  - JM-BIBLE-SPECIALTY-GOVERNANCE
  - JM-BIBLE-RINGFAM-EXECUTION-BOUNDARY
implementation_status: current
---

# Specialty Rings — execution boundary

Exactly what runs, exactly what does not, every number measured rather than
claimed. A capability is CURRENT only if the runtime produces it.

## Measured geometry, per specialty variant

Built by `build_solitaire_ring()` against the real default document. Volumes are
the CAD kernel's own, in mm³. **These are software measurements, not
manufacturing figures, and nothing here is professionally validated.**

| Variant | Combined metal | Stone components | Total components | Retention solids |
| --- | --- | --- | --- | --- |
| `ETERNITY_FULL` | **343.377** | 44 | 48 | **134** |
| `ETERNITY_HALF` | **341.728** | 13 | 17 | **48** |
| `CLUSTER_ROUND` | 341.443 | 9 | 12 | **0** |
| `TOI_ET_MOI_BYPASS` | 341.443 | 2 | 5 | **0** |

**Read the last two rows carefully.** Their metal is *exactly* the baseline's
341.443, to the last digit, because they add **stones and no metal**. That
equality IS the PARTIAL boundary, not a measurement error. The eternity rows
exceed the baseline precisely because the Pavé Engine builds real retention.

## The parametric claim, measured

| Input changed | Measured consequence |
| --- | --- |
| finger size 12 → 24 (`ETERNITY_FULL`) | **40 → 48 set stones**, 158 → 188 beads |
| pitch 2.4 → 1.2 mm (`ETERNITY_FULL`) | fewer → more stones, the count following the pitch |
| count 8 → 16 (`ETERNITY_HALF`) | 8 → 16 stones, 32 → 64 beads |
| spacing 1.6 → 1.2 mm at 16 stones | **64 → 34 beads** — the corners genuinely share |
| retention `BEAD` → `NONE` | 48 → **0** retention solids; the stones remain |
| cluster radius 3.0 → 5.5 mm | stones measured at **exactly 3.000 → 5.500 mm** |
| cluster count 6 → 12 | 7 → 13 stone components |
| cluster scale 0.3 → 0.7 | accent volume **1.572 → 19.970 mm³** |
| toi-et-moi second scale 1.0 → 0.5 | second stone **58.221 → 7.278 mm³**, first unchanged |
| toi-et-moi separation 3.0 → 8.0 mm | centre distance measured **3.000 → 8.000 mm** |
| toi-et-moi angle 0° → 90° | the pair rotates from the X axis onto the Y axis |

The finger-size row is the strongest evidence in the sprint: a full eternity
states a *pitch*, so the stone count follows the band's own circumference. A
stored preset cannot do that.

## What executes

| Capability | Evidence |
| --- | --- |
| Resolution of all 4 specialty variants | `resolve_ring_family()`, the same single resolution point |
| Derivation into real JDL | `pave` for eternity; `family.familyType` + `family.params` (+ `family.members`) for the others |
| A full stone-set band | 43 set stones evenly wrapped, largest angular gap 5.8° |
| A half stone-set band | an explicit count, leaving a measured 176.8° unadorned region |
| Real retention metal | 134 / 48 bead solids; `SHARED_BEAD` and `MICRO_PRONG` also build |
| A cluster topology | count, radius and scale, every position from the arrangement resolver |
| Two principal stones | two separate Stone Instances, independently sized, exactly placed |
| Composition | gem identity, non-round stones, band profile, setting type — all verified |
| Inspection | every variant PASS/WARNING, facts naming the specialty family |
| Studio | family, variant and only the parameters the variant reads |
| Designer / Conversation | 8 new recognised terms, derived from the registry |

## What does NOT execute

Stated plainly, because a boundary presented as a detail is a boundary hidden.

| Not built | Why |
| --- | --- |
| **Metal holding a cluster's accent stones** | The Multi-Stone Family layer's `settingGeometry` is `false` for every family. Sprint 24's recorded boundary. This is why `cluster` is PARTIAL. |
| **Metal holding a toi-et-moi's second stone** | The same. |
| **Two different CUTS in one toi-et-moi** | A `FamilyMember` carries no shape; both stones are occurrences of the document's one `stone`. Per-member stone specifications is a Sprint 24 RFC. |
| **A stone-less eternity band** | `REQUIRED_COMPONENT_NAMES` includes `stone_reference` and `basket_support`, so every specialty ring still carries a centre stone and head. The same blocker `plain_band` records. |
| **A channel-set band** | `setting/channel.py` builds straight prisms in the stone's frame; it cannot follow the band's curve. |
| **A stacking band** | The stone-less blocker again — the same capability as `plain_band`. |
| **A tension-style family** | The `tension` setting family already builds that geometry; a family would be a second name. |
| **Any structural or manufacturing claim** | Every variant `NOT_REVIEWED`. |

## A correction to the Sprint 28 record

Sprint 28 reserved `eternity` on this reason:

> "The pavé engine's containment policy clips a field at the host's declared
> extent rather than wrapping it, so a 360-degree field is not expressible yet."

**That was false when written.** `PaveSpec.angularSpanDeg` is bounded `le=360.0`
and `pave/compile.py` carries an explicit closed-ring branch at `span >= 360.0`.
Measured before Sprint 29 wrote any code: **68 stones, largest angular gap 5.8°,
134 bead solids, no warnings.**

It is recorded here rather than deleted because the Bible's fundamental rule is
to report a contradiction between code and documentation, never to make one
disappear. The lesson is the sprint's own method: the reservation was written
from reading the containment policy's *description*, and one measurement would
have contradicted it.

## Software limits, and what they are not

`MAX_PAVE_STONES_PER_BAND = 200` and `MAX_CLUSTER_STONES = 24` are **software
safety limits**. Neither says anything about how many stones a band or cluster
*should* carry. They exist so a malformed or hostile document cannot request an
unbounded lattice or arrangement expansion — the same reason `MAX_PAVE_STONES`
and `MAX_CLUSTER_COUNT` exist in their own layers — and both sit at or below the
limit the delegated engine already enforces, so this layer can never ask for
more than that engine accepts.
