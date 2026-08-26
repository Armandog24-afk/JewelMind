---
id: JM-BIBLE-500
title: Geometry Quality Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-QUALITY-README
related_documents:
  - JM-BIBLE-090
  - JM-BIBLE-120
  - JM-BIBLE-460
implementation_status: current
professional_validation: not_required
normative: true
---

# Geometry Quality Governance

18 non-negotiable rules for `backend/jewelmind/geometry_quality/`, `goldens/`, and `specs/geometry-quality/v1/`. Mirrors the INSPECT-GOV/ATLAS-GOV governance pattern established in Sprints 5 and 14.

**QUALITY-GOV-001 — Golden Models are software regression references, not professional approvals.** A `GoldenModel` never claims manufacturing readiness, professional validation, or aesthetic correctness. See [`514-professional-validation-boundary.md`](514-professional-validation-boundary.md).

**QUALITY-GOV-002 — Golden snapshots must originate from real generated JewelMind geometry.** Every `GeometrySnapshot` is built by `generate_snapshot()` running the real `build_solitaire_ring()` → `inspect_model()` pipeline. No fact in `goldens/` is hand-invented.

**QUALITY-GOV-003 — No developer or AI agent may automatically overwrite a failing baseline.** `verify_golden()`, `verify_all_goldens()`, and `generate_candidate_baseline()` never call `save_golden()`. See `TestNoAutoUpdate` in `backend/tests/test_geometry_quality_harness.py`.

**QUALITY-GOV-004 — Intentional baseline changes require explicit acceptance.** Only `accept_candidate_baseline()` writes an accepted baseline, and it is only ever reachable via the `geometry-quality accept --reason "..."` CLI command — never from CI, never from a test.

**QUALITY-GOV-005 — Exact invariants and floating-point comparisons must remain distinct.** `GeometryDiff.exactChanges` and `GeometryDiff.numericChanges` are separate lists; `compare_snapshot()` never merges an exact mismatch into a tolerance check or vice versa.

**QUALITY-GOV-006 — Comparison tolerances are software-regression tolerances, not manufacturing tolerances.** `ABSOLUTE_COMPARISON_TOLERANCE_MM`/`RELATIVE_COMPARISON_TOLERANCE` (`geometry_quality/version.py`) exist only to distinguish real regressions from cross-platform kernel noise. See [`505-comparison-tolerance-policy.md`](505-comparison-tolerance-policy.md).

**QUALITY-GOV-007 — STEP byte equality must not be required.** CadQuery's STEP writer embeds variable OpenCascade metadata (timestamp/GUID/counters); two exports of identical geometry are not byte-identical. Proven by `test_two_step_exports_of_identical_geometry_are_not_byte_identical`.

**QUALITY-GOV-008 — Geometry-equivalent STEP output may still be valid despite binary differences.** `step_roundtrip_check()` compares solid count, volume, and bounding box after re-import — never a checksum.

**QUALITY-GOV-009 — Golden models must record relevant version fingerprints.** Every `GoldenModel.versionFingerprint` is collected by `collect_fingerprint()` from real running version constants — never invented. See [`510-version-fingerprint-policy.md`](510-version-fingerprint-policy.md).

**QUALITY-GOV-010 — A CAD-kernel version change must not silently rewrite baselines.** `compare_snapshot()` classifies a topology change as `VERSION_REVIEW_REQUIRED` (not an unconditional `REGRESSION`) only when `kernelVersion`/`ocpVersion`/`atlasGeneratorVersion` differ between the expected and actual fingerprint — and `VERSION_REVIEW_REQUIRED` still requires baseline review, never an automatic pass.

**QUALITY-GOV-011 — Component disappearance must always be reported.** A missing component produces an `ExactChange` at `components.missing`, always driving `severity: REGRESSION`.

**QUALITY-GOV-012 — Connectivity changes must always be reported.** A flipped `connected` fact produces a `RelationshipChange`, always driving `severity: REGRESSION`.

**QUALITY-GOV-013 — StoneReference identity and production exclusion must remain regression-protected.** `designConsistency.stoneReferenceIsProductionMetal` is an exact invariant in every comparison, restating LAW-006/INSPECT-GOV-008 at the quality layer.

**QUALITY-GOV-014 — Requested/generated prong-count consistency must remain regression-protected.** `designConsistency.requestedProngCount`/`generatedProngCount`/`prongCountMatches` are exact invariants in every comparison.

**QUALITY-GOV-015 — Golden tests must use actual Atlas/Inspection output.** No function under `geometry_quality/` ever mocks a `GeneratedComponent`, a `GeometryInspectionReport`, or any part of the real pipeline.

**QUALITY-GOV-016 — Tests must never be weakened merely because a new implementation fails them.** A genuine regression is fixed in code, or an intentional change is accepted through the explicit `accept` workflow with a documented reason — never by loosening a tolerance or deleting an assertion to make CI pass.

**QUALITY-GOV-017 — Intentional geometry improvements may legitimately require new Golden baselines.** A deliberate, reviewed geometry change is expected to fail verification until its baseline is explicitly accepted — this is the system working as designed, not a defect.

**QUALITY-GOV-018 — Baseline updates require a human-readable diff.** `accept_candidate_baseline()` is only ever invoked after `geometry-quality diff <id>` has been run and its output reviewed; the CLI's `accept` command requires `--reason` and records it in the golden's `notes` field and in [`golden-update-register.md`](../appendices/golden-update-register.md).
