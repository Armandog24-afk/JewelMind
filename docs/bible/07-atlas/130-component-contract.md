---
id: JM-BIBLE-130
title: Component Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-121
related_documents:
  - JM-BIBLE-A20
implementation_status: partial
professional_validation: not_required
normative: true
---

# Component Contract

The normative `AtlasGeometryComponent` model is `specs/atlas/v1/geometry-component.schema.json`; two real worked examples (`band-component.json`, `forge-geom-001`-adjacent inspection facts aside) are in `specs/atlas/v1/examples/`.

## Fields and current mapping

| Field | Current mapping | Status |
|---|---|---|
| `componentId` / `componentName` | `GeneratedComponent.name` (`"band"`, `"stone_reference"`, `"prongs"`, `"basket_support"`) | CURRENT |
| `componentType` | Not an explicit field — derivable (`band`/`stone_reference`/`basket_support` are solids; `prongs` is always a compound) | CURRENT (derivable) |
| `parentAssembly` | Implicit — always `"solitaire"`, the only assembly | CURRENT (implicit) |
| `geometryRole` | Not an explicit field — see mapping below | CURRENT (derivable) |
| `productionRole` | Not an explicit field — derivable from `include_stone` exporter logic | CURRENT (derivable) |
| `previewRole` | Not an explicit field — every component is currently always visible in preview | CURRENT (derivable) |
| `sourceJDLPaths` | Not tracked as a field — derivable by reading each builder's field accesses (documented per-component in [`149-current-solitaire-geometry-mapping.md`](149-current-solitaire-geometry-mapping.md)) | PARTIAL |
| `derivedParameters` | `GeneratedComponent.metadata` (a free-form dict) | CURRENT |
| `geometry` | The actual `cq.Shape`/OCCT object — never serialized; this schema deliberately represents metadata only | CURRENT (by design, see below) |
| `boundingBox` | `GeneratedComponent.bounding_box` | CURRENT |
| `volume` | `GeneratedComponent.volume_mm3` | CURRENT |
| `transform` | **Not implemented** — see [`125-transformations.md`](125-transformations.md) | PLANNED |
| `generationStatus` | Not an explicit field — derivable from whether `warnings` is empty and whether solids exist | PARTIAL |
| `warnings` | `GeneratedComponent.warnings` | CURRENT |
| `fallbackUsed` | Not an explicit field — derivable from `warnings` content or, for the band, `metadata["filletApplied"] == False` | PARTIAL |
| `inspectionResults` | **Not implemented** — no component carries embedded inspection results | PLANNED |

## `geometryRole`, mapped to the current four components

| Component | `geometryRole` | `productionRole` | `previewRole` |
|---|---|---|---|
| `band` | `production_metal` | `included_by_default` | `visible` |
| `stone_reference` | `stone_reference` | `excluded_by_default` | `visible` |
| `prongs` | `production_metal` | `included_by_default` | `visible` |
| `basket_support` | `production_metal` | `included_by_default` | `visible` |

**No component currently has `geometryRole: "support"` or `previewRole: "hidden"`** — `support` is listed in the schema as a category future components (e.g. a gallery or bridge, per [`04-jewelry-domain/049-basket-and-support-domain.md`](../04-jewelry-domain/049-basket-and-support-domain.md), NOT IMPLEMENTED) might occupy; `basket_support` is currently classified `production_metal` because, despite its name, it is fused into the same metal body as the band and prongs, not treated as a structurally distinct support role today.

## Machine-readable records do not serialize kernel geometry

Per this Sprint's explicit instruction, `specs/atlas/v1/geometry-component.schema.json`'s `geometry` field is a placeholder object (`{"representation": "kernel-native-not-serialized"}`), never an attempt to encode the actual OCCT B-Rep or a mesh. A component record describes geometry — its metadata, bounding box, volume, warnings — never the geometry itself.
