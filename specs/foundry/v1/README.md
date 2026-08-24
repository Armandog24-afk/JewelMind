# Foundry Export System v1 — Machine-Readable Specification

The machine-readable half of Foundry. The narrative, architecture, and contract half lives in [`docs/bible/09-foundry/`](../../../docs/bible/09-foundry/README.md); start there for context.

## What Foundry is

Foundry is the artifact-generation and export-integrity layer: the conceptual boundary between a validated, compiled model (Atlas geometry + Alchemist orchestration) and a file the outside world can open — STEP, STL, canonical JDL JSON, or a technical specification document. **Foundry v1 formalizes an export system that already runs in production**, unlike Alchemist v1 (mostly a target architecture) — `export_step()`, `export_stl()`, `export_json()`, and `build_specification()` are real, exercised code paths today. What Foundry v1 adds is: a shared name and boundary for concepts that were previously implicit or duplicated (production-shape selection, filename safety, artifact integrity), plus a target vocabulary (artifact records, manifests, version fingerprints, partial-success outcomes) for concepts the current code does not yet represent as structured data.

## Files

| File | Purpose | Status |
|---|---|---|
| [`artifact-request.schema.json`](artifact-request.schema.json) | Structural schema for a request to generate one artifact | PARTIAL — maps to 4 real, separate export endpoints; most request fields are PLANNED |
| [`artifact-record.schema.json`](artifact-record.schema.json) | Structural schema for one generated artifact's record | PARTIAL — checksum/byteSize are CURRENT for STEP/STL as of Sprint 7; most other fields are PLANNED |
| [`artifact-manifest.schema.json`](artifact-manifest.schema.json) | Structural schema for an aggregate manifest across multiple artifacts | PLANNED — no unified manifest exists; each export endpoint is called and evaluated independently |
| [`export-diagnostic.schema.json`](export-diagnostic.schema.json) | Structural schema for an export-specific diagnostic code | PARTIAL — `realCurrentCode` maps each target code to the actual unmodified `AppError.code` in use today |
| [`export-validation-result.schema.json`](export-validation-result.schema.json) | Structural schema for one integrity-check result | PARTIAL — 3 of 8 levels run for every real request; 2 more run only in the test suite; 3 are not executed anywhere |
| [`export-version-fingerprint.schema.json`](export-version-fingerprint.schema.json) | Structural schema for a recorded export-environment fingerprint | PLANNED — no code assembles these fields together; each individual value is independently queryable today |
| [`examples/`](examples/) | 7 example records, generated from real Sprint 7 export runs where numeric | — |
| [`test-vectors/`](test-vectors/) | 7 test-vector files covering component inclusion, filename sanitization, integrity-check coverage, real checksums/roundtrip measurements, partial-success outcomes, unit/scale declarations, and version-fingerprint field status | — |

## No fabricated measurements

Every numeric value in `examples/` and `test-vectors/` that represents a real geometric or file-level quantity (byte sizes, checksums, triangle counts, volumes, STEP unit/uncertainty declarations, installed package versions) was obtained by running the real exporters, the real filename sanitizer, or `importlib.metadata` against the real installed environment during this Sprint — not estimated or invented. Where a field genuinely does not exist in any current code path, it is marked `PLANNED` or `null` rather than filled with a placeholder.

## How these files are validated

`backend/tests/test_foundry_registry.py` (added in Sprint 7) validates all 6 schemas, validates all 7 examples against their respective schemas, and cross-checks `filename-vectors.json` against a live run of `sanitize_filename()` and `component-inclusion-vectors.json` against a live run of `select_export_shapes()`.
