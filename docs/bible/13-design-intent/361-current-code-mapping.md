---
id: JM-BIBLE-361
title: Current Code Mapping
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-360
related_documents:
  - JM-BIBLE-362
implementation_status: current
professional_validation: not_required
normative: true
---

# Current Code Mapping

## Backend: `backend/jewelmind/design_intent/`

| File | Responsibility |
|---|---|
| `__init__.py` | Package docstring; documents the boundary with `domain/schema.py`'s `JewelryDefinition` (comment only — no import). |
| `schemas.py` | All Pydantic shapes: `IntentTarget`, `IntentConceptCategory`, `IntentStrength`, `IntentProvenance`, `IntentConfidence`, `ResolutionStatus`, `ConflictType`, `IntentDiagnosticCode`, `RelationPredicate`, `IntentStatement`, `IntentRelation`, `IntentConflict`, `IntentDiagnostic`, `DesignIntent`, `IntentResolution` (schema-only, never constructed), `IntentDiffEntry`, `IntentProfile` (schema-only, zero registered). |
| `vocabulary.py` | The controlled-vocabulary source: recognized targets, concepts, descriptor values, relation predicates, and their Italian/English synonym tables. |
| `normalizer.py` | `normalize_target()`, `normalize_descriptor()`, `normalize_predicate()`, `KNOWN_CONCEPTS` — the deterministic gate every raw statement/relation must pass before becoming part of a `DesignIntent`. |
| `resolver.py` | `build_design_intent()` (orchestration entry point: resolve statements/relations, MODIFY-mode merge, conflict detection, diagnostic assembly) and `compute_intent_diff()` (pure before/after comparison). |
| `conflicts.py` | `detect_conflicts()`, `conflicting_ids()` — flags contradictory statement/relation pairs. |
| `diagnostics.py` | The 9 `INTENT_*` diagnostic code constants and `ALL_INTENT_DIAGNOSTIC_CODES`. |

## Backend: modified Designer files

| File | Change this Sprint |
|---|---|
| `designer/schemas.py` | `RawDesignerResponse` gained `designIntentStatements`, `designIntentRelations`; `NaturalLanguageDesignRequest` gained `currentDesignIntent`; `DesignerProposal` gained required `designIntent`. |
| `designer/service.py` | `_build_proposal()` calls `build_design_intent()`; `diff` now always computed against `request.currentJDL` regardless of interaction mode (the real stale-model fix — see [`356-designer-intent-extraction.md`](356-designer-intent-extraction.md)). |
| `designer/prompts.py` | `SYSTEM_CONTRACT` gained the PART 1/PART 2 technical/aesthetic split; added `build_intent_vocabulary_block()` and `build_current_intent_block()`. |
| `designer/provider.py` | Provider abstraction extended to pass through the two new raw-response fields; no change to provider selection or `FakeDesignerProvider`/live-provider switching logic. |

## Frontend

| File | Responsibility |
|---|---|
| `frontend/src/store/useDesignIntentStore.ts` | New Zustand store: `currentIntent`, `applyIntent()`, `removeStatement()`, `removeUnresolvedDescriptor()`, `clearIntent()`. Not persisted to localStorage. |
| `frontend/src/components/DesignerPanel.tsx` (intent-related parts) | "Design intent" / "Conflicting intent" / "Not yet mapped to a technical parameter" review sections; the persistent compact intent summary with removable tags; `handleApply()`'s two independent calls (`applyDesignerProposal()` gated on `diff.some(d => d.changed)`, `applyIntent()` unconditional). |
| `frontend/src/store/useProjectStore.ts` (reset addition) | `resetProject()` now also calls `useDesignIntentStore.getState().clearIntent()` — the one deliberate one-way coupling INTENT-GOV-004 permits. |

## What is deliberately absent from this table

No file under `backend/jewelmind/domain/`, `backend/jewelmind/validation/`, or `backend/jewelmind/geometry/` appears here, because none of them were touched by this Sprint — Design Intent's entire footprint is the new `design_intent/` package plus the Designer/frontend integration points listed above. This absence is itself evidence for [`350-intent-to-jdl-boundary.md`](350-intent-to-jdl-boundary.md) and [`351-intent-to-forge-boundary.md`](351-intent-to-forge-boundary.md)'s findings.

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md).
- [`../appendices/intent-code-mapping.md`](../appendices/intent-code-mapping.md) — a fuller appendix-level version of this table, once written.
- `../09-foundry/217-current-exporter-code-mapping.md`-style convention this table follows.
