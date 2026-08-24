# JDL v1 Compiler Contract — Machine Reference

Normative narrative: [`docs/bible/05-jdl/077-compiler-contract.md`](../../../docs/bible/05-jdl/077-compiler-contract.md).
This file maps the conceptual `CompilationResult` directly onto the current backend types, for implementers.

## Current backend types this contract is grounded in

- `backend/jewelmind/services/model_service.py::ModelService.generate()` — the closest thing to a "compile" entry point today.
- `backend/jewelmind/services/model_service.py::ModelRecord` — `model_id`, `definition`, `generated_model`, `validation_results`, `preview_manifest`, `temp_dir`, `generated_at`.
- `backend/jewelmind/geometry/model.py::GeneratedModel` — `definition_hash`, `generator_version`, `generation_duration_s`, `components` (name → `GeneratedComponent`), `combined_metal`, `combined_metal_volume_mm3`, `bounding_box`, `warnings`.
- `backend/jewelmind/geometry/model.py::GeneratedComponent` — `name`, `shape`, `volume_mm3`, `bounding_box`, `warnings`, `metadata`.

## Conceptual `CompilationResult` → current implementation mapping

| Conceptual field | Current source | Status |
|---|---|---|
| Source schema version | `definition.schemaVersion` | CURRENT |
| Compiler version | `GENERATOR_VERSION` (`backend/jewelmind/geometry/constants.py`, currently `"0.1.0"`) | CURRENT — a distinct constant from `schemaVersion` that presently happens to hold the same string; do not assume they move together (see [`081-schema-versioning-and-migrations.md`](../../../docs/bible/05-jdl/081-schema-versioning-and-migrations.md)) |
| Definition hash | `GeneratedModel.definition_hash` (= `definition_hash(definition)`) | CURRENT |
| Normalized definition | The `JewelryDefinition` instance itself, post-Pydantic-defaulting | CURRENT |
| Validation diagnostics | `ModelRecord.validation_results` (`list[ValidationResult]`) | CURRENT |
| Geometry plan | Not materialized as a separate artifact — `build_solitaire_ring()` goes directly from definition to components | PARTIAL (planning and generation are one undivided step today; see [`063-jdl-processing-model.md`](../../../docs/bible/05-jdl/063-jdl-processing-model.md) JDL-6/JDL-7) |
| Generated component manifest | `GeneratedModel.components` + `ModelRecord.preview_manifest` | CURRENT |
| Geometry metadata | `GeneratedComponent.volume_mm3`, `.bounding_box`, `GeneratedModel.combined_metal_volume_mm3`, `.bounding_box` | CURRENT |
| Generation warnings | `GeneratedComponent.warnings` (per component) + `GeneratedModel.warnings` (assembly-level) | CURRENT |
| Generated artifacts | Not persisted as part of the record — STEP/STL/JSON/spec are generated on demand per export request (`export_step_file`, `export_stl_file`, `export_json_text`, `export_specification_text`) | PARTIAL — "artifact generation" is a caller-triggered side effect, not part of `generate()`'s own output |
| Timing | `GeneratedModel.generation_duration_s` | CURRENT |
| Success/failure | `generate()` either returns a `ModelRecord` or raises `ValidationBlockedError`/an unhandled generation exception; there is no unified success/failure result object | PARTIAL |

## Phases (current call sequence inside `ModelService.generate()`)

1. **Normalize** — implicit: `JewelryDefinition.model_validate()` already ran before `generate()` is called (in `api/routes.py`), filling defaults.
2. **Validate** — `validate_definition(definition)`. If `has_errors(results)`, raise `ValidationBlockedError` and stop. Nothing past this point runs.
3. **Plan + Generate** — `build_solitaire_ring(definition)`, a single undivided call producing a `GeneratedModel`.
4. **Inspect** — implicit in step 3's return value (volumes, bounding boxes, warnings already computed by the geometry builders); no separate inspection pass exists.
5. **Report** — `write_component_previews(...)` builds the preview manifest; the `ModelRecord` is assembled and cached.
6. **Export** (separate, caller-triggered, not part of `generate()`) — `export_step_file` / `export_stl_file` / `export_json_text` / `export_specification_text`.

## Determinism requirement

For a fixed `JewelryDefinition` and a fixed `GENERATOR_VERSION`, `build_solitaire_ring()` must produce the same `combined_metal_volume_mm3`, the same per-component volumes, and the same `definition_hash` on every call, on every machine. This is the same guarantee CLAUDE.md calls "Preserve CAD determinism" and is not weakened or extended by this contract.

## Prohibited compiler behaviors (unchanged from current code, restated for this contract)

- Silently changing user intent (e.g. clamping an out-of-range dimension instead of reporting a validation error).
- Inventing missing components not implied by the definition.
- Ignoring validation errors (`has_errors()` must gate generation — it does, in `generate()`).
- Fusing the stone into the production metal body (`combined_metal` must never include the stone; see LAW-006 and [`housing 052-parametric-dependency-model.md`](../../../docs/bible/04-jewelry-domain/052-parametric-dependency-model.md)).
- Silently dropping a failed component instead of falling back to a documented degraded form (see `docs/known-limitations.md` and `stl_exporter.py`'s multi-solid-compound fallback).
- Non-deterministic output for the same input.
- LLM-dependent geometry decisions of any kind.
- Hiding fallback geometry from the caller (a fallback must surface as a `warnings` entry, not disappear silently).
