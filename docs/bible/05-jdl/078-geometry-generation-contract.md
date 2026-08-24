---
id: JM-BIBLE-078
title: Geometry Generation Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-077
related_documents:
  - JM-BIBLE-079
  - JM-BIBLE-052
  - JM-BIBLE-130
implementation_status: current
professional_validation: not_required
normative: true
---

# Geometry Generation Contract

**Relationship to Atlas (Sprint 5):** this document's per-component
contract table is superseded in detail (never contradicted) by
[`07-atlas/130-component-contract.md`](../07-atlas/130-component-contract.md)
(the normative `AtlasGeometryComponent` model) and
[`07-atlas/149-current-solitaire-geometry-mapping.md`](../07-atlas/149-current-solitaire-geometry-mapping.md)
(a full JDL-field-to-operation trace). Atlas also formalizes the exact
fillet/fuse fallback behavior only briefly summarized here — see
[`07-atlas/135-fillets-rounding-and-fallbacks.md`](../07-atlas/135-fillets-rounding-and-fallbacks.md).

Per-component contract, grounded directly in `backend/jewelmind/geometry/components/*.py`, `geometry/constants.py`, and `geometry/assemblies/solitaire.py`.

## Shared derived values (`geometry/constants.py`)

| Derived value | Formula | Used by |
|---|---|---|
| `inner_radius` | `ring.innerDiameter / 2` | band |
| `outer_radius` | `inner_radius + band.thickness` | band, stone (via `band_top_z`), prongs, basket |
| `band_top_z` | `outer_radius` | stone, prongs, basket (assembly anchor point) |
| `prong_center_radius` | `stone.diameter/2 − (setting.prongDiameter/2) × 0.3` | prongs, basket (shared footprint) |
| `EMBED_MM` | fixed constant `0.4` mm | prongs, basket (base embedding depth for a genuine 3D overlap with the band, so a boolean fuse has real volume to merge, not a zero-volume tangent touch) |

## Per-component contract

| Component | Input fields | Derived values used | Output name | Type | Invariants | Inspection checks | Fallback | Warnings | File | Tests |
|---|---|---|---|---|---|---|---|---|---|---|
| Band | `band.width`, `band.thickness`, `band.profile`, `ring.innerDiameter` | `inner_radius`, `outer_radius` | `"band"` | `GeneratedComponent` (single solid, revolved) | Non-zero, finite volume; `outer_radius > inner_radius` (also checked as `JM-GEOMETRY-001` upstream) | `volume_mm3 > 0`; bounding box spans the expected radial range | None documented — no known failure mode for this component today | none by default | `geometry/components/band.py` | `test_geometry.py` |
| Stone reference | `stone.diameter`, `stone.depth`, `setting.basketHeight` | `band_top_z` | `"stone_reference"` | `GeneratedComponent` (single solid, reference-only) | Never fused into `combined_metal`; excluded from export unless `includeStoneReference: true` (LAW-006) | `volume_mm3 > 0`; bounding box sits above `band_top_z` | None documented | none by default | `geometry/components/stone.py` | `test_geometry.py::test_stone_reference_is_valid_and_separate_from_metal` |
| Prongs | `setting.prongCount`, `setting.prongDiameter`, `setting.prongHeight` | `band_top_z`, `prong_center_radius`, `EMBED_MM` | `"prongs"` | `GeneratedComponent` (compound of individual prong solids) | Prong count as requested (invalidity is caught upstream by `JM-PRONG-001`, not by this builder) | `volume_mm3 > 0`; per-prong solids present | None documented | none by default | `geometry/components/prongs.py` | `test_geometry.py` |
| Basket support | `setting.basketHeight`, `setting.prongDiameter` | `band_top_z`, `prong_center_radius`, `EMBED_MM` | `"basket_support"` | `GeneratedComponent` (single solid) | Embedded `EMBED_MM` into the band's assembly anchor for fuse compatibility | `volume_mm3 > 0` | None documented | none by default | `geometry/components/basket.py` | `test_geometry.py` |
| Full assembly (`combined_metal`) | outputs of band + prongs + basket | — | `combined_metal` on `GeneratedModel` | `cq.Shape` — either one fused solid, or (fallback) a multi-solid `cq.Compound` | Never includes the stone (LAW-006); always includes band + prongs + basket in some form | `combined_metal_volume_mm3 > 0`; `bounding_box` unions metal + stone reference | **Documented fallback**: if `.fuse()` raises or yields zero solids, fall back to `cq.Compound.makeCompound([band, basket, prongs])` — this is the only fallback path in the current geometry pipeline, matching CLAUDE.md's "never fake an export" guidance | `"Combined metal union failed (...); exporting band, prongs, and basket as a multi-solid compound instead of a single fused solid."` appended to `GeneratedModel.warnings` | `geometry/assemblies/solitaire.py::_fuse_metal` | `test_geometry.py` |

## Component-manifest requirements

The current `GeneratedComponent` dataclass (`geometry/model.py`) carries: `name`, `shape` (the CadQuery/OCCT solid itself, not serialized directly), `volume_mm3`, `bounding_box`, `warnings`, `metadata` (a free-form dict — e.g. band's builder stores `profile` there). It does **not** currently carry: a `productionInclusion`/`previewInclusion` boolean pair, a `materialRole` field, or an explicit `parentAssembly` reference — these are useful conceptual fields for a future, richer manifest format, but adding them is an application code change out of scope for this documentation Sprint. Recorded as a gap in [`084-current-implementation-mapping.md`](084-current-implementation-mapping.md), not implemented here.
