---
id: JM-BIBLE-544
title: Shank Path Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
  - JM-BIBLE-543
related_documents:
  - JM-BIBLE-545
  - JM-BIBLE-548
implementation_status: current
professional_validation: not_required
normative: true
---

# Shank Path Contract

## The real centerline, in v1

The centerline every Shank is built around is a single circle of radius `outer_radius(definition)` (`geometry/constants.py::outer_radius()`), lying in the ring's equatorial plane — the X/Z plane, centered on the world origin, revolved/rotated around the global Y axis (see [`543-shank-coordinate-model.md`](543-shank-coordinate-model.md) and [`07-atlas/123-coordinate-system-and-orientation.md`](../07-atlas/123-coordinate-system-and-orientation.md) for the base convention).

`outer_radius()` itself is derived, not independently specified:

```python
def inner_radius(definition: JewelryDefinition) -> float:
    return definition.ring.innerDiameter / 2

def outer_radius(definition: JewelryDefinition) -> float:
    return inner_radius(definition) + definition.band.thickness
```

For the default definition, this is `inner_radius = 8.9`, `outer_radius = 10.700000000000001` (real values, checked into `specs/atlas/v1/test-vectors/coordinate-vectors.json` and cited in `07-atlas/123-coordinate-system-and-orientation.md`).

## Uniform path: `revolve()`

The uniform construction path (`builder.py::_build_uniform_shank()`) builds one profile wire at the resolved `inner_r`/`outer_r`/`half_width` and calls `wire.revolve(360, (0, 0, 0), (0, 1, 0))` — a true continuous 360-degree revolution around the world origin about the global Y axis. There is no discrete sampling in this path; the centerline is walked continuously by the kernel's own revolve operation, exactly as it was before Sprint 17 (SHANK-GOV-003).

## Tapered path: sampled loft around the same circle

The tapered construction path (`builder.py::_build_tapered_shank()`) walks the identical circular centerline, but discretely: it samples `SECTION_COUNT = 48` profile wires at `u = i / SECTION_COUNT` for `i in range(49)` (49 wires total, so `wire[48] == wire[0]`, closing the loop exactly), each rotated into place via `angle_deg_for_u(u)`, then lofts them with `cq.Solid.makeLoft(wires, ruled=True)`. The radius each section sits at is still `outer_radius(definition)` at the profile's outer edge — taper varies each section's *width and thickness*, never its position on the centerline circle. See [`545-section-profile-contract.md`](545-section-profile-contract.md) for what varies within a section and [`548-taper-model.md`](548-taper-model.md) for how much.

## v1 supports exactly one path shape: circular

There is exactly one centerline path in v1: a circle, walked either continuously (uniform) or via 48 discrete samples (tapered). No other path shape — elliptical, D-shaped, or otherwise non-circular — exists anywhere in `geometry/shank/`. In particular, a "Euro shank" (a ring style with a flattened or modified cross-section on the underside of the shank, which in practice usually implies a non-circular or locally-modified centerline/profile combination) is not implemented. The capability registry records this explicitly:

```json
{
  "capability": "euro_shank",
  "status": "planned",
  "jdlExposed": false,
  "generatable": false,
  "inspectable": false,
  "description": "A modified centerline path; the current path is circular only."
}
```

(`geometry/shank/capability.py::SHANK_CAPABILITIES["euro_shank"]`, mirrored at `specs/shank/v1/capability-registry.json`.) Per SHANK-GOV-015, this registry is the single source of truth for what is CURRENT vs PLANNED — no documentation, Designer capability list, or Studio copy may claim Euro shank support while this entry reads `planned`.

## Why this is a path property, not a taper property

It is worth stating explicitly because the two are easy to conflate: taper (documented in [`548-taper-model.md`](548-taper-model.md)) changes the *cross-section dimensions* at different points along a fixed circular path. It never changes the path itself — the outer edge of every section, tapered or not, sits at radial distance `outer_radius(definition)` from the ring axis (the loft's sections vary in `half_width` and in how far `outer_r` sits from `inner_r`, i.e. thickness, but the path radius the sections are strung along is unchanged). A split shank, multi-rail shank, or Euro shank would require an actual second centerline or a locally non-circular one — a materially different feature from taper, and one no code path in this Sprint implements (see the `split_shank`/`multi_rail_shank`/`euro_shank` entries in the capability registry, all `planned`).

## The path's relationship to `ShankConnectionInterface`

`ShankConnectionInterface.headCenterRadiusMm` (see [`550-head-connection-interface.md`](550-head-connection-interface.md)) is a related but distinct radius: it is `prong_center_radius(definition)`, the radius at which prong/basket centers sit, which is deliberately slightly inside the stone's girdle radius rather than on the shank's own centerline circle. The shank's path (this document) and the prong/basket placement radius are computed from related but separate inputs in `geometry/constants.py`, and neither is derived from the other — both simply share the same `definition.ring.innerDiameter`/`definition.band.thickness` inputs that ultimately root back to `inner_radius()`/`outer_radius()`.

## Verification: one path, checked once per Golden case

Because v1 has exactly one path shape, there is no per-path-type conformance test beyond what the existing Golden Suite already exercises: every one of the 12 solitaire Golden cases (`SOL-001` through `SOL-012`, see [`555-shank-golden-strategy.md`](555-shank-golden-strategy.md)) builds a shank around this same circular centerline, uniform or tapered, and `backend/tests/test_shank.py::TestShankVolumeAndBoundingBox`/`TestShankConnectivity` confirm the resulting solid's bounding box and connectivity are consistent with a single closed revolution/loft around one circle — not a fragmented or multi-lobed shape. A future second path shape (Euro shank or split shank) would need its own dedicated conformance tests rather than reusing these, since "one closed loop around one circle" is exactly the invariant those tests currently assume.
