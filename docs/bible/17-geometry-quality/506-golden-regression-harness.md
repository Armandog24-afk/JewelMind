---
id: JM-BIBLE-506
title: Golden Regression Harness
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
  - JM-BIBLE-507
implementation_status: current
professional_validation: not_required
normative: true
---

# Golden Regression Harness

`backend/jewelmind/geometry_quality/harness.py` provides the four functions every other entry point (tests, the CLI) is built on. Every one of them runs the real JDL → validation → geometry → inspection pipeline; none mocks a `GeneratedComponent`, a `GeometryInspectionReport`, or any other part of it (QUALITY-GOV-015).

## The 4 real functions

### `verify_golden(golden_id: str, *, check_artifacts: bool = False) -> QualityResult`

Loads the accepted `GoldenModel` via `registry.load_golden()`, loads its source `design.json` via `registry.load_design()`, regenerates a fresh `GeometrySnapshot` from that real design through `generate_snapshot()`, collects the current run's real `VersionFingerprint` via `collect_fingerprint()`, and calls `compare_snapshot()`. If `check_artifacts=True`, it additionally runs `step_roundtrip_check()`/`stl_structure_check()` and folds their results in (see [`504-regression-comparison-model.md`](504-regression-comparison-model.md)'s "How artifact checks fold into severity" section for the exact rule). Returns a `QualityResult` — never raises for an ordinary regression, `BASELINE_MISSING`, or a pipeline exception (those become `ERROR`, caught with a broad `except Exception` and reported as text, "report, never crash the harness" per the code's own comment).

### `verify_all_goldens(*, check_artifacts: bool = False) -> list[QualityResult]`

`[verify_golden(golden_id, check_artifacts=check_artifacts) for golden_id in list_golden_ids()]` — one line, iterating every `goldenId` in the current suite's `manifest.json`.

### `generate_candidate_baseline(golden_id: str) -> GoldenModel`

Loads the source `design.json`, regenerates a fresh snapshot and fingerprint from the real pipeline, and constructs a **new, in-memory** `GoldenModel` with `baselineStatus="CANDIDATE"`, `acceptedAt=None`, and `createdAt` set to now. It carries forward `description`/`artifactExpectations`/`knownLimitations`/`notes` from the existing accepted golden when one exists (falls back to sensible defaults, including `DEFAULT_ARTIFACT_EXPECTATIONS`, when generating a candidate for a brand-new case with no prior accepted baseline). **It returns the candidate — it never writes it to disk.**

### `accept_candidate_baseline(candidate: GoldenModel) -> GoldenModel`

The only function in this module that imports and calls `registry.save_golden()`. Copies the candidate with `baselineStatus="STABLE"` and `acceptedAt` set to now, writes it, and returns the accepted `GoldenModel`. Never called by `verify_golden`, `verify_all_goldens`, or `generate_candidate_baseline` — only ever reached through the CLI's explicit `accept` subcommand. See [`507-golden-update-policy.md`](507-golden-update-policy.md) for the full workflow this sits inside.

## The 5 CLI subcommands

`backend/jewelmind/geometry_quality/cli.py` (`python -m jewelmind.geometry_quality.cli <subcommand>`):

| Subcommand | Wraps | Exit code |
|---|---|---|
| `verify-all [--artifacts]` | `verify_all_goldens()`; prints one line per golden plus each failure's `human_readable()` message | `0` if every result is `PASS`/`PASS_WITH_KNOWN_LIMITATIONS`, else `1` |
| `verify <id> [--artifacts]` | `verify_golden(id)`; prints `result.message` | same PASS/PASS_WITH_KNOWN_LIMITATIONS rule |
| `generate-candidate <id>` | `generate_candidate_baseline(id)`, then `registry.save_candidate()` writes `candidate.json` | always `0` |
| `diff <id>` | Loads the accepted golden (if any) and the just-generated candidate via `registry.load_candidate()`, runs `compare_snapshot()` between them, prints `human_readable()` | always `0` |
| `accept <id> --reason "..."` | `--reason` is `required=True` at the `argparse` level — the command cannot run without one; appends the reason to the candidate's `notes`, then calls `accept_candidate_baseline()` | always `0` |

## Real pipeline, never a mock

`generate_snapshot()` (`snapshot.py`) is the shared entry point `verify_golden`/`generate_candidate_baseline` both call: it runs `validate_definition()` (raising `ValueError` on a real validation error — a Golden fixture must be a genuinely valid definition), `build_solitaire_ring()`, and `inspect_model()` — the exact same three real calls the production `ModelService.generate()` path makes, per [`../08-alchemist/README.md`](../08-alchemist/README.md)'s orchestration description. `TestRealGeneration::test_verify_golden_uses_the_real_pipeline_not_a_mock` (`backend/tests/test_geometry_quality_harness.py`) asserts the returned diff's `actualFingerprint.kernelVersion` is truthy — a real `cadquery.__version__` string, which only a real CadQuery invocation could have produced.

## Read-only by structural test, not just convention

`TestNoAutoUpdate` in `backend/tests/test_geometry_quality_harness.py` does not merely assert on behavior — it inspects the actual source of each function (`inspect.getsource(...)`) and asserts the substring `"save_golden"` is absent from `verify_golden`, `verify_all_goldens`, and `generate_candidate_baseline`, and present only in `accept_candidate_baseline`. A separate test in the same class regenerates and re-verifies the real `SOL-001-default-solitaire` golden twice in a loop and asserts the on-disk `snapshot.json` is byte-for-byte unchanged before and after. See [`507-golden-update-policy.md`](507-golden-update-policy.md) for why this matters and what governs the one legitimate write path.
