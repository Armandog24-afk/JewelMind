---
id: JM-BIBLE-253
title: User Workflow Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-251
related_documents:
  - JM-BIBLE-259
implementation_status: current
professional_validation: not_required
normative: true
---

# User Workflow Model

## The 17-step primary workflow, confirmed by live browser verification this Sprint

| # | Step | Verified this Sprint? |
|---|---|---|
| 1 | User opens JewelMind | Yes |
| 2 | Default solitaire definition is available | Yes — `createDefaultDefinition()`, or a restored local design (see [`275-session-recovery.md`](275-session-recovery.md)) |
| 3 | User edits parameters | Yes |
| 4 | Validation updates | Yes — instant, client-side |
| 5 | User sees whether generation is allowed | Yes — `ModelStatusBadge` + Generate button's disabled state |
| 6 | User clicks Generate | Yes |
| 7 | Loading state is visible | Yes — `LoadingOverlay`, "Generating model…" |
| 8 | Backend generates geometry | Yes — real `POST /api/models/generate`, confirmed via network inspection |
| 9 | Current model appears | Yes — `ModelStatusBadge` → "Current model" |
| 10 | User reviews Technical or Presentation view | Yes |
| 11 | User changes a parameter | Yes |
| 12 | Existing model becomes visibly STALE | Yes — "Design changed" badge, confirmed via live inspection |
| 13 | Previous model remains visible | Yes — `lastSuccessfulPreview` unchanged |
| 14 | User regenerates | Yes — including via the `G` keyboard shortcut |
| 15 | New model replaces previous model only after successful generation | Yes — `generate()`'s success branch is the only writer of `lastSuccessfulPreview` |
| 16 | User reviews diagnostics | Yes — Validation tab |
| 17 | User exports desired outputs | Yes — STEP export confirmed via a real `POST /api/models/export/step` call during this Sprint's verification |

See [`SPRINT-9-VALIDATION-REPORT.md`](SPRINT-9-VALIDATION-REPORT.md) for the exact sequence of browser actions and network requests this table is grounded in.

## What this workflow is not

Not a wizard, not a multi-page flow, and not gated behind sequential steps a user must complete in order — every step above is available at any time from the single workspace; the table describes a *typical* session, not an enforced sequence.
