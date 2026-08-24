---
id: JM-BIBLE-A21
title: "Appendix: Atlas Operation Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-133
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Atlas Operation Catalog

Every CadQuery operation used anywhere in the current geometry codebase. See [`07-atlas/133-operation-contracts.md`](../07-atlas/133-operation-contracts.md) for the full per-operation contract.

| Operation | Used by | Deterministic | Fallback exists |
|---|---|---|---|
| Workplane creation | All builders | Yes | n/a |
| Sketch/profile (`.moveTo`, `.lineTo`, `.threePointArc`, `.polyline`, `.close`) | `band.py` | Yes | No |
| Revolve | `band.py` | Yes | No |
| Extrude | `prongs.py`, `basket.py` | Yes | No |
| Loft | `stone.py` | Yes | No |
| Sweep | **Never used** | n/a | n/a |
| Cylinder (circle + extrude) | `prongs.py`, `basket.py` | Yes | No |
| Translation (`.center`, workplane offset) | All builders | Yes | n/a |
| Rotation (`.revolve` angle; `math.cos`/`math.sin`) | `band.py`, `prongs.py` | Yes | n/a |
| Union (`.fuse`) | `solitaire.py::_fuse_metal` | Yes | **Yes** — compound fallback |
| Cut | `basket.py` | Yes | No |
| Intersection | **Never used** | n/a | n/a |
| Fillet | `band.py` | Yes | **Yes** — unfilleted fallback |
| Tessellation (`.tessellate`, `.exportStl`) | `preview/mesh.py`, `exporters/stl_exporter.py` | Yes | No |
| Export (`.exportStep`) | `exporters/step_exporter.py` | Yes | No |

**Total distinct operations catalogued: 14** used, 2 never used (sweep, intersection). **Fallback exists for 2 of 14** (union, fillet) — see [`atlas-fallback-register.md`](atlas-fallback-register.md).
