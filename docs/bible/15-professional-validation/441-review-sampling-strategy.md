---
id: JM-BIBLE-441
title: Review Sampling Strategy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-442
implementation_status: current
professional_validation: not_required
normative: false
---

# Review Sampling Strategy

## One default ring is not enough

A single default solitaire exercises only one point in JewelMind's real supported parameter space. Real supported ranges, verified directly in `backend/jewelmind/domain/schema.py`: `band.width` 1.5–12mm, `stone.diameter` 2–15mm, `setting.prongCount` must be 4 or 6 (`JM-PRONG-001`), 4 prongs blocked when `stone.diameter > 8mm` (`JM-PRONG-003`), `band.profile` is `comfort_fit` or `flat`, `material.metal` has 5 values, `manufacturing.method` has 2 values. No value below is invented — every one is a real, currently-supported input.

## A representative sampling matrix

| Case | prongCount | band.profile | stone.diameter | material.metal | manufacturing.method | Why sampled |
|---|---|---|---|---|---|---|
| Default | 6 | comfort_fit | 6.5mm (default) | yellow_gold_18k | lost_wax_casting | Baseline — the model most users will actually see first. |
| Four-prong | 4 | comfort_fit | 6.5mm | yellow_gold_18k | lost_wax_casting | Exercises the other supported prong count. |
| Flat band | 6 | flat | 6.5mm | yellow_gold_18k | lost_wax_casting | Exercises the other supported band profile. |
| Low-boundary stone | 6 | comfort_fit | 2.0mm (schema minimum) | platinum | lost_wax_casting | Smallest supported stone — checks whether small-scale geometry stays plausible. |
| High-boundary stone | 6 | comfort_fit | 15.0mm (schema maximum) | platinum | lost_wax_casting | Largest supported stone — checks whether large-scale geometry stays plausible. |
| 8mm boundary, 6 prongs | 6 | comfort_fit | 8.0mm | white_gold_18k | lost_wax_casting | Exactly at the `JM-PRONG-003` threshold, on the still-permitted side. |
| 8mm boundary, 4 prongs (invalid) | 4 | comfort_fit | 8.1mm | white_gold_18k | lost_wax_casting | Deliberately just past the threshold — `JM-PRONG-003` blocks this; useful to show a reviewer exactly how JewelMind handles an invalid combination. |
| Resin-printing context | 6 | comfort_fit | 6.5mm | silver | direct_resin_printing | Exercises the other manufacturing-method context (`JM-MANUFACTURING-001`). |
| Alternate metal, narrow band | 4 | flat | 4.0mm | rose_gold_18k | lost_wax_casting | Combines a narrower band with the flat profile and a different metal for visual/metadata diversity. |

## The purpose is behavioral diversity, never threshold certification

Sampling a case at the 8mm boundary does not mean that boundary has been professionally validated — it means a reviewer looking at that case has something concrete, real, and representative of a real software decision point to react to. A `ValidationRecord` only ever exists once a real reviewer has actually looked at a real case and made a real decision (PROVAL-GOV-001) — this sampling matrix produces cases to show reviewers, not validation itself.

## Cross-references

- [`442-golden-review-models.md`](442-golden-review-models.md) — turning this matrix into stable, named fixtures.
- [`444-current-solitaire-review-plan.md`](444-current-solitaire-review-plan.md) — the practical review agenda these cases would support.
