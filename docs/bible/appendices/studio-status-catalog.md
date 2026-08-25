---
id: JM-BIBLE-A51
title: "Appendix: Studio Status Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-267
related_documents:
  - JM-BIBLE-A49
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Studio Status Catalog

Restates [`11-studio/267-status-and-feedback-system.md`](../11-studio/267-status-and-feedback-system.md) as a standalone reference — two distinct vocabularies, never conflated.

## Message severity

| Level | Real mapping |
|---|---|
| `INFO` | `information`-severity `ValidationResult` |
| `SUCCESS` | No dedicated component exists — see the toast/notification gap in [`283-studio-gap-analysis.md`](../11-studio/283-studio-gap-analysis.md) |
| `WARNING` | `warning`-severity `ValidationResult` |
| `ERROR` | `error`-severity `ValidationResult`, or `ErrorBanner` for a generation/preview failure |

## Model status tone (5 values, from `ModelStatusBadge`'s `TONE` table)

`neutral` (NO_MODEL), `progress` (GENERATING_FIRST_MODEL/REGENERATING), `success` (CURRENT), `warning` (STALE), `error` (FAILED_NO_MODEL/FAILED_WITH_LAST_GOOD).
