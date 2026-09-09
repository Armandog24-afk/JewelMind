---
id: JM-BIBLE-A103
title: "Appendix: Golden Update Register"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-500
related_documents:
  - JM-BIBLE-507
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Golden Update Register

Every accepted change to a Golden baseline, ever. Per QUALITY-GOV-018, an entry here is created at the same time a baseline is accepted via `geometry-quality accept --reason "..."` — never after the fact, never inferred from git history.

**No entry below claims professional approval.** `INITIAL_BASELINE` records that a baseline was created from real generated geometry and independently reverified — nothing more.

| Golden ID | Previous version | New version | Reason | Affected geometry | Related issue/ADR/RFC | Date |
|---|---|---|---|---|---|---|
| `SOL-001-default-solitaire` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) | Sprint 15 milestone | 2026-08-26 |
| `SOL-002-four-prong-comfort-fit` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) | Sprint 15 milestone | 2026-08-26 |
| `SOL-003-six-prong-flat` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) | Sprint 15 milestone | 2026-08-26 |
| `SOL-004-four-prong-flat` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) | Sprint 15 milestone | 2026-08-26 |
| `SOL-005-ring-size-variation` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) | Sprint 15 milestone | 2026-08-26 |
| `SOL-006-band-dimension-variation` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) | Sprint 15 milestone | 2026-08-26 |
| `SOL-007-stone-dimension-variation` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) | Sprint 15 milestone | 2026-08-26 |
| `SOL-008-prong-basket-dimension-variation` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) | Sprint 15 milestone | 2026-08-26 |
| `SOL-009-warning-only-large-stone-four-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) | Sprint 15 milestone | 2026-08-26 |
| `SOL-010-width-taper-solitaire` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — real width-taper geometry, comfort-fit profile, `bottomRatio=0.6` | Sprint 17 milestone | 2026-08-26 |
| `SOL-011-thickness-taper-solitaire` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — real thickness-taper geometry, comfort-fit profile, `bottomRatio=0.5` | Sprint 17 milestone | 2026-08-26 |
| `SOL-012-combined-taper-solitaire` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — real combined width+thickness taper, flat profile, `bottomRatio=0.7`/`0.6` | Sprint 17 milestone | 2026-08-26 |
| `SOL-013-oval-solitaire` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — real oval StoneReference, 8.0 × 6.0 mm | Sprint 18 milestone | 2026-08-26 |
| `SOL-014-pear-solitaire` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — real pear StoneReference (asymmetric), 9.0 × 6.0 mm | Sprint 18 milestone | 2026-08-26 |
| `SOL-015-emerald-solitaire` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — real emerald StoneReference (clipped corners), 8.0 × 6.0 mm | Sprint 18 milestone | 2026-08-26 |
| `SOL-016-cushion-solitaire` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — real cushion StoneReference (rounded corners), 7.0 × 7.0 mm | Sprint 18 milestone | 2026-08-26 |
| `SOL-017-princess-solitaire` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — real princess StoneReference (rectangular), 6.5 × 6.5 mm | Sprint 18 milestone | 2026-08-26 |
| `SOL-018-marquise-solitaire` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — real marquise StoneReference (pointed lens), 10.0 × 5.0 mm | Sprint 18 milestone | 2026-08-26 |
| `SOL-013-oval-solitaire` | 1 | 2 | Shape-aware prong placement (see below) | `components.prongs.boundingBox.sizeY`/`ymax`/`ymin` only. Prong volume unchanged (Δ 3.55e-15); X extents unchanged. | Sprint 19 milestone | 2026-08-27 |
| `SOL-014-pear-solitaire` | 1 | 2 | Shape-aware prong placement (see below) | As above | Sprint 19 milestone | 2026-08-27 |
| `SOL-015-emerald-solitaire` | 1 | 2 | Shape-aware prong placement (see below) | As above | Sprint 19 milestone | 2026-08-27 |
| `SOL-016-cushion-solitaire` | 1 | 2 | Shape-aware prong placement (see below) | As above | Sprint 19 milestone | 2026-08-27 |
| `SOL-017-princess-solitaire` | 1 | 2 | Shape-aware prong placement (see below) | As above | Sprint 19 milestone | 2026-08-27 |
| `SOL-018-marquise-solitaire` | 1 | 2 | Shape-aware prong placement (see below) | As above | Sprint 19 milestone | 2026-08-27 |
| `SET-001-round-4-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — round, 4 prongs, RADIAL placement | Sprint 19 milestone | 2026-08-27 |
| `SET-002-round-6-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — round, 6 prongs, RADIAL placement | Sprint 19 milestone | 2026-08-27 |
| `SET-003-oval-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — oval 8 × 6, OUTLINE_CARDINAL placement | Sprint 19 milestone | 2026-08-27 |
| `SET-004-round-bezel` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — round, real parametric bezel wall | Sprint 19 milestone | 2026-08-27 |
| `SET-005-oval-bezel` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — oval 8 × 6, bezel with STEP-safety resampling | Sprint 19 milestone | 2026-08-27 |
| `STV2-001-heart-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — heart 8 x 8, 6 prongs. Records a PRE-EXISTING, size-driven head-attachment finding | Sprint 20 milestone | 2026-09-02 |
| `STV2-002-radiant-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — radiant 8 x 6, clipped-corner rectangle | Sprint 20 milestone | 2026-09-02 |
| `STV2-003-asscher-bezel` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — asscher 6.5 x 6.5 with a bezel wall | Sprint 20 milestone | 2026-09-02 |
| `STV2-004-trillion-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — trillion 7 x 7, bowed-side triangle | Sprint 20 milestone | 2026-09-02 |
| `STV2-005-baguette-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — baguette 6 x 3, plain rectangle | Sprint 20 milestone | 2026-09-02 |
| `STV2-006-tapered-baguette-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — tapered baguette 6 x 3.2, narrowWidth 2.0 | Sprint 20 milestone | 2026-09-02 |
| `STV2-007-triangle-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — triangle 7 x 7, straight sides | Sprint 20 milestone | 2026-09-02 |
| `STV2-008-trapezoid-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — trapezoid 4 x 6, narrowWidth 3.6 | Sprint 20 milestone | 2026-09-02 |
| `STV2-009-lozenge-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — lozenge 8 x 4, rhombus | Sprint 20 milestone | 2026-09-02 |
| `STV2-010-hexagon-bezel` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — elongated hexagon 8 x 6 with a bezel wall | Sprint 20 milestone | 2026-09-02 |
| `STV2-011-kite-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — kite 9 x 5, longitudinally asymmetric | Sprint 20 milestone | 2026-09-02 |
| `STV2-012-shield-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — shield 8 x 6, seven-vertex polygon | Sprint 20 milestone | 2026-09-02 |
| `STV2-013-half-moon-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — half moon 6 x 6, chord plus elliptical arc | Sprint 20 milestone | 2026-09-02 |
| `STV2-014-oval-cabochon-bezel` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — oval 8 x 6 with a CABOCHON_REFERENCE profile | Sprint 20 milestone | 2026-09-02 |
| `STV2-015-custom-outline-bezel` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — CUSTOM_OUTLINE source through the generic bezel interface | Sprint 20 milestone | 2026-09-02 |
| `STV2-016-measured-oval-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — MEASURED source, MEASURED_DIMENSION_REFERENCE geometry | Sprint 20 milestone | 2026-09-02 |
| `FAM-001-three-stone-symmetric` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — 3 stone components, centre plus two mirrored sides at 0.6 scale via the arrangement MIRROR pattern | Sprint 24 milestone | 2026-09-07 |
| `FAM-002-three-stone-mixed-gems` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — 3 stone components, explicit placement, per-member scales 0.55/0.45, three declared gems | Sprint 24 milestone | 2026-09-07 |
| `FAM-003-toi-et-moi-diagonal` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — 2 equal stone components on a 30° axis, placed by point reflection | Sprint 24 milestone | 2026-09-07 |
| `FAM-004-cluster-eight` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — 9 stone components, closed-form ring arithmetic, memberScale 0.35 | Sprint 24 milestone | 2026-09-07 |
| `FAM-005-center-with-accents` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — 7 stone components, accentScale 0.3 reaching geometry | Sprint 24 milestone | 2026-09-07 |
| `HALO-001-single-halo` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — 17 stone components, one 3.4mm ring of 16 at 0.22 scale | Sprint 25 milestone | 2026-09-07 |
| `HALO-002-double-halo` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — 33 stone components, two independently parameterized rings (0.22 and 0.16 scale) | Sprint 25 milestone | 2026-09-07 |
| `HALO-003-hidden-halo` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — 13 stone components, ring offset −1.4mm below the centre plane | Sprint 25 milestone | 2026-09-07 |
| `HALO-004-three-stone-with-halo` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — 17 stone components; a family's MIRROR pattern and a halo in one document | Sprint 25 milestone | 2026-09-07 |
| `HALO-005-halo-around-toi-et-moi` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — 20 stone components, origin-anchored 6.0mm ring around a pair | Sprint 25 milestone | 2026-09-07 |
| `PAVE-001-shank-single-row` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — 24 stone components, shared-bead retention, recessed band | Sprint 26 milestone | 2026-09-08 |
| `PAVE-002-shank-staggered` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — 41 stone components in two staggered rows | Sprint 26 milestone | 2026-09-08 |
| `PAVE-003-microsetting` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — a stated 14x2 structure with micro-prong retention | Sprint 26 milestone | 2026-09-08 |
| `PAVE-004-head-plane-gallery` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — 16 stones on the planar head host, individual beads, no recess | Sprint 26 milestone | 2026-09-08 |
| `PAVE-005-three-stone-with-pave` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — a family and a pavé in one document | Sprint 26 milestone | 2026-09-08 |
| `ESM-001-channel-set-solitaire` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — a real `channel_walls` component, 109.760 mm³, one solid: two 0.8mm walls 5.0mm apart over a 9.0mm run with closed ends | Sprint 27 milestone / ADR-013 | 2026-09-09 |
| `ESM-002-bar-set-solitaire` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — a real `bars` component, 66.150 mm³, three solids at a 3.6mm pitch | Sprint 27 milestone / ADR-013 | 2026-09-09 |
| `ESM-003-flush-gypsy-solitaire` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — a real `flush_collar` component, 229.758 mm³. `basket_support` records 79.372 rather than the untouched 83.156, which is the recess visible in the baseline | Sprint 27 milestone / ADR-013 | 2026-09-09 |
| `ESM-004-partial-bezel-solitaire` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — `bezel` at 20.632 mm³ in THREE solids: three 46° openings leave three arcs | Sprint 27 milestone / ADR-013 | 2026-09-09 |
| `ESM-005-open-gallery-head` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — `basket_support` at 54.190 rather than 83.156, in ONE solid: six windows removed real metal and the rims kept the head connected | Sprint 27 milestone / ADR-013 | 2026-09-09 |
| `ESM-006-tension-solitaire` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — a real `tension_supports` component, 43.158 mm³, two solids. `basket_support` records 79.372, the relief again visible | Sprint 27 milestone / ADR-013 | 2026-09-09 |
| `ESM-007-pave-shared-prong` | — | 1 | `INITIAL_BASELINE` | All facts (first creation) — 22 pavé stones with `pave_retention` in 46 solids rather than the 88 an individual field would need, which is the shared-corner topology measured | Sprint 27 milestone / ADR-013 | 2026-09-09 |

### Sprint 19: the six non-round prong-placement acceptances

The programme's **first intentional baseline change**. The `SOL-013`–`SOL-018` baselines were created
in Sprint 18, when every stone shape used the generic width-derived radial prong circle. Sprint 19
replaced that with shape-aware `OUTLINE_CARDINAL` placement — the milestone's stated objective — so
the six non-round cases changed by design.

The recorded `--reason` for all six:

> Sprint 19 Setting System v1: prong placement for non-round stones changed from the generic
> width-derived radial circle to shape-aware OUTLINE_CARDINAL placement. Prong count, diameter,
> height and volume are unchanged (volume delta ~3.6e-15); only the prong POSITIONS moved outward to
> follow the stone's own girdle outline. Measured improvement on this oval: off-axis prongs sat
> 0.784mm away from the outline under radial placement and sit 0.049mm from it now, while the on-axis
> prong is unchanged at the intended 0.165mm girdle inset. Intentional, reviewed geometry change —
> see docs/bible/21-setting/prong-placement-model.md.

Process followed in full (QUALITY-GOV-003/004): `verify-all` surfaced the regressions →
`generate-candidate` per case → `diff` reviewed per case → independent prong-to-outline measurement
confirmed the change was an improvement → `accept --reason` → full `verify-all` re-run → transient
`candidate.json` files removed. No baseline was regenerated to obtain green CI.

**All 12 round-stone cases (`SOL-001`–`SOL-012`) required zero updates**, which is the evidence that
the refactor changed architecture rather than geometry.

### Sprint 20: sixteen new Stone v2 cases, zero baseline updates

All 16 are `INITIAL_BASELINE` creations, not updates. **No existing baseline was
modified**, including all 23 pre-existing cases and the exact-equality guards
(`combined_metal_volume_mm3 == 341.44334316909976`, prong volume
`== 29.650351464580467`, round stone volume `== 58.22141924499569`).

Created through the sanctioned path: `design.json` written from a real validated
definition, registered in `manifest.json`, then
`generate_candidate_baseline()` -> `accept_candidate_baseline()` with an explicit
reason, transient `candidate.json` removed, and a full `verify-all` re-run.
Nothing was hand-authored.

The recorded `--reason` for all 16:

> Sprint 20 Stone System v2: INITIAL_BASELINE for a newly supported stone
> shape, profile or source. Created by running the real pipeline; no existing
> baseline was modified.

**`STV2-001-heart-prong` records a pre-existing finding rather than avoiding
it.** Its snapshot captures `productionIsFullyConnected: false` — the band sits
0.0681mm from `basket_support` and 0.1112mm from `prongs`, so the head floats
above the band. This is a function of the stone FOOTPRINT, not of the heart
shape: a `round` stone of diameter 8.0mm — a capability since Sprint 2 —
reproduces the identical distances, and a `princess 8 x 7.5` is already at
0.0378mm. The threshold sits near a 7.5mm footprint. Sprint 20 did not introduce
this; its wider shape coverage surfaced it. The baseline documents the real
geometry instead of sidestepping it by choosing a smaller heart.

**No Golden ring case exists for `pearl` or for imported stones**, because
neither can currently be set: a sphere has no girdle plane and imported geometry
has no derived outline, so both setting families refuse them and no ring can be
assembled. Their geometry is covered by unit tests and by real import vectors
instead. See
[`../22-stone-v2/stone-v2-golden-strategy.md`](../22-stone-v2/stone-v2-golden-strategy.md).

### Sprint 24: five new multi-stone family cases, zero baseline updates

All five are `INITIAL_BASELINE` creations. **No existing baseline was modified**
— all 39 pre-existing cases reverified unchanged, including the exact-equality
guards (`combined_metal_volume_mm3 == 341.44334316909976`, prong volume
`== 29.650351464580467`, round stone volume `== 58.22141924499569`). That is the
evidence for ARRANGE-GOV-013's requirement that a design declaring no family and
no arrangement generate byte-identical geometry to its pre-Sprint-22 self: the
new per-instance placement path is reached only when an arrangement exists, and
the identity-placement path returns the builder's own solid object.

Created through the sanctioned path: `design.json` written from a real validated
definition, registered in `manifest.json`, then `generate-candidate` → `diff`
(reviewed per case) → `accept --reason` with the per-case reason recorded in the
table above, transient `candidate.json` removed, and a full `verify-all` re-run.
Nothing was hand-authored.

**Every one of the five records the same real limitation**, in its own
`knownLimitations`:

> `SETTING_COVERAGE_PRIMARY_ONLY`: a stone solid is built for every family
> member, but a setting is built only for the primary instance. The additional
> stones are placed reference geometry with no metal holding them.

The baselines therefore lock in what actually exists — nine stone solids in a
cluster, one setting — rather than a shape the pipeline does not yet produce. An
accent-setting strategy is an RFC, identified explicitly in
[`../26-multi-stone-families/execution-boundary.md`](../26-multi-stone-families/execution-boundary.md)
rather than approximated here.

**The metal body is identical in all five cases** (band `250.991683`, head
`83.155758`, prongs `29.650351`, one fully-connected production group), which is
the geometric proof that additional stone references never reach a metal fuse
(LAW-006, ATLAS-GOV-011).

### Sprint 25: five new halo cases, zero baseline updates

All five are `INITIAL_BASELINE` creations. **No existing baseline was modified**
— all 44 pre-existing cases reverified unchanged, including the exact-equality
guards (`combined_metal_volume_mm3 == 341.44334316909976`, prong volume
`== 29.650351464580467`, round stone volume `== 58.22141924499569`).

That matters more than usual this sprint, because Sprint 25 **extracted** the
radial ring arithmetic out of the resolver and the family compiler into one
shared `arrangement/radial.py`. Float addition is not associative, so a
re-expressed loop would have moved every ring stone by ~1e-14 and shown up as a
diff on the five Sprint 24 `FAM-*` cases. It did not: the extraction is
expression-for-expression identical, and the unchanged `FAM-*` baselines are the
evidence.

Created through the sanctioned path: `design.json` written from a real validated
definition, registered in `manifest.json`, then `generate-candidate` → `diff`
(reviewed per case) → `accept --reason` with the per-case reason recorded in the
table above, transient `candidate.json` removed, and a full `verify-all` re-run.
Nothing was hand-authored.

**Every one of the five records the same real limitation**, in its own
`knownLimitations`:

> `HALO_METAL_ABSENT`: a stone solid is built for every halo stone, but no metal
> is generated to hold them. A setting is built only for the primary stone; the
> halo stones are placed reference geometry.

**The metal body is identical in all five cases** (band `250.991683`, head
`83.155758`, prongs `29.650351`, one fully-connected production group), which is
the geometric proof that thirty-three additional stone references never reach a
metal fuse (LAW-006, ATLAS-GOV-011).

**The scales are verifiable arithmetic, not recorded opinion.** Volume scales
with the cube of a uniform scale: `HALO-001`'s ring stones measure `0.619942` =
`58.221419 × 0.22³`, `HALO-002`'s outer ring `0.238475` = `58.221419 × 0.16³`,
and `HALO-004`'s side stones `9.686589` = `58.221419 × 0.55³`. A per-ring scale
that never reached the solid would have produced identical stones and still
passed a component count.

### Sprint 26: five new pavé cases, zero baseline updates

All five are `INITIAL_BASELINE` creations. **No existing baseline was
modified** — all 49 pre-existing cases reverified unchanged, including the
exact-equality guards (`combined_metal_volume_mm3 == 341.44334316909976`, prong
volume `== 29.650351464580467`, round stone volume `== 58.22141924499569`).

That matters more than usual this sprint, because Sprint 26 added two fields to
`InstanceTransform` — a real axis tilt (ADR-011). Both default to zero and take
the placer's identity path, so every existing instance's solid is returned
untouched. The unchanged `FAM-*` and `HALO-*` baselines are the evidence.

Created through the sanctioned path: `design.json` written from a real validated
definition, registered in `manifest.json`, then `generate-candidate` → `diff`
(reviewed per case) → `accept --reason` with the per-case reason recorded in the
table above, transient `candidate.json` removed, and a full `verify-all` re-run.
Nothing was hand-authored.

**These are the first Golden cases in the programme that record real setting
geometry.** Every one carries a `pave_retention` production component with a
non-zero volume, and every one reports four production components in a single
fully-connected group — which is the geometric proof that retention metal joins
the body rather than resting on it.

**The recess is visible in the baselines.** `PAVE-001`/`002`/`003` record a band
volume below the untouched `250.991683` (`249.38985`, `249.22781`, `250.27171`
respectively); `PAVE-004`/`005`, which request no recess, record exactly
`250.991683`. A recess that removed nothing would be indistinguishable from one
that was never applied, and this is what makes the difference checkable.

**Every one records the same professional limitation** in its own
`knownLimitations`:

> `PAVE_AWAITING_PROFESSIONAL_REVIEW`: every pitch, bead radius, seat depth and
> stone scale in this field is a construction parameter. No pavé dimension in
> JewelMind has been reviewed by a qualified jewelry professional, and this
> baseline records generated geometry rather than a manufacturing standard.

## Sprint 27 — Extended Setting Modes v1 (`ESM-001`–`ESM-007`)

**Seven NEW cases, and zero existing baselines modified.** That second half is
the point: `BEZEL_FULL`, `BASKET` and `ROUND_PRONG` reproduce their previous
constructions exactly, so a default prong solitaire's metal volume is still
`341.44334316909976 mm³` and all 54 pre-existing baselines verified unchanged.

**One case per real capability, never one per number.** Each of the seven locks
in something this sprint made executable for the first time — a channel wall
pair, a bar row, a gypsy collar with its recess, a partial bezel's arcs, a
pierced gallery, opposed tension supports, and shared micro-prong retention.

**Three findings are visible IN the baselines rather than only asserted:**

- The **recess removes real metal**. `ESM-003` and `ESM-006` record
  `basket_support` at `79.3716` where an untouched head is `83.1558`. A recess
  that removed nothing would be indistinguishable from one never applied.
- The **openings and windows remove real metal**. `ESM-004`'s bezel is
  `20.632 mm³` in three solids rather than one; `ESM-005`'s head is `54.190`
  rather than `83.156` and still ONE solid, which is the rim guarantee measured.
- **Sharing genuinely shares.** `ESM-007` carries 22 pavé stones and a
  `pave_retention` component of **46 solids**. An individual field would need
  88. That number is the only evidence that the shared-corner topology is real
  rather than a label.

**Every one records honest limitations** in its own `knownLimitations`:

> `EXTENDED_SETTING_MODES_AWAITING_PROFESSIONAL_REVIEW`: every dimension in this
> design is a software construction parameter. No minimum wall, minimum bar,
> collar thickness, clearance or settability judgment is asserted anywhere,
> because no sourced professional evidence for one exists in this project.

and, for the tension case specifically:

> `TENSION_STRUCTURAL_BEHAVIOUR_NOT_MODELLED`: the opposing supports are real
> solids and nothing computes the elastic response of the metal, the force they
> apply, or whether the stone would be retained under load or wear. This
> baseline guards the geometry and makes no functional claim. Professional
> review is required.

## Sprint 28 — Ring Families v2 (`RF-001`–`RF-007`)

**Seven NEW cases. Zero existing baselines modified.** `verify-all` reported all
61 goldens PASS before these were added and all 68 PASS after, and the default
solitaire's metal is still exactly `341.44334316909976 mm³` — the same number
Sprints 19, 23 and 27 each had to preserve.

That is the sprint's central compatibility claim, and it is what the register
exists to record: an additive schema change (`JewelryDefinition.ringFamily` plus
five `BandSpec` fields) moved every document's `definitionHash`, and moved no
geometry at all.

| Golden | What it locks in |
| --- | --- |
| `RF-001-solitaire-cathedral` | Two real shoulder arches — the FIRST geometry the shoulder has ever had. One connected solid rising above the band. |
| `RF-002-solitaire-elevated` | The head factor scales `setting.basketHeight`, which moves the stone, AND derives shoulder arches to reach it. |
| `RF-003-split-shank-parallel` | TWO rails, ONE connected solid, a real axial gap at the head, four shoulder arches. |
| `RF-004-split-shank-tapered` | The derived width taper is actually READ, and produces measurably less metal than the parallel variant. |
| `RF-005-bypass-crossover` | ONE open rail over 420°, ONE connected solid, ends passing rather than meeting. |
| `RF-006-signet-flat-table` | A real `signet_body` component with parametric identity, not metal fused anonymously into the band. |
| `RF-007-halo-hidden` | Delegation to the Halo System (16 halo stones) plus the raised head that makes room for them. |

**Each case guards a defect this sprint actually shipped and fixed.** They were
chosen for that reason rather than for coverage of the taxonomy:

- `RF-002` — `LOW_PROFILE`, `CLASSIC` and `ELEVATED` produced *identical*
  geometry at first, because all three had `headHeightFactor = 1.0` and the
  variant contributed nothing of its own.
- `RF-003` — both rails came out coincident, because
  `Workplane.translate()` before `.revolve()` silently loses the offset. The
  fused volume was exactly one rail's.
- `RF-004` — the variant derived `band.widthTaper` and the architecture builder
  *ignored* it, so the tapered and parallel variants were byte-identical. A
  silently ignored derived value.
- `RF-005` — built as two axially separated arcs, a bypass came out as TWO
  disconnected solids.

No case was added for a variant whose only difference is a scaled parameter: a
baseline recording the same components with a different volume would add
maintenance without adding coverage.

**Every one records honest limitations** in its own `knownLimitations`:

> `RING_FAMILIES_AWAITING_PROFESSIONAL_REVIEW`: every dimension in this design
> is a software construction parameter. No rail width, shoulder proportion,
> signet table thickness, crossing clearance or settability judgment is asserted
> anywhere, and no qualified jewelry professional has reviewed this geometry.
> The variant's capability status is `NOT_REVIEWED`.

and, for the two PARTIAL families specifically:

> `HALO_SETTING_METAL_ABSENT`: the halo stones are real geometry and NO METAL IS
> GENERATED TO HOLD THEM. Sprint 25's own recorded boundary, unchanged by
> Sprint 28.

> `SIGNET_TABLE_UNDECORATED`: the table is flat and rectangular. No engraving,
> relief or texture exists anywhere in JewelMind, which is why the signet family
> is PARTIAL and why `SIGNET_ENGRAVED` and `SIGNET_OVAL_TABLE` are reserved.

### One pre-existing gap closed while here

`manifest.json`'s `fullSuite` list had been quietly incomplete since Sprint 24:
every `FAM`, `HALO`, `PAVE` and `ESM` case was registered in `goldenIds` and
never added to `fullSuite`, so 22 of 68 entries were missing. Nothing in
`backend/jewelmind/` reads that list — `verify-all` iterates `goldenIds` — so
the drift had no runtime effect and no test caught it. Completed rather than
left half-updated, because adding only the seven Sprint 28 cases would have made
the file inconsistent in a new way.

## How a future entry gets added

1. Run `python -m jewelmind.geometry_quality.cli generate-candidate <golden_id>`.
2. Run `python -m jewelmind.geometry_quality.cli diff <golden_id>` and read the output.
3. Confirm the change is intentional (a real, reviewed geometry improvement — QUALITY-GOV-017), not a defect.
4. Run `python -m jewelmind.geometry_quality.cli accept <golden_id> --reason "..."`.
5. Add a row to this table with the real `--reason` text, the affected geometry (from the diff), and a link to the related issue/ADR/RFC if one exists.

## Cross-references

- [`507-golden-update-policy.md`](../17-geometry-quality/507-golden-update-policy.md) — the full explicit-acceptance workflow.
