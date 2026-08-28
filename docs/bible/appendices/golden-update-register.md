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

## How a future entry gets added

1. Run `python -m jewelmind.geometry_quality.cli generate-candidate <golden_id>`.
2. Run `python -m jewelmind.geometry_quality.cli diff <golden_id>` and read the output.
3. Confirm the change is intentional (a real, reviewed geometry improvement — QUALITY-GOV-017), not a defect.
4. Run `python -m jewelmind.geometry_quality.cli accept <golden_id> --reason "..."`.
5. Add a row to this table with the real `--reason` text, the affected geometry (from the diff), and a link to the related issue/ADR/RFC if one exists.

## Cross-references

- [`507-golden-update-policy.md`](../17-geometry-quality/507-golden-update-policy.md) — the full explicit-acceptance workflow.
