---
id: JM-BIBLE-110
title: Current Rule Inventory
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-109
related_documents:
  - JM-BIBLE-A14
implementation_status: current
professional_validation: preliminary
normative: true
---

# Current Rule Inventory

Every rule below was found by inspecting `backend/jewelmind/validation/rules.py`, `engine.py`, `backend/jewelmind/domain/schema.py`, `backend/jewelmind/geometry/assemblies/solitaire.py`, and `backend/jewelmind/api/errors.py` directly during this Sprint, cross-checked against `shared/validation/engine.ts` and `backend/tests/`. **No preliminary threshold is called a professional rule.**

| Rule ID | Description | Code | Test | Condition | Severity | Blocking | Classification | Provenance | Prof. validation | Geometry influence | Manufacturing influence | Frontend duplication | Lifecycle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `JM-RING-001` | Inner diameter range | `engine.py::_ring_rules` | `test_validation.py` | `10 < innerDiameter < 30` | error | Yes | PROTOTYPE_HEURISTIC | prototype_heuristic | preliminary | Yes (band radius) | No | Exact mirror in `engine.ts` | ACCEPTED |
| `JM-RING-002` | EU size range | `engine.py::_ring_rules` | `test_validation.py` | `1 < size < 50` | error | Yes | PROTOTYPE_HEURISTIC | prototype_heuristic | preliminary | No | No | Exact mirror | ACCEPTED |
| `JM-RING-003` | Size/diameter consistency | `engine.py::_ring_rules` + `sizing.py` | `test_validation.py` | discrepancy thresholds 0.15mm/0.5mm | information/warning | No | SEMANTIC_COMPATIBILITY | mathematical_constraint | preliminary | No | No | Exact mirror | ACCEPTED |
| `JM-BAND-001` | Minimum band width | `engine.py::_band_rules` | `test_validation.py` | `width < 1.5` | error | Yes | PROTOTYPE_HEURISTIC | prototype_heuristic | preliminary | Yes | No | Exact mirror | ACCEPTED |
| `JM-BAND-002` | Minimum band thickness | `engine.py::_band_rules` | `test_validation.py` | `thickness < 1.4` error, `< 1.6` warning | error/warning | Conditional | PROTOTYPE_HEURISTIC | prototype_heuristic | preliminary | Yes | No | Exact mirror | ACCEPTED |
| `JM-BAND-003` | Maximum band width advisory | `engine.py::_band_rules` | `test_validation.py` | `width > 12` | warning | No | PROTOTYPE_HEURISTIC | prototype_heuristic | preliminary | No | No | Exact mirror | ACCEPTED |
| `JM-STONE-001` | Stone diameter range | `engine.py::_stone_rules` | `test_validation.py` | `2 <= diameter <= 15` | error | Yes | PROTOTYPE_HEURISTIC | prototype_heuristic | preliminary | Yes | No | Exact mirror | ACCEPTED |
| `JM-STONE-002` | Depth vs. diameter | `engine.py::_stone_rules` | `test_validation.py` | `0.5 < depth < diameter` | error | Yes | DOMAIN_INVARIANT | mathematical_constraint | preliminary | Yes | No | Exact mirror | ACCEPTED |
| `JM-PRONG-001` | Prong count set | `engine.py::_prong_rules` | `test_validation.py`, `test_geometry.py` | `prongCount ∈ {4, 6}` | error | Yes | PROTOTYPE_HEURISTIC | prototype_heuristic | preliminary | Yes | No | Exact mirror | ACCEPTED |
| `JM-PRONG-002` | Prong diameter minimum | `engine.py::_prong_rules` | `test_validation.py` | `< 0.8` error, `< 1.0` warning | error/warning | Conditional | PROTOTYPE_HEURISTIC | prototype_heuristic | preliminary | Yes | No | Exact mirror | ACCEPTED |
| `JM-PRONG-003` | Prong count vs. stone size advisory | `engine.py::_prong_rules` | `test_validation.py` | `stone.diameter > 8 and prongCount == 4` | warning | No | PROTOTYPE_HEURISTIC | prototype_heuristic | preliminary | No | No | Exact mirror | ACCEPTED |
| `JM-PRONG-004` | Prong height vs. basket height | `engine.py::_prong_rules` | `test_validation.py` | `prongHeight > basketHeight` | error | Yes | SEMANTIC_COMPATIBILITY | geometry_engine_constraint | preliminary | Yes | No | Exact mirror | ACCEPTED |
| `JM-SETTING-001` | Basket height positivity | `engine.py::_setting_rules` | `test_validation.py` | `basketHeight <= 0` | error | Yes | GEOMETRY_PRECONDITION | implementation_necessity | preliminary | Yes | No | Exact mirror | ACCEPTED |
| `JM-SETTING-002` | Basket height maximum advisory | `engine.py::_setting_rules` | `test_validation.py` | `basketHeight > 8` | warning | No | PROTOTYPE_HEURISTIC | prototype_heuristic | preliminary | No | No | Exact mirror | ACCEPTED |
| `JM-MANUFACTURING-001` | Minimum feature size for resin printing | `engine.py::_manufacturing_rules` | `test_validation.py` | `method == direct_resin_printing and (band.thickness or band.width) < 0.8` | warning | No | MANUFACTURING_CONTEXT | prototype_heuristic | preliminary | No | Yes | Exact mirror | ACCEPTED |
| `JM-GEOMETRY-001` | Positive outer band dimension | `engine.py::_geometry_rules` | `test_validation.py` | `thickness <= 0` or `outer <= inner`, or `width <= 0` | error | Yes | GEOMETRY_PRECONDITION | implementation_necessity | preliminary | Yes | No | Exact mirror | ACCEPTED |
| `FORGE-SCHEMA-001` | Schema version literal | `schema.py::JewelryDefinition.schemaVersion` | `test_schema.py`, `test_jdl_schema_examples.py` | `schemaVersion == "0.1.0"` | fatal (structural) | Yes | SCHEMA_INTEGRITY | implementation_necessity | not_required | No | No | Frontend has an exact-match runtime guard, not a `ValidationResult`-shaped rule | ACCEPTED |
| `FORGE-SAFETY-001` | No non-finite numbers | `schema.py` (`allow_inf_nan=False`) | `test_schema_safety.py` | any float field is NaN/Infinity | fatal (structural) | Yes | SYSTEM_SAFETY | implementation_necessity | not_required | No | No | Frontend `isFiniteNumber()` guard, not a `ValidationResult`-shaped rule | ACCEPTED |
| `FORGE-SAFETY-002` | No unknown fields | `schema.py::StrictModel` (`extra="forbid"`) | `test_schema.py`, `test_jdl_schema_examples.py` | any unrecognized key | fatal (structural) | Yes | SYSTEM_SAFETY | implementation_necessity | not_required | No | No | TypeScript's structural typing achieves a similar effect at compile time only, not at runtime | ACCEPTED |
| `FORGE-GEOM-001` | Fuse must yield a solid | `geometry/assemblies/solitaire.py::_fuse_metal` | `test_geometry.py` | `not fused.Solids()` | warning | No | GEOMETRY_INSPECTION | geometry_engine_constraint | not_required | Yes | No | None — no frontend equivalent exists | ACCEPTED |
| `FORGE-EXPORT-001` | Export requires a valid cached record | `services/model_service.py::get_record` + `api/errors.py` | `test_api.py` | `model_id` not found, or generation was previously blocked | error-equivalent (404/422) | Yes, for the requested export | EXPORT_PRECONDITION | implementation_necessity | not_required | No | No | Frontend's `isStale` check is a *different*, non-equivalent precondition — see [`107-export-precondition-rules.md`](107-export-precondition-rules.md) | ACCEPTED |

## Frontend/backend rule mismatches found

**None among the 16 `JM-*` rules.** `shared/validation/engine.ts` is a byte-for-byte behavioral mirror of `backend/jewelmind/validation/engine.py` — same rule IDs, same thresholds, same severities, same messages, confirmed by direct side-by-side inspection during this Sprint. The only genuine frontend/backend divergence found is **not** a rule-threshold mismatch but a **precondition-scope** mismatch: the frontend's `isStale` export gate has no backend-side equivalent (see [`107-export-precondition-rules.md`](107-export-precondition-rules.md)).
