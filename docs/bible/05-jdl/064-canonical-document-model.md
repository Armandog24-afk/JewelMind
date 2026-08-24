---
id: JM-BIBLE-064
title: Canonical Document Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-063
related_documents:
  - JM-BIBLE-070
  - JM-BIBLE-A09
implementation_status: current
professional_validation: not_required
normative: true
---

# Canonical Document Model

## Conceptual `JDLDocumentV1` root type

```
JDLDocumentV1 {
  schemaVersion: "0.1.0"
  project:       ProjectInfo
  jewelry:       JewelryInfo
  ring:          RingSpec
  band:          BandSpec
  stone:         StoneSpec          // reference geometry only — see LAW-006
  setting:       SettingSpec
  material:      MaterialSpec
  manufacturing: ManufacturingSpec
  preview:       PreviewSpec
}
```

Every nested type name above (`ProjectInfo`, `JewelryInfo`, ...) is the literal Pydantic class name in `backend/jewelmind/domain/schema.py` and the literal TypeScript interface name in `shared/types/jewelry-definition.ts`. This document does not rename anything for presentation purposes.

## Conclusion: is `JewelryDefinition` equivalent to `JDLDocumentV1`?

**Equivalent.** `backend/jewelmind/domain/schema.py::JewelryDefinition` *is* `JDLDocumentV1` as implemented today — there is no field in the conceptual model above that the code lacks, and no field in the code that this model omits. `JDLDocumentV1` is introduced as a name so future JDL documents (this Bible section, `specs/jdl/v1/`, and any future non-Python/non-TypeScript implementation) have a representation-neutral term to refer to, rather than binding the language definition to one language's class name.

## Field groups and their role

| Group | Fields | Role |
|---|---|---|
| `schemaVersion` | — | Version gate; see [`081-schema-versioning-and-migrations.md`](081-schema-versioning-and-migrations.md) |
| `project` | `name`, `units` | Metadata; `units` is a fixed literal (`"mm"`), never user-chosen |
| `jewelry` | `category`, `style` | Classification; both fixed literals today (`"ring"`, `"solitaire"`) — see [`04-jewelry-domain/041-jewelry-product-taxonomy.md`](../04-jewelry-domain/041-jewelry-product-taxonomy.md) |
| `ring` | `sizeSystem`, `size`, `innerDiameter` | Geometry-driving |
| `band` | `width`, `thickness`, `profile` | Geometry-driving |
| `stone` | `shape`, `diameter`, `depth` | Geometry-driving, but the resulting solid is a **reference**, never fused into production metal (LAW-006) |
| `setting` | `type`, `prongCount`, `prongDiameter`, `prongHeight`, `basketHeight` | Geometry-driving |
| `material` | `metal` | Metadata/validation-context only — does not currently affect geometry (see [`04-jewelry-domain/052-parametric-dependency-model.md`](../04-jewelry-domain/052-parametric-dependency-model.md)) |
| `manufacturing` | `method` | Metadata/validation-context only — affects which semantic rules fire (`JM-MANUFACTURING-001`), not geometry shape |
| `preview` | `meshTolerance`, `angularTolerance` | Tessellation-only parameters; affect the preview/export mesh, not the underlying B-Rep solid |

## Why this document exists separately from the Sprint 2 domain model

[`04-jewelry-domain/044-solitaire-domain-model.md`](../04-jewelry-domain/044-solitaire-domain-model.md) describes the solitaire ring as a *jewelry concept* (what a band, a setting, a basket mean to a jeweler). This document describes the same information as a *data type* — its exact shape, field names, and nesting, the way a schema author or a serializer needs it. The two must stay consistent; where they overlap, this document defers to Sprint 2 for jewelry meaning and only adds language-level structure.

## What this document is not

It is not a new schema. It does not add, remove, or rename a single field relative to `backend/jewelmind/domain/schema.py`. Any apparent addition (like the `JDLDocumentV1` name itself) is purely a naming convenience for this specification, with zero runtime effect.
