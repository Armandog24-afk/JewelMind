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

## Superseded by Sprint 17

**Update (Sprint 17, "Band & Shank System v1"):** the forward reference
this document originally recorded has now happened. The real, current
Shank geometry subsystem, its 15 SHANK-GOV-* governance rules, and its
full domain/generation model are documented in
[`../19-shank/README.md`](../19-shank/README.md) — this document is not
rewritten to restate that content; it now only records how the Ring
Architecture v2 `ShankDefinition` layer (a data-mapping model, not a
geometry builder) reflects that change.

## Current fields (real)

`ShankDefinition` (`backend/jewelmind/ring/models.py`), mapped 1:1 by
[`ring_definition_from_jdl()`](../../../backend/jewelmind/ring/adapter.py)
from `JewelryDefinition.band`:

| `ShankDefinition` field | Source JDL field | Type |
|---|---|---|
| `profile` | `band.profile` | `BandProfile = Literal["comfort_fit", "flat"]` |
| `widthMm` | `band.width` | float, mm |
| `thicknessMm` | `band.thickness` | float, mm |
| `widthTaper` | `band.widthTaper` | `BandTaperSpec` (Sprint 17) |
| `thicknessTaper` | `band.thicknessTaper` | `BandTaperSpec` (Sprint 17) |

Status: **CURRENT — uniform shank, plus real width and/or thickness
taper.** The real geometry builder is now
`geometry/shank/builder.py::build_shank()` (Sprint 17; the old
`geometry/components/band.py` is a thin re-export) — see
[`../19-shank/README.md`](../19-shank/README.md) for its full authority;
this document does not restate it.

## Future PLANNED shank variants (not implemented)

Split, cathedral, knife-edge, Euro shank, twisted, and multi-rail
shanks. None of these has a field, a geometry builder, or a test today —
see the real, current `capability-registry.json` at
[`../../../specs/shank/v1/capability-registry.json`](../../../specs/shank/v1/capability-registry.json)
for the authoritative current/planned list. Widening `BandProfile` or
adding these shank-variant fields is out of scope and requires its own
extension process (see
[`../04-jewelry-domain/056-domain-extension-strategy.md`](../04-jewelry-domain/056-domain-extension-strategy.md)).

## What Sprint 17 did and did not do

- `domain/schema.py::BandSpec` gained `widthTaper`/`thicknessTaper` as an
  additive, backward-compatible MINOR JDL change — `band.profile`,
  `band.width`, `band.thickness` are unchanged.
- No split/cathedral/knife-edge/Euro/twisted/multi-rail geometry was
  added anywhere in `geometry/`.
- `jewelmind.jewelry_category.forge_scope.rule_scope()` still classifies
  `BAND_WIDTH_MIN` (`JM-BAND-001`) as `ring_shank` scope — unchanged, see
  [`521-shared-vs-category-specific-domain.md`](521-shared-vs-category-specific-domain.md).
