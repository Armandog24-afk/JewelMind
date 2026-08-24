---
id: JM-BIBLE-A37
title: "Appendix: Foundry Export Diagnostic Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-204
related_documents:
  - JM-BIBLE-A31
implementation_status: partial
professional_validation: not_required
normative: true
---

# Appendix: Foundry Export Diagnostic Catalog

Restates [`09-foundry/204-export-diagnostics.md`](../09-foundry/204-export-diagnostics.md)'s mapping as a standalone reference table, kept in sync with `specs/foundry/v1/export-diagnostic.schema.json`.

| Conceptual code | `realCurrentCode` | HTTP status |
|---|---|---|
| `FOUNDRY_REQUEST_INVALID` | `BAD_REQUEST` | 400 |
| `FOUNDRY_EXPORT_BLOCKED` | `MODEL_NOT_FOUND` / `VALIDATION_BLOCKED` | 404 / 422 |
| `FOUNDRY_COMPONENT_MISSING` | *(none)* | n/a |
| `FOUNDRY_STEP_FAILED` | `STEP_EXPORT_FAILED` | 500 |
| `FOUNDRY_STL_FAILED` | `STL_EXPORT_FAILED` | 500 |
| `FOUNDRY_JSON_FAILED` | `EXPORT_FAILED` (class defined, never raised — see `09-foundry/204`) | n/a (unhandled 500 today) |
| `FOUNDRY_SPEC_FAILED` | `EXPORT_FAILED` (same gap) | n/a (unhandled 500 today) |
| `FOUNDRY_FILE_EMPTY` | `FOUNDRY_INTEGRITY_FAILED` | 500 |
| `FOUNDRY_FILE_INVALID` | *(none)* | n/a |
| `FOUNDRY_TEMPFILE_ERROR` | *(none)* | n/a |
| `FOUNDRY_CLEANUP_ERROR` | *(none — intentionally unreachable, see `09-foundry/204`)* | n/a |
| `FOUNDRY_INTEGRITY_FAILED` | `FOUNDRY_INTEGRITY_FAILED` | 500 |
| `FOUNDRY_OPTION_UNSUPPORTED` | *(none)* | n/a |

Actual `AppError` status codes confirmed by inspecting `backend/jewelmind/api/errors.py` directly.
