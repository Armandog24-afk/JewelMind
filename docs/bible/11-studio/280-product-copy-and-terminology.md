---
id: JM-BIBLE-280
title: Product Copy and Terminology
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-250
related_documents:
  - JM-BIBLE-A53
implementation_status: current
professional_validation: not_required
normative: true
---

# Product Copy and Terminology

## Controlled user-facing terms, confirmed in use

`Generate model` / `Regenerate model`, `Technical` / `Presentation`, `Current model` / `Design changed`, `Validation`, `Outputs`, `STEP`, `STL`, `Technical specification` — every one of these exact strings appears verbatim in the running UI, confirmed by live inspection this Sprint (`get_page_text` output matched this list exactly).

## Internal architecture names never shown to normal users

`Forge`, `Atlas`, `Alchemist`, `Foundry`, and `Vision` do not appear anywhere in `frontend/src/components/` — confirmed by inspection. `Vision` and its layer-mates are internal Bible/architecture names for coding agents; the product itself only ever says `Technical`/`Presentation` (the two Vision views) or a plain output name (`STEP`, `STL`, `Presentation PNG`). "StoneReference" (the internal, code-facing term) is shown to users as **"Stone (reference)"** — confirmed in `ComponentVisibilityPanel`'s label map.

## Where the controlled vocabulary lives

This document is descriptive (it records terms already in use); [`04-jewelry-domain/`](../04-jewelry-domain/README.md) and [`00-foundation/008-glossary.md`](../00-foundation/008-glossary.md) remain the authoritative controlled vocabularies for jewelry-domain and architecture terms respectively — Studio does not define a third, competing glossary. STUDIO-GOV-011 requires consulting those, not inventing new terms independently.

## No manufacturing-readiness language anywhere in Studio's own copy

Every new string this Sprint added (`OutputsPanel`'s purpose descriptions, `ModelStatusBadge`'s labels/details, `ArtifactRow`'s status labels) was checked against LAW-010: none claims or implies the generated model, any export, or the captured PNG is ready for production. The existing `ProfessionalReviewNotice` remains the single, unmodified authoritative disclaimer text.
