---
id: JM-BIBLE-ADR-005
title: "ADR-005: Canonical JewelryDefinition schema"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-013
  - JM-BIBLE-026
implementation_status: current
---

# ADR-005: Canonical `JewelryDefinition` schema

## Status

Accepted.

## Context

Every layer of the system (form, validation, geometry, export, storage)
needs to agree on exactly what a "ring definition" is. Without one
canonical shape, the frontend, backend, and stored/exported files could
each drift toward slightly different representations.

## Decision

Define one canonical `JewelryDefinition` shape, authoritative in
`backend/jewelmind/domain/schema.py` (Pydantic v2, strict, `extra="forbid"`),
mirrored by hand in `shared/types/jewelry-definition.ts` for the frontend.
This shape is what is validated, generated from, hashed, persisted to
`localStorage`, and exported as JSON — the same structure, everywhere.

## Alternatives considered

- **Separate, loosely-related types per layer** (a form-state shape, a
  wire-format shape, a geometry-input shape). Rejected: guarantees drift
  and mapping bugs between layers.
- **Generating the TypeScript type from the Pydantic schema (codegen).**
  Considered; not adopted for the MVP given the schema's current size —
  documented as a known limitation
  ([`026-known-technical-limitations.md`](../02-architecture/026-known-technical-limitations.md))
  and a plausible next step, not a rejected idea.
- **One canonical schema, hand-mirrored (the chosen path).** Selected —
  practical for the current schema size, with the risk (manual sync)
  explicitly documented rather than ignored.

## Positive consequences

- `definitionHash` is meaningful precisely because there is one canonical
  serialization to hash (`utils/hashing.py`).
- Adding a field is a single, well-understood change: schema field +
  default + (if applicable) a validation rule — see Product Principle 1.
- The same shape flows unmodified from form to `localStorage` to the
  wire to the backend to geometry to export — no translation layer to
  get wrong.

## Negative consequences

- The Python and TypeScript definitions must be updated together by hand;
  forgetting one side is a real, if currently manually-caught, risk.
- `strict=True` type coercion rejection (a hardening addition — see
  `AUDIT_FIXES.md` §1) means any future field must be added with the same
  numeric-safety care (`allow_inf_nan=False` where relevant).

## Risks

- Schema growth without codegen increases the manual-sync burden
  described above.

## Review trigger

Revisit the hand-mirrored approach if schema changes become frequent
enough that sync mistakes start recurring — see
[ADR-004](ADR-004-backend-authoritative-validation.md)'s equivalent
review trigger for the validation engines, which would likely be revisited
together.

## Related implementation files

`backend/jewelmind/domain/schema.py`, `shared/types/jewelry-definition.ts`.

## Related tests

`backend/tests/test_schema.py` (3 tests),
`backend/tests/test_schema_safety.py` (70 tests).
