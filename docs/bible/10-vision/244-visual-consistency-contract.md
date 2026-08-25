---
id: JM-BIBLE-244
title: Visual Consistency Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-220
related_documents:
  - JM-BIBLE-003
implementation_status: current
professional_validation: not_required
normative: true
---

# Visual Consistency Contract

## The most important product guarantee

**The object shown in Vision must be derived from the same generated geometry used for exports.** Every mesh in `ModelViewport.tsx` is parsed from the identical STL bytes `exporters/step_exporter.py`/`stl_exporter.py` would tessellate from — restating VISION-GOV-003 as the single guarantee everything else in this document decomposes into.

## The 5 consistency levels

| Level | Meaning | Status |
|---|---|---|
| `GEOMETRY_SOURCE_CONSISTENT` | Vision's mesh and Foundry's STEP/STL come from the same `GeneratedModel` | **CURRENT** — both are produced from one `ModelService.generate()` call; Vision consumes the preview STL, Foundry consumes `combined_metal`/`stone_reference` shapes directly, but both trace to the identical Atlas construction |
| `COMPONENT_SET_CONSISTENT` | The same 4 named components exist in both the visual scene and any export | **CURRENT** — `band`/`prongs`/`basket_support`/`stone_reference`, identical names, identical `geometryRole` classification (this Sprint's addition made this explicit rather than merely coincidental) |
| `SCALE_CONSISTENT` | 1 Vision scene unit = 1mm, matching STEP/STL's millimeter contract | **CURRENT** — Vision applies only a rotation, never a scale, to the geometry it receives; confirmed by inspection of the single `<group rotation=...>` transform, which has no accompanying `scale` prop |
| `MATERIAL_METADATA_CONSISTENT` | The metal shown in Presentation mode matches the JDL-selected metal | **CURRENT** — `resolveComponentMaterial()` always reads `definition.material.metal` live; there is no way to preview a different metal than the one currently selected in the configuration panel |
| `CAMERA_ONLY_TRANSFORMATION` | Every visual customization (camera, lighting, material style) is a presentation-layer transform, never a geometry change | **CURRENT** — restating [`235-shadows-and-grounding.md`](235-shadows-and-grounding.md)'s "camera may move; geometry coordinate truth must remain unchanged" |

## Presentation styling changes appearance, never shape

Switching view mode, metal, or camera preset never alters a single vertex of the `BufferGeometry` being rendered — every one of those changes is a material-parameter, light, camera, or scene-background change layered on top of an unchanged mesh. This is verified two ways: structurally (no Vision code path calls a geometry-mutating Three.js method — no `.applyMatrix4()`, no vertex-attribute rewrite) and behaviorally (`useVisionStore.test.ts` confirms view-mode/visibility changes never touch `useProjectStore`, which is the only place a new `GeneratedModel`/mesh fetch could originate from).

## Verified this Sprint, concretely

`backend/tests/test_export_integrity.py` and the full backend suite (194 tests) were re-run after this Sprint's backend metadata addition (`geometryRole` etc. in `preview/mesh.py`) and passed unchanged — confirming the new Vision-facing metadata is genuinely additive and does not alter STEP/STL bytes, satisfying VISION-GOV-015 concretely rather than by assertion alone.
