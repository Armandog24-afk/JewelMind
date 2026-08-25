---
id: JM-BIBLE-260
title: Output Review Experience
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-259
related_documents:
  - JM-BIBLE-261
implementation_status: current
professional_validation: not_required
normative: true
---

# Output Review Experience

## The consolidated Outputs area, exactly as shipped

`OutputsPanel.tsx`, a new tab in `RightPanelTabs`, lists all 5 current output types through one repeated `ArtifactRow`:

| Output | Purpose text shown to the user |
|---|---|
| STEP | "Neutral CAD exchange for further professional CAD work." |
| STL | "Tessellated mesh for 3D printing and prototyping workflows." |
| JDL JSON | "The editable JewelMind design definition itself." |
| Technical specification | "Design and generation information, in one document." |
| Presentation PNG | "A visual image of the generated model, captured from the Presentation view." |

Each row shows: name, purpose, current availability (via `OUTPUT_ELIGIBILITY_LABELS`), and one action button — matching this Sprint's own required fields exactly ("output name; purpose; availability; current/stale relationship; action").

## Current/stale relationship, per output

Every row's eligibility comes from the identical `computeOutputEligibility()` function (STEP/STL/JSON/specification) or the equivalent `captureBlockedReason()`-derived mapping (PNG) — both keyed on the same `isStale` flag the model-status badge reads. There is no output-specific staleness rule; restating STUDIO-GOV-007 concretely.

## A real gap this consolidation closed

Before this Sprint, `runExport('specification')` and `exportSpecification()` already existed in `useProjectStore`/`api/client.ts`, but **no button anywhere called them** — the Specification tab only ever fetched the text for inline reading (`fetchSpecificationText()`, a separate, non-downloading call). The consolidated Outputs panel is the first place a user can actually download the technical specification file, not just read it inline.

## Avoiding technical clutter

Purpose text is one short sentence per output, written for a jeweler, not a software engineer — no mention of MIME types, ISO-10303, or STL/OCCT internals in the visible copy (those live in the Bible, not the product UI). Restates STUDIO-GOV-011/[`280-product-copy-and-terminology.md`](280-product-copy-and-terminology.md).
