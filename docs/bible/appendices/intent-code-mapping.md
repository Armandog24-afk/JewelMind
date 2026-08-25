---
id: JM-BIBLE-A71
title: "Appendix: Intent Code Mapping"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-DESIGN-INTENT-README
  - JM-BIBLE-330
related_documents:
  - JM-BIBLE-361
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Intent Code Mapping

Maps each Bible doc topic under `docs/bible/13-design-intent/` (331 through 363) to the real file(s)/function(s) that implement it. Mirrors `designer-code-mapping.md`'s style — honest about a topic having no dedicated module rather than forcing a weak mapping.

| Doc | Topic (from filename) | Real implementing file(s)/function(s) |
|---|---|---|
| 331 | design-intent-architecture | `backend/jewelmind/design_intent/` package as a whole (`schemas.py`, `vocabulary.py`, `normalizer.py`, `resolver.py`, `conflicts.py`, `diagnostics.py`), invoked from `backend/jewelmind/designer/service.py::DesignerService.interpret()` |
| 332 | intent-domain-model | `design_intent/schemas.py` (`IntentStatement`, `IntentRelation`, `DesignIntent`, `IntentConflict`, `IntentDiagnostic`) |
| 333 | intent-vocabulary | `design_intent/vocabulary.py` (`CATEGORIES`), mirrored in `specs/design-intent/v1/vocabulary.json` |
| 334 | intent-target-model | `design_intent/schemas.py` (`IntentTarget` Literal), `vocabulary.py` (`TARGET_SYNONYMS`), `normalizer.py::normalize_target()` |
| 335 | aesthetic-descriptor-model | `normalizer.py::normalize_descriptor()`, `vocabulary.py`'s per-category `synonyms` dicts |
| 336 | relative-proportion-intent | `vocabulary.py::PROPORTIONAL_CHARACTER` category |
| 337 | visual-weight-model | `vocabulary.py::VISUAL_WEIGHT` category |
| 338 | style-continuum-model | `vocabulary.py::ConceptCategory` NamedTuple, `concept_values()`, `continuum_distance()` |
| 339 | emphasis-and-hierarchy-model | `vocabulary.py::VISUAL_EMPHASIS` category |
| 340 | symmetry-and-balance-model | No dedicated module — `BALANCED` exists as one value within 4 separate categories (`VISUAL_WEIGHT`, `SIMPLICITY`, `VISUAL_EMPHASIS`, `PROPORTIONAL_CHARACTER`) and `BALANCED_WITH` as one `RelationPredicate`; there is no standalone symmetry/balance concept category |
| 341 | simplicity-and-complexity-model | `vocabulary.py::SIMPLICITY` category |
| 342 | classic-contemporary-model | `vocabulary.py::STYLE_TEMPORALITY` category |
| 343 | intent-strength-and-priority | `schemas.py::IntentStrength` Literal, `IntentStatement.strength`/`.priority`, `resolver.py::_normalize_strength()` |
| 344 | intent-provenance | `schemas.py::IntentProvenance` Literal; `resolver.py` hardcodes every statement/relation to `provenance="AI_NORMALIZED"` |
| 345 | intent-confidence | `schemas.py::IntentConfidence` Literal; `resolver.py::_resolve_statements` sets `confidenceClass` to `"EXACT"` or `"HIGH_CONFIDENCE_NORMALIZATION"` based on `normalize_descriptor()`'s `is_exact` flag |
| 346 | intent-conflict-model | `design_intent/conflicts.py` (`detect_conflicts()`, `_value_conflicts()`, `_relation_conflicts()`) |
| 347 | intent-compatibility-model | No dedicated module — the closest real code is `conflicts.py::_value_conflicts`'s non-conflict branch (continuum distance `<= 1` is treated as compatible, not flagged) |
| 348 | intent-resolution-model | `schemas.py::IntentResolution` — modeled but "not currently persisted anywhere" per its own docstring |
| 349 | deterministic-resolution-policy | `resolver.py` — every statement/relation is hardcoded to `resolutionStatus="PRESERVED"`; zero `IntentProfile`s registered anywhere in the codebase |
| 350 | intent-to-jdl-boundary | `designer/service.py::_build_proposal()` — `design_intent` is built entirely separately from `patch`/`candidate` and never merged into `candidateJDL` |
| 351 | intent-to-forge-boundary | `validation/engine.py` — no import of, or reference to, `jewelmind.design_intent` anywhere in the Forge rule engine; Forge only ever evaluates `candidateJDL` |
| 352 | unresolved-intent-lifecycle | `resolver.py::_resolve_statements`/`_resolve_relations` (the `unresolved` accumulation), `schemas.py::DesignIntent.unresolvedDescriptors` |
| 353 | intent-preservation | `resolver.py::build_design_intent`'s `mode == "MODIFY"` merge block; `frontend/src/components/DesignerPanel.tsx::handleApply()`'s `proposal.diff.some(d => d.changed)` gate |
| 354 | intent-diff-model | `resolver.py::compute_intent_diff()` — implemented and unit-tested (`test_design_intent.py::TestIntentDiff`) but not currently called from `designer/service.py` or any API route; not yet wired into the live request/response cycle |
| 355 | intent-profile-model | `schemas.py::IntentProfile` — modeled with required `provenance`/`version`/`professionalReview` fields per INTENT-GOV-018, zero instances registered |
| 356 | designer-intent-extraction | `designer/schemas.py::RawIntentStatement`/`RawIntentRelation`/`RawDesignerResponse.designIntentStatements`/`.designIntentRelations`; `designer/service.py::interpret()`'s call to `build_design_intent()` |
| 357 | studio-intent-review | `frontend/src/components/DesignerPanel.tsx` ("Design intent" section), `frontend/src/store/useDesignIntentStore.ts` |
| 358 | intent-diagnostics | `design_intent/diagnostics.py` (the 9 `INTENT_*` codes) |
| 359 | intent-evaluation-framework | `backend/tests/test_design_intent_corpus.py`'s `Case`/`CASES` structure and `check` callables (`has_statement`, `has_relation`, `no_numeric_field_changed`, etc.) |
| 360 | intent-test-corpus | `backend/tests/test_design_intent_corpus.py` (88 cases across 9 categories — see `intent-test-case-catalog.md`) |
| 361 | current-code-mapping | This appendix (`intent-code-mapping.md`) is the appendix-form mirror of this doc |
| 362 | design-intent-gap-analysis | No dedicated implementation file by definition — documents what is deliberately *not* built (`IntentProfile`/`IntentResolution` registration, `compute_intent_diff()` wiring, `SOFT_TENSION`/`TARGET_CONFLICT`/`RESOLUTION_CONFLICT` corpus coverage — see `intent-conflict-catalog.md`) |
| 363 | open-design-intent-questions | No dedicated implementation file by definition — a forward-looking questions doc, not a current-code doc |

## Notes grounded in the real code

- Topics 340 and 347 have no standalone implementing module — this is reported here rather than invented, per this Sprint's own instruction not to force a weak mapping.
- Topic 354's `compute_intent_diff()` exists, is unit-tested, and is a real deterministic function, but is a genuinely separate code path from `resolver.py::build_design_intent()`'s own diff-adjacent MODIFY-merge logic — it is not currently invoked by `designer/service.py`, so no live request today produces an `IntentDiffEntry` list end-to-end.
