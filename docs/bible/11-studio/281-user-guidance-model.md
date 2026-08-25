---
id: JM-BIBLE-281
title: User Guidance Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-280
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# User Guidance Model

## Contextual help, added this Sprint

| Location | Guidance text |
|---|---|
| `OutputsPanel` intro | "Every output below is generated on demand from the current model — nothing is pre-rendered or cached beyond that." |
| Each `ArtifactRow` | A one-sentence purpose description (see [`260-output-review-experience.md`](260-output-review-experience.md)'s table) |
| Advanced parameters disclosure | "These control exact dimensions and preview quality directly. Most designs only need the parameters above." |
| Generate button (disabled) | "Resolve the blocking validation errors first" |
| Every shortcut-bearing button | Its key, in the native `title` tooltip |

All are short, single-sentence tooltips or inline captions — none is a multi-paragraph tutorial block, per this Sprint's explicit "do not flood the interface with tutorial text" instruction.

## Pre-existing guidance, confirmed unchanged

`ProfessionalReviewNotice`'s manufacturing-review disclaimer, `ComponentVisibilityPanel`'s "Stone (reference)" label, and every camera-preset button's descriptive title (Sprint 8) — none were altered, all still present.

## Where guidance was deliberately NOT added

No first-run onboarding tour, no dismissible tooltip callouts, and no help sidebar were introduced — a small, professional tool's interface should be legible from its labels and inline copy alone at this stage, matching this Sprint's "prefer tooltips/short explanations" instruction over building a guidance system.
