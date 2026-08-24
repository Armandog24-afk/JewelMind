---
id: JM-BIBLE-082
title: Extension and Capability Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-081
related_documents:
  - JM-BIBLE-060
  - JM-BIBLE-056
implementation_status: planned
professional_validation: not_required
normative: true
---

# Extension and Capability Model

**Nothing in this document is implemented today.** `backend/jewelmind/domain/schema.py` enforces `extra="forbid"` on every model — there is no experimental-field namespace, no capability-declaration endpoint, and no plugin mechanism in the current codebase. This document defines the *preferred shape* such a mechanism should take if and when one is built, so it is not invented ad hoc under time pressure later.

## Preferred approach, in order

1. **Versioned official fields** — the default path for anything that reaches consensus: add the field to `schema.py` and `jewelry-definition.ts` together, bump `schemaVersion` per [`081-schema-versioning-and-migrations.md`](081-schema-versioning-and-migrations.md).
2. **Declared capabilities** — a server/client can advertise what it supports (see the conceptual shape below) so a caller knows ahead of time whether a given ring style, stone shape, setting type, or export format will be accepted, rather than discovering it via a rejected request.
3. **Namespaced experimental extensions** — a hypothetical future `x-<vendor>-<feature>` field, explicitly out-of-schema, ignored by strict validation, and never influencing geometry unless promoted to an official field first (see JDL-GOV-006 — unknown fields must never silently alter geometry).
4. **Explicit unsupported-feature errors** — a request for something not supported gets a specific, catalogued diagnostic (a new `JM-SYSTEM-*` or `JM-DOMAIN-*` code), never a silent fallback to a different, unrequested behavior.

This ordering exists specifically to avoid uncontrolled arbitrary fields: a namespaced experimental field (option 3) is a last resort, not a default way to add functionality.

## Conceptual capability-declaration shape (not implemented)

```
CapabilityDeclaration {
  supportedSchemaVersions: ["0.1.0"]
  supportedJewelryCategories: ["ring"]
  supportedRingStyles: ["solitaire"]
  supportedStoneShapes: ["round"]
  supportedSettingTypes: ["prong"]
  supportedExportFormats: ["step", "stl", "json", "specification"]
}
```

Every value in this illustrative declaration is exactly what the current backend already supports — this document does not enable an experimental namespace or advertise a capability the code doesn't already have. Building this declaration as a real, callable API endpoint is future work, not part of this Sprint.

## What this document explicitly does not do

- It does not add a new ring style, stone shape, setting type, component, material dataset, manufacturing context, exporter, preview format, or validation profile.
- It does not open an experimental-namespace field in the current schema — `extra="forbid"` remains unchanged.
- It does not commit to when or whether this mechanism is built — that is future-sprint scope, gated by an RFC/ADR per [`060-jdl-governance.md`](060-jdl-governance.md) if and when a second ring style or stone shape is actually proposed.
