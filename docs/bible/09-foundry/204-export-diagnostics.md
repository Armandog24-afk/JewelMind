---
id: JM-BIBLE-204
title: Export Diagnostics
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-203
related_documents:
  - JM-BIBLE-A37
implementation_status: partial
professional_validation: not_required
normative: true
---

# Export Diagnostics

## The 13 conceptual codes, mapped to real, unmodified public codes

Per FOUNDRY-GOV-010, this Sprint does not rename or introduce any new public `AppError.code` beyond `FOUNDRY_INTEGRITY_FAILED` (already added alongside `exporters/integrity.py`). The 13 codes below are a conceptual, Foundry-namespaced vocabulary for documentation and the machine-readable spec; `realCurrentCode` names what a caller actually receives today.

| Conceptual code | `realCurrentCode` | Notes |
|---|---|---|
| `FOUNDRY_REQUEST_INVALID` | `BAD_REQUEST` | Malformed request body/parameters. |
| `FOUNDRY_EXPORT_BLOCKED` | `MODEL_NOT_FOUND` or `VALIDATION_BLOCKED` | Export requested for a model that doesn't exist, or whose generation never succeeded. |
| `FOUNDRY_COMPONENT_MISSING` | *(none)* | No current code distinguishes "a required component was missing" from a generic export failure — a real, recorded gap. |
| `FOUNDRY_STEP_FAILED` | `STEP_EXPORT_FAILED` | Any exception during `export_step()`. |
| `FOUNDRY_STL_FAILED` | `STL_EXPORT_FAILED` | Any exception during `export_stl()`. |
| `FOUNDRY_JSON_FAILED` | `EXPORT_FAILED` (defined, never raised) | `api/errors.py` defines `ExportFailedError` (code `EXPORT_FAILED`) with a docstring stating it is for "JSON / specification exports," but no route ever imports or raises it — `export_json_route()` has no `try`/`except` at all. A real failure would surface as FastAPI's generic unhandled-exception 500, not the structured `ErrorEnvelope` shape every other export failure uses. A genuine, previously undocumented gap. |
| `FOUNDRY_SPEC_FAILED` | `EXPORT_FAILED` (defined, never raised) | Same gap — `specification_route()` also has no `try`/`except`. |
| `FOUNDRY_FILE_EMPTY` | `FOUNDRY_INTEGRITY_FAILED` | `validate_non_empty()`, this Sprint. |
| `FOUNDRY_FILE_INVALID` | *(none)* | No runtime format-signature check exists for STEP; STL's `binary_stl_triangle_count()` would raise `FOUNDRY_INTEGRITY_FAILED` too, but is only called in tests today, not at runtime. |
| `FOUNDRY_TEMPFILE_ERROR` | *(none)* | A filesystem-level failure (disk full, permissions) during temp-file creation is not distinguished from any other exception. |
| `FOUNDRY_CLEANUP_ERROR` | *(none)* | `destination.unlink(missing_ok=True)` never raises by construction (`missing_ok=True`), so this case cannot currently occur — documented as intentionally unreachable, not as a gap. |
| `FOUNDRY_INTEGRITY_FAILED` | `FOUNDRY_INTEGRITY_FAILED` | The one code that is already identical in both columns — added this Sprint. |
| `FOUNDRY_OPTION_UNSUPPORTED` | *(none)* | No request option validation beyond Pydantic's own type coercion exists; an unsupported combination is not currently possible to request through the real API surface. |

## Never rename or reuse

Per FOUNDRY-GOV-010/FORGE-GOV-001/JDL-GOV-007, once `FOUNDRY_INTEGRITY_FAILED` or any future Foundry-specific code ships, its meaning is permanent. A future change that needs a different meaning gets a new code, never a redefinition of an existing one.

## What this table is not

It is not a claim that 13 distinct error paths exist in the running application today — 3 of the 13 conceptual codes have no dedicated real code at all (honestly marked `*(none)*` above rather than invented), and 2 more (`FOUNDRY_JSON_FAILED`, `FOUNDRY_SPEC_FAILED`) map to a real `AppError` subclass that is defined but never actually raised by any route — itself a real, newly-discovered gap, not a working mechanism. See [`218-foundry-gap-analysis.md`](218-foundry-gap-analysis.md) for whether closing these gaps is worth prioritizing.
