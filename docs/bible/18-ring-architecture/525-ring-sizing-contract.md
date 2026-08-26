---
id: JM-BIBLE-525
title: Ring Sizing Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-RING-README
  - JM-BIBLE-520
related_documents:
  - JM-BIBLE-523
  - JM-BIBLE-053
implementation_status: current
professional_validation: not_required
normative: true
---

# Ring Sizing Contract

`RingSizing` (`backend/jewelmind/ring/models.py`) is a pure 1:1 mapping of
the real, unmodified `domain/schema.py::RingSpec` fields — `sizeSystem`
(`RingSizeSystem = Literal["EU"]`), `size`, `innerDiameter`. This Sprint
did not refactor ring-sizing semantics; it only gave the existing three
fields a named place inside `RingDefinition` v2.

## The size ↔ innerDiameter relationship (unchanged, audited here)

Two fields describe the same physical ring opening, and JewelMind never
silently derives one from the other. The real relationship, read from
[`backend/jewelmind/validation/sizing.py`](../../../backend/jewelmind/validation/sizing.py)
and [`backend/jewelmind/geometry/constants.py`](../../../backend/jewelmind/geometry/constants.py):

- **`innerDiameter` is the geometry-driving field.**
  `geometry/constants.py::inner_radius(definition)` returns
  `definition.ring.innerDiameter / 2` directly — this is the only place
  ring size/diameter reaches the CAD kernel. `size` is never read by any
  geometry builder.
- **`size` is validated for EU-sizing-convention consistency with
  `innerDiameter`, not used in geometry.** `validation/sizing.py` documents
  the EU/French civil convention JewelMind uses:
  `size = (pi * inner_diameter_mm) - 40`, equivalently
  `inner_diameter_mm = (size + 40) / pi`. This is explicitly *not* the
  German, US, or UK sizing systems — see the module docstring for why
  JewelMind never silently rewrites one field from the other.
- **`sizing_consistency(size, inner_diameter_mm)`** compares the diameter
  implied by `size` against the stored `innerDiameter` and returns `None`
  (consistent, ≤0.15 mm discrepancy), `"information"` (≤0.5 mm), or
  `"warning"` (>0.5 mm) — never an error that blocks generation.
- **`validation/engine.py`'s `RING_SIZE_DIAMETER_CONSISTENCY` rule**
  (`_ring_rules()`) surfaces that classification as a `ValidationResult` at
  the matching severity when the two fields disagree; it also enforces two
  independent range checks, `RING_INNER_DIAMETER_RANGE`
  (`10 < innerDiameter < 30` mm) and `RING_SIZE_RANGE`
  (`1 < size < 50`), both `"error"` severity.

See [`../04-jewelry-domain/053-domain-invariants.md`](../04-jewelry-domain/053-domain-invariants.md)
for this rule's place among the domain's other invariants, and
[`../06-forge/README.md`](../06-forge/README.md) for Forge's own rule-authority
model — not restated here.

## What this Sprint did not do

- No international ring-size conversion table (US, UK, or otherwise) was
  added or invented anywhere in this Sprint's code or documentation.
- `RingSizing` does not change which field drives geometry, does not add a
  new consistency threshold, and does not alter `JM-RING-003`'s severity
  or blocking behavior (a change to any of those would be a MAJOR Forge
  rule-version change — see
  [`../06-forge/108-rule-versioning.md`](../06-forge/108-rule-versioning.md)).
- `jewelmind.jewelry_category.forge_scope.rule_scope()` classifies
  `RING_INNER_DIAMETER_RANGE` and `RING_SIZE_RANGE` (both `JM-RING-*`) as
  `ring_sizing` scope — see
  [`521-shared-vs-category-specific-domain.md`](521-shared-vs-category-specific-domain.md).
