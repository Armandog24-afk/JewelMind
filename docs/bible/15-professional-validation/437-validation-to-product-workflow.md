---
id: JM-BIBLE-437
title: Validation to Product Workflow
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-435
  - JM-BIBLE-436
implementation_status: current
professional_validation: not_required
normative: false
---

# Validation to Product Workflow

## What professional feedback can affect outside Forge and Atlas

Not every finding implies a rule or geometry change. A review may instead reveal that JewelMind's own product surface is misleading or incomplete, affecting:

- **warnings** — a Forge diagnostic message that a professional finds confusing or insufficiently specific;
- **UI explanations** — copy in Studio, the Designer/Conversation panels, or a generated review package that doesn't accurately describe what a reviewer would actually need to know;
- **workflow** — the order or grouping of steps a user takes (e.g. should "Review Mode" be more discoverable);
- **terminology** — a mismatch between JewelMind's internal vocabulary and real jewelry-industry usage;
- **review prompts** — the actual questions asked in `docs/professional-review/*.md` or the auto-generated `review-form.md`;
- **parameter exposure** — whether a field is shown in the "Design" vs. "Advanced" parameter split (`docs/bible/11-studio/`).

## Even a product-only change still requires implementation review

A UI-wording change is lower-risk than a Forge rule change, but it is not zero-risk — a wording change can itself misrepresent JewelMind's actual validation status (e.g. accidentally implying something is "approved" when it isn't, the exact failure mode PROVAL-GOV exists to prevent). The same discipline as [`435-validation-to-forge-workflow.md`](435-validation-to-forge-workflow.md) and [`436-validation-to-atlas-workflow.md`](436-validation-to-atlas-workflow.md) applies: professional feedback informs a proposed change; a developer reviews and implements it; nothing is committed to frontend copy or documentation directly from a `ReviewObservation`'s free text.

## Cross-references

- [`438-professional-review-audit-trail.md`](438-professional-review-audit-trail.md) — how a product-facing change originating from review feedback is still tracked back to its source finding.
- [`452-open-professional-validation-questions.md`](452-open-professional-validation-questions.md) — open questions about exactly which language ("professionally reviewed", "manufacturing-ready") should ever be used in product copy, and under what evidentiary threshold.
