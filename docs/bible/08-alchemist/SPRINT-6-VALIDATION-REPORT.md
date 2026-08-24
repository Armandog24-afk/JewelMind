---
id: JM-BIBLE-SPRINT6-REPORT
title: Sprint 6 Validation Report
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-ALCHEMIST-README
related_documents: []
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 6 Validation Report

## Compiler documents created

`docs/bible/08-alchemist/README.md` plus 29 numbered documents (`160`–`188`), plus this report. 7 new appendices: `alchemist-stage-catalog.md`, `alchemist-state-transition-matrix.md`, `geometry-plan-field-catalog.md`, `compilation-result-field-catalog.md`, `compiler-diagnostic-catalog.md`, `compiler-code-mapping.md`, `compiler-test-matrix.md`.

## Schemas created

8 JSON Schemas (Draft 2020-12): `compilation-input`, `geometry-plan`, `geometry-plan-component`, `compilation-result`, `compiler-diagnostic`, `artifact-request`, `artifact-manifest`, `compiler-capabilities`. All validate. 6 real example records and 7 test-vector files, all generated from or verified against real Sprint 3/5 data or live code, checked into `specs/alchemist/v1/`. New test file: `backend/tests/test_alchemist_registry.py` (5 test cases).

## Compiler stages identified in current code

**13 conceptual stages**, per `docs/bible/appendices/alchemist-stage-catalog.md`: **5 CURRENT** (JDL Canonical Document, Normalization, Forge Evaluation, Eligibility Decision, Atlas Execution), **6 PARTIAL** (Compiler Input, Atlas Inspection, Artifact Requests, Foundry/Vision, Artifact Manifest, CompilationResult), **1 PLANNED** (GeometryPlan), **1 NOT IMPLEMENTED** (Post-Geometry Forge Evaluation).

## GeometryPlan status

**PLANNED. Not implemented anywhere.** `build_solitaire_ring()` computes and consumes every derived value (`inner_radius`, `outer_radius`, `band_top_z`, `prong_center_radius`) inline, in the same call that constructs actual solids — confirmed by direct inspection of `geometry/assemblies/solitaire.py` and all four `geometry/components/*.py` files. Every derived calculation is pure Python arithmetic with zero CadQuery/OCCT dependency, meaning a future extraction into a real `GeometryPlan` object would be architecturally clean but is not performed in this Sprint.

## Current compiler-like services discovered

**1**: `ModelService` (`backend/jewelmind/services/model_service.py`), the only module performing cross-layer orchestration (Forge gate → Atlas call → preview generation, in sequence) at this scope.

## Mixed-responsibility modules found

**3**: `ModelService.generate()` (orchestration + preview generation + temp-directory lifecycle, all in one function); `exporters/step_exporter.py` and `exporters/stl_exporter.py` (Foundry-layer code that directly imports `cadquery` and calls `cq.Compound.makeCompound()` — a small, genuine CAD-kernel operation performed outside `geometry/`).

## Missing version fingerprints found

**6 of 8** conceptual `CompilationEnvironmentFingerprint` fields are never recorded on any generated model: compiler version, Forge rule-set version, CadQuery version, OpenCascade version, exporter version, operating environment. Only JDL schema version and Atlas generator version are currently recorded.

## Cache identity risks found

**1**: `ModelService`'s cache key is `definitionHash` alone — a compiler/Atlas-generator/kernel version change would not invalidate a cached `GeneratedModel`, since no version fingerprint participates in the cache key (ALCHEMIST-GOV-010 not currently enforced). This has never manifested as a real bug, since no second compiler/generator/kernel version has ever shipped — a structural risk, not an observed defect.

## Partial-failure gaps found

**1 major, previously-undocumented finding**: preview generation is coupled to core geometry generation inside `ModelService.generate()` — a hypothetical tessellation failure would fail the entire compilation even though the underlying B-Rep geometry was valid. STEP/STL/JSON/specification export are correctly decoupled (separate, later, independently-failable calls against an already-cached model). This asymmetry was confirmed by tracing the exact call structure of `ModelService.generate()` and the four export routes in `api/routes.py`.

## Code/specification mismatches

**0 shipped.** Two self-corrections were made during this Sprint's own drafting, before anything was committed: (1) an initial draft of [`168-atlas-execution-contract.md`](168-atlas-execution-contract.md) incorrectly claimed no code outside `geometry/` imports `cadquery` — a `grep` during the same drafting session found `exporters/step_exporter.py`/`stl_exporter.py` do, and the document was corrected before being finalized; (2) an initial draft of the geometry-plan example (`specs/alchemist/v1/examples/default-solitaire-geometry-plan.json`) listed invented inter-component dependencies (e.g. "prongs depends on band") that turned out not to be true data dependencies on closer inspection — corrected to accurately reflect that the four components have no true dependency on each other, only the assembly/fuse step depends on three of them. Neither correction reached a committed state as a wrong claim.

## Validation results

| Check | Result |
|---|---|
| All 8 Alchemist JSON Schemas valid (Draft 2020-12) | Yes |
| All 6 examples pass their respective schemas | 6 / 6 |
| Normalization vectors match a live run of `JewelryDefinition.model_validate()` + `definition_hash()` | Confirmed, 3 / 3 |
| Proposed `compilationHash` formula reproducible from checked-in vectors | Confirmed, 3 / 3 |
| Capability vectors match live `Literal` type arguments in `domain/schema.py` | Confirmed |
| Markdown relative links across `docs/bible/` (209 files checked) | All resolve, after this report's own file was created |
| Front matter completeness (all 10 base fields + `normative` on every Sprint 3–6 doc + `professional_validation` on every Forge/Atlas/Alchemist doc) | Complete |
| Duplicate Bible document IDs | None found |
| Personal email addresses / absolute local Windows paths | None found |
| Repository paths referenced in backticks across new/updated Sprint 6 docs | All resolve |
| Backend test suite | **175 passed** (170 pre-existing + 5 new, `test_alchemist_registry.py`) |
| Backend lint (`ruff check`) | Clean (one `UP012` finding in the new test file, fixed during this Sprint) |
| Geometry/export/Atlas/Alchemist-specific tests | **32 passed** (`test_geometry.py`, `test_atlas_registry.py`, `test_alchemist_registry.py`, filtered `test_api.py`) |
| Frontend test suite | **41 passed**, unchanged — no frontend code was modified this Sprint |
| Frontend type check (`tsc -b`) | Clean |
| Frontend production build (`vite build`) | Succeeds |

## What was, and was not, changed in application code

**Changed**: `backend/tests/test_alchemist_registry.py` (new test file only). **Not changed**: no field, service, geometry builder, exporter, or frontend component was modified, and no new runtime endpoint or `GeometryPlan` implementation was added. This Sprint is documentation- and specification-only, exactly as required — Alchemist is named and gap-analyzed, not built.
