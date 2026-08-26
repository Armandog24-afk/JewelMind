---
id: JM-BIBLE-548
title: Taper Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
  - JM-BIBLE-546
  - JM-BIBLE-547
related_documents:
  - JM-BIBLE-543
  - JM-BIBLE-550
implementation_status: current
professional_validation: not_required
normative: true
---

# Taper Model

## `BandTaperMode`

```python
BandTaperMode = Literal["NONE", "TOWARD_BOTTOM"]

class BandTaperSpec(StrictModel):
    mode: BandTaperMode = "NONE"
    bottomRatio: float = Field(default=1.0, gt=0, le=1, allow_inf_nan=False)
```

(`domain/schema.py`.) Exactly two modes exist. `NONE` is the default and means no taper — every existing pre-Sprint-17 JDL document, which never set `widthTaper`/`thicknessTaper` at all, resolves to `mode: "NONE"` on both fields via `Field(default_factory=BandTaperSpec)`, which is why this is an additive, backward-compatible MINOR schema change (see [`556-current-band-migration.md`](556-current-band-migration.md)). `bottomRatio` is constrained to `(0, 1]` — always a shrink-or-unchanged ratio; a value above 1 (widening toward the bottom) is not representable in v1, per [`specs/shank/v1/taper-definition.schema.json`](../../../specs/shank/v1/taper-definition.schema.json)'s own `exclusiveMinimum`/`maximum` bounds.

## `taper_ratio()`, the exact formula

```python
def taper_ratio(u: float, taper: BandTaperSpec) -> float:
    if taper.mode == "NONE":
        return 1.0
    distance_from_head = min(u, 1.0 - u) * 2.0  # 0.0 at the head, 1.0 at the bottom
    return 1.0 + (taper.bottomRatio - 1.0) * distance_from_head
```

(`geometry/shank/taper.py`.) `distance_from_head` is `0.0` exactly at `u=0` and at `u→1` (both name the head — see [`543-shank-coordinate-model.md`](543-shank-coordinate-model.md)), rises linearly to `1.0` exactly at `u=0.5` (the bottom), and falls symmetrically back toward `0.0` as `u` continues past `0.5` toward `1.0`. Substituting `distance_from_head=0` gives `taper_ratio = 1.0` (the head, always full-size, in every mode including `NONE`); substituting `distance_from_head=1` gives `taper_ratio = bottomRatio` (the bottom).

## Symmetry is automatic, not duplicated

Because `distance_from_head = min(u, 1.0 - u) * 2.0` is symmetric around `u=0.5` by construction, both shoulders — the arc from the head toward the bottom going one direction around the ring, and the arc going the other direction — receive identical taper behavior automatically. There is no second `leftBottomRatio`/`rightBottomRatio` parameter, no separate code branch per direction, and no way to configure the two shoulders differently in v1 (SHANK-GOV-005). This was a deliberate design choice, not an oversight: a real ring's two shoulders are physically symmetric in every case v1 addresses, and the formula encodes that fact structurally rather than relying on two callers passing matching values.

## Head-anchoring design rationale

`TOWARD_BOTTOM` always anchors the **full base dimension** exactly at `u=0` (and `u→1`), interpolating down to `bottomRatio * base` only as `u` moves toward `0.5`. It never anchors the taper at the bottom and grows outward, and it never distributes the taper symmetrically around some other point. This is deliberate for one specific reason, stated in the `taper.py` module docstring and restated by SHANK-GOV-011: it guarantees `ShankConnectionInterface.topZMm` (see [`550-head-connection-interface.md`](550-head-connection-interface.md)) never moves for any taper configuration, because `topZMm = band_top_z(definition) = outer_radius(definition)`, which is defined purely from `ring.innerDiameter` and `band.thickness` — the *base* thickness, evaluated as if `u=0` — never from a tapered value. Since taper always evaluates to exactly `1.0` (full size) at `u=0`, the shank's actual geometry at the head matches this untapered reference point exactly, for every `bottomRatio` and for width-only, thickness-only, or combined taper alike.

The practical consequence (SHANK-GOV-010) is that `prongs.py`/`basket.py` need zero special-case code for a tapered shank: they call `shank_connection_interface(definition)` exactly as they would for a uniform shank, and get back the same `topZMm`/`embedMm`/`headCenterRadiusMm` regardless of whether the band underneath is uniform or tapered.

## Real sample values

From `specs/shank/v1/test-vectors/taper-vectors.json` (`mode="TOWARD_BOTTOM"`, `bottomRatio=0.6`):

| `u` | `taperRatio` | `angleDeg` |
|---|---|---|
| 0.0 | 1.0 | -90.0 |
| 0.25 | 0.8 | 0.0 |
| 0.5 | 0.6 | 90.0 |
| 0.75 | 0.8 | 180.0 |
| 0.99 | 0.992 | 266.4 |

`u=0.25` and `u=0.75` are equidistant from the head in opposite directions and both produce `taperRatio=0.8` — the symmetry stated above, confirmed numerically rather than merely asserted. The vectors file also includes `bottomRatio=0.5` and `bottomRatio=1.0` sweeps, and `mode="NONE"`, all consistent with the same formula.

## What is PLANNED, not implemented

Two related capabilities are explicitly `planned` in `geometry/shank/capability.py::SHANK_CAPABILITIES`, mirrored at `specs/shank/v1/capability-registry.json`:

- **`taper_toward_head`** — a mode that would taper toward the head instead of the bottom. The registry states the reason directly: it "would move the connection-interface anchor away from u=0," which is precisely the property `TOWARD_BOTTOM` was designed to avoid disturbing — it is deliberately out of v1 scope, not merely unimplemented by omission.
- Non-linear taper curves (anything beyond the linear interpolation `taper_ratio()` performs) — not a named capability-registry entry of its own, but explicitly called out as not implemented in [`specs/shank/v1/taper-definition.schema.json`](../../../specs/shank/v1/taper-definition.schema.json)'s `mode` field description: "TOWARD_HEAD, symmetric two-point tapers, and non-linear taper curves are PLANNED, not implemented in v1."

Per [`540-shank-governance.md`](540-shank-governance.md)'s "When an RFC is required," widening `BandTaperMode` beyond `NONE`/`TOWARD_BOTTOM` requires an RFC even though it is architecturally an additive JDL change, because it changes the taper *model* itself, not merely adds a field.
