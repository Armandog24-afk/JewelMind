# Geometry conventions

This document is the single source of truth for how a `JewelryDefinition`
turns into 3D geometry. Every geometry builder
(`backend/jewelmind/geometry/**`), the preview pipeline, the frontend
viewer, and the geometry tests all follow this convention. If you change it,
update all of those together.

## Units

All lengths are **millimeters**. There is no unit conversion anywhere in the
system — every numeric field in `JewelryDefinition`, every exported
STEP/STL file, and every dimension shown in the UI is in mm.

## Coordinate system

- The world origin is the center of the ring (the center of the band's
  revolution, i.e. the center of the finger hole).
- **The finger/hole axis is the global Y axis.** The band is a solid of
  revolution around Y: its cross-section is drawn with local x = radial
  distance from the axis and local y = position along the band's width,
  then revolved 360° around Y (see `build_ring_band` in
  `backend/jewelmind/geometry/components/band.py`).
- Consequently the band's circular profile lies in the **X/Z plane** when
  viewed down the Y axis — the same way a ring looks when you look through
  the hole from the side.
- The band's **topmost point** is at `(x=0, z=+outer_radius)`, where
  `outer_radius = ring.innerDiameter / 2 + band.thickness`. This is the "top
  of the ring": the highest point of the band when the hole axis is
  horizontal, exactly where a solitaire's stone sits in real life.
- `band_top_z = outer_radius` (see `jewelmind/geometry/constants.py`).

## The assembly anchor point

The stone reference, prongs, and basket support are **not** built around
the band's own revolution axis (Y) — they are built around a second,
independent vertical axis: the line `x=0, y=0`, parallel to global Z,
starting at `z = band_top_z` and rising in `+Z`. This is the "assembly
anchor point": everything above the band is centered on it.

- **Stone reference** (`build_stone_reference`): girdle plane at
  `z = band_top_z + setting.basketHeight`; pavilion extends downward from
  the girdle, crown extends upward. Girdle radius = `stone.diameter / 2`,
  centered at `(0, 0)`.
- **Prongs** (`build_prongs`): vertical cylinders whose centers sit on a
  circle of radius `prong_center_radius` (see `constants.py`, slightly
  inside the stone's girdle radius so each prong overlaps the girdle edge),
  evenly spaced by angle, starting just below `band_top_z` (embedded into
  the band/basket, see below) and rising to `band_top_z + setting.prongHeight`.
- **Basket support** (`build_basket_support`): a hollow cylindrical wall
  (outer radius minus inner radius) between `band_top_z` and
  `band_top_z + setting.basketHeight`, sized so its radial wall fully
  contains the prong footprint.

## Why solids are embedded, not just touching

If the prongs/basket start their solid geometry exactly at
`z = band_top_z`, they only *touch* the band's curved outer surface at a
single tangent line — a zero-volume contact that OpenCascade's boolean
`fuse()` leaves as a compound of separate solids rather than one fused
solid. To guarantee genuine 3D overlap (and therefore a real single fused
metal body, and no "floating" components), every component that attaches to
another one starts `EMBED_MM` (0.4 mm) *below* its nominal starting height
and is that much taller, so its visible top surface still lands exactly
where the parameters say it should. See `EMBED_MM` in
`jewelmind/geometry/constants.py`.

## Band profiles

Both profiles are drawn as a 2D wire in the (radius, width-position) plane,
then revolved around Y:

- **flat**: a rectangle — straight inner edge, straight outer edge. An
  optional small fillet is applied to the two *outer* rim edges only (never
  the inner edge, which would reduce the finger opening). If the fillet
  operation fails on a given input, the builder falls back to the sharp
  unfilleted solid and records a warning — see
  `docs/known-limitations.md`.
- **comfort_fit**: the inner edge is a shallow three-point arc instead of a
  straight line. Its radius is exactly `inner_radius` at the center of the
  band's width and flares outward by a fixed amount at the two edges — so
  the requested inner diameter is always the *minimum* opening, never
  reduced below what was requested.

## Stone reference

The stone reference is a simplified round-brilliant-style approximation
(lofted culet → pavilion → girdle → crown → table), not a gemological
reproduction. See `docs/known-limitations.md` for what this does and does
not represent. It is always a solid entirely separate from the metal
geometry — never unioned, never exported as part of the metal STEP/STL by
default.

## Determinism

For a given `JewelryDefinition`, the same code path always produces the
same geometry, the same volumes, and the same `definitionHash` (a SHA-256
of the canonical JSON — see `jewelmind/utils/hashing.py`). There is no
randomness anywhere in the geometry pipeline.
