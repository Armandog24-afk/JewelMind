---
id: JM-BIBLE-303
title: Field Provenance Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-302
related_documents:
  - JM-BIBLE-304
implementation_status: current
professional_validation: not_required
normative: true
---

# Field Provenance Model

## Why this is the single most safety-critical model in Sprint 10

Every other Designer model can be wrong without doing much harm — a bad confidence label, a missing diagnostic, a plain UX inconvenience. Provenance is different: it is the only signal that stops an AI guess from being indistinguishable from an ordinary system default or a value the user typed themselves. If provenance were ever wrong or optional, a user could apply a proposal believing a value came from their own words when it was actually inferred, without any review surface telling them so. That is exactly what DESIGNER-GOV-006, DESIGNER-GOV-007, and DESIGNER-GOV-011 exist to prevent.

## The 8-value `FieldProvenance` enum

`designer/schemas.py::FieldProvenance` is `Literal["USER_EXPLICIT", "USER_CONTEXT", "CURRENT_DESIGN", "SYSTEM_DEFAULT", "DETERMINISTIC_DERIVATION", "AI_INTERPRETATION", "CLARIFICATION_RESPONSE", "UNRESOLVED"]`. `ProposedField.provenance` is required, not optional — there is no `ProposedField` construction anywhere in `designer/service.py` that omits it (DESIGNER-GOV-011).

## What current code actually assigns

Grepping `service.py` for `provenance=` shows exactly three call sites, all in `_build_proposal()`, and all three assign the identical literal `"AI_INTERPRETATION"`:

1. The enum-field branch (normalized or exact synonym match).
2. The `project.name` branch.
3. The numeric-field branch.

Every `ProposedField` Designer v1 has ever produced — across all 62 corpus cases, all unit tests, all schema examples — carries `provenance: AI_INTERPRETATION`. This is intentional and honest: everything Designer currently proposes did, in fact, come from interpreting the request text through a provider (real or `FakeDesignerProvider`), so a single provenance value is the accurate description of the current pipeline, not a shortcut around the model.

## The other 7 values exist for schema completeness and future use

- `USER_EXPLICIT` / `USER_CONTEXT` would distinguish a value the user typed directly from one Designer inferred from surrounding context — a distinction the current pipeline does not attempt to make; everything from the provider is treated uniformly as `AI_INTERPRETATION`.
- `CURRENT_DESIGN` would mark a field carried forward unchanged from `currentJDL` on a `MODIFY` — but unspecified fields are never re-emitted as `ProposedField`s at all today (see `_apply_patch`, which only touches paths present in `patch`); they simply remain in the candidate JDL without a corresponding `ProposedField` entry.
- `SYSTEM_DEFAULT` mirrors `DEFAULTED` confidence's gap (see [`302-confidence-model.md`](302-confidence-model.md)) — Designer never surfaces a system default as a proposed field.
- `DETERMINISTIC_DERIVATION` would describe a value computed from another field by JewelMind's own code, not the provider — no such derivation exists in the current pipeline.
- `CLARIFICATION_RESPONSE` would mark a value that arrived via a clarification answer — see [`300-clarification-policy.md`](300-clarification-policy.md) for the confirmed gap: a clarified answer is reprocessed as an ordinary new request and gets `AI_INTERPRETATION` like everything else.
- `UNRESOLVED` would mark a field Designer could not resolve at all — in current code an unresolved field becomes either a `ClarificationQuestion`, an `UnsupportedFeature`, or a plain string in `unresolvedIntent`, never a `ProposedField`.

None of this is a defect to silently patch away; it is an accurate map of where the implementation currently is versus where the type deliberately leaves room to grow. See [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md) and the appendix [`designer-field-provenance-catalog.md`](../appendices/designer-field-provenance-catalog.md).
