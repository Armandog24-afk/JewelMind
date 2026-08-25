---
id: JM-BIBLE-332
title: Intent Domain Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-331
related_documents:
  - JM-BIBLE-333
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Domain Model

All shapes below are real Pydantic models in `backend/jewelmind/design_intent/schemas.py` (`model_config = ConfigDict(extra="forbid")` on every one — no undocumented field can silently pass through), mirrored in TypeScript in `frontend/src/api/types.ts`. Many other docs in this Sprint link back here.

## `DesignIntent`

| Field | Type | Notes |
|---|---|---|
| `version` | `str` | Always `"1.0.0"` in v1. See INTENT-GOV-012. |
| `sourceText` | `str` | The raw natural-language request that produced this intent. |
| `statements` | `IntentStatement[]` | Default empty. |
| `relationships` | `IntentRelation[]` | Default empty. |
| `unresolvedDescriptors` | `str[]` | Verbatim text JewelMind could not classify. Default empty. |
| `conflicts` | `IntentConflict[]` | Default empty. |
| `profile` | `str \| null` | Always `null` in v1 — zero `IntentProfile`s are registered anywhere in the codebase. |
| `diagnostics` | `IntentDiagnostic[]` | Default empty. |

## `IntentStatement`

| Field | Type | Notes |
|---|---|---|
| `intentId` | `str` | `f"intent-{uuid.uuid4()}"`, assigned by `resolver.py`. |
| `target` | `IntentTarget` | Required. See [`334-intent-target-model.md`](334-intent-target-model.md). |
| `concept` | `IntentConceptCategory` | Required. See [`333-intent-vocabulary.md`](333-intent-vocabulary.md). |
| `value` | `str` | The canonical value on that concept's continuum. |
| `strength` | `IntentStrength` | Default `"PREFERRED"`. See [`343-intent-strength-and-priority.md`](343-intent-strength-and-priority.md). |
| `priority` | `int` | Default `0`. Not currently read by any real logic — see 343. |
| `provenance` | `IntentProvenance` | Required. Real code only ever sets `AI_NORMALIZED`. See [`344-intent-provenance.md`](344-intent-provenance.md). |
| `confidenceClass` | `IntentConfidence` | Required. Real code only ever sets `EXACT` or `HIGH_CONFIDENCE_NORMALIZATION`. See [`345-intent-confidence.md`](345-intent-confidence.md). |
| `sourceText` | `str` | The specific phrase this statement was extracted from. |
| `resolutionStatus` | `ResolutionStatus` | Required. Real code only ever sets `PRESERVED` or `CONFLICTING`. |
| `relatedJDLPaths` | `str[]` | Always empty in v1 (INTENT-GOV-001). Exists for a future resolver. |
| `diagnostics` | `str[]` | Always empty on the statement itself in v1 — diagnostics are attached at the `DesignIntent` level, not per-statement, in current code. |

## `IntentRelation`

| Field | Type | Notes |
|---|---|---|
| `relationId` | `str` | `f"relation-{uuid.uuid4()}"`. |
| `subject` | `IntentTarget` | |
| `predicate` | `RelationPredicate` | See [`336-relative-proportion-intent.md`](336-relative-proportion-intent.md). |
| `object` | `IntentTarget` | |
| `strength` | `IntentStrength` | Default `"PREFERRED"`. |
| `provenance` | `IntentProvenance` | Always `AI_NORMALIZED` in v1. |
| `resolutionStatus` | `ResolutionStatus` | `PRESERVED` or `CONFLICTING`. |
| `sourceText` | `str` | Default `""`. |

## `IntentConflict`

| Field | Type | Notes |
|---|---|---|
| `conflictId` | `str` | Derived from the two involved statement/relation IDs. |
| `type` | `ConflictType` | See [`346-intent-conflict-model.md`](346-intent-conflict-model.md). |
| `statementIds` | `str[]` | The two `intentId`/`relationId` values involved. |
| `description` | `str` | Human-readable, e.g. `"BAND.VISUAL_WEIGHT: 'DELICATE' ... vs 'BOLD' ..."`. |

## `IntentDiagnostic`

| Field | Type | Notes |
|---|---|---|
| `code` | `IntentDiagnosticCode` | One of 9 constants. See [`358-intent-diagnostics.md`](358-intent-diagnostics.md). |
| `severity` | `"info" \| "warning" \| "error"` | Never `"error"` in current code — unlike Designer's diagnostics, an intent diagnostic never fails the HTTP request. |
| `message` | `str` | |
| `statementId` | `str \| null` | Default `null`; not currently populated by `resolver.py` for any diagnostic it appends. |

## `IntentResolution` and `IntentProfile` — modeled, not yet wired up

`IntentResolution` (a record of how one statement was or wasn't resolved) and `IntentProfile` (a future versioned intent-to-JDL mapping) both exist as real Pydantic classes in `schemas.py`, with their own docstrings pointing at [`348-intent-resolution-model.md`](348-intent-resolution-model.md) and [`355-intent-profile-model.md`](355-intent-profile-model.md). Neither is constructed or persisted anywhere in current code — `IntentResolution` has no producer, and `DesignIntent.profile` is hardcoded `None` by `build_design_intent()`. They are shaped now specifically so a future resolution step (INTENT-GOV-018) has a real target to write into, not a speculative placeholder.

## `IntentDiffEntry`

Produced only by `compute_intent_diff()`, never stored on `DesignIntent` itself. See [`354-intent-diff-model.md`](354-intent-diff-model.md).

| Field | Type |
|---|---|
| `key` | `str` (`"{target}.{concept}"`) |
| `previousValue` | `str \| null` |
| `newValue` | `str \| null` |
| `changeType` | `"ADDED" \| "REMOVED" \| "CHANGED" \| "UNCHANGED"` |
