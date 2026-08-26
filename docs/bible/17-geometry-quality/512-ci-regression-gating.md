---
id: JM-BIBLE-512
title: CI Regression Gating
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
  - JM-BIBLE-511
implementation_status: current
professional_validation: not_required
normative: true
---

# CI Regression Gating

## No new CI job was needed this Sprint

The real CI configuration is [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml). It defines three jobs: `backend` (name: "Backend (Python 3.11)"), `frontend` (name: "Frontend (Node 24)"), and `docker-smoke-test`. The `backend` job's steps are: checkout, `actions/setup-python@v5`, install OpenCascade/VTK runtime libraries, `pip install -r requirements.txt`, `ruff check .`, and finally a step named **"Pytest (all tests)"** running `python -m pytest -q` with `working-directory: backend`.

`backend/tests/test_geometry_quality_snapshot.py`, `test_geometry_quality_harness.py`, `test_geometry_quality_artifacts.py`, and `test_geometry_quality_schemas.py` are plain pytest files under `backend/tests/`, with no `pytest.mark.skip`/`xfail`/custom marker on any of their 47 tests. Pytest's default collection picks them up automatically as part of the same `python -m pytest -q` invocation that already runs every other backend test. **No new CI job, step, or workflow file was added for Geometry Quality** — the existing "Pytest (all tests)" step in the "Backend (Python 3.11)" job already runs, and already gates on, the full Golden Suite every time it runs.

## CI gating is already real and complete via one specific test

`backend/tests/test_geometry_quality_harness.py::TestRealGeneration::test_every_golden_in_the_manifest_passes` calls the real `verify_all_goldens()` and asserts `result.status in ("PASS", "PASS_WITH_KNOWN_LIMITATIONS")` for every one of the 9 goldens (with an additional `assert len(results) >= 8` floor). `verify_all_goldens()` runs the real pipeline — `JDL → validation → geometry → inspection → compare_snapshot()` — against the real accepted baselines in `goldens/solitaire-v1/`, exactly as a developer or CI machine would run it. If any golden's actual status resolves to `REGRESSION_DETECTED`, `VERSION_REVIEW_REQUIRED`, `BASELINE_MISSING`, or `ERROR`, this single assertion fails, which fails the test, which fails `python -m pytest -q`, which fails the "Pytest (all tests)" step, which fails the "Backend (Python 3.11)" job, which fails the whole CI workflow run (both jobs run in parallel; `docker-smoke-test` depends on both via `needs: [backend, frontend]`, so it never runs either).

This means: **CI already fails on an unexplained regression today, with no additional wiring required.** This is not a plan for a future gate — it is the real, current behavior of `test_every_golden_in_the_manifest_passes` running inside the existing CI job. QUALITY-GOV-003/004 (no automatic baseline rewrite, ever) mean a genuine regression cannot be silently absorbed by this test either — the only ways to make it pass again are fixing the code so the real geometry matches the baseline again, or running the explicit `geometry-quality accept --reason "..."` CLI workflow to update the baseline (see [`507-golden-update-policy.md`](507-golden-update-policy.md), [`513-regression-failure-triage.md`](513-regression-failure-triage.md)) — never something CI itself does.

## Why the `fastSuite`/`fullSuite` split exists without a workflow using it yet

[`511-current-solitaire-golden-suite.md`](511-current-solitaire-golden-suite.md) documents that `manifest.json`'s `fastSuite` (3 cases) and `fullSuite` (9 cases) arrays are real data, but that no code under `backend/jewelmind/geometry_quality/` currently reads either array — `verify_all_goldens()` always runs against every golden in `goldenIds` (all 9), regardless of the split. The split exists so a future targeted-vs-full CI workflow (e.g. run `fastSuite` on every push, `fullSuite` only on a merge to `main` or a nightly schedule) has a real place to read from, **if and when the Golden Suite ever becomes expensive enough to need that distinction**. It does not need it today.

Per-case timing for the current 9-case suite was not separately profiled this Sprint — no `time.perf_counter()` instrumentation exists anywhere in `backend/jewelmind/geometry_quality/harness.py` (verified directly; see [`515-performance-baseline-model.md`](515-performance-baseline-model.md) for the honest statement of that gap). Stating a specific number here would be inventing one; the honest fact is that the entire 47-test Geometry Quality suite currently runs as an unremarkable fraction of the whole `python -m pytest -q` backend run, with no observed slowdown that prompted profiling. If the suite grows to the point where per-case cost becomes a real concern, `fastSuite`/`fullSuite` is where that policy work would start.

## No brittle CI time limit exists or is planned

Consistent with [`16-geometry-inspection/484-inspection-performance-model.md`](../16-geometry-inspection/484-inspection-performance-model.md)'s own stance against inventing hard timing thresholds for kernel-derived work, no wall-clock timeout, `pytest-timeout` marker, or CI step time budget was added for the Golden Suite this Sprint, and none is proposed.

## Cross-references

- [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml) — the real workflow file.
- [`507-golden-update-policy.md`](507-golden-update-policy.md) — the only legitimate way to make a genuinely-changed baseline pass again.
- [`513-regression-failure-triage.md`](513-regression-failure-triage.md) — what to do when this gate fails.
- [`515-performance-baseline-model.md`](515-performance-baseline-model.md) — the honest gap: no harness-level timing instrumentation exists yet.
