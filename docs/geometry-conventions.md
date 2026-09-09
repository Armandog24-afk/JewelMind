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
- **The finger/hole axis is the global Y axis.** A uniform (non-tapered)
  band is a solid of revolution around Y: its cross-section is drawn
  with local x = radial distance from the axis and local y = position
  along the band's width, then revolved 360° around Y (see
  `build_shank` in `backend/jewelmind/geometry/shank/builder.py`,
  re-exported as `build_ring_band` from
  `backend/jewelmind/geometry/components/band.py`). A tapered band
  (Sprint 17) uses this same X/Z profile/Y-axis convention at every
  sampled section, but is built as a multi-section loft instead of a
  single revolve — see
  `docs/bible/19-shank/543-shank-coordinate-model.md` for the
  longitudinal `u ∈ [0,1)` parameter this introduces on top of the
  convention below, unchanged.
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

- **Stone reference** (`build_stone_reference`, a re-export of
  `geometry/stone/build_stone()`): girdle plane at
  `z = band_top_z + setting.basketHeight`; pavilion extends downward from
  the girdle, crown extends upward. The girdle **outline** is the shape's
  own 2D profile, centered at `(0, 0)`, with its major horizontal
  dimension (LENGTH) along local Y and its minor (WIDTH) along local X.
  For `round` that outline is a circle of radius `stone.diameter / 2`.
  `stone.orientation` rotates the finished solid about its own local
  vertical axis. See
  `docs/bible/20-stone/565-stone-coordinate-and-orientation.md`.
- **Prongs** (`build_prongs`): vertical cylinders whose centers sit on a
  circle of radius `prong_center_radius` (see `constants.py`, slightly
  inside the stone's resolved half-width so each prong overlaps the girdle
  edge — a generic provisional layout, not shape-optimized),
  evenly spaced by angle, starting just below `band_top_z` (embedded into
  the band/basket, see below) and rising to `band_top_z + setting.prongHeight`.
- **Basket support** (`build_basket_support`): a hollow cylindrical wall
  (outer radius minus inner radius) between `band_top_z` and
  `band_top_z + setting.basketHeight`, sized so its radial wall fully
  contains the prong footprint. An `OPEN_GALLERY` head is that same wall with
  angular sectors cut from the middle `galleryWindowHeightFraction` of its
  height, centred on it, so a continuous rim survives at each end.

### The Sprint 27 setting families

All four place rectangular prisms in the **stone's own horizontal frame**: a
direction `axisDeg` (or `gripAxisDeg`) measured in the XY plane from +X, an
extent ALONG it and an extent ACROSS it. Each prism is built at the origin,
rotated about the GLOBAL Z axis, and only then translated onto the stone's
centre — rotating after the translation would swing it around the design origin
instead of about its own centre.

Every one of them starts at `attachmentPlaneZMm - embedMm`, which is the same
expression the basket and the prongs use, so a Sprint 27 family sinks past the
attachment plane by exactly the amount the existing families do (see "Why solids
are embedded, not just touching" below).

An extent stated as `None` is resolved from the stone's **measured bounding
box**, not its requested dimensions: the box is the extent of the solid that
actually exists, so it already accounts for `stone.orientation` and for any
shape whose outline does not fill its nominal box.

- **Channel walls** (`generate_channel_setting`): two prisms whose centres sit
  `innerWidthMm / 2 + wallThicknessMm / 2` either side of the run's centreline,
  so the CLEAR distance between them is exactly `innerWidthMm`. They span
  `spanMm` along the axis and rise to
  `stone.girdlePlaneZMm + wallHeightMm`. `CLOSED_ENDS` adds two caps of the full
  outer width at each end of the run, so a cap genuinely meets both walls'
  material rather than touching them along a face.
- **Bars** (`generate_bar_setting`): `barCount` prisms distributed along the
  axis. `SYMMETRIC` centres them on the stone (an even count straddles it);
  `ASYMMETRIC` puts the first bar ON the stone's centre and runs the rest along
  `+axisDeg`. Each rises to `stone.girdlePlaneZMm + barHeightMm`.
- **Flush collar** (`generate_flush_setting`): not a prism — the stone's own
  girdle outline offset outward by `collarWidthMm` (the bezel's verified offset
  pipeline), extruded from the attachment plane to
  `stone.girdlePlaneZMm + rimHeightMm`. The stone's own solid is then CUT out of
  it by the existing `REFERENCE_SEAT` relief, which is what opens the recess.
  `rimHeightMm` must stay below the stone's measured crown height or the stone
  would be entirely buried.
- **Tension supports** (`generate_tension_setting`): two prisms opposing each
  other along `gripAxisDeg`. Each support's INNER face sits `padDepthMm` inside
  the stone's edge, so its centre is
  `halfExtent - padDepthMm + padThicknessMm / 2` from the stone's centre and the
  relief leaves a real groove rather than a tangent touch.

### The Sprint 28 ring-family components

Three components joined the assembly, and each states its placement against the
existing convention rather than introducing one (ATLAS-GOV-012).

**`shoulders`** — the shank-to-head transition, and the first geometry the
shoulder has ever had. Each arch is a ruled loft between two real sections: the
base is the band's OWN profile wire from `shank/profile.py`, placed at
`u = ±span/360` and rotated by `angle_deg_for_u(u)`; the top is a flat section
at the head's own height, rotated by `angle_deg_for_u(0)`. Using the same
rotation for both ends is what keeps the loft's sections compatible.

A cathedral builds two arches (one per side, at the band's own half-width); a
split shank builds four (one per rail per side, at the rails' own half-width and
axial offset, from the SAME `rail_half_width()` the shank builds them with, so
the shoulders land on the rails rather than beside them). Every architecture
produces the single `shoulders` component; the arch count is in its metadata.

**A CONSTRUCTION LIMIT LIVES HERE, and it is arithmetic.**
`MAX_ARCH_SPAN_DEG = 90.0`: section rotation is `angle_deg_for_u(u) = −90 + u ×
360`, so the base section's rotation is `−90 + span`. At 90° it reaches 0° — the
head section's own orientation — and past that it rotates beyond it, so the
ruled loft turns back on itself. Measured: at 90° the fused arches are
84.651 mm³ and the ring's metal is valid; at 92° they collapse to 19.577 mm³ and
the combined metal is invalid, while the individual arch still reports
`isValid() == True`. It is therefore refused as a PRECONDITION, in both the
schema and the builder, and never clamped.

**`band` under a `SPLIT` or `BYPASS` architecture** — same frame as the uniform
band: revolved about the global Y axis, ring in the XZ plane, top at
`(0, 0, +outer_radius)`.

A split shank is two rails at `±(separation/2 + half)` on the axial (Y) axis,
each `rail_half_width()` wide, joined by a bridge over the bottom
`splitJoinSpan` degrees. **Revolve first and translate the SHAPE afterwards**:
`Workplane.translate()` before `.revolve()` silently loses the offset, which
shipped as two coincident rails whose fused volume was exactly one rail's. Arcs
are built by intersecting a full revolve with a pie sector rather than by a
partial `revolve()`, which sweeps unpredictably.

A bypass is ONE rail lofted over `360 + overlap` degrees with the axial offset
interpolated linearly along the sweep, starting half the overlap before the top
so the crossing is centred on it. Deliberately one rail: two axially separated
arcs come out as two disconnected solids.

**`signet_body`** — a solid centred on the ring's top, embedded `_BODY_EMBED_MM`
into the band so the fused body is one solid. Its table length runs along the
ring's circumference and its width along the axial direction.

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

The stone reference is a simplified lofted approximation (culet →
pavilion → girdle → crown → table) over the shape's own 2D outline, not a
gemological reproduction — for any of the 7 supported shapes (`round`,
`oval`, `pear`, `emerald`, `cushion`, `princess`, `marquise`). See
`docs/known-limitations.md` for what this does and does not represent, and
`docs/bible/20-stone/README.md` for the full Stone System contract. It is always a solid entirely separate from the metal
geometry — never unioned, never exported as part of the metal STEP/STL by
default.

## Determinism

For a given `JewelryDefinition`, the same code path always produces the
same geometry, the same volumes, and the same `definitionHash` (a SHA-256
of the canonical JSON — see `jewelmind/utils/hashing.py`). There is no
randomness anywhere in the geometry pipeline.
