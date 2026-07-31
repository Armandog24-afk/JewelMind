---
id: JM-BIBLE-ADR-009
title: "ADR-009: Millimeter-only coordinate/unit system"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-004
  - JM-BIBLE-007
implementation_status: current
---

# ADR-009: Millimeter-only coordinate/unit system

## Status

Accepted.

## Context

Jewelry dimensions are conventionally specified in millimeters
worldwide. A system that supported multiple units, or left units
ambiguous, would risk a class of error (wrong-unit dimensions reaching
manufacturing) that is both easy to introduce and hard to catch visually.

## Decision

Every length field, everywhere in JewelMind — schema, geometry,
export, UI — is millimeters. There is no unit field to select and no
conversion code path. `project.units` is a fixed `Literal["mm"]`, not a
user choice. The coordinate convention itself (band revolve axis,
assembly anchor point) is documented once in
`docs/geometry-conventions.md` and followed consistently by geometry,
preview, tests, and metadata.

## Alternatives considered

- **Supporting multiple units with conversion.** Rejected: unit
  conversion is a well-known source of silent, catastrophic bugs (a
  classic engineering failure mode); with only one target audience
  (millimeter-native jewelry work) the complexity was judged to have no
  corresponding benefit.
- **Leaving units unspecified/implicit.** Rejected: ambiguity is worse
  than a single fixed convention — this is exactly the failure mode a
  fixed unit avoids.
- **Millimeters only, fixed and explicit everywhere (the chosen path).**
  Selected.

## Positive consequences

- No possibility of a unit-mismatch bug — there is only one unit.
- Every dimension in every export, in every UI field, and in the
  technical specification is directly comparable without conversion.
- Coordinate convention documentation
  (`docs/geometry-conventions.md`) has one less axis of variation to
  cover.

## Negative consequences

- A user working in inches must convert externally before entering
  values — no accommodation is made for this within the product.

## Risks

- Adding a new length parameter without following the millimeter
  convention would silently violate this decision — guarded by
  [LAW-007](../00-foundation/004-jewelmind-constitution.md#LAW-007) and
  code review, not by an automated unit-checker.

## Review trigger

Revisit only if a genuinely required use case demands another unit
system — this would need a new ADR given how many other decisions
(schema, geometry, export) assume millimeters throughout.

## Related implementation files

`backend/jewelmind/domain/schema.py` (`ProjectInfo.units: Literal["mm"]`),
`backend/jewelmind/geometry/constants.py`,
`docs/geometry-conventions.md`.

## Related tests

Indirectly, every geometry test in `test_geometry.py` asserts millimeter-
scale bounding boxes/volumes consistent with the documented convention.
