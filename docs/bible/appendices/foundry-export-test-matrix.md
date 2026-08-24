---
id: JM-BIBLE-A38
title: "Appendix: Foundry Export Test Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-190
related_documents:
  - JM-BIBLE-214
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Foundry Export Test Matrix

## 15 test categories considered for this Sprint

| # | Category | Covered? | Where |
|---|---|---|---|
| 1 | Checksum determinism | Yes | `test_export_integrity.py::test_checksum_is_deterministic_and_content_dependent` |
| 2 | Non-empty-file validation (accept real, reject empty) | Yes | `test_export_integrity.py::test_validate_non_empty_accepts_real_file_and_rejects_empty` |
| 3 | STEP roundtrip via re-import | Yes | `test_export_integrity.py::test_step_export_roundtrip_via_reimport` |
| 4 | STL structural roundtrip via binary header parse | Yes | `test_export_integrity.py::test_stl_export_roundtrip_via_binary_header_parse` |
| 5 | StoneReference excluded by default (STEP + STL) | Yes | `test_export_integrity.py::test_step_and_stl_exports_exclude_stone_by_default` |
| 6 | Filename sanitization — safe-character collapsing | Yes | `test_filenames.py` |
| 7 | Filename sanitization — empty/whitespace/dots-only fallback | Yes | `test_filenames.py` |
| 8 | Filename sanitization — length cap | Yes | `test_filenames.py` |
| 9 | Filename sanitization — Windows reserved device names (documents the gap) | Yes | `test_filenames.py::test_windows_reserved_device_names_pass_through_unmodified` |
| 10 | Component-inclusion matrix matches live code | Yes | `test_foundry_registry.py::test_component_inclusion_vectors_match_live_default_export` |
| 11 | All Foundry schemas are valid JSON Schema | Yes | `test_foundry_registry.py::test_all_foundry_schemas_are_valid_json_schema` |
| 12 | All Foundry examples pass their schema | Yes | `test_foundry_registry.py::test_examples_pass_their_schema` |
| 13 | Concurrent export requests don't collide on temp paths | No — not implemented this Sprint | See [`09-foundry/218-foundry-gap-analysis.md`](../09-foundry/218-foundry-gap-analysis.md) `FOUNDRY-GAP-009` |
| 14 | Real external CAD application import test | No — not implemented this Sprint | `FOUNDRY-GAP-007` |
| 15 | Mesh-level (not just structural) STL roundtrip | No — not implemented this Sprint | `FOUNDRY-GAP-006` |

## Test count added this Sprint

`backend/tests/test_export_integrity.py` (5 tests) + `backend/tests/test_filenames.py` (8 tests) + `backend/tests/test_foundry_registry.py` (6 tests) = **19 new tests**. Full backend suite: 194 passed (up from 175 before Sprint 6, 188 after Sprint 6, 194 after this Sprint).
