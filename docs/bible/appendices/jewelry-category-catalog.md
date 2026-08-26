---
id: JM-BIBLE-A105
title: "Appendix: Jewelry Category Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-RING-README
  - JM-BIBLE-520
related_documents:
  - JM-BIBLE-534
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Jewelry Category Catalog

All 6 real `CategoryCapability` entries, read directly from
[`specs/jewelry-architecture/v1/category-registry.json`](../../../specs/jewelry-architecture/v1/category-registry.json)
(generated from
[`backend/jewelmind/jewelry_category/registry.py::CATEGORY_CAPABILITIES`](../../../backend/jewelmind/jewelry_category/registry.py),
never hand-maintained — JEWELRY-ARCH-GOV-015). Registry version `1.0.0`.

## `ring`

| Field | Value |
|---|---|
| `category` | `ring` |
| `status` | `current` |
| `definitionVersion` | `2.0.0` |
| `generationSupported` | `true` |
| `validationSupported` | `true` |
| `previewSupported` | `true` |
| `exportSupported` | `true` |
| `supportedFamilies` | `["solitaire"]` |
| `sharedSystems` | `["material", "manufacturing", "stone", "setting", "preview"]` |
| `categorySpecificSystems` | `["sizing", "shank", "shoulders", "head"]` |
| `message` | "Rings are fully supported." |

## `earring`

| Field | Value |
|---|---|
| `category` | `earring` |
| `status` | `planned` |
| `definitionVersion` | `0.0.0` |
| `generationSupported` | `false` |
| `validationSupported` | `false` |
| `previewSupported` | `false` |
| `exportSupported` | `false` |
| `supportedFamilies` | `[]` |
| `sharedSystems` | `["material", "manufacturing", "stone", "setting", "preview"]` |
| `categorySpecificSystems` | `[]` |
| `message` | "Earring is a recognized future jewelry category; generation is not yet supported." |

## `pendant`

| Field | Value |
|---|---|
| `category` | `pendant` |
| `status` | `planned` |
| `definitionVersion` | `0.0.0` |
| `generationSupported` | `false` |
| `validationSupported` | `false` |
| `previewSupported` | `false` |
| `exportSupported` | `false` |
| `supportedFamilies` | `[]` |
| `sharedSystems` | `["material", "manufacturing", "stone", "setting", "preview"]` |
| `categorySpecificSystems` | `[]` |
| `message` | "Pendant is a recognized future jewelry category; generation is not yet supported." |

## `bracelet`

| Field | Value |
|---|---|
| `category` | `bracelet` |
| `status` | `planned` |
| `definitionVersion` | `0.0.0` |
| `generationSupported` | `false` |
| `validationSupported` | `false` |
| `previewSupported` | `false` |
| `exportSupported` | `false` |
| `supportedFamilies` | `[]` |
| `sharedSystems` | `["material", "manufacturing", "stone", "setting", "preview"]` |
| `categorySpecificSystems` | `[]` |
| `message` | "Bracelet is a recognized future jewelry category; generation is not yet supported." |

## `necklace`

| Field | Value |
|---|---|
| `category` | `necklace` |
| `status` | `planned` |
| `definitionVersion` | `0.0.0` |
| `generationSupported` | `false` |
| `validationSupported` | `false` |
| `previewSupported` | `false` |
| `exportSupported` | `false` |
| `supportedFamilies` | `[]` |
| `sharedSystems` | `["material", "manufacturing", "stone", "setting", "preview"]` |
| `categorySpecificSystems` | `[]` |
| `message` | "Necklace is a recognized future jewelry category; generation is not yet supported." |

## `charm`

| Field | Value |
|---|---|
| `category` | `charm` |
| `status` | `planned` |
| `definitionVersion` | `0.0.0` |
| `generationSupported` | `false` |
| `validationSupported` | `false` |
| `previewSupported` | `false` |
| `exportSupported` | `false` |
| `supportedFamilies` | `[]` |
| `sharedSystems` | `["material", "manufacturing", "stone", "setting", "preview"]` |
| `categorySpecificSystems` | `[]` |
| `message` | "Charm is a recognized future jewelry category; generation is not yet supported." |

`ring` is the only entry with `status: "current"` and
`generationSupported: true` — verified live against the running Python
registry by `backend/tests/test_ring_architecture_schemas.py::test_category_registry_matches_the_real_capability_registry_live`
and `test_only_ring_is_generation_supported_in_the_registry`.
