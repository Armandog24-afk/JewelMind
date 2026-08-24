---
id: JM-BIBLE-A33
title: "Appendix: Compiler Test Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-160
related_documents:
  - JM-BIBLE-A19
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Compiler Test Matrix

## Conformance levels (conceptual, from Sprint 6's scope)

`ALCHEMIST-NORMALIZER`, `ALCHEMIST-VALIDATOR`, `ALCHEMIST-PLANNER`, `ALCHEMIST-ATLAS-EXECUTOR`, `ALCHEMIST-ARTIFACT-ORCHESTRATOR`, `ALCHEMIST-FULL-V1`.

| Level | Requires | Current backend |
|---|---|---|
| `ALCHEMIST-NORMALIZER` | Parses + default-fills a JDL Canonical Document | MET — `JewelryDefinition.model_validate()` |
| `ALCHEMIST-VALIDATOR` | Above + Forge evaluation | MET — `validate_definition()` |
| `ALCHEMIST-PLANNER` | Above + produces a `GeometryPlan` | **NOT MET** — no `GeometryPlan` exists |
| `ALCHEMIST-ATLAS-EXECUTOR` | Above + calls Atlas to produce real geometry | PARTIALLY MET — `build_solitaire_ring()` runs, but directly from the definition, not from a plan |
| `ALCHEMIST-ARTIFACT-ORCHESTRATOR` | Above + produces requested artifacts | MET, per-artifact (not as one unified request) |
| `ALCHEMIST-FULL-V1` | All of the above | **NOT MET**, blocked on `ALCHEMIST-PLANNER` |

## New tests this Sprint

`backend/tests/test_alchemist_registry.py` (5 tests): validates all 8 Alchemist JSON Schemas, validates all 6 examples against their schemas, cross-checks `normalization-vectors.json` against a live `JewelryDefinition.model_validate()` + `definition_hash()` run, verifies the proposed `compilationHash` formula is internally reproducible, and cross-checks `capability-vectors.json` against the real `Literal` type arguments in `domain/schema.py`.

## Existing tests exercising compiler-adjacent behavior

`test_api.py` (generation, export, preview endpoints), `test_validation.py` (Forge evaluation), `test_geometry.py` + `test_atlas_registry.py` (Atlas execution).

## No standalone compiler runtime built

Per this Sprint's explicit instruction, no new runtime compiler component was implemented — the existing backend services already satisfy every behavior this Sprint specifies; only the specification and test-vector layer is new.
