---
id: JM-BIBLE-A07
title: "Appendix: Jewelry Domain Relationship Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-044
related_documents:
  - JM-BIBLE-A05
  - JM-BIBLE-052
implementation_status: current
professional_validation: not_required
---

# Appendix: Jewelry Domain Relationship Matrix

Relationship types: **contains**, **depends on**, **generates**,
**validates**, **describes**, **excludes**, **remains separate from**.

| From | Relationship | To | Type | Code reference |
|---|---|---|---|---|
| Ring | contains | Band | contains | `JewelryDefinition.band` |
| Ring | contains | Stone | contains | `JewelryDefinition.stone` |
| Ring | contains | Setting | contains | `JewelryDefinition.setting` |
| Setting | contains | Prongs | contains | `SettingSpec` fields drive `geometry/components/prongs.py` |
| Ring | contains | Material | contains | `JewelryDefinition.material` |
| Ring | contains | Manufacturing context | contains | `JewelryDefinition.manufacturing` |
| Ring | contains | Preview configuration | contains | `JewelryDefinition.preview` |
| Band | depends on | Ring (inner diameter) | depends on | `geometry/constants.py::inner_radius` reads `ring.innerDiameter` |
| Basket | depends on | Band (top Z anchor) | depends on | `geometry/components/basket.py` reads `band_top_z()` |
| Prongs | depends on | Band (top Z anchor) | depends on | `geometry/components/prongs.py` reads `band_top_z()` |
| Prongs | depends on | Stone (girdle radius) | depends on | `geometry/constants.py::prong_center_radius` reads `stone.diameter` |
| Basket | depends on | Prongs (shared center radius) | depends on | `geometry/components/basket.py` reuses `prong_center_radius()` |
| Stone (girdle Z) | depends on | Setting (basket height) | depends on | `geometry/components/stone.py` reads `setting.basketHeight` |
| Ring | generates | Band geometry | generates | `geometry/components/band.py::build_ring_band` |
| Ring | generates | Stone reference geometry | generates | `geometry/components/stone.py::build_stone_reference` |
| Ring | generates | Prong geometry | generates | `geometry/components/prongs.py::build_prongs` |
| Ring | generates | Basket geometry | generates | `geometry/components/basket.py::build_basket_support` |
| Ring | generates | Preview meshes | generates | `preview/mesh.py::write_component_previews` |
| Ring | generates | STEP artifact | generates | `exporters/step_exporter.py::export_step` |
| Ring | generates | STL artifact | generates | `exporters/stl_exporter.py::export_stl` |
| Ring | generates | JSON artifact | generates | `exporters/json_exporter.py::export_json` |
| Ring | generates | Specification artifact | generates | `exporters/specification.py::build_specification` |
| Validation engine | validates | Ring | validates | `validation/engine.py::validate_definition` |
| Preview | describes | Generated geometry | describes | Preview meshes are a tessellated *description* of the exact solids, not independent geometry |
| Specification | describes | Ring + generated model | describes | `exporters/specification.py` renders parameters, volumes, and validation results as text |
| Metal export (default) | excludes | Stone reference | excludes | `step_exporter.py`/`stl_exporter.py` default `include_stone=False` |
| Combined metal body | remains separate from | Stone reference | remains separate from | `geometry/assemblies/solitaire.py::_fuse_metal` never receives `stone` ([LAW-006](../00-foundation/004-jewelmind-constitution.md#LAW-006)) |
| Manufacturing context | describes | Ring (intended process) | describes | `ManufacturingSpec.method` is metadata/context, not a geometry driver |
| Material | describes | Ring (intended metal) | describes | `MaterialSpec.metal` is metadata/preview-color only |
| Frontend validation mirror | validates | Ring (locally, non-authoritatively) | validates | `shared/validation/engine.ts` — see [ADR-004](../03-decisions/ADR-004-backend-authoritative-validation.md) |

## Notes on relationship direction

"Depends on" edges point from the *dependent* geometry to the parameter
or component it reads — this matches the direction of data flow in
[`052-parametric-dependency-model.md`](../04-jewelry-domain/052-parametric-dependency-model.md)'s
graph, not necessarily the direction of physical assembly (e.g. physically
the basket sits *above* the band, but in dependency terms the basket
*depends on* the band's `band_top_z`, so the arrow points basket → band).
