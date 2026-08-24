---
id: JM-BIBLE-096
title: Rule Evaluation Pipeline (FORGE-0..FORGE-9)
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-091
related_documents:
  - JM-BIBLE-063
  - JM-BIBLE-075
implementation_status: partial
professional_validation: not_required
normative: true
---

# Rule Evaluation Pipeline (FORGE-0..FORGE-9)

This pipeline is Forge's own view of the same request lifecycle [`05-jdl/063-jdl-processing-model.md`](../05-jdl/063-jdl-processing-model.md) describes as JDL-0..JDL-10 — FORGE-0..FORGE-5 correspond to JDL-3..JDL-6 (schema through domain validation), FORGE-6/7 correspond to JDL-7/8/9 (geometry), and FORGE-8/9 correspond to JDL-10 (export) plus the professional-review boundary JDL does not itself model.

| Stage | Inputs | Outputs | Blocking semantics | Categories | Diagnostics | Current status |
|---|---|---|---|---|---|---|
| **FORGE-0** Schema integrity | Parsed JSON object | `JewelryDefinition` or a construction failure | Fatal — construction failure stops everything before any rule runs | `SCHEMA_INTEGRITY`, `SYSTEM_SAFETY` | `REQUEST_VALIDATION_ERROR` (via FastAPI/Pydantic) | CURRENT |
| **FORGE-1** Semantic compatibility | `JewelryDefinition` | `ValidationResult`s for cross-field consistency | `error` blocks; `information`/`warning` do not | `SEMANTIC_COMPATIBILITY` | `JM-RING-003`, `JM-PRONG-004` | CURRENT |
| **FORGE-2** Domain invariants | `JewelryDefinition` | `ValidationResult`s for structural domain truths | `error` blocks | `DOMAIN_INVARIANT` | `JM-STONE-002` | CURRENT |
| **FORGE-3** Geometry preconditions | `JewelryDefinition` | `ValidationResult`s gating whether geometry can be built at all | `error` blocks generation | `GEOMETRY_PRECONDITION` | `JM-SETTING-001`, `JM-GEOMETRY-001` | CURRENT |
| **FORGE-4** Prototype jewelry heuristics | `JewelryDefinition` | `ValidationResult`s from prototype-chosen thresholds | `error` blocks; `warning`/`information` advise | `PROTOTYPE_HEURISTIC` | 10 of the 16 `JM-*` rules — see [`093-rule-classification-model.md`](093-rule-classification-model.md) | CURRENT |
| **FORGE-5** Manufacturing-context checks | `JewelryDefinition` (specifically `manufacturing.method`) | `ValidationResult`s conditioned on manufacturing method | `warning` only today; does not block | `MANUFACTURING_CONTEXT` | `JM-MANUFACTURING-001` | CURRENT |
| **FORGE-6** Geometry generation | A `JewelryDefinition` with zero `error`-severity results from FORGE-1..5 | `GeneratedModel` | n/a (this stage does not itself emit diagnostics; it is gated by FORGE-1..5's results via `has_errors()`) | n/a | n/a | CURRENT — `build_solitaire_ring()` |
| **FORGE-7** Generated geometry inspection | `GeneratedModel` | `ValidationResult`-shaped diagnostics for post-generation properties | Currently non-blocking (`FORGE-GEOM-001` is a `WARNING` that never prevents export) | `GEOMETRY_INSPECTION` | `FORGE-GEOM-001` (runtime); many more properties verified only by tests, not runtime diagnostics — see [`106-generated-geometry-inspection-rules.md`](106-generated-geometry-inspection-rules.md) | PARTIAL |
| **FORGE-8** Export preconditions | `model_id`, export request parameters | Export allowed, or an `AppError` | Blocks the specific export requested | `EXPORT_PRECONDITION` | `FORGE-EXPORT-001` (`VALIDATION_BLOCKED`, `MODEL_NOT_FOUND`) | CURRENT |
| **FORGE-9** Professional-review boundary | The exported artifact | A human decision (accept, revise, reject) | Outside software entirely — no software gate exists here | `PROFESSIONALLY_VALIDATED` (target state, not yet populated) | n/a | NOT IMPLEMENTED — no professional review has ever occurred for any output of this system, per [`04-jewelry-domain/058-professional-validation-register.md`](../04-jewelry-domain/058-professional-validation-register.md) |

## Why FORGE-1 through FORGE-5 are five conceptual stages but one function call

Exactly as Sprint 3's [`063-jdl-processing-model.md`](../05-jdl/063-jdl-processing-model.md) noted for JDL-5/JDL-6, `validate_definition()` runs all of FORGE-1 through FORGE-5's rules in one undivided pass (`_RULE_GROUPS` in `backend/jewelmind/validation/engine.py`). This document's stage split is a classification lens for reasoning about rules, not a claim that five separate engine invocations occur.

## Short-circuit behavior

None exists today. `validate_definition()` always runs every rule group to completion and returns every fired diagnostic, regardless of severity — an `error` in FORGE-1 does not prevent FORGE-2 through FORGE-5 from also running and reporting. Only the *downstream* gate (`has_errors()`, checked once after all rules have run) stops FORGE-6 (geometry generation) from proceeding. See [`100-rule-dependencies-and-ordering.md`](100-rule-dependencies-and-ordering.md).
