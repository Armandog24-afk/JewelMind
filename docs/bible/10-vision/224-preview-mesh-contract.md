---
id: JM-BIBLE-224
title: Preview Mesh Contract (Vision)
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-144
related_documents:
  - JM-BIBLE-223
implementation_status: current
professional_validation: not_required
normative: true
---

# Preview Mesh Contract (Vision)

This restates [`07-atlas/144-preview-mesh-contract.md`](../07-atlas/144-preview-mesh-contract.md) from Vision's consuming side, without duplicating its normative content.

## The real pipeline, confirmed by inspection this Sprint

```
Atlas B-Rep (cq.Shape, per component)
  -> shape.exportStl(tolerance, angularTolerance)          [backend/jewelmind/preview/mesh.py]
  -> binary STL file, one per component, in a temp directory
  -> served via GET /api/models/{model_id}/preview/{component_name}
  -> fetch() + STLLoader().parse(arrayBuffer)                [frontend/src/hooks/useComponentGeometries.ts]
  -> THREE.BufferGeometry
  -> Vision scene (ModelViewport.tsx)
```

## STL is genuinely used for preview today — confirmed, not assumed

`preview/mesh.py`'s own docstring states plainly: "GLB packaging was evaluated and intentionally not used in this milestone." This Sprint did not change that decision — STL remains the real, current preview transport, and this document does not pretend a GLB pipeline exists. See [`247-vision-gap-analysis.md`](247-vision-gap-analysis.md) for GLB as a named, unimplemented future option.

## Preview mesh is derived, never a source of truth

Restating ATLAS-GOV-013/FOUNDRY-GOV-013 at the Vision layer: the browser never treats a previously-loaded `BufferGeometry` as authoritative — every `generate()` call fetches fresh STL files, and `useComponentGeometries()` disposes the old geometry set only once the new one has fully loaded (never before), so a failed reload can never silently substitute stale geometry for what the backend now considers current.

## Nothing is generated in the browser

No frontend code calls a tessellation, boolean, or mesh-construction routine. The only computation Vision performs on geometry is reading `BufferGeometry` attributes already produced by `STLLoader.parse()` — restating VISION-GOV-001/002.
