"""Deterministic taper interpolation (SHANK-GOV-005, brief sections 8/14).

`u` is the stable longitudinal parameter around the ring, `u in [0, 1)`:
`u=0` is the head (where the setting sits — the same point
`geometry.connection.shank_connection_interface().topZMm` names), `u=0.5`
is the bottom, directly opposite. Both shoulders (`u` near 0 from either
direction) share taper behaviour automatically, since `taper_ratio()` is a
pure function of angular distance from the head — no manually duplicated
left/right parameters exist (SHANK-GOV-005, brief section 28).

`mode="TOWARD_BOTTOM"` anchors the FULL base dimension exactly at `u=0`
(the head) and linearly interpolates down to `bottomRatio * base` at
`u=0.5` — this is a deliberate v1 design choice, not an oversight: it
guarantees the shank's connection interface (`topZMm`) never moves for
any taper configuration, so RingHead placement needs zero changes for a
tapered shank. See docs/bible/19-shank/550-head-connection-interface.md.
"""

from __future__ import annotations

from jewelmind.domain.schema import BandTaperSpec


def taper_ratio(u: float, taper: BandTaperSpec) -> float:
    """The multiplier to apply to the base dimension at longitudinal
    position `u`. Always exactly 1.0 at `u=0`/`u=1` (the head) and at
    every `u` when `taper.mode == "NONE"`."""

    if taper.mode == "NONE":
        return 1.0
    distance_from_head = min(u, 1.0 - u) * 2.0  # 0.0 at the head, 1.0 at the bottom
    return 1.0 + (taper.bottomRatio - 1.0) * distance_from_head


def angle_deg_for_u(u: float) -> float:
    """The real-world rotation angle (matching `cq.Workplane.rotate()`
    around the global Y axis) that places a section at longitudinal
    position `u`. Verified empirically against `band_top_z()`'s reference
    point (x=0, z=+outer_radius): `u=0` maps to angle=-90, matching that
    exact point. See docs/bible/19-shank/543-shank-coordinate-model.md."""

    return -90.0 + u * 360.0
