---
id: JM-BIBLE-513
title: Regression Failure Triage
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
  - JM-BIBLE-504
  - JM-BIBLE-508
implementation_status: current
professional_validation: not_required
normative: true
---

# Regression Failure Triage

When `verify_golden()`/`verify_all_goldens()` returns anything other than `PASS`/`PASS_WITH_KNOWN_LIMITATIONS`, a human triages the failure into one of 6 categories before deciding what to do. None of these categories is a `QualityResultStatus` or `DiffSeverity` value in code — they are a triage vocabulary a developer applies by reading the real `GeometryDiff`, not a field the system itself sets.

## The 6 categories

1. **EXPECTED_INTENTIONAL_CHANGE** — a deliberate, reviewed geometry improvement (e.g. a fillet added, a dimension formula corrected) that was expected to fail verification until its baseline is explicitly accepted. Typically shows as `REGRESSION_DETECTED` with `exactChanges`/`numericChanges`/`topologyChanges` that match exactly what the change was supposed to do, and nothing else. This is QUALITY-GOV-017's "the system working as designed" case.
2. **SOFTWARE_DEFECT** — an unintended code change (a bug in a geometry builder, a broken boolean operation, a regression introduced by an unrelated refactor) silently altered output. Typically shows as `REGRESSION_DETECTED` with `exactChanges`/`relationshipChanges`/`topologyChanges` unrelated to whatever change was actually intended, or a component going missing (`components.missing`, always `REGRESSION` per QUALITY-GOV-011) or losing connectivity (a `connected` flip, always `REGRESSION` per QUALITY-GOV-012).
3. **KERNEL_VERSION_CHANGE** — a CadQuery/OpenCascade upgrade changed low-level topology counts (face/edge/vertex counts, or booleans producing a different-but-geometrically-equivalent tessellation) without a real geometry defect. Typically shows as `topologyChanges` with `expectedFingerprint.kernelVersion`/`ocpVersion`/`atlasGeneratorVersion` differing from `actualFingerprint`'s — `compare.py::_kernel_related_fields_differ()` detects exactly this condition and `compare_snapshot()` classifies the result `VERSION_REVIEW_REQUIRED` rather than an unconditional `REGRESSION` (QUALITY-GOV-010). If a numeric/exact/relationship change accompanies the topology change, severity still escalates to `REGRESSION` regardless of a kernel-version difference — `VERSION_REVIEW_REQUIRED` only applies when topology changes are the *only* finding.
4. **INSPECTION_SEMANTIC_CHANGE** — Sprint 14's `geometry/inspection/` measurement logic itself changed (e.g. a different `CONTACT_TOLERANCE_MM`, a redefinition of "connected," a new broad-phase skip condition) in a way that changes what a `GeometrySnapshot` reports even though the underlying geometry is unchanged. Typically shows as `relationshipChanges` (a `connected`/`intersectionStatus` flip) or `exactChanges` at `designConsistency.*`, with `expectedFingerprint.inspectionVersion` differing from `actualFingerprint.inspectionVersion`. Unlike the kernel-version case, `compare_snapshot()` does not currently special-case an `inspectionVersion` difference — this category is identified by a human reading the fingerprint diff and the actual inspection code change, not by an automated status.
5. **BASELINE_CORRUPTION** — the accepted `snapshot.json` on disk was hand-edited, corrupted, or written by something other than `accept_candidate_baseline()`. Typically shows as an implausible `exactChanges`/`numericChanges` set with no corresponding real code or kernel change to explain it, or a `QualityResultStatus` of `ERROR` if the file fails to parse as a `GoldenModel` at all (`registry.py::load_golden()` raising `FileNotFoundError` instead produces `BASELINE_MISSING`, a distinct, non-corruption case).
6. **UNKNOWN** — the diff doesn't cleanly match any of the above; more investigation is needed before deciding. This is the honest default when the `GeometryDiff` (or a re-run of `geometry-quality diff <id>`) doesn't yet point at a clear cause — it is not a status to hide behind indefinitely.

## The real workflow

1. A golden fails: `verify_golden(golden_id)`/`verify_all_goldens()` (via CI's "Pytest (all tests)" step, see [`512-ci-regression-gating.md`](512-ci-regression-gating.md)) returns a non-passing `QualityResult`.
2. Inspect the `GeometryDiff` — either by running `python -m jewelmind.geometry_quality.cli diff <golden_id>` after `generate-candidate`, or by reading `QualityResult.diff` directly (its `human_readable()` method, used by both the CLI and the test's failure message, names every changed metric with expected/actual/delta/tolerance).
3. Identify which of the 6 categories the diff matches, using the patterns above plus the actual code/environment change under review.
4. Act:
   - **EXPECTED_INTENTIONAL_CHANGE**: run `geometry-quality generate-candidate <id>`, review the diff, then `geometry-quality accept <id> --reason "..."` — the only code path that writes an accepted baseline (QUALITY-GOV-004), and record the change in [`golden-update-register.md`](../appendices/golden-update-register.md) (QUALITY-GOV-018).
   - **SOFTWARE_DEFECT**: fix the code. Do not touch the baseline.
   - **KERNEL_VERSION_CHANGE** / **INSPECTION_SEMANTIC_CHANGE**: review whether the new topology/relationship facts are geometrically legitimate for the new kernel/inspection version; if so, treat as an intentional change (generate-candidate → diff → accept with a reason naming the version change); if the new facts look wrong, treat as a software defect in the new kernel/inspection integration instead.
   - **BASELINE_CORRUPTION**: restore or regenerate the baseline through the same explicit `generate-candidate`/`accept` workflow — never hand-edit `snapshot.json`.
   - **UNKNOWN**: keep investigating; do not guess.

## The one rule this document exists to restate

**Never**: failure → regenerate snapshots automatically → green CI. `verify_golden()`, `verify_all_goldens()`, and `generate_candidate_baseline()` never call `save_golden()` — only `accept_candidate_baseline()` does, and it is only ever reachable through the explicit `geometry-quality accept --reason "..."` CLI command (QUALITY-GOV-003/004), never from CI, never from a test, and never automatically by an agent reacting to a failing pipeline. `backend/tests/test_geometry_quality_harness.py::TestNoAutoUpdate` enforces this structurally by inspecting the source of all four functions for calls to `save_golden`/`save_candidate`. Loosening a tolerance or deleting an assertion to make a genuine finding disappear is equally prohibited (QUALITY-GOV-016) — a real regression gets fixed in code or explicitly accepted with a documented reason, never silenced.

## Cross-references

- [`504-regression-comparison-model.md`](504-regression-comparison-model.md), [`508-geometry-diff-model.md`](508-geometry-diff-model.md) — the structures this triage reads.
- [`507-golden-update-policy.md`](507-golden-update-policy.md) — the accept workflow in full.
- [`510-version-fingerprint-policy.md`](510-version-fingerprint-policy.md) — how `VERSION_REVIEW_REQUIRED` is derived.
- [`golden-update-register.md`](../appendices/golden-update-register.md) — where every accepted baseline change is recorded.
