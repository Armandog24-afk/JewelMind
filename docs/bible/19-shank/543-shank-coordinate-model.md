---
id: JM-BIBLE-543
title: Shank Coordinate Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
  - JM-BIBLE-123
related_documents:
  - JM-BIBLE-542
  - JM-BIBLE-548
implementation_status: current
professional_validation: not_required
normative: true
---

# Shank Coordinate Model

## Grounding in the existing Atlas convention

This document adds one new parameter — the longitudinal position `u` — on top of the coordinate convention already formalized in [`07-atlas/123-coordinate-system-and-orientation.md`](../07-atlas/123-coordinate-system-and-orientation.md), which this document does not restate in full. The relevant facts carried over unchanged: the finger-hole axis is the global **Y axis**, the band lies in the X/Z plane when viewed down Y, the world origin is the center of the ring, and ring "top" is `(x=0, z=+outer_radius)`, the same point `band_top_z()` names.

## The `u` parameter

`u ∈ [0, 1)` is the stable longitudinal parameter describing a position around the shank's circumference, defined in `geometry/shank/taper.py`:

- `u = 0` (and, equivalently, `u → 1`) is **the head** — the point where the setting sits, matching `band_top_z()`'s reference point `(x=0, z=+outer_radius)`.
- `u = 0.5` is **the bottom**, directly opposite the head.
- Every other `u` value is a point partway around the circumference, symmetric in distance-from-head between the two directions (`u` slightly above 0 and `u` slightly below 1 are equally close to the head).

`u` is used in exactly two places in the current code: `taper.py::taper_ratio(u, taper)` (the width/thickness multiplier at that position, see [`548-taper-model.md`](548-taper-model.md)) and `taper.py::angle_deg_for_u(u)` (the real rotation angle for that position). Both are pure functions of `u` and, for `taper_ratio`, the `BandTaperSpec` — no other input.

## `angle_deg_for_u()`

```python
def angle_deg_for_u(u: float) -> float:
    return -90.0 + u * 360.0
```

This is the real-world rotation angle, in the same convention `cq.Workplane.rotate()` around the global Y axis uses, that places a profile section at longitudinal position `u`. It was verified empirically against `band_top_z()`'s reference point: at `u=0`, `angle_deg_for_u(0) = -90.0`, and rotating a profile wire built at the canonical `(x=0, z=+outer_radius)`-referenced orientation by `-90` degrees around Y lands it exactly at that same point — confirming `u=0` really is the head, not an assumption asserted without a check.

Real sample values, from `specs/shank/v1/test-vectors/taper-vectors.json` (mode `NONE`, so `taperRatio` stays `1.0` throughout — only the angle varies):

| `u` | `angleDeg` |
|---|---|
| 0.0 | -90.0 |
| 0.25 | 0.0 |
| 0.5 | 90.0 |
| 0.75 | 180.0 |
| 0.99 | 266.4 |

The mapping is linear and monotonic across the full range: `u=0.5` (the bottom) lands at `angleDeg=90.0`, and `u` approaching `1.0` approaches `angleDeg=270.0` (`-90 + 360`), which is the same physical location as `angleDeg=-90.0` — consistent with `u=0` and `u→1` both naming the head.

## How `_section_wire()` uses both together

`builder.py::_section_wire()` builds one profile wire per sampled `u`, resolves its width/thickness via `taper_ratio(u, ...)`, builds the 2D wire via `profile.py::build_profile()`, and then rotates it into place with `wire.rotate((0, 0, 0), (0, 1, 0), angle_deg_for_u(u))` — a rotation around the world origin about the global Y axis, the same axis the uniform path's `revolve()` call already used. This is why the tapered loft path stays geometrically consistent with the uniform path's coordinate frame: both revolve/rotate around the same axis, through the same origin, in the same direction.

## No new coordinate convention

Nothing in this Sprint introduces a new axis, a new plane, or a new origin. `u` is a parameterization of the existing circular path around the existing Y axis, not an independent coordinate system — see [`544-shank-path-contract.md`](544-shank-path-contract.md) for the centerline this parameterization walks around. A future non-circular centerline path (Euro shank, `planned` per the capability registry) would need its own document extending this one; it is out of scope for v1.

## Why `u` had to be verified empirically, not just asserted

The module docstring for `taper.py` and the inline comment on `angle_deg_for_u()` both state that the `u=0 → angle=-90` mapping was "verified empirically against real rotated bounding boxes," not derived purely on paper from the revolve convention. This matters because `angle_deg_for_u()`'s sign and offset (`-90.0 + u * 360.0`, rather than, say, `u * 360.0` with no offset, or a different sign) are not forced by the coordinate convention alone — `cq.Workplane.rotate()`'s angle direction around a given axis has to be checked against the kernel's actual behavior, not assumed from the axis definition. Getting the offset wrong would silently place `u=0` somewhere other than the head, which `taper.py`'s head-anchoring guarantee (SHANK-GOV-011) depends on being exactly correct. This is why the formula is treated as a verified fact with a citation trail (the taper-vectors test file, re-derived live by `backend/tests/test_shank_schemas.py`), not a convention stated once and trusted forever.

## Consuming `u` correctly in future code

Any future code that needs to know "where around the shank is this," including a hypothetical Studio taper-preview control or a new inspection fact, should compute or accept `u` in `[0, 1)` and go through `angle_deg_for_u()`/`taper_ratio()` rather than re-deriving an angle-to-position mapping independently — duplicating the `-90` offset in a second location would create exactly the kind of silent-drift risk SHANK-GOV-008 exists to prevent for the generation contract itself.
