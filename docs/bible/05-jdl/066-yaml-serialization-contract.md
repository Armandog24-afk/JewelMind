---
id: JM-BIBLE-066
title: YAML Serialization Contract (Planned)
version: 1.0.0
status: draft
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-065
related_documents:
  - JM-BIBLE-JDL-README
implementation_status: planned
professional_validation: not_required
normative: true
---

# YAML Serialization Contract (Planned)

**Status: PLANNED, NON-NORMATIVE as a representation. No YAML parser or loader exists anywhere in this codebase today.** The restrictions below ARE normative in the sense that a future implementation must follow them — this document is written now specifically so a future implementer cannot pick unsafe YAML defaults (arbitrary tags, implicit type coercion) and call it JDL-compliant.

## Why YAML at all

YAML would give human authors comment support and a less punctuation-heavy authoring experience than JSON, while still deserializing to the exact same `JDLDocumentV1` shape (see [`064-canonical-document-model.md`](064-canonical-document-model.md)). It is not a different language — it is an alternate *serialization* of the same Canonical JSON structure.

## Required restrictions (safe-YAML subset only)

1. **No executable tags.** `!!python/object`, `!!python/module`, or any language-specific constructor tag is rejected outright — a conforming loader must be equivalent to `yaml.safe_load`, never `yaml.load` with the default (unsafe) loader.
2. **No custom constructors.** A JDL YAML loader defines zero custom tags; only the standard safe scalar/sequence/mapping tags are recognized.
3. **No implicit date conversion.** A bare `2026-08-24`-shaped scalar must remain a string, not become a YAML timestamp object — nothing in `JDLDocumentV1` is a date.
4. **No anchors that change meaning.** YAML anchors/aliases (`&name` / `*name`) may be used purely as a textual convenience for repeated values, but must never produce a document whose meaning differs from writing the value out in full — an implementation must resolve them before interpreting the JDL fields.
5. **No merge keys** (`<<:`) unless the loader normalizes the result to a flat mapping identical to writing the fields out directly — no merge-key-dependent field resolution order.
6. **No duplicate keys** — a YAML mapping with a repeated key at the same level must be rejected, not silently resolved to the last value (unlike current JSON parsing behavior, which is JSON's own well-known last-value-wins rule and is not being changed).
7. **No non-finite values** — YAML's `.inf`, `-.inf`, `.nan` scalars must be rejected with the same `JDL-SCHEMA-*` diagnostic a JSON `Infinity` token would produce (see [`specs/jdl/v1/canonicalization.md`](../../../specs/jdl/v1/canonicalization.md) "Known limitation").

## Informative, non-normative example

This shows the *shape* a YAML JDL document would take. **It is not currently accepted by the API.**

```yaml
# Informative example only — NOT accepted by the current API.
schemaVersion: "0.1.0"
project:
  name: Solitaire Ring
  units: mm
ring:
  sizeSystem: EU
  size: 16.0
  innerDiameter: 17.8
band:
  width: 2.4
  thickness: 1.8
  profile: comfort_fit
```

## Relationship to Canonical JSON

A conforming YAML loader must produce, after parsing and default-filling, a value that canonicalizes (per [`065-canonical-json-serialization.md`](065-canonical-json-serialization.md)) identically to the equivalent JSON document. YAML is a convenience *representation*; it introduces no new fields, no new defaults, and no new semantics.
