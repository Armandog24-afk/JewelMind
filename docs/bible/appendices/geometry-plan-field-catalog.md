---
id: JM-BIBLE-A29
title: "Appendix: Geometry Plan Field Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-166
related_documents:
  - JM-BIBLE-A09
implementation_status: planned
professional_validation: not_required
normative: true
---

# Appendix: Geometry Plan Field Catalog

Every field in `specs/alchemist/v1/geometry-plan.schema.json` and `geometry-plan-component.schema.json`, with real example values from `specs/alchemist/v1/examples/default-solitaire-geometry-plan.json`.

## `GeometryPlan`

| Field | Real example value |
|---|---|
| `planVersion` | `"1.0.0"` |
| `sourceDefinitionHash` | `"355ddca57e7e49ad"` |
| `compilerVersion` | `"0.1.0"` |
| `buildOrder` | `["band", "stone_reference", "prongs", "basket_support", "solitaire"]` |
| `derivedParameters.innerRadiusMm` | `8.9` |
| `derivedParameters.outerRadiusMm` | `10.700000000000001` |
| `derivedParameters.bandTopZMm` | `10.700000000000001` |
| `derivedParameters.prongCenterRadiusMm` | `3.085` |
| `derivedParameters.embedMm` | `0.4` |

## `GeometryComponentPlan` (band, real example)

| Field | Value |
|---|---|
| `componentPlanId` | `"band"` |
| `componentType` | `"solid"` |
| `sourceJDLPaths` | `["ring.innerDiameter", "band.width", "band.thickness", "band.profile"]` |
| `buildOperation` | `"revolve_comfort_fit_profile"` |
| `productionRole` | `"included_by_default"` |
| `fallbackPolicy` | `"fallback_to_unfilleted_solid"` |

**None of this is implemented** — see [`08-alchemist/166-geometry-plan-model.md`](../08-alchemist/166-geometry-plan-model.md).
