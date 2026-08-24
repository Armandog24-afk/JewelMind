---
id: JM-BIBLE-122
title: Geometric Representation Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-121
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Geometric Representation Model

**JewelMind does not own a custom CAD kernel.** Every representation below is provided by CadQuery (a Python fluent API) built on OpenCascade (OCCT, the underlying B-Rep geometry kernel). This is unchanged from ADR-001/ADR-002 and is restated here as the Atlas-level foundational fact.

| Representation | Definition | Provided by | CURRENT in JewelMind? |
|---|---|---|---|
| Point | A location in 3D space | OCCT `gp_Pnt`, exposed via CadQuery tuples/`cq.Vector` | Yes — used throughout (e.g. `.moveTo()`, `.center()`) |
| Vector | A direction + magnitude | OCCT `gp_Vec` / CadQuery `cq.Vector` | Yes |
| Plane | An infinite flat surface with an origin and normal | OCCT `gp_Pln` / CadQuery `Workplane` planes | Yes — every builder starts from `cq.Workplane("XY")` |
| Axis | A line with a direction | OCCT `gp_Ax1` | Yes — the revolve axis `(0,0,0)-(0,1,0)` in `build_ring_band` |
| Coordinate frame | An origin + three orthogonal axes | OCCT `gp_Ax2`/`gp_Ax3` | Yes, implicitly — see [`123-coordinate-system-and-orientation.md`](123-coordinate-system-and-orientation.md) |
| Curve | A 1D parametric shape (line, arc, etc.) | OCCT `Geom_Curve` subclasses | Yes — `.lineTo()`, `.threePointArc()` |
| Profile | A closed 2D wire used as a revolve/extrude cross-section | CadQuery sketch/wire API | Yes — the band's flat/comfort-fit wires |
| Wire | An ordered, connected sequence of edges | OCCT `TopoDS_Wire` | Yes, implicitly (CadQuery's `.close()`) |
| Face | A bounded portion of a surface | OCCT `TopoDS_Face` | Yes, implicitly |
| Shell | A connected set of faces | OCCT `TopoDS_Shell` | Yes, implicitly |
| Solid | A closed volume bounded by a shell | OCCT `TopoDS_Solid` | Yes — every `GeneratedComponent.shape` is (or contains) one or more solids |
| Compound | An unordered collection of shapes | OCCT `TopoDS_Compound` | Yes — `prongs` is always a compound; `combined_metal` is a compound on fuse fallback |
| Assembly | A named collection of components with shared metadata | Not an OCCT/CadQuery concept — a JewelMind-level grouping | Yes, at the JewelMind level — `GeneratedModel` |
| B-Rep | Boundary Representation: a solid described by its bounding faces/edges/vertices, exactly (not approximated) | OCCT's native internal representation | Yes — this is what every `GeneratedComponent.shape` actually is until tessellated |
| Mesh | A triangulated approximation of a B-Rep surface | OCCT `BRepMesh_IncrementalMesh`, exposed via CadQuery's `.tessellate()`/`.exportStl()` | Yes — used only for preview and STL, never as source geometry (see [`129-mesh-model.md`](129-mesh-model.md)) |
| Bounding box | The smallest axis-aligned box containing a shape | OCCT `Bnd_Box`, exposed via CadQuery's `.BoundingBox()` | Yes — `BoundingBox.from_shape()` in `geometry/model.py` |
| Volume | The enclosed volume of a solid | OCCT's `BRepGProp` volume properties, exposed via CadQuery's `.Volume()` | Yes |
| Topology | The connectivity structure of vertices/edges/faces/shells/solids | OCCT's `TopoDS_*` hierarchy | Yes, implicitly — see [`128-brep-and-topology-model.md`](128-brep-and-topology-model.md) for which topology properties are and are not currently checked |

## Kernel independence is VISION, not planned

A future kernel-neutral geometry interface (so Atlas could, in principle, target a different B-Rep kernel) is a long-term possibility with no scoped implementation path — see open question `ATLAS-OQ-001` in [`151-open-atlas-questions.md`](151-open-atlas-questions.md). It is not PLANNED, because nothing about it has been designed or scheduled; calling it PLANNED would overstate its status per [`00-foundation/000-bible-governance.md`](../00-foundation/000-bible-governance.md)'s classification rule.
