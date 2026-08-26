---
id: JM-BIBLE-045
title: Band Domain
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-044
related_documents:
  - JM-BIBLE-043
  - JM-BIBLE-052
implementation_status: current
professional_validation: preliminary
---

# Band Domain

## Identity

The band is the ring's metal shank: a single closed solid, built by
`backend/jewelmind/geometry/shank/build_shank()` (Sprint 17; the older
`geometry/components/band.py` is now a thin re-export of that
function). A **uniform** band (no taper requested) is a solid of
revolution around the global Y axis, byte-identical to the
pre-Sprint-17 construction, per the coordinate convention in
`docs/geometry-conventions.md`. A **tapered** band (Sprint 17; see
[`../19-shank/README.md`](../19-shank/README.md)) is a real,
deterministic 48-section loft instead — this document describes the
domain-level parameters and invariants for both; the full geometry
subsystem, its governance, and machine-readable contract live in
[`19-shank/`](../19-shank/README.md) and are not restated here.

## Parameters currently exposed (direct inputs)

| Parameter | Path | Type | Notes |
|---|---|---|---|
| Inner diameter | `ring.innerDiameter` | float, mm | Lives on `RingSpec`, not `BandSpec` — see [`052-parametric-dependency-model.md`](052-parametric-dependency-model.md) for why it's still the band's primary driver. |
| Width | `band.width` | float, mm | Extent along the finger axis. |
| Thickness | `band.thickness` | float, mm | Radial metal thickness. |
| Profile | `band.profile` | `"flat"` \| `"comfort_fit"` | Determines cross-section construction. |
| Width taper (Sprint 17) | `band.widthTaper` | `{mode: "NONE"\|"TOWARD_BOTTOM", bottomRatio: float}` | Default `mode: "NONE"` (no change from pre-Sprint-17 behavior). See [`19-shank/548-taper-model.md`](../19-shank/548-taper-model.md). |
| Thickness taper (Sprint 17) | `band.thicknessTaper` | `{mode: "NONE"\|"TOWARD_BOTTOM", bottomRatio: float}` | Default `mode: "NONE"`. Same model as width taper, applied independently. |

Ring size (`ring.size`) is metadata *about* the inner diameter (a
sizing-system label), not a band geometry input by itself — see
[`053-domain-invariants.md`](053-domain-invariants.md) for the
consistency check between the two (`JM-RING-003`), which never rewrites
either field automatically.

## Parameters currently derived (not stored, computed from inputs)

| Derived value | Formula | Code |
|---|---|---|
| Inner radius | `innerDiameter / 2` | `geometry/constants.py::inner_radius` |
| Outer radius | `inner_radius + thickness` | `geometry/constants.py::outer_radius` |
| Band-top Z (assembly anchor) | `outer_radius` | `geometry/constants.py::band_top_z` |

## Current profiles

### Flat

A rectangular cross-section (straight inner edge, straight outer edge).
An optional small fillet is applied to the two *outer* rim edges only —
never the inner edge, which would reduce the finger opening. If the
fillet operation fails for a given input, the builder falls back to sharp
unfilleted edges and records a warning
(`geometry/components/band.py::_try_fillet_outer_rim`).

### Comfort fit

The inner edge is a shallow three-point arc instead of a straight line.
Its radius equals `inner_radius` (from the requested `innerDiameter`)
exactly at the center of the band's width, and flares outward by a fixed
amount (`_COMFORT_FLARE_MM = 0.3` in `band.py`) toward the two edges — so
the requested inner diameter is always the *minimum* opening, never
reduced below what was requested.

Both profiles produce genuinely different volumes for the same
`width`/`thickness`/`innerDiameter` — confirmed by
`backend/tests/test_geometry.py::test_flat_and_comfort_fit_bands_differ_in_volume`.

## Coordinate orientation

The band revolves around the global Y axis; its circular profile lies in
the X/Z plane; its topmost point (`x=0, z=+outer_radius`) is the anchor
for everything built above it (stone, setting, basket). Full convention:
`docs/geometry-conventions.md`.

## Geometric output

One `GeneratedComponent` named `"band"`, with `volume_mm3` and a
`BoundingBox`. Metadata differs by variation (see
[`19-shank/542-shank-domain-model.md`](../19-shank/542-shank-domain-model.md)
for the full contract): a uniform band records `profile`,
`innerRadiusMm`, `outerRadiusMm`, `filletApplied`, `variation:
"UNIFORM"`; a tapered band additionally records
`filletSkippedReason` (the fillet is not applied to a tapered outer
rim — a real v1 limitation), `widthTaperMode`/`thicknessTaperMode`,
and `widthSamplesMm`/`thicknessSamplesMm` — the latter two are
CONSTRUCTION_PARAMETER (computed from the same taper function used to
build the geometry), never independently re-measured.

## Dependency on ring dimensions

`ring.innerDiameter` and `band.thickness` together determine
`outer_radius`, which in turn is the sole positioning anchor for the
stone/setting/basket assembly (see
[`052-parametric-dependency-model.md`](052-parametric-dependency-model.md)).
There is no independent "band position" — the band is always centered at
the world origin.

## Relation to basket support

The basket's base is embedded `EMBED_MM` (0.4mm) below `band_top_z` so
the boolean union between band and basket produces genuine 3D overlap
rather than a zero-volume tangent touch (see
[`049-basket-and-support-domain.md`](049-basket-and-support-domain.md)
and [LAW-005](../00-foundation/004-jewelmind-constitution.md#LAW-005)).

## Current fallbacks

The flat profile's outer-rim fillet degrades to sharp edges (with a
recorded warning) rather than failing generation — see
[`053-domain-invariants.md`](053-domain-invariants.md) for how this
relates to workflow invariants (a fallback must never silently drop a
required component).

## Current validation rules

| Rule ID | Check |
|---|---|
| `JM-BAND-001` | `width < 1.5` → error |
| `JM-BAND-002` | `thickness < 1.4` → error; `1.4 ≤ thickness < 1.6` → warning |
| `JM-BAND-003` | `width > 12` → warning |
| `JM-GEOMETRY-001` | non-positive outer band dimension (thickness/width ≤ 0) → error |

Full detail and classification: [`054-domain-validation-classification.md`](054-domain-validation-classification.md).

## Known geometric limitations

- No taper, asymmetric profile, or split-shank topology — the band is
  always a single closed circular revolve.
- No shoulder or cathedral-rise geometry between band and setting.
- No engraving or internal relief.

## Parameters planned for future versions (PLANNED / VISION — no defaults assigned)

None of the following exist in code; no numeric default is invented for
any of them here, per [`040-domain-governance.md`](040-domain-governance.md):

| Concept | Status |
|---|---|
| Taper (width or thickness varying around the band) | PLANNED |
| Shoulder width (as a distinct parameter from band width) | PLANNED |
| Outer contour (beyond the current implicit circular revolve) | PLANNED |
| Edge radius (as a user-controlled parameter, vs. the current fixed fillet) | PLANNED |
| Asymmetric profile (different left/right cross-section) | VISION |
| Split shank | PLANNED (see [`042-ring-taxonomy.md`](042-ring-taxonomy.md)) |
| Cathedral rise | PLANNED (see [`042-ring-taxonomy.md`](042-ring-taxonomy.md)) |
| Internal relief | VISION |
