---
id: JM-BIBLE-SPRINT7-REPORT
title: Sprint 7 Validation Report
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-FOUNDRY-README
related_documents: []
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 7 Validation Report

## Foundry documents created

`docs/bible/09-foundry/README.md` plus 30 numbered documents (`190`–`219`), plus this report. 7 new appendices: `foundry-artifact-catalog.md`, `foundry-mime-type-catalog.md`, `foundry-component-inclusion-matrix.md`, `foundry-export-diagnostic-catalog.md`, `foundry-export-test-matrix.md`, `foundry-code-mapping.md`, `foundry-interoperability-matrix.md` (`JM-BIBLE-A34` through `A40`, continuing directly from Sprint 6's last appendix, `A33`).

## Schemas created

6 JSON Schemas (Draft 2020-12): `artifact-request`, `artifact-record`, `artifact-manifest`, `export-diagnostic`, `export-validation-result`, `export-version-fingerprint`. All validate. 7 real example records and 7 test-vector files, all generated from or verified against real Sprint 7 export runs and live code, checked into `specs/foundry/v1/`. New test file: `backend/tests/test_foundry_registry.py` (6 test cases).

## Current artifact types formalized

4 production/technical artifact types (`STEP`, `STL`, `JSON`, `TECHNICAL_SPECIFICATION`) plus a fifth, `PREVIEW_MESH`, explicitly left to Alchemist/Vision rather than duplicated into Foundry's schema — see [`193-artifact-request-contract.md`](193-artifact-request-contract.md).

## Export verification, run against the real backend

| Check | Result |
|---|---|
| STEP export verified | **Yes** — real `export_step()` run against the default solitaire, 197081 bytes, re-imported via `cadquery.importers.importStep()`, volume matches original within `3.96e-7` relative difference |
| STL export verified | **Yes** — real `export_stl()` run, 522784 bytes, 10454 triangles, binary header structurally validated (`84 + 10454*50 == 522784`) |
| JSON export verified | **Yes** — `export_json()` run and re-parsed; already covered by `test_api.py::test_export_json_matches_original_definition` |
| Technical specification verified | **Yes** — `build_specification()` run; disclaimer presence already covered by existing tests |
| StoneReference excluded correctly | **Yes** — confirmed both by direct code inspection (`select_export_shapes()`) and by a live test asserting the with-stone export has exactly one more solid than the default export (`test_foundry_registry.py::test_component_inclusion_vectors_match_live_default_export`) |

## Export integrity checks implemented

**2 new, real, request-time checks**: `validate_non_empty()` (file existence + non-zero size) and `sha256_checksum()` (exposed via the `X-Content-SHA256` response header), both applied to every real STEP/STL export. Plus **1 new structural, test-time-only check**: `binary_stl_triangle_count()`.

## Roundtrip checks implemented

**2**: STEP re-import via `cadquery.importers.importStep()` (geometric roundtrip, volume/solid-count comparison); STL binary-header structural roundtrip (size-formula reconciliation). Both are test-suite-only, never triggered by a real user request — see [`202-artifact-integrity-model.md`](202-artifact-integrity-model.md) for why.

## Mixed-responsibility modules remaining

**1** (`ModelService.generate()`, unchanged, out of this Sprint's scope) — down from Sprint 6's count of **3**. The other two (`exporters/step_exporter.py`, `exporters/stl_exporter.py`) are resolved by this Sprint's `selection.py` extraction; see [`217-current-exporter-code-mapping.md`](217-current-exporter-code-mapping.md).

## Targeted refactors performed

**1**: extraction of `exporters/selection.py::select_export_shapes()` from duplicated logic previously present identically in both `step_exporter.py` and `stl_exporter.py`. Verified behavior-preserving: the full backend test suite passed unchanged in outcome before and after (175 tests before this Sprint's new files were added, 194 after — the 19 new tests are additive, not replacements, and no pre-existing test's assertions changed).

## Export-version fingerprints implemented

**Partial.** No single `ExportVersionFingerprint` object is assembled anywhere in real code. Every individual field was independently checked and recorded this Sprint (CadQuery `2.8.0`, OpenCascade/OCP `7.9.3.1.1`, matching the `"7.9"` found inside real STEP file headers; mesh/angular tolerance defaults `0.1`/`0.2`; STL always binary) — see [`208-export-version-fingerprint.md`](208-export-version-fingerprint.md) and `specs/foundry/v1/test-vectors/version-fingerprint-vectors.json`.

## Interoperability workflows actually tested

**0** external, independent CAD applications. The only `IMPORT_TESTED`-equivalent result is CadQuery/OpenCascade re-importing its own STEP output — explicitly not counted as independent third-party interoperability testing. See [`209-cad-interoperability-philosophy.md`](209-cad-interoperability-philosophy.md) and `docs/bible/appendices/foundry-interoperability-matrix.md`.

## Newly discovered findings

1. **STEP export is not byte-for-byte deterministic.** Two exports of an identical `GeneratedModel` differ in exactly 2 of ~4315 lines (an embedded wall-clock timestamp and an incrementing OpenCascade translator-instance counter); all real geometry data is identical. STL export, by contrast, is fully byte-for-byte deterministic.
2. **STEP files explicitly declare their length unit** (`SI_UNIT(.MILLI.,.METRE.)`), confirmed by direct inspection, resolving a previously-unverified claim in `07-atlas/145-step-export-geometry-contract.md`.
3. **An OCCT-internal uncertainty value** (`UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(5.E-06), ...)`, i.e. 5 nanometres) is embedded in every STEP export's unit context — a real, previously-undocumented fact, not a JewelMind-chosen tolerance.
4. **`ExportFailedError` is dead code.** `api/errors.py` defines it with a docstring stating it is for "JSON / specification exports," but neither `export_json_route()` nor `specification_route()` ever imports or raises it — a real failure in either path surfaces as an unstructured, unhandled 500 rather than the `ErrorEnvelope` shape every other export failure uses.

## Code/specification mismatches

**0 shipped.** One correction was made during this Sprint's own drafting, before anything was committed: an initial draft of `export-version-fingerprint.schema.json`'s `openCascadeVersion` description said "PLANNED — never queried or recorded anywhere," which became incomplete once the STEP-header-diff investigation showed the version text is empirically present inside every exported file's own header — corrected to state this precisely before the schema was finalized.

## Validation results

| Check | Result |
|---|---|
| All 6 Foundry JSON Schemas valid (Draft 2020-12) | Yes |
| All 7 examples pass their respective schemas | 7 / 7 |
| Filename vectors match a live run of `sanitize_filename()` | Confirmed, all vectors |
| Component-inclusion vectors match a live run of `select_export_shapes()` | Confirmed |
| Artifact-integrity vectors internally consistent (size formula, roundtrip tolerance) | Confirmed |
| Version-fingerprint vectors carry no unlabeled guess (every entry has `status` + `howObtained`) | Confirmed |
| Markdown relative links across `docs/bible/` (248 files checked) | All resolve, after this report's own file was created |
| Front matter completeness (all 10 fields, on all 38 Sprint 7 files) | Complete |
| Duplicate Bible document IDs | None found |
| Personal email addresses / absolute local Windows paths | None found |
| Backend test suite | **194 passed** (175 pre-existing + 19 new: 5 `test_export_integrity.py`, 8 `test_filenames.py`, 6 `test_foundry_registry.py`) |
| Backend lint (`ruff check`) | Clean |
| Frontend test suite | **41 passed**, unchanged — no frontend code was modified this Sprint |
| Frontend type check (`tsc -b`) | Clean |
| Frontend production build (`vite build`) | Succeeds |

## What was, and was not, changed in application code

**Changed** (behavior-preserving hardening, explicitly pre-authorized by this Sprint's scope): `exporters/selection.py` (new, extracted), `exporters/step_exporter.py` and `exporters/stl_exporter.py` (refactored to delegate to it), `exporters/integrity.py` (new — checksums and non-empty validation), `services/model_service.py` (calls `validate_non_empty()`), `api/routes.py` (calls `sha256_checksum()`, adds `X-Content-SHA256` header). **Not changed**: no export's actual output geometry, no default component-inclusion behavior, no public API request/response schema field, no frontend code. Every claim above is verified by the full backend and frontend test suites passing unchanged in outcome.
