---
id: JM-BIBLE-133
title: Operation Contracts
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-132
related_documents:
  - JM-BIBLE-A21
implementation_status: current
professional_validation: not_required
normative: true
---

# Operation Contracts

Every CadQuery operation actually used in this codebase, inventoried directly from `geometry/components/*.py` and `geometry/assemblies/solitaire.py`. See [`atlas-operation-catalog.md`](../appendices/atlas-operation-catalog.md) for the appendix-form summary table.

| Operation | Inputs | Expected output | Failure modes | Deterministic? | Fallback | Wrapper or direct call |
|---|---|---|---|---|---|---|
| Workplane creation | Plane name (`"XY"`), optional Z offset | A `cq.Workplane` context | None observed | Yes | n/a | Direct (`cq.Workplane("XY")`, `.workplane(offset=...)`) |
| Sketch/profile creation | Points, arc control points | A closed 2D wire | A non-closing point set would fail `.close()` — not currently possible given fixed-formula inputs | Yes | None | Direct (`.moveTo`, `.lineTo`, `.threePointArc`, `.polyline`, `.close`) |
| Revolve | A closed wire + axis + angle | A solid | Self-intersecting or degenerate profile (not currently guarded) | Yes | None | Direct (`.revolve(360, (0,0,0), (0,1,0))`) |
| Extrude | A closed 2D profile + height | A solid | height <= 0 not currently possible (basket/prong heights always include `EMBED_MM` addition) | Yes | None | Direct (`.circle(r).extrude(h)`) |
| Loft | An ordered list of cross-sections | A solid | A non-monotonic or self-intersecting cross-section sequence (not currently guarded) | Yes | None | Direct (`.loft(ruled=True)`) |
| Sweep | n/a | n/a | n/a | n/a | n/a | **Never used** anywhere in this codebase |
| Cylinder creation | Circle + extrude, not a dedicated CadQuery cylinder primitive | A solid | See extrude | Yes | None | Direct, via circle+extrude composition |
| Translation | Workplane offset, `.center(x, y)` | A repositioned construction context | None observed | Yes | n/a | Direct |
| Rotation | `.revolve()`'s angle parameter; `math.cos`/`math.sin` for prong placement | A solid, or a set of positions | None observed | Yes | n/a | Direct / plain Python math |
| Union (fuse) | Two or more solids | A single solid, or a raised exception | A boolean fuse can fail or yield zero solids for tolerance-sensitive OCCT reasons | Yes, for a fixed OCCT version and input (see [`137-determinism-and-reproducibility.md`](137-determinism-and-reproducibility.md) for the OCCT-version caveat) | **Yes — documented fallback to a multi-solid compound** | Direct (`.fuse()`), wrapped in `solitaire.py::_fuse_metal`'s try/except |
| Cut | Outer solid − inner solid | A hollow solid | None observed for current parameter ranges | Yes | None | Direct (`outer.cut(inner)`, `basket.py`) |
| Intersection | n/a | n/a | n/a | n/a | n/a | **Never used** anywhere in this codebase |
| Fillet | A solid + edge selector + radius | A solid with rounded edges, or a raised exception | OpenCascade fillet operations are known to be tolerance-sensitive and can fail for small radii or unusual edge geometry | Yes, for a fixed OCCT version and input | **Yes — documented fallback to the unfilleted solid** | Direct (`.fillet()`), wrapped in `band.py::_try_fillet_outer_rim`'s caller try/except |
| Tessellation | A solid + tolerance + angular tolerance | Vertices + triangles, or a written STL file | None observed for valid finite tolerances | Yes, for fixed tolerance values | None | Direct (`.tessellate()`, `.exportStl()`) |
| Export (STEP) | A solid or compound | A written STEP file | None observed | Yes | None | Direct (`.exportStep()`) |

## Direct CadQuery usage, not conceptual wrappers

With the sole exceptions of `FlatCircleAtRadius` (an edge selector, `geometry/primitives/selectors.py`) and the two documented fallback try/excepts (fillet, fuse), **every operation above is a direct CadQuery call** — there is no intermediate "Atlas operation" abstraction layer in the current codebase. This document names the operations conceptually for cataloging purposes; it does not claim a wrapper API exists where only direct calls do.
