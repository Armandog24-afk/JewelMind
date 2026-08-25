---
id: JM-BIBLE-A45
title: "Appendix: Vision Diagnostic Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-241
related_documents: []
implementation_status: planned
professional_validation: not_required
normative: true
---

# Appendix: Vision Diagnostic Catalog

Restates [`10-vision/241-rendering-errors-and-diagnostics.md`](../10-vision/241-rendering-errors-and-diagnostics.md)'s table as a standalone reference. **0 of 9 codes are implemented as distinct, named error types today.**

| Conceptual code | Implemented? | Real current behavior |
|---|---|---|
| `VISION_MESH_LOAD_FAILED` | No | Generic `catch` in `useComponentGeometries`, sets `hasError` |
| `VISION_MESH_PARSE_FAILED` | No | Same `catch`, indistinguishable from load failure |
| `VISION_WEBGL_UNAVAILABLE` | No | Unhandled — fails inside R3F itself |
| `VISION_RENDER_FAILED` | No | No error boundary around `<Canvas>` |
| `VISION_CAMERA_FAILED` | No | Silent no-op guard in `applyPose()` |
| `VISION_CAPTURE_FAILED` | No | Silent `if (blob)` check, no user-facing message on `null` |
| `VISION_COMPONENT_MISSING` | No | Component simply does not render |
| `VISION_MATERIAL_FALLBACK` | No | Silent fallback to `yellow_gold_18k` |
| `VISION_GPU_RESOURCE_ERROR` | No | No `webglcontextlost` handler |
