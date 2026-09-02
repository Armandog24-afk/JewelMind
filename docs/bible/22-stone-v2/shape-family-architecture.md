---
id: JM-BIBLE-603
title: "Shape Family Architecture"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-602
related_documents:
  - JM-BIBLE-604
implementation_status: current
professional_validation: not_required
normative: true
---

# Shape Family Architecture

## The reuse the brief asked for, and the reuse it warned against

Brief section 5 asked for useful shape families so that fourteen new cuts are
not fourteen unrelated implementations. It also warned: *"Do not build one
universal magic shape generator"* and *"Do not force geometrically distinct
shapes through inappropriate shared logic."*

Both halves were honoured. There are shared primitives, and there is no single
generator.

## The shared primitives

`backend/jewelmind/geometry/stone/outline.py`:

| Primitive | Used by | Parameters beyond length/width |
|---|---|---|
| `_polyline_outline` | every polygonal shape | — |
| `_clipped_rectangle` | emerald, radiant, asscher | clip ratio |
| `_tapered_quadrilateral` | tapered_baguette, trapezoid | narrow width |
| `custom_outline` | custom outlines | the points themselves |

Everything else — heart, half_moon, trillion, kite, shield, hexagon, lozenge,
triangle, baguette — is its own short, readable function. That is deliberate:
`shield`'s seven vertices and `heart`'s two lobe arcs have nothing structurally
in common, and a parameterization covering both would be less legible than
either.

## Where a shared primitive is genuinely correct

`_clipped_rectangle(half_length, half_width, scale, clip_ratio)` is the strongest
case. Three shapes differ **only** in a ratio:

```
emerald  0.18
radiant  0.14
asscher  0.22
```

Sharing here means a future change to how a corner is clipped — a chamfer
instead of a straight cut, say — is one edit rather than three, and the three
shapes cannot drift into inconsistent corner treatments.

## Where reuse was deliberately refused

### Round keeps its own construction

`_build_round_stone()` is untouched from before Sprint 18. Routing it through
the shared pipeline would change its geometry: its culet radius is ABSOLUTE
(0.05mm) while the shared pipeline's is PROPORTIONAL (0.05 × half-width, i.e.
0.1625mm for a 6.5mm stone), which makes the shared body about **1.8% larger**.

Measured, not assumed, and now pinned by
`test_round_geometry_differs_from_the_v2_pipeline`. See STONEV2-GOV-017.

### `princess` and `baguette` keep separate functions

Identical geometry today, distinct canonical identities, independently
changeable tomorrow (STONEV2-GOV-005).

### `triangle` and `trillion` share a family, not a construction

Same family (`TRIANGULAR`), fundamentally different silhouettes: straight sides
versus bowed. Forcing them through one parameterized "triangle with optional
bulge" would make `bulge=0` the definition of `triangle`, which is a
coincidence of the current implementation rather than a fact about the shape.

## The outline signature, and its one exception

Every outline builder has the same shape:

```python
def <shape>_outline(half_length: float, half_width: float, scale: float) -> cq.Wire
```

`scale` exists so the 3D profile builders can sample the same silhouette at the
culet, girdle and table levels without knowing which shape they are building —
which is what makes `outline × profile` a genuine product rather than a set of
special cases.

Two exceptions, both explicit:

- `round_outline(radius, scale)` takes a radius. Adapted at both call sites
  (`normalize.outline_builder_for`, `setting/stone_interface._OUTLINE_BUILDERS`).
- The tapered builders take a fourth argument, `half_narrow_width`.

Both adaptations are done by binding, so the profile builders still see a plain
`(scale) -> Wire` callable.

## Ordered outline sampling

`sample_outline(wire)` discretizes an outline into ordered points. It is what
`StoneOutline` carries and what a bezel over a custom stone consumes.

**`Wire.Edges()` is not reliably ordered.** The heart returns its four arcs in
the order 1, 4, 2, 3 with mixed orientations. Concatenating them naively
produces a scrambled ring that still has a **correct bounding box** — so any
check based on extents would pass while the point sequence was wrong, silently
corrupting anchor derivation and any offset built from the points.

`_ordered_edges()` therefore walks the wire by endpoint connectivity, returning
each edge with the direction the traversal needs. The regression test compares
the sampled ring's **enclosed area** against the real face area, and verifies
that a deliberately scrambled ring fails the same check — because step length
cannot be the signal: the heart has two long straight sides, and a LINE edge
contributes only its start vertex, so a correct traversal legitimately contains
a 7mm step.

**Sampling honesty:** a straight edge contributes only its start vertex, so a
polygon samples to exactly its own vertices and stays EXACT. A curved edge
contributes `OUTLINE_CURVE_SAMPLES` (48) evenly-parameterized points and is
therefore an approximation — reported as `isPolygonal: false`. The measured
worst-case extent deviation is about 1.6e-4mm on the heart at 48 samples per
arc. The **solid** is always built from the real wire, so measured dimensions
remain exact.

## Cross-references

- [`extended-native-shapes.md`](extended-native-shapes.md)
- [`../19-shank/README.md`](../19-shank/README.md) — the same
  "shared section builder, separate longitudinal logic" split, in the Shank.
