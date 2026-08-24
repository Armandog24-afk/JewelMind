---
id: JM-BIBLE-165
title: Forge Evaluation Integration
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-164
related_documents:
  - JM-BIBLE-096
  - JM-BIBLE-140
implementation_status: partial
professional_validation: not_required
normative: true
---

# Forge Evaluation Integration

## `PreGeometryForgeEvaluation`

Conceptually, the FORGE-1 through FORGE-5 evaluation ([`06-forge/096-rule-evaluation-pipeline.md`](../06-forge/096-rule-evaluation-pipeline.md)) that must complete before Atlas execution begins. **Current implementation: `validate_definition(definition)`, called once inside `ModelService.generate()` before `build_solitaire_ring()`.**

## How Alchemist consumes Forge's output today

| Conceptual input | Current mechanism |
|---|---|
| Passed rules | Not tracked — `validate_definition()` returns only fired diagnostics, never a "passed" list (see [`06-forge/098-rule-result-and-diagnostics.md`](../06-forge/098-rule-result-and-diagnostics.md)) |
| Diagnostics | The full `list[ValidationResult]` |
| Generation blockers | `has_errors(results)` — any `error`-severity result blocks `build_solitaire_ring()` from being called at all |
| Export blockers | Indirect — export requires a previously-generated `ModelRecord`, which itself required zero generation blockers; there is no separate, distinct "export blocker" check today |
| Advisory warnings | `warning`/`information`-severity results — returned to the caller but never gate anything |
| `professionalReviewRequired` | **Does not exist** — no rule in the current registry has `professionalValidationStatus: required`, so this flag would always be `false` if computed; it is not computed at all today |

## Post-geometry Forge evaluation

**Not implemented in any form.** No Forge rule reads an Atlas inspection fact — the one runtime inspection check that exists (`FORGE-GEOM-001`'s fuse-solid-count check) is evaluated and warned about entirely inside `geometry/assemblies/solitaire.py::_fuse_metal()`, never handed to a separate Forge evaluation pass. This is the same finding Sprint 4/5 already recorded (`FORGE-OQ-007`, `ATLAS-GAP-002`); this document is the compiler-level restatement of why: there is no "post-geometry evaluation" stage in the pipeline for such a rule to run in.

## No duplication of Forge logic

This document does not restate any rule threshold, provenance, or lifecycle detail — [`06-forge/`](../06-forge/README.md) remains the sole authority on rule content; Alchemist only orchestrates *when* Forge runs and *what happens* to compilation as a result.
