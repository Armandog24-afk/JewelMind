---
id: JM-BIBLE-267
title: Status and Feedback System
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-250
related_documents:
  - JM-BIBLE-A51
implementation_status: current
professional_validation: not_required
normative: true
---

# Status and Feedback System

## Two separate systems, not one — confirmed as a deliberate distinction

| System | Values | Owner |
|---|---|---|
| Message severity | `INFO`, `SUCCESS`, `WARNING`, `ERROR` | `ValidationItem`'s severity classes (`error`/`warning`/`information` today — `INFO` maps to `information`); `ErrorBanner` for `ERROR`; no dedicated `SUCCESS`/`INFO` toast component exists yet (see gap below) |
| Model status | The 7-value `ModelStateKey` | `computeModelState()` / `ModelStatusBadge` — a distinct, richer vocabulary describing the model's lifecycle, never conflated with generic message severity |

Conflating these two would have been a real mistake: "the model is stale" is not an error, warning, or success message — it is a lifecycle fact best expressed in its own vocabulary, which is exactly why [`259-model-state-experience.md`](259-model-state-experience.md) defines a separate 7-state model rather than overloading a 4-value severity enum.

## No component invents its own wording

Every place that shows the model's status (`AppHeader`, `ModelViewport`, `OutputsPanel`'s eligibility labels) sources its text from the same two functions: `describeModelState()` and `OUTPUT_ELIGIBILITY_LABELS`. Before this Sprint, the viewport's stale banner had its own hardcoded string ("Parameters changed — regenerate model.") independent of anything else — a real, now-closed inconsistency risk.

## A real, honest gap: no generic toast/notification system

`specs/studio/v1/notification.schema.json` documents a conceptual `INFO`/`SUCCESS`/`WARNING`/`ERROR` notification shape, but no runtime toast/snackbar component exists in this codebase — feedback today is always inline (a banner, a badge, a disabled button with a title) rather than a transient notification. This is recorded honestly as PLANNED, not implemented under a different name.

## Real test coverage

`ModelStatusBadge` is exercised indirectly through `modelState.test.ts`'s coverage of every state's label/detail; `AppHeader`/`ModelViewport` were verified live this Sprint to render the identical wording for the same computed state.
