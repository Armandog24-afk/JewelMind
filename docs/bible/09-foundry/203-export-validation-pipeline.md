---
id: JM-BIBLE-203
title: Export Validation Pipeline
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-202
related_documents:
  - JM-BIBLE-194
implementation_status: partial
professional_validation: not_required
normative: true
---

# Export Validation Pipeline

## Pre-export checks (FOUNDRY-0..3)

| Check | Real mechanism | Blocking? |
|---|---|---|
| Model exists | `ModelService.get_record()` | Yes — `MODEL_NOT_FOUND` |
| Definition passed Forge validation | Implicit — a `ModelRecord` is only ever created after `validate_definition()` reported zero `error`-severity results, at generation time | Yes, transitively |
| Destination path is safe and unique | `_unique_temp_path()` | Yes — a path collision would raise before any write |
| Requested filename is safe | `sanitize_filename()` | n/a — sanitization always succeeds by falling back to a default, never blocks |

## Post-export checks (FOUNDRY-5..9)

Covered in full in [`202-artifact-integrity-model.md`](202-artifact-integrity-model.md). Restated briefly: `validate_non_empty()` and `sha256_checksum()` run for every real STEP/STL request; format-signature parsing runs for STL only; re-import/roundtrip validation runs only in the test suite.

## What happens on a validation failure

Every check in this pipeline raises a subclass of `AppError` (see [`204-export-diagnostics.md`](204-export-diagnostics.md) for the exact codes) rather than returning a partial or default result. `ModelService.export_step_file()`/`export_stl_file()` wrap the build-and-validate sequence in a `try`/`except` that deletes the temp file (`destination.unlink(missing_ok=True)`) before re-raising on any failure — so a validation failure never leaves an orphaned, possibly-corrupt file on disk for a later request to accidentally reuse.

## What this pipeline does not do

It never inspects geometry for jewelry-domain correctness (Forge's job, already done before generation) and never re-runs Atlas construction to "fix" a bad export — a failure here is always reported, never silently retried with different parameters.
