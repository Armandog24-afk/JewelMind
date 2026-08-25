---
id: JM-BIBLE-353
title: Intent Preservation
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-352
related_documents:
  - JM-BIBLE-354
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Preservation

## What "preserved" must mean in practice

An `IntentStatement` with `resolutionStatus: PRESERVED` is a promise: JewelMind understood the aesthetic language and will not lose track of it, even though it will not (yet) turn it into a number. This document covers what preservation actually survives today, and what it deliberately does not.

## Survives: proposal review and apply

`proposal.designIntent` is rendered in `DesignerPanel.tsx`'s review card (the "Design intent" / "Conflicting intent" / "Not yet mapped to a technical parameter" sections — see [`357-studio-intent-review.md`](357-studio-intent-review.md)) before any apply action. `handleApply()` calls `useDesignIntentStore.applyIntent(proposal.designIntent)` unconditionally whenever the intent has content, independent of whether the accompanying JDL diff has any changes.

## Survives: manual editing in `ConfigurationPanel`

`ConfigurationPanel` — the existing full parameter editor — writes only to `useProjectStore.currentDefinition` via its own `updateXxx()` actions. None of those actions reference `useDesignIntentStore`. Editing a numeric field by hand therefore leaves `currentIntent` completely untouched, in either direction: manual edits never modify stored intent, and stored intent never overrides a manual edit (INTENT-GOV-004, INTENT-GOV-016).

## Survives: regeneration

Neither `useProjectStore.generate()` nor `applyDesignerProposal()` calls `useDesignIntentStore.clearIntent()`. A model regeneration marks the model stale and produces new geometry, but the design-intent summary above it in the UI is unaffected.

## Survives: multi-turn MODIFY merging

Within a session, `build_design_intent()`'s MODIFY-mode merge (keyed by `(target, concept)` for statements, `(subject, object)` for relations) means a statement from an earlier turn survives every later turn unless a new statement on the exact same key replaces it, or the user removes it explicitly. See [`352-unresolved-intent-lifecycle.md`](352-unresolved-intent-lifecycle.md) for the unresolved-descriptor half of this.

## Does NOT survive: a page reload

`useDesignIntentStore` is a plain Zustand store with no persistence middleware — unlike `useProjectStore`, whose `currentDefinition` is expected to be the durable design-of-record, `currentIntent` is held only in memory. A browser refresh loses it entirely. This is a real, deliberate v1 scope limit, directly following this Sprint's own instruction to prefer a separate DesignIntent state rather than entangling it with JDL persistence — not an oversight. It is listed again in [`362-design-intent-gap-analysis.md`](362-design-intent-gap-analysis.md).

## Does NOT survive: JDL JSON export or the technical specification

Exported JDL JSON (`exporters/`) and the technical specification export contain only `JewelryDefinition` fields. `DesignIntent` is never embedded in either artifact today. This follows the same brief instruction directly: do not inject non-JDL fields into canonical JDL unless JDL explicitly evolves to support metadata — no such evolution has happened in v1. A future JDL metadata block is an open question, not a decision; see [`363-open-design-intent-questions.md`](363-open-design-intent-questions.md), question 5.

## One deliberate exception: `resetProject()`

`useProjectStore.resetProject()` is the one place `currentDefinition` and `currentIntent` are intentionally coupled: it calls `useDesignIntentStore.getState().clearIntent()` as its last step. Starting a new design correctly clears old intent along with old JDL — this is the single one-way dependency INTENT-GOV-004 permits.

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md) — INTENT-GOV-004, INTENT-GOV-015, INTENT-GOV-016.
- [`352-unresolved-intent-lifecycle.md`](352-unresolved-intent-lifecycle.md) — preservation of the unresolved-descriptor list specifically.
- [`357-studio-intent-review.md`](357-studio-intent-review.md) — the review UI these preservation guarantees feed.
- [`362-design-intent-gap-analysis.md`](362-design-intent-gap-analysis.md) — persistence and export gaps as future work.
