---
id: JM-BIBLE-310
title: User Review and Acceptance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-309
related_documents:
  - JM-BIBLE-311
implementation_status: current
professional_validation: not_required
normative: true
---

# User Review and Acceptance

## The real `DesignerPanel.tsx` review structure

Once a `DesignerResult` is returned, `DesignerPanel.tsx` renders a fixed sequence of review sections, each conditional on having content:

1. **"You asked"** — the verbatim `proposal.sourceText`, so the user can confirm what was actually interpreted.
2. **"JewelMind understood"** — every `proposal.proposedFields` entry, each labeled with its provenance via `PROVENANCE_LABEL` (e.g. `AI_INTERPRETATION` -> "From your description").
3. **"Not yet mapped to a technical parameter"** — `proposal.unresolvedIntent`, plain descriptive strings the pipeline could not and did not force into a dimension.
4. **"A few questions"** — every `proposal.clarificationQuestions`, each with clickable option buttons (`handleClarify`).
5. **"Not currently supported"** — every `proposal.unsupportedFeatures`, with its reason and, when known, a suggested alternative.
6. **Forge summary line** — "Design rule check: N errors, N warnings" when `candidateJDL` exists, or an explicit "could not form a valid design" alert when it doesn't.
7. **Apply proposal / Cancel buttons.**

## `currentDefinition` is never mutated before Apply

Everything above is rendered from local component state (`result`), not from `useProjectStore`. `handleApply()` is the only place `applyDesignerProposal(result.proposal.candidateJDL)` is called, and it is the only path from a review screen to the authoritative design state. There is no code path — auto-apply on receipt, apply-on-clarify, apply-on-hover — that writes `candidateJDL` into `currentDefinition` before the user explicitly clicks Apply proposal (DESIGNER-GOV-018).

## Two buttons shipped, not three — a deliberate simplification

The original Sprint 10 brief's mockup showed three actions: **[Apply proposal] [Edit] [Cancel]**. This implementation ships two: **Apply proposal** and **Cancel**. The reason is architectural, not an oversight: `ConfigurationPanel` — the existing, full parameter editor — is rendered directly below `DesignerPanel` in `App.tsx` and stays visible and fully editable both before and after a proposal is reviewed or applied (see [`320-current-studio-integration.md`](320-current-studio-integration.md)). A dedicated "Edit mode" button on the proposal card itself would duplicate a capability the user already has one scroll away, with no additional editing power it could offer beyond what `ConfigurationPanel` already provides. Cutting it kept the review surface focused on its one real job — accept or discard the AI's interpretation — while editing individual values remains exactly where it already lived.

See [`311-proposal-diff-model.md`](311-proposal-diff-model.md) for how the diff data this review screen could someday render in more detail is already computed but not yet used that way.
