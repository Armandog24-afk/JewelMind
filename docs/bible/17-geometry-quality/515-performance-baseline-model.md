---
id: JM-BIBLE-515
title: Performance Baseline Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-500
related_documents:
  - JM-BIBLE-484
implementation_status: current
professional_validation: not_required
normative: true
---

# Performance Baseline Model

## No new performance model was introduced this Sprint

Sprint 14 already owns a real, measured performance model for the inspection pipeline itself: [`16-geometry-inspection/484-inspection-performance-model.md`](../16-geometry-inspection/484-inspection-performance-model.md), backed by `InspectionPerformance` (`totalDurationMs`, `componentInspectionMs`, `distanceInspectionMs`, `intersectionInspectionMs`, `topologyInspectionMs`), all populated by real `time.perf_counter()` measurements inside `inspect_assembly()`/`inspect_model()`. Geometry Quality does not duplicate, replace, or reinterpret that model — see that document for the real measured ranges (e.g. ~350 ms–1 s total inspection overhead for the current 4-component solitaire) and the broad-phase distance-before-intersection optimization it documents.

`QualitySignalType` (`backend/jewelmind/geometry_quality/models.py`) does declare a `PERFORMANCE_OBSERVATION` literal value alongside `EXACT_INVARIANT`/`NUMERIC_REGRESSION`/`RELATIONSHIP_REGRESSION`/`TOPOLOGY_REGRESSION`/`ARTIFACT_REGRESSION`. This is a real enum member, honestly present in the type — but verified directly, **no code anywhere in `geometry_quality/` currently produces a signal of this type**. It exists as a named slot in the signal vocabulary for a future capability, not as something the current harness populates.

## What IS new this Sprint, stated honestly: a real, current gap

None of the Golden harness functions in `backend/jewelmind/geometry_quality/harness.py` — `verify_golden()`, `verify_all_goldens()`, `generate_candidate_baseline()`, `accept_candidate_baseline()` — record their own timing. This was verified by reading the full, real source of `harness.py` (126 lines): there is no `time.perf_counter()` call, no `datetime.now()` duration measurement, and no field on `QualityResult`/`GeometryDiff` for elapsed time anywhere in the module. `verify_golden()` calls `generate_snapshot()` (which itself calls `build_solitaire_ring()` then `inspect_model()`, both of which are timed at the *inspection* layer per `484-inspection-performance-model.md`) but does not capture or forward how long its own comparison (`compare_snapshot()`) or artifact-regression checks (`step_roundtrip_check()`/`stl_structure_check()`, when `check_artifacts=True`) took.

This is recorded here as a real, current gap — **not something to fix as part of this Sprint**. Per QUALITY-GOV-016's spirit (don't retrofit scope to hide a finding), the honest statement is: Geometry Quality has no timing data of its own today, only the inspection-layer timing it indirectly inherits by calling `inspect_model()`. This gap is also referenced from [`517-open-geometry-quality-questions.md`](517-open-geometry-quality-questions.md) as an open question for a future sprint, rather than being answered here.

## No brittle CI time limits exist or are planned

Consistent with [`512-ci-regression-gating.md`](512-ci-regression-gating.md), no wall-clock timeout or CI time budget exists for any Golden verification step, and none is proposed by this document. `484-inspection-performance-model.md`'s own posture — report real measured ranges, never invent a hard pass/fail time threshold for kernel-derived work — is the same posture this document takes for any future Geometry Quality timing, if it is ever added.

## Cross-references

- [`16-geometry-inspection/484-inspection-performance-model.md`](../16-geometry-inspection/484-inspection-performance-model.md) — the real, current performance model this document defers to entirely.
- [`512-ci-regression-gating.md`](512-ci-regression-gating.md) — why no CI time limit exists.
- [`517-open-geometry-quality-questions.md`](517-open-geometry-quality-questions.md) — whether harness-level timing should be added.
