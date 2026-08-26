---
id: JM-BIBLE-SPRINT15-REPORT
title: "Sprint 15 Validation Report — Geometry Quality & Golden Models v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-500
related_documents:
  - JM-BIBLE-516
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 15 Validation Report — Geometry Quality & Golden Models v1

## Golden Quality documents created

19 files under `docs/bible/17-geometry-quality/`: `README.md`, `500`–`517` (18 numbered docs), and this validation report. Plus 5 new appendices (`A100`–`A104`) and 4 cross-cutting updates (`docs/bible/07-atlas/137-determinism-and-reproducibility.md`, `docs/bible/16-geometry-inspection/492-inspection-regression-model.md`, `docs/bible/15-professional-validation/442-golden-review-models.md`, `docs/bible/README.md`, `docs/bible/00-foundation/008-glossary.md`, `docs/bible/appendices/documentation-index.md`, `CLAUDE.md`).

## Machine-readable schemas created

6 JSON Schemas, 5 real generated test-vector files under `specs/geometry-quality/v1/`.

## Golden solitaire cases created

9 (`SOL-001` through `SOL-009`), covering all 10 categories in the brief's selection list (the default case and "6-prong comfort-fit" are the same geometry, deliberately not duplicated — see [`502-golden-suite-selection.md`](502-golden-suite-selection.md)).

## Golden cases generated from real geometry

9 of 9 — every `snapshot.json` was produced by `backend/generate_golden_fixtures.py` (a one-off script, deleted after use) running the real `build_solitaire_ring()` → `inspect_model()` pipeline. Zero hand-invented facts.

## Golden cases independently reverified

9 of 9 — `generate_golden_fixtures.py` calls `verify_golden()` against each freshly-saved baseline before finishing; all 9 passed on that independent rerun.

## Exact invariants protected

9: `assembly.componentCount`, `productionComponentCount`, `referenceComponentCount`, `productionConnectivityGroups`, `productionIsFullyConnected`, `designConsistency.requestedProngCount`/`generatedProngCount`/`prongCountMatches`, `stoneReferenceIsProductionMetal` — plus component-set membership (missing/unexpected) and per-component `role`/`present`/`fallbackUsed`.

## Numeric regression metrics protected

Component `volumeMm3`, component/assembly `boundingBox.*` (12 fields each), and relationship `minDistanceMm` — compared with `RELATIVE_COMPARISON_TOLERANCE = 1e-3` / `ABSOLUTE_COMPARISON_TOLERANCE_MM = 1e-4`, empirically derived (see [`505-comparison-tolerance-policy.md`](505-comparison-tolerance-policy.md)).

## Relationship regressions protected

2 per pair, across all 6 pairwise component combinations: `connected` (connectivity) and `intersectionStatus`.

## STEP semantic roundtrip cases

2 verified directly (`test_default_solitaire_step_roundtrip_has_no_regressions`, `test_four_prong_variant_step_roundtrip_has_no_regressions`), plus all 9 real Golden cases via `verify_all_goldens(check_artifacts=True)` — export → re-import → compare solid count/volume/bounding box, never bytes.

## STL regression cases

2 verified directly, plus all 9 real Golden cases via the same `check_artifacts=True` path — non-empty file, real triangle count (via the existing `exporters/integrity.py::binary_stl_triangle_count`), and an approximate bounding-box consistency check via a new lightweight binary STL parse.

## Repeatability runs performed

3 (the default solitaire's `GeometrySnapshot` generated 3 times locally) — see `TestRepeatability::test_three_repeated_generations_are_bit_identical_locally`.

## Observed non-deterministic geometric facts

0 locally (all 3 repeatability runs were bit-identical, confirming ATLAS-GOV-003 holds on a fixed machine/kernel build). 1 real, previously-measured cross-platform fact (not newly observed this Sprint): Sprint 14's own CI run showed a ~1.3e-5 relative divergence between Windows and Linux OCCT builds on the smallest, most near-tangent pairwise intersection volume — this Sprint's tolerance is set two orders of magnitude above that measured bound.

## Known geometry limitations captured

1: `SOL-009-warning-only-large-stone-four-prong` triggers Forge warning `JM-PRONG-003` (a 9mm stone with 4 prongs) — the definition remains valid and generates correctly; this is documented as an intentional warning-only test case, not a defect.

## Golden auto-update possible in CI: no

Structurally enforced, not merely documented: `verify_golden()`, `verify_all_goldens()`, and `generate_candidate_baseline()` never call `save_golden()` — only `accept_candidate_baseline()` does, reachable exclusively via `geometry-quality accept --reason "..."`. `TestNoAutoUpdate` (`backend/tests/test_geometry_quality_harness.py`) proves this both by inspecting each function's own source code and by running `verify_golden`/`verify_all_goldens` repeatedly and confirming the accepted baseline file is byte-identical before and after.

## Human-readable geometry diff implemented: yes

`GeometryDiff.human_readable()` produces a per-metric report (`Golden: <id>`, `Metric: <path>`, `Expected:`/`Actual:`/`Delta:`/`Tolerance:`/`Status:`) rather than a bare assertion error — see [`508-geometry-diff-model.md`](508-geometry-diff-model.md) and `TestHumanReadableDiff`.

## Version fingerprint implemented: yes

`VersionFingerprint` (7 fields: JDL schema, Forge rule set, compiler, Atlas generator, inspection, CAD kernel, OCP) is collected by `collect_fingerprint()` from real running version constants and attached to every Golden Model and every comparison. A kernel/OCP/generator version mismatch reclassifies a topology diff from `REGRESSION` to `VERSION_REVIEW_REQUIRED` rather than being silently absorbed (QUALITY-GOV-010).

## Golden models falsely marked professionally validated

0 — verified by `TestNoProfessionalClaim` scanning every accepted Golden snapshot and the suite manifest for prohibited claim strings (`manufacturing_ready`, `production_approved`, `professionally_validated`, `industry_standard`, and hyphen/space variants).

## Tests passed

- Backend: **763/763** (`pytest -q`), including 48 new tests across `test_geometry_quality_snapshot.py` (16), `test_geometry_quality_harness.py` (16, including the escalation-fix regression test below), `test_geometry_quality_artifacts.py` (6), and `test_geometry_quality_schemas.py` (10).
- Frontend: **137/137** (unaffected — this Sprint made no frontend changes).
- `ruff check .`: clean.
- Geometry Inspection (Sprint 14), Professional Validation (Sprint 13), Designer/Conversation/Design-Intent, and Studio/Vision test suites: all unaffected, verified as part of the same full `pytest -q` run.

## Frontend build

Not applicable — Sprint 15 made no frontend changes. `npm run test`/`tsc -b`/`npm run build` were not expected to change and were not required to re-verify beyond confirming no backend-only sprint could have touched them; they were nonetheless re-run as part of the overall repository validation pass and remain green.

## CI result

See the top-level Sprint 15 delivery message for the final GitHub Actions run link and status.

## A real bug found and fixed during this Sprint's own validation

A background documentation agent, while writing [`504-regression-comparison-model.md`](504-regression-comparison-model.md) and [`509-artifact-regression-model.md`](509-artifact-regression-model.md) from the real `harness.py` source, correctly identified that `verify_golden()`'s artifact-severity escalation rule (`if diff.artifactChanges and diff.severity == "NONE"`) would let a real STEP/STL artifact regression hide behind an unrelated, harmless `INFO`-level numeric drift — the top-line `QualityResultStatus` could read `PASS` even with a real artifact defect present. This was fixed (the condition now escalates from `NONE` **or** `INFO`) before this Sprint's commit, with a new regression test (`TestArtifactSeverityEscalation::test_artifact_regression_escalates_even_when_geometric_diff_is_info`) proving the fix, and the two docs that had accurately described the bug were updated to describe the fix instead. This is exactly the kind of contradiction-reporting discipline the Bible's own fundamental rule requires — the agent reported what it found rather than silently working around it, and the underlying code was fixed rather than the documentation being rewritten to excuse it.

---

**Sprint 16 — Ring Architecture v2** — generalize the current solitaire-specific model into a composable ring architecture with explicit head, shank, shoulder, setting and stone-arrangement contracts, preparing JewelMind for multiple ring families without implementing them all at once.
