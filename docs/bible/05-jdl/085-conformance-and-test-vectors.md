---
id: JM-BIBLE-085
title: Conformance Levels and Test Vectors
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-075
  - JM-BIBLE-077
related_documents:
  - JM-BIBLE-A13
implementation_status: partial
professional_validation: not_required
normative: true
---

# Conformance Levels and Test Vectors

## Conformance levels

| Level | Requires | Current JewelMind backend |
|---|---|---|
| **JDL-READER** | Parses Canonical JSON into an in-memory document, applying defaults correctly | MET — `JewelryDefinition.model_validate()` |
| **JDL-VALIDATOR** | JDL-READER, plus structural (`jdl.schema.json`-equivalent) and semantic (rule-engine-equivalent) validation producing the documented diagnostic codes | MET — Pydantic + `validation/engine.py` |
| **JDL-COMPILER** | JDL-VALIDATOR, plus deterministic geometry generation matching [`077-compiler-contract.md`](077-compiler-contract.md) | MET — `build_solitaire_ring()` |
| **JDL-EXPORTER** | JDL-COMPILER, plus real STEP/STL/JSON/specification artifact generation matching [`079-artifact-generation-contract.md`](079-artifact-generation-contract.md) | MET — `exporters/*.py` |
| **JDL-FULL-V1** | All of the above, passing every test-vector group below | MET for the current single-implementation case (see caveat below) |

**Caveat**: JewelMind's own backend is, today, the only implementation of JDL v1 that exists. "Conformant" currently means "matches its own behavior, verified by its own tests" — these levels exist to give a *future*, independent implementation (or a second internal one) a concrete target, not to claim independent interoperability has been demonstrated.

## Required test-vector groups

| Group | Present in `specs/jdl/v1/test-vectors/` or `examples/`? | Count |
|---|---|---|
| valid-minimal | Yes — `examples/minimal-solitaire.json` | 1 |
| valid-default | Yes — `examples/default-solitaire.json` | 1 |
| valid-enum-variations | Yes — `four-prong-solitaire.json`, `six-prong-solitaire.json`, `flat-band-solitaire.json`, `comfort-fit-solitaire.json`, `direct-resin-printing-solitaire.json` | 5 |
| invalid-versions | Yes — `examples/invalid/invalid-schema-version.json`, plus `compatibility-vectors.json` | 1 example + 4 vector rows |
| invalid-types | Yes — `examples/invalid/invalid-non-finite-number.json` | 1 |
| invalid-ranges | Yes — `examples/invalid/invalid-negative-dimension.json`, `invalid-basket-height.json` | 2 |
| invalid-enum-values | Yes — `examples/invalid/invalid-prong-count.json` (an out-of-set integer, not an out-of-enum string, since `prongCount` is typed `int` rather than a `Literal` — see [`072-identifiers-enums-and-naming.md`](072-identifiers-enums-and-naming.md)) | 1 |
| incompatible-semantic-combinations | Covered by `invalid-basket-height.json` (also fails an implicit `prongHeight > basketHeight` check path) and by the multi-error case in `invalid-negative-dimension.json` (fires both `JM-BAND-001` and `JM-GEOMETRY-001`) | 2 |
| canonicalization-equivalence | Yes — `canonicalization-vectors.json` (three documents proven byte-identical to the default) | 3 equivalence pairs |
| stable-definition-hash | Yes — `definition-hash-vectors.json` | 10 rows |
| expected-validation-diagnostics | Yes — `validation-vectors.json` | 10 rows |
| expected-component-manifest | **Not present as a standalone test-vector file** — component manifest shape is documented in [`078-geometry-generation-contract.md`](078-geometry-generation-contract.md) and exercised by `backend/tests/test_geometry.py`, but no `component-manifest-vectors.json` was generated this Sprint | 0 — gap, recorded in `SPRINT-3-VALIDATION-REPORT.md` |

## Automated tests

`backend/tests/test_jdl_schema_examples.py` (added this Sprint) automatically:

- Validates every valid example against `jdl.schema.json`.
- Rejects every invalid example for its documented reason (Pydantic construction failure, or the exact expected `ruleId` set from `validate_definition()`).
- Compares canonicalization and hash vectors against a live run of `canonical_json()`/`definition_hash()`.
- Compares schema-version compatibility vectors against a live run of `JewelryDefinition.model_validate()`.

It does **not** implement a textual DSL parser test (none exists to test, per this milestone's explicit scope) and does not yet assert a machine-checked component-manifest vector file (the gap noted above).

## What "confirming TypeScript defaults match the normative default example" actually checks

`frontend/src/store/useProjectStore.test.ts` and `shared/types/jewelry-definition.ts::createDefaultDefinition()` already assert the frontend's default matches the fields in this Sprint's `examples/default-solitaire.json` field-for-field (both were compared by hand during [`084-current-implementation-mapping.md`](084-current-implementation-mapping.md)'s inspection) — this Sprint did not add a new automated cross-check between the TypeScript default and the JSON example file itself; that remains a manual-inspection guarantee today, recorded as a candidate for a future automated check.
