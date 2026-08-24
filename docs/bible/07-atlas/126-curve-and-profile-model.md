---
id: JM-BIBLE-126
title: Curve and Profile Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-124
related_documents:
  - JM-BIBLE-045
implementation_status: current
professional_validation: preliminary
normative: true
---

# Curve and Profile Model

## Current profiles

### Flat (`band.py::_build_flat_wire`)

- **Cross-section**: a rectangle, corners at `(inner_r, ±half_width)` and `(outer_r, ±half_width)`.
- **Profile plane**: the local (radius, width-position) plane, i.e. what becomes the band's X/Z cross-section once revolved.
- **Strategy**: revolve 360° around global Y.
- **Inner diameter preservation**: exact — the inner edge is a straight line at `x = inner_r` for the full width, so the requested `ring.innerDiameter` is the finger opening everywhere along the band's width.
- **Outer contour**: straight line at `x = outer_r`.
- **Edge treatment**: an optional fillet on the two outer rim edges only (see [`135-fillets-rounding-and-fallbacks.md`](135-fillets-rounding-and-fallbacks.md)); the inner edge is never filleted, so the finger opening is never reduced by rounding.
- **Fallback strategy**: if the fillet fails, fall back to the sharp-edged rectangle.

### Comfort-fit (`band.py::_build_comfort_fit_wire`)

- **Cross-section**: outer edge is the same straight line as flat; the inner edge is a three-point arc from `(edge_r, -half_width)` through `(inner_r, 0)` to `(edge_r, half_width)`, where `edge_r = inner_r + _COMFORT_FLARE_MM` (0.3mm, a fixed constant).
- **Profile plane**: same as flat.
- **Strategy**: same revolve.
- **Inner diameter preservation**: the *minimum* inner radius (at the band's width center) is exactly `inner_r` — the requested `ring.innerDiameter` is never reduced; the arc only flares *outward* toward the edges, by a fixed 0.3mm.
- **Outer contour**: same straight line as flat.
- **Edge treatment**: no fillet is applied to the comfort-fit inner arc — the arc itself is the "soft edge" feature; only the flat profile's fillet logic exists in this codebase.
- **Fallback strategy**: **none exists**. The comfort-fit wire construction (`.moveTo()`, `.threePointArc()`, `.lineTo()`, `.close()`) has no try/except around it — if it were ever to fail (no failure has been observed for any valid input), the exception would propagate up as an unhandled construction error, unlike the flat profile's filleted rim.

## Future profiles (PLANNED/VISION — not implemented)

Tapered band, asymmetric band, split shank, cathedral profile. **None of these has any code, test, partial implementation, or scoped design in this repository.** They are listed here only because they are the natural next profile variants a future RFC might propose — see [`04-jewelry-domain/045-band-domain.md`](../04-jewelry-domain/045-band-domain.md) for the jewelry-domain framing and [`151-open-atlas-questions.md`](151-open-atlas-questions.md) for related open questions. Per this Sprint's explicit scope, none is designed or implemented here.
