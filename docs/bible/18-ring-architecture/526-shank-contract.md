---
id: JM-BIBLE-526
title: Shank Contract
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
  - JM-BIBLE-045
implementation_status: current
professional_validation: not_required
normative: true
---

# Shank Contract

## The Band/Shank naming decision

This Sprint deliberately keeps two names for closely related things,
rather than renaming one to match the other:

- **"Band"** remains the user-facing and JDL field name —
  `domain/schema.py::BandSpec` (`width`, `thickness`, `profile`) is
  unchanged, and no code outside `jewelmind.ring` was touched to rename
  it. See [`../04-jewelry-domain/045-band-domain.md`](../04-jewelry-domain/045-band-domain.md)
  for its full domain definition (not restated here).
- **"Shank"** is a new, internal architectural term, used only inside
  `jewelmind.ring.models.ShankDefinition` and this Sprint's documentation.

This is a deliberate choice, not an inconsistency: the public API/JDL was
not renamed merely for vocabulary purity. "Do not rename public APIs
merely for vocabulary purity" is a design constraint this Sprint's own
brief states explicitly, and it is why `ShankDefinition` maps from
`band.*` rather than the schema itself being renamed to `shank.*`.

## Current fields (real, unchanged)

`ShankDefinition` (`backend/jewelmind/ring/models.py`), mapped 1:1 by
[`ring_definition_from_jdl()`](../../../backend/jewelmind/ring/adapter.py)
from `JewelryDefinition.band`:

| `ShankDefinition` field | Source JDL field | Type |
|---|---|---|
| `profile` | `band.profile` | `BandProfile = Literal["comfort_fit", "flat"]` |
| `widthMm` | `band.width` | float, mm |
| `thicknessMm` | `band.thickness` | float, mm |

Status: **CURRENT — uniform plain shank only.** The real geometry builder
(`geometry/components/band.py`, unchanged this Sprint) produces one
closed solid of revolution per the `comfort_fit`/`flat` profile — see
[`../04-jewelry-domain/045-band-domain.md`](../04-jewelry-domain/045-band-domain.md)
and [`../07-atlas/README.md`](../07-atlas/README.md) for that geometry's own
authority; this document does not restate it.

## Future PLANNED shank variants (not implemented)

Named here only to record the direction, per this Sprint's brief: tapered,
split, cathedral, knife-edge, and Euro shank profiles. None of these has a
field, a `BandProfile` literal value, a geometry builder, or a test today.
Widening `BandProfile` or adding shank-variant fields is out of scope for
this Sprint and requires its own extension process
(see [`../04-jewelry-domain/056-domain-extension-strategy.md`](../04-jewelry-domain/056-domain-extension-strategy.md)).

## Forward reference: Sprint 17

Sprint 17, "Band & Shank System v1," is planned to replace the current
uniform band implementation with a reusable parametric shank subsystem
supporting controlled profiles, width/thickness variation, tapering, and
connection interfaces, while preserving Golden regression safety. This
document does not describe that work further — it is out of this Sprint's
scope and not yet implemented.

## What this Sprint did not do

- `domain/schema.py::BandSpec` was not modified, renamed, or extended.
- No tapered/split/cathedral/knife-edge/Euro geometry was added anywhere
  in `geometry/components/`.
- `jewelmind.jewelry_category.forge_scope.rule_scope()` classifies
  `BAND_WIDTH_MIN` (`JM-BAND-001`) as `ring_shank` scope — see
  [`521-shared-vs-category-specific-domain.md`](521-shared-vs-category-specific-domain.md).
