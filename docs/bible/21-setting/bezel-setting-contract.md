---
id: JM-BIBLE-587
title: Bezel Setting Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-27
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SETTING-README
  - JM-BIBLE-580
related_documents:
  - JM-BIBLE-583
  - JM-BIBLE-589
implementation_status: current
professional_validation: not_required
normative: true
---

# Bezel Setting Contract

## Status

| Property | Value |
|---|---|
| Family | `bezel` |
| Implementation status | `CURRENT` |
| Stone shapes `SUPPORTED_SOFTWARE` | `round`, `oval` |
| Stone shapes `EXPERIMENTAL` | `pear`, `emerald`, `cushion`, `princess`, `marquise` |
| Seat / bearing / cutter | `PLANNED` — none exists |
| Professional validation | `NOT_REVIEWED` |

All 7 current stone shapes produce a valid single-solid bezel. `round` and `oval` are the two the brief required and the two marked `SUPPORTED_SOFTWARE`; the rest generate but are honestly `EXPERIMENTAL`.

## Parameters

`BezelSettingDefinition` (`setting/models.py`):

| Field | Default | Meaning |
|---|---|---|
| `wallThicknessMm` | `0.6` | Constant geometric offset outward from the stone girdle outline. |
| `wallHeightMm` | `2.5` | Total vertical extent of the wall. |
| `verticalReference` | `GIRDLE` | The wall is centred on the stone's girdle plane. |
| `outlineOffsetMode` | `CONSTANT_OFFSET` | A true constant-distance offset, not a scaled outline. |

**The two defaults are PRELIMINARY SOFTWARE VALUES**, in exactly the same class as `band.width = 2.4` — deliberate, configurable software choices verified only to produce robust geometry. They are **not** professional recommendations and must never be described as such (SETTING-GOV-010). Correspondingly, **no minimum wall thickness or height is enforced**: a minimum would be a professional manufacturing threshold, and no sourced value exists. `test_setting.py::test_no_minimum_bezel_wall_dimension_is_asserted` pins that absence deliberately.

The two Forge rules that do exist (`JM-SETTING-003`/`004`) check only that each value is positive — a constructibility invariant, not a domain judgement.

## Construction

```
stone girdle outline                (the stone's OWN outline, via stone_interface)
  -> cq.Wire.offset2D(wallThickness)      constant geometric offset
  -> STEP-safety repair (curve-type triggered, see below)
  -> cq.Face.makeFromWires(outer, [inner])    annular face, stone outline as the hole
  -> cq.Solid.extrudeLinear(face, (0,0,wallHeight))
  -> translate to girdlePlaneZ - wallHeight/2
  -> validity check (.Solids() and .isValid())
```

Real B-Rep throughout. Not a frontend visualization, not a ring around the origin, not a scaled mesh.

### Outline-agnostic by construction

The pipeline never asks what shape it is building. It takes whatever closed wire `girdle_outline_wire()` returns and offsets it, which is what brief section 19 requires: a future custom outline, a measured stone, or an eighth shape flows through unchanged rather than needing an `if round / elif oval` branch. The only shape-dependent input is the wire itself, which the Stone System already owns.

### Vertical extent

The wall is **centred on the stone's girdle plane**: bottom at `girdlePlaneZ - wallHeight/2`, top at `girdlePlaneZ + wallHeight/2`. An explicit, symmetric rule, chosen precisely to avoid fabricating an asymmetric crown/pavilion coverage split that would look like a professional proportion without being one.

Connectivity to the ring is not asserted, it is achieved: the basket support already spans from the band top up to the girdle plane, so a girdle-centred wall overlaps its top by `wallHeight/2`. `test_setting.py::TestSettingConnectivity` verifies the production connectivity graph is fully connected and the metal fuses to one solid.

## The one real geometry-engine accommodation

This is the most important finding of the Sprint and is documented in the module docstring as well.

`cq.Wire.offset2D()` produces a genuine constant-distance offset. For a wire of lines and circular arcs the result is again lines and arcs, which OpenCascade's STEP writer round-trips exactly. **For an ellipse it is not**: the offset of an ellipse is not an ellipse, and OCCT represents it with edges whose `geomType()` is `OFFSET`. An extruded `OFFSET`-curve surface does **not** survive a STEP write/read cycle — it re-imports as a `Shell` with **zero solids**, which `step_roundtrip_check()` correctly flags.

Measured offset edge types, per shape:

| Shape | inner outline | offset result |
|---|---|---|
| `round` | `CIRCLE` | `CIRCLE` |
| **`oval`** | **`ELLIPSE`** | **`OFFSET`** ← the only affected case |
| `emerald` | `LINE` | `CIRCLE`, `LINE` |
| `princess` | `LINE` | `CIRCLE`, `LINE` |
| `cushion` | `CIRCLE`, `LINE` | `CIRCLE`, `LINE` |
| `marquise` | `CIRCLE` | `CIRCLE` |
| `pear` | `CIRCLE`, `LINE` | `CIRCLE`, `LINE` |

**The repair is triggered by the real curve type, not by a shape name.** Any offset wire containing an `OFFSET` edge is resampled into a periodic B-spline over 96 points. This matters for two reasons: hardcoding `if shape == "oval"` would have re-introduced exactly the per-shape branching section 19 exists to prevent, and it would silently miss a future custom outline built from splines.

The repair is recorded as an observable `SettingFallbackEvent` on the result and as a component warning (SETTING-GOV-013), and surfaced in the technical specification.

Measured cost: volume deviation from the true offset is ~0.006% (35.9827 → 35.9806 mm³ on the reference oval), and the repaired solid round-trips through STEP with a volume delta below 1e-11 mm³.

### Rejected alternatives

| Approach | Why rejected |
|---|---|
| **Expanded semi-axes** (ellipse with `a+t`, `b+t`) | Exports cleanly, but is not a constant offset — the wall would be thinner at the ends than at the sides. Wrong geometry to fix an export problem. |
| **Blanket resampling of every offset wire** | Works, but measurably rounds the angular shapes' crisp corners (princess volume wobbled 44.83 → 45.00 at 96 points, → 44.67 at 192). Repairing what is not broken. |
| **Loft between two copies of the wire** | Identical STEP failure — the problem is the curve type, not the construction. |
| **Boolean cut of two extrusions** | Produced geometry identical to the annular face, with the same STEP failure. No advantage. |

The annular-face + linear-extrusion construction was chosen because it produced a valid single solid for all 7 shapes and expresses the intent directly: a wall *is* an outline with a hole, extruded.

## Real generated results

At `wallThickness = 0.6`, `wallHeight = 2.5`:

| Shape | Dimensions | Volume (mm³) | Solids | STEP repair |
|---|---|---|---|---|
| `round` | d 6.5 | 33.458 | 1 | no |
| `oval` | 8 × 6 | 35.981 | 1 | **yes** |
| `emerald` | 8 × 6 | 42.929 | 1 | no |
| `cushion` | 7 × 7 | 42.574 | 1 | no |
| `princess` | 6.5 × 6.5 | 41.827 | 1 | no |
| `marquise` | 10 × 5 | 37.601 | 1 | no |
| `pear` | 9 × 6 | 37.089 | 1 | no |

Recorded in `specs/setting/v1/test-vectors/bezel-vectors.json`, re-derived live by `test_setting_schemas.py`.

That the wall really is a geometric offset is asserted directly: for a round stone of diameter D the bezel's outer extent must be `D + 2 × thickness`, and for a 9 × 5 oval the extents must be `9 + 1.2` and `5 + 1.2`.

## What this is NOT

- **Not a professionally valid bezel.** `NOT_REVIEWED`. No jeweller has assessed wall thickness, height, coverage, or finishing.
- **No seat or bearing.** A real bezel is set by cutting a seat inside the wall for the stone's girdle to sit on. None exists. The stone/bezel overlap is a reference-volume intersection, **not** a seat, and must never be renamed as one.
- **No cutter geometry.** Nothing models the tool operations a setter would perform.
- **No coverage judgement.** Inspection reports `BEZEL_WALL_CONTINUOUS` — whether the wall is one closed solid — which is pure topology, never a claim that the stone is adequately held.

## Cross-references

- [`stone-setting-interface.md`](stone-setting-interface.md) — where the outline comes from.
- [`setting-inspection-contract.md`](setting-inspection-contract.md) — the bezel facts and what they do not mean.
- [`setting-golden-strategy.md`](setting-golden-strategy.md) — `SET-004`/`SET-005`.
