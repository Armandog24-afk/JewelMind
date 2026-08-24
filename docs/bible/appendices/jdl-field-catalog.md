---
id: JM-BIBLE-A09
title: "Appendix: JDL Field Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-064
  - JM-BIBLE-073
related_documents:
  - JM-BIBLE-A06
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: JDL Field Catalog

Every field in `JDLDocumentV1` (= the current `JewelryDefinition`), cross-checked against `backend/jewelmind/domain/schema.py` and `shared/types/jewelry-definition.ts` during this Sprint. See [`04-jewelry-domain/appendices/jewelry-domain-parameter-catalog.md`](jewelry-domain-parameter-catalog.md) for the jewelry-meaning version of the same data; this table is the language/type version.

| Field (JSON path) | Type | Default | Class (see [`073`](../05-jdl/073-required-optional-default-and-derived-values.md)) | Pydantic | TypeScript |
|---|---|---|---|---|---|
| `schemaVersion` | Version | `"0.1.0"` | REQUIRED WITH DEFAULT | `Literal["0.1.0"]` | `string` |
| `project.name` | String | `"Solitaire Ring"` | REQUIRED WITH DEFAULT, METADATA | `str` (1–200 chars) | `string` |
| `project.units` | Enumeration | `"mm"` | REQUIRED WITH DEFAULT | `Literal["mm"]` | `'mm'` |
| `jewelry.category` | Enumeration | `"ring"` | REQUIRED WITH DEFAULT | `Literal["ring"]` | `'ring'` |
| `jewelry.style` | Enumeration | `"solitaire"` | REQUIRED WITH DEFAULT | `Literal["solitaire"]` | `'solitaire'` |
| `ring.sizeSystem` | Enumeration | `"EU"` | REQUIRED WITH DEFAULT | `Literal["EU"]` | `'EU'` |
| `ring.size` | Decimal | `16.0` | REQUIRED WITH DEFAULT | `float` | `number` |
| `ring.innerDiameter` | Dimension | `17.8` | REQUIRED WITH DEFAULT | `float` | `number` |
| `band.width` | Dimension | `2.4` | REQUIRED WITH DEFAULT | `float` | `number` |
| `band.thickness` | Dimension | `1.8` | REQUIRED WITH DEFAULT | `float` | `number` |
| `band.profile` | Enumeration | `"comfort_fit"` | REQUIRED WITH DEFAULT | `Literal["comfort_fit", "flat"]` | `BandProfile` |
| `stone.shape` | Enumeration | `"round"` | REQUIRED WITH DEFAULT | `Literal["round"]` | `'round'` |
| `stone.diameter` | Dimension | `6.5` | REQUIRED WITH DEFAULT | `float` | `number` |
| `stone.depth` | Dimension | `4.0` | REQUIRED WITH DEFAULT | `float` | `number` |
| `setting.type` | Enumeration | `"prong"` | REQUIRED WITH DEFAULT | `Literal["prong"]` | `'prong'` |
| `setting.prongCount` | Integer | `6` | REQUIRED WITH DEFAULT | `int` | `number` |
| `setting.prongDiameter` | Dimension | `1.1` | REQUIRED WITH DEFAULT | `float` | `number` |
| `setting.prongHeight` | Dimension | `4.8` | REQUIRED WITH DEFAULT | `float` | `number` |
| `setting.basketHeight` | Dimension | `3.5` | REQUIRED WITH DEFAULT | `float` | `number` |
| `material.metal` | Enumeration | `"yellow_gold_18k"` | REQUIRED WITH DEFAULT, METADATA | `Literal[...5 values]` | `MetalType` |
| `manufacturing.method` | Enumeration | `"lost_wax_casting"` | REQUIRED WITH DEFAULT, METADATA | `Literal["lost_wax_casting", "direct_resin_printing"]` | `ManufacturingMethod` |
| `preview.meshTolerance` | Decimal | `0.1` | REQUIRED WITH DEFAULT | `float` (`gt=0`) | `number` |
| `preview.angularTolerance` | Decimal (radians) | `0.2` | REQUIRED WITH DEFAULT | `float` (`gt=0`) | `number` |

**Total current fields catalogued: 23** (including `schemaVersion`). Every default value above was read directly from `backend/jewelmind/domain/schema.py` during this Sprint, not recalled from memory or estimated.
