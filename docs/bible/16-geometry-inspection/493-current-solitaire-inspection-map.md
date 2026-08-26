---
id: JM-BIBLE-493
title: Current Solitaire Inspection Map
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-106
  - JM-BIBLE-140
  - JM-BIBLE-472
  - JM-BIBLE-471
normative: true
implementation_status: current
professional_validation: not_required
---

# Current Solitaire Inspection Map

## Starting point: the Sprint 4/5 finding this table updates

`docs/bible/06-forge/106-generated-geometry-inspection-rules.md` and `docs/bible/07-atlas/140-geometry-inspection-framework.md` (Sprint 4/5) recorded, as their single most important finding: **before this Sprint, only one real runtime geometric check existed anywhere in the codebase** — `FORGE-GEOM-001`, `_fuse_metal()`'s `if not fused.Solids(): raise ValueError(...)`, caught internally and triggering the documented compound fallback. Every other geometric property those Sprints described as "current" was proven only at development/CI time against a fixed set of test definitions, never re-verified for a real user's specific input.

This document is the per-relationship map both of those documents point to for the full breakdown. It is grounded in the same real generation this Sprint's investigation used: the default 6-prong solitaire (`band` 250.99 mm³/1 solid, `stone_reference` 58.22 mm³/1 solid, `prongs` 29.65 mm³/6 solids, `basket_support` 83.16 mm³/1 solid), confirmed fully connected in both the production-only and full-assembly connectivity graphs, and a separately-verified 4-prong variant (also fully connected, requested/generated prong count both matching at 4).

## Per-component coverage

| Component | What is generated | What is inspected at runtime (this Sprint) | What is only tested (not runtime) | What remains unknown |
|---|---|---|---|---|
| **Band** | A single solid of revolution around the global Y axis (`band.py`), flat or comfort-fit cross-section, with an optional outer-rim fillet subject to `ATLAS-FALLBACK-001` | Existence, solid count, volume, bounding box, kernel shape validity (`isValid()`), full topology counts (solids/shells/faces/edges/vertices), and the real `filletApplied` fallback flag surfaced via `ComponentInspectionResult.fallbackUsed`/`metadata` | Nothing — every property listed to the left is now genuinely runtime, not merely dev-time-tested | Detailed topology-defect classification beyond binary valid/invalid (e.g. which specific edge or face is defective when `isValid()` returns `False`) |
| **StoneReference** | A simplified lofted crown/girdle/pavilion solid (`stone.py`), a deliberate non-gemological approximation, always kept separate from metal | Existence, solid count (1), volume (58.22 mm³), bounding box, shape validity, topology counts, and structural (identity-based, not geometric-coincidence-based) stone-metal separation via `StoneMetalSeparationResult` | Nothing at the component level | Same topology-defect-classification gap as every component; additionally, no gemological or optical-proportion inspection exists or is planned inside this subsystem (out of scope by design — see [`474-stone-metal-separation-inspection.md`](474-stone-metal-separation-inspection.md)) |
| **BasketSupport** | A hollow cylindrical wall (`basket.py`, outer cylinder minus inner cylinder), radially sized to fully embed the prong footprint per `EMBED_MM` | Existence, solid count, volume (83.16 mm³), bounding box, shape validity, topology counts | Nothing | Same topology-defect-classification gap |
| **Prongs** | 4 or 6 separate cylindrical solids (`prongs.py`), positioned evenly around the stone girdle, embedded slightly into band/basket | Existence, solid count (6 for the default definition, 4 for the verified variant), volume (29.65 mm³ for 6-prong), bounding box, shape validity, topology counts, and requested-vs-generated prong count match (`ProngCountResult`, both requested and generated equal 6, `matches: True`; separately verified for the 4-prong variant) | Nothing — the aggregate count above is genuinely runtime | Individual prong identity (which solid is "prong 3") is neither runtime nor separately tested — it simply does not exist as a concept anywhere in the pipeline yet, even though the ordered `_prong_positions()` list makes it structurally easy to add; also, per-prong contact area/grip-depth quality (see [`494-current-runtime-inspection-gap-analysis.md`](494-current-runtime-inspection-gap-analysis.md)) |

## Per-relationship coverage

| Relationship | What is generated | What is inspected at runtime (this Sprint) | What is only tested (not runtime) | What remains unknown |
|---|---|---|---|---|
| **Band ↔ Basket** | Basket built from `band_top_z(definition) - EMBED_MM`, i.e. deliberately overlapping the band's top by `EMBED_MM` (0.4 mm) so the two solids genuinely share volume rather than merely touch | Real `Shape.distance()` measurement (feeding `productionConnectivity`, which reports this pair inside the single connected group `["band", "basket_support", "prongs"]`) and inclusion in the pairwise intersection pass (not skipped by broad-phase elimination, since the two are not distance-separated) | The precise measured intersection volume for this specific pair is documented at the pairwise-intersection-model level, not restated here — see [`471-component-intersection-model.md`](471-component-intersection-model.md)/[`472-component-distance-model.md`](472-component-distance-model.md) for the full number | Whether the overlap depth is appropriate for any specific manufacturing process — a Forge, not Inspection, question, and currently unconsumed regardless (see [`487-forge-fact-contract.md`](487-forge-fact-contract.md)) |
| **Basket ↔ Prongs** | Prongs embedded into band/basket by design so unions "produce genuine solid contact" (`prongs.py`'s own docstring) | Same as Band ↔ Basket: real distance measurement, part of the same connected production group, included in the intersection pass | Same as above — precise intersection volume documented in [`471`](471-component-intersection-model.md)/[`472`](472-component-distance-model.md) | Same Forge-consumption question as above |
| **Prongs ↔ Stone** | The stone's girdle sits above `band_top_z(definition) + basketHeight`; prongs rise past the girdle to grip the stone crown by design | Real distance and intersection measurement: **INTERSECTS**, 2.10 mm³ overlap — measured directly during this Sprint's investigation. Structurally classified as an expected reference relationship (grip), never as evidence of fusion into production metal (`StoneMetalSeparationResult.intersectsProductionComponents` includes `prongs`) | Nothing — this pairwise fact is genuinely new and runtime this Sprint; no prior test asserted it at all | Whether 2.10 mm³ represents a physically plausible grip depth for any specific stone/prong-diameter combination — a professional-validation question, not an Inspection one |
| **Band ↔ Stone** | The stone is positioned entirely above the band by construction, with no deliberate overlap | Real distance measurement: **NO_INTERSECTION**, 0.9 mm apart — the one genuinely separated pair among the five inspected pairs. Correctly excluded from the full-assembly connected group only in the sense that it is not the edge that connects them (the full assembly is still fully connected via the basket/prongs path) | Nothing — genuinely new and runtime | Whether 0.9 mm is an intentional design clearance or an emergent side effect of the `basketHeight`/`depth` relationship — not evaluated by Inspection (Forge/domain question) |
| **Basket ↔ Stone** | The stone's pavilion extends down toward/into the basket cavity by the geometry's own proportions | Real distance and intersection measurement: **INTERSECTS**, 3.62 mm³ overlap — measured directly during this Sprint's investigation, structurally classified the same expected-reference-relationship way as Prongs ↔ Stone | Nothing — genuinely new and runtime | Same professional-validation question as Prongs ↔ Stone |
| **Production assembly as a whole** | `band` + `prongs` + `basket_support`, unioned via `_fuse_metal()` into `combined_metal` (1 solid for the current default and 4-prong variants — no fallback observed in either verified run) | `AssemblyInspectionResult.requiredComponentsPresent`, `componentCount`, `productionComponentCount`, `totalProductionVolumeMm3`, `assemblyBoundingBox`, `productionConnectivity` (fully connected, 1 group), `fullAssemblyConnectivity` (also fully connected, 1 group of all 4 components including `stone_reference`), and `booleanOperations` (the `combined_metal` `FUSE` entry, `fallbackUsed: False` for both verified runs) | Nothing at the assembly-summary level for the current solitaire — every summary field is genuinely computed at runtime | Behavior for a hypothetically disconnected or multi-body production assembly — never observed on real geometry this Sprint, only exercised via the deliberately-broken test fixture described below |

## The one deliberately-broken case, and why it matters

A real test fixture (never a real jewelry model) with an emptied `prongs` component was inspected during this Sprint's investigation and correctly produced `status: "FAIL"`, `requiredComponentsPresent: False`, `missingComponentIds: ["prongs"]`, and an `INSPECTION_COMPONENT_MISSING` diagnostic. This proves the pipeline detects and reports — never hides — a broken-geometry case, satisfying INSPECT-GOV-014 (inspection must not repair geometry silently) on the one path this Sprint could exercise a genuine failure through.

## The count this table supports

Before this Sprint: **1** real runtime geometric check (`FORGE-GEOM-001`). Counting the rows above that moved from "only tested" to genuinely runtime this Sprint: 4 components × 6 properties each (existence, solid count, volume, bounding box, shape validity, topology) = 24 component-level facts, plus 5 pairwise distance/intersection relationships, plus production connectivity, full-assembly connectivity, prong-count matching, stone-metal separation, and the `combined_metal` boolean-operation fact — **well over 30 individual geometric properties are now genuinely runtime**, none of which existed as a real-time API-observable fact before this Sprint. Every "what is only tested (not runtime)" cell in both tables above reads "Nothing" — for the current solitaire, this Sprint closed the runtime/test-only gap completely for every property this table catalogues. What remains is not a test-vs-runtime gap at all, but a genuine absence: individual prong identity and topology-defect classification beyond binary valid/invalid simply do not exist yet, in tests or at runtime.
