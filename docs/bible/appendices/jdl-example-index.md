---
id: JM-BIBLE-A13
title: "Appendix: JDL Example Index"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-085
related_documents:
  - JM-BIBLE-A11
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: JDL Example Index

Every example in `specs/jdl/v1/examples/` and `specs/jdl/v1/examples/invalid/`, with the exact, verified reason it passes or fails. All results below were produced by actually running `jsonschema` and the real `validation/engine.py` against each file during this Sprint (see `backend/tests/test_jdl_schema_examples.py`), not inferred.

## Valid examples (7)

| File | `definitionHash` | Illustrates |
|---|---|---|
| `default-solitaire.json` | `355ddca57e7e49ad` | The full explicit default document |
| `minimal-solitaire.json` | `355ddca57e7e49ad` | A minimal authored document (`{"schemaVersion": "0.1.0"}`) that default-fills to the identical canonical document |
| `six-prong-solitaire.json` | `355ddca57e7e49ad` | Explicit `prongCount: 6`, identical to the default value |
| `comfort-fit-solitaire.json` | `355ddca57e7e49ad` | Explicit `band.profile: "comfort_fit"`, identical to the default value |
| `four-prong-solitaire.json` | `fc385afc962b175d` | The other valid `prongCount` member, `4` |
| `flat-band-solitaire.json` | `6dd59e1b430a03ff` | The other valid `band.profile` member, `"flat"` |
| `direct-resin-printing-solitaire.json` | `4b744be1e34b0e80` | The other valid `manufacturing.method` member |

All seven pass `jdl.schema.json` with zero errors, construct a `JewelryDefinition` successfully, and produce zero `error`-severity results from `validate_definition()`.

## Invalid examples (5)

| File | Fails at | Specific reason | `definitionHash` |
|---|---|---|---|
| `invalid-schema-version.json` | JDL-SCHEMA (structural, Pydantic construction) | `schemaVersion: "0.2.0"` does not match the required literal `"0.1.0"` | — (rejected before a `JewelryDefinition` exists to hash) |
| `invalid-non-finite-number.json` | JDL-SCHEMA (structural, Pydantic construction) | `preview.meshTolerance: Infinity` — a non-standard JSON token that Python's `json` module parses but Pydantic's `allow_inf_nan=False` rejects; **a generic JSON-Schema-only validator cannot detect this** (JSON Schema has no native "finite number" constraint — see [`specs/jdl/v1/canonicalization.md`](../../../specs/jdl/v1/canonicalization.md) "Known limitation") | — (rejected before hashing) |
| `invalid-prong-count.json` | Semantic validation | `setting.prongCount: 5` is structurally a valid integer but fails `JM-PRONG-001` (must be exactly 4 or 6) | `1d8c5ab5f59a5da5` |
| `invalid-negative-dimension.json` | Semantic validation | `band.width: -2.4` is structurally a valid number (no positivity constraint exists at the schema layer for this field) but fails `JM-BAND-001` and `JM-GEOMETRY-001` | `545c730b7a0a7b61` |
| `invalid-basket-height.json` | Semantic validation | `setting.basketHeight: -1.0` is structurally valid but fails `JM-SETTING-001` (must be positive) | `45d093fcf7ca6f23` |

## Why the 5 invalid examples fail at two different layers, deliberately

Only 2 of the 5 fail JSON Schema / Pydantic construction outright (`invalid-schema-version`, `invalid-non-finite-number`). The other 3 are **structurally valid** JDL documents that fail only at the semantic-validation layer — this is not an oversight; it directly demonstrates the structural/semantic separation documented in [`075-validation-pipeline.md`](../05-jdl/075-validation-pipeline.md) and required by JDL-GOV-004. A validator that only checks `jdl.schema.json` will incorrectly consider `invalid-prong-count.json`, `invalid-negative-dimension.json`, and `invalid-basket-height.json` "valid" — this is expected and is why [`specs/jdl/v1/README.md`](../../../specs/jdl/v1/README.md) states both checks are required for full conformance.
