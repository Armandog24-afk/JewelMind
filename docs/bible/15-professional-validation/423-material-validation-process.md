---
id: JM-BIBLE-423
title: Material Validation Process
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
  - JM-BIBLE-421
implementation_status: current
professional_validation: not_required
normative: false
---

# Material Validation Process

## Material is currently metadata/visual context only

`backend/jewelmind/domain/schema.py::MetalType` has 5 values: `yellow_gold_18k`, `white_gold_18k`, `rose_gold_18k`, `platinum`, `silver`. A direct search across `backend/jewelmind/validation/engine.py` and every file in `backend/jewelmind/geometry/` for `metal ==` (or any other metal-conditional branch) returns **zero matches**. No Forge rule and no geometry builder currently produces a different result depending on which metal is selected — `material.metal` today drives only the frontend's visual material preset (`frontend/src/vision/materials.ts`, Sprint 8/Vision) and the technical specification's reported value, never a dimension, a rule threshold, or a geometry decision.

## No physical constants exist

A search across the entire `backend/jewelmind/` tree for `density` returns zero matches. No density value, no specific-gravity constant, and no metal-to-metal structural difference is encoded anywhere in this codebase.

## Future material-validation review areas (none reviewed yet)

- density datasets (needed if JewelMind ever computes an estimated weight per metal);
- geometry rules that should differ by metal (e.g. a minimum prong thickness that is metal-specific — none exists today, every rule applies identically regardless of `material.metal`);
- manufacturing profiles (a given metal may suit one manufacturing method better than another — not modeled today);
- finishing allowances;
- structural differences between metals that would change what geometry is safe (platinum and 18k gold do not behave identically at the same wall thickness — this is exactly the kind of assumption that must come from a real metallurgist/goldsmith, never be invented here).

## Do not add densities or physical constants without sourced data

This is an explicit rule, not a suggestion: no future change may add a metal-specific numeric constant to `backend/jewelmind/domain/schema.py`, `backend/jewelmind/validation/engine.py`, or any geometry builder without a real, cited source — and per PROVAL-GOV-006/007, "the number sounds physically reasonable" is not a source; a real `ValidationRecord` backed by `REFERENCE_DOCUMENT` or `PROFESSIONAL_EXPERIENCE` evidence (see [`417-review-evidence-model.md`](417-review-evidence-model.md)) is.

## Reviewer role

`GOLDSMITH_BENCH_JEWELER` or `CASTING_SPECIALIST` for practical material-behavior questions; `GEMOLOGIST` is not the right role here (gemology concerns the stone, not the metal) — a reminder that role-to-review-area matching (PROVAL-GOV-004) is not automatic even among adjacent-sounding specialties.

## Cross-references

- [`421-manufacturing-validation-process.md`](421-manufacturing-validation-process.md) — the closely related manufacturing-method review area.
- [`412-validation-object-model.md`](412-validation-object-model.md) — `MATERIAL_PROFILE` as a distinct future validation object type.
