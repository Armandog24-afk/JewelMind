---
id: JM-BIBLE-049
title: Basket and Support Domain
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-048
related_documents:
  - JM-BIBLE-045
  - JM-BIBLE-043
implementation_status: current
professional_validation: preliminary
---

# Basket and Support Domain

## Terminology discipline

This document distinguishes four terms that are sometimes used loosely
or interchangeably in casual jewelry language, but represent different
concepts in this Bible:

| Term | Meaning here | In current code? |
|---|---|---|
| **Structural support** | Any load-bearing connection between the setting and the band. | Yes — this is exactly what `BasketSupport` is. |
| **Gallery** | Decorative (often open/filigreed) structure visible between the stone/setting and the band, which may or may not also be load-bearing. | No. |
| **Bridge** | A structural connector distinct from the gallery, e.g. linking a basket to shoulders. | No. |
| **Shoulder transition** | The band's transition zone as it approaches the setting (relevant to styles like cathedral). | No. |

The current `BasketSupport` fulfills the **structural support** role
only. It is not a gallery (it has no decorative openwork) and the code
does not distinguish a bridge or shoulder-transition concept at all.
Using "gallery" or "bridge" to describe the current basket geometry would
be a terminology error this document exists to prevent.

## Current implementation: a hollow cylindrical wall

`geometry/components/basket.py::build_basket_support` constructs a
hollow cylindrical shell:

```
outer_radius = prong_center_radius + prong_radius
inner_radius = max(prong_center_radius − prong_radius, 0.2mm)
height       = setting.basketHeight + EMBED_MM
base_z       = band_top_z − EMBED_MM
```

This is a deliberate, conservative choice: a plain hollow cylinder is
robust (always produces valid geometry) rather than decorative. The
outer/inner radii are specifically chosen so the wall's radial thickness
fully contains the prong footprint at every angle, guaranteeing the
prongs, basket, and band all genuinely overlap in 3D when fused — not
just touch at a surface (see
[LAW-005](../00-foundation/004-jewelmind-constitution.md#LAW-005)).

## Support ring, lower support, upper support, connectors

The current single hollow cylinder plays all of these informal roles at
once — it is simultaneously the "lower support" (where it meets the
band) and "upper support" (where it meets the prong bases), with no
separate connector geometry between them, because it is one continuous
wall, not a two-ring-plus-connector assembly. This is a simplification
relative to how a basket might be described conceptually (see
[`043-ring-anatomy.md`](043-ring-anatomy.md)'s anatomy table) — the
current code does not implement the upper-ring/lower-ring/connector
decomposition as separate solids.

## Relationship with prongs

Shares `prong_center_radius()` with `build_prongs()` (see
[`048-prong-domain.md`](048-prong-domain.md)) so the two components'
footprints are consistent with each other by construction, not by a
separate consistency check.

## Relationship with band

The basket's `base_z` sits `EMBED_MM` (0.4mm) below `band_top_z`, and its
height is extended by the same amount, so the extruded solid's actual
visible top/bottom stay at the intended positions while the base
genuinely penetrates into the band's solid volume for a valid boolean
fuse (see [`045-band-domain.md`](045-band-domain.md)).

## Separation from stone

The basket is a metal (or metal-representing) solid; it has no geometric
relationship to `CenterStoneReference` beyond sharing the same vertical
axis and radius family as the prongs — it is never unioned with the
stone reference, consistent with
[LAW-006](../00-foundation/004-jewelmind-constitution.md#LAW-006).

## Current assembly behavior

`geometry/assemblies/solitaire.py::_fuse_metal` attempts to fuse
`band ∪ basket ∪ prongs` into one solid. If the fuse fails for any
reason, the assembly falls back to a multi-solid compound of the three
separate solids and records a warning — never dropping a component (see
[LAW-005](../00-foundation/004-jewelmind-constitution.md#LAW-005) and
[`053-domain-invariants.md`](053-domain-invariants.md)).

## Current limitations

- Plain cylindrical shell — no decorative openwork, no gallery, no
  bridge, no shoulder transition.
- No differentiation between an "upper" and "lower" support ring as
  separate solids.
- Wall thickness is derived purely from the prong footprint, not from
  any independent structural-adequacy calculation.
- No relief/cutout for reduced weight or visual openness.

## Open questions for professional review

Logged in full in
[`057-open-domain-questions.md`](057-open-domain-questions.md); the
basket/support-specific ones include:

- Is a solid cylindrical wall an adequate structural approximation for
  any real basket design, or does it systematically over- or
  under-estimate the metal needed?
- At what point (if any) should the basket wall thickness be validated
  independently of the prong footprint, rather than always derived from
  it?
- What is the professionally correct relationship (if any) between
  gallery openwork and structural adequacy, for a future decorative
  basket variant?
