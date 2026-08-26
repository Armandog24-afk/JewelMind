---
id: JM-BIBLE-QUALITY-README
title: Geometry Quality & Golden Models v1 — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-120
  - JM-BIBLE-INSPECTION-README
related_documents:
  - JM-BIBLE-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Geometry Quality & Golden Models v1 — Index

This is **Sprint 15** of the Technical Bible: **Geometry Quality & Golden Models v1**. Sprint 14 (Geometry Inspection) built real runtime measurement of geometric facts; this Sprint builds on top of that measurement to answer a different question — **has a code change silently altered JewelMind's geometry?** A Golden Model is a versioned JewelMind input plus its expected geometric facts, expected component relationships, and expected artifact invariants, captured from real generated geometry and compared against on every regeneration.

**Read this README, then [`500-quality-governance.md`](500-quality-governance.md), before changing anything in `backend/jewelmind/geometry_quality/` or `goldens/`.**

## A Golden Model is NOT

Professionally approved. Manufacturing-ready. Aesthetically ideal. A jewelry-industry standard. Physically tested. It is a **software regression reference** — see QUALITY-GOV-001 in [`500-quality-governance.md`](500-quality-governance.md) and [`514-professional-validation-boundary.md`](514-professional-validation-boundary.md).

## Where Geometry Quality sits

```
JDL
  ↓
FORGE (pre-generation)
  ↓
ALCHEMIST
  ↓
ATLAS (creates geometry)
  ↓
GEOMETRY INSPECTION      (Sprint 14 — measures geometric facts)
  ↓
GEOMETRY QUALITY         (this Sprint — compares facts against approved software baselines)
  ↓
REGRESSION DECISION       (PASS / REGRESSION_DETECTED / VERSION_REVIEW_REQUIRED / ...)
  ↓
VISION / FOUNDRY / PROFESSIONAL REVIEW
```

Atlas creates geometry. Geometry Inspection measures it. Geometry Quality compares it against a versioned baseline. Forge interprets domain rules. Professional Validation determines whether professional jewelry assumptions are justified. **These five responsibilities are never merged.**

## The core workflow

```
generate_snapshot(design.json)  →  GeometrySnapshot
compare_snapshot(golden, actual) →  GeometryDiff
verify_golden(golden_id)         →  QualityResult
verify_all_goldens()             →  list[QualityResult]
generate_candidate_baseline(id)  →  GoldenModel (CANDIDATE, never written to disk)
accept_candidate_baseline(...)   →  GoldenModel (STABLE, explicitly written — the ONLY write path)
```

No code path other than an explicit, human-invoked `accept` ever writes to an accepted Golden baseline file. See [`507-golden-update-policy.md`](507-golden-update-policy.md) and [`GOLDEN_NO_AUTO_UPDATE_TEST`](../appendices/geometry-quality-test-matrix.md).

## Reading order

1. [`500-quality-governance.md`](500-quality-governance.md) — 18 non-negotiable rules (QUALITY-GOV-001 through 018).
2. [`501-golden-model-contract.md`](501-golden-model-contract.md), [`502-golden-suite-selection.md`](502-golden-suite-selection.md), [`511-current-solitaire-golden-suite.md`](511-current-solitaire-golden-suite.md).
3. [`503-quality-signal-model.md`](503-quality-signal-model.md), [`504-regression-comparison-model.md`](504-regression-comparison-model.md), [`505-comparison-tolerance-policy.md`](505-comparison-tolerance-policy.md), [`508-geometry-diff-model.md`](508-geometry-diff-model.md).
4. [`506-golden-regression-harness.md`](506-golden-regression-harness.md), [`507-golden-update-policy.md`](507-golden-update-policy.md).
5. [`509-artifact-regression-model.md`](509-artifact-regression-model.md), [`510-version-fingerprint-policy.md`](510-version-fingerprint-policy.md), [`515-performance-baseline-model.md`](515-performance-baseline-model.md).
6. [`512-ci-regression-gating.md`](512-ci-regression-gating.md), [`513-regression-failure-triage.md`](513-regression-failure-triage.md).
7. [`514-professional-validation-boundary.md`](514-professional-validation-boundary.md).
8. [`516-current-code-mapping-and-gaps.md`](516-current-code-mapping-and-gaps.md), [`517-open-geometry-quality-questions.md`](517-open-geometry-quality-questions.md).

## Appendices

[`golden-model-catalog.md`](../appendices/golden-model-catalog.md), [`geometry-quality-signal-catalog.md`](../appendices/geometry-quality-signal-catalog.md), [`geometry-regression-metric-catalog.md`](../appendices/geometry-regression-metric-catalog.md), [`golden-update-register.md`](../appendices/golden-update-register.md), [`geometry-quality-test-matrix.md`](../appendices/geometry-quality-test-matrix.md).

## Machine-readable specification

[`specs/geometry-quality/v1/`](../../../specs/geometry-quality/v1/README.md) holds 6 JSON Schemas and 5 test-vector files, all generated from the real `compare_snapshot()`/`generate_candidate_baseline()` code. The real Golden Suite itself lives at the repository root, [`goldens/solitaire-v1/`](../../../goldens/solitaire-v1/) — 9 cases, each a real generated `design.json` + `snapshot.json`, never hand-invented and never a committed STEP/STL binary.

## The single most important finding of this Sprint

**Cross-platform CAD-kernel floating-point drift is real, measured, and now has a place to live.** Sprint 14's own CI run already showed a ~1.3e-5 relative divergence between Windows and Linux OCCT builds on a near-tangent sliver intersection volume. This Sprint's `RELATIVE_COMPARISON_TOLERANCE` (1e-3) is set with a full two orders of magnitude of margin above that measured value — not guessed, not manufacturing-derived, purely a software-regression comparison tool (QUALITY-GOV-006). See [`505-comparison-tolerance-policy.md`](505-comparison-tolerance-policy.md).

## What was investigated, not invented

Every one of the 9 Golden Suite cases is a real, schema-valid variation of the default `JewelryDefinition` (prong count, band profile, ring size, band/stone/prong/basket dimensions, one warning-only-but-valid range) — never an invented "professional" parameter value. Every snapshot was generated by actually running `build_solitaire_ring()` → `inspect_model()`, then independently reverified against its own saved baseline before being accepted. See [`502-golden-suite-selection.md`](502-golden-suite-selection.md).

## Validation of this sprint

See [`SPRINT-15-VALIDATION-REPORT.md`](SPRINT-15-VALIDATION-REPORT.md) for the checks run against this section and the findings from that pass.
