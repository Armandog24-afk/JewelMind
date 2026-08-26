---
id: JM-BIBLE-A83
title: "Appendix: Professional Review Checklist Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-413
  - JM-BIBLE-427
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Professional Review Checklist Catalog

A table-only re-statement of [`427-review-checklist-model.md`](../15-professional-validation/427-review-checklist-model.md)'s 4 role-specific checklist categories. Every item below is an **open-ended observation prompt**, never a scoring rubric or a pass/fail gate — no numeric threshold may ever be embedded in a checklist item (a minimum wall thickness, a maximum overhang, a tolerance in mm). Every actual numeric limit JewelMind enforces lives in `backend/jewelmind/validation/engine.py` with a Forge rule ID. Working through a checklist item does not, by itself, move any status toward `VALIDATED` — an engaged item that produces a finding becomes one `ReviewObservation`.

Only 4 of the 8 `ReviewerRole` values have a defined checklist; `RESIN_PRINTING_SPECIALIST`, `JEWELRY_MANUFACTURING_ENGINEER`, `GEMOLOGIST`, and `CAD_INTEROPERABILITY_SPECIALIST` do not — a real, tracked gap (see [`451-validation-gap-analysis.md`](../15-professional-validation/451-validation-gap-analysis.md)).

## CAD Designer checklist (`JEWELRY_CAD_DESIGNER`)

| Item | Prompt |
|---|---|
| File opens | Does the exported STEP/STL actually open in the reviewer's CAD application without error? |
| Scale correct | Does the imported geometry read at the expected millimeter scale? |
| Solids recognizable | Do band, prongs, and basket present as distinct, sensible solids rather than a degenerate or fused mass? |
| Component organization | Are components named/grouped usably, or does everything arrive as one undifferentiated blob? |
| Topology | Any non-manifold geometry, self-intersections, or open shells worth flagging before trusting the model further? |
| Editability | Could a designer realistically start editing this model in their own tool, or would they have to rebuild it from scratch? |
| Model proportions | Do the proportions look like a plausible piece of jewelry, independent of whether every Forge rule passed? |
| Unusual construction | Anything constructed in a way a professional CAD designer would not normally build it, even if geometrically valid? |

## Stone Setter checklist (`STONE_SETTER`)

| Item | Prompt |
|---|---|
| Stone position | Is the stone reference plausibly seated relative to the band and basket? |
| Prong position | Are prongs positioned where a setter could actually reach and work them? |
| Seat/bearing | Does the geometry suggest an adequate bearing surface for the stone, in the setter's practical judgment (not a Forge-enforced number)? |
| Access | Can a setter's tools physically reach the prongs and stone given the surrounding geometry? |
| Number/placement of prongs | Does the prong count and arrangement look workable for this stone size and shape? |
| Setting feasibility | Could this actually be set by hand using normal bench techniques? |
| Finishing implications | Would setting this piece leave finishing work (burring, polishing around prongs) that is unusually difficult given the geometry? |

## Goldsmith / Bench Jeweler checklist (`GOLDSMITH_BENCH_JEWELER`)

| Item | Prompt |
|---|---|
| Construction plausibility | Could this piece plausibly be constructed on a bench using normal goldsmithing methods? |
| Assembly | Do the components (band, basket, prongs) relate to each other the way a goldsmith would actually assemble them? |
| Finishing | Are there features that would be difficult or impossible to polish/finish by hand given their geometry? |
| Wear-related concerns | Does anything about the geometry suggest a likely wear or durability problem, independent of any Forge rule that may already flag it? |
| Component transitions | Are the transitions between band, basket, and prongs the kind a goldsmith would consider clean, or an artifact of how the CAD model was generated? |

## Casting Specialist checklist (`CASTING_SPECIALIST`)

| Item | Prompt |
|---|---|
| Casting concerns | Anything about the geometry a casting specialist would flag before sending this to a mold, independent of whether Forge currently flags it? |
| Thin/heavy regions | Regions that look unusually thin (porosity/incomplete-fill risk) or unusually heavy (shrinkage/investment-cracking risk) — described qualitatively, never as a new numeric threshold. |
| Process sensitivity | Does the geometry look sensitive to which casting process is used (`lost_wax_casting` vs. `direct_resin_printing`), such that a scope-specific `ValidationScope.manufacturingMethod` matters? |
| Cleanup | Would this geometry require unusual amounts of post-cast cleanup (sprue removal, porosity repair)? |
| Likely production issues | Any other production-stage issue a specialist would flag from experience, captured qualitatively rather than as a pass/fail verdict. |

## Cross-references

- [`427-review-checklist-model.md`](../15-professional-validation/427-review-checklist-model.md) — narrative rationale and what a checklist is not.
- [`docs/professional-review/`](../../professional-review/README.md) — the actual fillable forms these checklists are built from (not part of the Bible's numbered docs).
- [`428-review-observation-model.md`](../15-professional-validation/428-review-observation-model.md) — how an engaged checklist item becomes a `ReviewObservation`.
