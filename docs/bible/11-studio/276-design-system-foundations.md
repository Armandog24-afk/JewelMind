---
id: JM-BIBLE-276
title: Design System Foundations
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-250
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Design System Foundations

## The existing foundation, confirmed and extended (not replaced)

`frontend/src/styles/theme.css` already defined a coherent token set before this Sprint: spacing (`--space-1` through `--space-6`), a dark surface hierarchy (`--color-bg`/`--color-surface`/`--color-surface-raised`), status colors (`--color-error`/`--color-warning`/`--color-info`/`--color-success`, each with a `-muted` background variant), a gold accent, two font families (UI sans + mono for technical data), and radius/shadow tokens. This Sprint's new components (`ModelStatusBadge`, `OutputsPanel`, `ArtifactRow`, the advanced-parameters disclosure) use exclusively these existing tokens — no new color, spacing unit, or font was introduced.

## What this Sprint added to the foundation

One addition: a consistent `:focus-visible` treatment (`outline: 2px solid var(--color-gold); outline-offset: 2px`) applied globally, replacing the previous form-field-only, always-on `:focus` border change — see [`272-accessibility-contract.md`](272-accessibility-contract.md).

## No heavyweight external design system

Per this Sprint's explicit instruction, no component library (Material UI, Radix, shadcn, etc.) was introduced. Every new control (`ModelStatusBadge`, `ArtifactRow`, `ViewModeSwitch` from Sprint 8) is a small, purpose-built component styled with plain CSS classes against the existing token set — consistent with the pre-existing codebase's approach.

## The viewer stays visually central

The 3D viewport retains the largest single area in the layout (`1fr` grid column) and its own dark/light backgrounds per view mode (Vision, Sprint 8) — none of this Sprint's additions (the header badge, the Outputs tab) compete with it for visual weight; both are compact (a single-line badge, a tab among five).

## Status semantics, centralized

| Tone | Used for |
|---|---|
| `neutral` | No model yet |
| `progress` | Generating/regenerating |
| `success` | Current model |
| `warning` | Stale model |
| `error` | Generation/regeneration failed |

This 5-tone mapping (`ModelStatusBadge`'s `TONE` table) is the one place model-lifecycle color is decided — restating [`267-status-and-feedback-system.md`](267-status-and-feedback-system.md)'s "no component invents its own wording" at the color level too.
