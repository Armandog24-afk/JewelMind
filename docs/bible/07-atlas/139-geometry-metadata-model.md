---
id: JM-BIBLE-139
title: Geometry Metadata Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-131
related_documents:
  - JM-BIBLE-A20
implementation_status: current
professional_validation: not_required
normative: true
---

# Geometry Metadata Model

The normative shape is `specs/atlas/v1/geometry-metadata.schema.json`; real values for the default definition are checked into `specs/atlas/v1/test-vectors/metadata-vectors.json`.

## Mapping to the current API

| Metadata field | Current source | Real value (default definition) |
|---|---|---|
| `generatorVersion` | `GeneratedModel.generator_version` | `"0.1.0"` |
| `definitionHash` | `GeneratedModel.definition_hash` | `"355ddca57e7e49ad"` |
| `generationTimestamp` | `ModelRecord.generated_at` (not on `GeneratedModel` itself) | ISO 8601 UTC, set once at generation |
| `generationDurationS` | `GeneratedModel.generation_duration_s` | `0.730515600182116` (this specific run; varies run to run — timing is not part of `definitionHash`) |
| `componentList` | `list(GeneratedModel.components.keys())` | `["band", "stone_reference", "prongs", "basket_support"]` |
| `componentVolumes` | `GeneratedModel.component_volumes()` | `band: 250.99...`, `stone_reference: 58.22...`, `prongs: 29.65...`, `basket_support: 83.16...` |
| `totalProductionMetalVolume` | `GeneratedModel.combined_metal_volume_mm3` | `341.44334316909976` |
| `boundingBoxes` | Per-component `.bounding_box`, plus `GeneratedModel.bounding_box` for the aggregate | See `metadata-vectors.json` |
| `componentCount` | `len(GeneratedModel.components)` | `4` |
| `requestedProngCount` / `generatedProngCount` | `definition.setting.prongCount` / `components["prongs"].metadata["generatedCount"]` | `6` / `6` |
| `fallbackRecords` | Not a separate list — a subset of `warnings`, distinguished only by message text, not a structured flag | `[]` for the default definition (no fallback triggered) |
| `warnings` | `GeneratedModel.warnings` | `[]` for the default definition |
| `inspectionResults` | **PLANNED** — not populated | n/a |

## Important non-obvious fact: production-metal volume is not a sum of component volumes

`totalProductionMetalVolume` (the fused `combined_metal`'s volume) is **not** the arithmetic sum of `band` + `prongs` + `basket_support`'s individually-reported volumes, because the fuse operation removes the overlapping `EMBED_MM`-deep regions used to guarantee genuine 3D contact. For the default definition: `250.99168317654699 + 29.650351464580467 + 83.15575842566426 = 363.7977930667917`, while `totalProductionMetalVolume = 341.44334316909976` — a difference of `22.35444989769195` mm³, the volume of mutual overlap consumed by the union. This is expected, documented behavior (see [`142-volume-and-bounding-box-inspection.md`](142-volume-and-bounding-box-inspection.md)), not a bug, and not previously stated anywhere in the Bible before this Sprint.

## `fallbackRecords` is not currently a distinct, structured list

Per this Sprint's honest-mapping requirement: there is no code path that tags a specific warning string as "this one is a fallback record" versus "this one is something else." Every fallback (fillet, fuse) happens to always populate `warnings` when triggered, so in practice `fallbackRecords` and `warnings` are currently identical whenever a fallback occurs — but this is not enforced by any type or schema, only by the fact that no other warning-generating code path currently exists in `geometry/`. A future structured `fallbackUsed: bool` + `fallbackReason: str` pair (as already modeled per-component in `specs/atlas/v1/geometry-component.schema.json`) would make this distinction real rather than incidental.
