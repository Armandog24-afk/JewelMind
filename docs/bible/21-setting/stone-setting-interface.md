---
id: JM-BIBLE-583
title: Stone to Setting Interface
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
  - JM-BIBLE-573
  - JM-BIBLE-585
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone to Setting Interface

## The contract

`StoneSettingReference` (`setting/models.py`) is the complete set of stone facts a Setting may consume, built by `setting/stone_interface.py` from a real generated stone component:

| Field | Source | Purpose |
|---|---|---|
| `stoneId`, `shape` | `StoneSpec` | Identity; lets a family branch honestly on shape. |
| `lengthMm`, `widthMm`, `depthMm` | `domain/stone_dimensions.py` resolvers | The canonical resolved dimensions. Round normalizes to `length == width == diameter`. |
| `orientationDeg` | `StoneSpec.orientation` | So a setting rotates with a rotated stone. |
| `girdlePlaneZMm` | the stone component's own metadata | The reference plane a setting grips at. |
| `centerXMm`, `centerYMm` | the stone's real bounding box | Placement origin. |
| `boundingBoxMinMm` / `MaxMm` | the real generated solid | Extents. |
| `isBilaterallySymmetric` | derived from shape | `False` for `pear`. |
| `tipDirectionY` | derived from shape | `+1.0` for `pear`, `None` otherwise. |

Plus `girdle_outline_wire()`, which returns the stone's **own** girdle outline as a closed planar wire by calling the real Stone System outline primitives.

## Why this is a contract and not just "pass the stone"

The Setting could have received the `GeneratedComponent` and read whatever it liked. Two reasons it does not:

1. **Kernel neutrality.** `StoneSettingReference` is plain data, so the facts a Setting depends on can cross layer boundaries — into a Forge rule, a Studio display, a Designer capability check — without dragging CadQuery along.
2. **An auditable dependency surface.** Because the interface is explicit and small, SETTING-GOV-003 is checkable: a Setting consumes these facts and cannot quietly start reading Stone builder internals. Passing the raw component would have made the real dependency unbounded.

Brief section 20's caveat applies and is honoured: *within* Atlas geometry execution real geometry objects are used where necessary — `girdle_outline_wire()` genuinely returns a `cq.Wire`, because a bezel path and an outline sample cannot be expressed as scalars. The domain contract stays clear because that wire is obtained through one named function that calls Stone's own primitives, rather than by reaching into the builder.

## `isBilaterallySymmetric` and `tipDirectionY`

These two fields exist so a placement strategy can *refuse to assume* symmetry it does not have (SETTING-GOV-008). Six of seven shapes are bilaterally symmetric about both horizontal midplanes; `pear` is symmetric about one axis only, and has a distinguished tip at `+Y`.

Neither field is consumed by a strategy today: `OUTLINE_CARDINAL` derives everything it needs from the outline itself, which already carries the asymmetry. They are recorded because a future tip-protecting strategy (a real `V_PRONG`) needs exactly this information, and deriving it ad hoc per strategy would be where a shape assumption creeps back in. This is stated plainly rather than implying they are already load-bearing.

## The outline is authoritative

Both consumers use the stone's real outline rather than a substitute:

- **Bezel** offsets it directly — so the bezel path *is* the stone silhouette, and a future custom outline flows through the same pipeline (brief section 19).
- **`OUTLINE_CARDINAL` placement** samples it to find where the stone extends furthest along each prong direction.

Neither reads `stone.diameter`. That matters: `diameter` is `None` for every non-round shape, so a Setting reading it directly would crash — which is precisely the leak that existed in `prong_center_radius()` before Sprint 18 fixed it.

## What a Setting must never do

- Rebuild, scale, or approximate a stone silhouette (SETTING-GOV-003).
- Read `stone.diameter` (use the resolved dimensions).
- Fuse the stone into production metal (SETTING-GOV-004).
- Treat a stone/metal intersection as an error — a StoneReference is a reference volume and setting geometry may intentionally overlap it (brief section 26).

## Cross-references

- [`../20-stone/573-stone-setting-interface.md`](../20-stone/573-stone-setting-interface.md) — the Stone side of the same boundary, written in Sprint 18 before this consumer existed.
- [`prong-placement-model.md`](prong-placement-model.md) — how the outline is actually sampled.
