---
id: JM-BIBLE-042
title: Ring Taxonomy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-041
related_documents:
  - JM-BIBLE-044
  - JM-BIBLE-047
implementation_status: partial
professional_validation: preliminary
---

# Ring Taxonomy

## Four separate axes, not one

A ring's appearance is the product of at least four **separate** axes
that are often conflated in casual jewelry language. This document
insists on keeping them apart:

| Axis | Question it answers | Current example |
|---|---|---|
| **Structural style** | What is the overall ring construction (single band, split, multiple stones in a row, etc.)? | Solitaire (single centered stone) |
| **Setting style** | How is the stone physically held? | Prong setting |
| **Band style** | What is the shank's cross-section/shape? | Flat or comfort-fit profile |
| **Decorative treatment** | What surface/stone decoration is applied (independent of structure)? | None implemented |

**Explicit warning:** "pavé" is a **setting/decorative treatment**, not a
structural ring category — a solitaire, a halo, or an eternity ring could
each, independently, have pavé-set accent stones. Treating "pavé" as if
it named a complete ring style would conflate the setting axis with the
structural axis. The same caution applies to any term that names a
technique rather than an overall structure.

## CURRENT

### Solitaire

- **Definition:** a ring with one center stone, held by a single setting,
  on a plain or comfort-fit band — no side stones, no halo, no secondary
  decorative stone arrangement.
- **Distinguishing components:** `CenterStoneReference`, `ProngSetting`,
  `BasketSupport` (see [`044-solitaire-domain-model.md`](044-solitaire-domain-model.md)).
- **Shared components:** `Band`, `MaterialMetadata`, `ManufacturingContext`.
- **Likely parameters:** ring size/inner diameter, band width/thickness/
  profile, stone diameter/depth, prong count/diameter/height, basket
  height (all IMPLEMENTED — see
  [`appendices/jewelry-domain-parameter-catalog.md`](../appendices/jewelry-domain-parameter-catalog.md)).
  This document does not restate the parameters implemented in code — the
  parameter catalog is the source of that detail.
- **Implementation status:** **CURRENT.**
- **Dependency on future domain research:** none for the current scope;
  any refinement of prong/basket realism would need professional review
  (see [`048-prong-domain.md`](048-prong-domain.md),
  [`049-basket-and-support-domain.md`](049-basket-and-support-domain.md)).

## PLANNED candidates

None of the styles below are implemented. Each entry states only what can
be said without inventing professional specification detail.

| Style | Concise definition | Distinguishing components (conceptual) | Shared components | Research dependency | Status |
|---|---|---|---|---|---|
| **Wedding band** | A plain or lightly decorated band, typically without a center stone, often worn alongside another ring. | Possibly none beyond `Band` itself | `Band`, `MaterialMetadata`, `ManufacturingContext` | Whether it needs its own style value or is a solitaire with no stone/setting — UNKNOWN, see [`057-open-domain-questions.md`](057-open-domain-questions.md) | PLANNED |
| **Signet / chevalier** | A ring with a flat or engraved face (often a seal or family crest), typically wider at the top. | A distinct "head" or face component, differing structurally from a stone setting | `Band`, `MaterialMetadata`, `ManufacturingContext` | Engraving representation is entirely undefined | PLANNED |
| **Halo** | A center stone surrounded by a ring of smaller accent stones. | A `Halo`/accent-stone-ring component, a relationship to `CenterStoneReference` | `Band`, `ProngSetting` (for the center stone), `MaterialMetadata` | Multi-stone arrangement is not modeled at all today (see [`046-stone-domain.md`](046-stone-domain.md)) | PLANNED |
| **Hidden halo** | A halo positioned below/behind the center stone, not visible from the top view. | Same as Halo, plus a visibility/positioning distinction | Same as Halo | Same as Halo, plus viewing-angle semantics | PLANNED |
| **Trilogy** | Three stones in a row, typically a center stone flanked by two side stones. | Multiple `CenterStoneReference`-like components with defined roles (center/side) | `Band`, setting per stone, `MaterialMetadata` | Multi-stone arrangement (see above) | PLANNED |
| **Toi et Moi** | Two stones, often of different character, set side by side symmetrically. | Two stone components with a symmetric relationship, no single "center" | `Band`, setting per stone, `MaterialMetadata` | Multi-stone arrangement; symmetric-pair semantics | PLANNED |
| **Eternity** | Stones set continuously around the entire band. | A repeating stone-and-setting pattern around the full band circumference | `Band`, `MaterialMetadata` | Requires a fundamentally different band/stone relationship (stones embedded in the band itself, not above it) | PLANNED |
| **Half-eternity** | Stones set around roughly half the band's circumference (the top-facing half). | Same as Eternity, bounded by an angular range | Same as Eternity | Same as Eternity, plus defining the angular boundary | PLANNED |
| **Cluster** | Multiple smaller stones grouped to resemble one larger area of stones. | A stone-group component with an internal arrangement | `Band`, setting per stone, `MaterialMetadata` | Multi-stone arrangement; grouping geometry | PLANNED |
| **Bypass** | A band whose ends do not meet at the top, instead passing by each other, often each ending in its own stone/detail. | An open-band-top structural variant | `Band`, `MaterialMetadata` | Fundamentally different band topology than the current closed revolve (see [`045-band-domain.md`](045-band-domain.md)) | PLANNED |
| **Split shank** | A band that separates into two (or more) strands as it approaches the setting. | A shank-branching structural variant | `Band`, `ProngSetting`, `MaterialMetadata` | Same band-topology dependency as Bypass | PLANNED |
| **Cathedral** | Shoulders that rise from the band toward the setting, elevating the stone. | A shoulder/rise structural component between band and setting | `Band`, `ProngSetting`, `BasketSupport`, `MaterialMetadata` | Shoulder geometry is entirely unmodeled (see [`043-ring-anatomy.md`](043-ring-anatomy.md)) | PLANNED |

None of these PLANNED entries have a schema, a default value, or a
geometry builder. Their inclusion here exists solely so the current model
is evaluated against them for extensibility — see
[`056-domain-extension-strategy.md`](056-domain-extension-strategy.md).

## Terminology ambiguity across jewelry practices and languages

- **"Chevalier"** (used in several European jewelry traditions,
  particularly Italian and French) and **"signet ring"** (more common in
  English) often refer to the same broad concept but are not guaranteed
  to be perfectly synonymous across every regional tradition — this
  Bible treats them as one PLANNED candidate provisionally, flagged as an
  open question.
- **"Eternity"** vs. **"half-eternity"** boundaries (what fraction of the
  band counts as "half") are not standardized here and would need
  professional input.
- **"Pavé"**, as already noted, names a setting/decorative technique, not
  a structural style — using it as if it were a ring category (as
  informal marketing language sometimes does) would be a terminology
  error this Bible deliberately avoids.

See [`057-open-domain-questions.md`](057-open-domain-questions.md) for
these logged as open questions rather than resolved here.
