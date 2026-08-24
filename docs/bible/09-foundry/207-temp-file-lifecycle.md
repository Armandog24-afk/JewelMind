---
id: JM-BIBLE-207
title: Temp-File Lifecycle
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-206
related_documents:
  - JM-BIBLE-186
implementation_status: current
professional_validation: not_required
normative: true
---

# Temp-File Lifecycle

## Two distinct temp-file mechanisms, confirmed by direct inspection

| Mechanism | Created by | Named by | Lifetime | Cleanup |
|---|---|---|---|---|
| Per-model preview directory | `ModelService.generate()`, via `tempfile.mkdtemp(prefix=f"jewelmind_{model_id}_")` | Model ID only, never a user string | As long as the model stays cached | Evicted oldest-first once `len(self._records) > MAX_CACHED_MODELS` (20); the whole directory is removed with the record |
| Per-export temp file | `ModelService._unique_temp_path()`, via `tempfile.mkstemp(prefix=f"jewelmind_{model_id}_export_", suffix=suffix)` | Model ID + a kernel-guaranteed-unique suffix, never a user string | One HTTP request | Deleted via `BackgroundTask(_delete_file, path)`, which runs after the `FileResponse` has finished streaming |

Both paths are constructed exclusively from the model ID (a server-generated UUID-like value) and a fixed suffix — never from `record.definition.project.name` or any other user-controlled string. This makes the two-mechanism split relevant to [`206-filename-and-path-safety.md`](206-filename-and-path-safety.md)'s finding: even a maximally hostile project name cannot influence any real filesystem path, only the client-facing suggested download name.

## Cleanup on both success and failure

- **Failure during export/validation**: `ModelService.export_step_file()`/`export_stl_file()` wrap the build in `try`/`except`, calling `destination.unlink(missing_ok=True)` before re-raising — the partially-built or empty file never survives a failed request.
- **Success**: `api/routes.py::_delete_file()` runs as a Starlette `BackgroundTask` after the response body has fully streamed to the client, wrapped in `contextlib.suppress(OSError)` so a delete-time race (e.g. the file already gone) never turns a successful export into a 500 for the caller.

## What this means for concurrent requests

Because every export temp file is uniquely named per request (via `tempfile.mkstemp()`'s own uniqueness guarantee), two concurrent exports of the same model never collide on the same path — each gets its own file, its own cleanup callback, and its own lifetime, independent of the other.

## Known limitation

If the process crashes between file creation and the `BackgroundTask` running (e.g. the server process is killed mid-response), the temp file is orphaned on disk — there is no separate janitor process that sweeps stale `jewelmind_*_export_*` files. This is a real, low-probability gap, not yet worth a dedicated cleanup mechanism given the prototype's current scale — see [`218-foundry-gap-analysis.md`](218-foundry-gap-analysis.md).
