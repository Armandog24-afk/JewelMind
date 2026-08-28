---
id: JM-BIBLE-591
title: Setting Golden Strategy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-27
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SETTING-README
  - JM-BIBLE-580
related_documents:
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-514
  - JM-BIBLE-586
implementation_status: current
professional_validation: not_required
normative: true
---

# Setting Golden Strategy

## Two different outcomes, both correct

This Sprint produced the first **intentional** Golden baseline change in the programme, and the split between what changed and what did not is exactly the split the Sprint set out to achieve:

| Cases | Outcome |
|---|---|
| `SOL-001` … `SOL-012` (12 round-stone cases) | **PASS, zero baseline updates.** Mandatory (SETTING-GOV-017). |
| `SOL-013` … `SOL-018` (6 non-round cases) | **REGRESSION_DETECTED → reviewed → accepted.** Intentional. |
| `SET-001` … `SET-005` (5 new Setting cases) | New baselines. |

## Why the round cases had to be untouched

Round uses `RADIAL` placement, preserved character-for-character. All 12 round-stone cases verified with no baseline change, which is the strongest available evidence that the Setting System refactor changed architecture rather than geometry.

## Why the six non-round cases changed

Those baselines were generated in Sprint 18, when every shape used the width-derived radial circle. This Sprint replaced that with shape-aware `OUTLINE_CARDINAL` placement — which is the milestone's stated objective, so the change is intentional by definition.

The diff was reviewed before anything was accepted, and it is confined precisely to what the change should affect:

| Metric | Delta | Verdict |
|---|---|---|
| `components.prongs.volumeMm3` | `3.55e-15` | unchanged — same prongs |
| `components.prongs.boundingBox.sizeX` | `2.25e-07` | unchanged |
| `components.prongs.boundingBox.xmax` / `xmin` | `~2e-07` | unchanged |
| `components.prongs.boundingBox.sizeY` | **1.342** | **REGRESSION** — prongs moved |
| `components.prongs.boundingBox.ymax` / `ymin` | **0.671** | **REGRESSION** — prongs moved |

Prong volume identical, X extents identical, only Y extents moved. That is the signature of *the same prongs repositioned*, not of different prongs.

The supporting measurement, for the oval case: off-axis prongs sat **0.784 mm** from the stone outline under radial placement and sit **0.049 mm** from it now, while the on-axis prong is unchanged at the intended 0.165 mm girdle inset. The prongs went from floating clear of the stone to reaching it.

### The acceptance process actually followed

Per QUALITY-GOV-003/004 and brief section 57, baselines were **not** regenerated to make CI pass. The sanctioned path was used in full:

1. `verify-all` → 6 cases reported `REGRESSION_DETECTED`.
2. `generate-candidate` for each of the six.
3. `diff` reviewed for each — confirming volume/X unchanged, Y moved.
4. Independent measurement of prong-to-outline distance to confirm the change was an improvement rather than a drift.
5. `accept --reason "..."` with a real reason string recording the measurement.
6. Full `verify-all` re-run; transient `candidate.json` files removed.
7. Each case recorded in [`../appendices/golden-update-register.md`](../appendices/golden-update-register.md).

The reason string is stored on each snapshot and names the measured improvement, so a future reader can tell this was a reviewed change rather than an accommodation.

## The 5 new Setting cases

One per acceptance configuration (brief section 40), each a complete ring:

| Golden ID | Configuration | Known limitations |
|---|---|---|
| `SET-001-round-4-prong` | round, 4 prongs, RADIAL | none |
| `SET-002-round-6-prong` | round, 6 prongs, RADIAL | none |
| `SET-003-oval-prong` | oval 8 × 6, 6 prongs, OUTLINE_CARDINAL | EXPERIMENTAL placement |
| `SET-004-round-bezel` | round, bezel | preliminary wall values; no seat/bearing/cutter |
| `SET-005-oval-bezel` | oval 8 × 6, bezel | as above, plus the STEP-safety resampling |

`SET-001` and `SET-002` verify `PASS`; the other three `PASS_WITH_KNOWN_LIMITATIONS`, which is the correct status — the geometry is a valid accepted baseline *and* the recorded limitation is real.

`SET-001`/`SET-002` deliberately duplicate configurations the `SOL-*` cases already cover. That is not redundancy: they protect the prong geometry specifically *through the Setting System abstraction*, so a future refactor of `setting/` that broke round would fail a Setting-owned case rather than only a Stone-era one.

## What the Golden facts protect

Per brief section 41, and all already captured by the existing snapshot schema — no new snapshot fields were needed:

- setting type (via the component set: `prongs` vs `bezel`)
- stone shape (via `design.json`)
- generated component count and identity
- requested vs generated prong count (via component metadata)
- StoneReference role and production exclusion
- solid counts, volumes, bounding boxes
- connectivity
- artifact expectations (STEP/STL)

Existing comparison tolerances are used throughout. No manufacturing tolerance is introduced.

## Not professional approval

`baselineStatus: STABLE` means the geometry was generated from real code, independently reverified, and is now the reference for detecting unintended change. It carries no professional endorsement — see [`../17-geometry-quality/514-professional-validation-boundary.md`](../17-geometry-quality/514-professional-validation-boundary.md).

`SET-003`, `SET-004` and `SET-005` are simultaneously `STABLE` and `EXPERIMENTAL`/`NOT_REVIEWED`. Those are not in conflict: the first says the geometry is reproducible, the second says the setting around it is provisional and unreviewed.

## Suite status

All **23** goldens pass: 10 `PASS` (`SOL-001`–`SOL-008`, `SET-001`, `SET-002`) and 13 `PASS_WITH_KNOWN_LIMITATIONS`. The 5 new cases are in `fullSuite`; `fastSuite` is unchanged.
