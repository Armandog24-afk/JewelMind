---
id: JM-BIBLE-A19
title: "Appendix: Forge Rule Test Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-112
related_documents:
  - JM-BIBLE-A02
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Forge Rule Test Matrix

| Rule ID | Unit test | Boundary test | Geometry-integration test |
|---|---|---|---|
| `JM-RING-001` | `test_validation.py` | Implicit (range endpoints not separately isolated) | — |
| `JM-RING-002` | `test_validation.py` | Implicit | — |
| `JM-RING-003` | `test_validation.py` | Implicit (0.15mm/0.5mm thresholds) | — |
| `JM-BAND-001` | `test_validation.py` | Implicit | `test_geometry.py` (band construction) |
| `JM-BAND-002` | `test_validation.py` | **Explicit** — `test_forge_registry.py::test_jm_rule_severities_match_live_validation_engine` (1.3 vs 1.5) | `test_geometry.py` |
| `JM-BAND-003` | `test_validation.py` | Implicit | — |
| `JM-STONE-001` | `test_validation.py` | Implicit | `test_geometry.py` |
| `JM-STONE-002` | `test_validation.py` | Implicit | `test_geometry.py` |
| `JM-PRONG-001` | `test_validation.py` | Implicit | `test_geometry.py` (`test_prongs_four_count`, `test_prongs_default_count_is_six`) |
| `JM-PRONG-002` | `test_validation.py` | **Explicit** — `test_forge_registry.py` (0.7 vs 0.9) | — |
| `JM-PRONG-003` | `test_validation.py` | Implicit | — |
| `JM-PRONG-004` | `test_validation.py` | Implicit | — |
| `JM-SETTING-001` | `test_validation.py` | Implicit | — |
| `JM-SETTING-002` | `test_validation.py` | Implicit | — |
| `JM-MANUFACTURING-001` | `test_validation.py` | Implicit | — |
| `JM-GEOMETRY-001` | `test_validation.py` | Implicit | `test_geometry.py` |
| `FORGE-SCHEMA-001` | `test_schema.py`, `test_jdl_schema_examples.py` | Explicit (`invalid-schema-version.json`) | — |
| `FORGE-SAFETY-001` | `test_schema_safety.py` | Explicit (`invalid-non-finite-number.json`) | — |
| `FORGE-SAFETY-002` | `test_schema.py` | — | — |
| `FORGE-GEOM-001` | — | — | `test_geometry.py::test_solitaire_assembly_metal_is_single_fused_solid_by_default` |
| `FORGE-EXPORT-001` | `test_api.py` | — | — |

## New this Sprint

`backend/tests/test_forge_registry.py` (11 tests): validates every Forge JSON Schema, validates the current rule registry against its schema, validates all 2 valid + rejects all 4 invalid rule examples, checks for duplicate registry IDs, and cross-checks `JM-BAND-002`/`JM-PRONG-002`'s boundary behavior plus the multi-rule-firing and invalid-example evaluation vectors against a live run of the real validation engine.

## Test gaps

Per [`06-forge/112-rule-testing-strategy.md`](../06-forge/112-rule-testing-strategy.md): no dedicated boundary-value matrix exists as a standalone artifact for the 14 rules marked "Implicit" above (their boundary behavior is covered incidentally by existing tests using round-number inputs, not by tests specifically designed to probe the exact threshold edge); no property-based/fuzz testing exists anywhere in this codebase; no conflict, profile, or professional-validation tests exist because none of those scenarios currently occur in the real system.
