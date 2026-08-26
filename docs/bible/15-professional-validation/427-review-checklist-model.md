---
id: JM-BIBLE-427
title: Review Checklist Model
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
  - JM-BIBLE-413
  - JM-BIBLE-425
  - JM-BIBLE-428
implementation_status: current
professional_validation: not_required
normative: false
---

# Review Checklist Model

## What a checklist is, and is not, in this framework

A review checklist is a set of **open-ended observation prompts** grouped by
what a specific reviewer role would naturally look at first. It is not a
scoring rubric, not a pass/fail gate, and not a place where a numeric
threshold gets defined. Every actual numeric limit JewelMind enforces lives
in `backend/jewelmind/validation/engine.py` with a Forge rule ID (see
[`06-forge/091-rule-system-overview.md`](../06-forge/091-rule-system-overview.md));
a checklist category exists only to prompt a reviewer toward producing a
`ReviewObservation` (see
[`428-review-observation-model.md`](428-review-observation-model.md)), never
to encode a threshold of its own. This is a hard rule for this document: **no
checklist category below may ever be amended to embed an invented numeric
limit** (a minimum wall thickness, a maximum overhang, a tolerance in
millimeters). If a reviewer's observation implies a candidate numeric rule,
that observation still routes through the real rule-proposal workflow in
[`435-validation-to-forge-workflow.md`](435-validation-to-forge-workflow.md)
— it never becomes a checklist item.

The actual fillable forms a real reviewer would use are a separate,
sibling deliverable: [`docs/professional-review/`](../../professional-review/README.md)
holds role-specific review-form templates (for example
`docs/professional-review/stone-setting-review-form.md`). This document
describes the **checklist categories** those forms are built from; it does
not duplicate the forms themselves, and the forms are not part of the
Bible's numbered documents (per the README's "Professional review templates"
section).

## Checklist categories exist per `ReviewerRole`

`ReviewerRole` (`backend/jewelmind/professional_validation/schemas.py`) has
8 real values. This document defines checklist categories for the 4 roles
the original Sprint 13 brief specified in detail —
`JEWELRY_CAD_DESIGNER`, `STONE_SETTER`, `GOLDSMITH_BENCH_JEWELER`, and
`CASTING_SPECIALIST`. The other 4 roles (`RESIN_PRINTING_SPECIALIST`,
`JEWELRY_MANUFACTURING_ENGINEER`, `GEMOLOGIST`,
`CAD_INTEROPERABILITY_SPECIALIST`) have no role-specific checklist defined
yet — this is a real, honest gap, not an oversight to paper over; see
[`451-validation-gap-analysis.md`](451-validation-gap-analysis.md) for
where it is tracked.

### CAD Designer checklist (`JEWELRY_CAD_DESIGNER`)

- **File opens** — does the exported STEP/STL actually open in the
  reviewer's CAD application without error, per
  [`424-cad-workflow-validation-process.md`](424-cad-workflow-validation-process.md)?
- **Scale correct** — does the imported geometry read at the expected
  millimeter scale (CLAUDE.md's "use millimeters everywhere" rule, restated
  for import-side verification)?
- **Solids recognizable** — do band, prongs, and basket present as
  distinct, sensible solids rather than a degenerate or fused mass?
- **Component organization** — are components named/grouped in a way a CAD
  designer could work with, or does everything arrive as one undifferentiated
  blob?
- **Topology** — any non-manifold geometry, self-intersections, or open
  shells a designer would flag before trusting the model further?
- **Editability** — could a designer realistically start editing this model
  in their own tool, or would they have to rebuild it from scratch?
- **Model proportions** — do the proportions look like a plausible piece of
  jewelry to someone who works with jewelry CAD daily, independent of
  whether every Forge rule passed?
- **Unusual construction** — anything constructed in a way a professional
  CAD designer would not normally build it, even if geometrically valid?

### Stone Setter checklist (`STONE_SETTER`)

- **Stone position** — is the stone reference plausibly seated where a
  setter would expect it, relative to the band and basket?
- **Prong position** — are prongs positioned where a setter could actually
  reach and work them?
- **Seat/bearing** — does the geometry suggest an adequate bearing surface
  for the stone to rest on, from a setter's practical judgment (not a
  Forge-enforced number)?
- **Access** — can a setter's tools physically reach the prongs and stone
  given the surrounding geometry?
- **Number/placement of prongs** — does the prong count and arrangement
  look workable for this stone size and shape, in the setter's professional
  judgment?
- **Setting feasibility** — could this actually be set by hand using normal
  bench techniques, or does something about the geometry make that
  impractical?
- **Finishing implications** — would setting this piece leave finishing
  work (burring, polishing around prongs) that is unusually difficult given
  the geometry?

### Goldsmith / Bench Jeweler checklist (`GOLDSMITH_BENCH_JEWELER`)

- **Construction plausibility** — could this piece plausibly be constructed
  on a bench using normal goldsmithing methods?
- **Assembly** — do the components (band, basket, prongs) relate to each
  other the way a goldsmith would actually assemble them, or does the
  geometry imply an assembly order that doesn't make sense?
- **Finishing** — are there features that would be difficult or impossible
  to polish/finish by hand given their geometry?
- **Wear-related concerns** — does anything about the geometry suggest a
  likely wear or durability problem a goldsmith would recognize from
  experience (independent of any Forge rule that may or may not already
  flag it)?
- **Component transitions** — are the transitions between band, basket,
  and prongs the kind of transition a goldsmith would consider clean, or do
  they look like an artifact of how the CAD model was generated rather than
  how a real piece would be built?

### Casting Specialist checklist (`CASTING_SPECIALIST`)

- **Casting concerns** — anything about the geometry that a casting
  specialist would flag before sending this to a mold, independent of
  whether Forge currently flags it?
- **Thin/heavy regions** — regions that look unusually thin (porosity/
  incomplete-fill risk) or unusually heavy (shrinkage/investment-cracking
  risk) to a specialist's eye — described qualitatively here, never as a
  new numeric threshold invented inside this checklist.
- **Process sensitivity** — does the geometry look sensitive to which
  casting process is used (see `ManufacturingMethod`'s
  `lost_wax_casting`/`direct_resin_printing` distinction,
  [`04-jewelry-domain/README.md`](../04-jewelry-domain/README.md)), such
  that a scope-specific `ValidationScope.manufacturingMethod` matters for
  any resulting `ReviewObservation`?
- **Cleanup** — would this geometry require unusual amounts of post-cast
  cleanup (sprue removal, porosity repair) compared to a typical piece?
- **Likely production issues** — any other production-stage issue a
  specialist would flag from experience, captured as a qualitative
  observation rather than a pass/fail verdict.

## How a checklist category becomes evidence

Working through a checklist category does not, by itself, produce a
`ValidationRecord` or move any status toward `VALIDATED` (PROVAL-GOV-001).
Each checklist item a reviewer actually engages with, if it produces a
finding, becomes one `ReviewObservation` (`target`, `category`, `severity`,
`observation`) — see [`428-review-observation-model.md`](428-review-observation-model.md).
A checklist is the prompt; an observation is the evidence.
