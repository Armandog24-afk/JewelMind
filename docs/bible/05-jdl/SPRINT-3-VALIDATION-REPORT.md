---
id: JM-BIBLE-SPRINT3-REPORT
title: Sprint 3 Validation Report
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-JDL-README
related_documents: []
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 3 Validation Report

## Documents created

- `docs/bible/05-jdl/README.md` plus 27 numbered documents (`060`–`086`).
- 5 new appendices: `jdl-field-catalog.md`, `jdl-enumeration-catalog.md`, `jdl-error-code-catalog.md`, `jdl-version-compatibility-matrix.md`, `jdl-example-index.md`.
- This report.

## Machine-readable specification files created

- `specs/jdl/v1/README.md`, `jdl.schema.json` (JSON Schema draft 2020-12), `jdl.ebnf` (grammar only, no parser), `canonicalization.md`, `compiler-contract.md`.
- `specs/jdl/v1/examples/` — 7 valid documents.
- `specs/jdl/v1/examples/invalid/` — 5 invalid documents.
- `specs/jdl/v1/test-vectors/` — 4 files (`canonicalization-vectors.json`, `definition-hash-vectors.json`, `validation-vectors.json`, `compatibility-vectors.json`).
- `backend/tests/test_jdl_schema_examples.py` — new automated test (15 test cases), keeps the above honest against the running implementation on every `pytest` run.
- `backend/requirements.txt` — added `jsonschema>=4.20` as a dev/test-only dependency (used only by the new test file, never imported by `jewelmind/` application code).

## Normative representation selected

**Canonical JSON.** YAML serialization and the textual JDL DSL are documented as PLANNED, non-normative. No parser was implemented for either, per the explicit scope of this milestone.

## Validation results

| Check | Result |
|---|---|
| JSON Schema (`jdl.schema.json`) is itself valid Draft 2020-12 | **Yes** — `jsonschema.Draft202012Validator.check_schema()` passes |
| Valid examples passing schema + zero validation errors | **7 / 7** |
| Invalid examples correctly rejected, each for its documented reason | **5 / 5** (2 at the structural/Pydantic layer, 3 at the semantic-validation layer — see `jdl-example-index.md` for why this split is deliberate) |
| Canonicalization vectors passing (matching a live run of `canonical_json()`) | **7 / 7** parseable examples checked, all match |
| Definition-hash vectors passing (matching a live run of `definition_hash()`) | **10 / 10** rows (7 valid + 3 semantically-invalid-but-parseable examples) |
| Schema-version compatibility vectors passing | **5 / 5** rows |
| Current fields catalogued | **23** (including `schemaVersion`) |
| Current enumerations catalogued | **8** named `Literal` type aliases, plus 2 additional value sets noted for completeness (fixed `units: "mm"`, semantic-only `prongCount ∈ {4,6}`) |
| Backend test suite | **154 passed** (139 pre-existing + 15 new, in `test_jdl_schema_examples.py`) |
| Backend lint (`ruff check`) | **Clean** |
| Frontend test suite | **41 passed**, unchanged — no frontend code was modified this Sprint |
| Frontend type check (`tsc -b`) | **Clean** |
| Frontend production build (`vite build`) | **Succeeds** (pre-existing chunk-size warning only, unrelated to this Sprint) |
| Markdown relative links across `docs/bible/` (96 files checked) | **All resolve**, after this report's own file was created |
| Front matter completeness (all 10 Sprint 1/2 fields + new `normative` field on every Sprint 3 doc) | **Complete** |
| Duplicate Bible document IDs | **None found** |
| Personal email addresses / absolute local Windows paths in `docs/bible/` | **None found** |
| Repository paths referenced in backticks across the new/updated Sprint 3 docs | **All resolve** to real files |
| Mermaid diagrams (3: in `061`, `063`, and the sequence diagrams pre-existing in `023-data-flow.md`) | Fence-balanced; reviewed by hand for the known curly-brace-in-sequence-diagram pitfall (none of the new diagrams are sequence diagrams, so this does not apply to Sprint 3's new content) |

## Field/enum mismatches found

**None.** Every field and enum member in `specs/jdl/v1/jdl.schema.json`, the field catalog, and the enumeration catalog was cross-checked directly against `backend/jewelmind/domain/schema.py` and `shared/types/jewelry-definition.ts` during this Sprint and matches exactly.

## Hash behavior discovered

- `definition_hash()` includes every field, including `preview.meshTolerance`/`angularTolerance` (confirmed by test vectors) — flagged as open question JDL-OQ-001, not changed.
- An omitted field and its explicit default value canonicalize byte-identically (`minimal-solitaire.json` == `default-solitaire.json`, hash `355ddca57e7e49ad`).
- `-0.0` normalization is undefined and currently unreachable by any valid field — flagged as open question JDL-OQ-003, not changed.
- Cross-Python-version and cross-OS hash stability were not separately tested this Sprint — flagged as a risk in `076-canonicalization-and-definition-hashing.md`, not fixed.

## Unresolved language decisions

Ten open questions recorded in `086-open-jdl-questions.md` (JDL-OQ-001 through JDL-OQ-010), none guessed at or silently resolved.

## Code/specification gaps found (reported, not fixed)

1. **No request-body size limit or geometry-generation timeout exists** in the backend (`083-security-and-resource-limits.md`) — a real, pre-existing gap, not introduced or fixed this Sprint.
2. **Frontend/backend constraint mismatch on `setting.prongCount`**: the frontend's `isValidJewelryDefinition()` guard checks only finiteness, not integer-ness or `{4,6}` membership, while the backend's Pydantic `int` type and `JM-PRONG-001` are stricter (`084-current-implementation-mapping.md` finding 3).
3. **No UI control for `preview.meshTolerance`/`angularTolerance`** — these can only be set via direct export-request parameters, not through `ConfigurationPanel.tsx` (`084-current-implementation-mapping.md` finding 4).
4. **No `expected-component-manifest` test-vector file was generated** — the component-manifest shape is documented and exercised by `backend/tests/test_geometry.py`, but no standalone vector file exists (`085-conformance-and-test-vectors.md`).
5. **Frontend and backend package versions are not synchronized** (`0.0.0` vs. `0.1.0`) — a pre-existing, unrelated-to-JDL fact, recorded in `081-schema-versioning-and-migrations.md` for completeness.

None of these gaps were fixed in this documentation-only milestone, per the Sprint 3 brief's explicit instruction that larger discrepancies be recorded for a future sprint rather than silently patched.

## What was, and was not, changed in application code

**Changed**: `backend/requirements.txt` (added `jsonschema>=4.20`, dev/test-only); `backend/tests/test_jdl_schema_examples.py` (new test file). **Not changed**: no field, default, validation rule, geometry builder, exporter, or frontend component was modified. This Sprint is documentation- and specification-only, exactly as required.
