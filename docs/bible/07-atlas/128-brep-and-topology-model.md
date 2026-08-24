---
id: JM-BIBLE-128
title: B-Rep and Topology Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-122
related_documents:
  - JM-BIBLE-134
implementation_status: partial
professional_validation: not_required
normative: true
---

# B-Rep and Topology Model

## B-Rep, conceptually and for JewelMind

Boundary Representation (B-Rep) describes a solid exactly, by its bounding topology: vertices (points), edges (curves between vertices), wires (ordered edge loops), faces (bounded surface regions), shells (connected face sets), and solids (closed shells enclosing a volume). Every `GeneratedComponent.shape` in JewelMind is a real OCCT B-Rep object — never an approximation — until it is explicitly tessellated for preview or STL export (see [`129-mesh-model.md`](129-mesh-model.md)).

## Topology risks

| Risk | Currently checked? | Where |
|---|---|---|
| Invalid solids (e.g. self-intersecting shells, non-manifold topology) | **No** — no `BRepCheck_Analyzer` or equivalent validity check runs anywhere in this codebase | Gap — see [`150-atlas-gap-analysis.md`](150-atlas-gap-analysis.md) |
| Disconnected solids | **Partially** — `_fuse_metal()` checks `fused.Solids()` is non-empty after fuse, and the fallback compound is by definition 3 separate solids; there is no check for *unintended* disconnection within what should be one continuous fused body | `solitaire.py::_fuse_metal` |
| Coincident surfaces | **No** — not checked | Gap |
| Tiny edges | **No** — not checked; `FlatCircleAtRadius`'s `tol=1e-3` (band.py's fillet-edge selector) is a *selection* tolerance, not a tiny-edge detector | `geometry/primitives/selectors.py` |
| Failed booleans | **Yes** — the fuse operation is wrapped in try/except with an explicit fallback (see [`134-boolean-operation-strategy.md`](134-boolean-operation-strategy.md)) | `solitaire.py::_fuse_metal` |
| Self-intersections | **No** — not checked for any component's own geometry (e.g. an extreme parameter combination causing the comfort-fit arc to self-intersect is not detected before `.revolve()` is attempted) | Gap |
| Degenerate faces | **No** — not checked | Gap |

## Vertices, edges, wires, faces, shells, solids, compounds — where each appears in current code

- **Vertices/edges/wires**: implicitly constructed by every `.moveTo()`/`.lineTo()`/`.threePointArc()`/`.circle()`/`.polyline()` call, never directly manipulated by JewelMind code.
- **Faces/shells**: implicitly produced by `.revolve()`, `.extrude()`, `.loft()`, `.cut()`, `.fuse()` — never directly constructed.
- **Solids**: the output type of every component builder.
- **Compounds**: `prongs` (always), `combined_metal` (fallback only), and the STEP/STL export shape when `include_stone=True` (`cq.Compound.makeCompound([combined_metal, stone_reference])`).

## What is CURRENT vs. PLANNED

**CURRENT**: failed-boolean detection and fallback (one specific case). **PLANNED, none implemented**: general solid-validity checking, coincident-surface detection, tiny-edge detection, self-intersection detection, degenerate-face detection. This is the same honest gap already surfaced in Sprint 4's [`06-forge/106-generated-geometry-inspection-rules.md`](../06-forge/106-generated-geometry-inspection-rules.md); this document is the Atlas-level (geometry-owning) restatement of the same gap, cross-referenced rather than duplicated in [`150-atlas-gap-analysis.md`](150-atlas-gap-analysis.md).
