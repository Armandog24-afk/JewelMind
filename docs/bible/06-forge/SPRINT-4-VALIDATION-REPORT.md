---
id: JM-BIBLE-SPRINT4-REPORT
title: Sprint 4 Validation Report
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-FORGE-README
related_documents: []
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 4 Validation Report

## Documents created

- `docs/bible/06-forge/README.md` plus 26 numbered documents (`090`–`115`).
- 6 new appendices: `forge-rule-catalog.md`, `forge-rule-provenance-register.md`, `forge-severity-matrix.md`, `forge-professional-validation-matrix.md`, `forge-rule-dependency-matrix.md`, `forge-rule-test-matrix.md`.
- This report.

## Machine-readable specification files created

- `specs/forge/v1/README.md`, `rule.schema.json`, `rule-result.schema.json`, `rule-context.schema.json`, `rule-registry.schema.json` (all Draft 2020-12).
- `specs/forge/v1/current-rule-registry.json` — 21 rules, generated exclusively from real code inspection.
- `specs/forge/v1/examples/valid/` — 2 complete `ForgeRule` definitions.
- `specs/forge/v1/examples/invalid/` — 4 definitions, each invalid for one documented reason.
- `specs/forge/v1/test-vectors/` — 4 files (`evaluation-vectors.json`, `severity-vectors.json`, `precedence-vectors.json`, `provenance-vectors.json`).
- `backend/tests/test_forge_registry.py` — new automated test (11 test cases).

## Rules discovered

**21 rules** total: 16 pre-existing jewelry-domain rules (`JM-*`, none renamed) in `backend/jewelmind/validation/rules.py`/`engine.py`, plus 5 newly-named cross-cutting rules (`FORGE-SCHEMA-001`, `FORGE-SAFETY-001`, `FORGE-SAFETY-002`, `FORGE-GEOM-001`, `FORGE-EXPORT-001`) that already existed as real code behavior but had no stable rule ID before this Sprint.

## Rules classified

All 21, across all 11 categories (see [`093-rule-classification-model.md`](093-rule-classification-model.md)): `PROTOTYPE_HEURISTIC` (11), `SEMANTIC_COMPATIBILITY` (2), `DOMAIN_INVARIANT` (1), `GEOMETRY_PRECONDITION` (2), `MANUFACTURING_CONTEXT` (1), `SCHEMA_INTEGRITY` (1), `SYSTEM_SAFETY` (2), `GEOMETRY_INSPECTION` (1), `EXPORT_PRECONDITION` (1). `PROFESSIONAL_CANDIDATE` and `PROFESSIONALLY_VALIDATED` are correctly populated with zero rules — no candidate has been proposed and no review has occurred.

## Rules with known provenance

**21 / 21.** Every rule has an assigned, evidence-based `provenanceType`: `prototype_heuristic` (11), `implementation_necessity` (6), `mathematical_constraint` (2), `geometry_engine_constraint` (2). Zero rules are `unknown` — every rule's justification traced cleanly to a code necessity, a named formula, or an acknowledged prototype choice.

## Professionally validated rules

**0.** Every rule is `professionalValidationStatus: preliminary` (the 16 `JM-*` rules) or `not_required` (the 5 `FORGE-*` system rules). No validation record exists anywhere in this repository. As instructed, existing implementation does not itself count as professional validation, and no reviewer was invented.

## Preliminary rules

**16** (all `JM-*` rules).

## Frontend/backend rule mismatches

**None found among the 16 `JM-*` rules.** Direct side-by-side inspection of `backend/jewelmind/validation/engine.py` and `shared/validation/engine.ts` confirms an exact behavioral mirror — same rule IDs, thresholds, severities, and messages. The one genuine divergence found is a **precondition-scope** mismatch, not a rule-threshold mismatch: the frontend's `isStale` export gate (`useProjectStore.ts`) has no backend-side equivalent — the backend will export a stale cached model if called directly, bypassing the UI (see [`107-export-precondition-rules.md`](107-export-precondition-rules.md)).

## Undocumented geometry assumptions found

1. `FORGE-GEOM-001` (the fuse-must-yield-a-solid check) lives inline inside `geometry/assemblies/solitaire.py::_fuse_metal`, not inside `validation/engine.py` — an inconsistency with FORGE-GOV-005's spirit that a jewelry/geometry rule should live in `validation/`. Recorded as open question `FORGE-OQ-007` in [`115-open-forge-questions.md`](115-open-forge-questions.md), not silently moved (moving it would be a real code change, out of scope for this documentation Sprint).
2. Every other geometry-inspection property (positive volume, plausible bounding box, requested-vs-generated prong count, stone separation) is verified **only by tests** (`backend/tests/test_geometry.py`), never as a runtime diagnostic returned to a real API caller — see [`106-generated-geometry-inspection-rules.md`](106-generated-geometry-inspection-rules.md). This is the single most significant finding of this Sprint: there is currently no runtime safety net if a real user's specific input produced a geometrically implausible result outside the fixed set of test cases.

## Test gaps found

1. No dedicated boundary-value-matrix artifact exists as a standalone file — boundary behavior for 14 of 16 rules is covered only incidentally by existing round-number test inputs, not by tests specifically designed to probe the exact threshold edge (see [`appendices/forge-rule-test-matrix.md`](../appendices/forge-rule-test-matrix.md)).
2. No property-based/fuzz testing exists anywhere in this codebase.
3. No conflict, profile, or professional-validation tests exist, because none of those scenarios currently occur in the real system (verified, not assumed — see `specs/forge/v1/test-vectors/precedence-vectors.json`).
4. No `component-manifest` or full-`ForgeRule`-per-rule JSON files were generated for all 21 rules this Sprint (only 2 worked examples exist) — a mechanical, low-risk follow-up rather than an architectural gap.

## Unresolved professional questions

Eleven open questions recorded in [`115-open-forge-questions.md`](115-open-forge-questions.md) (`FORGE-OQ-001` through `FORGE-OQ-011`), covering material/manufacturing profile overrides, conflicting-expert representation, warning-blocks-export scenarios, jurisdiction/supplier scoping, the Forge-vs-geometry-engine boundary for inspection rules, evaluation performance at scale, historical-rule executability, auto-fix auditing, and provenance expiration — none guessed at or silently resolved.

## Validation results

| Check | Result |
|---|---|
| All 4 Forge JSON Schemas are valid Draft 2020-12 | **Yes** |
| Valid rule examples passing schema | **2 / 2** |
| Invalid rule examples correctly rejected | **4 / 4** |
| Current rule registry validates against `rule-registry.schema.json` | **Yes**, 0 errors |
| Registry has no duplicate rule IDs | **Confirmed**, 21 unique IDs |
| Evaluation vectors match a live run of `validate_definition()` | **5 / 5** scenarios |
| Severity/boundary vectors match a live run (`JM-BAND-002`, `JM-PRONG-002` at both branches) | **Confirmed** |
| Markdown relative links across `docs/bible/` (130 files checked) | **All resolve**, after this report's own file was created |
| Front matter completeness (all 10 base fields + `normative` on every Sprint 3/4 doc + `professional_validation` on every Forge doc) | **Complete** |
| Duplicate Bible document IDs | **None found** |
| Personal email addresses / absolute local Windows paths | **None found** |
| Repository paths referenced in backticks across new/updated Sprint 4 docs | **All resolve** |
| Unsupported CURRENT claims | **None found** — every CURRENT claim in this Sprint traces to a cited file/test; PARTIAL/PLANNED/VISION/NOT IMPLEMENTED are used explicitly wherever a capability does not fully exist |
| Backend test suite | **165 passed** (154 pre-existing + 11 new, in `test_forge_registry.py`) |
| Backend lint (`ruff check`) | **Clean** |
| Frontend test suite | **41 passed**, unchanged — no frontend code was modified this Sprint |
| Frontend type check (`tsc -b`) | **Clean** |
| Frontend production build (`vite build`) | **Succeeds** (pre-existing chunk-size warning only, unrelated to this Sprint) |

## What was, and was not, changed in application code

**Changed**: `backend/tests/test_forge_registry.py` (new test file only). **Not changed**: no field, default, validation rule, geometry builder, exporter, or frontend component was modified, and no new runtime endpoint was added. This Sprint is documentation- and specification-only, exactly as required — Forge is a classification and specification layer over the rule engine that already existed.
