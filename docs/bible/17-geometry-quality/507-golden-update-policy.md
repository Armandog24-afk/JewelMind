---
id: JM-BIBLE-507
title: Golden Update Policy
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
  - JM-BIBLE-506
  - JM-BIBLE-508
implementation_status: current
professional_validation: not_required
normative: true
---

# Golden Update Policy

## The explicit accept workflow

```
generate-candidate <id>   →  writes goldens/<suite>/<id>/candidate.json   (never snapshot.json)
diff <id>                 →  compares candidate.json against the accepted snapshot.json, human-readable
accept <id> --reason "…"  →  the ONLY path that calls save_golden() — writes snapshot.json
```

1. **`geometry-quality generate-candidate <id>`** runs `generate_candidate_baseline()` and `registry.save_candidate()` writes the result to `goldens/<suite>/<id>/candidate.json` via `registry.candidate_path()`. This file is a working scratch artifact, not an accepted baseline — nothing in the harness or any test treats `candidate.json` as authoritative.
2. **`geometry-quality diff <id>`** loads the accepted `snapshot.json` (if one exists) and the just-written `candidate.json`, runs the real `compare_snapshot()` between them, and prints `GeometryDiff.human_readable()`. If no accepted baseline exists yet for this `id`, it instead prints the full candidate JSON, since every fact in it is new.
3. **`geometry-quality accept <id> --reason "..."`** is the only command that reaches `accept_candidate_baseline()`, which is the only function that calls `registry.save_golden()`. `--reason` is declared `required=True` in `cli.py`'s `argparse` setup — the command cannot be invoked without one. The reason is appended to the accepted golden's `notes` field (`f"{candidate.notes}\nReason: {args.reason}".strip()`), and the CLI prints a reminder to also record it in [`../appendices/golden-update-register.md`](../appendices/golden-update-register.md).

## QUALITY-GOV-003/004/018, restated at the workflow level

- **QUALITY-GOV-003** — no developer or AI agent may automatically overwrite a failing baseline. `verify_golden()`, `verify_all_goldens()`, and `generate_candidate_baseline()` never call `save_golden()` — enforced structurally, not just by convention (see below).
- **QUALITY-GOV-004** — an intentional baseline change requires explicit acceptance. `accept_candidate_baseline()` is the only write path, and it is only ever reachable through the `accept --reason "..."` CLI command — never from CI, never from a test, never as a side effect of running the verify suite.
- **QUALITY-GOV-018** — a baseline update requires a human-readable diff. `accept` is expected to be run only after `diff <id>` has been run and its output reviewed; the `--reason` requirement and the `golden-update-register.md` reminder exist precisely so that acceptance is never a blind, unreviewed action.

## CI must never call `accept`

Nothing in `harness.py` or `cli.py` invokes `accept`/`accept_candidate_baseline()` automatically, and no test does either — `accept_candidate_baseline()` is called exactly once in the entire test suite, in `TestNoAutoUpdate::test_only_accept_candidate_baseline_calls_save_golden`, which inspects its *source code* rather than actually invoking it against the real registry. A CI pipeline running `geometry-quality verify-all` on every pull request will correctly fail (`exit 1`) on a real regression and will never silently rewrite the failing baseline to make the run green — the only way to make a legitimate, reviewed geometry change pass CI again is for a human to run `generate-candidate` → `diff` → `accept --reason "..."` locally (or in an explicitly human-triggered workflow step) and commit the resulting `snapshot.json`.

## Enforced by source inspection, not just behavior

`TestNoAutoUpdate` in `backend/tests/test_geometry_quality_harness.py` uses `inspect.getsource()` to assert the literal string `"save_golden"` is absent from `verify_golden`, `verify_all_goldens`, and `generate_candidate_baseline`, and present in `accept_candidate_baseline`. This is a stronger guarantee than a behavioral test alone: it fails immediately if a future edit adds a `save_golden()` call anywhere inside those three functions, even inside a code path a behavioral test might not exercise (e.g. a conditional branch only reachable under specific inputs). A companion test, `test_a_regression_detected_by_verify_golden_does_not_change_the_file_on_disk`, calls `verify_golden`/`verify_all_goldens` twice in a loop against `SOL-001-default-solitaire` and asserts the on-disk `snapshot.json` is unchanged before and after — behavioral confirmation alongside the structural one.

## QUALITY-GOV-017, restated

A deliberate, reviewed geometry improvement is *expected* to fail `verify_golden`/`verify-all` until its new baseline is explicitly accepted through this workflow — that is the system doing its job, not a defect to work around by loosening a tolerance or deleting an assertion (QUALITY-GOV-016).
