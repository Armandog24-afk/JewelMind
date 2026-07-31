---
id: JM-BIBLE-041
title: Jewelry Product Taxonomy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-040
related_documents:
  - JM-BIBLE-006
  - JM-BIBLE-042
implementation_status: partial
professional_validation: preliminary
---

# Jewelry Product Taxonomy

**Purpose:** ensure the current model does not make future jewelry
categories impossible — not to design them. No schema for any category
below `Ring` is proposed here.

## `JewelryProduct` (top-level concept)

`JewelryProduct` is the conceptual root every jewelry category belongs to.
It is not a class in the current code — `backend/jewelmind/domain/schema.py`
only ever instantiates the `ring`/`solitaire` case
(`jewelry.category: Literal["ring"]`, `jewelry.style: Literal["solitaire"]`).
`JewelryProduct` exists in this document purely to give future categories
a place to attach without requiring a rewrite of `JewelryInfo`.

## Category table

| Category | Definition | Status | Likely shared components | Category-specific components |
|---|---|---|---|---|
| **Ring** | A closed band worn around a finger, optionally carrying a stone/setting. | **CURRENT** (solitaire style only — see [`042-ring-taxonomy.md`](042-ring-taxonomy.md)) | Material, stone, setting, manufacturing context, preview, validation, artifacts | Band/shank, inner diameter |
| **Earring** | A piece worn on or through the ear. | **VISION** | Material, stone, setting, manufacturing context, preview, validation, artifacts | Post/hook/clip mechanism, ear-facing geometry |
| **Pendant** | A piece suspended from a chain or cord, typically resting on the chest. | **VISION** | Material, stone, setting, manufacturing context, preview, validation, artifacts | Bail/suspension point |
| **Necklace** | A continuous piece worn around the neck. | **VISION** | Material, manufacturing context, preview, validation, artifacts | Chain/link construction, clasp |
| **Bracelet** | A piece worn around the wrist, typically with a clasp. | **VISION** | Material, manufacturing context, preview, validation, artifacts | Clasp, link/chain construction |
| **Bangle** | A rigid, usually clasp-less piece worn around the wrist. | **VISION** | Material, manufacturing context, preview, validation, artifacts | Opening mechanism (if any), rigid hoop geometry |
| **Brooch** | A piece pinned to fabric. | **VISION** | Material, stone, setting, manufacturing context, preview, validation, artifacts | Pin/catch mechanism, back-facing geometry |
| **Charm** | A small decorative piece attached to another jewelry item. | **VISION** | Material, manufacturing context, preview, validation, artifacts | Attachment loop |
| **Cufflink** | A paired fastener for shirt cuffs. | **VISION** | Material, manufacturing context, preview, validation, artifacts | Toggle/fastening mechanism, pairing (left/right or symmetric) |

Every category above `Ring` is **VISION**, not **PLANNED** — none has a
concrete near-term implementation intention as of this Sprint. See
[`00-foundation/000-bible-governance.md`](../00-foundation/000-bible-governance.md)
for why that distinction matters.

## Concepts that may be shared across categories

These are concepts the current `ring`/`solitaire` implementation already
expresses in a way that is *not inherently ring-specific*, and that a
future category could plausibly reuse rather than reinvent:

- **Material** (`MaterialSpec` — metal selection) — the concept "what
  metal is this made of" applies to any category.
- **Stone** (`StoneSpec` — shape/diameter/depth reference) — applies to
  any category that can carry a set stone.
- **Setting** (`SettingSpec` — how a stone is held) — same reasoning.
- **Dimensions** — every category needs *some* dimensional parameter set,
  though the specific dimensions differ (a ring's inner diameter has no
  equivalent in, say, a brooch).
- **Manufacturing context** (`ManufacturingSpec` — casting vs. printing)
  — applies to any category producible by the same processes.
- **Component assembly** (the `GeneratedModel` pattern of named
  components combined into one model) — the pattern, not the specific
  band/prong/basket components, is reusable.
- **Validation results** (`ValidationResult` shape, severities) — the
  mechanism is category-agnostic; the sixteen current rules are
  ring-specific.
- **Generated artifacts** (STEP, STL, preview mesh, JSON, specification)
  — the export pipeline's shape does not depend on the category.
- **Technical specification** — the Markdown document structure
  generalizes; its content sections are currently ring-specific.

## What this document does not do

It does not define fields, defaults, or geometry for any category other
than Ring — that would violate this Sprint's explicit instruction not to
design complete future schemas. See
[`056-domain-extension-strategy.md`](056-domain-extension-strategy.md)
for the process a future category would have to go through.
