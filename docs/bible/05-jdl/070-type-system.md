---
id: JM-BIBLE-070
title: Type System
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-064
related_documents:
  - JM-BIBLE-071
  - JM-BIBLE-072
implementation_status: partial
professional_validation: not_required
normative: true
---

# Type System

Every JDL type below is named at the language level, then mapped onto its current concrete representations. A row marked "N/A" means the current schema has no field of that conceptual type — it is listed because a future field might need it, not because one exists.

| JDL type | JSON | Pydantic | TypeScript | Future DSL | Example field |
|---|---|---|---|---|---|
| Document | object | `JewelryDefinition` (root model) | `JewelryDefinition` (root interface) | `jdl-document` | the whole document |
| Object | object | nested `StrictModel` subclass | nested interface | named block (`band { }`) | `band`, `stone`, `setting` |
| String | string | `str` | `string` | quoted string literal | `project.name` |
| Identifier | N/A (strings serve this role in JSON) | N/A | N/A | bareword identifier | reserved for future DSL block names |
| Enumeration | string | `Literal[...]` | string union | bareword keyword | `band.profile`, `material.metal` |
| Boolean | N/A | N/A | N/A | N/A | no boolean field exists in `JewelryDefinition` today; not added speculatively |
| Integer | number (no fractional part) | `int` | `number` | integer literal | `setting.prongCount` |
| Decimal | number | `float` (`allow_inf_nan=False`) | `number` | numeric literal | `ring.size`, `band.width` |
| Dimension | number, implicitly millimeters | `float` | `number` | numeric literal, optional `mm` suffix | `band.thickness`, `stone.diameter` |
| Angle | N/A as a distinct type — `preview.angularTolerance` is a `Decimal` in radians, not a dedicated Angle type | `float` | `number` | numeric literal | `preview.angularTolerance` — see [`071-units-and-numeric-model.md`](071-units-and-numeric-model.md) for why this is not elevated to its own type in v1 |
| Version | string, exact literal match | `Literal["0.1.0"]` | `string` (loosely typed; runtime guard checks equality) | version literal (`jdl 1.0`) | `schemaVersion` |
| URI | N/A | N/A | N/A | N/A | no URI-typed field exists; not added speculatively — JDL documents reference no external resource (see [`062-design-goals-and-non-goals.md`](062-design-goals-and-non-goals.md) non-goal 2) |
| Collection | N/A | N/A | N/A | N/A (grammar has no array/list production) | no array-typed field exists in the current schema |
| Domain reference | N/A | N/A | N/A | N/A | fields like `band.profile` reference a jewelry-domain concept but are represented as plain Enumerations, not a distinct reference type |
| Diagnostic | object, external to the document itself | `ValidationResult` | not currently mirrored as a TS type (frontend re-derives its own messages; see [`04-jewelry-domain/055-domain-to-code-mapping.md`](../04-jewelry-domain/055-domain-to-code-mapping.md)) | N/A | a `JM-BAND-001` result |
| Generated artifact descriptor | object, external to the document itself | `GeneratedComponent` (partial fit — see [`078-geometry-generation-contract.md`](078-geometry-generation-contract.md)) | not currently mirrored | N/A | a component manifest entry |

## Notes on deliberately absent types

- **Boolean**: the schema has no boolean field; `includeStoneReference` (a real boolean) exists only as an *export request parameter*, not as a field inside `JewelryDefinition` itself — see [`079-artifact-generation-contract.md`](079-artifact-generation-contract.md). It is not listed as a JDL document type because it is not part of the document.
- **URI**: deliberately excluded per non-goal 2 in [`062-design-goals-and-non-goals.md`](062-design-goals-and-non-goals.md) — a JDL document must never carry a reference the compiler would need to fetch.
- **Collection**: no array field exists; when one is eventually needed (e.g. multiple accent stones), array-order semantics must be defined at that time in [`065-canonical-json-serialization.md`](065-canonical-json-serialization.md), not assumed now.

## Angle as a type, explicitly

`preview.angularTolerance` is the only angle-shaped value in the current schema, and it is **radians**, confirmed by inspecting the installed CadQuery source (`Shape.mesh()` passes it straight into OCCT's `BRepMesh_IncrementalMesh`, which documents its angular-deflection parameter in radians). It is modeled here as a plain Decimal rather than a distinct Angle type because nothing in the current schema needs angle arithmetic or unit conversion between degrees and radians — introducing a distinct type now would be speculative. See [`071-units-and-numeric-model.md`](071-units-and-numeric-model.md) for the full numeric-model discussion.
