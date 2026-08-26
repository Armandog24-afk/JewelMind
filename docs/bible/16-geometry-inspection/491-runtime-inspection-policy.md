---
id: JM-BIBLE-491
title: Runtime Inspection Policy
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
  - JM-BIBLE-484
  - JM-BIBLE-465
normative: true
implementation_status: current
professional_validation: not_required
---

# Runtime Inspection Policy

## The classification vocabulary, and the honest current reality

The Sprint 14 brief asked for inspections to be classified `ALWAYS`, `ON_GENERATION`, `ON_EXPORT`, `ON_REVIEW`, or `EXPENSIVE_OPTIONAL`. That vocabulary is documented here because it is a useful conceptual model for future policy decisions — but the real current implementation has exactly **one tier**: every inspection this Sprint implements runs unconditionally, inline, inside `ModelService.generate()`, i.e. `ALWAYS` and `ON_GENERATION` collapse into the same real thing today. There is no `ON_EXPORT`-only or `ON_REVIEW`-only inspection tier implemented anywhere in the codebase — `export_step_file()`/`export_stl_file()` do not run any additional inspection (see [`489-foundry-inspection-integration.md`](489-foundry-inspection-integration.md)), and the Professional Review Package (`review_package.py`) does not trigger a fresh inspection either; it reuses `record.inspection_report`, the same report computed once at generation time.

| Classification | Real current inspections in this tier | Notes |
|---|---|---|
| `ALWAYS` (= `ON_GENERATION` today) | Component existence/solid-count/volume/bounding-box/shape-validity/topology (`components.py`), pairwise distance (`connectivity.py::pairwise_distances`), production and full-assembly connectivity graphs, pairwise intersection (`assembly.py::inspect_assembly`, with broad-phase elimination — see below), stone-metal separation, prong count, boolean-operation/fallback detection | Everything this Sprint implements lives here. Runs once per `ModelService.generate()` call, never repeated for the same cached `ModelRecord`. |
| `ON_EXPORT` | None | Not implemented. STEP/STL export does not run or re-run any inspection. |
| `ON_REVIEW` | None | Not implemented. The Professional Review Package embeds the already-computed `inspection_report`; it does not trigger a second, review-specific inspection pass. |
| `EXPENSIVE_OPTIONAL` | None | No inspection in this codebase is currently gated as optional or user-triggered; everything that exists runs by default. |

Stating this plainly: the classification scheme is conceptually complete in this document, but the code has not yet grown into needing the other four tiers. That is a real, current scope limit, not a defect — see [`494-current-runtime-inspection-gap-analysis.md`](494-current-runtime-inspection-gap-analysis.md) for when a second tier might become necessary (larger assemblies, pavé stone counts).

## Pairwise intersection: the one inspection expensive enough to discuss

Every other current inspection (component-level checks, topology counts, `Shape.distance()`) is measured as cheap — single-digit-to-tens of milliseconds per component or pair on the current 4-component solitaire (see `distance.py`'s and `shape.py`'s own docstrings, cross-referencing [`484-inspection-performance-model.md`](484-inspection-performance-model.md) for the full measured numbers). Pairwise intersection (`intersection.py::inspect_intersection`, wrapping `cadquery.Shape.intersect()` / OCP's `BRepAlgoAPI_Common`) is different: tens to roughly a thousand milliseconds per pair depending on solid complexity, per `intersection.py`'s own docstring.

**It is still run by default at the current small scale.** `INSPECT-GOV-018` requires this to be a measured decision, not a guess, and it is: [`484-inspection-performance-model.md`](484-inspection-performance-model.md) documents real timing data showing the current total added cost (a few hundred milliseconds to roughly one second per generation) acceptable for a prototype-scale assembly. This document does not re-derive those numbers; it states the policy conclusion they support — run intersection by default today, revisit if the component count grows materially (see the pavé-stone scaling question in [`495-open-inspection-questions.md`](495-open-inspection-questions.md)).

## Broad-phase elimination is real and already reduces the cost

`assembly.py::inspect_assembly()` computes all pairwise distances first (cheap), then only calls `intersection.inspect_intersection()` for a pair when `should_skip_intersection(min_distance_mm)` (`intersection.py`) is `False` — i.e. when the prior real distance measurement did not already prove the pair separated beyond `CONTACT_TOLERANCE_MM`. For the default solitaire's 4 required components (`band`, `stone_reference`, `prongs`, `basket_support`), `_ALL_PAIRS` in `assembly.py` is the full 6-pair combination. Of those 6 pairs, exactly one — `band`↔`stone_reference`, measured at 0.9 mm apart — is proven separated by the distance pass and its intersection call is skipped (`known_separated=True`, returning `NO_INTERSECTION` without invoking the boolean-common operation at all). The remaining 5 pairs (`band`↔`basket_support`, `band`↔`prongs`, `basket_support`↔`prongs`, `stone_reference`↔`prongs`, `stone_reference`↔`basket_support`) each run the real `Shape.intersect()` call. This is the real, measured "6 to 5" reduction this Sprint's investigation found for the default solitaire — not an estimate, a direct count of `should_skip_intersection()`'s real return values against the real distance results.

This broad-phase step is itself governed by INSPECT-GOV-012 (a pure kernel contact tolerance, `CONTACT_TOLERANCE_MM = 1e-6`, never an invented jewelry tolerance) and never used as the connectivity signal itself (`connectivity.py`'s own docstring is explicit that bounding-box/distance-based elimination "is never itself the connectivity signal").

## What "measured, not guessed" means here

Per `docs/bible/16-geometry-inspection/README.md`'s "What was investigated, not invented" section, every kernel operation cited above (`distance()`, `intersect()`, `isValid()`) was run against real generated geometry before being wired into production code. This document's timing characterization is consistent with that same discipline: it cites [`484-inspection-performance-model.md`](484-inspection-performance-model.md) as the source of the actual measured numbers rather than restating them independently, so the two documents cannot silently drift apart.
