---
id: JM-BIBLE-A110
title: "Appendix: Shank Profile Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
related_documents:
  - JM-BIBLE-A20
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Shank Profile Catalog

Every section-profile type known to `geometry/shank/profile.py`, cross-checked against the real code and `specs/shank/v1/section-profile.schema.json`/`test-vectors/profile-vectors.json`. A profile is a real, closed 2D wire in the local XY plane (local x = radial distance from the ring axis, local y = axial/width position) built for one angular position only — no longitudinal variation is ever mixed into profile generation (SHANK-GOV-004).

| Profile type | Status | Geometric definition | Real parameters | Builder function | Used by |
|---|---|---|---|---|---|
| `flat` | CURRENT | A rectangle: `inner_r <= x <= outer_r`, `-half_width <= y <= half_width`, 4 vertices. | None beyond `inner_r`/`outer_r`/`half_width` (all caller-supplied per section). | `flat_profile_wire()` in `geometry/shank/profile.py` | Uniform (revolve) and tapered (loft) paths, both dispatched via `build_profile()`. |
| `comfort_fit` | CURRENT | The inner edge is a shallow outward-bulging arc (`threePointArc`) instead of a straight line; the outer edge and sides stay straight. The minimum inner radius is exactly `inner_r` at the profile's vertical center — the requested finger opening is never reduced. | `COMFORT_FLARE_MM = 0.3` (mm, fixed, not user-configurable) — the outward bulge added to `inner_r` at the profile's Y edges (`edge_r = inner_r + COMFORT_FLARE_MM`). | `comfort_fit_profile_wire()` in `geometry/shank/profile.py` | Uniform (revolve) and tapered (loft) paths, both dispatched via `build_profile()`. |
| `knife_edge` | PLANNED | Not implemented — a third section-profile type reserved by name only. | n/a | n/a | Not reachable through `build_profile()`; requesting it is not possible via JDL (`band.profile` only accepts `flat`/`comfort_fit` at the schema layer). |

## Dispatch

`build_profile(profile_type, inner_r, outer_r, half_width)` is the single entry point both construction paths call — `_build_uniform_shank()` calls it once per revolve, `_build_tapered_shank()` calls it `SECTION_COUNT + 1` times per loft (once per sampled angular position, closing the loop). Any `profile_type` other than `"flat"` dispatches to `comfort_fit_profile_wire()` (the function's `else` branch), so a caller can only ever reach `flat` or `comfort_fit` because the JDL schema layer (`BandSpec.profile`) itself only accepts those two literal values before `build_profile()` is ever called.

## Real geometric constant

| Constant | Value | File | Meaning |
|---|---|---|---|
| `COMFORT_FLARE_MM` | `0.3` (mm) | `geometry/shank/profile.py` | Outward flare of the comfort-fit inner edge at the profile's Y edges, relative to the profile's center; unchanged from the pre-Sprint-17 `band.py` implementation, moved verbatim into `geometry/shank/profile.py`. |

## Cross-references

- [`545-section-profile-contract.md`](../19-shank/545-section-profile-contract.md) — full narrative contract.
- [`shank-capability-catalog.md`](shank-capability-catalog.md) — `flat_profile`/`comfort_fit_profile`/`knife_edge_profile` capability entries.
- `specs/shank/v1/section-profile.schema.json` and `specs/shank/v1/test-vectors/profile-vectors.json` — the machine-readable equivalents this table was cross-checked against.
