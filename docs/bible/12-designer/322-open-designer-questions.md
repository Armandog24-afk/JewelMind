---
id: JM-BIBLE-322
title: Open Designer Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-321
related_documents:
  - JM-BIBLE-DESIGNER-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Open Designer Questions

This document records open product and policy questions raised while building Sprint 10 that this Sprint does not answer. None of these should be resolved by silently picking a default in code — each needs a deliberate decision, and several would require an RFC or ADR per [`290-designer-governance.md`](290-designer-governance.md) if acted on.

1. Should low-risk changes ever auto-apply without review, or must every Designer-originated change always pass through the review screen described in [`310-user-review-and-acceptance.md`](310-user-review-and-acceptance.md)?
2. Which value types, if any, should always require explicit user confirmation regardless of confidence — even an `EXACT`-confidence field?
3. Should Designer ever propose multiple competing candidate designs per request instead of the single proposal it produces today?
4. Should vague aesthetic intent get its own persisted, structured storage, separate from `unresolvedIntent`'s current plain string list?
5. Should unresolved descriptors persist across sessions for a future Design Intent Model to consume, rather than being discarded once a proposal is applied or cancelled?
6. Should Designer become aware of a user's historical style preferences, and if so, how does that interact with the current stateless, no-accounts architecture?
7. How should prompt design extend past Italian and English to a third language, and what does that mean for `normalizer.py`'s synonym tables?
8. Should Studio ever expose a provider-selection control in the UI, instead of the current environment-variable-only configuration (`DESIGNER_PROVIDER`/`ANTHROPIC_API_KEY`)?
9. Should professional users be able to fully disable AI-sourced defaults/inference for their own workflow, even when a provider is configured?
10. How would a future image/sketch intent entry point (see [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md)) fit into this same proposal-review architecture, rather than requiring a parallel one?
11. Should confidence and provenance be shown more richly in the review UI than today's plain text labels (e.g. visually distinct badges, a filter by provenance)?
12. Should token or cost information ever be exposed to end users, and if so, where — per-request, cumulative, or not at all?

## Why these stay open rather than defaulted

Several of these questions look like they have an obvious answer until the specific failure mode is considered: auto-applying "low-risk" changes (question 1) sounds convenient until a "low-risk" `INFERRED` numeric value turns out to matter more than expected for one particular design; disabling AI-sourced defaults per-user (question 9) sounds like a reasonable escape hatch until it has to interact with the review-before-apply flow every proposal already goes through. None of them are answered by this Sprint because none of them are implementation questions — they are product and trust decisions that belong to whoever owns JewelMind's roadmap, informed by real usage once a provider is live (see [`317-designer-cost-and-latency-model.md`](317-designer-cost-and-latency-model.md)).

The most consequential of these — question 1, 4, 5, and 6 — converge on the same future concept named throughout this Sprint's documents: **Design Intent Model v1 — formal semantic layer for aesthetic and conceptual intent such as delicate, bold, minimal, classic and proportional relationships, without converting subjective language into arbitrary CAD dimensions.**
