---
id: JM-BIBLE-ADR-006
title: "ADR-006: Stone reference separated from production metal"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-004
  - JM-BIBLE-022
implementation_status: current
---

# ADR-006: Stone reference separated from production metal

## Status

Accepted.

## Context

A solitaire ring's model needs some representation of the stone for
visualization, sizing, and clearance purposes — but the stone itself is
not part of what a caster or printer would produce as the metal object.
Accidentally treating the stone solid as manufacturable metal would be a
serious, physically-wrong error.

## Decision

The stone reference is always a **separate** solid from the combined
metal body (band + prongs + basket). It is never unioned into the metal,
and is excluded from STEP/STL exports unless the caller explicitly passes
`includeStoneReference: true`. It is visually distinct in the preview
(transparent, gemstone-like material vs. opaque metal material).

## Alternatives considered

- **Unioning the stone into the metal assembly for a single combined
  export.** Rejected outright — this is exactly the error
  [LAW-006](../00-foundation/004-jewelmind-constitution.md#LAW-006)
  exists to prevent.
- **Omitting the stone from the model entirely** (metal-only). Rejected:
  the stone's size and position are needed for visualization, sizing
  checks (e.g. `JM-PRONG-003`'s stone-size-vs-prong-count rule), and to
  give the user a realistic preview.
- **Separate solid, excluded from export by default, optional include
  flag (the chosen path).** Selected — gives the visualization and
  sizing benefit without the manufacturing risk, and still allows an
  explicit opt-in for a user who wants the reference included for their
  own purposes.

## Positive consequences

- Impossible to accidentally export a stone-included file without
  explicitly asking for it.
- Preview clearly communicates "this is a reference, not metal" via
  material distinction.
- Sizing rules (e.g. `JM-PRONG-003`) can still reason about the stone's
  dimensions even though it's never fused.

## Negative consequences

- Slightly more bookkeeping in `GeneratedModel` (an extra named
  component and an extra exporter parameter) than a single-solid model
  would need.

## Risks

- Any new geometry code path that combines components must be reviewed
  to confirm it does not include the stone by accident — this is exactly
  what `test_stone_reference_is_valid_and_separate_from_metal` guards.

## Review trigger

Revisit only if a future feature explicitly requires stone geometry to be
manufacturable (e.g. a synthetic-stone or lab-grown insert workflow) —
this would need its own ADR, not a quiet change to the default export
behavior.

## Related implementation files

`backend/jewelmind/geometry/assemblies/solitaire.py`,
`backend/jewelmind/exporters/step_exporter.py`,
`backend/jewelmind/exporters/stl_exporter.py`.

## Related tests

`backend/tests/test_geometry.py::test_stone_reference_is_valid_and_separate_from_metal`.
