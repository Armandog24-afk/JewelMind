---
id: JM-BIBLE-181
title: Compiler Capability Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-162
related_documents:
  - JM-BIBLE-082
implementation_status: planned
professional_validation: not_required
normative: true
---

# Compiler Capability Model

The normative shape is `specs/alchemist/v1/compiler-capabilities.schema.json`; the real, current capability set is in `specs/alchemist/v1/test-vectors/capability-vectors.json`, populated by reading `backend/jewelmind/domain/schema.py`'s `Literal` types and `api/routes.py`'s actual endpoints directly during this Sprint.

## No capability-declaration endpoint exists

Restates and extends Sprint 3's [`05-jdl/082-extension-and-capability-model.md`](../05-jdl/082-extension-and-capability-model.md) at the compiler level — no such endpoint has been added since Sprint 3, and none is added now.

## Current capabilities, accurately

`supportedJDLVersions: ["0.1.0"]`, `supportedJewelryCategories: ["ring"]`, `supportedStyles: ["solitaire"]`, `supportedBandProfiles: ["comfort_fit", "flat"]`, `supportedStoneShapes: ["round"]`, `supportedSettings: ["prong"]`, `supportedProngCounts: [4, 6]`, `supportedArtifacts: ["PREVIEW_MESH", "STEP", "STL", "JSON", "TECHNICAL_SPECIFICATION"]`, `supportedManufacturingContexts: ["lost_wax_casting", "direct_resin_printing"]`, `supportedPreviewFormats: ["STL"]`.

## No roadmap value marked supported

Per this Sprint's explicit instruction, and cross-checked by `backend/tests/test_alchemist_registry.py::test_capability_vectors_match_live_schema_enums` (which asserts the vector file's lists exactly equal the real `Literal` type arguments in `schema.py`), nothing PLANNED or VISION appears in `currentCapabilities` — GLB preview, additional ring styles, additional stone shapes, and additional prong counts are all explicitly listed under `notSupported` instead.
