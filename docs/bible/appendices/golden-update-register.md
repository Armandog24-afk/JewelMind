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

## How a future entry gets added

1. Run `python -m jewelmind.geometry_quality.cli generate-candidate <golden_id>`.
2. Run `python -m jewelmind.geometry_quality.cli diff <golden_id>` and read the output.
3. Confirm the change is intentional (a real, reviewed geometry improvement — QUALITY-GOV-017), not a defect.
4. Run `python -m jewelmind.geometry_quality.cli accept <golden_id> --reason "..."`.
5. Add a row to this table with the real `--reason` text, the affected geometry (from the diff), and a link to the related issue/ADR/RFC if one exists.

## Cross-references

- [`507-golden-update-policy.md`](../17-geometry-quality/507-golden-update-policy.md) — the full explicit-acceptance workflow.
