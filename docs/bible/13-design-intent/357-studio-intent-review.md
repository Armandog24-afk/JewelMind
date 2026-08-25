---
id: JM-BIBLE-357
title: Studio Intent Review
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-356
related_documents:
  - JM-BIBLE-358
implementation_status: current
professional_validation: not_required
normative: true
---

# Studio Intent Review

## Why this UI matters more than its size suggests

The brief for this Sprint frames the review UI as essential for user trust, and this document adopts that framing directly: a user must never be able to look at a generated model and believe their unresolved aesthetic request was already satisfied. Every status label in this section exists to prevent that specific misunderstanding.

## The real `DesignerPanel.tsx` proposal-review sections

Inside the existing proposal-review card (`../12-designer/310-user-review-and-acceptance.md`'s numbered sequence), Design Intent adds:

1. **"Design intent"** — one entry per `proposal.designIntent.statements[i]`, rendered as `{target}: {value} ({concept})` plus a resolution label from `RESOLUTION_LABEL`:
   - `PRESERVED` -> **"Preserved — not yet technically resolved"**
   - `CONFLICTING` -> **"Conflicting — needs your attention"**
2. **"Conflicting intent"** — rendered only when `proposal.designIntent.conflicts.length > 0`, listing each conflict's description.
3. **"Not yet mapped to a technical parameter"** — rendered only when `proposal.designIntent.unresolvedDescriptors.length > 0`, using the exact required copy per entry: *"'{text}' has been preserved as design intent. JewelMind does not currently convert this subjective preference into arbitrary dimensions."*

## The persistent compact summary

Outside any active proposal review — visible whenever `currentIntent` has content, regardless of whether a proposal is currently being reviewed — `DesignerPanel.tsx` renders a compact "Design intent" summary (`role="region" aria-label="Current design intent"`) listing every statement and unresolved descriptor as a removable tag with a × button, backed by `useDesignIntentStore.removeStatement()` / `removeUnresolvedDescriptor()`.

## The stale-model fix, and why it lives here

`handleApply()` makes two independent calls:

- `useProjectStore.applyDesignerProposal()` — called **only when** `proposal.diff.some(d => d.changed)` is true. This is what marks the model stale.
- `useDesignIntentStore.applyIntent(proposal.designIntent)` — called unconditionally whenever the intent has content, regardless of the JDL diff.

Because these are fully independent, a pure-aesthetic MODIFY ("make it more minimal") — which produces design intent statements but no JDL diff — never marks the model stale. A real technical MODIFY (e.g. "use platinum") still does, exactly as it always did. The natural-language request now always sends `currentJDL` (both CREATE and MODIFY, previously MODIFY-only), which is what makes `proposal.diff` a meaningful signal in both interaction modes — this fix is the real, concrete improvement this Sprint made to Sprint 10's own stale-model logic.

## A known, deliberate simplification

There is no dedicated "edit a statement's value inline" control. A user who wants to change their mind about a statement either describes it again in a follow-up request (which the MODIFY merge then overwrites by `(target, concept)` key — see [`353-intent-preservation.md`](353-intent-preservation.md)) or removes it via the × button. There is no value-editing widget, because aesthetic values are categorical strings, not `NumericField`-style controls a slider or number input could meaningfully edit. This mirrors Sprint 10's own documented "two buttons, not three" simplification (`../12-designer/310-user-review-and-acceptance.md`) — a capability judged unnecessary given the surrounding UI, not an oversight.

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md) — INTENT-GOV-007, INTENT-GOV-015.
- `../12-designer/310-user-review-and-acceptance.md` — the surrounding review sequence this extends.
- `../11-studio/272-accessibility-contract.md` — the accessible-control requirement the × buttons and `role="region"` satisfy.
- [`352-unresolved-intent-lifecycle.md`](352-unresolved-intent-lifecycle.md) — what removing a tag does and does not do.
