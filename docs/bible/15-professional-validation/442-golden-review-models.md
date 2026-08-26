---
id: JM-BIBLE-442
title: Golden Review Models
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
  - JM-BIBLE-425
  - JM-BIBLE-441
implementation_status: planned
professional_validation: not_required
normative: false
---

# Golden Review Models

## Stable, deterministic review fixtures

Building on [`441-review-sampling-strategy.md`](441-review-sampling-strategy.md)'s matrix, a "golden review model" is one specific, named, deterministic `JewelryDefinition` intended to live under `examples/professional-review/solitaire/` as a real JSON fixture — the same JDL every reviewer session referencing that fixture would use, guaranteeing the same `definitionHash` and the same geometry every time (per [`425-review-case-model.md`](425-review-case-model.md)'s reproducibility requirement).

## Real current state: defined here, not yet materialized as files

`examples/professional-review/solitaire/` exists as a directory but currently contains **zero files** — verified directly. The fixtures below are defined conceptually in this document; producing the actual JSON files (by running `default_definition()`/a modified `JewelryDefinition` through the real schema and writing the result, exactly the discipline every other sprint's spec-generation followed) is planned but not yet done as of this Sprint's documentation pass. This document's `implementation_status` is marked `planned` for exactly this reason — the fixture set is designed, not yet built.

## The minimum fixture set

1. **default-six-prong** — the schema default in every field.
2. **four-prong** — `setting.prongCount: 4`, otherwise default.
3. **flat-band** — `band.profile: "flat"`, otherwise default.
4. **comfort-fit-band** — `band.profile: "comfort_fit"` (already the default, included explicitly for symmetry with flat-band as a named, addressable case).
5. **low-boundary-stone** — `stone.diameter: 2.0` (the schema minimum).
6. **high-boundary-stone** — `stone.diameter: 15.0` (the schema maximum).
7. **invalid-four-prong-large-stone** — `setting.prongCount: 4`, `stone.diameter: 8.1` — deliberately fails `JM-PRONG-003`; included specifically because seeing how JewelMind handles an invalid combination is itself informative for a reviewer, not despite being invalid.

## Never label a fixture "manufacturing approved"

A fixture is a reproducible starting point for a review session — it makes zero claim about its own validation status. Nothing in this document, in any generated fixture file, or in any review package generated from one of these fixtures may describe the fixture itself as approved, validated, or manufacturing-ready before an actual `ValidationRecord` exists for it.

## Cross-references

- [`425-review-case-model.md`](425-review-case-model.md) — the reproducibility contract these fixtures rely on.
- [`441-review-sampling-strategy.md`](441-review-sampling-strategy.md) — the sampling rationale behind this exact fixture set.
- [`451-validation-gap-analysis.md`](451-validation-gap-analysis.md) — tracks the "fixtures not yet materialized as files" gap.
