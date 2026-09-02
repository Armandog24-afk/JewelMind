---
id: JM-BIBLE-602
title: "Extended Shape Taxonomy"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-600
related_documents:
  - JM-BIBLE-603
  - JM-BIBLE-604
implementation_status: current
professional_validation: not_required
normative: true
---

# Extended Shape Taxonomy

The 21 native cuts, grouped by the construction strategy they share.

**A family is a geometry-reuse grouping, not a jewelry-marketing taxonomy.**
Two shapes in one family remain independently changeable canonical IDs
(STONEV2-GOV-005).

## The families

| Family | Shapes | Construction |
|---|---|---|
| `RADIAL` | round | Circle |
| `ELLIPTICAL` | oval | Ellipse |
| `POINTED_ELONGATED` | marquise | Two arcs meeting at points |
| `ASYMMETRIC_POINTED` | pear | One point, one rounded end |
| `RECTILINEAR` | baguette | Plain rectangle |
| `CLIPPED_RECTILINEAR` | emerald, radiant, asscher | Rectangle with clipped corners |
| `ROUNDED_RECTILINEAR` | cushion | Rectangle with arc corners |
| `SQUARE_ANGULAR` | princess | Plain rectangle |
| `TRIANGULAR` | triangle, trillion | Three vertices |
| `TAPERED_QUADRILATERAL` | tapered_baguette, trapezoid | Trapezoid |
| `POLYGONAL` | lozenge, hexagon, kite, shield | Explicit vertex list |
| `SPECIAL_OUTLINE` | heart, half_moon | Shape-specific construction |
| `SPHERICAL` | pearl | Sphere (no outline) |
| `CUSTOM` | custom | Caller-supplied points |
| `IMPORTED` | imported | External geometry |

## Where the brief's suggested taxonomy was followed, and where it was not

The brief proposed grouping `emerald` under both `RECTILINEAR` and
`CLIPPED_RECTILINEAR`. A shape has exactly one family here, because a family
selects a construction and emerald has one construction: it is
`CLIPPED_RECTILINEAR`. `baguette` occupies `RECTILINEAR` instead.

The brief also grouped `triangle` with `trillion` under `TRIANGULAR`, which is
kept — but the two are **not** the same shape. `triangle` has straight sides;
`trillion`'s bow outward. Sharing a family is precisely what
STONEV2-GOV-005 exists to keep from becoming an identity merge.

`TAPERED_QUADRILATERAL` was added beyond the brief's list, because
`tapered_baguette` and `trapezoid` share a genuinely distinct primitive —
a trapezoid needs a fourth dimension (`narrowWidth`) that no other family does.

## Why `princess` and `baguette` are separate shapes with identical geometry

Both are plain rectangles. `princess_outline` and `baguette_outline` produce the
same wire for the same dimensions.

They stay separate because they are distinct canonical identities with distinct
expected proportions — a princess is near-square, a baguette is elongated — and
because a future change to either (a princess corner treatment, say) must not
silently move the other. Aliasing one to the other would trade a real
distinction for a saved function.

The same reasoning applies to `tapered_baguette` versus `trapezoid`.

## Shapes deliberately NOT implemented

From `jewelmind/stone/capability.py::RESERVED_STONE_SHAPES`:

| Shape | Why not |
|---|---|
| `briolette` | Fully three-dimensional drop with no single girdle plane; the outline-plus-profile pipeline cannot express it |
| `rose_cut` | Defined by its facet arrangement rather than its outline; needs a real facet model |
| `old_mine` | A historical proportion set, not a distinct outline; would require sourced proportions JewelMind does not have |
| `star` | Concave polygonal outline is expressible, but no sourced proportions exist |
| `cross` | As above |

None is a JDL enum member and none has a generator. The last two are reachable
**today** through `CUSTOM_OUTLINE`, which is the point of the escape hatch: a
shape's absence from the enum is no longer the same as its absence from the
product.

**Enforced by** `test_stone_v2.py::test_every_reserved_shape_is_rejected_by_jdl`
and `test_reserved_shapes_have_no_generator_and_no_enum_membership`.

## Symmetry classes

Symmetry is a separate axis from family, and it is what the Setting System
actually reads to choose a placement strategy:

| Class | Shapes |
|---|---|
| `RADIAL` | round, pearl |
| `BILATERAL_BOTH_AXES` | oval, emerald, cushion, princess, marquise, radiant, asscher, baguette, lozenge, hexagon |
| `BILATERAL_ONE_AXIS` | pear, heart, trillion, triangle, trapezoid, tapered_baguette, kite, shield, half_moon |
| `UNKNOWN` | custom, imported |

`UNKNOWN` is treated as "not symmetric" by every consumer, which is the safe
direction: assuming symmetry a stone does not have mirrors prongs onto places
the stone never reaches, whereas assuming less symmetry than it has only costs
the outline-aware strategy.

## Cross-references

- [`shape-family-architecture.md`](shape-family-architecture.md) — the shared
  primitives themselves.
- [`extended-native-shapes.md`](extended-native-shapes.md) — how each shape is
  built, and what broke while building it.
