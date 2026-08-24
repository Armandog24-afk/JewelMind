---
id: JM-BIBLE-216
title: Foundry Security and Resource Limits
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-186
related_documents:
  - JM-BIBLE-083
implementation_status: current
professional_validation: not_required
normative: true
---

# Foundry Security and Resource Limits

Restates and extends [`08-alchemist/186-compiler-security-and-resource-limits.md`](../08-alchemist/186-compiler-security-and-resource-limits.md) at the artifact-generation layer specifically.

| Risk | Current status |
|---|---|
| Path traversal via project name | **MITIGATED** — `sanitize_filename()`; see [`206-filename-and-path-safety.md`](206-filename-and-path-safety.md) for the one known low-risk gap (Windows reserved device names) |
| Server-internal path exposure | **MITIGATED** — the sanitized project name, never the real `tempfile.mkstemp()` path, is the only path-like value ever returned to a caller |
| Temporary-file exhaustion from exports | **MITIGATED** — unique per-request temp files, `BackgroundTask`-scheduled deletion on success, `unlink(missing_ok=True)` on failure; see [`207-temp-file-lifecycle.md`](207-temp-file-lifecycle.md) |
| Orphaned temp files from a process crash | **NOT MITIGATED** — no janitor process sweeps stale export temp files if the server is killed mid-response; a real, low-probability, documented gap |
| Empty or corrupt file returned as a success | **MITIGATED as of Sprint 7** — `validate_non_empty()` runs for every real STEP/STL export |
| Undetected file tampering/corruption in transit | **PARTIALLY MITIGATED as of Sprint 7** — `X-Content-SHA256` lets a caller verify integrity after the fact, but nothing enforces the caller actually checks it |
| Excessive concurrent export requests | **NOT MITIGATED** — no rate limit or concurrency cap on export endpoints specifically, same finding as the Alchemist-level document |
| Re-import/roundtrip validation as a denial-of-service vector | **NOT APPLICABLE** — this check runs only in the test suite, never triggered by a real request, so it cannot be abused as a per-request cost amplifier |
| Reserved filenames (Windows `CON`, `PRN`, etc.) | **LOW-RISK, NOT MITIGATED** — client-side download-name inconvenience only, never a server path; see [`206-filename-and-path-safety.md`](206-filename-and-path-safety.md) |

## What changed this Sprint

Two genuine new mitigations were added: `validate_non_empty()` (closes "empty file returned as success") and `sha256_checksum()` (partially closes "undetected tampering," by giving the caller a way to check, though nothing forces them to). No new gap was introduced by either change — both are purely additive read-only checks on an already-written file.

## What remains unmitigated, honestly

Concurrency/rate limiting and crash-window temp-file cleanup remain open, matching prior sprints' findings at their respective layers. Neither is addressed in this Sprint's scope, which was explicitly targeted hardening (checksums, filenames, integrity), not a general resource-limits overhaul.
