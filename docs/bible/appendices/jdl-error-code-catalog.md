---
id: JM-BIBLE-A11
title: "Appendix: JDL Error Code Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-080
related_documents:
  - JM-BIBLE-054
implementation_status: current
professional_validation: preliminary
normative: true
---

# Appendix: JDL Error Code Catalog

Every diagnostic code that actually exists in the current codebase, verbatim — none renamed for this catalog (JDL-GOV-007). See [`080-errors-warnings-and-diagnostics.md`](../05-jdl/080-errors-warnings-and-diagnostics.md) for the conceptual namespace grouping.

## Semantic/domain rule codes (`ValidationResult.ruleId`, from `backend/jewelmind/validation/rules.py`)

| Code | Severity | Parameter | Message | File |
|---|---|---|---|---|
| `JM-RING-001` | error | `ring.innerDiameter` | Ring inner diameter must be greater than 10 mm and lower than 30 mm. | `validation/engine.py::_ring_rules` |
| `JM-RING-002` | error | `ring.size` | EU ring size must be greater than 1 and lower than 50. | same |
| `JM-RING-003` | information or warning | `ring.innerDiameter` | Size/diameter consistency discrepancy, with a suggested value | same, via `validation/sizing.py` |
| `JM-BAND-001` | error | `band.width` | Band width below 1.5 mm is not supported. | `_band_rules` |
| `JM-BAND-002` | error or warning | `band.thickness` | Below 1.4mm: error, "not supported"; below 1.6mm: warning, "may be structurally fragile" | same |
| `JM-BAND-003` | warning | `band.width` | Band width above 12 mm is unusually wide for a solitaire band. | same |
| `JM-STONE-001` | error | `stone.diameter` | Stone diameter must be between 2 mm and 15 mm. | `_stone_rules` |
| `JM-STONE-002` | error | `stone.depth` | Stone depth must be greater than 0.5 mm and lower than the stone diameter. | same |
| `JM-PRONG-001` | error | `setting.prongCount` | Prong count must be exactly 4 or 6. | `_prong_rules` |
| `JM-PRONG-002` | error or warning | `setting.prongDiameter` | Below 0.8mm: error; below 1.0mm: warning | same |
| `JM-PRONG-003` | warning | `setting.prongCount` | Stones larger than 8 mm are typically more secure with six prongs. | same |
| `JM-PRONG-004` | error | `setting.prongHeight` | Prong height must be greater than basket height. | same |
| `JM-SETTING-001` | error | `setting.basketHeight` | Basket height must be positive. | `_setting_rules` |
| `JM-SETTING-002` | warning | `setting.basketHeight` | Basket height above 8 mm is unusually tall. | same |
| `JM-MANUFACTURING-001` | warning | `band.thickness` or `band.width` | Feature may not print reliably under 0.8mm with direct resin printing. | `_manufacturing_rules` |
| `JM-GEOMETRY-001` | error | `band.thickness` or `band.width` | Band thickness/width must produce a valid, positive outer band dimension. | `_geometry_rules` |

## HTTP-level application error codes (`AppError.code`, from `backend/jewelmind/api/errors.py`)

| Code | HTTP status | Meaning |
|---|---|---|
| `VALIDATION_BLOCKED` | 422 | At least one `error`-severity `ValidationResult` exists; generation/export refused |
| `MODEL_NOT_FOUND` | 404 | No cached `ModelRecord` for the requested `model_id` (never generated, or evicted from the 20-entry cache) |
| `MODEL_GENERATION_FAILED` | 500 | Geometry generation raised an unexpected exception |
| `EXPORT_FAILED` | 500 | Generic JSON/specification export failure |
| `STEP_EXPORT_FAILED` | 500 | STEP-specific export failure |
| `STL_EXPORT_FAILED` | 500 | STL-specific export failure |
| `BAD_REQUEST` | 400 | Malformed request not covered by a more specific code |
| `CAD_ENGINE_UNAVAILABLE` | 503 | CadQuery/OpenCascade failed its startup health probe in this process |
| `INTERNAL_ERROR` | 500 | `AppError` default; an unclassified failure |
| `REQUEST_VALIDATION_ERROR` | 422 | FastAPI/Pydantic request-body structural validation failure (the JDL-SCHEMA layer) |

## Deprecation policy

No code in either table has ever been deprecated. Per JDL-GOV-007, if a code is ever deprecated, it is marked here as `deprecated` with the version it was deprecated in and the replacement code (if any) — never silently removed from this catalog or reused for a different meaning.

**Total current codes catalogued: 16 semantic rule codes + 10 application error codes = 26.**
