---
id: JM-BIBLE-252
title: Information Architecture
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-251
related_documents:
  - JM-BIBLE-265
implementation_status: current
professional_validation: not_required
normative: true
---

# Information Architecture

## The four conceptual zones, and how they actually map to panels

| Zone | Real UI |
|---|---|
| DESIGN | `.panel--left` → `ProfessionalReviewNotice` + `ConfigurationPanel` |
| REVIEW | `.panel--center` → `ModelViewport` (Technical/Presentation, Vision) |
| VALIDATION | `.panel--right`'s `Validation` tab |
| OUTPUT | `.panel--right`'s `Outputs` tab (new this Sprint) |

These are not four permanent, equal-sized panels — VALIDATION and OUTPUT share the same right-hand panel as tabs alongside `Specification`, `JSON`, and `Model info`, exactly as the pre-Sprint-9 UI already did for the first three. This Sprint added `Outputs` as a fifth tab rather than a fifth panel, preserving the existing 3-column layout (`.app-body { grid-template-columns: 340px 1fr 380px }`) which already gives REVIEW (the viewport) the largest area, per the desktop-priority requirement in [`265-layout-system.md`](265-layout-system.md).

## Why a tab, not a new panel

Adding a literal fourth column for OUTPUT would either shrink the viewport (violating the desktop-priority requirement) or require a wider window than most desktop displays comfortably offer. A tab inside the existing right panel achieves the same "OUTPUT is a first-class, discoverable zone" goal without either cost — and matches how VALIDATION, Specification, JSON, and Model info already coexist in that same panel.

## Header row

The header (`AppHeader.tsx`) carries the brand, the `ModelStatusBadge` (new this Sprint — a compact, always-visible status read without needing to look at the viewport or a tab), the primary `Generate`/`Regenerate` action, `Reset`, and backend connectivity — matching this Sprint's own suggested header row ("JewelMind / Project / Model status / Actions") closely, with "Project" represented by the design name field inside the DESIGN zone rather than duplicated in the header.

## Contextual status strip

The brief's diagram includes a bottom "contextual status/diagnostics/generation information" strip. This Sprint did not add a literal fifth, permanent strip — that information already surfaces contextually: generation status via `LoadingOverlay`/`ErrorBanner` inside the viewport, and diagnostics via the Validation tab. Adding a duplicate, always-present strip risked exactly the "components inventing their own unrelated wording" problem [`267-status-and-feedback-system.md`](267-status-and-feedback-system.md) warns against.
