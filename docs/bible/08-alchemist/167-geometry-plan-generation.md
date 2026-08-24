---
id: JM-BIBLE-167
title: Geometry Plan Generation
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-166
related_documents:
  - JM-BIBLE-149
implementation_status: planned
professional_validation: not_required
normative: true
---

# Geometry Plan Generation

How current JDL fields would map into `GeometryPlan` component plans, if one were generated — grounded in exactly the same real code trace as [`07-atlas/149-current-solitaire-geometry-mapping.md`](../07-atlas/149-current-solitaire-geometry-mapping.md).

## Worked mappings

| JDL field | Plan contribution |
|---|---|
| `ring.innerDiameter` | `band` component plan's direct parameter; feeds `derivedParameters.innerRadiusMm`/`outerRadiusMm` |
| `band.profile` | `band` component plan's `buildOperation` selection (`revolve_flat_profile` vs. `revolve_comfort_fit_profile`) |
| `stone.diameter` | `stone_reference` component plan's direct parameter; **also** feeds `prongs` and `basket_support`'s derived `prong_center_radius` — a cross-component derivation, exactly as documented in Sprint 5 |
| `setting.prongCount` | `prongs` component plan's cardinality; feeds the angular-distribution derivation (`_prong_positions()`) |

## Where current derived calculations conceptually belong

| Derived calculation | Current location | Conceptual home |
|---|---|---|
| `inner_radius`, `outer_radius`, `band_top_z` | `geometry/constants.py`, called from inside each builder | **Alchemist planning** — these are pure functions of the definition with no CAD-kernel dependency; they could be computed once, upfront, and handed to Atlas as `derivedParameters` |
| `prong_center_radius` | Same | **Alchemist planning**, same reasoning |
| Prong angular positions (`_prong_positions()`) | `prongs.py`, pure Python math | **Alchemist planning** — no CadQuery call is involved in computing the (x, y) pairs themselves, only in extruding at them |
| Fillet radius calculation (`min(0.25, width*0.15, thickness*0.15)`) | `band.py` | **Alchemist planning** — pure arithmetic, no kernel dependency |
| Stone crown/pavilion/table split | `stone.py` | **Alchemist planning** — pure arithmetic |
| The actual `.revolve()`, `.loft()`, `.extrude()`, `.cut()`, `.fuse()`, `.fillet()` calls | All four builders + `solitaire.py` | **Atlas construction** — genuine CAD-kernel operations |
| `JM-PRONG-001`'s `{4, 6}` set-membership check | `validation/engine.py` | **Forge** — correctly already there, not in geometry code |

**Every derived value currently computed inside a builder is pure Python arithmetic with zero CadQuery/OCCT dependency**, confirmed by inspection during this Sprint — none of them touches `cq.Workplane` or any kernel call. This means the conceptual "Alchemist planning vs. Atlas construction" split is real and clean *by function boundary* already: `geometry/constants.py` (`inner_radius`, `outer_radius`, `band_top_z`, `prong_center_radius`) and `_prong_positions()` are already pure functions, callable independently of any CAD kernel. What is missing is a *temporal* separation — a distinct planning stage that calls all of these upfront, before any builder runs, and packages the results into a returned `GeometryPlan` value — rather than each builder independently re-calling the same shared functions inline at construction time.

## No refactor performed

Per this Sprint's explicit instruction, no code was extracted or moved in this Sprint. The pure-function boundary already exists (`geometry/constants.py`); introducing an upfront planning stage that calls it once and threads a `GeometryPlan` value through construction would be a real, mechanical, low-risk future change — but it still touches all four builder call sites, so it is deferred to whichever future sprint actually needs `GeometryPlan` for one of the reasons listed in [`166-geometry-plan-model.md`](166-geometry-plan-model.md), rather than performed speculatively here.
