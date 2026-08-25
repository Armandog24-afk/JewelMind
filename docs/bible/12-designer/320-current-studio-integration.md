---
id: JM-BIBLE-320
title: Current Studio Integration
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-319
related_documents:
  - JM-BIBLE-321
implementation_status: current
professional_validation: not_required
normative: true
---

# Current Studio Integration

## Where `DesignerPanel` sits

`frontend/src/App.tsx` renders the left panel in a fixed order: `ProfessionalReviewNotice`, then `DesignerPanel`, then `ConfigurationPanel`. Designer is a new entry point placed above the existing parameter editor, not a replacement for it — the parameter editor remains rendered, visible, and fully editable regardless of whether a Designer proposal exists, is being reviewed, or was just applied (STUDIO-GOV-011's Bible/architecture-name-hiding discipline is also respected here: nothing in `DesignerPanel.tsx`'s UI copy names "Forge," "Atlas," "Alchemist," or "Foundry").

## Mapping every real UI element to Studio's existing structure

| `DesignerPanel.tsx` element | Studio concept it integrates with |
|---|---|
| Textarea + mode radio + Interpret button | A new input surface, entirely local component state (`text`, `mode`) — never written to `useProjectStore` until Apply |
| "AI interpretation is unavailable" banner (`providerUnavailable`) | Rendered only on `DESIGNER_PROVIDER_UNAVAILABLE`; `ConfigurationPanel` underneath keeps working exactly as before this Sprint |
| "You asked" / "JewelMind understood" / clarification / unsupported sections | Pure read-only review of the in-flight `DesignerResult`, described fully in [`310-user-review-and-acceptance.md`](310-user-review-and-acceptance.md) |
| Forge summary line | Reads `proposal.forgeEvaluation` — the same `ValidationResult` shape the existing Validation tab already renders |
| Apply proposal button | Calls `useProjectStore.applyDesignerProposal(candidateJDL)` |
| Cancel button | Clears local `result` state only; touches no store state at all |

## `applyDesignerProposal()` integrates through the existing staleness mechanism

`applyDesignerProposal` is implemented as `(definition) => set((state) => withUpdatedDefinition(state, definition))` — the identical helper every other `updateXxx()` action (`updateRing`, `updateBand`, `updateMaterial`, ...) already uses. This means accepting a proposal: persists the new definition via `saveDefinition()`, re-runs `validateDefinition()` to refresh `validationResults`, and sets `isStale: true` whenever `generatedModel` is not `null` — exactly the same staleness rule a manual parameter edit triggers. Designer introduces no second code path for "the design changed," and no separate staleness flag; a Designer-originated change and a manually-typed change are indistinguishable to every downstream consumer of `currentDefinition` and `isStale` (STUDIO-GOV-004/013).

## Generate/Regenerate remains fully separate and deliberate

Nothing in `applyDesignerProposal()`, `handleApply()`, or any other Designer code path calls `useProjectStore.generate()`. Applying a proposal only ever updates `currentDefinition` and marks the existing model (if any) stale — regenerating geometry, exporting, and every other action gated on `isStale` remain exactly where they were before this Sprint, triggered only by the user's own explicit Generate/Regenerate click (DESIGNER-GOV-018).

See the README's "Relationship to Sprint 9" section, and [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md) for integration points not yet built (a dedicated diff view, richer provenance display).
