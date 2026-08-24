---
id: JM-BIBLE-075
title: Validation Pipeline
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-063
  - JM-BIBLE-074
related_documents:
  - JM-BIBLE-080
implementation_status: partial
professional_validation: preliminary
normative: true
---

# Validation Pipeline

**Passing every layer below does not certify manufacturability.** No layer in this pipeline, individually or combined, constitutes professional review — see LAW-010 and [`04-jewelry-domain/040-domain-governance.md`](../04-jewelry-domain/040-domain-governance.md).

| Layer | Authority | Input | Output | Severity | Blocks generation | Blocks export | Implemented | Files | Tests |
|---|---|---|---|---|---|---|---|---|---|
| 1. Parser | JSON parser | Raw request body | Parsed object or a parse failure | fatal | yes | yes | CURRENT | FastAPI/Starlette body decoding | `test_api_hardening.py` |
| 2. Structural schema | Pydantic (authoritative); `jdl.schema.json` (non-authoritative mirror) | Parsed object | `JewelryDefinition` or `ValidationError` | fatal | yes | yes | CURRENT | `domain/schema.py` | `test_schema.py`, `test_schema_safety.py`, `test_jdl_schema_examples.py` |
| 3. Canonicalization | `hashing.py` | `JewelryDefinition` | Canonical JSON string + hash | n/a (not a rejection layer) | no | no | CURRENT | `utils/hashing.py` | `test_jdl_schema_examples.py` |
| 4. Semantic/compatibility | `validation/engine.py` (JDL-5 rules) | `JewelryDefinition` | `ValidationResult` list | error/warning/information | yes (errors only) | yes (errors only) | CURRENT | `validation/engine.py` | `test_validation.py` |
| 5. Preliminary jewelry-domain | `validation/engine.py` (JDL-6 rules; same engine) | `JewelryDefinition` | `ValidationResult` list | error/warning/information | yes (errors only) | yes (errors only) | CURRENT | same | same |
| 6. Geometry precondition | `ModelService.generate()` | Validation results | `has_errors()` gate | n/a | yes | n/a (upstream of export) | CURRENT | `services/model_service.py` | `test_api.py::test_generate_invalid_definition_returns_422` |
| 7. Generated-geometry inspection | Geometry builders | `GeneratedModel` | volumes, bounding boxes, per-component warnings | information (warnings only; no rejection layer here) | no | no | CURRENT | `geometry/model.py`, `geometry/assemblies/solitaire.py` | `test_geometry.py` |
| 8. Export | Exporters | `GeneratedModel` + definition | STEP/STL/JSON/spec files, or an export error | error (on failure) | n/a | yes | CURRENT | `exporters/*.py` | `test_api.py` |
| 9. Professional manufacturing review | A qualified jewelry professional | The exported artifact | Human sign-off (or not) | n/a — outside software | n/a | n/a | NOT IMPLEMENTED — no such review has ever occurred for any output of this system | [`04-jewelry-domain/058-professional-validation-register.md`](../04-jewelry-domain/058-professional-validation-register.md) | n/a |

## Structural vs. semantic validation — kept separate on purpose

Layer 2 (structural) enforces types, literal/enum membership, and `additionalProperties: false`. It deliberately does **not** enforce positive-dimension constraints, prong-count set membership, or basket-height range — those are Layer 4/5 (semantic) rules by design, so an out-of-range value produces a structured `ValidationResult` (with a `ruleId`, a `severity`, a suggested value) instead of an opaque Pydantic type error. `backend/jewelmind/domain/schema.py`'s own comment on `SettingSpec.prongCount` states this explicitly for that field; the same principle applies to every dimension field that has no `gt=0` constraint in Pydantic (see [`specs/jdl/v1/jdl.schema.json`](../../../specs/jdl/v1/jdl.schema.json)'s per-field `description` text for the complete list).

## Warnings never block

Per LAW-009, only `error`-severity results block generation/export (Layer 6/8's gate is `has_errors()`, which checks severity, not presence). A document with only `warning`/`information` results generates and exports normally — proven by every valid example in `specs/jdl/v1/examples/` returning zero validation results at all, and by the semantic-rule table in [`074-semantic-rules.md`](074-semantic-rules.md) showing which rules are warning-only.
