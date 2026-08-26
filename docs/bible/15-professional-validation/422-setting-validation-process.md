---
id: JM-BIBLE-422
title: Setting Validation Process
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
  - JM-BIBLE-420
  - JM-BIBLE-444
implementation_status: current
professional_validation: not_required
normative: false
---

# Setting Validation Process

This is the **highest-priority review area** for the current product (see [`444-current-solitaire-review-plan.md`](444-current-solitaire-review-plan.md), priority items 3–5). Prong and basket construction are where JewelMind's current geometry is most simplified relative to real bench practice, and where a professional's judgment matters most before any language of readiness is used.

## Real review questions

- prong geometry — shape, taper, thickness;
- prong position — placement relative to the stone and to each other;
- prong count behaviour — the current schema allows only 4 or 6 prongs (`JM-PRONG-001`, `backend/jewelmind/domain/schema.py`/`validation/engine.py`), and 4 prongs are blocked once `stone.diameter > 8mm` (`JM-PRONG-003`) — a reviewer should judge whether this exact 8mm threshold matches real practice, not just whether the software enforces *some* threshold;
- stone relationship — does the prong geometry actually appear to hold the stone reference in a plausible position;
- basket support — does the basket plausibly support the prongs and transition to the band;
- seat/bearing strategy — see the honest finding below;
- setting access — could a setter's tools plausibly reach the stone once assembled;
- stone insertion feasibility;
- prong finishing/bending expectations — what bench work would be needed after casting/printing before a stone could actually be set.

## What the current geometry actually builds (verified by reading the code)

`backend/jewelmind/geometry/components/prongs.py` and `basket.py` were read directly for this document: a search across both files for "seat" or "bearing" (case-insensitive) returns **zero matches**. No seat or bearing cut exists in the current prong or basket geometry builder — the prongs and basket are constructed as solid forms without a machined recess for the stone's girdle. This is a real, verified fact about the current implementation, not a guess.

This matches, word for word, what the real review-package generator already tells every reviewer — `backend/jewelmind/professional_validation/review_package.py`'s generated README states plainly:

> "Prong and basket geometry is deliberately simplified — this is an early parametric prototype, not a finished setting design."
> "No seat/bearing cutting strategy has been professionally reviewed."

## Never present this as production-ready before review

JewelMind must never describe the current setting geometry as production-ready, bench-ready, or manufacturing-ready in any user-facing copy, documentation, or generated artifact. Every review package's README and every review form's questions are written to actively invite a "this needs substantial rework" answer, not to seek approval — see [`426-review-package-contract.md`](426-review-package-contract.md) and the real fillable forms under `docs/professional-review/`.

## Reviewer role

`STONE_SETTER` for setting-feasibility questions; `GOLDSMITH_BENCH_JEWELER` for construction/finishing plausibility; `JEWELRY_CAD_DESIGNER` for topology and editability concerns specific to the prong/basket model. Multiple roles are genuinely relevant here — this is not a single-reviewer review area.

## Cross-references

- [`420-geometry-validation-process.md`](420-geometry-validation-process.md) — the general geometry-review dimensions this document specializes for settings.
- [`427-review-checklist-model.md`](427-review-checklist-model.md) — the stone-setter checklist category.
- `docs/professional-review/stone-setting-review-form.md` — the real fillable form for this review area.
