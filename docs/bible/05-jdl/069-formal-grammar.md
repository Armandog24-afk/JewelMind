---
id: JM-BIBLE-069
title: Formal Grammar (Planned DSL)
version: 1.0.0
status: draft
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-068
related_documents:
  - JM-BIBLE-067
implementation_status: planned
professional_validation: not_required
normative: false
---

# Formal Grammar (Planned DSL)

**Status: PLANNED, NON-NORMATIVE. Grammar only — no parser exists or is built in this milestone.**

The full grammar lives in [`specs/jdl/v1/jdl.ebnf`](../../../specs/jdl/v1/jdl.ebnf) (ISO/IEC 14977 EBNF), not duplicated here. This document is the narrative companion.

## Scope discipline

The grammar covers exactly the current solitaire schema surface: one `jdl-document` production, one project declaration, one ring declaration (style fixed to `solitaire`), one band/stone/setting/material/manufacturing/preview declaration each, matching `JDLDocumentV1` field-for-field (see [`064-canonical-document-model.md`](064-canonical-document-model.md)). It adds no new ring style, stone shape, or setting type.

## Reserved extension points

The grammar marks the following alternatives as deliberately extensible without a breaking grammar change, each commented `(* RESERVED EXTENSION POINT *)` in `jdl.ebnf`:

- `style-literal` (ring styles beyond `solitaire`)
- `size-system-literal` (ring sizing systems beyond `EU`)
- `band-profile-literal` (band profiles beyond `comfort_fit` / `flat`)
- `stone-role-literal` (stone roles beyond `center` — e.g. a future side-stone)
- `stone-shape-literal` (stone shapes beyond `round`)
- `setting-type-literal` (setting types beyond `prong`)
- `metal-literal` (metals beyond the current five)
- `method-literal` (manufacturing methods beyond the current two)

A reserved extension point is a place in the grammar where a future alternative can be added without changing any other production — it is not itself a working rule, and none of the placeholder alternatives are implemented, accepted, or parseable today.

## Verifying internal consistency

Every production in `jdl.ebnf` either terminates in a literal/lexical rule or references another named production defined in the same file — there is no forward reference to an undefined name and no unreachable production. This was checked by hand during Sprint 3 (no EBNF-checking tool was introduced, since no parser exists to validate against); a future implementer building a real parser should treat a parser-generator's own grammar-load step as the authoritative check going forward.

## What this document explicitly does not do

It does not specify parser implementation strategy (recursive descent, parser combinator, generated parser, etc.) — that decision is deferred to whichever future sprint actually builds the parser, and is out of scope for a grammar-only milestone.
