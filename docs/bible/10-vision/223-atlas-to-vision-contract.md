---
id: JM-BIBLE-223
title: Atlas to Vision Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-130
  - JM-BIBLE-144
related_documents:
  - JM-BIBLE-226
implementation_status: current
professional_validation: not_required
normative: true
---

# Atlas to Vision Contract

## The per-component preview manifest, as of this Sprint

`backend/jewelmind/preview/mesh.py::write_component_previews()` now emits, per component:

| Field | Status before Sprint 8 | Status as of Sprint 8 |
|---|---|---|
| `file` / `url` | CURRENT | Unchanged |
| `vertexCount`, `triangleCount` | CURRENT | Unchanged |
| `volumeMm3` | CURRENT | Unchanged |
| `boundingBox` | CURRENT | Unchanged |
| `warnings` | CURRENT | Unchanged |
| `geometryRole` | Derivable only (`07-atlas/130-component-contract.md` called this CURRENT-but-implicit) | **CURRENT, explicit** — `production_metal` for band/prongs/basket_support, `stone_reference` for the stone |
| `productionRole` | Derivable only | **CURRENT, explicit** — `included_by_default` / `excluded_by_default`, matching Foundry's [`09-foundry/195-component-inclusion-policy.md`](../09-foundry/195-component-inclusion-policy.md) |
| `meshSource` | Not present | **CURRENT, explicit** — always `"stl"` today |
| `generationStatus` | Not present | **CURRENT, explicit** — `SUCCEEDED` or `EMPTY`, mapped from the existing `has_geometry` check |

This is the "smallest backward-compatible metadata" this Sprint's own scope allowed: no new endpoint, no schema-breaking change (`GenerateResponse.previewComponents` was already typed `dict[str, Any]` on the backend and a loosely-typed record on the frontend), and every new field is additive — a frontend built against the pre-Sprint-8 manifest shape still works unchanged, it simply won't see the new fields.

## Why this closes a real, previously-named gap

[`07-atlas/130-component-contract.md`](../07-atlas/130-component-contract.md) already named `geometryRole`/`productionRole`/`previewRole` as CURRENT-but-derivable concepts back in Sprint 5, and [`144-preview-mesh-contract.md`](../07-atlas/144-preview-mesh-contract.md) explicitly said material-role inference from the component name string was "not currently a distinct manifest field." Vision's frontend code (`ModelViewport.tsx`) now reads `entry.geometryRole` first, falling back to the name-based check (`name === 'stone_reference'`) only when the field is absent — satisfying VISION-GOV-011 ("all component visibility must use explicit component identity") while staying safe against an older cached response shape.

## Current components, mapped

| Component | `geometryRole` | `productionRole` | `meshSource` |
|---|---|---|---|
| `band` | `production_metal` | `included_by_default` | `stl` |
| `prongs` | `production_metal` | `included_by_default` | `stl` |
| `basket_support` | `production_metal` | `included_by_default` | `stl` |
| `stone_reference` | `stone_reference` | `excluded_by_default` | `stl` |

## What Vision does not receive

`sourceJDLPaths`, `inspectionResults`, or any Forge-domain field — restating VISION-GOV-001/002: Vision's only per-component inputs are geometric/identity facts, never a jewelry-domain rule outcome.
