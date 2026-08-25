---
id: JM-BIBLE-231
title: Material System
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-220
related_documents:
  - JM-BIBLE-232
  - JM-BIBLE-233
  - JM-BIBLE-A43
implementation_status: current
professional_validation: not_required
normative: true
---

# Material System

## Resolution pipeline

```
JewelryDefinition.material.metal (JDL, e.g. "platinum")
  -> resolveComponentMaterial(isStone, metal, viewMode)     [frontend/src/vision/materials.ts]
  -> ResolvedComponentMaterial (color, metalness, roughness, opacity, transmission, ior, thickness, clearcoat, envMapIntensity)
  -> <meshPhysicalMaterial {...} />                          [frontend/src/components/ComponentMesh.tsx]
```

`isStone` comes from the component's explicit `geometryRole` (see [`226-component-visual-identity.md`](226-component-visual-identity.md)), `metal` from the live `JewelryDefinition`, and `viewMode` from `useVisionStore`. No other module resolves a material independently.

## Centralization, enforced by construction

`frontend/src/vision/materials.ts` is the **only** file in the frontend that contains a metal hex color or the stone's color. `ComponentMesh.tsx` accepts fully-resolved numeric/string parameters and has no preset table of its own; `ModelViewport.tsx` never hardcodes a color, always calling `resolveComponentMaterial()`. This is verified structurally (one file, one set of exported presets) and by `materials.test.ts`, which asserts all 5 metals resolve to visibly distinct colors in both view modes.

## No claim of optical accuracy

Every value in `materials.ts` — metalness, roughness, transmission, ior — is a chosen visual approximation for on-screen legibility, not a measured or spectrally-accurate material property for any real alloy or gemstone. This is stated in the module's own doc-comment and restated here per VISION-GOV-005's spirit (extended from manufacturability to optical-accuracy claims generally).

## One material type for both metal and stone

`ComponentMesh` always renders `meshPhysicalMaterial` — a superset of the standard PBR material — rather than switching material *types* between metal (opaque) and stone (transmissive). Passing `transmission: 0` (metal's case) makes it behave identically to a plain metallic material; passing a nonzero `transmission` (stone's presentation case) activates the transmissive look. This was a deliberate simplification adopted mid-implementation after an initial `'field' in material` type-narrowing approach proved fragile under TypeScript's `exactOptionalPropertyTypes` setting — replaced with `resolveComponentMaterial()` returning one fully-populated shape for every call, with stone-only fields defaulted to neutral values for metal.
