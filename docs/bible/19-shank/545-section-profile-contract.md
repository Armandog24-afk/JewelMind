---
id: JM-BIBLE-545
title: Section Profile Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
  - JM-BIBLE-544
related_documents:
  - JM-BIBLE-546
  - JM-BIBLE-547
implementation_status: current
professional_validation: not_required
normative: true
---

# Section Profile Contract

## The single place profiles are built

`geometry/shank/profile.py` is the one module in the codebase that builds a Shank cross-section wire. Both the uniform (revolve) and tapered (loft) construction paths call into it — `_build_uniform_shank()` calls `build_profile()` once, and `_build_tapered_shank()`'s `_section_wire()` calls it once per sampled section — so profile logic is never duplicated between the two paths (SHANK-GOV-004). A profile builder never sees longitudinal variation: `build_profile(profile_type, inner_r, outer_r, half_width)` takes only the already-resolved dimensions for one angular position; all taper interpolation happens in `builder.py`/`taper.py` before calling in.

## The two real profile types

`domain/schema.py::BandProfile = Literal["comfort_fit", "flat"]` — unchanged from before this Sprint, and the only two values `build_profile()` dispatches on:

**`flat_profile_wire()`** — a plain rectangular cross-section, 4 vertices, drawn in the local XY plane (local x = radial distance from the ring axis, local y = position along the shank's axial/width direction):

```python
def flat_profile_wire(inner_r, outer_r, half_width):
    pts = [
        (inner_r, -half_width),
        (inner_r, half_width),
        (outer_r, half_width),
        (outer_r, -half_width),
    ]
    return cq.Workplane("XY").polyline(pts).close()
```

**`comfort_fit_profile_wire()`** — the inner edge is a shallow, outward-bulging arc instead of a straight line:

```python
def comfort_fit_profile_wire(inner_r, outer_r, half_width):
    edge_r = inner_r + COMFORT_FLARE_MM
    return (
        cq.Workplane("XY")
        .moveTo(edge_r, -half_width)
        .threePointArc((inner_r, 0.0), (edge_r, half_width))
        .lineTo(outer_r, half_width)
        .lineTo(outer_r, -half_width)
        .close()
    )
```

## Why the comfort-fit inner radius never goes below the requested value

`COMFORT_FLARE_MM = 0.3` is a fixed, conservative constant — not user-configurable in v1 — describing how far outward (in mm) the inner edge flares at the profile's Y edges relative to its longitudinal center. The arc's minimum inner radius, at the profile's center point `(inner_r, 0.0)`, is exactly the requested `inner_r` — the shape only ever flares outward from that point toward the edges, via a `threePointArc` from `(edge_r, -half_width)` through `(inner_r, 0.0)` to `(edge_r, half_width)`. This means the requested finger opening is never reduced by the comfort-fit treatment: a wearer's actual clearance at the profile's narrowest point matches the requested `inner_r` exactly, with the flare only adding clearance toward the profile's edges, never subtracting it at the center. This is restated normatively in [`specs/shank/v1/section-profile.schema.json`](../../../specs/shank/v1/section-profile.schema.json)'s `innerRadiusMm` description.

## Both profile types are unchanged from before Sprint 17

`COMFORT_FLARE_MM`, `flat_profile_wire()`, and `comfort_fit_profile_wire()` were moved unchanged from the pre-Sprint-17 `geometry/components/band.py` into `geometry/shank/profile.py` — the module docstring notes it is "the single place flat and comfort-fit cross-sections are built," and the construction logic itself is byte-identical to before. What is new is that a tapered loft can now call the same builder repeatedly at varying `inner_r`/`outer_r`/`half_width`, rather than the builder only ever being called once per generation.

## One profile type per shank; profile shape is never varied within a loft

Per SHANK-GOV-004, taper only ever varies a section's *dimensions* (`half_width`, and the thickness that determines `outer_r`), never its *profile shape*. A single `build_shank()` call always uses exactly one `profile_type` (`definition.band.profile`) for every section it builds, uniform or tapered. There is no code path that mixes `flat` and `comfort_fit` sections within one loft, and no code path that morphs one profile shape into another partway around the shank.

## Knife edge is PLANNED, not implemented

A third profile type — knife edge, a sharply pointed rather than flat or gently-curved outer/inner treatment — has no field, no builder function, and no test in the current code. The capability registry records this explicitly:

```json
{
  "capability": "knife_edge_profile",
  "status": "planned",
  "jdlExposed": false,
  "generatable": false,
  "inspectable": false,
  "description": "A third section-profile type; not implemented."
}
```

(`geometry/shank/capability.py::SHANK_CAPABILITIES["knife_edge_profile"]`.) Adding it requires a new `flat`/`comfort_fit`-sibling function in `profile.py`, a widened `BandProfile` literal, and — per [`540-shank-governance.md`](540-shank-governance.md)'s "When an ADR is required" — an ADR, since a new section-profile type is explicitly listed there as ADR-triggering.
