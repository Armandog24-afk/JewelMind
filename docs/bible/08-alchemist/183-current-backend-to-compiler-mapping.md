---
id: JM-BIBLE-183
title: Current Backend to Compiler Mapping
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-162
related_documents:
  - JM-BIBLE-A32
implementation_status: current
professional_validation: not_required
normative: true
---

# Current Backend to Compiler Mapping

Every file classified by its actual responsibility, confirmed by direct inspection during this Sprint.

| Responsibility | File(s) | Classification |
|---|---|---|
| Request parsing | `api/routes.py`, `api/schemas.py` | API |
| Validation | `validation/rules.py`, `validation/engine.py`, `validation/sizing.py` | FORGE |
| Orchestration (validate → generate → cache → preview) | `services/model_service.py::ModelService.generate()` | **ALREADY_ALCHEMIST_LIKE** |
| Model retrieval/caching | `services/model_service.py`'s `_records`, `get_record()`, eviction logic | **ALREADY_ALCHEMIST_LIKE** (cache orchestration) / MIXED_RESPONSIBILITY (also owns temp-directory lifecycle, an Atlas/Foundry-adjacent concern) |
| Component building | `geometry/components/*.py` | ATLAS |
| Assembly + boolean strategy | `geometry/assemblies/solitaire.py` | ATLAS |
| Derived-parameter calculation | `geometry/constants.py` | ATLAS (today) / conceptually ALCHEMIST planning (see [`167-geometry-plan-generation.md`](167-geometry-plan-generation.md)) |
| Preview tessellation | `preview/mesh.py` | VISION (generation half) — but invoked **inline inside** `ModelService.generate()`, so also **MIXED_RESPONSIBILITY** at the call-site level |
| STEP/STL export | `exporters/step_exporter.py`, `stl_exporter.py` | FOUNDRY (Sprint 7) — but each directly imports and calls `cq.Compound.makeCompound()`, a small ATLAS-adjacent operation performed outside `geometry/` (see [`168-atlas-execution-contract.md`](168-atlas-execution-contract.md)) — **MIXED_RESPONSIBILITY** |
| JSON/specification export | `exporters/json_exporter.py`, `specification.py` | FOUNDRY |
| Model IDs | `model_id = generated_model.definition_hash` (`services/model_service.py`) | ALREADY_ALCHEMIST_LIKE (identity assignment) |
| Definition hashing | `utils/hashing.py` | JDL |
| Error handling | `api/errors.py` | API |
| CAD engine health probe | `services/cad_engine.py` | ATLAS-adjacent (kernel lifecycle) |
| Filename sanitization | `exporters/filenames.py` | FOUNDRY |

## Architecture debt, named plainly

`ModelService.generate()` is the single largest concentration of `MIXED_RESPONSIBILITY` in the codebase — it performs real orchestration (Forge gate → Atlas call → Vision-generation call, in sequence) while also directly managing filesystem lifecycle (temp directories) that arguably belongs to a lower-level Atlas/Foundry concern, and while coupling preview generation to core geometry generation (see [`172-diagnostics-and-failure-propagation.md`](172-diagnostics-and-failure-propagation.md)). This is not presented as an urgent problem — the code is correct and fully tested — but it is the clearest concrete evidence for why Alchemist as a formally separate layer does not yet exist in code, only in this specification.

## Compiler-like services discovered

**1**: `ModelService`. No other module in the codebase performs cross-layer orchestration at this scope.

## Mixed-responsibility modules found

**3**: `ModelService.generate()` (orchestration + preview generation + temp-directory lifecycle), `exporters/step_exporter.py` and `exporters/stl_exporter.py` (Foundry-layer code directly calling a CAD-kernel compound operation).
