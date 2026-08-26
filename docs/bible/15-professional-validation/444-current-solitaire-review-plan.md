---
id: JM-BIBLE-444
title: Current Solitaire Review Plan
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-420
  - JM-BIBLE-427
  - JM-BIBLE-445
  - JM-BIBLE-451
implementation_status: current
professional_validation: not_required
normative: false
---

# Current Solitaire Review Plan

This document is the practical review agenda for the one complete model
JewelMind can currently produce: the six-or-four-prong round-solitaire
assembly built by `backend/jewelmind/geometry/assemblies/solitaire.py`. It
gives a real jewelry professional a concrete, ordered sequence to work
through against a generated review package (see
[`446-review-package-generation.md`](446-review-package-generation.md)),
grounded in [`420-geometry-validation-process.md`](420-geometry-validation-process.md)'s
general geometry review dimensions and
[`427-review-checklist-model.md`](427-review-checklist-model.md)'s
role-specific checklists. It does not itself constitute a review, and
working through it does not produce a `ValidationRecord` — only a real
reviewer's `ReviewObservation`s and `ValidationDecision`s do that
(PROVAL-GOV-001).

## The single most important instruction for a reviewer

**Identify what is missing, not only what is present.** JewelMind's
solitaire assembly is a genuinely simplified prototype: four named
components (`band`, `stone_reference`, `prongs`, `basket_support`),
exactly as read from `backend/jewelmind/geometry/components/*.py` and
`geometry/assemblies/solitaire.py`. A reviewer who only rates the quality
of what exists will systematically under-report the gap between this
prototype and a real production-ready CAD file, because entire categories
of geometry a professional would expect (a cut seat/bearing, a tapered or
decorative basket, a gallery, undercuts, a finished prong tip profile) are
not merely low-quality here — they do not exist in the code at all. Every
item below explicitly asks "what is missing," not only "is what's here
good."

## Priority order and what actually exists to review

### 1. Band construction

`backend/jewelmind/geometry/components/band.py::build_ring_band()`
produces a solid of revolution around the global Y axis, in one of two
profiles: `flat` (rectangular cross-section, with an optional outer-rim
fillet capped at `_FILLET_FRACTION = 0.15` / `_FILLET_MAX_MM = 0.25`) or
`comfort_fit` (an outward-bulging inner arc, flared `_COMFORT_FLARE_MM =
0.3` mm at the band's edges — a fixed constant, not user-configurable).
The fillet operation falls back to unfilleted geometry with a warning if
OpenCascade's fillet fails. **Review this first** because every other
component is positioned relative to it (`band_top_z()`,
`geometry/constants.py`).

### 2. Basket-to-band relationship

The basket (`basket.py::build_basket_support()`) starts at `base_z =
band_top_z(definition) - EMBED_MM` — a fixed embedding constant so the
basket genuinely overlaps the band in 3D rather than merely touching its
top surface. Review whether this embedding depth and the resulting
transition read as a real, buildable joint, or as a CAD-generation
artifact.

### 3. Prong arrangement

`prongs.py::build_prongs()` distributes exactly 4 or 6 plain cylindrical
solids evenly around the stone girdle (`_prong_positions()`, even angular
spacing, no clustering or asymmetric placement logic exists). Prong
diameter and count come directly from `definition.setting.prongDiameter`/
`prongCount` with no shape tapering, faceting, or tip-shaping of any
kind — each prong is a plain extruded cylinder from base to tip.

### 4. Basket support

`basket.py` implements the basket as **a single hollow cylindrical
wall** (outer radius minus inner radius) — explicitly documented in its
own module docstring as "a robust first implementation ... rather than a
highly decorative one." There is no gallery, no cutout, no
scroll/openwork detail, and no tapering wall thickness.

### 5. Stone reference position

`stone.py::build_stone_reference()` places a lofted crown/girdle/pavilion
solid at `girdle_z = band_top_z(definition) + definition.setting.basketHeight`,
using fixed, non-gemological proportions (`_CROWN_FRACTION = 0.35`,
`_PAVILION_FRACTION = 0.65`, `_TABLE_TO_GIRDLE_RATIO = 0.56`) — the
module docstring states plainly this is "not a gemological reproduction
of a real round brilliant cut." The stone is never fused into the metal
(LAW-006) and must never appear in an export unless
`includeStoneReference: true` is explicitly requested.

### 6. Component connectivity

`solitaire.py::_fuse_metal()` attempts `band.fuse(basket).fuse(prongs)`
into one solid; on any OpenCascade failure it falls back to an unfused
multi-solid `cq.Compound` and appends a warning
(`docs/bible/appendices/atlas-fallback-register.md`). A reviewer should
open the actual STEP/STL and check which case occurred for the reviewed
case — a fallback compound is a real, disclosed geometric fact, not a
hidden defect, but it changes what "one solid model" means for import.

### 7. Stone-setting realism

There is **no seat or bearing cut** in the current metal geometry at
all — no code path in `prongs.py` or `basket.py` cuts a girdle rest,
bearing groove, or seat into any solid. A stone setter reviewing this
should evaluate the assembly on the explicit understanding that, as
currently built, no professional setter could physically set a real
stone into this exact geometry without first cutting a seat by hand —
this is a missing-geometry finding, not merely a quality finding about
existing prong shape.

### 8. CAD cleanliness

Evaluate the actual STEP/STL for non-manifold geometry, self-intersections,
degenerate faces, or the fallback-compound condition from item 6. Also
check component naming/grouping once imported — `component-manifest.json`
in the review package lists the four real component names
(`band`, `stone_reference`, `prongs`, `basket_support`) with their
`geometryRole`, so a reviewer never has to guess identity from render
order (ATLAS-GOV-006, VISION-GOV-011).

### 9. STEP workflow

Confirm the STEP file actually opens in the reviewer's own CAD
application at the expected millimeter scale (CLAUDE.md's "use
millimeters everywhere" rule) and that the imported solids are usable,
editable primitives rather than a monolithic, unstructured blob — see
[`424-cad-workflow-validation-process.md`](424-cad-workflow-validation-process.md).
No external CAD import of this exact package has been professionally
verified as of this writing (also stated in the review package's own
`manifest.json::knownLimitations`).

### 10. Manufacturing concerns

`material.metal` and `manufacturing.method` currently affect metadata and
validation-context only — **no manufacturing-specific geometry
adjustment happens for either lost-wax casting or resin printing** (see
`docs/bible/04-jewelry-domain/052-parametric-dependency-model.md`). A
casting or resin-printing specialist reviewing this model should evaluate
it as one undifferentiated geometry regardless of which
`manufacturingMethod` was selected in the design, and should explicitly
note whether that lack of differentiation itself is a blocking concern
for their process.

### 11. Missing essential professional geometry

This is the summary item, deliberately last, and deliberately the one a
reviewer should spend real time on rather than treat as a formality.
Beyond the seat/bearing absence already named in item 7, candidates a
reviewer should actively look for and confirm present or absent (never
assumed from this list alone) include: a gallery or decorative
underbasket structure, prong tapering/faceting/tip finishing, an
engraved or textured inner band surface, a sizing/adjustment allowance,
undercuts for stone security beyond raw prong contact, and any bridge or
reinforcement structure a real solitaire of this stone size would
typically need. Any of these, if the reviewer confirms it is genuinely
absent and would be needed for a production-ready design, should be
recorded as its own `ReviewObservation` (category e.g.
`"missing_geometry"`, per
[`428-review-observation-model.md`](428-review-observation-model.md)) —
never folded silently into a general "needs polish" note.

## What this plan is not

This plan does not define a pass/fail threshold, a numeric score, or a
minimum number of findings required for a valid review — consistent with
[`427-review-checklist-model.md`](427-review-checklist-model.md)'s "no
invented numeric thresholds" rule. It is an agenda, not a rubric.

## Cross-references

- [`420-geometry-validation-process.md`](420-geometry-validation-process.md) — the general geometry review dimensions this plan specializes.
- [`427-review-checklist-model.md`](427-review-checklist-model.md) — role-specific checklists this plan's items map onto.
- [`07-atlas/149-current-solitaire-geometry-mapping.md`](../07-atlas/149-current-solitaire-geometry-mapping.md) — the authoritative field-to-geometry mapping this plan observes, never re-derives.
- `docs/known-limitations.md` — the same known-limitations list surfaced in every generated review package's `README.md`.
