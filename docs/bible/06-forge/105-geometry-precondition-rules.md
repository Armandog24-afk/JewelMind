---
id: JM-BIBLE-105
title: Geometry Precondition Rules
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-093
related_documents:
  - JM-BIBLE-132
implementation_status: current
professional_validation: preliminary
normative: true
---

# Geometry Precondition Rules

Rules that must pass before `build_solitaire_ring()` is called at all — the FORGE-3 stage in [`096-rule-evaluation-pipeline.md`](096-rule-evaluation-pipeline.md).

**Relationship to Atlas (Sprint 5):** FORGE-3 corresponds to `ATLAS-0`
("receive validated geometry plan") in
[`07-atlas/132-construction-pipeline.md`](../07-atlas/132-construction-pipeline.md)
— by the time Atlas begins construction, every rule in this document has
already passed. Atlas itself additionally guarantees a small number of
pure-implementation preconditions (e.g. a non-positive height cannot
become a solid) that are geometry-engineering facts, not Forge rules —
see [`07-atlas/124-geometric-primitives.md`](../07-atlas/124-geometric-primitives.md)
for the primitive-level invariants Atlas itself relies on.

| Rule | Precondition | Code | Test |
|---|---|---|---|
| `JM-GEOMETRY-001` | `band.thickness > 0` and `ring.innerDiameter + 2×band.thickness > ring.innerDiameter`, and `band.width > 0` | `backend/jewelmind/validation/engine.py::_geometry_rules` | `backend/tests/test_validation.py` |
| `JM-SETTING-001` | `setting.basketHeight > 0` | `backend/jewelmind/validation/engine.py::_setting_rules` | `backend/tests/test_validation.py` |
| `FORGE-SCHEMA-001` | `schemaVersion == "0.1.0"` | `backend/jewelmind/domain/schema.py::JewelryDefinition.schemaVersion` | `backend/tests/test_schema.py` |
| `FORGE-SAFETY-001` | Every numeric field is finite (no NaN/Infinity) | `backend/jewelmind/domain/schema.py` (`allow_inf_nan=False` on every `float` field) | `backend/tests/test_schema_safety.py` |

## Not duplicated here

`setting.prongCount ∈ {4, 6}` (`JM-PRONG-001`) and `stone.shape == "round"` (a fixed `Literal`) are both preconditions in the sense that a geometry builder could not sensibly handle an unsupported value, but they are documented once, in [`093-rule-classification-model.md`](093-rule-classification-model.md) (as `PROTOTYPE_HEURISTIC` and `SCHEMA_INTEGRITY` respectively) and [`04-jewelry-domain/`](../04-jewelry-domain/README.md)'s taxonomy documents, rather than re-listed here — this document only covers rules whose primary classification is `GEOMETRY_PRECONDITION`, per [`093-rule-classification-model.md`](093-rule-classification-model.md), to avoid duplicating the same fact across three documents.

## Every current precondition maps to real code and tests

No precondition in this document is aspirational — each row above cites the exact function and the exact test file that exercises it, confirmed by direct inspection during this Sprint.
