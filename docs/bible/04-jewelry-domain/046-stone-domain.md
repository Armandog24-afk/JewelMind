---
id: JM-BIBLE-046
title: Stone Domain
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-044
related_documents:
  - JM-BIBLE-006
  - JM-BIBLE-ADR-006
implementation_status: current
professional_validation: preliminary
---

# Stone Domain

## Naming — deliberately not what it might sound like

The current concept is **`StoneReference`**, not:

- ~~`CertifiedGemstone`~~ — nothing about it implies any grading,
  certification, or authenticity.
- ~~`ManufacturingStoneSeat`~~ — it has no seat/bearing geometry a real
  stone-setting process would need.
- ~~`GemologicalModel`~~ — it does not reproduce real optical or cut
  properties.

This naming discipline exists specifically to prevent the current
simplified geometry from being read as more authoritative than it is —
see [LAW-006](../00-foundation/004-jewelmind-constitution.md#LAW-006) and
`docs/known-limitations.md`.

## Current concept: round shape only

`domain/schema.py::StoneSpec.shape` is `Literal["round"]` — no other
shape is accepted today.

## Current parameters

| Parameter | Path | Type | Notes |
|---|---|---|---|
| Diameter | `stone.diameter` | float, mm | Girdle diameter — see below. |
| Depth | `stone.depth` | float, mm | Total culet-to-table height. |

## Crown / girdle / pavilion in the current reference

`geometry/components/stone.py` builds a lofted solid:

1. Culet point (a near-zero radius circle, `_CULET_RADIUS_MM = 0.05`) at
   the bottom.
2. Pavilion: a straight loft from the culet up to the girdle radius
   (`stone.diameter / 2`), over a height of `stone.depth *
   _PAVILION_FRACTION` (currently `0.65`).
3. Girdle: the widest circle, at radius `stone.diameter / 2`.
4. Crown: a straight loft from the girdle up to the table radius
   (`girdle_radius * _TABLE_TO_GIRDLE_RATIO`, currently `0.56`), over a
   height of `stone.depth * _CROWN_FRACTION` (currently `0.35`).

**These three constants (`_CROWN_FRACTION`, `_PAVILION_FRACTION`,
`_TABLE_TO_GIRDLE_RATIO`) are PRELIMINARY SOFTWARE RULEs** — reasonable
approximations chosen for a plausible-looking reference silhouette, not
values derived from any gemological cutting standard. The code comment
in `stone.py` itself states this ("Rough round-brilliant proportions...
Not derived from any gemological standard").

## Reference geometry vs. preview role

The stone reference solid exists to:

1. Give the 3D preview a visually distinct (transparent, gemstone-like
   material), correctly-sized placeholder.
2. Give `setting.prongCount`-vs-stone-size validation
   (`JM-PRONG-003`) something concrete to reason about (girdle radius).
3. Position the setting/basket assembly relative to a real, if
   simplified, stone silhouette.

It does **not** exist to represent real optical properties, faceting, or
a manufacturable stone-setting seat.

## Separation from metal

The stone reference is never unioned into `combined_metal`
(band + prongs + basket), and is excluded from STEP/STL export unless
`includeStoneReference: true` is explicitly requested — see
[ADR-006](../03-decisions/ADR-006-stone-reference-separated-from-metal.md).

## Current approximation and limitations

- Only round stones.
- Fixed proportion constants, not user-adjustable, not shape-dependent.
- No facet geometry — the solid is a smooth loft, not a faceted cut.
- No optical/refractive properties (irrelevant for a solid model, noted
  for completeness against any future rendering ambitions).
- No relationship to real carat weight (see below).

## Future stone-shape taxonomy (status only — no defaults invented)

None of the shapes below are implemented. No dimensional default is
assigned to any of them, per
[`040-domain-governance.md`](040-domain-governance.md).

| Shape | General classification | Likely dimensional parameters | Domain questions requiring professional validation | Status |
|---|---|---|---|---|
| Round | Brilliant-style, radially symmetric | Diameter, depth (current) | Whether current crown/pavilion fractions should ever be professionally validated as defaults, or replaced entirely | CURRENT |
| Oval | Elongated brilliant-style | Length, width, depth | Length:width ratio conventions | PLANNED |
| Princess | Square/rectangular brilliant-style | Length, width, depth | Corner treatment, pavilion depth convention | PLANNED |
| Emerald | Step-cut, rectangular | Length, width, depth | Step count, corner (cut-corner) convention | PLANNED |
| Cushion | Rounded-square/rectangular brilliant or mixed-cut | Length, width, depth | Corner rounding radius convention | PLANNED |
| Pear | Asymmetric brilliant-style (teardrop) | Length, width, depth | Point/shoulder proportions | PLANNED |
| Marquise | Elongated pointed-oval brilliant-style | Length, width, depth | Point angle convention | PLANNED |
| Radiant | Cut-corner rectangular brilliant-style | Length, width, depth | Corner cut angle, facet pattern | PLANNED |
| Asscher | Cut-corner square step-cut | Length, width, depth | Step count, corner convention | PLANNED |
| Heart | Bifurcated brilliant-style | Length, width, depth, cleft depth | Cleft/point proportions | PLANNED |

Every non-round shape needs at minimum a length/width pair rather than a
single diameter — this alone means `StoneSpec` cannot simply add a
`shape` enum value without a schema change (see
[`056-domain-extension-strategy.md`](056-domain-extension-strategy.md)).

## Why carat weight must not be inferred from diameter alone

Carat weight is a *mass* measurement, and mass depends on **volume and
density**, both of which depend on factors this reference model does not
capture:

- Different shapes with the same "diameter"-equivalent measurement
  enclose different volumes (a round brilliant and an oval of the same
  longest dimension are not the same volume).
- Depth-to-diameter ratio ("spread") varies stone to stone even within
  round brilliants, so two stones of the same diameter can have
  different volumes if their depths differ — which `stone.depth` in this
  schema already allows, but no carat-weight calculation exists to
  consume it.
- Density varies by gemstone material (diamond vs. sapphire vs. other
  species), which this schema does not model at all — `stone` has no
  material/species field today.

Any future carat-weight estimation feature would need, at minimum, a
material/species field, real proportion data, and professional review
before being presented as anything more than a rough estimate — logged as
an open question in
[`057-open-domain-questions.md`](057-open-domain-questions.md).
