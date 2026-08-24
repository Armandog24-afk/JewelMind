---
id: JM-BIBLE-124
title: Geometric Primitives
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-122
related_documents:
  - JM-BIBLE-A20
implementation_status: current
professional_validation: not_required
normative: true
---

# Geometric Primitives

Every primitive actually used by the current geometry code, catalogued factually — none invented, none implemented as a custom class where CadQuery already owns the concept.

| Primitive | Definition | Parameters | CadQuery mapping | Current usage | Output type | Invariants | Limitations |
|---|---|---|---|---|---|---|---|
| Point3 | A 3D location | (x, y, z) | Tuple args to `.moveTo()`, `.center()`, `.lineTo()` | Every builder | n/a (input) | mm | No dedicated wrapper class — plain tuples throughout |
| Vector3 | A direction | (x, y, z) | Tuple args to `.revolve(angle, axis_start, axis_end)` | `band.py` | n/a (input) | Unit-independent | No dedicated wrapper class |
| Axis | A line + direction | Two points | `.revolve(360, (0,0,0), (0,1,0))` | `band.py` | n/a (input) | Fixed to global Y for the band | Only one axis is ever used; no generalized axis object exists |
| Plane | A 2D workplane | Named plane string | `cq.Workplane("XY")` | Every builder | n/a (construction context) | Always `"XY"`, offset via `.workplane(offset=...)` | No non-axis-aligned workplane is ever used |
| Circle | A closed circular curve | Center + radius | `.circle(r)` | `stone.py`, `prongs.py`, `basket.py` | Wire (2D) | radius > 0 required by CadQuery (not separately checked by JewelMind code before the call) | — |
| Arc | A circular curve segment | Three points (JewelMind's usage) | `.threePointArc((x1,y1),(x2,y2))` | `band.py` comfort-fit wire | Curve segment | — | Only a three-point arc form is used; no start-angle/sweep-angle arc form appears |
| Line | A straight segment | Two points | `.lineTo(x, y)` | `band.py` flat wire, comfort-fit wire | Curve segment | — | — |
| Polyline | A connected sequence of line segments | List of points | `.polyline(pts)` | `band.py::_build_flat_wire` | Wire (open, closed via `.close()`) | Points must form a valid closed loop when `.close()` is called | — |
| Profile | A closed 2D cross-section | A closed wire | `cq.Workplane` chain ending in `.close()` | `band.py`'s flat/comfort-fit wires | Wire | Must be planar and non-self-intersecting for `.revolve()`/`.extrude()` to succeed | No explicit self-intersection check exists before the operation is attempted |
| Cylinder | A circular-cross-section extrusion | Radius + height | `.circle(r).extrude(h)` | `prongs.py`, `basket.py` (as outer/inner shells) | Solid | height > 0 | No taper — a true cylinder only, no cone |
| Cone / tapered solid | A linearly-tapering solid | n/a | Not used | Not used anywhere in the current codebase | n/a | n/a | No component currently has a tapered profile |
| Revolved profile | A solid formed by revolving a 2D wire around an axis | Wire + axis + angle | `.revolve(360, axis_start, axis_end)` | `band.py` (both profiles) | Solid | Always a full 360° revolution | No partial-revolution component exists |
| Ring-like solid | A torus-like or annular solid | n/a as a dedicated CadQuery primitive | Achieved via revolve (band) or via cut of two concentric cylinders (basket) | `band.py` (revolve), `basket.py` (`outer.cut(inner)`) | Solid | — | Two different construction strategies are used for two conceptually similar "ring-like" shapes — not a defect, just worth noting for a future primitives library |
| Lofted solid | A solid interpolated between cross-sections at different heights | Ordered list of profiles at different Z offsets | `.loft(ruled=True)` | `stone.py` (culet→girdle→table) | Solid | `ruled=True` (straight-line interpolation between cross-sections, not smoothed) | Only the stone reference uses loft; no other component does |
| Compound | An unordered collection of solids | List of shapes | `cq.Compound.makeCompound([...])` | `prongs.py` (always), `solitaire.py::_fuse_metal` (fallback only) | Compound | — | — |

## No custom primitive implementation

Every primitive above is a direct CadQuery/OpenCascade call — JewelMind's own code (`geometry/primitives/`) contains exactly one custom class, `FlatCircleAtRadius` (an edge *selector*, not a primitive constructor — see [`134-boolean-operation-strategy.md`](134-boolean-operation-strategy.md) and [`135-fillets-rounding-and-fallbacks.md`](135-fillets-rounding-and-fallbacks.md)), confirming ATLAS-GOV-002's spirit of not reinventing what the kernel already owns.
