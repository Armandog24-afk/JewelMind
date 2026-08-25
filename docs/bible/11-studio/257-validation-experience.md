---
id: JM-BIBLE-257
title: Validation Experience
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-250
related_documents:
  - JM-BIBLE-259
implementation_status: current
professional_validation: not_required
normative: true
---

# Validation Experience

## The status hierarchy, mapped to real states

| Status (conceptual) | Real signal |
|---|---|
| READY TO GENERATE | No blocking (`error`-severity) validation results; Generate button enabled |
| WARNING | `warning`/`information`-severity results present, but no `error` — Generate still enabled |
| BLOCKED | At least one `error`-severity result — Generate button disabled, with a `title` explaining why |
| GENERATING | `generationStatus === 'generating'` — `LoadingOverlay` shown |
| CURRENT MODEL | `computeModelState()` → `CURRENT` |
| STALE MODEL | `computeModelState()` → `STALE` |
| GENERATION FAILED | `computeModelState()` → `FAILED_NO_MODEL` or `FAILED_WITH_LAST_GOOD` |

The first three are validation-specific (already real, pre-existing behavior in `ProjectActions`/`hasErrors()`); the last four are the unified `ModelStateKey` from [`259-model-state-experience.md`](259-model-state-experience.md) — this document is the validation-specific half, that document is the generation-lifecycle half, and together they cover every status this Sprint's brief listed.

## Per-diagnostic information, already present

Every `ValidationResult` the backend (and its frontend mirror) produces already carries `severity`, `parameter`, `message`, `ruleId`, and an optional `suggestedValue` — confirmed by inspecting `shared/validation/rules.py`'s type and `ValidationItem.tsx`'s rendering. This Sprint did not need to add these fields; they already satisfied "severity, affected parameter, explanation, suggested correction" from day one. What Studio contributes is presentation: results are severity-ordered (`error` first) in `ValidationPanel.tsx`, unchanged from before this Sprint but confirmed still correct.

## No raw backend error blobs

`ValidationItem` renders `result.message` (a human-authored string from `validation/rules.py`) plus a compact `ruleId · parameter` line — never a raw exception, stack trace, or JSON blob. The `ruleId` remains visible specifically so it stays available for support/debugging conversations, per this Sprint's own instruction ("technical codes may remain accessible for debugging/details").

## What changed vs. what was preserved

**Preserved**: `ValidationPanel.tsx`, `ValidationItem.tsx`, and the underlying `shared/validation/engine.ts` — all unchanged. **Added**: the unified `ModelStatusBadge` that gives the READY/BLOCKED distinction a permanent, header-level home instead of being visible only via the Generate button's own disabled state.
