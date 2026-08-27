---
id: JM-BIBLE-573
title: Stone Setting Interface
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-STONE-README
  - JM-BIBLE-560
related_documents:
  - JM-BIBLE-575
  - JM-BIBLE-578
  - JM-BIBLE-528
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Setting Interface

## The boundary

> Stone System exposes geometric facts about a stone. The Setting layer decides prong, bezel, and seat geometry **from** those facts. Neither redefines the other's geometry. (STONE-GOV-009)

Concretely: `StoneDefinition` contains **no prong positions**, no bezel wall, no seat, and no basket. `geometry/stone/` builds exactly one thing — the `stone_reference` solid — and never imports `jewelmind.validation` or constructs metal.

## What Stone exposes

Everything a setting needs is available today, from the generated component and the resolved-dimension layer:

| Fact | Source | Notes |
|---|---|---|
| Resolved LENGTH / WIDTH / DEPTH | `domain/stone_dimensions.py` | The canonical contract; round normalizes to `length == width == diameter`. |
| Girdle plane Z | `metadata["girdleZMm"]` | `band_top_z + basketHeight`. The vertical anchor a setting grips at. |
| Crown / pavilion heights | `metadata["crownHeightMm"]`, `["pavilionHeightMm"]` | How far the stone rises above and drops below the girdle. |
| Bounding box | `GeneratedComponent.bounding_box` | Real axis-aligned extents. |
| Centre | derivable from the bounding box; real centre of mass via `shape.Center()` | Used by `_apply_orientation()` itself. |
| Orientation | `metadata["orientationDeg"]` | So a setting can align to a rotated stone. |
| Outline | `geometry/stone/outline.py` | The 2D profile, callable independently of the solid — see [`566-stone-outline-contract.md`](566-stone-outline-contract.md). |
| Shape identity | `metadata["shape"]` | So a future shape-aware setting can branch honestly. |

The outline is the most important of these for the future. A bezel wall, a halo path, a pavé boundary, a seat, and a clearance envelope are all offsets of the stone's girdle outline — which is exactly why outline generation was kept independent of the 3D loft.

## What the current setting actually does

One real consumer exists today: `geometry/constants.py::prong_center_radius()`.

```python
girdle_r = resolved_width_mm(definition.stone) / 2
prong_r  = definition.setting.prongDiameter / 2
return girdle_r - prong_r * 0.3
```

Before Sprint 18 this read `definition.stone.diameter / 2`. That would now crash for any non-round stone (`diameter` is `None` there), so it was changed to read the resolved minor horizontal dimension.

**This is placement geometry, not a threshold evaluation.** The distinction matters because it is exactly where a "fake equivalent diameter" could have crept in:

- It produces a **radius at which to place prong solids** — a real construction parameter, consumed by `prongs.py` and `basket.py`.
- It does **not** feed any Forge rule, and no jewelry-domain threshold is compared against it.
- Every non-round shape's `currentSettingCompatibility` is honestly `EXPERIMENTAL` **precisely because** this placement is generic rather than shape-derived.

Contrast with what was *not* done: `JM-STONE-001` (diameter range) and `JM-PRONG-003` (prong count vs stone size) were scoped `ROUND_ONLY` rather than evaluated against a substituted dimension. A rule threshold is a domain judgement and must not be applied to a dimension it was never calibrated for; a placement radius is a construction input and may legitimately be generalised. See [`578-current-code-mapping-and-gaps.md`](578-current-code-mapping-and-gaps.md).

## Compatibility states

`SettingCompatibility` (`geometry/stone/capability.py`) is a real, separate axis from `generationSupported`:

| State | Meaning | Shapes |
|---|---|---|
| `SUPPORTED` | The current setting geometry was designed for this shape and places prongs meaningfully. | `round` |
| `EXPERIMENTAL` | The stone generates real geometry and assembles into a complete ring, but prong placement is a generic provisional circular layout, not shape-derived. | `oval`, `pear`, `emerald`, `cushion`, `princess`, `marquise` |
| `UNSUPPORTED` | Reserved. No current shape uses it. | — |

`EXPERIMENTAL` is not a hedge — it is a specific, per-shape claim recorded in the registry:

| Shape | Recorded reason |
|---|---|
| `oval` | Prong placement is generic/circular, not shape-optimized. |
| `marquise` | Placement does not cluster prongs at the tips. |
| `pear` | Placement is not tip-aware. |
| `emerald`, `princess`, `cushion` | Placement is not corner-aware. |

Each of those names a real deficiency a jeweller would recognise: a marquise needs V-prongs at its tips, an angular stone needs corner prongs, a pear needs its tip protected. The current layout distributes prongs evenly around a circle derived from `resolved_width_mm`, so for a 10 × 5 marquise the prongs sit on a circle far narrower than the stone and the tips are unsupported entirely.

Reporting this honestly was a requirement, not a choice: the brief was explicit that *"If current prong logic cannot responsibly support a shape: report it as setting compatibility limitation rather than faking correct prong geometry."*

## Minimum integration achieved

The brief required more than isolated test solids — new stones had to actually assemble. Verified by `test_stone.py::TestNonRoundAssembly::test_shape_generates_a_fully_connected_solitaire_assembly` for `oval`, `emerald`, `cushion`, and `princess`: each builds a complete solitaire, passes `inspect_model()` with `fullAssemblyConnectivity.isFullyConnected is True`, and reports a matching generated prong count.

This exceeds the required minimum (round + oval + one angular shape). It demonstrates positioning, inspection, Vision (the preview mesh pipeline is shape-agnostic), and export all working — while explicitly **not** claiming professional setting validity.

## Geometric anchors

Useful canonical positions, derivable deterministically from the outline and bounding box:

| Anchor | Definition |
|---|---|
| `TOP` / `BOTTOM` | Girdle-plane extremes along +Y / −Y. |
| `LEFT` / `RIGHT` | Girdle-plane extremes along −X / +X. |
| `TIP` (pear only) | `(0, +length/2)` — the pointed end. |
| `ROUNDED_END` (pear only) | `(0, −length/2)` — the rounded end. |

Two honest qualifications:

1. **These are geometric anchors, not mandatory prong positions.** They describe where notable points on the stone are; they carry no claim about where metal should go.
2. **They are documented conceptual anchors, not a separate implemented API this Sprint.** There is no `stone_anchors()` function. Every anchor above is computable from data already exposed (the outline and the bounding box), and the names exist so a future Setting System has vocabulary to target. Introducing them as a real API is a Sprint 19 concern.

## What Setting must never do

- Redefine or rebuild stone geometry (STONE-GOV-009). A setting reads the stone's facts; it does not re-derive the stone.
- Fuse the stone into production metal (STONE-GOV-003/004, LAW-006).
- Push a prong position back into `StoneDefinition`.
- Treat `currentSettingCompatibility: EXPERIMENTAL` as good enough to describe a shape as professionally settable.

## Forward reference: Sprint 19

Sprint 19 is *"Setting System v1 — separate stone-setting geometry from ring-specific head construction and establish reusable parametric setting strategies, beginning with generalized prong placement and bezel support across compatible Stone System shapes."* That is where shape-aware placement, the anchor API, and bezel geometry belong. This document does not describe that work further; it is out of Sprint 18's scope and not implemented.

See also [`../18-ring-architecture/528-head-contract.md`](../18-ring-architecture/528-head-contract.md) for the Ring-side head contract this will eventually plug into.
