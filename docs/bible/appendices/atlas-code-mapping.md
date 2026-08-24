---
id: JM-BIBLE-A26
title: "Appendix: Atlas Code Mapping"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-149
related_documents:
  - JM-BIBLE-055
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Atlas Code Mapping

Every Atlas concept mapped to its real backend file, cross-checked against `backend/jewelmind/geometry/`, `preview/`, and `exporters/` during this Sprint.

| Atlas concept | Backend file(s) |
|---|---|
| Derived geometric parameters | `geometry/constants.py` |
| Band component builder | `geometry/components/band.py` |
| Stone reference component builder | `geometry/components/stone.py` |
| Prong component builder | `geometry/components/prongs.py` |
| Basket support component builder | `geometry/components/basket.py` |
| Edge selector (fillet support) | `geometry/primitives/selectors.py` |
| Component/bounding-box/assembly data model | `geometry/model.py` |
| Assembly builder + boolean fuse strategy | `geometry/assemblies/solitaire.py` |
| Preview tessellation + manifest | `preview/mesh.py` |
| STEP export | `exporters/step_exporter.py` |
| STL export | `exporters/stl_exporter.py` |
| Generation orchestration, caching, temp-file lifecycle | `services/model_service.py` |
| CAD engine health probe | `services/cad_engine.py` |
| Geometry-related error types | `api/errors.py` |
| Geometry tests | `backend/tests/test_geometry.py` |
| Atlas specification self-check | `backend/tests/test_atlas_registry.py` (new, Sprint 5) |

## Duplication found

**None.** Unlike Sprint 4's finding of an exact frontend/backend rule mirror for validation, geometry construction has **no frontend equivalent at all** — the frontend never constructs, approximates, or duplicates any geometry; it only renders backend-generated STL files (ATLAS-GOV-010). No geometric threshold or formula is duplicated between two files anywhere in the current codebase.

## Undocumented assumptions found (before this Sprint)

7 magic numbers (see [`atlas-geometry-invariant-catalog.md`](atlas-geometry-invariant-catalog.md)) and 1 undocumented CAD-kernel-tolerance fact (JewelMind never overrides OCCT's internal default — see [`07-atlas/136-tolerance-model.md`](../07-atlas/136-tolerance-model.md)) were found and are now documented as of this Sprint.

## Preview vs. export geometry divergence

Not a defect, but a documented architectural fact worth restating here: preview tessellates the four pre-fuse components; STEP/STL export tessellates the post-fuse `combined_metal` (see [`07-atlas/144-preview-mesh-contract.md`](../07-atlas/144-preview-mesh-contract.md), [`146-stl-export-geometry-contract.md`](../07-atlas/146-stl-export-geometry-contract.md)). This means the frontend's four-mesh preview and the exported single/triple-solid STL are genuinely different tessellation outputs, though of the same underlying components.
