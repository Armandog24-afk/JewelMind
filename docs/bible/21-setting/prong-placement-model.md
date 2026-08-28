---
id: JM-BIBLE-586
title: Prong Placement Model
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
  - JM-BIBLE-585
  - JM-BIBLE-583
implementation_status: current
professional_validation: not_required
normative: true
---

# Prong Placement Model

## The problem this solves

The pre-Sprint-19 placement was:

```python
girdle_r = stone.diameter / 2                     # round-only field
center_r = girdle_r - prong_r * 0.3
positions = [(center_r*cos(2*pi*i/n), center_r*sin(2*pi*i/n)) for i in range(n)]
```

One circle, evenly spaced angles, radius derived from a single stone dimension. For a round stone that is exactly right. For anything else it is a circle that ignores the stone's actual silhouette — and after Sprint 18 made six non-round shapes real, it was placing prongs that did not reach the stone.

## Two strategies

`ProngPlacementStrategy = Literal["RADIAL", "OUTLINE_CARDINAL"]`.

Which one runs is decided by the stone's real symmetry, in `placement.py::resolve_strategy()` — never by a shape-name branch in a caller:

```python
return "RADIAL" if reference.shape == "round" else "OUTLINE_CARDINAL"
```

### RADIAL

The pre-Sprint-19 formula, preserved character-for-character including the `cos`/`sin` order and the `2*pi*i/count` phase. It is geometrically faithful for a radially symmetric stone, and preserving it exactly is what keeps round's Goldens unchanged (SETTING-GOV-017).

### OUTLINE_CARDINAL

For each of `prongCount` evenly spaced **directions**, find the point where the stone's own girdle outline extends furthest along that direction, then pull it inward by the same girdle inset:

```python
for i in range(prong_count):
    ux, uy = cos(2*pi*i/prong_count), sin(2*pi*i/prong_count)
    best = max(outline_points, key=lambda p: p[0]*ux + p[1]*uy)   # support function
    distance = best[0]*ux + best[1]*uy
    positions.append(((distance - inset) * ux, (distance - inset) * uy))
```

This is the outline's **support function** evaluated in each prong direction. It follows the real silhouette: an oval's prongs sit near its own perimeter on both axes, and an emerald's sit on its flats rather than on a circle that ignores its corners.

Directions start at `+X` and advance counter-clockwise, matching RADIAL's phase — so the two strategies produce the same *ordering*, and agree exactly wherever the geometry agrees.

## The measured improvement

Oval, 8 × 6 mm, 6 prongs, prong radius 0.55 mm. Distance from each prong axis to the nearest point on the stone outline:

| Prong | RADIAL | OUTLINE_CARDINAL |
|---|---|---|
| on `+X` axis | 0.165 mm | **0.165 mm** (identical) |
| at 60° | 0.784 mm | **0.049 mm** |
| at 120° | 0.784 mm | **0.049 mm** |

The on-axis prong is unchanged — it sits at the intended girdle inset under both strategies, which confirms `OUTLINE_CARDINAL` is a *generalization* of `RADIAL` rather than a different convention. The off-axis prongs move from floating 0.784 mm clear of the stone to essentially touching it.

Max `|y|` of prong centres also rises from 2.455 mm to 3.126 mm against an oval half-length of 4.0 mm — the prongs now reach along the stone's long axis instead of being confined to a circle sized by its narrow one.

Asserted by `test_setting.py::TestNonRoundProngPlacement::test_outline_placement_puts_prongs_closer_to_the_real_outline_than_radial` and `::test_outline_placement_agrees_with_radial_on_the_x_axis_prong`.

## What this is NOT

**Not a professionally correct setting position.** Brief section 12 is explicit: *"Do NOT claim that these are professionally correct setting positions unless validated by real professionals."* No professional has reviewed any of it, and every non-round combination is honestly `EXPERIMENTAL`.

Specifically still wrong, by a jeweller's standards:

- **Marquise tips are unsupported.** A real marquise setting places V-prongs at the two points, because that is where the stone is most vulnerable. `OUTLINE_CARDINAL` will place a prong *near* a tip only if a prong direction happens to point at it, and it has no V-prong geometry regardless.
- **Pear's tip is not protected.** Same reason. The `tipDirectionY` fact exists on `StoneSettingReference` precisely so a future strategy can use it; no strategy consumes it yet.
- **Angular stones' corners are not targeted.** For an emerald or princess, `OUTLINE_CARDINAL` places prongs along the flats at whatever directions the even spacing produces, not at the corners where a real setting would grip.
- **Prong count is not shape-derived.** A 10 × 5 marquise and a 6.5 mm round both get whatever count the JDL requests.

## Orientation

The outline is rotated by the stone's own `orientationDeg` before sampling, so a rotated stone's prongs rotate with it. Verified by `test_placement_honours_stone_orientation`: at 0° an oval's prongs extend further in Y than X; at 90° the reverse.

## Constants

| Constant | Value | Nature |
|---|---|---|
| `GIRDLE_INSET_PRONG_RADIUS_FRACTION` | `0.3` | Inherited unchanged from the pre-Sprint-19 `prong_center_radius()`. A construction parameter, not a jewelry threshold. |
| `_OUTLINE_SAMPLES` | `720` | Numerical resolution of the support-function search. Not a geometric claim. |

Neither is a professional minimum, and no professional minimum is introduced anywhere in the package (SETTING-GOV-010).

## Extensibility

`prong_positions()` dispatches on the strategy and returns `(positions, strategy_used)`, so the caller reports the strategy as a real fact rather than assuming it. Adding a third strategy — corner-aware, tip-protecting, symmetry-partitioned — means adding a function and a `resolve_strategy()` case. The `isBilaterallySymmetric` and `tipDirectionY` facts are already on the interface for exactly that.

## Cross-references

- [`stone-setting-interface.md`](stone-setting-interface.md) — where the outline comes from.
- [`setting-golden-strategy.md`](setting-golden-strategy.md) — why the six non-round Golden baselines changed, and the recorded reason.
